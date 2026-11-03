#!/usr/bin/env python3
"""SUNSET v5. Native-source editorial compositor, locked to actual 24s voice."""
import argparse, functools, hashlib, json, math, subprocess, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
ROOT=Path(__file__).resolve().parents[4]
SRC=Path(__file__).resolve().parent
OUT=ROOT/".publication/sunset-launch-v5"
V1=ROOT/".publication/sunset-launch-v1"
W,H,FPS,DURATION=1920,1080,30,24
S=1.5
BLACK=(16,19,22)
CREAM=(242,240,233)
WHITE=CREAM
CORAL=(153,106,77)
MUTED=(180,180,175)
FONT=V1/"render/Geist.ttf"
LOGO=Image.open(V1/"render/logo.png").convert("RGBA")
SAFE=(192,108,1728,972)
CG_INDICES=list(range(486))+list(range(588,630))
READS=[
 {"id":"hook","lines":["OUTLAST","THE WEBSITE"],"window":[.55,2.95],"plane":[128,144,628,444],"size":82},
 {"id":"community","lines":["COMMUNITIES","FUND LEARNING"],"window":[3.60,5.30],"plane":[128,154,628,432],"size":65},
 {"id":"near","lines":["NEAR","ESCROW"],"window":[5.70,7.45],"plane":[128,150,628,443],"size":93},
 {"id":"key","lines":["AGREED","KEY"],"window":[8.20,10.10],"plane":[128,145,628,446],"size":98},
 {"id":"creator","lines":["CREATOR CAN","WITHDRAW"],"window":[10.65,12.75],"plane":[128,147,628,437],"size":73},
 {"id":"deadline","lines":["DEADLINES","ENFORCED"],"window":[13.30,14.55],"plane":[128,148,628,433],"size":73},
 {"id":"refund","lines":["CLAIM","REFUNDS"],"window":[14.70,16.00],"plane":[128,150,628,442],"size":89},
 {"id":"support","lines":["SUPPORT","ONCE."],"window":[19.65,20.95],"plane":[128,148,628,446],"size":100},
]
def px(x):
    return round(x * S)

def clamp(x):
    return max(0.0, min(1.0, x))

def ease(x):
    return 1 - (1 - clamp(x)) ** 3

def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def spring(x):
    if x <= 0:
        return 0
    return 1 - math.exp(-7.5 * x) * (math.cos(10.5 * x) + .20 * math.sin(10.5 * x))

@functools.lru_cache(maxsize=72)
def font(size, weight=600):
    f = ImageFont.truetype(str(FONT), px(size))
    f.set_variation_by_axes([weight])
    return f

@functools.lru_cache(maxsize=400)
def word(value, size, color=BLACK, weight=600):
    f = font(size, weight)
    b = f.getbbox(value)
    im = Image.new("RGBA", (max(1, b[2] - b[0] + px(8)), max(1, b[3] - b[1] + px(8))))
    ImageDraw.Draw(im).text((px(4) - b[0], px(4) - b[1]), value, font=f, fill=(*color, 255))
    return im

def put(dst, image, xy, scale=1, angle=0, alpha=1, center=False):
    if scale <= .005 or alpha <= 0:
        return
    im = image
    if abs(scale - 1) > .001:
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.Resampling.BICUBIC)
    if angle:
        im = im.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    if alpha < .999:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda n: round(n * clamp(alpha))))
    x, y = px(xy[0]), px(xy[1])
    if center:
        x -= im.width // 2
        y -= im.height // 2
    dst.alpha_composite(im, (x, y))

def text(dst, value, xy, size=26, color=BLACK, weight=600, center=False, alpha=1):
    put(dst, word(value, size, color, weight), xy, center=center, alpha=alpha)

def line(dst, points, color=BLACK, width=1):
    ImageDraw.Draw(dst).line([(px(x), px(y)) for x, y in points], fill=color, width=max(1, px(width)))

def rectangle(dst, bounds, fill, outline=None, radius=0, width=1):
    ImageDraw.Draw(dst).rounded_rectangle(tuple(px(v) for v in bounds), radius=px(radius), fill=fill, outline=outline, width=max(1, px(width)))

