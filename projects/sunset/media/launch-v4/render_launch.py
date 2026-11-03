#!/usr/bin/env python3
"""SUNSET v4: editorial typography and genuine UI over deterministic Three.js scenes."""
import argparse, functools, hashlib, json, math, subprocess, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[4]
SRC = Path(__file__).resolve().parent
OUT = ROOT / ".publication/sunset-launch-v4"
V1 = ROOT / ".publication/sunset-launch-v1"
W, H, FPS, DURATION = 1920, 1080, 30, 24
S = 1.5
CREAM = (244, 239, 229)
BLACK = (15, 17, 18)
CORAL = (239, 86, 53)
WHITE = (255, 251, 242)
MUTED = (113, 114, 104)
FONT = V1 / "render/Geist.ttf"
LOGO = Image.open(V1 / "render/logo.png").convert("RGBA")
# These are literal excerpts from the verified hosted/standalone browser captures.
GAME_A = Image.open(V1 / "footage/06-hosted-verified-game.png").convert("RGBA").crop((640, 540, 1280, 830))
GAME_B = Image.open(V1 / "footage/07-hosted-game-feedback.png").convert("RGBA").crop((640, 435, 1280, 900))
OFFLINE = Image.open(V1 / "footage/11-offline-game-complete.png").convert("RGBA").crop((604, 293, 1316, 638))
COVER = Image.open(V1 / "footage/06-hosted-verified-game.png").convert("RGBA").crop((765, 203, 1155, 399))

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

def corner_brand(dst, dark=False, actual=False):
    fg = WHITE if dark else BLACK
    # Original SUNSET mark is retained, not a substitute rebrand.
    put(dst, LOGO, (28, 25), .23)
    text(dst, "SUNSET", (78, 33), 20, fg, 650)
    rectangle(dst, (1080, 26, 1248, 58), BLACK, radius=6)
    dot(dst, 1096, 42, 3, CORAL)
    text(dst, "NEAR TESTNET", (1108, 33), 15, WHITE, 600)
    text(dst, "ACTUAL GAME" if actual else "MOTION VISUALIZATION", (30, 687), 14, fg, 450)

def captions(dst, t, cues):
    for cue in cues:
        if cue["start"] <= t < cue["end"]:
            rows = textwrap.wrap(cue["text"], 57)
            size = 32  # 48 physical pixels at 1080p.
            f = font(size, 500)
            widths = [f.getlength(row) / S for row in rows]
            height = 39*len(rows)+18
            top = 708-height
            width = min(1220, max(widths)+34)
            rectangle(dst, ((1280-width)/2, top, (1280+width)/2, 708), (13, 18, 16, 242), radius=6)
            for i, row in enumerate(rows):
                put(dst, word(row, size, WHITE, 500), ((1280-word(row, size, WHITE, 500).width/S)/2, top+7+i*39))

def pointer(dst, x, y, click=0, alpha=1):
    overlay = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(overlay)
    if 0 < click < 1:
        r = 12+34*click
        d.ellipse(tuple(px(v) for v in (x-r, y-r, x+r, y+r)), outline=(*CORAL, round(220*(1-click))), width=px(3))
    points = [(x,y),(x+1,y+31),(x+11,y+24),(x+19,y+37),(x+25,y+34),(x+17,y+20),(x+29,y+18)]
    d.polygon([(px(a),px(b)) for a,b in points], fill=(255,255,255,round(255*alpha)), outline=(*BLACK,round(255*alpha)), width=px(2))
    dst.alpha_composite(overlay)

