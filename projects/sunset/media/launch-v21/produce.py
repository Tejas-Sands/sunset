#!/usr/bin/env python3
"""SUNSET V21: deterministic perspective collage and original logo-only ending.

Run check/stills/render. Reuses V20's exact retained helpers; outputs remain in
ignored .publication/sunset-launch-v21. No browser, network, model or installation.
"""
import argparse
from functools import lru_cache
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

if sys.flags.optimize:
    raise SystemExit('Run without Python optimization; verification requires assertions.')

SOURCE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('sunset_v20',SOURCE.parent/'launch-v20/finish.py')
base=importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
ROOT,MASTER,CAPTURE=base.ROOT,base.MASTER,base.CAPTURE
sha,text,font,ease,smooth=base.sha,base.text,base.font,base.ease,base.smooth
W,H,FPS,FRAMES,DURATION=1920,1080,30,930,31
OUT=ROOT/'.publication/sunset-launch-v21'
INK,PAPER,CORAL=base.INK,base.PAPER,base.CORAL
NATIVE_ROI=base.NATIVE_ROI
NATIVE_BOX=(842,550,1622,700)


def project_corners(center,size,camera,ry=0,rz=0):
    w,h=size; cx,cy,push=camera
    ay,az=math.radians(ry),math.radians(rz)
    result=[]
    for u,v in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]:
        x,z=u*math.cos(ay),-u*math.sin(ay)
        px=center[0]+x*math.cos(az)-v*math.sin(az)
        py=center[1]+x*math.sin(az)+v*math.cos(az)
        depth=1600+center[2]+z-push
        assert depth>150, 'Paper crossed the camera near plane'
        result.append((960+1600*(px-cx)/depth,540+1600*(py-cy)/depth))
    return result


def sheet(frame,texture,center,size,camera,ry=0,rz=0):
    quad=project_corners(center,size,camera,ry,rz)
    left=max(0,math.floor(min(p[0] for p in quad))); right=min(W,math.ceil(max(p[0] for p in quad)))
    top=max(0,math.floor(min(p[1] for p in quad))); bottom=min(H,math.ceil(max(p[1] for p in quad)))
    if right<=left or bottom<=top: return
    # Inverse homography maps the actual projected plane to its original pixels.
    rows=[]; values=[]
    for (x,y),(u,v) in zip(quad,[(0,0),(texture.width,0),(texture.width,texture.height),(0,texture.height)]):
        x-=left; y-=top
        rows.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]])
        values.extend([u,v])
    coefficients=np.linalg.solve(np.asarray(rows),np.asarray(values))
    warped=texture.transform((right-left,bottom-top),Image.Transform.PERSPECTIVE,
                             coefficients,Image.Resampling.BICUBIC)
    frame.paste(warped,(left,top),warped)


def curve(a,b,c,d):
    return [tuple((1-t)**3*a[j]+3*(1-t)**2*t*b[j]+3*(1-t)*t*t*c[j]+t**3*d[j]
                  for j in [0,1]) for t in np.linspace(0,1,30)]


@lru_cache(maxsize=1)
def artwork():
    pages=[]
    for i,colour in enumerate(['#e7b936','#dce5c9','#dc6b47']):
        page=Image.new('RGBA',(920,1200),colour); d=ImageDraw.Draw(page)
        text(page,(70,80),['LEARN','MAKE','SHARE'][i],80)
        if i==0:
            d.line([(160,920),(470,350),(770,920),(160,920)],fill=INK,width=18,joint='curve')
            for y,x0,x1 in [(730,260,670),(560,355,575)]: d.line((x0,y,x1,y),fill=INK,width=14)
            for x,y in [(160,920),(470,350),(770,920)]: d.ellipse((x-38,y-38,x+38,y+38),fill=colour,outline=INK,width=12)
        elif i==1:
            d.ellipse((210,370,750,910),outline=INK,width=24)
            d.ellipse((365,525,595,755),outline=INK,width=20)
            for j in range(8):
                a=j*math.pi/4
                d.line((480+285*math.cos(a),640+285*math.sin(a),480+355*math.cos(a),640+355*math.sin(a)),fill=INK,width=22)
            d.arc((250,420,700,870),20,120,fill=CORAL,width=28)
        else:
            d.line(curve((455,1040),(420,800),(540,600),(480,300)),fill=INK,width=22)
            leaves=[((455,750),(235,750),(100,570),(145,385),(365,390),(460,540)),
                    ((485,575),(725,560),(860,350),(810,235),(585,245),(485,420)),
                    ((455,1000),(700,1000),(850,820),(800,660),(565,665),(455,835))]
            for start,a,b,end,c,d0 in leaves:
                d.polygon(curve(start,a,b,end)+curve(end,c,d0,start),fill=INK)
            d.ellipse((435,225,535,325),fill=CORAL)
        d.line((70,1070,850,1070),fill=INK,width=3)
        text(page,(70,1100),'A USEFUL IDEA, SHARED',44)
        pages.append(page)
    maker,room,hands=base.assets()
    portrait=Image.new('RGBA',(620,745),'#e5b83a'); portrait.paste(maker,(25,25),maker)
    draft=Image.new('RGBA',(800,1000),'#f3edda'); d=ImageDraw.Draw(draft)
    for y,width in [(160,510),(235,620),(310,470),(790,620),(865,510)]: d.line((80,y,80+width,y),fill='#769077',width=6)
    d.line(curve((80,700),(250,180),(420,980),(700,420)),fill=CORAL,width=20)
    edge=Image.new('RGBA',(160,1200),'#e8b83a')
    return pages,portrait,draft,hands,edge,room


