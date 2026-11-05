#!/usr/bin/env python3
"""Private eight-second motion syntax study; original artwork only in the proof.

Pillow's inverse homography maps independent 3D paper planes into native pixels.
The supplied film is only opened by the explicitly labelled --compare mode.
"""
import argparse
import hashlib
import json
import math
import random
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / '.publication/sunset-launch-v14/collage'
ASSETS = ROOT / '.publication/sunset-launch-v14/assets'
HANDS = ROOT / '.publication/sunset-launch-v13/assets/creator-cutout.png'
REF = ROOT / '.publication/sunset-reference-study-20261105/feel-good'
W, H, FPS, FRAMES = 1920, 1440, 20, 160
S = 2
INK, PAPER, RUST, MUSTARD = '#06131b', '#ece8df', '#ad341b', '#d99513'
COLORS = ['#915563', '#c79b3f', '#71826b', '#716184']
TALL_COLORS = ['#ac4f77', '#eaa640', '#d7dc76', '#ed7044']
FONTS = {
    'bold': '/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf',
    'italic': '/usr/share/fonts/opentype/urw-base35/NimbusSans-BoldItalic.otf',
    'narrow': '/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Bold.otf',
    'narrowitalic': '/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-BoldOblique.otf',
    'serif': '/usr/share/fonts/opentype/urw-base35/NimbusRoman-Bold.otf',
    'mono': '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
}

# Source native frame numbers at 20 fps, not approximate one-second chapters.
EVENTS = [
    (0, 'grid: lower first paper'), (1, 'grid: upper right arrives'),
    (2, 'grid: lower pair arrives'), (3, 'grid: upper left arrives'),
    (5, 'grid complete'), (9, 'abrupt contraction'), (12, 'grid label locks'),
    (15, 'first horizontal print tear'), (16, 'second print tear'),
    (17, 'third print tear'), (18, 'tilted camera dives to lower panel'),
    (19, 'near-plane smear'), (20, 'first macro landing'),
    (29, 'first macro whip'), (30, 'bright near-plane smear'),
    (31, 'second macro landing'), (40, 'portrait drops'),
    (41, 'oblique physical word plane enters'), (43, 'first word hit'),
    (44, 'second word hit'), (45, 'first arrow extends'),
    (46, 'second arrow loops'), (47, 'first miniature panel'),
    (48, 'second miniature panel'), (49, 'miniature row complete'),
    (50, 'word collage landing'), (54, 'independent red arrow crosses'),
    (58, 'directional text departure'), (59, 'mustard picture enters'),
    (60, 'halftone reveals'), (61, 'first letter slips'),
    (63, 'middle letter slips'), (64, 'foreground rust arrow'),
    (65, 'foreground white ribbon'), (67, 'last letter slips'),
    (69, 'second rust loop'), (72, 'sideways camera starts'),
    (73, 'first tall panel enters'), (74, 'second tall panel enters'),
    (75, 'third tall panel enters'), (76, 'fourth tall panel enters'),
    (80, 'radial push blur'), (81, 'tall panels on dark tableau'),
    (83, 'scratch accents expand'), (87, 'pale physical occluder'),
    (88, 'near-black physical sweep'), (89, 'blurred return'),
    (90, 'white exposure flash'), (92, 'photo wall reveal'),
    (93, 'low left magazine'), (95, 'upper magazine'),
    (96, 'central magazine'), (97, 'right print'), (99, 'full stack landing'),
    (107, 'pullback focus shift'), (109, 'defocused foreground crosses'),
    (110, 'profile cutout reveals in photo space'),
    (113, 'small type strip starts'), (117, 'small type complete'),
    (124, 'dark exposure dip'), (125, 'halftone near-plane enters'),
    (126, 'camera HUD'), (128, 'first face plane macro'),
    (133, 'focus smear'), (134, 'focus-square flash'),
    (135, 'second face plane macro'), (141, 'face print tear'),
    (142, 'camera whip and square flash'), (145, 'third face plane macro'),
    (150, 'rapid pullback'), (151, 'whole face stack'),
    (156, 'focus ring'), (157, 'halftone overlay'), (159, 'white focus spot'),
]

def ease(x):
    x = max(0., min(1., x))
    return 1 - (1 - x) ** 3

def ramp(t, a, b):
    return ease((t-a)/(b-a))

def lerp(a, b, x):
    return a+(b-a)*x

@lru_cache(None)
def font(size, kind='bold'):
    return ImageFont.truetype(FONTS[kind], round(size*S))