class Scenes:
    def __init__(self, directory, strict=False):
        self.directory = Path(directory)
        self.files = sorted(self.directory.glob("[0-9][0-9][0-9][0-9][0-9][0-9].png"))
        self.indices = [int(p.stem) for p in self.files]
        self.strict = strict
        self.fallbacks = set()
        if strict:
            missing = [n for n in range(round(DURATION*FPS)) if not (self.directory/f"{n:06d}.png").exists()]
            if missing:
                raise RuntimeError(f"Complete Three.js sequence required; {len(missing)} frames missing")

    @functools.lru_cache(maxsize=3)
    def load(self, n):
        path = self.directory/f"{n:06d}.png"
        if not path.exists():
            if self.strict:
                raise RuntimeError(f"Missing source scene frame {n}")
            if not self.files:
                self.fallbacks.add("blank-design-preview")
                return Image.new("RGBA", (W,H), CREAM)
            nearest = min(self.indices, key=lambda i: abs(i-n))
            self.fallbacks.add((n,nearest))
            path = self.directory/f"{nearest:06d}.png"
        image = Image.open(path).convert("RGBA")
        if image.size != (W,H):
            image = image.resize((W,H), Image.Resampling.LANCZOS)
        return image

    def at(self, t):
        return self.load(max(0,min(round(DURATION*FPS)-1,round(t*FPS)))).copy()

def window_strip(dst, material, t, bg=CORAL, variant=False):
    dst.paste((*bg,255),(0,0,W,H))
    fg = WHITE if bg == BLACK else BLACK
    left = 188
    for i in range(5):
        x = left+i*181 + 12*math.sin(t*3.7+i)
        y = 235 + 54*math.sin(t*2.1+i*.62)
        ww,hh = 208,245+(i%3)*22
        cx = int(W*(.32+i*.085))
        cy = int(H*(.38+.055*math.sin(i+t)))
        crop = material.crop((cx-170,cy-195,cx+170,cy+195)).resize((px(ww),px(hh)),Image.Resampling.LANCZOS)
        if variant and i%2:
            crop = ImageOps.colorize(ImageOps.grayscale(crop), BLACK, CREAM).convert("RGBA")
        put(dst,crop,(x,y))
        guide(dst,(x,y,ww,hh),fg,["FUND","COMMIT","RELEASE","KEEP","MAINTAIN"][i])
        if i:
            x0,y0=left,480
            points=[]
            for k in range(25):
                u=k/24
                points.append((x0+(x-x0)*u,y0+(y+hh-y0)*u+math.sin(math.pi*u)*(75+i*13)))
            line(dst,points,fg,1)
    line(dst,[(left,110),(left,610)],fg)
    line(dst,[(left-110,235),(1190,235)],fg)
    line(dst,[(left-110,565),(1190,565)],fg)

def actual_panel(dst, source, t, start, width=760, center=(640,360)):
    enter=ease((t-start)/.48)
    scale=.72+.28*enter
    tile=source.resize((px(width),round(source.height*px(width)/source.width)),Image.Resampling.LANCZOS)
    put(dst,tile,(center[0]+210*(1-enter),center[1]+40*(1-enter)),scale=scale,angle=-5*(1-enter),center=True)