def dot(dst, x, y, radius=3, fill=CORAL):
    ImageDraw.Draw(dst).ellipse(tuple(px(v) for v in (x-radius, y-radius, x+radius, y+radius)), fill=fill)

def guide(dst, box, color, label=None):
    x, y, w, h = box
    line(dst, [(x, y), (x+w, y), (x+w, y+h), (x, y+h), (x, y)], color)
    for a, b in [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]:
        rectangle(dst, (a-3, b-3, a+3, b+3), color)
    if label:
        text(dst, label, (x, y-25), 15, color, 450)

def cross(dst, x, y, color=CORAL, r=7):
    line(dst, [(x-r, y), (x+r, y)], color)
    line(dst, [(x, y-r), (x, y+r)], color)

def glyphs(dst, value, center_x, y, size, elapsed, color=BLACK, mode="scatter", tracking=0, weight=620):
    f = font(size, weight)
    advances = [(f.getlength(c) / S + tracking) for c in value]
    start = center_x - sum(advances) / 2
    x = start
    for i, (c, adv) in enumerate(zip(value, advances)):
        q = spring((elapsed - i*.035) / .55)
        settled = clamp(q)
        dx, dy, angle = 0, 0, 0
        if mode == "scatter":
            dx = ((i*233) % 760 - 380) * (1-q)
            dy = ((i*181) % 540 - 270) * (1-q)
            angle = ((i%5)-2)*22*(1-q)
        elif mode == "rise":
            dy = (400 + (i%3)*90) * (1-q)
        elif mode == "spread":
            dx = (i-(len(value)-1)/2) * 260 * (1-q)
            dy = (1-q) * (-130 if i%2 else 130)
        if c != " ":
            put(dst, word(c, size, color, weight), (x+dx, y+dy), angle=angle, alpha=clamp((elapsed-i*.035)*6), scale=.78+.22*settled)
        x += adv


def linear_channel(v):
    v=v/255
    return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4

def contrast(a,b):
    lum=lambda c:sum(w*linear_channel(v) for w,v in zip((.2126,.7152,.0722),c))
    x,y=sorted((lum(a),lum(b)))
    return (y+.05)/(x+.05)

@functools.lru_cache(maxsize=512)
def solid_probe(value,size,color,weight):
    tile=word(value,size,color,weight)
    alpha=tile.getchannel("A").point(lambda n:255 if n>=254 else 0)
    for radius in (5,3,1):
        mask=alpha.filter(ImageFilter.MinFilter(radius)) if radius>1 else alpha
        bounds=mask.getbbox()
        if not bounds:continue
        center=((bounds[0]+bounds[2])/2,(bounds[1]+bounds[3])/2)
        best=None
        for n,v in enumerate(mask.tobytes()):
            if not v:continue
            x,y=n%tile.width,n//tile.width
            distance=(x-center[0])**2+(y-center[1])**2
            if best is None or distance<best[0]:best=(distance,x,y)
        return best[1],best[2],radius
    raise RuntimeError("No fully opaque glyph pixel to measure")

def safe_text(dst,value,xy,size,color=BLACK,weight=600,center=False,records=None,kind="headline",bg=CREAM):
    tile=word(value,size,color,weight)
    x,y=px(xy[0]),px(xy[1])
    if center:
        x-=tile.width//2;y-=tile.height//2
    alpha=tile.getchannel("A")
    b=alpha.getbbox()
    bbox=[x+b[0],y+b[1],x+b[2],y+b[3]]
    if any((bbox[0]<SAFE[0],bbox[1]<SAFE[1],bbox[2]>SAFE[2],bbox[3]>SAFE[3])):
        raise RuntimeError(f"Essential {kind} outside title-safe region: {value} {bbox}")
    dst.alpha_composite(tile,(x,y))
    if records is not None:
        gx,gy,patch=solid_probe(value,size,color,weight)
        actual_fg=dst.getpixel((x+gx,y+gy))[:3]
        actual_bg=dst.getpixel((x,y))[:3]
        actual_contrast=contrast(actual_fg,actual_bg)
        if actual_contrast<4.5:
            raise RuntimeError(f"Actual text/plane pixels fail contrast: {value} {actual_fg} {actual_bg}")
        records.append({"kind":kind,"text":value,"bbox":bbox,"foreground":color,"background":bg,"contrast":actual_contrast,"actual_pixel_foreground":actual_fg,"actual_pixel_background":actual_bg,"probe_foreground_xy":[x+gx,y+gy],"foreground_opaque_patch_size":patch,"probe_background_xy":[x,y],"solid_protected":True})
    return bbox