def words(im, xy, value, size, color=PAPER, kind='bold', anchor='lt'):
    if '\n' in value:
        for j,line in enumerate(value.splitlines()):
            words(im,(xy[0],xy[1]+j*(size+2)),line,size,color,kind,anchor)
        return
    ImageDraw.Draw(im).text((round(xy[0]*S), round(xy[1]*S)), value,
        font=font(size, kind), fill=color, anchor=anchor, stroke_width=0)

@lru_cache(None)
def word_art(value, size, color=PAPER, kind='italic'):
    f=font(size, kind); box=f.getbbox(value)
    im=Image.new('RGBA', (box[2]-box[0]+32, box[3]-box[1]+24))
    ImageDraw.Draw(im).text((16-box[0], 12-box[1]), value, font=f, fill=color)
    return im

@lru_cache(None)
def ground(color=INK):
    im=Image.new('RGBA',(W,H),color)
    rng=random.Random(76); d=ImageDraw.Draw(im)
    rgb=Image.new('RGB',(1,1),color).getpixel((0,0))
    for _ in range(13000):
        x,y=rng.randrange(W),rng.randrange(H)
        delta=rng.choice([-3,-2,2,3])
        d.point((x,y),fill=tuple(max(0,min(255,c+delta)) for c in rgb)+(255,))
    return im

def cover(im, width, height, center=(.5,.5)):
    z=max(width/im.width,height/im.height)
    im=im.resize((round(im.width*z),round(im.height*z)),Image.Resampling.LANCZOS)
    x=round((im.width-width)*center[0]); y=round((im.height-height)*center[1])
    return im.crop((x,y,x+width,y+height))

@lru_cache(None)
def portrait():
    path=ASSETS/'creator-portrait.png'
    assert path.exists(), f'Original portrait asset missing: {path}'
    return Image.open(path).convert('RGBA')

@lru_cache(None)
def room():
    path=ASSETS/'workroom.png'
    assert path.exists(), f'Original photographic room asset missing: {path}'
    return Image.open(path).convert('RGBA')

@lru_cache(None)
def hand():
    return Image.open(HANDS).convert('RGBA')

