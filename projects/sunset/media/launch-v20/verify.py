#!/usr/bin/env python3
"""Verify the completed finishing cut, including decoded source/native pixels."""
import json
from pathlib import Path
import re
import subprocess

import numpy as np
from PIL import Image, ImageDraw

from finish import ROOT, OUT, MASTER, CAPTURE, NATIVE_ROI, NATIVE_BOX, sha


def decode(path):
    return subprocess.Popen(['ffmpeg','-v','error','-xerror','-i',str(path),'-an',
                             '-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)


def take(process):
    data=process.stdout.read(1920*1080*3)
    assert len(data)==1920*1080*3, 'Incomplete decoded frame'
    return np.frombuffer(data,dtype=np.uint8).reshape(1080,1920,3)


def error(a,b):
    return float(np.mean(np.abs(a.astype(np.int16)-b.astype(np.int16))))


def main():
    movie=OUT/'sunset-launch-v20.mp4'
    target=OUT/'verification'
    assert not target.exists(), f'Refusing to overwrite {target}'
    manifest=json.loads((OUT/'source-manifest.json').read_text())
    for relative,expected in {**manifest['inputs'],**manifest['source']}.items():
        assert sha(ROOT/relative)==expected, relative
    mapping=json.loads((OUT/'frame-map.json').read_text())
    assert len(mapping)==1020 and [r['frame'] for r in mapping]==list(range(1020))
    for output,source in [(0,0),(401,401),(402,402),(428,428),(449,428),
                          (450,429),(495,474),(509,488),(527,488),(530,491),
                          (774,690),(797,713),(885,780),(989,884),(1019,884)]:
        assert mapping[output]['source_frame']==source, (output,source)
    assert [r['frame'] for r in mapping if r['source']=='reader']==list(range(531,657))
    assert [r['frame'] for r in mapping if r['source']=='continuation']==list(range(657,774))
    assert [r['frame'] for r in mapping if r['source']=='payoff']==list(range(798,885))
    assert sum(bool(r.get('explicit_reading_hold')) for r in mapping)==69
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(movie)]))
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert (video['width'],video['height'],video['codec_name'],video['pix_fmt'])==(1920,1080,'h264','yuv420p')
    assert video['r_frame_rate']==video['avg_frame_rate']=='30/1' and int(video['nb_read_frames'])==1020
    assert float(video['duration'])==34 and abs(float(probe['format']['duration'])-34)<.05
    assert video['color_range']=='tv' and all(video[k]=='bt709' for k in ['color_space','color_primaries','color_transfer'])
    assert (audio['codec_name'],audio['sample_rate'],audio['channels'])==('aac','48000',2)
    assert abs(float(audio['duration'])-34)<.05
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(movie),'-f','null','-'],check=True)
    # Atom order is checked directly, independently of encoder arguments.
    import struct
    atoms=[]
    with movie.open('rb') as stream:
        while stream.tell()<movie.stat().st_size:
            offset=stream.tell(); size,kind=struct.unpack('>I4s',stream.read(8))
            if size==1: size=struct.unpack('>Q',stream.read(8))[0]
            if size==0: size=movie.stat().st_size-offset
            assert size>=8 and offset+size<=movie.stat().st_size
            atoms.append(kind.decode('ascii')); stream.seek(offset+size)
    assert atoms.index('moov')<atoms.index('mdat')
    previous=json.loads((ROOT/'.publication/sunset-launch-v19/verification-delivery/final-report.json').read_text())
    retained={**previous['older_movies_preserved'],previous['movie']:previous['sha256']}
    assert len(retained)==20
    for path,expected in retained.items(): assert sha(Path(path) if Path(path).is_absolute() else ROOT/path)==expected,path
    x0,y0,x1,y1=NATIVE_BOX
    expected_native=np.asarray(Image.open(CAPTURE).convert('RGB').crop(NATIVE_ROI).resize((x1-x0,y1-y0),Image.Resampling.LANCZOS))
    assert (x1-x0)/(NATIVE_ROI[2]-NATIVE_ROI[0])==(y1-y0)/(NATIVE_ROI[3]-NATIVE_ROI[1])
    final,original=decode(movie),decode(MASTER)
    source_n=-1; expected=None
    comparisons=[]; native_errors=[]; selected={}
    landmarks=[0,36,70,100,130,180,246,315,374,392,418,440,456,485,505,
               540,570,615,650,675,696,735,765,785,810,835,870,920,960,1019]
    dense=set(range(519,681,3))|set(range(765,906,3))
    try:
        for item in mapping:
            pixels=take(final)
            n=item['frame']
            if item['source'].startswith('v19'):
                while source_n<item['source_frame']:
                    expected=take(original); source_n+=1
                # CTA occupies only the lower closing band; brand/tagline pixels stay intact.
                height=820 if item['source']=='v19-closing' else 1080
                measured=error(pixels[:height],expected[:height])
                assert measured<5, (n,measured)
                comparisons.append({'frame':n,'source_frame':source_n,'mae':round(measured,5),'region_height':height})
            elif item['source']=='reader':
                measured=error(pixels[y0:y1,x0:x1],expected_native)
                assert measured<5,(n,measured)
                native_errors.append({'frame':n,'mae':round(measured,5)})
            if n in set(landmarks)|dense:
                selected[n]=Image.fromarray(pixels.copy())
        assert not final.stdout.read(1) and final.wait()==0
        assert original.wait()==0
    finally:
        for process in (final,original):
            if process.poll() is None: process.terminate(); process.wait()
    sound=json.loads((OUT/'audio/qa.json').read_text())
    assert sha(OUT/'audio/mix.wav')==sound['master_sha256']
    assert sound['voice'] is None and sound['music_is_continuous'] and len(sound['cues'])==29
    assert all(c['id']!='real-checklist-input' for c in sound['cues'])
    cues={c['id']:c['peak_seconds'] for c in sound['cues']}
    assert cues['deliberate-withdrawal']==15.0 and abs(cues['withdrawal-confirmed']-16.15)<1e-9
    loudness=subprocess.run(['ffmpeg','-hide_banner','-i',str(movie),'-vn','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True).stderr
    lufs=float(re.findall(r'I:\s*(-?[\d.]+) LUFS',loudness)[-1])
    peak=float(re.findall(r'Peak:\s*(-?[\d.]+) dBFS',loudness)[-1])
    assert -16<=lufs<=-14 and peak<=-1.5,(lufs,peak)
    target.mkdir()
    (target/'loudness.log').write_text(loudness)
    for n in landmarks:
        selected[n].save(target/f'frame-{n:04}.png')
    def sheet(numbers,path,width=384,columns=5):
        height=round(width*1080/1920)
        board=Image.new('RGB',(columns*width,((len(numbers)+columns-1)//columns)*(height+28)),'#f7f5ed')
        draw=ImageDraw.Draw(board)
        for i,n in enumerate(numbers):
            x=(i%columns)*width; y=(i//columns)*(height+28)
            board.paste(selected[n].resize((width,height),Image.Resampling.LANCZOS),(x,y))
            draw.text((x+6,y+height+5),f'{n:04} / {n/30:.2f}s',fill='#183c2e')
        board.save(path)
    sheet(landmarks,OUT/'story-sheet.jpg')
    sheet(landmarks,OUT/'phone-sheet.jpg',width=390)
    for start in range(0,len(dense),35):
        sheet(sorted(dense)[start:start+35],target/f'transitions-{start//35+1}.jpg')
    selected[1019].save(OUT/'poster.png')
    report={'ok':True,'movie':str(movie.relative_to(ROOT)),'sha256':sha(movie),'bytes':movie.stat().st_size,
        'frames':1020,'duration':34,'probe':probe,'full_decode':True,'atoms':atoms,
        'source_frame_comparisons':comparisons,'max_source_mae':max(c['mae'] for c in comparisons),
        'native_frames':native_errors,'max_native_mae':max(c['mae'] for c in native_errors),
        'encoded_lufs':lufs,'encoded_true_peak_dbtp':peak,'older_movies_preserved':retained,
        'inspection_frames':sorted(selected),'author_inspection_required':True,
        'new_transactions':False,'new_browser_capture':False,'narration':False}
    (target/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['ok','frames','duration','max_source_mae','max_native_mae','encoded_lufs','encoded_true_peak_dbtp']}))


if __name__=='__main__':
    main()