def fit_size(lines,size,width):
    while max(word(v,size).width/S for v in lines)>width:
        size-=.5
    return size

def headline(dst,read,t,records):
    a,b=read["window"]
    # Read windows use static final glyphs. Crop/scatter is restricted to the entrance.
    previous=[r["window"][1] for r in READS if r["window"][1]<=a]
    start=max(a-.32,max(previous,default=-1)+.02)
    if read["id"]=="key":start=max(start,8.16)
    if read["id"]=="deadline":start=max(start,13.27)
    if not start <=t< b:
        return
    x0,y0,x1,y1=read["plane"]
    dark=read["id"]!="near"
    bg,fg=(BLACK,CREAM) if dark else (CREAM,BLACK)
    rectangle(dst,(x0,y0,x1,y1),bg)
    line(dst,[(x0+22,y0+23),(x0+77,y0+23)],CORAL,3)
    size=fit_size(read["lines"],read["size"],x1-x0-44)
    step=size*1.06
    rows=len(read["lines"])
    y=y0+(y1-y0-rows*step)/2+9
    if t<a:
        q=ease((t-start)/(a-start))
        overlay=Image.new("RGBA",(W,H))
        for rownum,row in enumerate(read["lines"]):
            f=font(size,620)
            cursor=x0+22
            for i,c in enumerate(row):
                delay=(i%5)*.023
                progress=ease(clamp((q-delay)/(1-delay)))
                drift=1-progress
                if c!=" ":
                    put(overlay,word(c,size,fg,620),(cursor+((i*67)%97-48)*drift,y+rownum*step+((i%3)-1)*98*drift),angle=((i%5)-2)*13*drift,alpha=progress)
                cursor+=f.getlength(c)/S
        # Entrance material stays clipped to the exact type slab.
        crop=overlay.crop(tuple(px(v) for v in (x0,y0,x1,y1)))
        dst.alpha_composite(crop,(px(x0),px(y0)))
    else:
        for i,row in enumerate(read["lines"]):
            safe_text(dst,row,(x0+22,y+i*step),size,fg,620,records=records,bg=bg)

def context_brand(dst,t,actual=False):
    # Small truthful context, secondary to the essential type/caption hierarchy.
    put(dst,LOGO,(140,77),.16)
    text(dst,"SUNSET",(177,82),16,CREAM,650)
    rectangle(dst,(1000,74,1148,102),BLACK)
    text(dst,"NEAR TESTNET",(1010,80),13,CREAM,550)
    if t<21:
        value="ACTUAL RESOURCE" if actual else "PROTOCOL VISUALIZATION"
        rectangle(dst,(138,508,390 if actual else 438,535),BLACK)
        text(dst,value,(148,514),13,CREAM,450)

def caption_rows(value,maxwidth=966):
    parts=value.split()
    width=lambda v:word(v,32,CREAM,500).width/S
    if len(parts)<=6 and width(value)<=maxwidth:return [value]
    options=[]
    for split in range(1,len(parts)):
        rows=[" ".join(parts[:split])," ".join(parts[split:])]
        if any(len(v.split())>6 or width(v)>maxwidth for v in rows):continue
        options.append((abs(width(rows[0])-width(rows[1])),rows))
    if not options:raise RuntimeError("Caption cannot fit two six-word lines")
    return min(options,key=lambda item:item[0])[1]

