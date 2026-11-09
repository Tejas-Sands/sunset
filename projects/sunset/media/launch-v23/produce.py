#!/usr/bin/env python3
"""SUNSET V23: a connected projected protocol world, with unchanged V22 sound."""
import argparse
from functools import lru_cache
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

SOURCE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('narrated',SOURCE.parent/'launch-v22/produce.py')
v22=importlib.util.module_from_spec(spec);spec.loader.exec_module(v22)
ROOT,MASTER=v22.ROOT,v22.MASTER
OUT=ROOT/'.publication/sunset-launch-v23'
APPROVED=ROOT/'.publication/sunset-launch-v22'
W,H,FPS,FRAMES=1920,1080,30,1340
DURATION=FRAMES/FPS
PAPER,WHITE,DARK,MINT,CORAL,QUIET='#f7f5ed','#f3efdc','#071a17','#baf4c6','#f47b50','#88aca0'
font,text,sha,ease,smooth=v22.font,v22.text,v22.sha,v22.ease,v22.smooth
EVENTS={'target':341,'match':500,'release':525,'credit':549,'claim':609,'confirmed':644,'paid':654}


def ramp(value,a,b):
    return smooth((value-a)/(b-a))


def lerp(a,b,p):
    return tuple(x+(y-x)*p for x,y in zip(a,b))


def metadata():
    expected='95fb51bb914c790f584481a5fb1a10dfd5ee449af8fd92ac09af8dafeac7a088'
    assert sha(APPROVED/'sunset-launch-v22.mp4')==expected
    tl=json.loads((APPROVED/'timeline.json').read_text())
    assert tl['frames']==FRAMES and tl['synthetic_voice']=='af_bella'
    original=json.loads((APPROVED/'frame-map.json').read_text())
    for name,source in [('target',252),('match',374),('release',378),('credit',402),('claim',429),('confirmed',464),('paid',474)]:
        assert next(r['frame'] for r in original if r['source']=='v19' and r['source_frame']==source)==EVENTS[name]
    mapping=[]
    for p in tl['phases']:
        a,b=round(p['start']*FPS),round(p['end']*FPS)
        for n in range(a,b):
            if p['id']=='intro':row={'frame':n,'phase':p['id'],'source':'v19','source_frame':min(n,44)}
            elif p['id']=='closing':row={'frame':n,'phase':p['id'],'source':'v19','source_frame':780+n-a}
            else:row={'frame':n,'phase':p['id'],'source':'native','scene_frame':n-a}
            mapping.append(row)
    assert len(mapping)==FRAMES
    return tl,mapping


def rotate(x,y,z,camera):
    angle=math.radians(camera[3] if len(camera)>3 else 0)
    dx=x-1330
    return 1330+dx*math.cos(angle)+z*math.sin(angle),y,-dx*math.sin(angle)+z*math.cos(angle)


def sheet(frame,texture,center,size,camera,ry=0,rz=0):
    yaw=camera[3] if len(camera)>3 else 0
    return v22.sheet(frame,texture,rotate(*center,camera),size,camera[:3],ry=ry+yaw,rz=rz)


def point(x,y,z,camera):
    x,y,z=rotate(x,y,z,camera)
    cx,cy,push=camera[:3];depth=1600+z-push
    assert depth>200
    return (960+1600*(x-cx)/depth,540+1600*(y-cy)/depth)


def line(frame,points,colour,width=2):
    ImageDraw.Draw(frame).line(points,fill=colour,width=width,joint='curve')


@lru_cache(maxsize=1)
def backdrop():
    y,x=np.mgrid[0:H,0:W]
    glow=np.exp(-(((x-1330)/850)**2+((y-620)/650)**2)*1.4)
    rim=np.exp(-(((x-1750)/650)**2+((y-180)/500)**2)*1.8)
    pixels=np.zeros((H,W,3),np.float32)+np.array([5,18,17])
    pixels+=glow[:,:,None]*np.array([9,29,21])+rim[:,:,None]*np.array([12,11,3])
    return Image.fromarray(np.uint8(np.clip(pixels,0,255)))


