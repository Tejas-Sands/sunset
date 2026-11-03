#!/usr/bin/env python3
"""A frame-driven 9.6-second SUNSET motion proof. All UI pixels are genuine captures."""
import argparse, array, json, math, os, subprocess, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT=Path(__file__).resolve().parents[4]
V1=ROOT/'.publication/sunset-launch-v1'
OUT=ROOT/'.publication/sunset-launch-v2'
W,H,FPS=1280,720,30
CREAM=(247,245,237); GREEN=(37,62,49); ORANGE=(215,88,53)
FONT=V1/'render/Geist.ttf'
def clamp(v): return max(0,min(1,v))
def ease(v):
    v=clamp(v); return 1-(1-v)**3
def spring(v):
    if v<=0:return 0
    return 1-math.exp(-7*v)*(math.cos(11*v)+.25*math.sin(11*v))
def bitmap(text,size,color=GREEN,weight=650):
    f=ImageFont.truetype(str(FONT),size);f.set_variation_by_axes([weight])
    box=f.getbbox(text);im=Image.new('RGBA',(box[2]-box[0]+12,box[3]-box[1]+12))
    ImageDraw.Draw(im).text((6-box[0],6-box[1]),text,font=f,fill=(*color,255))
    return im
TEXT={key:bitmap(text,size,color,weight) for key,text,size,color,weight in [
('fund','FUND',224,GREEN,720),('it','IT',224,GREEN,720),('once','ONCE',233,CREAM,720),
('sunset','SUNSET',214,CREAM,640),('support','SUPPORT ONCE.',111,CREAM,660),
('share','SHARE FOREVER.',111,(244,178,140),660),('testnet','NEAR TESTNET',17,CREAM,600)]}
hero=Image.open(ROOT/'projects/sunset/public/images/sunset-commons-hero.webp').convert('RGBA')
game_a=Image.open(V1/'footage/06-hosted-verified-game.png').convert('RGBA').crop((620,405,1300,878))
game_b=Image.open(V1/'footage/07-hosted-game-feedback.png').convert('RGBA').crop((620,300,1300,985))
logo=Image.open(V1/'render/logo.png').convert('RGBA')
def put(dst,im,xy,scale=1,alpha=1,angle=0):
    if scale<=.01 or alpha<=0:return
    if scale!=1:im=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.BICUBIC)
    if alpha<1:
        im=im.copy();im.putalpha(im.getchannel('A').point(lambda x:round(x*clamp(alpha))))
    if angle:im=im.rotate(angle,Image.Resampling.BICUBIC,expand=True)
    dst.alpha_composite(im,(round(xy[0]),round(xy[1])))
def circle_reveal(dst,src,center,radius):
    mask=Image.new('L',(W,H));d=ImageDraw.Draw(mask);x,y=center
    d.ellipse((round(x-radius),round(y-radius),round(x+radius),round(y+radius)),fill=255)
    dst.paste(src,(0,0),mask)
def cursor(dst,x,y,press=0):
    d=ImageDraw.Draw(dst)
    if press>0:
        r=10+37*press;d.ellipse((x-r,y-r,x+r,y+r),outline=(215,88,53,round(220*(1-press))),width=4)
    p=[(x,y),(x+2,y+34),(x+12,y+26),(x+20,y+40),(x+28,y+36),(x+19,y+22),(x+33,y+20)]
    d.polygon(p,fill=(255,255,255,255),outline=(30,47,38,255),width=2)
def frame(t):
    canvas=Image.new('RGBA',(W,H),(*CREAM,255))
    d=ImageDraw.Draw(canvas)
    if t<1.12:
        a=spring(t/.52);b=spring((t-.32)/.44)
        put(canvas,TEXT['fund'],(185-100*ease((t-.32)/.5),225+420*(1-a)))
        put(canvas,TEXT['it'],(824+570*(1-b),225))
        d.ellipse((1120,474,1148,502),fill=ORANGE)
    elif t<2.30:
        q=ease((t-1.12)/.30);canvas.paste(ORANGE,(0,0,W,H))
        s=spring((t-1.12)/.54)
        put(canvas,TEXT['once'],((W-TEXT['once'].width)/2,238+330*(1-s)),1+.06*math.sin(clamp((t-1.12)/.6)*math.pi))
        d=ImageDraw.Draw(canvas)
        rad=24+980*ease((t-1.85)/.45)
        d.ellipse((1110-rad,482-rad,1110+rad,482+rad),fill=GREEN)
    elif t<3.82:
        canvas.paste(GREEN,(0,0,W,H));q=(t-2.30)/1.52
        bg=ImageOps.fit(hero,(W,H),method=Image.Resampling.BICUBIC)
        circle_reveal(canvas,bg,(1060-420*ease(q),360),1260*ease((t-2.30)/.85))
        overlay=Image.new('RGBA',(W,H),(37,62,49,round(155*ease((t-2.85)/.45))))
        canvas.alpha_composite(overlay)
        s=spring((t-2.55)/.55)
        word=TEXT['sunset']
        put(canvas,word,((W-word.width)/2,265+180*(1-s)),1,clamp((t-2.55)/.22))
        put(canvas,logo,(65,55),.26,clamp((t-2.6)/.2))
    elif t<7.10:
        q=ease((t-3.82)/.42)
        canvas.paste((223,231,215),(0,0,W,H))
        shift=-125*ease((t-5.65)/.75)
        scale=1.32+.035*(1-q)
        image=game_a if t<5.56 else game_b
        x=190-90*(1-q); y=45+500*(1-q)+shift
        put(canvas,image,(x,y),scale,1,0)
        # Actual answer button 12, mapped from the genuine pre-click screenshot.
        cx=190+(882-620)*scale;cy=45+(749-405)*scale
        progress=ease((t-4.45)/.77)
        px=1130+(cx-1130)*progress;py=650+(cy-650)*progress
        press=(t-5.52)/.32
        if t<5.82:cursor(canvas,px,py,press if 0<press<1 else 0)
        if t>6.50:
            band=Image.new('RGBA',(W,H),(*GREEN,255))
            circle_reveal(canvas,band,(640,520),1400*ease((t-6.70)/.40))
    else:
        canvas.paste(GREEN,(0,0,W,H))
        a=spring((t-7.1)/.50);b=spring((t-7.42)/.50)
        put(canvas,logo,(590,28),.40)
        put(canvas,TEXT['support'],((W-TEXT['support'].width)/2,285+250*(1-a)))
        put(canvas,TEXT['share'],((W-TEXT['share'].width)/2,415+250*(1-b)))
        # A small continuous orange sun stroke connects the reveal and the close.
        d=ImageDraw.Draw(canvas);width=880*ease((t-7.58)/.72)
        d.rounded_rectangle((200,583,200+width,588),radius=2,fill=ORANGE)
    if t>2.45:
        chip=Image.new('RGBA',(170,35),(*GREEN,245))
        chip.alpha_composite(TEXT['testnet'],(14,8));put(canvas,chip,(W-192,22))
    return canvas.convert('RGB')
