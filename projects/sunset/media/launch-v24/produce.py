#!/usr/bin/env python3
"""One continuous SUNSET world; exact approved narration and native dark bookends."""
import argparse
from functools import lru_cache
import importlib.util
import json
import math
from pathlib import Path
import shutil

import numpy as np
from PIL import Image,ImageDraw

SOURCE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('protocol',SOURCE.parent/'launch-v23/produce.py')
v23=importlib.util.module_from_spec(spec);spec.loader.exec_module(v23)
ROOT,APPROVED=v23.ROOT,v23.APPROVED
MASTER=v23.MASTER
OUT=ROOT/'.publication/sunset-launch-v24/delivery'
W,H,FPS,FRAMES,DURATION=v23.W,v23.H,v23.FPS,v23.FRAMES,v23.DURATION
WHITE,DARK,MINT,CORAL,QUIET=v23.WHITE,v23.DARK,v23.MINT,v23.CORAL,v23.QUIET
font,text,sha,ramp,lerp=v23.font,v23.text,v23.sha,v23.ramp,v23.lerp
EVENTS=v23.EVENTS


def track(t,knots):
    if t<=knots[0][0]:return knots[0][1]
    for (a,start),(b,end) in zip(knots,knots[1:]):
        if t<=b:
            p=ramp(t,a,b)
            return lerp(start,end,p) if isinstance(start,tuple) else start+(end-start)*p
    return knots[-1][1]


def camera(t):
    return track(t,[(0,(1330,540,-120,0)),(1.35,(1330,540,-120,0)),
        (2.6,(1040,540,20,-8)),(6.4,(1040,540,50,-5)),(9.4,(1060,540,65,-9)),
        (13.5,(1080,550,120,-4)),(16,(1180,560,240,2)),(17.2,(1180,560,240,2)),
        (18.9,(1320,550,10,0)),(22,(1320,550,10,0)),(23.6,(1670,550,-200,2)),
        (26.2,(1670,550,-200,2)),(28,(1300,540,-160,-4)),(31,(1280,550,-140,0)),
        (32,(1280,550,20,0)),(34,(1280,550,20,0)),(36,(1260,550,-60,-3)),
        (38.3,(1330,540,-140,0)),(40.8,(1330,540,-80,0)),(DURATION,(1330,540,-80,0))])


def window(t,a,b,c,d):
    return ramp(t,a,b)*(1-ramp(t,c,d))


def fade(texture,alpha):
    if alpha>=.999:return texture
    result=texture.copy();result.putalpha(texture.getchannel('A').point([round(i*max(0,alpha)) for i in range(256)]))
    return result


def sprite(frame,texture,center,size,cam,opacity=1,ry=0,rz=0):
    if opacity>.001:v23.sheet(frame,fade(texture,opacity),center,size,cam,ry=ry,rz=rz)


@lru_cache(maxsize=1)
def art():
    a=v23.art().copy()
    back=Image.new('RGBA',(920,1200),'#b5c7a7');d=ImageDraw.Draw(back)
    d.rectangle((40,40,880,1160),outline='#638c6a',width=4)
    text(back,(460,465),'CC0',140,'#244b37',anchor='mt')
    text(back,(460,665),'FREE TO SHARE',60,'#244b37',anchor='mt');a['back']=back.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    clasp=Image.new('RGBA',(150,150),'#cdd8bb');d=ImageDraw.Draw(clasp)
    d.rounded_rectangle((3,3,146,146),radius=22,outline='#7f9b76',width=5)
    d.rounded_rectangle((68,37,82,113),radius=6,fill='#183c2e');a['clasp']=clasp
    archive=Image.new('RGBA',(1120,1000),'#132e26');d=ImageDraw.Draw(archive)
    d.rectangle((1,1,1118,998),outline='#83bf95',width=3)
    for xy,words,size,c in [((65,55),'PRIOR LANTERN TRAIL',55,MINT),((65,145),'RECORDED NEAR TESTNET',39,QUIET),
        ((65,270),'Creator payout',78,WHITE),((65,395),'0.1 testNEAR',108,WHITE),
        ((65,625),'Offline reader checked',62,MINT),((65,765),'2 November 2026',49,WHITE),((65,865),'Recorded run · one operator',45,QUIET)]:text(archive,xy,words,size,c)
    d.line((65,580,1055,580),fill='#54836b',width=3);a['archive']=archive
    # Exact original SVG foreground geometry, uniformly scaled; its cream tile is omitted for the requested dark theme.
    logo=(ROOT/'projects/sunset/public/icon.svg').read_text()
    assert 'M10 34a22 22 0 0 1 44 0' in logo and 'M11 40h42M16 47h32M23 54h18' in logo
    icon=Image.new('RGBA',(768,768));d=ImageDraw.Draw(icon);s=12
    d.pieslice((10*s,12*s,54*s,56*s),180,360,fill='#d75835')
    for x0,x1,y in [(11,53,40),(16,48,47),(23,41,54)]:
        radius=1.75*s;d.line((x0*s,y*s,x1*s,y*s),fill='#d75835',width=42)
        for x in [x0,x1]:d.ellipse((x*s-radius,y*s-radius,x*s+radius,y*s+radius),fill='#d75835')
    a['mark']=icon.resize((256,256),Image.Resampling.LANCZOS)
    return a