def frame(t, scenes, cues, caption=True):
    im = scenes.at(t)
    dark = False
    actual = False
    if t < 1.6:
        # Specimen dossier -> assembled type. The central material is real 3D.
        u=t
        line(im,[(162,100),(1118,100)],(155,146,131))
        line(im,[(162,585),(1118,585)],(155,146,131))
        line(im,[(235,60),(235,640)],(155,146,131))
        line(im,[(1045,60),(1045,640)],(155,146,131))
        for x,y in [(235,100),(1045,100),(235,585),(1045,585)]:
            cross(im,x,y)
        text(im,"RESOURCE / 001",(55,95),17,BLACK,450)
        text(im,"PUBLIC LEARNING, ON NEAR",(818,610),17,BLACK,500)
        glyphs(im,"SUNSET",640,265,202,u+.13,CREAM if u>.38 else BLACK,"scatter",tracking=-4)
        if u>.82:
            text(im,"FUND ONCE. KEEP A COPY.",(640,520),31,BLACK,500,center=True,alpha=ease((u-.82)/.3))
        if u>1.34:
            # Fast material crop prelap, not a white-flash strobe.
            width=1280*ease((u-1.34)/.26)
            rectangle(im,(1280-width,0,1280,720),CORAL)
            glyphs(im,"FUND",640,230,250,u-1.25,BLACK,"spread",tracking=-7)
    elif t < 4.8:
        u=t-1.6
        if u<.65:
            window_strip(im,scenes.at(t),t,CORAL)
            glyphs(im,"FUND",640,247,245,u+.30,BLACK,"spread",tracking=-5)
        elif u<1.55:
            dark=True
            # Upper and lower cropped type frame the sculptural escrow material.
            glyphs(im,"ON",220,40,176,u-.55,WHITE,"rise")
            glyphs(im,"CHAIN",810,495,175,u-.64,WHITE,"spread",tracking=-6)
            text(im,"0.10 testNEAR CAP",(52,457),29,WHITE,550)
        elif u<2.25:
            window_strip(im,scenes.at(t),t,CREAM,True)
            text(im,"CAPPED",(710,90),110,BLACK,600,center=True)
            text(im,"SPONSORSHIP",(640,575),72,BLACK,600,center=True)
        else:
            dark=True
            text(im,"0.10",(640,200),190,WHITE,550,center=True)
            text(im,"testNEAR CAP",(640,447),52,WHITE,550,center=True)
            text(im,"sunset.shiftultra.testnet",(640,550),22,WHITE,450,center=True)
    elif t < 8.8:
        u=t-4.8
        dark=True
        if u<.74:
            glyphs(im,"KEY",260,90,196,u+.15,WHITE,"scatter")
            text(im,"MATCH",(960,492),137,WHITE,550,center=True)
        elif u<1.60:
            text(im,"COMMITMENT / MATCHED",(42,120),23,WHITE,500)
            guide(im,(150,175,980,390),WHITE)
            for i in range(6):
                dot(im,185+i*182,600+13*math.sin(t*5+i),3,WHITE)
        elif u<2.34:
            # Oversized per-glyph public word makes the whole frame the transition.
            glyphs(im,"PUBLIC",640,255,212,u-1.40,WHITE,"spread",tracking=-5)
        elif u<3.15:
            text(im,"RELEASE",(640,100),174,WHITE,550,center=True)
            text(im,"CREATOR CREDIT",(640,550),36,WHITE,550,center=True)
        else:
            text(im,"OPEN TO EVERYONE",(50,127),50,WHITE,550)
            text(im,"CREATOR CREDIT",(50,550),32,WHITE,550)
            guide(im,(935,145,280,370),WHITE,"RELEASE / VERIFIED")
    elif t < 9.6:
        u=t-8.8
        window_strip(im,scenes.at(t),t,CORAL,True)
        if u>.27:
            pix=im.resize((48,27),Image.Resampling.BILINEAR).resize((W,H),Image.Resampling.NEAREST)
            im=Image.blend(im,pix,.65*smooth((u-.27)/.31))
        glyphs(im,"OPEN",640,245,242,u+.15,BLACK,"scatter",tracking=-6)
        if u>.60:
            # Cream shutter carries the eye into the literal application.
            y=720*(1-ease((u-.60)/.20))
            rectangle(im,(0,y,1280,720),CREAM)
    elif t < 12.6:
        u=t-9.6
        actual=True
        im.paste((*CREAM,255),(0,0,W,H))
        for x in [104,1176]:
            line(im,[(x,90),(x,640)],(205,197,180))
        text(im,"THE LANTERN TRAIL / REAL APP",(45,95),20,BLACK,500)
        source=GAME_A if u<1.25 else GAME_B
        actual_panel(im,source,t,9.6,width=760)
        if u<1.30:
            q=ease((u-.33)/.72)
            cx=1120+(547-1120)*q
            cy=596+(436-596)*q
            pointer(im,cx,cy,(u-1.10)/.20,alpha=1-ease((u-1.23)/.07))
        if u>1.35:
            text(im,"12",(1080,468),110,CORAL,600,center=True)
            text(im,"A LITTLE BRIGHTER",(1080,602),17,BLACK,500,center=True)
    elif t < 15.8:
        u=t-12.6
        dark=True
        if u<.70:
            glyphs(im,"OFFLINE",640,62,137,u+.20,WHITE,"spread",tracking=-4)
        else:
            text(im,"OFFLINE",(640,82),114,WHITE,600,center=True)
        # The source is actual cold-browser completion, floating among 3D public copies.
        if u>.30:
            actual_panel(im,OFFLINE,t,12.9,width=690,center=(640,390))
            text(im,"ACTUAL OFFLINE GAME",(640,570),18,WHITE,500,center=True,alpha=ease((u-.3)/.3))
    elif t < 19.6:
        u=t-15.8
        dark=True
        if u<.65:
            glyphs(im,"PASS",640,210,235,u+.1,WHITE,"scatter",tracking=-6)
        elif u<2.15:
            text(im,"MIRROR",(44,115),70,WHITE,550)
            text(im,"MAINTENANCE",(44,205),70,WHITE,550)
            text(im,"PUBLIC COPIES STAY OPEN",(60,582),20,WHITE,500)
        else:
            glyphs(im,"A TO B",640,485,152,u-1.94,WHITE,"spread",tracking=-5)
            text(im,"MIRROR MAINTENANCE",(640,95),30,WHITE,550,center=True)
    elif t < 21.6:
        u=t-19.6
        if u<.64:
            im.paste((*CORAL,255),(0,0,W,H))
            window_strip(im,scenes.at(t),t,CORAL,True)
            glyphs(im,"KEEP",640,220,255,u+.22,BLACK,"spread",tracking=-9)
        elif u<1.25:
            im.paste((*CREAM,255),(0,0,W,H))
            glyphs(im,"IT.",640,160,350,u-.46,BLACK,"scatter",tracking=-14)
        else:
            im.paste((*BLACK,255),(0,0,W,H))
            dark=True
            # Narrow macro windows replace the previous layout rather than decorate it.
            material=scenes.at(t)
            for i in range(3):
                yy=128+i*154
                crop=material.crop((0,round(H*.22+i*45),W,round(H*.22+i*45)+px(88)))
                put(im,crop,(0,yy))
            glyphs(im,"PUBLIC.",640,235,212,u-1.10,CORAL,"spread",tracking=-6)
    else:
        # Calm arrival. No drift or scale on the URL during the final2.4s.
        im.paste((*CREAM,255),(0,0,W,H))
        # Settle on the original mark without overlapping decorative geometry.
        put(im,LOGO,(640,207),.48,center=True)
        text(im,"SUNSET",(640,345),126,BLACK,600,center=True)
        text(im,"Support once. Share forever.",(640,475),33,BLACK,500,center=True)
        text(im,"sunset-lemon.vercel.app",(640,570),37,BLACK,550,center=True)
        line(im,[(220,628),(1060,628)],CORAL,2)
    corner_brand(im,dark,actual)
    if caption:
        captions(im,t,cues)
    return im.convert("RGB")

