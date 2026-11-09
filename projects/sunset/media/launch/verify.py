#!/usr/bin/env python3
"""Verify the accepted final bundle without earlier films, models or renderers."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import subprocess

import numpy as np
from PIL import Image,ImageDraw,ImageFilter

import native
from produce import SOURCE,BUNDLE,W,H,FPS,FRAMES,DURATION,EVENTS,sha,picture,prepare,camera,book_pose,key_pose,credit_pose,window


def packets(path):
    result=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_packets',
                     '-show_data_hash','sha256','-of','json',str(path)]))
    return [{k:p[k] for k in ['data_hash','pts','dts','duration','size','flags','side_data_list'] if k in p}
            for p in result['packets']]


def packet_digest(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def error(a,b):
    return float(np.mean(np.abs(a.astype(np.int16)-b.astype(np.int16))))


def payoff_contrast(pixels):
    region=pixels[300:620,360:1560].astype(float)/255
    linear=np.where(region<=.04045,region/12.92,((region+.055)/1.055)**2.4)
    luminance=linear@np.array([.2126,.7152,.0722]);ratios=[]
    for words,y in [('[ FREE TO USE ]',0),('[ CREATOR PAID ]',155)]:
        mask=Image.new('L',(1200,320));d=ImageDraw.Draw(mask)
        d.text((600,y),words,font=native.font(89),fill=255,anchor='mt')
        core=np.asarray(mask.filter(ImageFilter.MinFilter(3)))>250
        width=d.textlength(words,font=native.font(89));box=Image.new('L',mask.size)
        ImageDraw.Draw(box).rectangle((600-width/2-20,y,600+width/2+20,y+110),fill=255)
        background=(np.asarray(box)>0)&(np.asarray(mask.filter(ImageFilter.MaxFilter(11)))==0)
        ratios.append((float(np.median(luminance[core]))+.05)/(float(np.quantile(luminance[background],.9))+.05))
    return ratios


def visible_plane(actual,expected,center,size,cam):
    quad=native.project_corners(native.rotate(*center,cam),size,cam[:3],ry=cam[3])
    mask=Image.new('L',(W,H));ImageDraw.Draw(mask).polygon(quad,fill=255)
    pixels=np.asarray(mask)>0
    assert int(pixels.sum())>10000,'Critical plane is not visibly projected'
    mae=error(actual[pixels],expected[pixels])
    assert mae<5,('Critical plane mismatch',mae)
    bright=(actual[pixels].min(axis=1)>130).sum()
    assert bright>200,'Critical plane has lost its light lettering/material'
    return {'visible_pixels':int(pixels.sum()),'light_pixels':int(bright),'mae':round(mae,5)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=BUNDLE/'verification.json')
    args=parser.parse_args()
    manifest=json.loads((SOURCE/'bundle.json').read_text())
    for name,expected in manifest['files'].items():
        path=BUNDLE/name
        assert path.stat().st_size==expected['bytes'] and sha(path)==expected['sha256'],name
    for name,expected in manifest['textures'].items():
        with Image.open(BUNDLE/'assets'/(name+'.png')) as image:
            assert list(image.size)==expected['size'] and image.mode==expected['mode'],name
            assert hashlib.sha256(image.tobytes()).hexdigest()==expected['pixel_sha256'],name
    movie=BUNDLE/'sunset-launch.mp4'
    assert sha(movie)==manifest['accepted_movie']['sha256']=='57348b1f7fea925c31b61650808bcc65f47b70d74b1889831674e8bb2e48022f'
    assert movie.stat().st_size==23121135
    timeline,mapping=prepare();phases={p['id']:p for p in timeline['phases']}
    srt=(BUNDLE/'narration.srt').read_text()
    for phase in timeline['phases']:
        assert round((phase['end']-phase['start'])*FPS)==phase['frames']
        if 'spoken' in phase:
            assert phase['spoken'] in srt
            assert phase['start']<=phase['voice_start']<phase['voice_end']<=phase['end']
    assert EVENTS=={'target':341,'match':500,'release':525,'credit':549,'claim':609,'confirmed':644,'paid':654}
    for n in [499,500,504,510]:
        center,turn=key_pose(n/FPS);a=math.radians(turn);dx=(650-360)/720*350;dy=(175-165)/330*160
        tip=(center[0]+dx*math.cos(a)-dy*math.sin(a),center[1]+dx*math.sin(a)+dy*math.cos(a))
        if n>=500:assert math.dist(tip,(1105,638))<1e-7
        else:assert tip[0]<1105
    for n in [525,530,540,548,683,728,808,935,1048]:
        center,scale,angle=book_pose(n/FPS);w=450*scale;theta=math.radians(angle)
        cx=center[0]-w/2+w/2*math.cos(theta);cz=center[2]-30-w/2*math.sin(theta)
        assert abs(cx-w/2*math.cos(theta)-1105)<1e-7
        assert abs(cz+w/2*math.sin(theta)+30)<1e-7
        if n>=548:assert abs(angle+154)<1e-7
    for n in range(683,809):
        assert book_pose(n/FPS)[2]==-154 and native.state(n)=='Paid'
        assert window(n/FPS,18.22,18.65,39.2,40.8)>.99 and credit_pose(n/FPS)[1]>=.5
    boundaries=sorted(set(round(p['start']*FPS) for p in timeline['phases'][1:])|{549})
    anchors=[]
    for n in boundaries:
        poses=[]
        for f in [n-1,n,n+1]:
            t=f/FPS;cam=camera(t);center,scale,angle=book_pose(t)
            poses.append(np.array([*cam,*center,scale,angle,*native.point(*center,cam)],dtype=float))
        step=float(max(np.max(np.abs(poses[1]-poses[0])),np.max(np.abs(poses[2]-poses[1]))))
        velocity=float(np.max(np.abs(poses[2]-poses[1]*2+poses[0])))
        assert step<25 and velocity<3,(n,step,velocity)
        anchors.append({'frame':n,'max_step':step,'max_velocity_change':velocity})
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(movie)]))
    video=next(p for p in probe['streams'] if p['codec_type']=='video');audio=next(p for p in probe['streams'] if p['codec_type']=='audio')
    assert (video['width'],video['height'],video['codec_name'],video['pix_fmt'])==(W,H,'h264','yuv420p')
    assert video['r_frame_rate']==video['avg_frame_rate']=='30/1' and int(video['nb_read_frames'])==FRAMES
    assert abs(float(video['duration'])-DURATION)<.001 and abs(float(probe['format']['duration'])-DURATION)<.05
    assert video['color_range']=='tv' and all(video[k]=='bt709' for k in ['color_space','color_transfer','color_primaries'])
    assert (audio['codec_name'],audio['sample_rate'],audio['channels'])==('aac','48000',2)
    assert abs(float(audio['duration'])-DURATION)<.05
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(movie),'-f','null','-'],check=True)
    actual_audio=packets(movie)
    assert len(actual_audio)==manifest['aac_packets']['count']==2095
    assert packet_digest(actual_audio)==manifest['aac_packets']['canonical_sha256']
    assert actual_audio==packets(BUNDLE/'assets/soundtrack.m4a')
    atoms=[]
    with movie.open('rb') as stream:
        while stream.tell()<movie.stat().st_size:
            offset=stream.tell();size,kind=struct.unpack('>I4s',stream.read(8))
            if size==1:size=struct.unpack('>Q',stream.read(8))[0]
            if size==0:size=movie.stat().st_size-offset
            assert size>=8 and offset+size<=movie.stat().st_size
            atoms.append(kind.decode('ascii'));stream.seek(offset+size)
    assert atoms.index('moov')<atoms.index('mdat')
    baselines={r['frame']:r for r in manifest['native_frames']}
    landmarks=set(baselines)|set(range(1235,FRAMES))|{n+d for n in boundaries for d in [-1,0,1]}
    landmarks|=set(range(0,FRAMES,30))
    payoff_frames={1175,1185,1200,1215}
    decoder=subprocess.Popen(['ffmpeg','-v','error','-xerror','-i',str(movie),'-an','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    comparisons=[];differences=[];previous=None;dark_count=0;footer_count=0;payoff=[];visibility=[]
    try:
        for row in mapping:
            n=row['frame'];data=decoder.stdout.read(W*H*3)
            assert len(data)==W*H*3,('Incomplete decoded frame',n)
            pixels=np.frombuffer(data,dtype=np.uint8).reshape(H,W,3)
            world=pixels[385:985:8,::8]
            if previous is not None:differences.append({'frame':n,'world_mae':error(world,previous)})
            previous=world.copy()
            if n in landmarks:
                expected=np.asarray(picture(phases[row['phase']],n))
                if n in baselines:assert hashlib.sha256(expected.tobytes()).hexdigest()==baselines[n]['pixel_sha256'],('Native identity changed',n)
                mae=error(pixels,expected);assert mae<5,(n,mae)
                comparisons.append({'frame':n,'mae':round(mae,5)})
                if n in [683,728,808]:
                    cam=camera(n/FPS);center,scale=credit_pose(n/FPS)
                    visibility.append({'frame':n,'paid_credit':visible_plane(pixels,expected,center,(650*scale,444*scale),cam),
                                       'open_resource':visible_plane(pixels,expected,(1330,590,5),(450,585),cam)})
            if n<54 or n>=1235:
                assert int(max(pixels[:64,:64].max(),pixels[:64,-64:].max()))<90,(n,'Light endpoint')
                dark_count+=1
            if n>=1263:
                assert int(pixels[830:1000,260:1660].max())<95,(n,'Unexpected bright ending footer')
                footer_count+=1
            if n in payoff_frames:
                ratios=payoff_contrast(pixels);assert min(ratios)>=4.5,(n,ratios)
                payoff.append({'frame':n,'text_backplate_contrast':ratios})
        assert not decoder.stdout.read(1) and decoder.wait()==0
    finally:
        if decoder.poll() is None:decoder.terminate();decoder.wait()
    boundary_pixels=[]
    for row in differences:
        if row['frame'] not in boundaries:continue
        neighbours=[r['world_mae'] for r in differences if 0<abs(r['frame']-row['frame'])<=5]
        allowed=max(4,1.8*float(np.median(neighbours)))
        assert row['world_mae']<=allowed,row
        boundary_pixels.append({**row,'allowed_world_mae':allowed})
    loudness=subprocess.run(['ffmpeg','-hide_banner','-i',str(movie),'-vn','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True).stderr
    lufs=float(re.findall(r'I:\s*(-?[\d.]+) LUFS',loudness)[-1]);peak=float(re.findall(r'Peak:\s*(-?[\d.]+) dBFS',loudness)[-1])
    assert -16<=lufs<=-14 and peak<=-1.5
    report={'ok':True,'movie':str(movie.relative_to(native.ROOT)),'sha256':sha(movie),'bytes':movie.stat().st_size,
            'bundle_files_verified':len(manifest['files']),'frames':FRAMES,'duration':DURATION,'full_video_audio_decode':True,
            'probe':probe,'atoms':atoms,'aac_packet_count':len(actual_audio),'aac_identity_fields':manifest['aac_packets']['fields'],
            'aac_identity_digest':packet_digest(actual_audio),'soundtrack_packets_identical':True,'native_identity_frames':len(baselines),
            'native_encoded_comparisons':comparisons,'max_native_encoded_mae':max(r['mae'] for r in comparisons),
            'key_contact_fixed_hinge':True,'refund_open_paid_pose_checks':126,'refund_visibility':visibility,
            'boundary_poses':anchors,'boundary_pixels':boundary_pixels,'dark_endpoint_frames':dark_count,
            'clean_ending_footer_frames':footer_count,'payoff_contrast':payoff,'encoded_lufs':lufs,'encoded_true_peak_dbtp':peak,
            'archival_report_rerun':False,'browser_executed':False,'new_protocol_actions':False,
            'continuous_human_playback_claimed':False,'perceptual_listening_claimed':False}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['ok','sha256','frames','aac_packet_count','native_identity_frames','max_native_encoded_mae','encoded_lufs']}))


if __name__=='__main__':main()
