#!/usr/bin/env python3
"""Original eight-second silent editorial spike; no reference media is consumed."""
import argparse
import hashlib
import json
import math
import random
import subprocess
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / '.publication/sunset-launch-v13'
FONT = ROOT / '.publication/sunset-launch-v6/fonts/BricolageGrotesque-VF.ttf'
SMALL = ROOT / '.publication/sunset-launch-v1/render/Geist.ttf'
CREATOR = OUT / 'assets/creator-cutout.png'
W, H, FPS, N = 1920, 1080, 30, 240
CREAM, INK, CORAL, MINT, OCHRE = '#f7f0dd', '#173f37', '#b83d25', '#bdd7be', '#e6bb69'
SAFE = [90, 70, 1830, 1010]
READS = [
    {'id': 'value', 'window': [.35, 2.15], 'lines': ['Useful work.', 'Shared freely.'], 'minimum': 1.7},
    {'id': 'maker', 'window': [2.95, 4.70], 'lines': ['Help creators', 'keep creating.'], 'minimum': 1.7},
    {'id': 'promise', 'window': [5.40, 8.0], 'lines': ['Free to use.', 'Creators paid.'], 'minimum': 2.45},
]

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def rel(p):
    return str(Path(p).resolve().relative_to(ROOT))

def ramp(t, a, b):
    x = max(0, min(1, (t-a)/(b-a)))
    return 1-(1-x)**3

@lru_cache(None)
def font(size, small=False, weight=800):
    f = ImageFont.truetype(str(SMALL if small else FONT), size)
    f.set_variation_by_axes([weight] if small else [96, weight, 100])
    return f

def text(im, pos, value, size, color=INK, small=False, weight=800):
    d, f = ImageDraw.Draw(im), font(size, small, weight)
    d.text(pos, value, font=f, fill=color, anchor='lt')
    return list(d.textbbox(pos, value, font=f, anchor='lt'))

def mark(im):
    # Public icon.svg's original SUNSET geometry, enlarged without its rounded tile.
    d = ImageDraw.Draw(im)
    x, y, k = 108, 94, 1.25
    d.pieslice((x+10*k,y+12*k,x+54*k,y+56*k),180,360,fill=CORAL)
    for a,b,yy in [(11,53,40),(16,48,47),(23,41,54)]:
        d.line((x+a*k,y+yy*k,x+b*k,y+yy*k),fill=CORAL,width=4)

@lru_cache(None)
def ground(dark=False):
    im = Image.new('RGBA',(W,H),INK if dark else CREAM)
    d, rng = ImageDraw.Draw(im), random.Random(735)
    for _ in range(6800):
        d.point((rng.randrange(W),rng.randrange(H)),fill='#244940' if dark else '#e7decb')
    return im

@lru_cache(None)
def paper(kind):
    im = Image.new('RGBA',(560,630),'#faf5e8')
    d, rng = ImageDraw.Draw(im), random.Random(41+kind)
    for _ in range(3600):
        d.point((rng.randrange(560),rng.randrange(630)),fill='#e7dfcd')
    d.rectangle((0,0,560,18),fill=[CORAL,INK,OCHRE][kind])
    text(im,(38,47),['01 / LESSON','02 / WORKSHOP','03 / GUIDE'][kind],24,small=True,weight=650)
    if kind == 0:
        text(im,(38,100),'Make a',58); text(im,(38,161),'little sense.',58)
        d.ellipse((65,278,267,480),outline=CORAL,width=12)
        d.polygon([(304,293),(469,469),(277,469)],fill=MINT,outline=INK,width=5)
        d.line((82,383,457,383),fill=INK,width=4)
        d.line((170,265,170,497),fill=INK,width=4)
        d.arc((176,250,433,505),210,335,fill=CORAL,width=5)
        text(im,(38,552),'A small idea. A new perspective.',21,small=True,weight=500)
    elif kind == 1:
        text(im,(38,100),'Bring people',58); text(im,(38,161),'together.',58)
        for i,words in enumerate(['Make space','Gather materials','Leave time to listen']):
            yy=300+i*74
            d.rectangle((41,yy,70,yy+29),outline=INK,width=3)
            if i == 0: d.line((45,yy+12,54,yy+22,69,yy+3),fill=CORAL,width=5)
            text(im,(92,yy-1),words,27,small=True,weight=550)
        d.rectangle((37,549,522,568),fill=MINT)
    else:
        text(im,(38,100),'Keep useful',58); text(im,(38,161),'things going.',58)
        d.rounded_rectangle((96,285,434,465),radius=30,fill=OCHRE,outline=INK,width=5)
        d.line((163,322,163,426),fill=INK,width=6)
        d.line((364,322,364,426),fill=INK,width=6)
        d.line((163,373,364,373),fill=INK,width=6)
        d.ellipse((239,347,291,399),fill=CREAM,outline=INK,width=4)
        text(im,(38,552),'Simple steps, made to be kept.',22,small=True,weight=500)
    for xx in range(0,560,13):
        d.polygon([(xx,630),(xx+6,624+rng.randrange(5)),(xx+13,630)],fill=(0,0,0,0))
    return im