def reader(time):
    frame=Image.new('RGB',(W,H),PAPER)
    pages,*_=artwork()
    for i in range(3):
        arrive=ease((time-.1-i*.13)/.6)
        fan=smooth((time-1.15)/1.9)
        center=(1250+850*(1-arrive)+(i-1)*(180+160*fan),
                620+(i-1)*90+220*(1-arrive),400+i*180)
        sheet(frame,pages[i],center,(920,1200),(960,540,0),
              ry=28*(1-arrive)+(i-1)*9,rz=(i-1)*(7+12*fan))
    # Native pixels travel only with the incoming paper, then land axis-aligned.
    arrive=ease(time/.36); x=790+round(1200*(1-arrive)); y=360+round(130*(1-arrive))
    d=ImageDraw.Draw(frame)
    d.rectangle((x+13,y+17,x+1033,y+437),fill='#1c3c2d24')
    d.rectangle((x,y,x+1020,y+420),fill='#fffdf7',outline='#c9d0bf',width=2)
    text(frame,(x+52,y+32),'OPEN-SOURCE MAINTAINER HANDBOOK',25,'#536759')
    text(frame,(x+52,y+83),'Keep a usable offline copy',52)
    frame.paste(Image.open(CAPTURE).convert('RGB').crop(NATIVE_ROI),(x+52,y+190))
    # Foreground text stays on quiet strips while the copy fan changes depth.
    d.rectangle((0,0,W,285),fill=PAPER)
    text(frame,(110,100),'Use it. Share it. Offline.',116)
    for i,(y0,phrase) in enumerate([(365,'No account.'),(510,'No wallet.'),(655,'Keep the file.')]):
        progress=ease((time-.14-i*.16)/.25)
        offset=round(70*(1-progress)); width=round(d.textlength(phrase,font=font(88)))
        d.rectangle((91-offset,y0-10,132+width-offset,y0+111),fill=PAPER)
        text(frame,(110-offset,y0),phrase,88)
    d.rectangle((0,890,760,H),fill=PAPER)
    text(frame,(110,928),'Existing handbook example',30,'#536759')
    return frame


def continuation(time):
    pages,portrait,draft,hands,edge,room=artwork()
    travel=-130*(1-ease(time/.55))+2000*smooth((time-.85)/2.9)
    push=-100*(1-ease(time/.55))+330*smooth((time-.7)/2.9)
    push+=320*(smooth((time-.7)/.45)-smooth((time-1.4)/.4))
    push+=270*(smooth((time-2)/.4)-smooth((time-2.65)/.5))
    camera=(960+travel,540+110*smooth(time/3.8),push)
    crop=round(120-80*smooth(time/3.8))
    frame=room.crop((crop,0,crop+W,H))
    # Distant prints, maker, draft, hands and a near foreground edge occupy
    # independent depths. Translation and push change their relative motion.
    for i,texture in reversed(list(enumerate(pages))):
        sheet(frame,texture,(2200+i*390,660+(i%2)*80,350+i*140),(650,845),camera,
              ry=[-18,16,-7][i]+8*(1-ease((time-1.7-i*.16)/.6)),rz=[10,-10,6][i])
    sheet(frame,portrait,(1400,610,100),(620,745),camera,ry=19-28*ease(time/.8),rz=-5)
    sheet(frame,draft,(650,815,-20),(800,1000),camera,ry=13,rz=3)
    sheet(frame,hands,(610,950,-280),(1350,900),camera,ry=-6,rz=-4)
    sheet(frame,edge,(2040,710,-530),(160,1400),camera,ry=-12,rz=10)
    d=ImageDraw.Draw(frame)
    for y,phrase in [(88,'Make the next'),(230,'free thing possible.')]:
        width=round(d.textlength(phrase,font=font(110)))
        d.rectangle((88,y-4,140+width,y+132),fill=INK)
        text(frame,(112,y),phrase,110,'#f7f0df')
    if time<.34:
        previous=reader(3.6)
        # The retained paper becomes a fast foreground wipe into the maker's room.
        offset=round(-W*smooth(time/.34))
        frame.paste(previous,(offset,0))
    return frame


