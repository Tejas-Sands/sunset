#!/usr/bin/env python3
"""Verify actual V24 continuity, dark bookends, key hinge and immutable sound."""
import importlib.util
import json
import math
from pathlib import Path
import re
import struct
import subprocess

import numpy as np
from PIL import Image,ImageDraw,ImageFilter

from produce import ROOT,OUT,SOURCE,APPROVED,MASTER,FRAMES,FPS,DURATION,EVENTS,sha,picture,camera,book_pose,key_pose,credit_pose,window,v23

spec=importlib.util.spec_from_file_location('decode_helpers',SOURCE.parent/'launch-v22/verify.py')
helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)


def packets(path):
    result=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-of','json',str(path)]))
    return [(p['data_hash'],p['pts'],p['size'],p['flags']) for p in result['packets']]


def payoff_contrast(pixels):
    region=pixels[300:620,360:1560].astype(float)/255
    linear=np.where(region<=.04045,region/12.92,((region+.055)/1.055)**2.4)
    luminance=linear@np.array([.2126,.7152,.0722]);ratios=[]
    for words,y in [('[ FREE TO USE ]',0),('[ CREATOR PAID ]',155)]:
        mask=Image.new('L',(1200,320));d=ImageDraw.Draw(mask)
        d.text((600,y),words,font=v23.font(89),fill=255,anchor='mt')
        core=np.asarray(mask.filter(ImageFilter.MinFilter(3)))>250
        width=d.textlength(words,font=v23.font(89));box=Image.new('L',mask.size)
        ImageDraw.Draw(box).rectangle((600-width/2-20,y,600+width/2+20,y+110),fill=255)
        background=(np.asarray(box)>0)&(np.asarray(mask.filter(ImageFilter.MaxFilter(11)))==0)
        ratio=(float(np.median(luminance[core]))+.05)/(float(np.quantile(luminance[background],.9))+.05)
        ratios.append(ratio)
    return ratios


def sheet(selected,numbers,path,width=384):
    height=round(width*1080/1920);board=Image.new('RGB',(width*5,math.ceil(len(numbers)/5)*(height+28)),'#071a17');d=ImageDraw.Draw(board)
    for i,n in enumerate(numbers):
        x=i%5*width;y=i//5*(height+28);board.paste(selected[n].resize((width,height),Image.Resampling.LANCZOS),(x,y))
        d.text((x+7,y+height+5),f'{n:04} / {n/30:.2f}s',fill='#f3efdc')
    board.save(path)