def paste(im, layer, center, angle=0, scale=1, shadow=True):
    layer=layer.resize((round(layer.width*scale),round(layer.height*scale)),Image.Resampling.LANCZOS)
    layer=layer.rotate(angle,Image.Resampling.BICUBIC,expand=True)
    x,y=round(center[0]-layer.width/2),round(center[1]-layer.height/2)
    if shadow:
        shade=Image.new('RGBA',layer.size,(0,0,0,0))
        shade.putalpha(layer.getchannel('A').point(lambda a:a//8))
        im.alpha_composite(shade.filter(ImageFilter.GaussianBlur(13)),(x+12,y+19))
    im.alpha_composite(layer,(x,y))

@lru_cache(None)
def maker():
    assert CREATOR.exists(),'Original creator artwork required; no placeholder final render.'
    im=Image.open(CREATOR).convert('RGBA')
    assert im.size==(1536,1024) and im.getextrema()[3][0]==0
    return im

def label(im,dark=False):
    text(im,(1614,83),'CONCEPT PREVIEW',22,CREAM if dark else INK,True,650)

@lru_cache(2)
def value_scene(t):
    im=ground().copy(); d=ImageDraw.Draw(im)
    d.rectangle((1390,0,1920,1080),fill=OCHRE)
    d.ellipse((1453,128,1750,425),outline=CORAL,width=5)
    text(im,(1503,226),'OPEN',53,CORAL)
    text(im,(113,87),'GOOD IDEAS DESERVE TO TRAVEL',23,small=True,weight=650)
    # A workshop detail pulls back into a triptych; type remains fixed above it.
    collage=Image.new('RGBA',(W,H),(0,0,0,0))
    for i,(cx,cy,angle) in enumerate([(386,868,8),(969,879,-4),(1535,856,-9)]):
        enter,push=ramp(t,i*.12,.52+i*.12),ramp(t,1.43,1.82)
        y=cy+(1-enter)*65-push*(24 if i!=1 else 60)
        x=cx+(1-enter)*(-70 if i==0 else 70)
        paste(collage,paper(i),(x,y),angle+(1-enter)*6-push*1.5,.88+push*.055)
    lower=collage.crop((0,535,W,H))
    pull=ramp(t,.20,1.08)
    zoom=2.7-1.7*pull
    cw,ch=W/zoom,(H-535)/zoom
    cx,cy=970,300
    cx=cx+(W/2-cx)*pull; cy=cy+((H-535)/2-cy)*pull
    crop=lower.crop((round(cx-cw/2),round(cy-ch/2),round(cx+cw/2),round(cy+ch/2)))
    lower=crop.resize((W,H-535),Image.Resampling.LANCZOS)
    im.alpha_composite(lower,(0,535))
    # This visible print divider, held before the cut, is the next scene's mask origin.
    d=ImageDraw.Draw(im)
    d.rectangle((112,515,1807,522),fill=CORAL)
    slide=round((1-ramp(t,0,.22))*48)
    boxes=[text(im,(104+slide,176),'Useful work.',154),text(im,(104+slide,345),'Shared freely.',154)]
    label(im)
    return im,boxes

@lru_cache(2)
def maker_scene(t):
    im=ground(True).copy(); d=ImageDraw.Draw(im)
    d.rectangle((112,715,794,727),fill=CORAL)
    d.ellipse((1450,110,1790,450),fill=CORAL)
    shift=(1-ramp(t,2.50,3.03))*90
    paste(im,maker(),(1550+shift,707),-3+3*ramp(t,2.50,3.03),.77,False)
    text(im,(117,770),'A person. Time. Care.',37,CREAM,True,550)
    text(im,(117,867),'THE WORK BEHIND THE WORK',23,MINT,True,650)
    boxes=[text(im,(110,173),'Help creators',128,CREAM),text(im,(110,323),'keep creating.',128,CREAM)]
    label(im,True)
    return im,boxes

@lru_cache(None)
def promise_scene():
    im=ground().copy(); d=ImageDraw.Draw(im)
    d.rectangle((0,865,W,H),fill=OCHRE)
    for i,angle in enumerate([10,0,-10]): paste(im,paper(i),(254+i*137,1000),angle,.38)
    paste(im,maker(),(1515,1015),0,.43,False)
    mark(im); text(im,(212,111),'SUNSET',43,INK,True,700)
    d.line((112,633,1807,633),fill=CORAL,width=7)
    boxes=[text(im,(104,235),'Free to use.',174),text(im,(104,425),'Creators paid.',174)]
    text(im,(111,699),'SUPPORT ONCE. SHARE FOREVER.',26,INK,True,650)
    label(im)
    return im,boxes

def frame(n):
    t=n/FPS
    if t<2.4: im,boxes=value_scene(min(t,1.82))
    elif t<4.9:
        old,_=value_scene(1.82); new,boxes=maker_scene(min(t,3.03))
        p=ramp(t,2.4,2.84); mask=Image.new('L',(W,H),0); radius=3+round(650*p)
        ImageDraw.Draw(mask).rectangle((0,519-radius,W,519+radius),fill=255)
        im=Image.composite(new,old,mask)
        if p<1: ImageDraw.Draw(im).line((0,519-radius,W,519-radius),fill=CORAL,width=7)
    else:
        new,boxes=promise_scene(); new=new.copy(); old,_=maker_scene(3.03)
        # The existing coral disc becomes an aperture carrying one whole FREE mark.
        alpha=round(255*(1-ramp(t,5.03,5.27)))
        if alpha:
            word=Image.new('RGBA',(W,H),(0,0,0,0))
            text(word,(1503,235),'FREE',82,(23,63,55,alpha))
            new.alpha_composite(word)
        p=ramp(t,4.9,5.36); mask=Image.new('L',(W,H),0); r=170+round(2180*p)
        ImageDraw.Draw(mask).ellipse((1620-r,280-r,1620+r,280+r),fill=255)
        im=Image.composite(new,old,mask)
    phase='value' if t<2.4 else 'maker' if t<4.9 else 'promise'
    read=next((r for r in READS if r['window'][0]<=t<r['window'][1]),None)
    record={'frame':n,'time':t,'phase':phase,'essential_text':[]}
    if read:
        for words,bbox in zip(read['lines'],boxes):
            assert SAFE[0]<=bbox[0]<bbox[2]<=SAFE[2] and SAFE[1]<=bbox[1]<bbox[3]<=SAFE[3],(n,words,bbox)
            record['essential_text'].append({'text':words,'bbox':bbox,'foreground':CREAM if phase=='maker' else INK,'background':INK if phase=='maker' else CREAM})
    return im.convert('RGB'),record

def sheet(pairs,target,width=640,columns=3):
    cell_h=round(width*H/W)+36
    out=Image.new('RGB',(width*columns,cell_h*math.ceil(len(pairs)/columns)),CREAM); d=ImageDraw.Draw(out)
    for i,(n,path) in enumerate(pairs):
        x,y=i%columns*width,i//columns*cell_h
        with Image.open(path) as im: out.paste(im.resize((width,round(width*H/W)),Image.Resampling.LANCZOS),(x,y))
        d.text((x+12,y+cell_h-28),f'f{n:03d} / {n/FPS:.3f}s',font=font(18,True,500),fill=INK)
    out.save(target,quality=96)

def write_json(p,data):
    p.write_text(json.dumps(data,indent=2)+'\n')

def poses():
    folder=OUT/'poses'; folder.mkdir(parents=True,exist_ok=True)
    ids=[8,27,58,76,89,114,153,189]; pairs=[]
    for n in ids:
        path=folder/f'{n:06d}.png'; frame(n)[0].save(path); pairs.append((n,path))
    sheet(pairs,OUT/'poses-contact.jpg')
    for n,name in [(27,'01-value.png'),(114,'02-maker.png'),(189,'03-promise.png')]: frame(n)[0].save(OUT/name)
    print(json.dumps({'native_poses':ids,'contact':rel(OUT/'poses-contact.jpg'),'gate':[rel(OUT/x) for x in ['01-value.png','02-maker.png','03-promise.png']]}))

def motion_poses():
    folder=OUT/'motion-poses'; folder.mkdir(parents=True,exist_ok=True)
    ids=[3,18,33,65,72,75,78,81,84,147,150,153,156,159,162]
    for n in ids: frame(n)[0].save(folder/f'{n:06d}.png')
    sheet([(n,folder/f'{n:06d}.png') for n in [3,18,33,65,147,150,153,156,162]],OUT/'motion-correction-contact.jpg')
    for name,seq in [('rule',[65,72,75,78,81,84]),('circle',[147,150,153,156,159,162])]:
        sheet([(n,folder/f'{n:06d}.png') for n in seq],OUT/f'{name}-mask-native-gate.jpg',640,3)
    print(json.dumps({'gate':rel(OUT/'motion-correction-contact.jpg'),'native_folder':rel(folder),'rule':rel(OUT/'rule-mask-native-gate.jpg'),'circle':rel(OUT/'circle-mask-native-gate.jpg')}))

def contrast(a,b):
    def lum(c):
        v=[int(c[i:i+2],16)/255 for i in [1,3,5]]
        return sum((x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4)*k for x,k in zip(v,[.2126,.7152,.0722]))
    x,y=sorted([lum(a),lum(b)]); return (y+.05)/(x+.05)

def render():
    folder=OUT/'frames'; folder.mkdir(parents=True,exist_ok=True); records=[]
    for n in range(N):
        im,record=frame(n); path=folder/f'{n:06d}.png'; im.save(path,compress_level=3)
        record.update({'path':rel(path),'sha256':sha(path)})
        for item in record['essential_text']:
            item['contrast_ratio']=contrast(item['foreground'],item['background']); assert item['contrast_ratio']>7
        records.append(record)
    for read in READS:
        rr=[r for r in records if read['window'][0]<=r['time']<read['window'][1]]
        assert len(rr)/FPS>=read['minimum'],read
        assert all([x['text'] for x in r['essential_text']]==read['lines'] for r in rr)
    target=OUT/'sunset-v13-style-proof.mp4'
    assert not target.exists(),'Encode once: remove only a rejected output deliberately before retrying.'
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-framerate',str(FPS),'-i',str(folder/'%06d.png'),'-vf',
         'scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709',
         '-an','-c:v','libx264','-preset','medium','-crf','14','-threads','4','-g','60','-color_range','tv',
         '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-frames:v',str(N),'-movflags','+faststart',str(target)]
    subprocess.run(cmd,check=True)
    decoded=OUT/'decoded'; decoded.mkdir(exist_ok=True)
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(target),'-vsync','0','-start_number','0',str(decoded/'%06d.png')],check=True)
    images=sorted(decoded.glob('*.png')); assert len(images)==N
    for path in images:
        with Image.open(path) as im: assert im.size==(W,H); im.verify()
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(target)],text=True))
    v=probe['streams'][0]
    assert len(probe['streams'])==1 and v['codec_name']=='h264' and v['pix_fmt']=='yuv420p'
    assert [v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']),v['color_range']]==[W,H,'30/1',N,'tv']
    assert all(v[k]=='bt709' for k in ['color_space','color_transfer','color_primaries'])
    assert abs(float(probe['format']['duration'])-8)<1/FPS
    atoms=[]
    with target.open('rb') as stream:
        while header:=stream.read(8):
            assert len(header)==8
            size,kind=int.from_bytes(header[:4],'big'),header[4:].decode('ascii')
            head=8
            if size==1: size=int.from_bytes(stream.read(8),'big'); head=16
            assert size>=head
            atoms.append(kind); stream.seek(size-head,1)
    assert atoms.index('moov')<atoms.index('mdat'),'Missing faststart'
    sheet([(n,decoded/f'{n:06d}.png') for n in [8,27,58,76,89,114,153,189,239]],OUT/'decoded-beat-sheet.jpg')
    sheet([(n,decoded/f'{n:06d}.png') for n in [65,70,71,72,73,76,83,84,85,86,144,146,147,148,150,153,160,161]],OUT/'decoded-cut-sheet.jpg',480,4)
    for name,a,b in [('rule-mask',66,91),('circle-mask',141,166)]:
        sheet([(n,decoded/f'{n:06d}.png') for n in range(a,b,3)],OUT/f'{name}-100ms.jpg',480,3)
    report={'schema':1,'stage':'original eight-second style spike','status':'Await decoded-frame creative review',
            'dimensions':[W,H],'fps':FPS,'frames':N,'duration':8,'silent':True,'encode_passes':1,'crf':14,
            'full_240_frame_decode':True,'mp4_atoms':atoms,'safe_bbox':SAFE,'reading_windows':READS,
            'source_hashes':{rel(p):sha(p) for p in [Path(__file__),FONT,SMALL,CREATOR,ROOT/'projects/sunset/public/icon.svg']},
            'movie':{'path':rel(target),'sha256':sha(target),'bytes':target.stat().st_size},
            'reference_pixels_or_audio_used':False,'original_creator_illustration':True,'new_resource_or_financial_action_claimed':False,
            'creator_alpha_preserved':True,'occlusion_model':'Intentional 2D collage/masks; no 3D collision claim.',
            'encode_command':cmd,'probe':probe,'records':records,
            'limits':['Author bounds/contrast records require decoded-picture visual inspection.','Silent concept only; no real action or full mechanism explanation.']}
    write_json(OUT/'render-report.json',report)
    print(json.dumps({'movie':rel(target),'sha256':sha(target),'frames':len(images),'report':rel(OUT/'render-report.json')}))

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--poses',action='store_true'); p.add_argument('--motion-poses',action='store_true'); p.add_argument('--render',action='store_true'); args=p.parse_args()
    assert sum([args.poses,args.motion_poses,args.render])==1,'Choose --poses, --motion-poses or --render.'
    OUT.mkdir(parents=True,exist_ok=True)
    poses() if args.poses else motion_poses() if args.motion_poses else render()