def captions(dst,t,cues,records):
    for cue in cues:
        if cue["start"]<=t<cue["end"]:
            rows=caption_rows(cue["text"])
            size=32;step=38
            h=step*len(rows)+18
            top=646-h
            width=max(word(row,size,CREAM,500).width/S for row in rows)+36
            left=(1280-width)/2
            rectangle(dst,(left,top,left+width,646),BLACK)
            for i,row in enumerate(rows):
                safe_text(dst,row,(640,top+11+i*step+word(row,size,CREAM,500).height/S/2),size,CREAM,500,True,records,"caption",BLACK)

class Scenes:
    def __init__(self,directory,strict=False):
        self.directory=Path(directory);self.strict=strict;self.hashes={}
        self.indices=sorted(int(p.stem) for p in self.directory.glob("??????.png"))
        if strict:
            missing=[i for i in CG_INDICES if not (self.directory/f"{i:06d}.png").exists()]
            if missing:raise RuntimeError(f"Missing {len(missing)} exact native CG frames")
    def validate_manifest(self,path):
        metadata=json.loads(Path(path).read_text())
        native=metadata["native"];sequence=metadata["sequence"]
        for key,expected in (("width",W),("height",H),("fps",FPS),("format","png"),("frames",len(CG_INDICES))):
            if native.get(key)!=expected:raise RuntimeError(f"Native capture {key} mismatch")
        if not native.get("antialias") or native.get("samples",0)<4:raise RuntimeError("Native MSAA4 required")
        if sequence.get("nearest_frame_fallback") is not False:raise RuntimeError("Nearest source fallback forbidden")
        if sequence.get("captured_indices")!=CG_INDICES or sequence.get("required_indices")!=CG_INDICES:
            raise RuntimeError("Complete exact visible-frame sequence required")
        if metadata["source_sha256"]!=hashlib.sha256((SRC/"scene.mjs").read_bytes()).hexdigest():
            raise RuntimeError("Capture manifest is stale for current scene source")
        if metadata["renderer_sha256"]!=hashlib.sha256((SRC/"render_scene.mjs").read_bytes()).hexdigest():
            raise RuntimeError("Capture manifest is stale for current scene renderer")
        for record in metadata["records"]:
            if not record["actual_context_antialias"] or record["actual_samples"]<4:
                raise RuntimeError("Frame captured without actual MSAA4")
            self.hashes[record["frame"]]=record["sha256"]
        if sorted(self.hashes)!=CG_INDICES:raise RuntimeError("Missing native frame hashes")
        return metadata
    @functools.lru_cache(maxsize=3)
    def load(self,n):
        path=self.directory/f"{n:06d}.png"
        if not path.exists():
            raise RuntimeError(f"Exact frame required, no nearest fallback: {path}")
        if self.strict and hashlib.sha256(path.read_bytes()).hexdigest()!=self.hashes[n]:
            raise RuntimeError(f"Native scene frame changed since capture: {n}")
        image=Image.open(path).convert("RGBA")
        if image.size!=(W,H):raise RuntimeError(f"Native 1080p source required: {path} {image.size}")
        return image
    def at(self,t):
        return self.load(max(0,min(719,round(t*FPS)))).copy()