def book_pose(t):
    center=track(t,[(0,(1330,540,0)),(1.35,(1330,540,0)),(2.6,(1180,730,-30)),
        (6.4,(1330,590,0)),(38.3,(1330,590,0)),(41,(1330,540,0)),(DURATION,(1330,540,0))])
    scale=track(t,[(0,.15),(1.35,.15),(2.6,.67),(6.4,1),(38.3,1),(41,.04),(DURATION,.04)])
    angle=-154*ramp(t,17.5,18.22)
    return center,scale,angle


def book(frame,cam,t,center=None,scale=None,angle=None,opacity=1):
    a=art();default_center,default_scale,default_angle=book_pose(t)
    x,y,z=center if center is not None else default_center
    scale=default_scale if scale is None else scale;angle=default_angle if angle is None else angle
    w,h=450*scale,585*scale;spine=x-w/2;theta=math.radians(angle)
    sprite(frame,a['kit-agenda'],(x,y,z+5),(w,h),cam,opacity)
    # The left edge stays fixed in world space through the complete cover hinge.
    cover_center=(spine+w/2*math.cos(theta),y,z-30-w/2*math.sin(theta))
    sprite(frame,a['kit-cover'] if angle>=-90 else a['back'],cover_center,(w,h),cam,opacity,ry=angle)
    return (spine,y,z-30)


def wirebox(frame,cam,center,half,opacity):
    if opacity<.002:return
    x,y,z=center;w,h,depth=half
    points=[v23.point(x+a*w,y+b*h,z+c*depth,cam) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    colour=tuple(round(a+(b-a)*opacity) for a,b in zip((7,26,23),(112,169,141)))
    for a,b in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]:v23.line(frame,[points[a],points[b]],colour,2)


def key_pose(t):
    turn=14*ramp(t,500/30,500/30+.15)
    dx=(650-360)/720*350;dy=(175-165)/330*160;theta=math.radians(turn)
    insert=ramp(t,16.2,500/30)
    return (1105-dx*math.cos(theta)+dy*math.sin(theta)-140*(1-insert),638-dx*math.sin(theta)-dy*math.cos(theta),-85),turn


@lru_cache(maxsize=80)
def credit_texture(state,progress,tap):
    panel=Image.new('RGBA',(820,560),'#14372c');d=ImageDraw.Draw(panel)
    d.rectangle((1,1,818,558),outline=MINT,width=3);text(panel,(60,55),'Creator credit',43,QUIET)
    text(panel,(60,165 if state=='Paid' else 195),state,150 if state=='Paid' else 87,MINT if state in ['Confirmed','Paid'] else WHITE)
    d.line((60,360,760,360),fill='#426f55',width=2)
    if state=='Ready to claim':
        text(panel,(60,418),'Claim payment',47,WHITE)
        d.line([(665,449),(745,449),(720,425)],fill=WHITE,width=4);d.line([(745,449),(720,473)],fill=WHITE,width=4)
        if tap:d.ellipse((705-tap,449-tap,705+tap,449+tap),outline=CORAL,width=4)
    elif state=='Claiming…':d.line((60,432,60+700*progress/16,432),fill=MINT,width=10)
    else:
        d.line([(65,440),(90,465),(145,405)],fill=MINT,width=9);text(panel,(205,414),'FREE FOR EVERYONE',36,QUIET)
    return panel


def credit_pose(t):
    center=track(t,[(0,(1370,780,0)),(18.22,(1370,780,0)),(19.05,(1740,660,-30)),
        (22.25,(1740,660,-30)),(23.3,(1580,850,0)),(30.8,(1580,850,0)),(32,(1030,855,60)),(DURATION,(1030,855,60))])
    scale=track(t,[(0,.03),(18.22,.03),(19.05,1),(22.25,1),(23.3,.50),(DURATION,.50)])
    return center,scale


