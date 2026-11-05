#!/usr/bin/env python3
"""SUNSET V15: a new 40-second original collage/minimal launch cut.

Uses V14's original assets and drawing helpers, never either rendered proof or
reference pixels/audio. The documentary insert is a separately verified native
capture. Financial paper animation is an illustration, not transaction footage.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / '.publication/sunset-launch-v15'
W, H, FPS, FRAMES = 1920, 1080, 30, 1200
INK, PAPER, CORAL, GOLD = '#09171d', '#f1eee5', '#be412b', '#daa21c'
GREEN = '#3e5a4e'
WHITE = '#fdfdfb'
BOUNDS = [0, 90, 156, 240, 345, 426, 534, 639, 762, 942, 1068, 1200]
NAMES = ['share', 'free', 'motivation', 'sponsor', 'custody', 'release',
         'withdraw', 'alternative', 'reader', 'resolution', 'sunset']
CADENCES = [20, 20, 30, 20, 30, 20, 20, 20, 30, 30, 20]
CAPTURE = OUT / 'capture/capture-provenance.json'
CAPTURE_DATA = json.loads(CAPTURE.read_text())

def module(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded

C = module('sunset_v14_collage', Path(__file__).parents[1] / 'launch-v14/collage-match.py')
M = module('sunset_v14_minimal', Path(__file__).parents[1] / 'launch-v14/minimal-match.py')
# Recompose the original independent planes for one full 16:9 output canvas.
C.W, C.H = W, H

def ease(x):
    return 1 - (1 - max(0, min(1, x))) ** 3

def ramp(t, a, b):
    return ease((t-a)/(b-a))

def lerp(a, b, p):
    return a+(b-a)*p

def txt(im, xy, value, size, color=PAPER, kind='bold', anchor='lt'):
    C.words(im, xy, value, size, color, kind, anchor)

def plane(im, art, **kw):
    C.plane(im, art, **kw)

@lru_cache(None)
def room_bg():
    return ImageOps.fit(C.room(), (W, H), Image.Resampling.LANCZOS)

def room(t=0):
    im = room_bg().copy()
    # Only a foreground plane drifts: the textured photographic environment stays
    # recognisable while different paper objects cross it.
    return im

def ground(color=INK):
    return C.ground(color).copy()

@lru_cache(None)
def page(kind='guide', public=False):
    im = Image.new('RGBA', (760, 940), PAPER)
    d = ImageDraw.Draw(im)
    d.polygon([(650,0),(760,0),(760,110)], fill=CORAL)
    d.rectangle((34,34,726,906), outline='#c6bca7', width=2)
    title = {'guide':'A USEFUL GUIDE', 'lesson':'A LESSON', 'notes':'SHARED NOTES',
             'new':'A FRESH PAGE'}[kind]
    txt(im,(30,33), title, 31, INK, 'narrow')
    txt(im,(31,80), 'MADE TO SHARE', 13, GREEN, 'mono')
    for i in range(6):
        y=252+i*81
        d.rectangle((66,y,95,y+29), outline=GREEN, width=3)
        d.line((128,y+12,660-(i%3)*55,y+12), fill='#8e9287', width=6)
    # One recurring drawn mark. The genuine UI remains untouched later.
    d.line((70,267,79,276,97,251),fill=CORAL,width=6,joint='curve')
    if public:
        txt(im,(31,409),'PUBLIC COPY',24,GREEN,'narrow')
    return im

@lru_cache(None)
def ticket(i):
    colors=[PAPER,'#c7d2aa','#d5b1bc','#e0b649','#9bb7b1','#b7a4c5']
    im=Image.new('RGBA',(500,230),colors[i%6]); d=ImageDraw.Draw(im)
    d.rectangle((10,10,489,219),outline=INK,width=3)
    for y in range(15,220,18): d.line((380,y,380,y+8),fill=INK,width=2)
    txt(im,(15,22),'SUPPORT',35,INK,'narrowitalic')
    txt(im,(16,75),f'PUBLIC RELEASE / {i+1:02}',12,INK,'mono')
    return im

@lru_cache(None)
def seal(label='PUBLIC',color=CORAL):
    im=Image.new('RGBA',(420,420)); d=ImageDraw.Draw(im)
    d.ellipse((18,18,402,402),fill=color)
    d.ellipse((33,33,387,387),outline=PAPER,width=4)
    d.ellipse((47,47,373,373),outline=PAPER,width=2)
    txt(im,(105,83),label,29,PAPER,'narrow','mt')
    txt(im,(105,124),'SUNSET',15,PAPER,'mono','mt')
    return im

@lru_cache(None)
def slip(title, subtitle='', color=PAPER):
    im=Image.new('RGBA',(1100,410),color); d=ImageDraw.Draw(im)
    d.rectangle((15,15,1084,394),outline=INK,width=3)
    txt(im,(22,32),title,49,INK,'narrowitalic')
    if subtitle:
        essential=title in {'People share','Sponsor the','Creator can claim','Help creators'}
        txt(im,(24,116 if essential else 126),subtitle,42 if essential else 19,
            INK,'narrowitalic' if essential else 'mono')
    return im

@lru_cache(None)
def mass_art(value,color,width,z):
    art=C.word_art(value,132,color,'narrowitalic')
    if color!=PAPER: return art
    f=C.font(132,'narrowitalic'); box=f.getbbox(value)
    stroke=max(1,round(7*art.width/(width*2000/(1000+z))))
    out=Image.new('RGBA',art.size)
    ImageDraw.Draw(out).text((16-box[0],12-box[1]),value,font=f,fill=color,
                             stroke_fill=INK,stroke_width=stroke)
    return out

def physical_words(im,value,x=0,y=0,width=800,height=155,rz=-10,color=PAPER,z=-50):
    art=mass_art(value,color,width,z)
    plane(im,art,x=x,y=y,z=z,width=width,height=height,ry=-6,rz=rz)

@lru_cache(None)
def word_strip(value, fg=INK, bg=PAPER):
    glyph=C.word_art(value,112,fg,'narrowitalic')
    art=Image.new('RGBA',glyph.size,bg)
    art.alpha_composite(glyph)
    return art

def strip_words(im,value,x,y,width,height,rz=-6,z=-80,fg=INK,bg=PAPER):
    plane(im,word_strip(value,fg,bg),x=x,y=y,width=width,height=height,
          rz=rz,ry=-4,z=z)

def disclose(im):
    # Passage-local editorial context, stable and legible at native dimensions.
    layer=Image.new('RGBA',(1050,84),(9,23,29,238))
    txt(layer,(12,8),'NEAR testnet · illustration',25,PAPER,'bold')
    im.alpha_composite(layer,(52,38))

def line_curve(im, points, progress=1, color=CORAL, width=4):
    C.arrow_curve(im,points,color,width,progress)

def white():
    return Image.new('RGBA',(W,H),WHITE)

def circle(im, radius, cx=960, cy=540):
    y,x=np.ogrid[:H,:W]
    mask=Image.fromarray(np.uint8(np.clip(radius+.5-np.sqrt((x-cx)**2+(y-cy)**2),0,1)*255),'L')
    out=white(); out.paste(im,(0,0),mask)
    return out

def point(im, p=1, x=960, y=540, color=CORAL):
    r=lerp(18,8,p); d=ImageDraw.Draw(im)
    d.ellipse((x-r,y-r,x+r,y+r),fill=color)

def brackets(im,value,size=45,color=INK,accent=0):
    # Regular upright typography and fixed cap size across semantic replacements.
    f=ImageFont.truetype(M.FONT_PATH,round(size*2))
    box=f.getbbox(value); tw=f.getlength(value)
    x=(W-tw)/2; top=(H-(box[3]-box[1]))/2-box[1]
    d=ImageDraw.Draw(im)
    d.text((x,top),value,font=f,fill=color)
    l,r=x-42,x+tw+42; a=16; y0,y1=H/2-48,H/2+48
    d.line((l+a,y0,l,y0,l,y1,l+a,y1),fill=INK,width=6)
    d.line((r-a,y0,r,y0,r,y1,r-a,y1),fill=INK,width=6)

def ink_work(t):
    im=room(t)
    plane(im,C.hand(),x=160,y=30,z=-50,width=1050,height=700,rz=-5)
    # This ink belongs to the authored paper world, not the documentary UI.
    pts=[(290+i*3.3,330+16*math.sin(i/15)) for i in range(140)]
    C.path(im,pts[:max(2,min(140,round(15+t*22)))],CORAL,4)
    plane(im,page(),x=-330,y=95,z=80,width=200,rz=-13)
    return im

def scene_share(t):
    im=ground()
    p=ramp(t,0,.35)
    # Brief warm disc belongs to the first material field.
    d=ImageDraw.Draw(im); d.ellipse((1490,-230,2150,430),fill=GOLD)
    for i,(x,y,z,w,rz,kind) in enumerate([
        (-355,-40,80,265,-13,'lesson'),(320,-15,150,285,12,'notes'),
        (-90,65,-20,300,-5,'guide')]):
        a=ramp(t,i*.11,.4+i*.11)
        plane(im,page(kind),x=x,y=y+lerp(480,0,a),z=z,width=w,rz=rz,ry=-10+i*7)
    for i,(x,y) in enumerate([(-330,20),(300,0)]):
        a=ramp(t,.15+i*.16,.5+i*.16)
        macro=ramp(t,1.25,1.7) if i==0 else 0
        plane(im,C.photo_panel(0 if i==0 else 1),
              x=lerp(x,-245,macro),y=y-lerp(420,0,a)+lerp(0,68,macro),
              z=lerp(-20,-85,macro),width=lerp(245,525,macro),
              height=lerp(235,500,macro),rz=lerp(-8+i*15,-13,macro))
    # Complete phrases land as printed strips inside the image.
    if t>.38:
        strip_words(im,'People share',x=-70,y=-160,width=540,height=82,rz=-7,z=-130)
        strip_words(im,'incredible things.',x=30,y=-64,width=700,height=82,rz=-7,z=-135)
    if t>1.4:
        line_curve(im,[(5,410),(220,180),(630,490),(950,340)],ramp(t,1.4,2),CORAL,5)
    if t>2.62:
        p=ramp(t,2.62,3)
        plane(im,page(),x=lerp(-90,0,p),y=lerp(65,20,p),z=lerp(-20,-390,p),
              width=lerp(300,740,p),height=lerp(371,630,p),rz=lerp(-5,7,p))
    return im

def scene_free(t):
    im=ink_work(t+1)
    plane(im,C.photo_panel(0),x=-350,y=35,z=50,width=325,height=360,rz=-8,ry=8)
    # Heavy wide word mass deliberately fills the field; no V14 thin upper-right type.
    p=ramp(t,0,.22)
    physical_words(im,'FOR',x=-170+lerp(900,0,p),y=-105,width=480,height=150,rz=-11)
    physical_words(im,'FREE.',x=45+lerp(900,0,ramp(t,.1,.32)),y=38,
                   width=660,height=150,rz=-11,z=-145)
    line_curve(im,[(-50,520),(190,110),(770,540),(1000,280)],ramp(t,.4,.85),CORAL,8)
    for i in range(3):
        if t>.45+i*.1:
            plane(im,page(['lesson','guide','notes'][i]),x=260+i*80,y=-190,
                  z=-70,width=67,height=83,rz=-11)
    return im

def scene_motivation(t):
    work=ink_work(t+3)
    if t<.35:
        return circle(work,lerp(1400,1030,ramp(t,0,.35)))
    if t<1.0:
        # Abrupt containment; content ink continues changing independently.
        r=lerp(265,235,ramp(t,.35,.6))
        im=circle(work,r)
        M.guides(im,r)
        # Restore clean circular content over tangent guides.
        im.paste(circle(work,r),(0,0),Image.fromarray(np.uint8(
            np.clip(r+.5-np.sqrt((np.ogrid[:H,:W][1]-W/2)**2+
                               (np.ogrid[:H,:W][0]-H/2)**2),0,1)*255),'L'))
        return im
    im=white()
    if t<1.25: point(im,ramp(t,1,1.25),color=INK)
    elif t<2.6: brackets(im,'Help creators keep creating.',37)
    else: point(im,ramp(t,2.6,2.8),color=CORAL)
    return im

def sponsor_world(t):
    im=ground(GOLD)
    # Mustard cutout/letter/ticket/ribbon material world.
    plane(im,C.hand(),x=-420,y=55,z=220,width=950,height=670,rz=-18)
    C.ribbon(im,t+3,False)
    arrival=ramp(t,.12,.65)
    px,py=lerp(0,-290,arrival),lerp(0,55,arrival)
    pw=lerp(55,300,ramp(t,.1,.6))
    plane(im,page(),x=px,y=py,z=70,width=pw,height=pw*940/760,rz=-8*arrival)
    sealx,sealy=lerp(0,-245,arrival),lerp(0,120,arrival)
    sw=lerp(8,125,ramp(t,0,.6))
    plane(im,seal('SPONSOR'),x=sealx,y=sealy,z=-65,width=sw,height=sw,rz=-8*arrival)
    if t>.45:
        a=ramp(t,.45,.72)
        physical_words(im,'SPONSOR',x=lerp(800,75,a),y=-145,width=755,
                       height=103,rz=-10,color=INK,z=-110)
        strip_words(im,'THE PUBLIC RELEASE.',x=120,y=-42,width=620,
                    height=68,rz=-10,z=-115)
    for i in range(6):
        a=ramp(t,.65+i*.18,.87+i*.18)
        if a<=0: continue
        plane(im,ticket(i),x=lerp(700,-75+(i%3)*172,a),y=80+(i//3)*86,
              z=-115-i*8,width=160,height=74,rz=-8+(i%3)*6)
    if t>.8:
        line_curve(im,[(-30,490),(180,60),(750,540),(1000,150)],
                   ramp(t,.8,1.3),CORAL,8)
    C.ribbon(im,t+3,True)
    # Fixed six-slot cap, followed by a stable target landing.
    d=ImageDraw.Draw(im)
    for i in range(6):
        x=935+i*104
        d.rectangle((x,957,x+82,989),outline=INK,width=3)
        if t>.85+i*.18: d.rectangle((x+6,963,x+76,983),fill=INK)
    if t>2.25: txt(im,(635,505),'TARGET REACHED',22,INK,'narrow','mt')
    return im

def scene_sponsor(t):
    world=sponsor_world(t)
    # The preceding coral point is the exact center of this expanding seal/world.
    return circle(world,lerp(8,1250,ramp(t,0,.48))) if t<.48 else world

def scene_custody(t):
    # Same capped tickets/page/seal and same field enter containment, no new layout.
    world=sponsor_world(3.5+t)
    if t<.72:
        return circle(world,lerp(1150,235,ramp(t,0,.3)))
    im=white()
    if t<.98: point(im,ramp(t,.72,.98),color=INK)
    else: brackets(im,'NEAR holds the funds.',44)
    return im

def key_art():
    im=Image.new('RGBA',(420,160)); d=ImageDraw.Draw(im)
    d.ellipse((8,8,135,135),outline=GOLD,width=20)
    d.line((128,75,400,75),fill=GOLD,width=24)
    d.line((330,75,330,125),fill=GOLD,width=20)
    d.line((380,75,380,115),fill=GOLD,width=20)
    return im

def scene_release(t):
    im=ground(GREEN)
    plane(im,page(public=t>=1.0),x=-220,y=40,z=20,width=360,height=445,rz=-5,ry=-6)
    plane(im,seal('PUBLIC' if t>=1 else 'BOUND'),x=-185,y=135,z=-55,width=125,height=125,rz=-5)
    plane(im,key_art(),x=lerp(460,-180,ramp(t,.1,.85)),y=-115,z=-180,width=240,height=90,rz=-5)
    if t<1.65:
        strip_words(im,'Release on time.',x=165,y=-122,width=495,height=83,rz=4,z=-100)
        txt(im,(660,216),'COMMITTED KEY MATCH',19,PAPER,'mono','mt')
        if t>=.9:
            txt(im,(700,285),'KEY MATCHED',23,PAPER,'mono','mt')
            line_curve(im,[(385,345),(460,110),(640,110),(670,258)],
                       ramp(t,.9,1.3),GOLD,5)
    else:
        strip_words(im,'Creator can',x=150,y=-132,width=480,height=73,rz=4,z=-100)
        strip_words(im,'claim payment.',x=175,y=-43,width=520,height=73,rz=4,z=-105)
        a=ramp(t,1.65,2)
        plane(im,slip('CREATOR CREDIT','CLAIMABLE'),x=lerp(-160,190,a),y=120,
              z=-180,width=315,height=117,rz=-4)
        line_curve(im,[(370,350),(470,450),(590,430),(650,375)],
                   ramp(t,1.8,2.25),GOLD,5)
    return im

def scene_withdraw(t):
    if t<.72:
        im=ground(GREEN)
        plane(im,C.photo_panel(0),x=-320,y=40,z=80,width=300,height=350,rz=-7)
        plane(im,page('guide',True),x=280,y=30,z=100,width=260,height=322,rz=9)
        a=ramp(t,0,.4)
        # Carry the same labelled creator-credit slip out of the preceding lane.
        plane(im,slip('CREATOR CREDIT','CLAIMABLE'),x=lerp(190,0,a),
              y=lerp(120,35,a),z=-180,width=lerp(315,510,a),
              height=lerp(117,190,a),rz=-4)
        strip_words(im,'Withdraw',x=40,y=-142,width=400,height=85,rz=-5,z=-100)
    elif t<1.8:
        # Deliberate close confirmation crop; distinct scale and stamp.
        im=ground(PAPER)
        plane(im,slip('CREATOR CREDIT','WITHDRAWAL'),x=-70,y=60,z=-110,
              width=900,height=335,rz=-9)
        plane(im,seal('CONFIRMED',GREEN),x=95,y=55,z=-210,width=260,height=260,rz=10)
        strip_words(im,'Withdrawal confirmed',x=0,y=-145,width=830,
                    height=82,rz=-4,z=-130,fg=PAPER,bg=GREEN)
    else:
        # Pull back to the human maker only after successful withdrawal.
        im=room(t)
        plane(im,C.photo_panel(0),x=-285,y=15,z=40,width=450,height=465,rz=-7)
        plane(im,page('guide',True),x=275,y=25,z=100,width=300,height=371,rz=8)
        plane(im,slip('CREATOR CREDIT','WITHDRAWAL COMPLETE'),x=150,y=155,
              z=-80,width=285,height=106,rz=6)
        plane(im,seal('PAID',GREEN),x=190,y=80,z=-190,width=220,height=220,rz=12)
        strip_words(im,'Creator paid',x=150,y=-145,width=550,height=84,rz=5,z=-120)
    return im

def scene_alternative(t):
    im=ground('#d6a536')
    # Distinct quiet pre-release branch. All conditions remain visible for4.1s.
    txt(im,(480,63),'Alternative outcome',23,INK,'mono','mt')
    txt(im,(480,148),'Target unmet at deadline',49,INK,'narrowitalic','mt')
    txt(im,(480,220),'or release deadline missed.',49,INK,'narrowitalic','mt')
    txt(im,(480,343),'Sponsors can claim refunds.',46,INK,'narrow','mt')
    # Local expiry stubs remain subordinate and stop in an eligibility lane.
    for i in range(3):
        plane(im,ticket(i),x=-100+i*100,y=205,z=40,width=80,height=37,rz=-5+i*5)
    return im

def browser_spec(n):
    source_time=max(0,min(5,n/FPS-26))
    sample=next(p for p in reversed(CAPTURE_DATA['samples']) if p['at']<=source_time+1e-9)
    if n/FPS>=31:
        # Verified retained native checkbox bbox665,778..686,799, magnified4x.
        crop=[665,778,686,799]
        dest=[918,498,1002,582]
    elif n/FPS<29.4:
        crop=[650,760,1240,820]
        dest=[120,445,1800,616]
    else:
        crop=[630,925,1040,975]
        dest=[181,435,1739,625]
    return {'output_frame':n,'source_time':source_time,'source_png':sample['path'],
            'source_sha256':sample['sha256'],'source_crop':crop,'destination_bbox':dest}

@lru_cache(None)
def capture_image(path):
    return Image.open(ROOT/path).convert('RGBA')

def scene_reader(t):
    im=white()
    if t<.6-1e-7:
        # The illustrated paper's cream edge supplies an explicit documentary handoff.
        p=max(0,min(1,t/.6))
        plane(im,page(),x=lerp(300,-800,p),y=30,z=-80,width=780,height=960,rz=-4)
        txt(im,(480,455),'Local handbook example',25,INK,'mono','mt')
        txt(im,(480,500),'Downloaded file · browser offline',25,INK,'mono','mt')
        return im
    n=round((25.4+t)*FPS)
    spec=browser_spec(n)
    x0,y0,x1,y1=spec['destination_bbox']
    pixels=capture_image(spec['source_png']).crop(spec['source_crop'])
    pixels=pixels.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS)
    im.alpha_composite(pixels,(x0,y0))
    txt(im,(480,55),'A useful copy to keep.',37,INK,'bold','mt')
    txt(im,(480,113),'Read without a wallet.',24,GREEN,'bold','mt')
    if 29.4<=n/FPS<31:
        txt(im,(480,359),'Still saved after reload.',25,GREEN,'bold','mt')
    txt(im,(480,455),'Local handbook example',25,INK,'mono','mt')
    txt(im,(480,500),'Downloaded file · browser offline',25,INK,'mono','mt')
    return im

def scene_resolution(t):
    im=white()
    if t<.28:
        # Clear editorial cut: neighbouring authored check takes over, no UI fabrication.
        d=ImageDraw.Draw(im); d.rounded_rectangle((918,498,1001,581),radius=4,fill=GREEN)
        d.line((934,539,952,557,985,519),fill=PAPER,width=8,joint='curve')
    elif t<.55:
        point(im,ramp(t,.28,.55),color=GREEN)
    elif t<1.5:
        brackets(im,'FREE TO USE',46)
    elif t<2.5:
        brackets(im,'CREATORS PAID',46)
    else:
        im=ink_work(t+1)
        plane(im,C.photo_panel(0),x=-320,y=-35,z=80,width=300,height=350,rz=-6)
        a=ramp(t,2.5,2.9)
        plane(im,page('new'),x=200,y=lerp(470,50,a),z=-70,
              width=430,height=532,rz=7)
    return im

def scene_sunset(t):
    im=ground(PAPER); d=ImageDraw.Draw(im)
    # Coral corner enlarges into a clean authored horizon/mark.
    p=ramp(t,0,.7)
    if t<.35:
        d.polygon([(lerp(1660,1140,p),0),(1920,0),(1920,lerp(250,700,p))],fill=CORAL)
    radius=140
    cx,cy=960,245
    d.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=CORAL)
    d.rectangle((cx-radius-5,cy+8,cx+radius+5,cy+radius+6),fill=PAPER)
    d.line((715,cy+8,1205,cy+8),fill=INK,width=5)
    txt(im,(480,190),'SUNSET',105,INK,'narrow','mt')
    txt(im,(480,338),'Support once. Share forever.',31,INK,'bold','mt')
    return im

SCENES=[scene_share,scene_free,scene_motivation,scene_sponsor,scene_custody,
        scene_release,scene_withdraw,scene_alternative,scene_reader,
        scene_resolution,scene_sunset]

def render(n):
    assert 0<=n<FRAMES
    k=next(i for i,b in enumerate(BOUNDS[1:]) if n<b)
    local=(n-BOUNDS[k])/FPS
    native=math.floor(local*CADENCES[k]+1e-7)/CADENCES[k]
    result=SCENES[k](native)
    if result is None: raise AssertionError(f'Scene {k} returned no pixels')
    if 3<=k<=7: disclose(result)
    return result.convert('RGB')

def frame_key(n):
    k=next(i for i,b in enumerate(BOUNDS[1:]) if n<b)
    return k, math.floor((n-BOUNDS[k])*CADENCES[k]/FPS+1e-7)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def manifest():
    assets=[C.ASSETS/'creator-portrait.png',C.ASSETS/'workroom.png',C.HANDS]
    return {'renderer':{'path':str(Path(__file__).relative_to(ROOT)),'sha256':sha(Path(__file__))},
            'format':{'width':W,'height':H,'fps':FPS,'frames':FRAMES,'duration':40},
            'scenes':[{'name':name,'first_frame':BOUNDS[i],'end_frame_exclusive':BOUNDS[i+1],
                       'drawing_cadence':CADENCES[i]} for i,name in enumerate(NAMES)],
            'cadence':'30fps delivery. Collage paper animation intentionally sampled at20fps; minimal typography and documentary placement use30fps. Only equal native timestamps are reused.',
            'asset_files':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in assets],
            'helpers':[{'path':str(Path(x.__file__).relative_to(ROOT)),'sha256':sha(Path(x.__file__))} for x in [C,M]],
            'reference_pixels_or_audio':False,'old_proof_movies_used':False,
            'financial_scope':'Labelled illustration of implemented testnet rules. Release creates credit; a separate successful withdrawal precedes paid. Alternative pre-release conditions permit claims; no automatic refunds.',
            'documentary_scope':'Genuine existing downloaded local handbook example, independent of earlier funded resources. Actual input/reload retained; editorial labels outside native crop.',
            'capture_manifest':{'path':str(CAPTURE.relative_to(ROOT)),'sha256':sha(CAPTURE)},
            'browser_frames':[browser_spec(n) for n in range(780,942)],
            'fonts':[{'path':str(p),'sha256':sha(p)} for p in sorted(set(
                [Path(x) for x in C.FONTS.values()]+[Path(M.FONT_PATH)]))],
            'reading_windows':[
                {'phrase':'People share incredible things.','start':.6,'end':2.6},
                {'phrase':'For free.','start':3.35,'end':5.2},
                {'phrase':'Help creators keep creating.','start':6.45,'end':7.8},
                {'phrase':'Sponsor the public release.','start':8.75,'end':11.5},
                {'phrase':'NEAR holds the funds.','start':12.5,'end':14.2},
                {'phrase':'Release on time.','start':14.2,'end':15.85},
                {'phrase':'Creator can claim payment.','start':15.85,'end':17.8},
                {'phrase':'Withdraw','start':17.98,'end':18.52},
                {'phrase':'Withdrawal confirmed','start':557/30,'end':19.6},
                {'phrase':'Creator paid','start':19.6,'end':21.3},
                {'phrase':'Target unmet at deadline / or release deadline missed. / Sponsors can claim refunds.','start':21.3,'end':25.4},
                {'phrase':'A useful copy to keep. / Read without a wallet.','start':26,'end':31.4},
                {'phrase':'FREE TO USE','start':31.95,'end':32.9},
                {'phrase':'CREATORS PAID','start':32.9,'end':33.9},
                {'phrase':'Maker continues on a fresh page (visual; no caption)','start':34.3,'end':35.6},
                {'phrase':'SUNSET / Support once. Share forever.','start':36.3,'end':40}]}

def gates():
    directory=OUT/'gates'; directory.mkdir(parents=True,exist_ok=True)
    times=[.7,2.25,3.7,4.7,5.72,6.25,7.25,9.25,10.8,12.05,13.2,14.9,16.7,
           18.2,18.9,20,21.8,23.5,25.7,27.5,30.6,31.6,32.5,33.5,35,37.2]
    cols=4; tw,th=480,270; cellh=306
    sheet=Image.new('RGB',(cols*tw,math.ceil(len(times)/cols)*cellh),'#202523')
    d=ImageDraw.Draw(sheet)
    small=ImageFont.truetype(M.FONT_PATH,24)
    for i,t in enumerate(times):
        n=round(t*FPS); im=render(n); im.save(directory/f'pose-{n:04}.png')
        x,y=(i%cols)*tw,(i//cols)*cellh
        sheet.paste(im.resize((tw,th),Image.Resampling.LANCZOS),(x,y+30))
        d.text((x+12,y+3),f'{t:05.2f}s / {NAMES[frame_key(n)[0]]}',font=small,fill='white')
    sheet.save(directory/'story-gate.jpg',quality=94)
    sheet.resize((1560,round(sheet.height*1560/sheet.width)),Image.Resampling.LANCZOS).save(directory/'phone390-gate.jpg',quality=94)
    # Consecutive samples expose object/semantic handoffs, not just intent.
    events=[3,5.2,5.55,6.2,6.45,7.8,8,8.15,8.3,8.6,11.5,12.22,12.48,14.2,15.1,
            15.85,17.8,18.52,19.6,21.3,25.4,31,31.4,31.68,31.95,32.9,33.9,35.6]
    thumbs=[]
    for t in events:
        for offset in [-1,0,1]:
            n=round(t*FPS)+offset
            if 0<=n<FRAMES: thumbs.append((n,render(n)))
    strip=Image.new('RGB',(1920,math.ceil(len(thumbs)/8)*160),'#202523')
    d=ImageDraw.Draw(strip)
    for i,(n,im) in enumerate(thumbs):
        x,y=(i%8)*240,(i//8)*160
        strip.paste(im.resize((240,135),Image.Resampling.LANCZOS),(x,y))
        d.text((x+5,y+135),f'{n:04} / {n/FPS:.3f}',font=ImageFont.truetype(M.FONT_PATH,17),fill='white')
    strip.save(directory/'transition-gate.jpg',quality=93)
    print(directory,flush=True)

def prepare_browser():
    assert CAPTURE_DATA['source_window_seconds']==[0,5]
    assert CAPTURE_DATA['playback_speed']==1
    assert CAPTURE_DATA['browser_offline_before_file_open'] is True
    assert CAPTURE_DATA['chain_mutations']==0
    assert CAPTURE_DATA['native_roi_without_git_commands']==[630,600,1562,975]
    for sample in CAPTURE_DATA['samples']:
        p=ROOT/sample['path']; assert sha(p)==sample['sha256'],p
        assert capture_image(sample['path']).size==(W,H)
    for n in range(780,942):
        x0,y0,x1,y1=browser_spec(n)['source_crop']
        assert 630<=x0<x1<=1562 and 600<=y0<y1<=975

def render_movie(rebuild):
    directory=OUT/'segments'; directory.mkdir(parents=True,exist_ok=True)
    source_sha=sha(Path(__file__))
    snapshot=OUT/f'renderer-source-{source_sha[:12]}.py'
    snapshot.write_bytes(Path(__file__).read_bytes())
    records_path=directory/'provenance.json'
    records=json.loads(records_path.read_text()) if records_path.exists() else {}
    filter_='scale=in_range=full:out_range=tv:in_color_matrix=bt709:out_color_matrix=bt709,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709,format=yuv420p'
    for k,name in enumerate(NAMES):
        path=directory/f'{k:02}-{name}.mp4'
        if path.exists() and k not in rebuild:
            assert str(k) in records and records[str(k)]['sha256']==sha(path), 'Unrecorded or changed segment cache'
            continue
        temporary=path.with_suffix('.rendering.mp4')
        proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
            '-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-vf',filter_,
            '-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p',
            '-color_range','tv','-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709',
            '-movflags','+faststart',str(temporary)],stdin=subprocess.PIPE)
        last_key,last_pixels=None,None
        for n in range(BOUNDS[k],BOUNDS[k+1]):
            key=frame_key(n)
            if key!=last_key: last_pixels=render(n).tobytes(); last_key=key
            proc.stdin.write(last_pixels)
            if n%60==0: print(f'{name} {n}/{FRAMES}',flush=True)
        proc.stdin.close()
        if proc.wait()!=0: raise RuntimeError(f'Encoding failed for {name}')
        temporary.replace(path)
        records[str(k)]={'file':str(path.relative_to(ROOT)),'first_frame':BOUNDS[k],
                         'end_frame_exclusive':BOUNDS[k+1],'renderer_sha256':source_sha,
                         'source_snapshot':str(snapshot.relative_to(ROOT)),'sha256':sha(path)}
        records_path.write_text(json.dumps(records,indent=2)+'\n')
        print(f'Completed {k:02} {name}',flush=True)
    listing=directory/'concat.txt'
    listing.write_text('\n'.join("file '"+(directory/f'{k:02}-{name}.mp4').name+"'" for k,name in enumerate(NAMES))+'\n')
    target=OUT/'sunset-fusion-silent-40s.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),
                    '-c','copy','-an','-movflags','+faststart',str(target)],check=True)
    print(target,flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--gates',action='store_true')
    parser.add_argument('--render',action='store_true')
    parser.add_argument('--rebuild',nargs='*',type=int,default=[])
    parser.add_argument('--times',nargs='+',type=float)
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    assert BOUNDS==sorted(set(BOUNDS)) and BOUNDS[-1]==FRAMES
    assert len(SCENES)==len(NAMES)==len(CADENCES)==len(BOUNDS)-1
    assert frame_key(89)[0]==0 and frame_key(90)[0]==1
    assert BOUNDS[8]/FPS==25.4 and BOUNDS[9]/FPS==31.4
    prepare_browser()
    if args.gates: gates()
    if args.times:
        for t in args.times:
            n=round(t*FPS); render(n).save(OUT/f'pose-{n:04}.png')
    if args.render: render_movie(args.rebuild)
    (OUT/'render-manifest.json').write_text(json.dumps(manifest(),indent=2)+'\n')

if __name__=='__main__':
    main()