def sound(duration):
    rate=24000;out=array.array('h')
    for n in range(round(rate*duration)):
        t=n/rate;beat=t%.5
        kick=math.sin(2*math.pi*(54*beat+55*(1-math.exp(-35*beat))/35))*math.exp(-beat*29)*.31
        hat=(math.sin(2*math.pi*6200*t)+.35*math.sin(2*math.pi*8761*t))*math.exp(-(t%.25)*100)*.027
        bass=math.sin(2*math.pi*[65.4064,82.4069,87.3071,73.4162][int(t/2)%4]*t)*(.035+.025*math.exp(-beat*9))
        whoosh=0
        for cut in [1.12,1.85,2.30,3.82,6.70,7.10]:
            dt=t-cut
            if -.11<dt<.17:
                env=math.exp(-((dt-.01)/.055)**2)
                whoosh+=(math.sin(2*math.pi*(1100+2600*dt)*t)+math.sin(2*math.pi*2100*t))*.033*env
        click=.18*math.sin(2*math.pi*2200*t)*math.exp(-(t-5.52)*95) if 5.52<=t<5.60 else 0
        env=min(1,t/.045,(duration-t)/.12)
        v=max(-.82,min(.82,(kick+hat+bass+whoosh+click)*max(0,env)))
        out.append(round(v*32767))
    path=OUT/'sound-design.wav'
    with wave.open(str(path),'wb') as f:f.setparams((1,2,rate,len(out),'NONE','not compressed'));f.writeframes(out.tobytes())
    return path
def main():
    p=argparse.ArgumentParser();p.add_argument('--duration',type=float,default=9.6);p.add_argument('--preview',action='store_true');a=p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    points=[.6,1.45,2.05,2.6,3.25,4.25,5.3,5.7,6.3,7.25,8.0,9.0]
    contact=Image.new('RGB',(W*3//2,H*4//2))
    for i,t in enumerate(points):
        im=frame(t);im.save(OUT/f'keyframe-{i:02}.png');contact.paste(im.resize((W//2,H//2)),((i%3)*W//2,(i//3)*H//2))
    contact.save(OUT/'motion-contact-sheet.jpg')
    frame(5.3).save(OUT/'app-action-preview.png')
    if a.preview:return
    silent=OUT/'motion-proof-silent.mp4'
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','4',str(silent)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for n in range(round(a.duration*FPS)):process.stdin.write(frame(n/FPS).tobytes())
        process.stdin.close();assert process.wait()==0
    finally:
        if process.poll() is None:process.kill()
    audio=sound(a.duration);target=OUT/'sunset-motion-proof.mp4'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(silent),'-i',str(audio),'-i',str(V1/'voice/sentence-02.wav'),'-i',str(V1/'voice/sentence-19.wav'),'-filter_complex','[1:a]volume=0.30[b];[2:a]adelay=2440|2440,apad[v1];[3:a]adelay=7160|7160,apad[v2];[b][v1][v2]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=8[a]','-map','0:v','-map','[a]','-t',str(a.duration),'-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(target)],check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(target)]))
    (OUT/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
    (OUT/'PROVENANCE.txt').write_text('9.6-second style proof, not the final launch film. Frame-driven independent type/image/mask/cursor layers. Game pixels are genuine verified browser captures from launch-v1 footage06/07. The cursor graphically reenacts the already captured answer12 action; no wallet or financial click is shown. Existing public SUNSET logo/hero/Geist, locally synthesized Kokoro sentence02+19 narration, and new original procedural120BPM sound design. No new package or paid service. No private wallet/release input. The original82-second film is preserved.\n')
    print(json.dumps({'video':str(target),'duration':probe['format']['duration'],'bytes':target.stat().st_size,'frames':round(a.duration*FPS)},indent=2))
if __name__=='__main__':main()