class ProductPixels:
    """Manifest supplies real DPR2 source rectangles. No synthetic app chrome."""
    def __init__(self,manifest):
        self.path=Path(manifest);self.manifest=None;self.sources={}
        if self.path.exists():
            self.manifest=json.loads(self.path.read_text())
    def get(self,kind):
        if kind not in self.sources:
            if self.manifest is None:
                raise RuntimeError(f"Actual high-resolution product manifest required: {self.path}")
            spec=self.manifest["compositor"][kind]
            path=ROOT/spec["path"]
            im=Image.open(path).convert("RGBA")
            if "crop" in spec:im=im.crop(tuple(spec["crop"]))
            if hashlib.sha256(path.read_bytes()).hexdigest()!=spec["sha256"]:
                raise RuntimeError(f"Actual UI source hash changed: {path}")
            self.sources[kind]=(im,spec)
        return self.sources[kind]
    def panel(self,dst,kind,t,records):
        source,spec=self.get(kind)
        available=(1440,540)
        scale=min(1,available[0]/source.width,available[1]/source.height)
        tile=source.resize((round(source.width*scale),round(source.height*scale)),Image.Resampling.LANCZOS)
        x=(W-tile.width)//2;y=round(290-tile.height*.12)
        if "focus" in spec:
            q=ease((t-spec["zoom_start"])/spec["zoom_duration"])
            scale=scale+(1-scale)*q
            tile=source.resize((round(source.width*scale),round(source.height*scale)),Image.Resampling.LANCZOS)
            focus_x=source.width/2+(spec["focus"][0]-source.width/2)*q
            focus_y=source.height/2+(spec["focus"][1]-source.height/2)*q
            x=round(W/2-focus_x*scale);y=round(500-focus_y*scale)
            if q>=.65 and "focus_crop" in spec:
                # A literal button-row cut replaces the moving full-context crop.
                # This excludes sliced technical text and the old verification control.
                tile=source.crop(tuple(spec["focus_crop"]))
                scale=.86+.14*ease((t-16.62)/.38)
                tile=tile.resize((round(tile.width*scale),round(tile.height*scale)),Image.Resampling.LANCZOS)
                x=(W-tile.width)//2;y=500-tile.height//2
                dst.alpha_composite(tile,(x,y))
            else:
                window=Image.new("RGBA",(W,H))
                window.alpha_composite(tile,(x,y))
                dst.alpha_composite(window.crop((192,220,1728,770)),(192,220))
        else:
            dst.alpha_composite(tile,(x,y))
        if "detail_crop" in spec:
            detail=Image.open(ROOT/spec["path"]).convert("RGBA").crop(tuple(spec["detail_crop"]))
            detail_scale=min(1,1440/detail.width)
            detail=detail.resize((round(detail.width*detail_scale),round(detail.height*detail_scale)),Image.Resampling.LANCZOS)
            dst.alpha_composite(detail,((W-detail.width)//2,602))
        return {"kind":kind,"source":spec,"display_bbox":[x,y,x+tile.width,y+tile.height],"scale":scale,"source_dimensions":list(source.size)}

def material_punctuation(dst,scene,t):
    # Short actual-material strip punctuation; never the only presentation of a word.
    # It is independent of protected type, which is painted after it.
    phase=t%3.2
    if phase>.30 or 7.8<=t<8.2 or 13.0<=t<13.3:return
    for k in range(3):
        x=752+k*127+18*math.sin(t*7+k)
        yy=156+k*92
        cx=round(W*.69+k*82);cy=round(H*.28+k*83)
        crop=scene.crop((cx-92,cy-85,cx+92,cy+85))
        put(dst,crop,(x,yy),angle=(k-1)*9*(1-phase/.30))
        line(dst,[(x,yy+112),(x+120,yy+112)],CORAL,1)

def frame(t,scenes,cues,pixels,caption=True,with_records=False):
    records=[];ui=None
    actual=16.2<=t<19.6
    if t<16.2 or 19.6<=t<21:
        im=scenes.at(t)
        material_punctuation(im,im.copy(),t)
        context_brand(im,t)
        for read in READS:headline(im,read,t,records)
    elif actual:
        im=Image.new("RGBA",(W,H),CREAM)
        # Graphite edge crop retains the physical world around actual product pixels.
        rectangle(im,(0,0,1280,128),BLACK)
        kind="download" if t<17.82 else "offline"
        ui=pixels.panel(im,kind,t,records)
        context_brand(im,t,True)
    else:
        im=Image.new("RGBA",(W,H),CREAM)
        # One original mark. No 3D fragment can overlap this end card.
        put(im,LOGO,(640,195),.43,center=True)
        safe_text(im,"SUNSET",(640,335),109,BLACK,620,True,records,"brand",CREAM)
        safe_text(im,"Support once. Share forever.",(640,435),29,BLACK,500,True,records,"tagline",CREAM)
        safe_text(im,"sunset-lemon.vercel.app",(640,520),36,BLACK,550,True,records,"url",CREAM)
        rectangle(im,(500,80,780,120),BLACK)
        safe_text(im,"NEAR TESTNET",(640,100),24,CREAM,550,True,records,"network",BLACK)
        if t>=22.4:
            safe_text(im,"Music by Scott Buckley — CC BY 4.0",(640,603),20,BLACK,450,True,records,"music_credit",CREAM)
            safe_text(im,"www.scottbuckley.com.au",(640,630),20,BLACK,450,True,records,"music_credit",CREAM)
    if caption:captions(im,t,cues,records)
    for i,r in enumerate(records):
        fg=im.getpixel(tuple(r["probe_foreground_xy"]))[:3]
        bg=im.getpixel(tuple(r["probe_background_xy"]))[:3]
        if fg!=r["actual_pixel_foreground"] or bg!=r["actual_pixel_background"]:
            raise RuntimeError(f"Later layer occludes essential text at {t}: {r['text']}")
        for previous in records[:i]:
            a,b=r["bbox"],previous["bbox"]
            if max(a[0],b[0])<min(a[2],b[2]) and max(a[1],b[1])<min(a[3],b[3]):
                raise RuntimeError(f"Essential text bboxes overlap at {t}: {r['text']} / {previous['text']}")
    if with_records:return im.convert("RGB"),records,ui
    return im.convert("RGB")

def render_previews(scenes,cues,pixels,times=None):
    destination=OUT/"composite";destination.mkdir(parents=True,exist_ok=True)
    requested=times or [0,17/30,1.5,88/30,3.2,113/30,5.1,5.8,218/30,236/30,257/30,304/30,316/30,368/30,394/30,14.5,467/30,16.4,17.3,18.2,19.1,592/30,20.5,21,21.8,22.5,23.5]
    available=[]
    for t in requested:
        if ((t<16.2 or 19.6<=t<21) and round(t*30) not in scenes.indices):continue
        if 16.2<=t<19.6 and pixels.manifest is None:continue
        available.append(t)
    cols=4;rows=math.ceil(len(available)/cols)
    sheet=Image.new("RGB",(480*cols,298*rows),CREAM)
    phone=Image.new("RGB",(360*3,226*math.ceil(len(available)/3)),CREAM)
    metadata=[]
    for i,t in enumerate(available):
        image,recs,ui=frame(t,scenes,cues,pixels,True,True)
        n=round(t*FPS);image.save(destination/f"frame-{n:06d}.png")
        sheet.paste(image.resize((480,270),Image.Resampling.LANCZOS),((i%cols)*480,(i//cols)*298))
        ImageDraw.Draw(sheet).text(((i%cols)*480+8,(i//cols)*298+274),f"{t:.3f}s",fill=BLACK)
        phone.paste(image.resize((360,203),Image.Resampling.LANCZOS),((i%3)*360,(i//3)*226))
        ImageDraw.Draw(phone).text(((i%3)*360+7,(i//3)*226+207),f"{t:.3f}s",fill=BLACK)
        metadata.append({"time":t,"frame":n,"text":recs,"ui":ui})
    sheet.save(destination/"contact-sheet.jpg",quality=97)
    phone.save(destination/"phone-sheet.jpg",quality=97)
    (destination/"preview.json").write_text(json.dumps({"exact_source_only":True,"frames":metadata},indent=2)+"\n")
    print(json.dumps({"preview_frames":len(available),"missing_requested":len(requested)-len(available),"contact_sheet":str(destination/"contact-sheet.jpg")}),flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--render",action="store_true")
    parser.add_argument("--preview",action="store_true")
    parser.add_argument("--frames-dir",type=Path,default=OUT/"scene/frames")
    parser.add_argument("--ui-manifest",type=Path,default=OUT/"footage/manifest.json")
    parser.add_argument("--output",type=Path,default=OUT/"sunset-launch-v5.mp4")
    parser.add_argument("--times",help="Comma-separated exact preview times")
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    timing_path=OUT/"story-timing.json"
    timing=json.loads(timing_path.read_text())
    cues=timing["phrases"]
    scenes=Scenes(args.frames_dir,strict=args.render)
    if args.render:scenes.validate_manifest(OUT/"scene/manifest.json")
    pixels=ProductPixels(args.ui_manifest)
    render_previews(scenes,cues,pixels,[float(t) for t in args.times.split(",")] if args.times else None)
    if not args.render:return
    scene_manifest=OUT/"scene/manifest.json"
    if not scene_manifest.exists():raise RuntimeError("Native capture manifest required")
    audio=OUT/"audio/mix.wav"
    if hashlib.sha256(audio.read_bytes()).hexdigest()!=timing["mix_sha256"]:raise RuntimeError("Mastered audio changed after story clock")
    # RGB full-range source is converted once into BT.709 limited-range delivery.
    command=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pixel_format","rgb24","-video_size","1920x1080","-framerate","30","-i","-","-i",str(audio),"-map","0:v:0","-map","1:a:0","-vf","scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709","-c:v","libx264","-preset","medium","-crf","14","-g","60","-keyint_min","60","-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709","-color_range","tv","-threads","4","-c:a","aac","-b:a","320k","-ar","48000","-t","24","-movflags","+faststart",str(args.output)]
    process=subprocess.Popen(command,stdin=subprocess.PIPE)
    readability=[];uis={}
    try:
        for n in range(720):
            image,records,ui=frame(n/FPS,scenes,cues,pixels,True,True)
            process.stdin.write(image.tobytes())
            for r in records:
                if r["contrast"]<4.5:raise RuntimeError(f"Unsafe text contrast: {r}")
            readability.append({"frame":n,"time":n/FPS,"text":records})
            if ui:uis[ui["kind"]]=ui
            if n%120==119:print(f"Composited {n+1}/720 exact native frames",flush=True)
        process.stdin.close()
        if process.wait()!=0:raise RuntimeError("One-pass final encode failed")
    finally:
        if process.poll() is None:process.kill()
    target=OUT/"composite";target.mkdir(parents=True,exist_ok=True)
    color_metadata=json.loads(subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=color_space,color_transfer,color_primaries,color_range","-of","json",str(args.output)]))["streams"][0]
    expected_color={"color_range":"tv","color_space":"bt709","color_transfer":"bt709","color_primaries":"bt709"}
    if color_metadata!=expected_color:raise RuntimeError(f"Final delivery color properties missing: {color_metadata}")
    (target/"color-metadata.json").write_text(json.dumps(color_metadata,indent=2)+"\n")
    spec={"schema":1,"dimensions":[W,H],"fps":FPS,"safe_bbox":SAFE,"contrast_method":"Every essential text instance in all720 actual composed frames samples one fully opaque glyph pixel and its protected solid plane pixel. Contrast uses linear sRGB relative luminance of those actual RGB pixels. Text is drawn last; anti-aliased edge pixels are excluded.","contrast_ratio":contrast(BLACK,CREAM),"source_order":"CG/UI first, opaque type planes, essential glyphs, opaque caption plane, caption glyphs","essential_read_windows":READS,"all_frames":readability}
    (target/"readability-spec.json").write_text(json.dumps(spec,indent=2)+"\n")
    proof={"schema":1,"path":str(args.output.relative_to(ROOT)),"sha256":hashlib.sha256(args.output.read_bytes()).hexdigest(),"bytes":args.output.stat().st_size,"frames":720,"duration":24,"dimensions":[W,H],"fps":FPS,"video_encode_passes":1,"color_metadata":color_metadata,"crf":14,"source_cg_indices":CG_INDICES,"native_scene_manifest":str(scene_manifest.relative_to(ROOT)),"native_scene_manifest_sha256":hashlib.sha256(scene_manifest.read_bytes()).hexdigest(),"nearest_source_fallback":False,"actual_ui":uis,"audio_master_sha256":timing["mix_sha256"],"source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"readability_proof":str((target/"readability-spec.json").relative_to(ROOT))}
    (target/"composite-provenance.json").write_text(json.dumps(proof,indent=2)+"\n")
    print(json.dumps({k:proof[k] for k in ("path","sha256","bytes","frames","video_encode_passes")}),flush=True)

if __name__=="__main__":main()