def copies(frame,cam,t,opacity):
    destinations=[(730,820,430),(1120,420,680),(2090,420,680),(2250,820,430)]
    for i,end in enumerate(destinations):
        depart=ramp(t,27.05+i*.18,29.2+i*.18);gather=ramp(t,38.5+i*.10,41.15)
        origin=(1330,590,50);center=lerp(lerp(origin,end,depart),(1330,540,0),gather)
        local=opacity*ramp(t,27+i*.18,27.5+i*.18)*(1-ramp(t,41,41.6))
        width=300*(1-.91*gather)
        a,b=v23.point(*origin,cam),v23.point(*center,cam)
        if local>.002:
            v23.line(frame,[a,(b[0],a[1]),b],'#365f4b',2)
            sprite(frame,art()['kit-cover'],center,(width,width*1200/920),cam,local,ry=[-12,8,-9,12][i]*(1-gather),rz=[-6,5,-4,5][i]*(1-gather))


CAPTIONS=[(1.8,6.1666666667,['Help creators make','useful work free.']),
    (6.1666666667,9.9666666667,['A useful workshop.','Ready to share.']),
    (9.9666666667,13.4,['Sponsor a','public release.']),(13.4,16.2,['NEAR holds','funds.']),
    (16.2,18.3,['Timely release']),(18.3,20.3,['unlocks','creator credit.']),
    (20.3,22.7666666667,['Creator claims','payment.']),
    (22.7666666667,26.9666666667,['Missed conditions.','Refunds claimable.']),
    (26.9666666667,31.1666666667,['Use it. Share it.','Offline.']),
    (31.1666666667,34.9666666667,['Core flow,','verified.']),
    (34.9666666667,38.7666666667,['Make the next','free thing possible.'])]


def captions(frame,t):
    for start,end,words in CAPTIONS:
        opacity=window(t,start,start+.20,end-.20,end)
        if opacity<.001:continue
        layer=Image.new('RGBA',(1060,385));d=ImageDraw.Draw(layer)
        for x in range(1060):
            a=round(225*(1-ramp(x,780,1060)));d.line((x,0,x,385),fill=(7,26,23,a))
        layer=layer.convert('RGBA')
        d=ImageDraw.Draw(layer);dy=round(14*(1-ramp(t,start,start+.2)))
        d.line((108,126+dy,182,126+dy),fill=CORAL,width=4)
        for i,line in enumerate(words):d.text((104,145+dy+i*110),line,font=font(86),fill=WHITE)
        frame.paste(fade(layer,opacity),(0,0),fade(layer,opacity))
    if 22.3<t<27:
        alpha=window(t,22.3,22.6,26.7,27)
        overlay=Image.new('RGBA',(740,75));text(overlay,(108,8),'Alternative outcome',37,CORAL)
        frame.paste(fade(overlay,alpha),(0,62),fade(overlay,alpha))


def brand(frame,t,start,end):
    local=t-start;remaining=end-t
    opacity=ramp(local,0,.28)*(1-ramp(remaining,0,.40)) if start<2 else ramp(local,0,.40)
    if start<2:opacity=ramp(local,0,.28)*(1-ramp(local,1.5,2.15))
    if opacity<.001:return
    assemble=ramp(local,.22,1.26);size=round(170+46*assemble)
    word='SUNSET';tracking=18;f=font(156,680)
    width=sum(f.getlength(c) for c in word)+tracking*(len(word)-1)
    left=(W-(216+72+width))/2;mark_x=960+(left+108-960)*assemble
    mark=art()['mark'].resize((size,size),Image.Resampling.LANCZOS)
    frame.paste(fade(mark,opacity),(round(mark_x-size/2),round(540-size/2)),fade(mark,opacity))
    letters=Image.new('RGBA',(round(width+60),230));d=ImageDraw.Draw(letters);cursor=0
    for c in word:d.text((cursor,25),c,font=f,fill=WHITE);cursor+=f.getlength(c)+tracking
    alpha=opacity*assemble
    frame.paste(fade(letters,alpha),(round(left+288+35*(1-assemble)),448),fade(letters,alpha))
    if start>2:
        tag=Image.new('RGBA',(1000,80));text(tag,(500,0),'Support once. Share forever.',42,WHITE,anchor='mt')
        frame.paste(fade(tag,alpha),(460,690),fade(tag,alpha))