def stage(time,camera=(960,540,0),floor=True):
    frame=backdrop().copy();d=ImageDraw.Draw(frame)
    if floor:
        drift=65*math.sin(time*.14)
        for x in range(350,2600,150):
            a,b=point(x+drift,960,-100,camera),point(x+drift,960,1800,camera)
            d.line([a,b],fill='#153b31',width=1)
        for z in range(-100,1900,160):
            d.line([point(250+drift,960,z,camera),point(2600+drift,960,z,camera)],fill='#153b31',width=1)
    return frame


def glow(frame,paths,colour=MINT,width=3):
    # Low-resolution bloom keeps the local renderer fast and lettering sharp.
    light=Image.new('RGB',(480,270));d=ImageDraw.Draw(light)
    for path in paths:d.line([(x/4,y/4) for x,y in path],fill=colour,width=max(1,round(width/2)),joint='curve')
    light=light.filter(ImageFilter.GaussianBlur(3)).resize((W,H),Image.Resampling.BILINEAR)
    a=np.asarray(frame,dtype=np.uint16)+np.asarray(light,dtype=np.uint16)//2
    frame.paste(Image.fromarray(np.uint8(np.minimum(a,255))))
    for path in paths:line(frame,path,colour,width)


def orbit(frame,camera,time,radius=500,alpha=1,complete=False):
    points=[]
    for angle in np.linspace(0,math.tau,121):
        points.append(point(1330+radius*math.cos(angle),820,180+radius*.65*math.sin(angle),camera))
    line(frame,points,'#315e4d',2)
    if alpha:
        offset=time*.12
        segment=[point(1330+radius*math.cos(a),820,180+radius*.65*math.sin(a),camera) for a in np.linspace(offset,offset+(math.tau if complete else 1.1),90)]
        glow(frame,[segment],MINT if complete else '#92c8aa',3)