def payoff(time):
    frame=Image.new('RGB',(W,H),'#f8f5ed')
    for i,(words,y,colour) in enumerate([('[ FREE TO USE ]',345,INK),('[ CREATOR PAID ]',573,CORAL)]):
        progress=ease((time-i*.15)/.4)
        x=960+round((-1 if i==0 else 1)*1250*(1-progress))
        text(frame,(x,y),words,100,colour,anchor='mt')
    if time<.18:
        radius=max(0,12*(1-ease(time/.18)))
        ImageDraw.Draw(frame).ellipse((960-radius,540-radius,960+radius,540+radius),fill=INK)
    return frame


def frame_map():
    result=[]
    def add(source,**extra): result.append({'frame':len(result),'source':source,**extra})
    for n in range(492):
        add('v19',source_frame=n)
        if n in [428,488]:
            for _ in range(12 if n==428 else 9): add('v19',source_frame=n,explicit_reading_hold=True)
    for scene,count in [('reader',108),('continuation',114)]:
        for n in range(count): add(scene,scene_frame=n)
    for n in range(690,714): add('v19',source_frame=n)
    for n in range(72): add('payoff',scene_frame=n)
    for n in range(780,879): add('v19',source_frame=n,closing=True)
    assert len(result)==FRAMES
    return result


def check():
    sources=base.inputs()
    sources[str((SOURCE.parent/'launch-v20/finish.py').relative_to(ROOT))]=sha(SOURCE.parent/'launch-v20/finish.py')
    quad=project_corners((960,540,0),(960,540),(960,540,0))
    assert np.allclose(quad,[(480,270),(1440,270),(1440,810),(480,810)])
    assert np.allclose(project_corners((960,540,0),(960,540),(960,540,800)),[(0,0),(1920,0),(1920,1080),(0,1080)])
    mapping=frame_map()
    assert mapping[441]['source_frame']==429 and mapping[486]['source_frame']==474
    assert mapping[513]['source']=='reader' and mapping[621]['source']=='continuation'
    assert mapping[759]['source']=='payoff' and mapping[831]['source_frame']==780
    return sources


def render(sources):
    output=OUT/'sunset-launch-v21.mp4'; picture=OUT/'picture-before-colour-tags.mp4'
    assert not output.exists() and not picture.exists()
    assert (OUT/'audio/mix.wav').exists(), 'Run audio.py first'
    mapping=frame_map()
    decoder=subprocess.Popen(['ffmpeg','-v','error','-i',str(MASTER),'-frames:v','879','-an','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
    with (OUT/'render.log').open('x') as log:
        encoder=subprocess.Popen(['ffmpeg','-v','warning','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30',
            '-i','-','-i',str(OUT/'audio/mix.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-preset','medium','-crf','15',
            '-pix_fmt','yuv420p','-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709',
            '-c:a','aac','-b:a','320k','-ar','48000','-ac','2','-movflags','+faststart','-t',str(DURATION),str(picture)],
            stdin=subprocess.PIPE,stderr=log)
        source_n=-1
        try:
            for item in mapping:
                if item['source']=='v19':
                    while source_n<item['source_frame']:
                        data=decoder.stdout.read(W*H*3); assert len(data)==W*H*3
                        source_n+=1
                    image=Image.frombytes('RGB',(W,H),data)
                else: image=globals()[item['source']](item['scene_frame']/FPS)
                encoder.stdin.write(image.tobytes())
                if item['frame']%150==0: print(f"Rendered {item['frame']}/{FRAMES}",flush=True)
            encoder.stdin.close(); assert encoder.wait()==0
            # The shorter ending deliberately omits source879..884.
            assert decoder.wait()==0
        finally:
            for process in [decoder,encoder]:
                if process.poll() is None: process.terminate(); process.wait()
    base.tag_colour(picture,output)
    (OUT/'frame-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
    manifest={'inputs':sources,'source':{str(p.relative_to(ROOT)):sha(p) for p in SOURCE.glob('*.py')},
        'frames':FRAMES,'duration':DURATION,'fps':FPS,'native_roi':NATIVE_ROI,'native_destination':NATIVE_BOX,
        'stable_native_frames':[524,620],'closing_frames':[831,929],'closing_overlays':False,
        'method':'Native perspective collage; retained V19 frames at1x with explicit12/9-frame holds. No browser render.'}
    (OUT/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(output)


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('command',choices=['check','stills','render'])
    args=parser.parse_args(); sources=check(); OUT.mkdir(parents=True,exist_ok=True)
    if args.command=='check': print(json.dumps({'ok':True,'frames':FRAMES,'duration':DURATION,'projection_checks':2})); return
    if args.command=='stills':
        for name,image in [('reader',reader(1.8)),('maker',continuation(.8)),('travel',continuation(2.3)),('prints',continuation(3.55)),('payoff',payoff(1))]:
            image.save(OUT/(name+'.png')); image.resize((390,219),Image.Resampling.LANCZOS).save(OUT/(name+'-390.png'))
        print(OUT); return
    render(sources)


if __name__=='__main__': main()
