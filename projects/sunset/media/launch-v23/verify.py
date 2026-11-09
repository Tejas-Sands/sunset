#!/usr/bin/env python3
"""Verify the encoded Web3 animation and unchanged approved V22 soundtrack."""
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess

import numpy as np
from PIL import Image, ImageDraw

from produce import ROOT,OUT,SOURCE,MASTER,APPROVED,FRAMES,FPS,DURATION,EVENTS,sha,picture,state,protocol_camera

spec=importlib.util.spec_from_file_location('prior_checks',SOURCE.parent/'launch-v22/verify.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)


def audio_packets(movie):
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0',
        '-show_packets','-show_data_hash','sha256','-of','json',str(movie)]))
    return probe['packets']


def sheet(selected,numbers,path,width=384):
    height=round(width*1080/1920);columns=5
    board=Image.new('RGB',(columns*width,((len(numbers)+columns-1)//columns)*(height+28)),'#f7f5ed');d=ImageDraw.Draw(board)
    for i,n in enumerate(numbers):
        x=i%columns*width;y=i//columns*(height+28)
        board.paste(selected[n].resize((width,height),Image.Resampling.LANCZOS),(x,y))
        d.text((x+6,y+height+5),f'{n:04} / {n/30:.2f}s',fill='#183c2e')
    board.save(path)


def main():
    movie=OUT/'sunset-launch-v23.mp4';target=OUT/'verification'
    assert not target.exists(),f'Refusing to overwrite {target}'
    manifest=json.loads((OUT/'source-manifest.json').read_text())
    for path,expected in manifest['inputs'].items():assert sha(ROOT/path)==expected,path
    assert manifest['native_projection'] and not manifest['browser_executed']
    tl=json.loads((OUT/'timeline.json').read_text());mapping=json.loads((OUT/'frame-map.json').read_text())
    assert (OUT/'timeline.json').read_bytes()==(APPROVED/'timeline.json').read_bytes()
    assert sha(OUT/'timeline.json')==manifest['timeline_sha256'] and sha(OUT/'frame-map.json')==manifest['frame_map_sha256']
    assert (OUT/'narration.srt').read_bytes()==(APPROVED/'narration.srt').read_bytes()
    assert len(mapping)==FRAMES and [r['frame'] for r in mapping]==list(range(FRAMES))
    assert [r['source_frame'] for r in mapping[:54]]==list(range(45))+[44]*9
    assert [r['source_frame'] for r in mapping[-105:]]==list(range(780,885))
    assert sum(r['source']=='v19' for r in mapping)==159
    expected_events={'target':341,'match':500,'release':525,'credit':549,'claim':609,'confirmed':644,'paid':654}
    assert EVENTS==expected_events and list(EVENTS.values())==sorted(EVENTS.values())
    for n,expected in [(499,'sealed'),(500,'sealed'),(524,'sealed'),(525,'public'),(548,'public'),
        (549,'Ready to claim'),(608,'Ready to claim'),(609,'Claiming…'),(643,'Claiming…'),
        (644,'Confirmed'),(653,'Confirmed'),(654,'Paid'),(682,'Paid')]:assert state(n)==expected,(n,state(n))
    assert protocol_camera(480/30)[2]>=700 and protocol_camera(545/30)[2]<200
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(movie)]))
    video=next(s for s in probe['streams'] if s['codec_type']=='video');audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert (video['width'],video['height'],video['codec_name'],video['pix_fmt'])==(1920,1080,'h264','yuv420p')
    assert video['r_frame_rate']==video['avg_frame_rate']=='30/1' and int(video['nb_read_frames'])==FRAMES
    assert abs(float(video['duration'])-DURATION)<.001 and abs(float(probe['format']['duration'])-DURATION)<.05
    assert video['color_range']=='tv' and all(video[k]=='bt709' for k in ['color_space','color_primaries','color_transfer'])
    assert (audio['codec_name'],audio['sample_rate'],audio['channels'])==('aac','48000',2)
    assert abs(float(audio['duration'])-DURATION)<.05
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(movie),'-f','null','-'],check=True)
    actual_sound,approved_sound=audio_packets(movie),audio_packets(APPROVED/'sunset-launch-v22.mp4')
    assert len(actual_sound)==len(approved_sound)
    assert [p['data_hash'] for p in actual_sound]==[p['data_hash'] for p in approved_sound],'Changed AAC packet'
    assert [p['pts'] for p in actual_sound]==[p['pts'] for p in approved_sound],'Changed narration timing'
    atoms=[]
    with movie.open('rb') as stream:
        while stream.tell()<movie.stat().st_size:
            offset=stream.tell();size,kind=struct.unpack('>I4s',stream.read(8))
            if size==1:size=struct.unpack('>Q',stream.read(8))[0]
            if size==0:size=movie.stat().st_size-offset
            assert size>=8 and offset+size<=movie.stat().st_size
            atoms.append(kind.decode('ascii'));stream.seek(offset+size)
    assert atoms.index('moov')<atoms.index('mdat')
    older=json.loads((APPROVED/'verification/report.json').read_text())
    retained={**older['older_movies_preserved'],older['movie']:older['sha256']};assert len(retained)==23
    for path,expected in retained.items():assert sha(Path(path) if Path(path).is_absolute() else ROOT/path)==expected,path
    previous_poster=np.asarray(Image.open(ROOT/'.publication/sunset-launch-v20/poster.png').convert('RGB'))
    assert int(previous_poster[830:1020,260:1660].min())<120
    landmarks=set(EVENTS.values())|{n-1 for n in EVENTS.values()}|{420,450,480,520,530,540,560,608}
    dense=set()
    phases={p['id']:p for p in tl['phases']}
    for p in tl['phases']:
        first,last=round(p['start']*30),round(p['end']*30)-1
        landmarks.update([first,min(first+18,last),min(first+45,last),last])
        dense.update(range(first,last+1,6))
    selected={};brand=[];native=[];footer=[];source_n=-1
    final,original=prior.decode(movie),prior.decode(MASTER)
    try:
        for row in mapping:
            n=row['frame'];pixels=prior.take(final)
            if row['source']=='v19':
                while source_n<row['source_frame']:expected=prior.take(original);source_n+=1
                mae=prior.error(pixels,expected);assert mae<5,(n,mae)
                brand.append({'frame':n,'source_frame':source_n,'mae':round(mae,5)})
                if row['phase']=='closing':
                    minimum=int(pixels[830:1020,260:1660].min());assert minimum>180,(n,minimum)
                    footer.append({'frame':n,'minimum_channel':minimum})
            elif n in landmarks|dense:
                expected=np.asarray(picture(phases[row['phase']],n));mae=prior.error(pixels,expected)
                assert mae<5,(n,mae);native.append({'frame':n,'phase':row['phase'],'mae':round(mae,5)})
            if n in landmarks|dense:selected[n]=Image.fromarray(pixels.copy())
        assert not final.stdout.read(1) and final.wait()==0 and original.wait()==0
    finally:
        for process in [final,original]:
            if process.poll() is None:process.terminate();process.wait()
    loudness=subprocess.run(['ffmpeg','-hide_banner','-i',str(movie),'-vn','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True).stderr
    lufs=float(re.findall(r'I:\s*(-?[\d.]+) LUFS',loudness)[-1]);peak=float(re.findall(r'Peak:\s*(-?[\d.]+) dBFS',loudness)[-1])
    assert -16<=lufs<=-14 and peak<=-1.5
    target.mkdir();(target/'loudness.log').write_text(loudness)
    for n in sorted(landmarks):selected[n].save(target/f'frame-{n:04}.png')
    sheet(selected,sorted(landmarks),OUT/'story-sheet.jpg');sheet(selected,sorted(landmarks),OUT/'phone-sheet.jpg',390)
    for start in range(0,len(dense),35):sheet(selected,sorted(dense)[start:start+35],target/f'transitions-{start//35+1}.jpg')
    selected[FRAMES-1].save(OUT/'poster.png')
    report={'ok':True,'movie':str(movie.relative_to(ROOT)),'sha256':sha(movie),'bytes':movie.stat().st_size,
        'frames':FRAMES,'duration':DURATION,'probe':probe,'full_decode':True,'atoms':atoms,'brand_comparisons':brand,
        'max_brand_mae':max(c['mae'] for c in brand),'closing_clean_frames':len(footer),'closing_footer_checks':footer,
        'v20_url_negative_control_detected':True,'native_comparisons':native,'max_native_mae':max(c['mae'] for c in native),
        'unchanged_aac_packet_count':len(actual_sound),'aac_packet_hashes_and_timestamps_identical':True,
        'unchanged_timeline_and_subtitles':True,'finance_events':EVENTS,'camera_macro_and_pullback_checked':True,
        'encoded_lufs':lufs,'encoded_true_peak_dbtp':peak,'older_movies_preserved':retained,
        'inspection_frames':sorted(selected),'browser_execution':False,'new_transactions':False,
        'continuous_playback_verified':False,'perceptual_listening_claimed':False,'author_visual_review_required':True}
    (target/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['ok','frames','duration','max_brand_mae','max_native_mae','unchanged_aac_packet_count','encoded_lufs','encoded_true_peak_dbtp']}))


if __name__=='__main__':
    main()