def block(frame,center,size,camera,colour=MINT):
    x,y,z=center;s=size/2
    coordinates=[(x+a*s,y+b*s,z+c*s) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    p=[point(*q,camera) for q in coordinates];d=ImageDraw.Draw(frame)
    for face,fill in [([1,5,6,2],'#28614b'),([0,4,5,1],'#7eaa86'),([0,1,2,3],colour)]:
        poly=[p[i] for i in face];d.polygon(poly,fill=fill);d.line(poly+[poly[0]],fill='#d5f3d3',width=2)


def platform(frame,camera,width=590,y=895):
    top=[point(1330+width*.5*math.cos(a),y,100+width*.32*math.sin(a),camera) for a in np.linspace(0,math.tau,7)[:-1]]
    bottom=[(x,b+48) for x,b in top];d=ImageDraw.Draw(frame)
    d.polygon(bottom,fill='#0a201c')
    for i in range(6):
        j=(i+1)%6;d.polygon([top[i],top[j],bottom[j],bottom[i]],fill='#143a30' if i%2 else '#1c493b')
    d.polygon(top,fill='#224a3c');glow(frame,[top+[top[0]]],MINT,2)


def cage(frame,camera,opening=0):
    spread=180*opening;d=ImageDraw.Draw(frame)
    for side in [-1,1]:
        x=1330+side*(310+spread)
        p=[point(x,y,z,camera) for y,z in [(240,-100),(880,-100),(880,190),(240,190)]]
        d.polygon(p,fill='#193e33');line(frame,p+[p[0]],'#70a98d' if opening<.7 else '#325c4b',2)
    top=[point(x,240,z,camera) for x,z in [(1020-spread,-100),(1640+spread,-100),(1640+spread,190),(1020-spread,190)]]
    line(frame,top+[top[0]],'#729e81',2)
    if opening<.98:
        front=[point(x,y,-105,camera) for x,y in [(1020-spread,240),(1640+spread,240),(1640+spread,880),(1020-spread,880)]]
        line(frame,front+[front[0]],'#5b947c',3)


@lru_cache(maxsize=1)
def art():
    a=v22.art().copy()
    key=Image.new('RGBA',(720,330));d=ImageDraw.Draw(key)
    d.ellipse((25,55,235,265),fill=CORAL,outline='#ffd5a3',width=6)
    d.ellipse((85,115,175,205),fill=(0,0,0,0))
    d.polygon([(230,125),(650,125),(650,225),(575,225),(575,185),(510,185),(510,245),(445,245),(445,185),(230,185)],fill=CORAL)
    d.line([(230,125),(650,125),(650,225)],fill='#ffd5a3',width=5)
    a['key']=key
    mask=key.getchannel('A');edge=ImageChops.subtract(mask.filter(ImageFilter.MaxFilter(11)),mask)
    receiver=Image.new('RGBA',key.size,'#102d24')
    ImageDraw.Draw(receiver).rounded_rectangle((2,2,717,327),radius=24,outline='#69ad88',width=4)
    receiver.paste(Image.new('RGBA',key.size,MINT),(0,0),edge);a['receiver']=receiver
    proof=Image.new('RGBA',(1120,1000),'#132e26');d=ImageDraw.Draw(proof)
    d.rectangle((1,1,1118,998),outline='#8cca9e',width=3)
    for xy,words,size,c in [((65,65),'RECORDED NEAR TESTNET',45,MINT),((65,185),'Creator payout',82,WHITE),((65,310),'0.1 testNEAR',108,WHITE),((65,565),'Offline reader checked',65,MINT),((65,715),'Lantern Trail · 2 Nov 2026',49,WHITE),((65,830),'Recorded run · one operator',45,QUIET)]:text(proof,xy,words,size,c)
    d.line((65,500,1055,500),fill='#54836b',width=3);a['proof-dark']=proof
    return a


def resource(frame,camera,opened=0,scale=1,center=(1330,570,0),time=0):
    a=art();x,y,z=center;w,h=450*scale,585*scale
    shadow=Image.new('RGBA',(460,600),'#173a2b')
    sheet(frame,shadow,(x+18*scale,y+18*scale,z+30),(w,h),camera,ry=-9,rz=-2)
    if opened>0:
        sheet(frame,a['kit-agenda'],(x+40*scale,y,z),(w,h),camera,ry=-4,rz=0)
    sheet(frame,a['kit-cover'],(x-130*scale*opened,y,z-25),(w,h),camera,ry=-9-68*opened,rz=-2-7*opened)


def headline(frame,lines,t,size=94,kicker=None):
    dy=round(26*(1-ease(t/.35)))
    if kicker:text(frame,(106,92+dy),kicker,35,CORAL)
    for i,words in enumerate(lines):text(frame,(104,175+dy+i*(size+25)),words,size,WHITE)
    d=ImageDraw.Draw(frame);d.line((108,145+dy,182,145+dy),fill=CORAL,width=5)


def label(frame,words,colour=QUIET):
    ImageDraw.Draw(frame).rectangle((0,985,W,H),fill=DARK)
    text(frame,(108,1005),words,34,colour)


def central_headline(frame,lines,t,size=88):
    d=ImageDraw.Draw(frame)
    for i,words in enumerate(lines):
        y=70+i*(size+20);width=d.textlength(words,font=font(size))
        d.rectangle((950-width/2,y-8,970+width/2,y+size+18),fill=DARK)
        text(frame,(960,y),words,size,WHITE,anchor='mt')


def protocol_camera(absolute):
    stops=[(9.967,(970,540,50,-17)),(13.4,(970,540,50,-4)),
           (14.35,(1330,550,250,-12)),(15.9,(1260,580,760,4)),
           (17.33,(1260,580,760,4)),(18.15,(970,540,100,0)),(22.767,(970,540,100,0))]
    for (a,start),(b,end) in zip(stops,stops[1:]):
        if absolute<=b:return lerp(start,end,ramp(absolute,a,b))
    return stops[-1][1]


def key_receiver(frame,camera,absolute):
    turn=14*ramp(absolute,16.667,17.3)
    sheet(frame,art()['receiver'],(1330,620,-135),(440,202),camera,ry=-8,rz=turn)


def state(n):
    if n<EVENTS['credit']:return 'sealed' if n<EVENTS['release'] else 'public'
    if n<EVENTS['claim']:return 'Ready to claim'
    if n<EVENTS['confirmed']:return 'Claiming…'
    if n<EVENTS['paid']:return 'Confirmed'
    return 'Paid'


def credit(frame,n,t,camera):
    current=state(n);panel=Image.new('RGBA',(820,560),'#14372c');d=ImageDraw.Draw(panel)
    d.rectangle((1,1,818,558),outline=MINT,width=3)
    text(panel,(60,55),'Creator credit',43,QUIET)
    text(panel,(60,195),current,87,MINT if current in ['Confirmed','Paid'] else WHITE)
    d.line((60,360,760,360),fill='#426f55',width=2)
    if current=='Ready to claim':
        text(panel,(60,418),'Claim payment',47,WHITE)
        d.line([(665,449),(745,449),(720,425)],fill=WHITE,width=4)
        d.line([(745,449),(720,473)],fill=WHITE,width=4)
        if n>=EVENTS['claim']-6:
            r=round(28-14*(n-(EVENTS['claim']-6))/6)
            d.ellipse((705-r,449-r,705+r,449+r),outline=CORAL,width=4)
    elif current=='Claiming…':
        progress=(n-EVENTS['claim'])/(EVENTS['confirmed']-EVENTS['claim'])
        d.line((60,432,60+700*progress,432),fill=MINT,width=10)
    else:
        d.line([(65,440),(90,465),(145,405)],fill=MINT,width=9)
        text(panel,(205,414),'FREE FOR EVERYONE',36,QUIET)
    arrive=ease((n-EVENTS['credit'])/14)
    sheet(frame,panel,(1330,600+70*(1-arrive),-70),(850,580),camera,ry=0,rz=0)


def finance(p,n):
    absolute=n/FPS;t=absolute-p['start'];name=p['id']
    camera=protocol_camera(absolute);frame=stage(absolute,camera)
    orbit(frame,camera,absolute,490,complete=n>=EVENTS['target']);platform(frame,camera)
    if name=='sponsor':
        cage(frame,camera);resource(frame,camera)
        for i in range(8):
            a=math.tau*i/8+.3
            arrive=ramp(absolute,10.05+i*.12,11.15+i*.02)
            far=(1330+650*math.cos(a),725+65*math.sin(a),100+340*math.sin(a))
            near=(1330+330*math.cos(a),825,110+210*math.sin(a))
            block(frame,lerp(far,near,arrive),42,camera)
        headline(frame,['Sponsor a','public release.'],t)
        if n>=EVENTS['target']:text(frame,(1110,168),'TARGET COMPLETE',44,MINT)
    elif name=='custody':
        cage(frame,camera);resource(frame,camera)
        for i in range(8):
            a=math.tau*i/8+.3;block(frame,(1330+330*math.cos(a),825,110+210*math.sin(a)),42,camera)
        if absolute>15.3:
            key_receiver(frame,camera,absolute)
            sheet(frame,art()['key'],(935,620,-170),(440,202),camera,ry=-8,rz=0)
        if absolute<15.3:central_headline(frame,['NEAR holds funds.'],t)
    elif n<EVENTS['credit']:
        opening=ramp(absolute,17.5,18.05)
        cage(frame,camera,opening);resource(frame,camera,opening)
        if absolute<17.5:
            key_receiver(frame,camera,absolute)
            insert=ramp(absolute,16.2,16.667)
            sheet(frame,art()['key'],(935+395*insert,620,-170+15*insert),(440,202),camera,ry=-8,rz=14*ramp(absolute,16.667,17.3))
        central_headline(frame,['Timely release'],t)
        d=ImageDraw.Draw(frame);d.rectangle((78,844,640,970),fill=DARK)
        text(frame,(108,860),'TARGET COMPLETE',35,MINT)
        text(frame,(108,915),'MATCHED KEY · ON TIME' if n>=EVENTS['match'] else 'MATCHING KEY',35,CORAL)
    else:
        credit(frame,n,t,camera)
        headline(frame,['unlocks','creator credit.'] if name=='release' else ['Creator claims','payment.'],t,size=92)
        if name=='claim' and n<EVENTS['confirmed']:
            route=[(1010,930),(1190,930),(1270,880)]
            glow(frame,[route],MINT,2)
            progress=(n-EVENTS['claim'])/(EVENTS['confirmed']-EVENTS['claim'])
            joint=math.dist(route[0],route[1])/(math.dist(route[0],route[1])+math.dist(route[1],route[2]))
            x,y=lerp(route[0],route[1],progress/joint) if progress<=joint else lerp(route[1],route[2],(progress-joint)/(1-joint))
            ImageDraw.Draw(frame).ellipse((x-8,y-8,x+8,y+8),fill=MINT)
    label(frame,'NEAR testnet · protocol illustration · local example')
    return frame


def creator(p,n,next_work=False):
    absolute=n/FPS;t=absolute-p['start'];u=t/(p['end']-p['start'])
    camera=(950+210*ramp(t,1,3.7) if next_work else 950,540,80+55*math.sin(math.pi*u),-8+16*u)
    frame=stage(absolute,camera);orbit(frame,camera,absolute,580);platform(frame,camera,720)
    a=art();sheet(frame,a['creator'],(1460,560,110),(570,685),camera,ry=12-16*ramp(t,0,1),rz=-3)
    resource(frame,camera,scale=.66,center=(1080,740,-110))
    if next_work:
        for i in range(3):
            progress=ramp(t,.8+i*.15,2.4+i*.15)
            sheet(frame,a['kit-cover'],(1650+230*i*progress,780-90*(i%2),300+i*180),(330,430),camera,ry=-18+8*i,rz=-8+9*i)
    else:
        sheet(frame,a['hands'],(1120,1000,-330),(940,627),camera,ry=-5,rz=-3)
    headline(frame,['Make the next','free thing possible.'] if next_work else ['Help creators make','useful work free.'],t,size=88)
    label(frame,'Workshop kit · local example')
    return frame


def kit(p,n,using=False):
    absolute=n/FPS;t=absolute-p['start'];u=t/(p['end']-p['start'])
    camera=(970+20*math.sin(math.pi*u),540,50+75*math.sin(math.pi*u),-10+20*u)
    frame=stage(absolute,camera);orbit(frame,camera,absolute,540,complete=using);platform(frame,camera,680)
    a=art()
    if using:
        spread=ramp(t,.15,2.4)
        locations=[(780,800,310),(1150,430,450),(1780,425,330),(1850,800,480)]
        for i,(x,y,z) in enumerate(locations):
            start=(1330,650,650);center=lerp(start,(x,y,z),spread)
            px,py=point(*center,camera);cx,cy=point(1330,700,0,camera)
            glow(frame,[[(cx,cy),(px,cy),(px,py)]],'#508f70',2)
            sheet(frame,a['kit-cover'],center,(310,405),camera,ry=[18,-16,13,-10][i],rz=[-9,7,-5,5][i])
        resource(frame,camera,1,scale=.80,center=(1390,655,-130))
        headline(frame,['Use it.','Share it.','Offline.'],t,size=100)
    else:
        resource(frame,camera,scale=.90,center=(1180,635,40))
        reveal=ramp(t,.3,1.5)
        sheet(frame,a['kit-agenda'],(1585,640+90*(1-reveal),-50),(420,500),camera,ry=-8+8*reveal,rz=0)
        headline(frame,['A useful workshop.','Ready to share.'],t,size=85)
    label(frame,'Workshop kit · local example' if not using else 'Illustrated shareable copies · same local kit')
    return frame


def refunds(p,n):
    absolute=n/FPS;t=absolute-p['start'];camera=(1330,540,40)
    frame=stage(absolute,camera);orbit(frame,camera,absolute,490,alpha=0);platform(frame,camera,510)
    resource(frame,camera,scale=.63,center=(1370,540,120))
    cage(frame,(1330,540,-290))
    # These are available paths, with no money particle travelling after release.
    for dx in [-270,270]:
        path=[point(1330,840,120,camera),point(1330+dx,840,120,camera),point(1330+dx,920,120,camera)]
        glow(frame,[path],CORAL,3);x,y=path[-1]
        line(frame,[(x-10,y-15),(x,y),(x+10,y-15)],CORAL,3)
        ImageDraw.Draw(frame).ellipse((x-18,y+18,x+18,y+54),outline=MINT,width=3)
    central_headline(frame,['Missed conditions.','Refunds claimable.'],t,size=80)
    text(frame,(108,70),'Alternative outcome',36,CORAL)
    label(frame,'Separate refund claim and withdrawal · protocol illustration')
    return frame


def proof(p,n):
    absolute=n/FPS;t=absolute-p['start'];camera=(960,540,30)
    frame=stage(absolute,camera);orbit(frame,camera,absolute,550);platform(frame,camera,650,y=955)
    sheet(frame,art()['proof-dark'],(1360,600,0),(800,715),camera,ry=9-9*ramp(t,0,.65),rz=0)
    headline(frame,['Core flow,','verified.'],t,size=104)
    label(frame,'Prior Lantern Trail evidence · separate earlier sample')
    return frame


def payoff(p,n):
    t=n/FPS-p['start'];frame=stage(n/FPS,floor=False)
    for i,(words,y,colour) in enumerate([('[ FREE TO USE ]',345,WHITE),('[ CREATOR PAID ]',573,CORAL)]):
        arrive=ease((t-i*.15)/.4);x=960+round((-1 if i==0 else 1)*1250*(1-arrive))
        text(frame,(x,y),words,100,colour,anchor='mt')
    fade=ramp(t,1.85,2.35)
    if fade:frame=Image.blend(frame,Image.new('RGB',(W,H),PAPER),fade)
    return frame


def picture(p,n):
    kind=p['id']
    if kind in ['sponsor','custody','release','claim']:return finance(p,n)
    if kind in ['why','next']:return creator(p,n,kind=='next')
    if kind in ['kit','use']:return kit(p,n,kind=='use')
    if kind=='refund':return refunds(p,n)
    if kind=='proof':return proof(p,n)
    if kind=='payoff':return payoff(p,n)
    raise ValueError(kind)


def prepare():
    tl,mapping=metadata();OUT.mkdir(parents=True,exist_ok=True)
    for name,data in [('timeline.json',tl),('frame-map.json',mapping),('finance-events.json',EVENTS)]:
        (OUT/name).write_text(json.dumps(data,indent=2)+'\n')
    if not (OUT/'narration.srt').exists():shutil.copyfile(APPROVED/'narration.srt',OUT/'narration.srt')
    return tl,mapping


def encode(movie,mapping,tl,proof=False):
    assert not movie.exists();raw=movie.with_name(movie.stem+'-before-tags.mp4');assert not raw.exists()
    phases={p['id']:p for p in tl['phases']}
    original=subprocess.Popen(['ffmpeg','-v','error','-i',str(MASTER),'-an','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE) if any(r['source']=='v19' for r in mapping) else None
    with movie.with_suffix('.log').open('x') as log:
        command=['ffmpeg','-v','warning','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-']
        if proof:command+=['-ss',str(mapping[0]['frame']/FPS)]
        command+=['-i',str(APPROVED/'sunset-launch-v22.mp4'),'-map','0:v','-map','1:a','-c:v','libx264','-preset','medium','-crf','15','-pix_fmt','yuv420p','-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709','-c:a','copy','-movflags','+faststart','-t',str(len(mapping)/FPS),str(raw)]
        encoder=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=log);source_n=-1
        try:
            for i,row in enumerate(mapping):
                if row['source']=='v19':
                    while source_n<row['source_frame']:
                        pixels=original.stdout.read(W*H*3);assert len(pixels)==W*H*3;source_n+=1
                    image=Image.frombytes('RGB',(W,H),pixels)
                else:image=picture(phases[row['phase']],row['frame'])
                encoder.stdin.write(image.tobytes())
                if i%180==0:print(f'Rendered {i}/{len(mapping)}',flush=True)
            encoder.stdin.close();assert encoder.wait()==0
        finally:
            for process in [encoder,original]:
                if process is not None and process.poll() is None:process.terminate();process.wait()
    v22.old.base.tag_colour(raw,movie)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['stills','study','render']);args=parser.parse_args()
    tl,mapping=prepare()
    if args.command=='stills':
        numbers=[]
        for p in tl['phases']:
            if p['id'] in ['intro','closing']:continue
            n=min(round((p['start']+1.5)*FPS),round(p['end']*FPS)-1);image=picture(p,n)
            image.save(OUT/(p['id']+'.png'));image.resize((390,219),Image.Resampling.LANCZOS).save(OUT/(p['id']+'-390.png'))
            numbers.append((p['id'],image))
        board=Image.new('RGB',(1920,math.ceil(len(numbers)/3)*388),PAPER);d=ImageDraw.Draw(board)
        for i,(name,image) in enumerate(numbers):
            x=i%3*640;y=i//3*388;board.paste(image.resize((640,360),Image.Resampling.LANCZOS),(x,y));d.text((x+10,y+365),name,fill='#183c2e')
        board.save(OUT/'direction.jpg');print(OUT/'direction.jpg');return
    if args.command=='study':
        subset=[r for r in mapping if 299<=r['frame']<683]
        encode(OUT/'sunset-web3-motion-study-refined.mp4',subset,tl,proof=True);return
    encode(OUT/'sunset-launch-v23.mp4',mapping,tl)
    inputs=[SOURCE/'produce.py',SOURCE.parent/'launch-v22/produce.py',SOURCE.parent/'launch-v21/produce.py',SOURCE.parent/'launch-v20/finish.py',
            ROOT/'projects/sunset/media/launch-v22/narration.json',ROOT/'projects/sunset/public/packs/workshop-kit.json',
            ROOT/'projects/sunset/evidence/testnet-showcase.json',ROOT/'projects/sunset/evidence/browser-showcase.json',ROOT/'projects/sunset/evidence/testnet-refunds.json',
            APPROVED/'sunset-launch-v22.mp4',APPROVED/'timeline.json',APPROVED/'audio/qa.json',APPROVED/'voice/takes.json',MASTER]
    inherited=json.loads((APPROVED/'verification/report.json').read_text())['inherited_inputs_preserved']
    (OUT/'source-manifest.json').write_text(json.dumps({'inputs':{**inherited,**{str(p.relative_to(ROOT)):sha(p) for p in inputs}},
        'timeline_sha256':sha(OUT/'timeline.json'),'frame_map_sha256':sha(OUT/'frame-map.json'),'native_projection':True,'browser_executed':False,
        'soundtrack':'Unchanged V22 AAC packets, stream-copied without regeneration or time stretching.'},indent=2)+'\n')
    print(OUT/'sunset-launch-v23.mp4')


if __name__=='__main__':
    if sys.flags.optimize:raise SystemExit('Run without Python optimization.')
    main()
