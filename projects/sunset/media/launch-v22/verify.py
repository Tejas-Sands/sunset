#!/usr/bin/env python3
"""Check the actual V22 encode, retained finance pixels, voice and old masters."""
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess

import numpy as np
from PIL import Image, ImageDraw

from produce import ROOT, OUT, MASTER, SOURCE, picture, sha


def decode(path):
    return subprocess.Popen(['ffmpeg','-v','error','-xerror','-i',str(path),'-an',
                             '-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)


def take(process):
    data=process.stdout.read(1920*1080*3)
    assert len(data)==1920*1080*3,'Incomplete decoded frame'
    return np.frombuffer(data,dtype=np.uint8).reshape(1080,1920,3)


def error(a,b):
    return float(np.mean(np.abs(a.astype(np.int16)-b.astype(np.int16))))


def main():
    movie=OUT/'sunset-launch-v22.mp4';target=OUT/'verification'
    assert not target.exists(),f'Refusing to overwrite {target}'
    manifest=json.loads((OUT/'source-manifest.json').read_text())
    for path,expected in manifest['sources'].items():assert sha(ROOT/path)==expected,path
    assert manifest['native_renderer'] and not manifest['browser_rendered']
    assert sha(MASTER)==manifest['master_sha256']
    assert sha(OUT/'timeline.json')==manifest['timeline_sha256']
    tl=json.loads((OUT/'timeline.json').read_text());duration=tl['duration'];count=tl['frames']
    mapping=json.loads((OUT/'frame-map.json').read_text());phases={p['id']:p for p in tl['phases']}
    assert count==1340 and abs(duration-1340/30)<1e-9
    assert len(mapping)==count and [r['frame'] for r in mapping]==list(range(count))
    spans={'intro':(0,54),'sponsor':(210,276),'custody':(276,360),
           'release':(360,429),'claim':(429,492),'closing':(780,885)}
    holds={}
    for name,(a,b) in spans.items():
        rows=[r for r in mapping if r['phase']==name]
        assert all(r['source']=='v19' for r in rows)
        sequence=[r['source_frame'] for r in rows]
        assert sorted(set(sequence))==list(range(a,b)) and sequence==sorted(sequence)
        holds[name]=len(sequence)-(b-a)
    assert holds=={'intro':0,'sponsor':37,'custody':0,'release':54,'claim':11,'closing':0}
    assert sum(r['source']=='v19' for r in mapping)==543
    assert [r['source_frame'] for r in mapping[-105:]]==list(range(780,885))
    config=json.loads((SOURCE/'narration.json').read_text())
    takes=json.loads((OUT/'voice/takes.json').read_text())
    assert tl['synthetic_voice']==takes['voice']=='af_bella' and takes['synthetic']
    for line,take_info in zip(config['lines'],takes['takes'],strict=True):
        p=phases[line['id']]
        assert p['spoken']==line['spoken'] and take_info['text']==line['spoken']
        assert sha(OUT/p['take'])==p['take_sha256']==take_info['sha256']
        assert p['start']<=p['voice_start']<p['voice_end']<=p['end']
        assert abs(p['voice_end']-p['voice_start']-take_info['duration'])<1e-8
        assert line['spoken'] in (OUT/'narration.srt').read_text()
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames',
                     '-show_streams','-show_format','-of','json',str(movie)]))
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert (video['width'],video['height'],video['codec_name'],video['pix_fmt'])==(1920,1080,'h264','yuv420p')
    assert video['r_frame_rate']==video['avg_frame_rate']=='30/1' and int(video['nb_read_frames'])==count
    assert abs(float(video['duration'])-duration)<.001 and abs(float(probe['format']['duration'])-duration)<.05
    assert video['color_range']=='tv' and all(video[k]=='bt709' for k in ['color_space','color_transfer','color_primaries'])
    assert (audio['codec_name'],audio['sample_rate'],audio['channels'])==('aac','48000',2)
    assert abs(float(audio['duration'])-duration)<.05
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(movie),'-f','null','-'],check=True)
    atoms=[]
    with movie.open('rb') as stream:
        while stream.tell()<movie.stat().st_size:
            offset=stream.tell();size,kind=struct.unpack('>I4s',stream.read(8))
            if size==1:size=struct.unpack('>Q',stream.read(8))[0]
            if size==0:size=movie.stat().st_size-offset
            assert size>=8 and offset+size<=movie.stat().st_size
            atoms.append(kind.decode('ascii'));stream.seek(offset+size)
    assert atoms.index('moov')<atoms.index('mdat')
    previous=json.loads((ROOT/'.publication/sunset-launch-v21/verification/report.json').read_text())
    retained={**previous['older_movies_preserved'],previous['movie']:previous['sha256']}
    assert len(retained)==22
    for path,expected in retained.items():assert sha(Path(path) if Path(path).is_absolute() else ROOT/path)==expected,path
    inherited=json.loads((ROOT/'.publication/sunset-launch-v21/source-manifest.json').read_text())['inputs']
    for path,expected in inherited.items():assert sha(ROOT/path)==expected,path
    old_poster=np.asarray(Image.open(ROOT/'.publication/sunset-launch-v20/poster.png').convert('RGB'))
    assert int(old_poster[830:1020,260:1660].min())<120,'URL negative control must detect V20 ink'
    landmarks=set()
    for p in tl['phases']:
        first=round(p['start']*30);last=round(p['end']*30)-1
        landmarks.update([first,min(first+18,last),min(first+45,last),last])
    dense=set()
    for p in tl['phases']:
        dense.update(range(round(p['start']*30),round(p['end']*30),6))
    selected={};comparisons=[];native=[];footer=[]
    final,original=decode(movie),decode(MASTER);source_n=-1
    try:
        for row in mapping:
            n=row['frame'];pixels=take(final)
            if row['source']=='v19':
                while source_n<row['source_frame']:expected=take(original);source_n+=1
                mae=error(pixels,expected);assert mae<5,(n,mae)
                comparisons.append({'frame':n,'source_frame':source_n,'mae':round(mae,5)})
                if row['phase']=='closing':
                    minimum=int(pixels[830:1020,260:1660].min())
                    assert minimum>180,('Unexpected ending ink',n,minimum)
                    footer.append({'frame':n,'minimum_channel':minimum})
            elif n in dense|landmarks:
                expected=np.asarray(picture(phases[row['phase']],row['scene_frame']/30))
                mae=error(pixels,expected);assert mae<5,(n,mae)
                native.append({'frame':n,'phase':row['phase'],'mae':round(mae,5)})
            if n in dense|landmarks:selected[n]=Image.fromarray(pixels.copy())
        assert not final.stdout.read(1) and final.wait()==0 and original.wait()==0
    finally:
        for process in [final,original]:
            if process.poll() is None:process.terminate();process.wait()
    sound=json.loads((OUT/'audio/qa.json').read_text())
    assert sha(OUT/'audio/mix.wav')==manifest['audio_sha256']==sound['master_sha256']
    assert sound['synthetic'] and sound['voice']=='af_bella' and sound['continuous_music']
    assert min(r['voice_above_music_rms_db'] for r in sound['voice_music_ratios'])>8
    spec=importlib.util.spec_from_file_location('helpers',SOURCE.parent/'launch-v10/prepare_audio.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    encoded=helper.decode(movie);mixed=helper.decode(OUT/'audio/mix.wav')
    assert len(mixed)==round(duration*48000) and abs(len(encoded)-len(mixed))<=1024
    limit=min(len(encoded),len(mixed));encoded=encoded[:limit];mixed=mixed[:limit]
    correlation=float(np.corrcoef(encoded.ravel(),mixed.ravel())[0,1]);assert correlation>.99
    waveform_mae=float(np.mean(np.abs(encoded-mixed)));assert waveform_mae<.01
    loudness=subprocess.run(['ffmpeg','-hide_banner','-i',str(movie),'-vn','-af','ebur128=peak=true',
                             '-f','null','-'],capture_output=True,text=True,check=True).stderr
    lufs=float(re.findall(r'I:\s*(-?[\d.]+) LUFS',loudness)[-1])
    peak=float(re.findall(r'Peak:\s*(-?[\d.]+) dBFS',loudness)[-1])
    assert -16<=lufs<=-14 and peak<=-1.5,(lufs,peak)
    target.mkdir();(target/'loudness.log').write_text(loudness)
    for n in sorted(landmarks):selected[n].save(target/f'frame-{n:04}.png')
    def sheet(numbers,path,width=384,columns=5):
        height=round(width*1080/1920)
        board=Image.new('RGB',(columns*width,((len(numbers)+columns-1)//columns)*(height+28)),'#f7f5ed')
        draw=ImageDraw.Draw(board)
        for i,n in enumerate(numbers):
            x=(i%columns)*width;y=(i//columns)*(height+28)
            board.paste(selected[n].resize((width,height),Image.Resampling.LANCZOS),(x,y))
            draw.text((x+6,y+height+5),f'{n:04} / {n/30:.2f}s',fill='#183c2e')
        board.save(path)
    sheet(sorted(landmarks),OUT/'story-sheet.jpg');sheet(sorted(landmarks),OUT/'phone-sheet.jpg',390)
    for start in range(0,len(dense),35):sheet(sorted(dense)[start:start+35],target/f'transitions-{start//35+1}.jpg')
    selected[count-1].save(OUT/'poster.png')
    report={'ok':True,'movie':str(movie.relative_to(ROOT)),'sha256':sha(movie),'bytes':movie.stat().st_size,
        'frames':count,'duration':duration,'probe':probe,'full_decode':True,'atoms':atoms,
        'source_frame_comparisons':comparisons,'max_source_mae':max(c['mae'] for c in comparisons),
        'reading_holds_frames':holds,'closing_full_frame_checks':len(footer),'closing_footer_no_ink_checks':footer,
        'closing_url_or_cta_overlay':False,'url_negative_control_detects_v20':True,
        'native_frame_comparisons':native,'max_native_mae':max(c['mae'] for c in native),
        'encoded_lufs':lufs,'encoded_true_peak_dbtp':peak,'audio_correlation':correlation,'audio_waveform_mae':waveform_mae,
        'min_voice_music_rms_db':min(r['voice_above_music_rms_db'] for r in sound['voice_music_ratios']),
        'older_movies_preserved':retained,'inherited_inputs_preserved':inherited,'inspection_frames':sorted(selected),'author_inspection_required':True,
        'new_transactions':False,'new_browser_capture':False,'browser_composition_rendered':False,
        'voice':'af_bella','synthetic_voice':True,'perceptual_listening_verified':False}
    (target/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['ok','frames','duration','max_source_mae','max_native_mae','encoded_lufs','encoded_true_peak_dbtp','audio_correlation']}))


if __name__=='__main__':
    main()