def picture(phase,n):
    t=n/FPS;cam=camera(t);frame=v23.stage(t,cam)
    world=window(t,.95,2.0,40.55,42.1)
    # The stage, hero and camera use absolute time through every caption/phase boundary.
    if world>.001:
        geometry=frame.copy();v23.orbit(geometry,cam,t,500,alpha=1,complete=t>=341/30);v23.platform(geometry,cam,690)
        frame=Image.blend(frame,geometry,world)
        cage_alpha=window(t,8.7,10,17.5,18.6)*world
        wirebox(frame,cam,(1330,585,40),(310,335,140),cage_alpha)
        actor=track(t,[(0,0),(1.7,0),(2.35,1),(5.6,1),(9.2,.4),(33.2,.4),(36,1),(38.8,1),(41,0)])*world
        actor_center=track(t,[(0,(1660,560,270)),(5.6,(1660,560,270)),(9.2,(3200,550,1100)),
            (33.2,(3200,550,1100)),(36,(1660,560,270)),(38.8,(1660,560,270)),(41,(1330,540,700))])
        sprite(frame,art()['creator'],actor_center,(570,685),cam,actor,ry=-6,rz=-3)
        hands=window(t,1.7,2.3,5.7,7.2)*world
        sprite(frame,art()['hands'],(1220,990,-180),(800,533),cam,hands,ry=-3,rz=-2)
        agenda=window(t,6.0,6.6,8.7,9.9)*world
        pos=track(t,[(0,(1330,620,100)),(6,(1330,620,100)),(7.2,(1740,620,100)),(8.7,(1740,620,100)),(9.9,(1330,590,20)),(DURATION,(1330,590,20))])
        sprite(frame,art()['kit-agenda'],pos,(420,520),cam,agenda)
        copies(frame,cam,t,world)
        book(frame,cam,t,opacity=world*ramp(t,1.35,2.1))
        if 9.8<t<18.2:
            contributions=frame.copy()
            for i in range(8):
                a=math.tau*i/8+.3;arrive=ramp(t,10.05+i*.12,11.15+i*.02)
                far=(1330+650*math.cos(a),725+65*math.sin(a),100+340*math.sin(a));near=(1330+330*math.cos(a),825,110+210*math.sin(a))
                v23.block(contributions,lerp(far,near,arrive),42,cam)
            frame=Image.blend(frame,contributions,window(t,9.8,10.2,17.5,18.2))
        key_alpha=window(t,15.5,16.0,17.1,17.5)
        sprite(frame,art()['clasp'],(1105,638,-85),(70,78),cam,window(t,8.7,10,17.5,17.72))
        if key_alpha>.001:
            center,turn=key_pose(t);sprite(frame,art()['key'],center,(350,160),cam,key_alpha,rz=turn)
        card_alpha=window(t,18.22,18.65,39.2,40.8)*world
        if card_alpha>.001:
            state=v23.state(n);progress=max(0,min(16,round((n-609)/(644-609)*16)))
            tap=round(28-14*(n-603)/6) if 603<=n<609 else 0
            panel=credit_texture(state,progress,tap) if n>=549 else Image.new('RGBA',(820,560),'#14372c')
            center,scale=credit_pose(t);sprite(frame,panel,center,(650*scale,444*scale),cam,card_alpha)
        alternative=window(t,22.3,23.1,26.7,27.8)*world
        if alternative>.001:
            wirebox(frame,cam,(2180,600,50),(220,280,110),alternative)
            book(frame,cam,t,center=(2180,600,30),scale=.72,angle=0,opacity=alternative)
            for dx in [-240,240]:
                route=[v23.point(2180,860,50,cam),v23.point(2180+dx,860,50,cam),v23.point(2180+dx,930,50,cam)]
                colour=tuple(round(a+(b-a)*alternative) for a,b in zip((7,26,23),(244,123,80)))
                v23.line(frame,route,colour,3);x,y=route[-1]
                v23.line(frame,[(x-10,y-15),(x,y),(x+10,y-15)],colour,3)
        archive=window(t,30.85,31.5,34.7,35.8)*world
        if archive>.001:
            center=track(t,[(0,(2050,650,350)),(30.85,(2050,650,350)),(31.7,(1740,585,-70)),(34.5,(1740,585,-70)),(35.8,(2210,650,450)),(DURATION,(2210,650,450))])
            sprite(frame,art()['archive'],center,(780,700),cam,archive,ry=6*(1-ramp(t,30.85,31.7)))
    captions(frame,t)
    if 16<t<18.6:
        layer=Image.new('RGBA',(700,125));text(layer,(108,5),'TARGET COMPLETE',34,MINT)
        text(layer,(108,57),'MATCHED KEY · ON TIME' if n>=500 else 'MATCHING KEY',34,CORAL)
        alpha=window(t,16,16.2,18.3,18.6);frame.paste(fade(layer,alpha),(0,420),fade(layer,alpha))
    if 1.8<t<40:
        footer='Workshop kit · local example'
        if 9.8<t<22.3:footer='NEAR testnet · protocol illustration · local example'
        elif 22.3<=t<27.8:footer='Alternative outcome · separate refund claim and withdrawal'
        elif 27.8<=t<30.85:footer='Illustrated retained copies · same local kit'
        elif 30.85<=t<35.8:footer='Prior Lantern Trail evidence · separate earlier sample'
        v23.label(frame,footer)
    if 38.65<t<41.2:
        alpha=window(t,38.65,39.15,40.65,41.2)
        payoff=Image.new('RGBA',(1200,320))
        d=ImageDraw.Draw(payoff)
        for words,y,colour in [('[ FREE TO USE ]',0,WHITE),('[ CREATOR PAID ]',155,CORAL)]:
            width=d.textlength(words,font=font(89));d.rectangle((600-width/2-24,y-5,600+width/2+24,y+116),fill=DARK)
            text(payoff,(600,y),words,89,colour,anchor='mt')
        frame.paste(fade(payoff,alpha),(360,300),fade(payoff,alpha))
    brand(frame,t,0,2.15)
    if t>=41.1:brand(frame,t,41.1,DURATION)
    return frame