def render_previews(scenes,cues):
    destination=OUT/"composite"
    destination.mkdir(parents=True,exist_ok=True)
    times=[0,.46,.95,1.47,1.9,2.8,3.7,4.35,5.08,5.9,6.8,7.55,8.30,9.1,9.95,10.58,11.25,12.05,13.35,14.70,16.10,17.30,18.75,19.95,20.55,21.05,22.0,23.2]
    sheet=Image.new("RGB",(480*4,270*7),CREAM)
    for i,t in enumerate(times):
        image=frame(t,scenes,cues)
        image.save(destination/f"keyframe-{i:02}.png")
        sheet.paste(image.resize((480,270),Image.Resampling.LANCZOS),((i%4)*480,(i//4)*270))
    sheet.save(destination/"contact-sheet.jpg",quality=94)
    frame(.95,scenes,cues,False).save(OUT/"sunset-launch-v4-poster.png")
    data={"preview_times":times,"scene_frames_available":len(scenes.indices),"nearest_scene_fallbacks":[str(x) for x in sorted(scenes.fallbacks,key=str)],"note":"Preview may use nearest available3D scene frame; final --render requires exact720-frame sequence."}
    (destination/"preview.json").write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps({"contact_sheet":str(destination/"contact-sheet.jpg"),"scene_frames":len(scenes.indices),"fallback_count":len(scenes.fallbacks)}),flush=True)

def main():
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group()
    group.add_argument("--preview",action="store_true")
    group.add_argument("--render",action="store_true")
    parser.add_argument("--frames-dir",type=Path,default=OUT/"scene/frames")
    parser.add_argument("--start-frame",type=int,default=0)
    parser.add_argument("--end-frame",type=int,default=DURATION*FPS,help="Exclusive global timeline frame")
    parser.add_argument("--output",type=Path,help="Required for a partial-range encode")
    args=parser.parse_args()
    if not 0<=args.start_frame<args.end_frame<=DURATION*FPS:
        parser.error("Frame range must be inside0..720, with an exclusive end")
    partial=args.start_frame!=0 or args.end_frame!=DURATION*FPS
    if partial and args.output is None:
        parser.error("Partial encoding requires --output to preserve the full silent film")
    OUT.mkdir(parents=True,exist_ok=True)
    voice_path=OUT/"voice/timing.json"
    if not voice_path.exists():
        raise SystemExit("Audio agent's voice/timing.json is required")
    cues=json.loads(voice_path.read_text())["phrases"]
    scenes=Scenes(args.frames_dir,strict=args.render)
    scene_metadata=None
    if args.render:
        metadata_path=OUT/"scene/manifest.json"
        if not metadata_path.exists():
            raise RuntimeError("Completed scene/manifest.json is required before final composition")
        scene_metadata=json.loads(metadata_path.read_text())
        sequence=scene_metadata["sequence"]
        if sequence["frames"]!=720 or sequence["fps"]!=30 or sequence["format"]!="png":
            raise RuntimeError("Unexpected scene sequence; inspect manifest before encoding")
    if not partial:
        render_previews(scenes,cues)
    if not args.render:
        return
    path=args.output or OUT/"sunset-launch-v4-silent.mp4"
    path.parent.mkdir(parents=True,exist_ok=True)
    frame_count=args.end_frame-args.start_frame
    command=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pixel_format","rgb24","-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","-","-an","-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p","-threads","4",str(path)]
    process=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for completed,n in enumerate(range(args.start_frame,args.end_frame),1):
            process.stdin.write(frame(n/FPS,scenes,cues).tobytes())
            if completed%min(120,frame_count)==0 or completed==frame_count:
                print(f"Composited {completed}/{frame_count} frames (global {n})",flush=True)
        process.stdin.close()
        if process.wait()!=0:
            raise RuntimeError("FFmpeg compositor encode failed")
    finally:
        if process.poll() is None:
            process.kill()
    proof={"silent_movie":str(path),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"bytes":path.stat().st_size,"duration":frame_count/FPS,"fps":FPS,"frames":frame_count,"global_start_frame":args.start_frame,"global_end_frame_exclusive":args.end_frame,"dimensions":[W,H],"exact_scene_sequence_frames":True,"scene_capture_manifest":str(OUT/"scene/manifest.json"),"native_three_capture":scene_metadata["native"],"scene_interpolation":scene_metadata["interpolation"],"scene_sequence":scene_metadata["sequence"],"complete_scene_metadata":scene_metadata,"scene_first_frame_dimensions":list(Image.open(args.frames_dir/"000000.png").size),"compositor_source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"caption_source":str(voice_path),"actual_ui_sources":["06-hosted-verified-game.png","07-hosted-game-feedback.png","11-offline-game-complete.png"],"format":"Editorial composition of original3D objects, independent per-glyph typography, macro windows/pixel variants and genuine UI crops; no financial signing or new chain action."}
    proof_path=OUT/"composite"/(path.stem+"-provenance.json" if partial else "composite-provenance.json")
    proof_path.parent.mkdir(parents=True,exist_ok=True)
    proof_path.write_text(json.dumps(proof,indent=2)+"\n")
    print(json.dumps(proof,indent=2),flush=True)

if __name__=="__main__":
    main()