def main():
    movie=OUT/'sunset-launch-v24.mp4';target=OUT/'verification';assert not target.exists()
    manifest=json.loads((OUT/'source-manifest.json').read_text())
    for path,expected in manifest['inputs'].items():assert sha(ROOT/path)==expected,path
    assert manifest['global_camera_objects'] and manifest['native_dark_brand'] and not manifest['browser_executed']
    assert sha(OUT/'timeline.json')==manifest['timeline_sha256'] and sha(OUT/'frame-map.json')==manifest['frame_map_sha256']
    assert (OUT/'timeline.json').read_bytes()==(APPROVED/'timeline.json').read_bytes()
    assert (OUT/'narration.srt').read_bytes()==(APPROVED/'narration.srt').read_bytes()
    tl=json.loads((OUT/'timeline.json').read_text());mapping=json.loads((OUT/'frame-map.json').read_text())
    assert len(mapping)==FRAMES and [r['frame'] for r in mapping]==list(range(FRAMES)) and all(r['source']=='native' for r in mapping)
    assert EVENTS=={'target':341,'match':500,'release':525,'credit':549,'claim':609,'confirmed':644,'paid':654}
    for n in [499,500,504,510]:
        center,turn=key_pose(n/30);a=math.radians(turn);dx=(650-360)/720*350;dy=(175-165)/330*160
        tip=(center[0]+dx*math.cos(a)-dy*math.sin(a),center[1]+dx*math.sin(a)+dy*math.cos(a))
        if n>=500:assert math.dist(tip,(1105,638))<1e-7
        else:assert tip[0]<1105
    for n in [525,530,540,548,683,728,808,935,1048]:
        center,scale,angle=book_pose(n/30);w=450*scale;theta=math.radians(angle)
        cx=center[0]-w/2+w/2*math.cos(theta);cz=center[2]-30-w/2*math.sin(theta)
        assert abs(cx-w/2*math.cos(theta)-1105)<1e-7
        assert abs(cz+w/2*math.sin(theta)+30)<1e-7
        if n>=548:assert abs(angle+154)<1e-7
    for n in range(683,809):
        assert book_pose(n/30)[2]==-154 and v23.state(n)=='Paid'
        assert window(n/30,18.22,18.65,39.2,40.8)>.99 and credit_pose(n/30)[1]>=.5
    boundaries=sorted(set(round(p['start']*30) for p in tl['phases'][1:])|{549})
    anchors=[]
    for n in boundaries:
        poses=[]
        for f in [n-1,n,n+1]:
            t=f/30;c=camera(t);center,scale,angle=book_pose(t);xy=v23.point(*center,c)
            poses.append(np.array([*c,*center,scale,angle,*xy],dtype=float))
        assert np.max(np.abs(poses[1]-poses[0]))<25 and np.max(np.abs(poses[2]-poses[1]))<25,(n,poses)
        assert np.max(np.abs((poses[2]-poses[1])-(poses[1]-poses[0])))<3,(n,'Pose velocity reset')
        anchors.append({'frame':n,'max_anchor_step':float(np.max(np.abs(poses[1]-poses[0]))),'max_velocity_change':float(np.max(np.abs(poses[2]-poses[1]*2+poses[0])))})
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(movie)]))
    video=next(p for p in probe['streams'] if p['codec_type']=='video');audio=next(p for p in probe['streams'] if p['codec_type']=='audio')
    assert (video['width'],video['height'],video['codec_name'],video['pix_fmt'])==(1920,1080,'h264','yuv420p')
    assert video['r_frame_rate']==video['avg_frame_rate']=='30/1' and int(video['nb_read_frames'])==FRAMES
    assert abs(float(video['duration'])-DURATION)<.001 and abs(float(probe['format']['duration'])-DURATION)<.05
    assert video['color_range']=='tv' and all(video[k]=='bt709' for k in ['color_space','color_transfer','color_primaries'])
    assert (audio['codec_name'],audio['sample_rate'],audio['channels'])==('aac','48000',2)
    assert abs(float(audio['duration'])-DURATION)<.05
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(movie),'-f','null','-'],check=True)
    actual_audio=packets(movie);assert actual_audio==packets(APPROVED/'sunset-launch-v22.mp4') and len(actual_audio)==2095
    atoms=[]
    with movie.open('rb') as stream:
        while stream.tell()<movie.stat().st_size:
            offset=stream.tell();size,kind=struct.unpack('>I4s',stream.read(8))
            if size==1:size=struct.unpack('>Q',stream.read(8))[0]
            if size==0:size=movie.stat().st_size-offset
            assert size>=8 and offset+size<=movie.stat().st_size;atoms.append(kind.decode('ascii'));stream.seek(offset+size)
    assert atoms.index('moov')<atoms.index('mdat')
    old=json.loads((ROOT/'.publication/sunset-launch-v23/verification/report.json').read_text())
    retained={**old['older_movies_preserved'],old['movie']:old['sha256']};assert len(retained)==24
    for path,expected in retained.items():assert sha(Path(path) if Path(path).is_absolute() else ROOT/path)==expected,path
    first_pass=ROOT/'.publication/sunset-launch-v24/sunset-launch-v24.mp4'
    assert sha(first_pass)=='a4268b1421312e39f6bee7b098ea13be6f45c2fe7ec4de9745bdf4330deac553'
    first_manifest=json.loads((first_pass.parent/'source-manifest.json').read_text())
    assert sha(first_pass.parent/'first-pass-source/produce.py')==first_manifest['inputs']['projects/sunset/media/launch-v24/produce.py']
    first_pixels=subprocess.check_output(['ffmpeg','-v','error','-ss','39.5','-i',str(first_pass),'-frames:v','1','-an','-pix_fmt','rgb24','-f','rawvideo','-'])
    first_payoff_ratios=payoff_contrast(np.frombuffer(first_pixels,dtype=np.uint8).reshape(1080,1920,3))
    assert min(first_payoff_ratios)<4.5,'Unprotected actual payoff must fail the reading control'
    # Actual V23's replaced-resource cut is a negative control for the same lower-world metric.
    raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(543/30),'-i',str(ROOT/old['movie']),'-frames:v','13','-an','-pix_fmt','rgb24','-f','rawvideo','-'])
    prior=np.frombuffer(raw,dtype=np.uint8).reshape(13,1080,1920,3)
    prior_changes=[helpers.error(prior[i-1,385:985:8,::8],prior[i,385:985:8,::8]) for i in range(1,13)]
    old_cut=prior_changes[5];old_neighbours=float(np.median(prior_changes[:5]+prior_changes[6:]))
    assert old_cut>max(4,1.8*old_neighbours),(old_cut,old_neighbours)
    prior_poster=np.asarray(Image.open(ROOT/'.publication/sunset-launch-v23/poster.png').convert('RGB'))
    assert float(prior_poster[:64,:64].mean())>180,'Prior cream endpoint must fail the dark-theme control'
    v20=np.asarray(Image.open(ROOT/'.publication/sunset-launch-v20/poster.png').convert('RGB'))
    old_url_mask=v20[830:1000,260:1660].min(axis=2)<120;assert old_url_mask.any()
    payoff_frames={1175,1185,1200,1215}
    landmarks=set(EVENTS.values())|{n-1 for n in EVENTS.values()}|{0,18,45,53,60,500,504,520,525,530,540,548,549,560,608,643,728,808,850,1048,1162,1200,1234,1235,1260,1280,1339}|payoff_frames
    for p in tl['phases']:
        first,last=round(p['start']*30),round(p['end']*30)-1;landmarks.update([first,min(first+45,last),last])
    dense=set(range(0,FRAMES,6))|{n+d for n in boundaries for d in range(-6,7) if 0<=n+d<FRAMES}
    native=[];selected={};differences=[];previous=None;previous_world=None;closing=[];dark=[];payoff_checks=[]
    phases={p['id']:p for p in tl['phases']};decoder=helpers.decode(movie)
    try:
        for row in mapping:
            n=row['frame'];pixels=helpers.take(decoder);small=pixels[::8,::8];world=pixels[385:985:8,::8]
            if previous is not None:differences.append({'frame':n,'full_mae':helpers.error(small,previous),'world_mae':helpers.error(world,previous_world)})
            previous=small.copy();previous_world=world.copy()
            if n in landmarks|dense or n>=1235:
                expected=np.asarray(picture(phases[row['phase']],n));mae=helpers.error(pixels,expected);assert mae<5,(n,mae)
                native.append({'frame':n,'phase':row['phase'],'mae':round(mae,5)})
            if n<54 or n>=1235:
                value=int(max(pixels[:64,:64].max(),pixels[:64,-64:].max()));assert value<90,(n,'Light endpoint',value)
                dark.append({'frame':n,'corner_max':value})
            if n>=1235:closing.append(n)
            if n in payoff_frames:
                ratios=payoff_contrast(pixels);assert min(ratios)>=4.5,(n,ratios)
                payoff_checks.append({'frame':n,'core_text_to_backplate_contrast':ratios})
            if n>=1263:
                roi=pixels[830:1000,260:1660];assert int(roi.max())<95,(n,'Unexpected bright ending footer')
                mutant=roi.copy();mutant[old_url_mask]=[243,239,220];assert int(mutant.max())>150
            if n in landmarks|dense:selected[n]=Image.fromarray(pixels.copy())
        assert not decoder.stdout.read(1) and decoder.wait()==0
    finally:
        if decoder.poll() is None:decoder.terminate();decoder.wait()
    boundary_checks=[r for r in differences if r['frame'] in boundaries]
    for row in boundary_checks:
        neighbours=[r['world_mae'] for r in differences if 0<abs(r['frame']-row['frame'])<=5]
        median=float(np.median(neighbours));row['neighbour_median_world_mae']=median
        # A sustained camera pan may change many pixels. Reject an isolated chapter reset.
        row['allowed_world_mae']=max(4,1.8*median)
        assert row['world_mae']<=row['allowed_world_mae'],row
    loudness=subprocess.run(['ffmpeg','-hide_banner','-i',str(movie),'-vn','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True).stderr
    lufs=float(re.findall(r'I:\s*(-?[\d.]+) LUFS',loudness)[-1]);peak=float(re.findall(r'Peak:\s*(-?[\d.]+) dBFS',loudness)[-1]);assert -16<=lufs<=-14 and peak<=-1.5
    target.mkdir();(target/'loudness.log').write_text(loudness)
    for n in sorted(landmarks):selected[n].save(target/f'frame-{n:04}.png')
    sheet(selected,sorted(landmarks),OUT/'story-sheet.jpg');sheet(selected,sorted(landmarks),OUT/'phone-sheet.jpg',390)
    for i,n in enumerate(boundaries):sheet(selected,[f for f in range(n-6,n+7) if f in selected],target/f'handoff-{i+1:02}-{n}.jpg')
    for offset in range(0,len(dense),35):sheet(selected,sorted(dense)[offset:offset+35],target/f'motion-{offset//35+1:02}.jpg')
    selected[FRAMES-1].save(OUT/'poster.png')
    report={'ok':True,'movie':str(movie.relative_to(ROOT)),'sha256':sha(movie),'bytes':movie.stat().st_size,'frames':FRAMES,'duration':DURATION,
        'probe':probe,'full_decode':True,'atoms':atoms,'native_comparisons':native,'max_native_mae':max(r['mae'] for r in native),
        'closing_full_frame_checks':len(closing),'dark_intro_outro_checks':dark,'closing_footer_url_negative_control':True,'prior_light_endpoint_negative_control':True,
        'aac_packet_count':len(actual_audio),'aac_content_pts_sizes_flags_identical':True,'timeline_subtitles_identical':True,'finance_events':EVENTS,
        'fixed_hinge_and_key_contact':True,'successful_resource_stays_open_in_refund_branch':True,'boundary_anchor_checks':anchors,'boundary_pixel_checks':boundary_checks,
        'max_boundary_world_mae':max(r['world_mae'] for r in boundary_checks),'prior_v23_reset_negative_control_mae':old_cut,'prior_v23_reset_neighbour_median_mae':old_neighbours,'adjacent_frame_metrics':differences,
        'encoded_lufs':lufs,'encoded_true_peak_dbtp':peak,'older_movies_preserved':retained,'inspection_frames':sorted(selected),
        'payoff_contrast_checks':payoff_checks,'first_pass_payoff_negative_control_ratios':first_payoff_ratios,'first_v24_pass_preserved':{'movie':str(first_pass.relative_to(ROOT)),'sha256':sha(first_pass)},
        'browser_executed':False,'new_protocol_actions':False,'continuous_human_playback_claimed':False,'perceptual_listening_claimed':False,'author_review_required':True}
    (target/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['ok','frames','duration','max_native_mae','aac_packet_count','closing_full_frame_checks','max_boundary_world_mae','prior_v23_reset_negative_control_mae','encoded_lufs']}))


if __name__=='__main__':main()