def prepare():
    tl,_=v23.metadata();OUT.mkdir(parents=True,exist_ok=True)
    mapping=[{'frame':n,'phase':p['id'],'source':'native','scene_frame':n-round(p['start']*FPS)} for p in tl['phases'] for n in range(round(p['start']*FPS),round(p['end']*FPS))]
    for name,data in [('timeline.json',tl),('frame-map.json',mapping)]: (OUT/name).write_text(json.dumps(data,indent=2)+'\n')
    if not (OUT/'narration.srt').exists():shutil.copyfile(APPROVED/'narration.srt',OUT/'narration.srt')
    return tl,mapping


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['stills','study','render']);args=parser.parse_args()
    tl,mapping=prepare()
    if args.command=='stills':
        images=[]
        for p in tl['phases']:
            n=min(round((p['start']+1.5)*FPS),round(p['end']*FPS)-1);img=picture(p,n)
            img.save(OUT/(p['id']+'.png'));img.resize((390,219),Image.Resampling.LANCZOS).save(OUT/(p['id']+'-390.png'));images.append((p['id'],img))
        board=Image.new('RGB',(1920,math.ceil(len(images)/3)*388),DARK);d=ImageDraw.Draw(board)
        for i,(name,img) in enumerate(images):
            x=i%3*640;y=i//3*388;board.paste(img.resize((640,360),Image.Resampling.LANCZOS),(x,y));d.text((x+8,y+365),name,fill=WHITE)
        board.save(OUT/'direction.jpg');print(OUT/'direction.jpg');return
    v23.picture=picture
    if args.command=='study':
        selected=[r for r in mapping if 432<=r['frame']<850]
        v23.encode(OUT/'sunset-continuity-study.mp4',selected,tl,proof=True);return
    v23.encode(OUT/'sunset-launch-v24.mp4',mapping,tl)
    previous=json.loads((ROOT/'.publication/sunset-launch-v23/source-manifest.json').read_text())
    paths=[SOURCE/'produce.py',SOURCE.parent/'launch-v23/produce.py',ROOT/'projects/sunset/public/icon.svg',APPROVED/'sunset-launch-v22.mp4']
    (OUT/'source-manifest.json').write_text(json.dumps({'inputs':{**previous['inputs'],**{str(p.relative_to(ROOT)):sha(p) for p in paths}},
        'timeline_sha256':sha(OUT/'timeline.json'),'frame_map_sha256':sha(OUT/'frame-map.json'),'global_camera_objects':True,
        'native_dark_brand':True,'browser_executed':False,'soundtrack':'Exact V22 AAC packets and timing, stream copied.'},indent=2)+'\n')
    print(OUT/'sunset-launch-v24.mp4')


if __name__=='__main__':main()