@lru_cache(None)
def photo_panel(i, tall=False):
    # Four distinct original adults, cropped from their transparent 2×2 sheet.
    size=(500,820) if tall else (630,520)
    sheet=portrait(); half=sheet.width//2
    cut=sheet.crop(((i%2)*half,(i//2)*half,(i%2+1)*half,(i//2+1)*half))
    cut=cover(cut,*size,center=(.5,.42))
    im=Image.new('RGBA',size,TALL_COLORS[i] if tall else PAPER)
    im.alpha_composite(cut)
    if tall:
        grey=ImageOps.autocontrast(ImageOps.grayscale(im),cutoff=1)
        im=ImageOps.colorize(grey,'#091517',TALL_COLORS[i]).convert('RGBA')
    grain=Image.new('RGBA',size); gd=ImageDraw.Draw(grain)
    for y in range(0,size[1],5): gd.line((0,y,size[0],y),fill=(8,8,12,12),width=1)
    im.alpha_composite(grain)
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,size[0]-1,size[1]-1),outline='#161a1c',width=5)
    return im

@lru_cache(None)
def figure_art():
    """An original paper figure: photo head, ink-drawn coat and trouser planes."""
    im=Image.new('RGBA',(600,1400)); d=ImageDraw.Draw(im)
    cream='#d6d0b9'; dark='#252a2b'; seam='#656b60'
    d.polygon([(156,380),(400,365),(465,765),(115,755)],fill=cream,outline=dark,width=8)
    d.polygon([(153,400),(100,427),(43,863),(97,879),(178,526)],fill=cream,outline=dark,width=8)
    d.polygon([(399,390),(464,426),(527,834),(471,850),(392,542)],fill=cream,outline=dark,width=8)
    d.ellipse((35,846,99,930),fill='#ab9279',outline=dark,width=7)
    d.ellipse((471,821,538,908),fill='#ab9279',outline=dark,width=7)
    d.polygon([(137,733),(400,737),(415,900),(330,1270),(267,1266),(277,877),(233,1278),(163,1275),(155,890)],fill=dark,outline=seam,width=7)
    d.polygon([(159,1245),(230,1256),(244,1345),(124,1353),(110,1327)],fill='#191d1e',outline=cream,width=5)
    d.polygon([(287,1251),(343,1251),(403,1323),(395,1350),(280,1353)],fill='#191d1e',outline=cream,width=5)
    d.line((277,435,278,750),fill=dark,width=7)
    d.line((136,694,433,690),fill=dark,width=8)
    d.polygon([(196,378),(278,439),(359,370),(279,526)],fill='#535d55',outline=dark,width=6)
    head=portrait().crop((0,0,627,627)).resize((368,368),Image.Resampling.LANCZOS)
    im.alpha_composite(head,(95,30))
    return im

@lru_cache(None)
def poster(i):
    if i==0:
        im=Image.new('RGBA',(650,570),'#121d22')
        words(im,(12,12),'SUNSET',46,PAPER,'italic')
        for j in range(4):
            p=cover(photo_panel(j),300,220)
            im.alpha_composite(p,(17+(j%2)*316,104+(j//2)*230))
    elif i==1:
        im=Image.new('RGBA',(560,820),PAPER)
        words(im,(12,8),'FREE',108,'#172327','narrowitalic')
        im.alpha_composite(cover(photo_panel(1),515,550),(22,190))
        words(im,(16,380),'A PRINTED EDITION / 02',13,'#172327','mono')
    elif i==2:
        im=Image.new('RGBA',(580,690),'#c75967')
        words(im,(12,5),'WORK',96,PAPER,'narrowitalic')
        im.alpha_composite(cover(hand(),540,465),(20,165))
        words(im,(16,319),'CREATORS / 03',17,'#172327','italic')
    elif i==3:
        im=Image.new('RGBA',(560,760),'#273525')
        words(im,(12,12),'paid',100,'#d3c875','bold')
        for j in range(6):
            p=cover(photo_panel(j%4),137,170)
            im.alpha_composite(p,(38+(j%3)*171,238+(j//3)*195))
        words(im,(20,330),'The work behind the work',18,PAPER,'serif')
    else:
        im=Image.new('RGBA',(680,390),'#d8c5a2')
        im.alpha_composite(cover(hand(),420,345),(230,20))
        words(im,(12,14),'MADE\nTO\nSHARE',43,'#2d3632','narrowitalic')
    return im

@lru_cache(None)
def tile_letter(char, i):
    colors=[('#eeece4','#13191a'),('#141b21','#eee9d9'),('#eeece4','#745f43'),
            ('#788a9a','#ede8df'),('#e8e8dd','#ad351b')]
    bg,fg=colors[i%len(colors)]
    im=Image.new('RGBA',(160,230),bg)
    kinds=['narrow','serif','bold','narrowitalic']
    words(im,(6,0),char,112,fg,kinds[i%4])
    return im

def plane(im, art, x=0, y=0, z=0, width=None, height=None,
          rx=0, ry=0, rz=0, cam=(0,0,0), opacity=1, blur=0):
    """Project a plane, then solve its inverse homography for Pillow sampling."""
    width=width or art.width/S; height=height or width*art.height/art.width
    ax,ay,az=np.radians([rx,ry,rz]); cx,sx=np.cos(ax),np.sin(ax)
    cy,sy=np.cos(ay),np.sin(ay); cz,sz=np.cos(az),np.sin(az)
    R=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]]) @ np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]) @ np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
    pts=np.array([[-width/2,-height/2,0],[width/2,-height/2,0],
                  [width/2,height/2,0],[-width/2,height/2,0]]) @ R.T
    pts+=np.array([x-cam[0],y-cam[1],z-cam[2]])
    depth=1000+pts[:,2]
    if np.any(depth<30): return
    quad=pts[:,:2]*2000/depth[:,None]+np.array([W/2,H/2])
    left=max(0,math.floor(quad[:,0].min())); top=max(0,math.floor(quad[:,1].min()))
    right=min(W,math.ceil(quad[:,0].max())); bottom=min(H,math.ceil(quad[:,1].max()))
    if right<=left or bottom<=top: return
    src=[(0,0),(art.width,0),(art.width,art.height),(0,art.height)]
    A=[]; B=[]
    for (px,py),(u,v) in zip(quad-np.array([left,top]),src):
        A.extend([[px,py,1,0,0,0,-u*px,-u*py],[0,0,0,px,py,1,-v*px,-v*py]])
        B.extend([u,v])
    coeff=np.linalg.solve(np.array(A),np.array(B))
    layer=art.transform((right-left,bottom-top), Image.Transform.PERSPECTIVE,
                        coeff, Image.Resampling.BICUBIC)
    if opacity<1: layer.putalpha(layer.getchannel('A').point(lambda a:round(a*opacity)))
    if blur: layer=layer.filter(ImageFilter.GaussianBlur(blur*S))
    im.alpha_composite(layer,(left,top))

def path(im, points, color, width=3, arrow=False):
    pts=[(round(x*S),round(y*S)) for x,y in points]
    ImageDraw.Draw(im).line(pts,fill=color,width=round(width*S),joint='curve')
    if arrow and len(pts)>1:
        a,b=np.array(pts[-2]),np.array(pts[-1]); v=b-a
        v=v/(np.linalg.norm(v)+1e-6); p=np.array([-v[1],v[0]])
        d=width*S*2.8
        ImageDraw.Draw(im).polygon([tuple(b),tuple(b-v*d+p*d*.4),tuple(b-v*d-p*d*.4)],fill=color)

def bezier(points,n=140):
    p=np.asarray(points,float); ts=np.linspace(0,1,n)
    return [tuple((1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3]) for t in ts]

def arrow_curve(im, points, color, width=3, progress=1):
    pts=bezier(points); pts=pts[:max(2,round(len(pts)*min(1,progress)))]
    path(im,pts,color,width,True)

def ribbon(im,t,front=True):
    col=PAPER if front else '#56676d'; shift=(t-3.15)*(48 if front else -37)
    pts=[(x,235+math.sin((x+shift)/125+(1.1 if front else 0))*82+(x-480)*(.19 if front else -.13)) for x in range(-100,1080,5)]
    # Separate short cross-strips form a physical perforated ribbon.
    for i in range(1,len(pts)-1):
        x,y=pts[i]; dx=pts[i+1][0]-pts[i-1][0]; dy=pts[i+1][1]-pts[i-1][1]
        n=np.array([-dy,dx]); n=n/(np.linalg.norm(n)+1e-6)*13
        path(im,[(x-n[0],y-n[1]),(x+n[0],y+n[1])],col,2)

def smear(im, amount=25, vertical=False):
    result=im.copy()
    for k in range(1,8):
        offset=round(amount*S*k/7)
        shifted=ImageChops.offset(im,0 if vertical else offset,offset if vertical else 0)
        result=Image.blend(result,shifted,.16)
    return result.filter(ImageFilter.GaussianBlur(amount*.07))

def radial(im, strength=.04):
    result=im.copy()
    for k in range(1,6):
        z=1+strength*k/5; nw,nh=round(W*z),round(H*z)
        layer=im.resize((nw,nh),Image.Resampling.BILINEAR)
        layer=layer.crop(((nw-W)//2,(nh-H)//2,(nw+W)//2,(nh+H)//2))
        result=Image.blend(result,layer,.18)
    return result

def grid(t):
    im=ground().copy(); f=t*20
    if t==0:
        plane(im,photo_panel(2),x=320,y=240,width=350,height=300)
        return im
    size=lerp(332,264,ramp(t,.4,.46)); gap=12
    for i,(gx,gy) in enumerate([(-1,-1),(1,-1),(-1,1),(1,1)]):
        start=[.12,0,.06,.08][i]; a=ramp(t,start,start+.09)
        if a<=0: continue
        dx=(1-a)*([0,0,-420,420][i]); dy=(1-a)*([400,-500,0,0][i])
        plane(im,photo_panel(i),x=gx*(size+gap)/2+dx,y=gy*(size*.825+gap)/2+dy,
              width=size,height=size*.825,rx=(1-a)*12,ry=(1-a)*-12)
    if t>=.5:
        words(im,(480,96),'SUNSET',15,PAPER,'bold','mt')
        words(im,(480,611),'MOTION STUDY',11,PAPER,'mono','mt')
    if .75<=t<.9:
        # Three local print tears, preserving surrounding paper tiles.
        i=min(2,int((t-.75)/.05)); y=[265,456,505][i]*S
        band=im.crop((round([230,515,225][i]*S),y,round([470,750,470][i]*S),y+26))
        im.alpha_composite(smear(band,9),(round([270,550,265][i]*S),y))
    return im

def macro(t):
    im=ground().copy()
    if t<.95:
        for i,(gx,gy) in enumerate([(-1,-1),(1,-1),(-1,1),(1,1)]):
            plane(im,photo_panel(i),x=gx*145-170,y=gy*120+30,z=-90,
                  width=275,height=228,rx=20,ry=-16,rz=-15)
        return radial(im,.05)
    first=t<1.5; a=ramp(t,.9,1.0) if first else ramp(t,1.5,1.62)
    i=2 if first else 1
    # Abrupt physical camera move magnifies panels through a tilted grid.
    drift=t-(1.0 if first else 1.65)
    z=lerp(360,-100,a)-drift*18; x=lerp(-500,(-50 if first else -40),a)+drift*7
    y=lerp(220,5,a); rz=lerp(-38,(-4 if first else 5),a)
    for j in range(2):
        plane(im,photo_panel((i+j)%4),x=x+j*590,y=y,z=z+j*10,width=570,height=500,
              rx=7,ry=(-15 if first else 12)+drift*2,rz=rz+drift*.8)
    if t>=1.98:
        im=ImageChops.offset(im,0,round(160*ramp(t,1.98,2.05)*S))
    if .9<=t<1.0 or 1.45<=t<1.6: im=smear(im,65,vertical=1.5<=t<1.6)
    return im

def word_scene(t):
    im=ground().copy(); p=ramp(t,2.05,2.24)
    plane(im,photo_panel(1),x=-185,y=lerp(250,320,p),z=0,width=650,height=540,rz=-9)
    phrase='WORK' if t<2.2 else 'FREE'
    if t>=2.15:
        plane(im,word_art(phrase,113,RUST if t<2.25 else PAPER),x=lerp(220,66,p),y=-100,z=-5,
              width=410,height=112,ry=8,rz=-10)
    if t>=2.25:
        plane(im,word_art('PAID',113),x=190,y=6,z=-40,width=335,height=106,ry=7,rz=-10)
    arrow_curve(im,[(-90,450),(80,130),(510,655),(930,285)],RUST,3,ramp(t,2.1,2.35))
    if t>=2.3: arrow_curve(im,[(920,285),(1050,550),(610,510),(730,170)],RUST,3,ramp(t,2.3,2.45))
    for i in range(4):
        if t>=2.35+i*.05:
            plane(im,photo_panel(i),x=60+i*69,y=-222,z=5,width=65,height=64,rz=-12)
    if t>=2.5:
        words(im,(568,109),'CREATORS / SUNSET',10,PAPER,'mono','mt')
    if t>=2.7: arrow_curve(im,[(750,200),(425,10),(330,126),(300,127)],RUST,3,ramp(t,2.7,2.8))
    if t>=2.9: im=smear(im,75)
    return im

def mustard(t):
    im=ground(MUSTARD).copy(); a=ramp(t,2.95,3.1)
    ribbon(im,t,False)
    travel=lerp(0,-620,ramp(t,3.55,3.95))
    plane(im,hand(),x=370+travel*.7,y=18,z=60,width=1100,height=750,rx=-4,ry=-12,rz=9)
    # Letters arrive independently and remain physical paper foreground planes.
    for i,c in enumerate('CREATORS'):
        start=3.00+i*.049
        if t>=start:
            p=ramp(t,start,start+.07)
            plane(im,tile_letter(c,i),x=-375+i*89+travel,y=8+(i%3-1)*12+(1-p)*140,
                  z=-150-i*2,width=80,height=153,ry=(i%2*2-1)*8,rz=[-8,5,11,-4,6,-9,8,1][i])
    if t>=3.2:
        arrow_curve(im,[(720+travel*.3,690),(330,600),(80,280),(610,350)],RUST,56,ramp(t,3.2,3.42))
    if t>=3.25:
        arrow_curve(im,[(610,780),(740,610),(830,325),(1080,265)],RUST,48,ramp(t,3.25,3.55))
    ribbon(im,t,True)
    for i in range(4):
        start=3.65+i*.05
        if t>=start:
            p=ramp(t,start,start+.08)
            plane(im,photo_panel(i,True),x=-335+i*173+lerp(340,0,p),y=24,z=-30,
                  width=162,height=400,ry=-8,rz=-2)
    if t<3.08: im=smear(im,30*(1-a))
    if t>=4.0: im=radial(im,.25)
    return im

def strips(t):
    im=ground().copy(); p=ramp(t,4.05,4.25)
    for i in range(4):
        plane(im,photo_panel(i,True),x=-322+i*215,y=20,z=i*15,width=210,height=460,
              rx=0,ry=-5,rz=-1+math.sin(t*2)*.5)
    # New material treatment: literal caution tape and screen scratches.
    tape=Image.new('RGBA',(2200,110),'#e8cf42'); d=ImageDraw.Draw(tape)
    for x in range(-200,2400,100): d.polygon([(x,0),(x+35,0),(x-15,25),(x-50,25)],fill=INK)
    for x in range(0,2000,560): words(tape,(x/S,17),'SUNSET  //  CREATORS',25,INK,'narrowitalic')
    plane(im,tape,x=0,y=226,z=-100,width=1100,height=55,rz=7)
    rng=random.Random(66); d=ImageDraw.Draw(im)
    for i in range(13):
        x=rng.randrange(-50,1020)+math.sin(t*9+i)*9
        y=rng.choice([10,675]); length=rng.randrange(100,300)*(.65+.35*p)
        direction=-1 if y>300 else 1; tip=(x+length*.53,y+direction*length)
        ww=rng.randrange(7,22)
        # Independent jagged white ink/torn-paper streaks cross strip boundaries.
        poly=[(x-ww,y),(x+ww*.4,y+3),(tip[0],tip[1]),
              (tip[0]-ww*.7,tip[1]-direction*length*.23),
              (x+ww*.15,y+direction*length*.18)]
        d.polygon([(round(xx*S),round(yy*S)) for xx,yy in poly],fill=PAPER)
        path(im,[(x+ww+4,y),(tip[0]+8,tip[1]-direction*24)],PAPER,2)
    if 4.35<=t<4.4:
        oc=Image.new('RGBA',(900,900),PAPER)
        plane(im,oc,x=lerp(-650,250,ramp(t,4.35,4.4)),y=-150,z=-440,width=650,height=600,ry=38,blur=15)
    if 4.4<=t<4.45: im=Image.new('RGBA',(W,H),'#030403')
    if 4.45<=t<4.5: im=radial(im,.33)
    if 4.5<=t<4.6: im=Image.new('RGBA',(W,H),PAPER)
    return im

def room_background(t, cam=(0,0,0)):
    im=ground('#161b1b').copy()
    plane(im,room(),x=0,y=-10,z=240,width=1420,height=900,rx=0,ry=3,cam=cam)
    return im

def wall(t):
    drift=(t-4.6)*22; pull=ramp(t,5.33,5.45)
    cam=(drift,-10,-100*pull)
    im=room_background(t,cam)
    positions=[(-190,130,-70,320,-3),(-100,-90,60,330,8),(110,80,-40,265,-5),(330,75,15,285,-6),(110,-190,100,300,8)]
    for i,(x,y,z,w,rz) in enumerate(positions):
        start=[4.65,4.75,4.8,4.85,4.95][i]
        if t>=start:
            a=ramp(t,start,start+.06)
            plane(im,poster(i),x=x,y=y+(1-a)*300,z=z,width=w,height=w*poster(i).height/poster(i).width,ry=-8,rz=rz,
                  cam=cam)
    # In front of the print wall: two dark work crates/table forms at another z.
    crate=Image.new('RGBA',(900,230),'#131716'); d=ImageDraw.Draw(crate)
    d.rectangle((15,15,885,210),outline='#434640',width=6)
    for y in range(60,200,18): d.line((38,y,850,y),fill='#242b29',width=5)
    plane(im,crate,x=40,y=290,z=-170,width=760,height=195,ry=-4,cam=cam)
    if t>=4.95: words(im,(50,330),'WORK\nFREE',21,PAPER,'italic')
    if t>=5.35: im=radial(im,.07+pull*.1)
    return im

def profile_space(t):
    p=(t-5.45)/.8; cam=(lerp(40,-30,p),0,-50)
    im=ground('#111a19').copy()
    # Distinct narrow photo space. Side walls converge independently toward the rear.
    plane(im,room(),x=0,y=-10,z=240,width=470,height=800,cam=cam)
    left=room().crop((0,0,1100,941)); right=room().crop((600,0,1672,941))
    plane(im,left,x=-330,y=0,z=0,width=450,height=900,ry=-58,cam=cam)
    plane(im,right,x=330,y=0,z=0,width=450,height=900,ry=58,cam=cam)
    floor=room().crop((0,700,1672,941))
    plane(im,floor,x=0,y=280,z=0,width=1150,height=350,rx=66,cam=cam)
    # A separate, narrow foreground portrait plane retains independent parallax.
    plane(im,figure_art(),x=0,y=10,z=-35,width=242,height=565,ry=-13,rz=2,cam=cam)
    plane(im,poster(3),x=-330,y=40,z=-90,width=185,height=310,ry=-49,rz=-8,cam=cam)
    if t>=5.65:
        count=min(3,1+int((t-5.65)/.1))
        words(im,(58,330),'\n'.join(['WORK','FREE','PAID'][:count]),20,PAPER,'italic')
    if t<5.53:
        oc=photo_panel(3,True).filter(ImageFilter.GaussianBlur(30))
        plane(im,oc,x=lerp(-80,-1200,ramp(t,5.45,5.53)),y=0,z=-620,width=680,height=800,ry=15,blur=18)
    if t>=6.2:
        shade=Image.new('RGBA',(W,H),(0,0,0,220)); im.alpha_composite(shade)
    return im

def hud(im,t,flash=False):
    d=ImageDraw.Draw(im); col=(235,236,224,205)
    words(im,(22,80),'P',24,PAPER,'mono')
    words(im,(940,82),'01  24M  RAW  16:9  4300K',12,PAPER,'mono','rt')
    words(im,(940,490),'AWB\nOFF\nD-R\n100\nC-OFF',11,PAPER,'mono','rt')
    words(im,(22,500),'AF-S\n±0.0\nAUTO\nFINDER',10,PAPER,'mono')
    words(im,(940,632),'0.6”   F2.8   ±0.0   ISO AUTO',12,PAPER,'mono','rt')
    box=(420*S,300*S,540*S,420*S)
    d.rectangle(box,outline=(230,231,224,100),width=1)
    if flash: d.rectangle((452*S,333*S,509*S,390*S),fill=PAPER)
    for x,y in [(32,118),(912,118),(32,604),(912,604)]:
        d.rectangle((x*S,y*S,(x+16)*S,(y+12)*S),outline=col,width=2)

def camera_faces(t):
    im=room_background(t,cam=(20,0,70))
    if t<6.4:
        plane(im,photo_panel(0),x=380,y=-30,z=-140,width=620,height=510,rz=18)
        a=ramp(t,6.25,6.4)
        veil=Image.new('RGBA',(W,H),(0,0,0,round(255*(1-a))))
        im.alpha_composite(veil)
    elif t<6.65:
        a=ramp(t,6.4,6.5)
        plane(im,photo_panel(1),x=lerp(300,22,a)+(t-6.4)*12,y=80,z=-160-(t-6.4)*20,width=850,height=700,ry=-15,rz=8)
    elif t<6.75:
        plane(im,photo_panel(1),x=-30,y=-40,z=-400,width=950,height=740,rz=8)
        im=smear(im,85,True)
    elif t<7.05:
        plane(im,photo_panel(2),x=60+(t-6.75)*18,y=20,z=-300-(t-6.75)*18,width=850,height=700,ry=13,rz=-8)
    elif t<7.25:
        plane(im,photo_panel(3),x=180,y=70,z=-240,width=720,height=680,ry=-22,rz=14)
        im=smear(im,75)
    elif t<7.5:
        plane(im,photo_panel(3),x=40-(t-7.25)*16,y=60,z=-260-(t-7.25)*20,width=780,height=690,ry=-9,rz=8)
    else:
        p=ramp(t,7.5,7.58); z=lerp(-280,90,p)+(t-7.58)*15
        for i,(x,y,ww,hh,rz) in enumerate([(-70,-138,430,250,-8),(-135,117,430,300,7),(130,-15,440,320,-6)]):
            plane(im,photo_panel([1,3,2][i]),x=x,y=y,z=z-i*60,width=ww,height=hh,ry=-8+i*5,rz=rz)
        if t<7.55: im=radial(im,.24)
    if 7.05<=t<7.1:
        # Locally displaced strips form a print tear; this is not a full-frame wipe.
        for j in range(9):
            yy=round((90+j*61)*S); band=im.crop((100*S,yy,900*S,yy+25*S))
            im.alpha_composite(band,(round((100+(-1)**j*45)*S),yy))
    hud(im,t,6.7<=t<6.75 or 7.1<=t<7.15)
    if 7.8<=t<7.85:
        ImageDraw.Draw(im).ellipse((255*S,150*S,705*S,600*S),outline=PAPER,width=3)
    if 7.85<=t<7.9:
        d=ImageDraw.Draw(im)
        for y in range(140,1300,11):
            for x in range(0,W,11): d.ellipse((x,y,x+3,y+3),fill=(10,12,9,175))
    if t>=7.95: ImageDraw.Draw(im).ellipse((463*S,364*S,501*S,402*S),fill=PAPER)
    return im

def frame(n):
    t=n/FPS
    if t<.9: im=grid(t)
    elif t<2.05: im=macro(t)
    elif t<2.95: im=word_scene(t)
    elif t<4.05: im=mustard(t)
    elif t<4.6: im=strips(t)
    elif t<5.45: im=wall(t)
    elif t<6.25: im=profile_space(t)
    else: im=camera_faces(t)
    d=ImageDraw.Draw(im)
    wide=2.95<=t<4.6 or t>=6.25
    bar=68 if wide else 140
    d.rectangle((0,0,W,bar-1),fill='#030403'); d.rectangle((0,H-bar,W,H),fill='#030403')
    return im.convert('RGB')

def comparison(frames):
    # Private analysis only. Reference pixels cannot enter frame() or encoded proof.
    canvas=Image.new('RGB',(1920, (len(frames)+1)*410),'#171a1a')
    d=ImageDraw.Draw(canvas)
    d.text((24,20),'PRIVATE ANALYSIS — SUPPLIED REFERENCE (LEFT) / ORIGINAL SUNSET STUDY (RIGHT)',font=font(15),fill='white')
    for row,n in enumerate(frames):
        native=min(159,round(n/FPS*20)); ref=Image.open(REF/f'frames/{native:06d}.png').convert('RGB')
        for col,pic in enumerate([ref,frame(n)]):
            pic=pic.resize((520,390),Image.Resampling.LANCZOS)
            canvas.paste(pic,(col*960+220,(row+1)*410))
        d.text((25,(row+1)*410+12),f'{n/FPS:.3f}s / ref f{native:03d}',font=font(10),fill='white')
    return canvas

def manifest():
    asset_paths=[HANDS,ASSETS/'creator-portrait.png',ASSETS/'workroom.png']
    return {'format':{'width':W,'height':H,'fps':FPS,'frames':FRAMES,'duration':8,'audio':False},
        'label':'Private throwaway motion study. No product/protocol execution represented.',
        'assets':[{'path':str(p.relative_to(ROOT)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in asset_paths],
        'source_timed_events':[{'source_frame':f,'source_time':f/20,'output_frame':math.ceil(f/20*FPS),'event':e} for f,e in EVENTS],
        'reference_pixels_in_proof':False,
        'projection':'Independent 3D planes; inverse perspective homography, per-layer z, camera translation, rx/ry/rz.'}

def main():
    p=argparse.ArgumentParser(); p.add_argument('--gate',action='store_true'); p.add_argument('--render',action='store_true')
    p.add_argument('--compare',action='store_true'); p.add_argument('--frames',nargs='+',type=int)
    a=p.parse_args(); OUT.mkdir(parents=True,exist_ok=True)
    assert len(EVENTS)>=60 and EVENTS[-1][0]==159
    if a.frames:
        for n in a.frames:
            assert 0<=n<FRAMES
            frame(n).save(OUT/f'keypose-{n:03d}.png')
    if a.gate:
        times=[.6,1.25,1.8,2.6,3.45,4.2,5.0,5.85,6.5,6.9,7.4,7.65]
        sheet=Image.new('RGB',(1920,1440),'#161a1a'); d=ImageDraw.Draw(sheet)
        for i,t in enumerate(times):
            n=round(t*FPS); im=frame(n); im.save(OUT/f'keypose-{n:03d}.png')
            thumb=im.resize((480,360),Image.Resampling.LANCZOS); sheet.paste(thumb,((i%4)*480,(i//4)*480+55))
            d.text(((i%4)*480+15,(i//4)*480+20),f'{t:.2f} s',font=font(13),fill='white')
        sheet.save(OUT/'keypose-gate.jpg',quality=94)
        transition=[.75,.85,.95,1,1.45,1.5,1.6,2.05,2.15,2.25,2.35,2.45,2.85,2.9,2.95,3.05,3.2,3.4,3.6,3.8,4,4.05,4.35,4.4,4.45,4.5,4.6,4.8,5.35,5.45,5.5,6.2,6.25,6.4,6.65,6.7,6.75,7.05,7.1,7.25,7.5,7.55,7.8,7.85,7.95]
        strip=Image.new('RGB',(1920,math.ceil(len(transition)/8)*205),'#171a1a'); d=ImageDraw.Draw(strip)
        for i,t in enumerate(transition):
            thumb=frame(round(t*FPS)).resize((240,180),Image.Resampling.LANCZOS)
            xy=((i%8)*240,(i//8)*205); strip.paste(thumb,xy)
            d.text((xy[0]+6,xy[1]+180),f'{t:.2f}',font=font(8),fill='white')
        strip.save(OUT/'transition-gate.jpg',quality=94)
    if a.compare:
        comparison([12,25,36,52,69,84,100,117,130,138,148,153]).save(OUT/'PRIVATE-reference-comparison.jpg',quality=94)
    if a.render:
        video=OUT/'sunset-collage-motion-match-8s.mp4'
        proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}',
            '-r',str(FPS),'-i','-','-an','-vf','scale=in_range=full:out_range=tv:in_color_matrix=bt709:out_color_matrix=bt709,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709,format=yuv420p',
            '-c:v','libx264','-preset','fast','-crf','14','-pix_fmt','yuv420p',
            '-color_range','tv','-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709',
            '-movflags','+faststart',str(video)],stdin=subprocess.PIPE)
        for n in range(FRAMES):
            proc.stdin.write(frame(n).tobytes())
            if n%30==0: print(f'{n}/{FRAMES}',flush=True)
        proc.stdin.close(); assert proc.wait()==0
        print(video,flush=True)
    (OUT/'motion-manifest.json').write_text(json.dumps(manifest(),indent=2)+'\n')

if __name__=='__main__': main()
