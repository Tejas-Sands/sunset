#!/usr/bin/env python3
"""Native layer animation for SUNSET's 30-second, 128 BPM app-launch film.
No product, chain, wallet or social actions. Output stays in ignored launch-v2.
"""
import argparse,array,hashlib,json,math,subprocess,textwrap,wave
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps

ROOT=Path(__file__).resolve().parents[4]
V1=ROOT/'.publication/sunset-launch-v1'
OUT=ROOT/'.publication/sunset-launch-v2'
S=1.5;W,H,FPS=1920,1080,30;DURATION=30.0
C=(247,245,237);G=(37,62,49);O=(215,88,53);PEACH=(244,178,140)
FONT=V1/'render/Geist.ttf'
def p(n):return round(n*S)
def clamp(v):return max(0,min(1,v))
def ease(v):
 v=clamp(v);return 1-(1-v)**3
def spring(v):
 if v<=0:return 0
 return 1-math.exp(-7*v)*(math.cos(11*v)+.25*math.sin(11*v))
def font(size,weight=650):
 f=ImageFont.truetype(str(FONT),p(size));f.set_variation_by_axes([weight]);return f
def word(text,size,color=G,weight=650):
 f=font(size,weight);b=f.getbbox(text);im=Image.new('RGBA',(b[2]-b[0]+p(10),b[3]-b[1]+p(10)))
 ImageDraw.Draw(im).text((p(5)-b[0],p(5)-b[1]),text,font=f,fill=(*color,255));return im
T={}
for key,text,size,color,weight in [
 ('fund','FUND',224,G,720),('it','IT',224,G,720),('once','ONCE',233,C,720),
 ('meaning','Learning, worth sharing.',48,G,520),('meaningw','Learning, worth sharing.',48,C,520),
 ('sunset','SUNSET',212,C,640),('sunsetg','SUNSET',168,G,650),
 ('support','SUPPORT',168,G,680),('finished','A FINISHED',127,G,620),('resource','RESOURCE.',156,G,680),
 ('creator','CREATORS',154,C,650),('reward','REWARDED.',154,PEACH,650),
 ('download','DOWNLOAD',161,G,680),('offline','OFFLINE.',165,C,680),
 ('forlearners','FOR LEARNERS',63,PEACH,560),('noaccount','NO ACCOUNT.',155,C,670),('nowallet','NO WALLET.',155,C,670),
 ('keep','KEEP',227,G,680),('share','SHARE',223,C,680),('forever','FOREVER.',156,C,680),
 ('url','sunset-lemon.vercel.app',56,G,570),('tag','Support once. Share forever.',43,G,520),
 ('testnet','NEAR TESTNET',17,C,600)]:
 T[key]=word(text,size,color,weight)
def center(dst,key,y,offset=0,scale=1,alpha=1,angle=0):
 im=T[key];put(dst,im,((1280-im.width/S*scale)/2+offset,y),scale,alpha,angle)
def put(dst,im,xy,scale=1,alpha=1,angle=0):
 if scale<=.001 or alpha<=0:return
 if abs(scale-1)>.0001:im=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.BICUBIC)
 if alpha<1:
  im=im.copy();im.putalpha(im.getchannel('A').point(lambda n:round(n*clamp(alpha))))
 if angle:im=im.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 dst.alpha_composite(im,(p(xy[0]),p(xy[1])))
def shape(dst,kind,box,fill,width=1,radius=0):
 d=ImageDraw.Draw(dst);box=tuple(p(x) for x in box)
 if kind=='ellipse':d.ellipse(box,fill=fill)
 elif kind=='line':d.line(box,fill=fill,width=p(width))
 else:d.rounded_rectangle(box,radius=p(radius),fill=fill)
def reveal(dst,src,center,radius):
 mask=Image.new('L',(W,H));x,y=center;r=radius;ImageDraw.Draw(mask).ellipse(tuple(p(v) for v in (x-r,y-r,x+r,y+r)),fill=255);dst.paste(src,(0,0),mask)
def crop(name,box):return Image.open(V1/'footage'/name).convert('RGBA').crop(box)
HERO=ImageOps.fit(Image.open(ROOT/'projects/sunset/public/images/sunset-commons-hero.webp').convert('RGBA'),(W,H),method=Image.Resampling.LANCZOS)
A=crop('06-hosted-verified-game.png',(620,405,1300,878))
B=crop('07-hosted-game-feedback.png',(620,300,1300,985))
DOWN=crop('05-hosted-pack-verified.png',(436,1000,1090,1080))
OFF=crop('10-offline-game-answer.png',(604,293,1316,778))
DONE=crop('11-offline-game-complete.png',(604,293,1316,638))
COVER=crop('06-hosted-verified-game.png',(765,203,1155,399))
LOGO=Image.open(V1/'render/logo.png').convert('RGBA')
def scaled(im,k):return im.resize((p(im.width*k),p(im.height*k)),Image.Resampling.LANCZOS)
# Fixed source resampling is cached; each frame animates independent layer transforms.
A=scaled(A,1.2);B=scaled(B,1.2);DOWN=scaled(DOWN,1000/654)
OFF=scaled(OFF,1.32);DONE=scaled(DONE,1.32);COVER=scaled(COVER,1.55)
VOICE=json.loads((OUT/'voice/timing.json').read_text())
STARTS=[2.34375,7.5,11.25,18.75,23.4375,26.71875]
def cursor(dst,x,y,click=0,alpha=1):
 layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
 if 0<click<1:
  r=10+34*click;d.ellipse(tuple(p(v) for v in (x-r,y-r,x+r,y+r)),outline=(*O,round(230*(1-click))),width=p(3))
 points=[(x,y),(x+2,y+31),(x+11,y+24),(x+19,y+37),(x+25,y+34),(x+17,y+20),(x+29,y+18)]
 d.polygon([(p(a),p(b)) for a,b in points],fill=(255,255,255,round(255*alpha)),outline=(25,43,33,round(255*alpha)),width=p(2))
 dst.alpha_composite(layer)
def file_tile():
 im=Image.new('RGBA',(p(325),p(335)));d=ImageDraw.Draw(im)
 d.rounded_rectangle((0,0,p(325),p(335)),radius=p(22),fill=(255,253,247,255))
 d.polygon([(p(250),0),(p(325),p(75)),(p(250),p(75))],fill=(*O,255))
 d.text((p(27),p(98)),'.HTML',font=font(72,650),fill=(*G,255))
 d.text((p(28),p(216)),'The Lantern Trail',font=font(26,550),fill=(*G,255))
 d.text((p(28),p(265)),'YOUR OFFLINE COPY',font=font(15,500),fill=(*G,255));return im
FILE=file_tile()
def poster():
 im=Image.new('RGBA',(W,H),(*C,255));put(im,LOGO,(70,48),.38);put(im,word('SUNSET',38,G,650),(178,68))
 center(im,'fund',210);learning=word('LEARNING.',169,G,650);put(im,learning,((1280-learning.width/S)/2,418))
 meaning=T['meaning'];put(im,meaning,((1280-meaning.width/S)/2,625))
 return im.convert('RGB')
def captions(dst,t):
 for start,phrase in zip(STARTS,VOICE['phrases']):
  if start<=t<start+phrase['duration']:
   rows=textwrap.wrap(phrase['text'],64)
   f=font(23,470);d=ImageDraw.Draw(dst);height=len(rows)*32+16;y=704-height
   widths=[d.textbbox((0,0),line,font=f)[2]/S for line in rows];wid=max(widths)+28
   overlay=Image.new('RGBA',(W,H));od=ImageDraw.Draw(overlay)
   od.rounded_rectangle(tuple(p(v) for v in ((1280-wid)/2,y,(1280+wid)/2,710)),radius=p(9),fill=(23,44,31,220));dst.alpha_composite(overlay)
   d=ImageDraw.Draw(dst)
   for i,line in enumerate(rows):d.text((p((1280-widths[i])/2),p(y+5+i*32)),line,font=f,fill=(*C,255))
def frame(t,caption=True):
 if t==0:return poster()
 im=Image.new('RGBA',(W,H),(*C,255))
 if t<1.125:
  a=spring((t+.14)/.57);b=spring((t-.20)/.42)
  put(im,T['fund'],(185-100*ease((t-.2)/.5),207+390*(1-a)))
  put(im,T['it'],(824+570*(1-b),207))
  center(im,'meaning',555+40*(1-ease(t/.35)))
  shape(im,'ellipse',(1120,448,1148,476),O)
 elif t<1.875:
  im.paste(O,(0,0,W,H));v=spring((t-1.125)/.4)
  center(im,'once',220+260*(1-v))
  center(im,'meaningw',555)
  r=22+1460*ease((t-1.55)/.325);shape(im,'ellipse',(1110-r,456-r,1110+r,456+r),G)
 elif t<3.75:
  im.paste(G,(0,0,W,H));q=(t-1.875)/1.875
  reveal(im,HERO,(1060-420*ease(q),360),1450*ease((t-1.875)/.9))
  overlay=Image.new('RGBA',(W,H),(*G,round(145*ease((t-2.35)/.38))));im.alpha_composite(overlay)
  center(im,'sunset',250+150*(1-spring((t-2.20)/.5)),alpha=clamp((t-2.20)/.16))
  put(im,LOGO,(60,45),.26,clamp((t-2.3)/.2))
 elif t<7.5:
  dt=t-3.75;im.paste((223,231,215),(0,0,W,H));enter=ease(dt/.35)
  z=1+.45*ease((dt-.62)/.87);targetx=232+262*1.2;targety=70+344*1.2
  tx=(640-z*targetx)*ease((dt-.62)/.87);ty=(420-z*targety)*ease((dt-.62)/.87)
  ty-=218*ease((dt-2.00)/.65)
  src=A if dt<1.84 else B
  put(im,src,(232*z+tx+450*(1-enter),70*z+ty),z)
  progress=ease((dt-.65)/1.08);cx=targetx*z+tx;cy=targety*z+ty
  if dt<2.1:cursor(im,1130+(cx-1130)*progress,650+(cy-650)*progress,(dt-1.80)/.30,1-ease((dt-1.93)/.17))
  if dt>3.35:reveal(im,Image.new('RGBA',(W,H),(*C,255)),(640,445),1450*ease((dt-3.35)/.40))
 elif t<11.25:
  dt=t-7.5
  if dt<1.875:
   center(im,'support',115+220*(1-spring(dt/.43)))
   center(im,'finished',330+210*(1-spring((dt-.26)/.43)))
   center(im,'resource',485+210*(1-spring((dt-.53)/.43)))
  else:
   im.paste(G,(0,0,W,H));a=spring((dt-1.875)/.43);b=spring((dt-2.20)/.43)
   center(im,'creator',225+270*(1-a));center(im,'reward',422+270*(1-b))
   shape(im,'line',(120,630,120+1040*ease((dt-2.40)/.50),630),O,5)
 elif t<15:
  dt=t-11.25
  if dt<1.75:
   center(im,'download',145+170*(1-spring(dt/.45)))
   put(im,DOWN,(140+500*(1-ease(dt/.38)),352))
   cx,cy=140+(776-436)*(1000/654),352+(1040-1000)*(1000/654)
   v=ease((dt-.28)/.90)
   cursor(im,1130+(cx-1130)*v,610+(cy-610)*v,(dt-1.21)/.32,1-ease((dt-1.5)/.20))
  else:
   im.paste(G,(0,0,W,H));q=spring((dt-1.75)/.43)
   put(im,FILE,(480+530*(1-q),145),1,-1 if q<0 else 1,angle=-6+7*ease((dt-2.0)/.7))
   center(im,'offline',500,alpha=clamp((dt-2.15)/.2))
   # Explicitly illustrated offline file, not a counterfeit browser/download dialog.
   if dt>3.35:reveal(im,Image.new('RGBA',(W,H),(223,231,215,255)),(640,360),1450*ease((dt-3.35)/.40))
 elif t<18.75:
  dt=t-15;im.paste((223,231,215),(0,0,W,H))
  if dt<2.10:
   z=1+.13*ease(dt/1.8)
   put(im,OFF,(170-(z-1)*470,35-(z-1)*320),z)
  else:
   z=1+.045*ease((dt-2.10)/1.4)
   put(im,DONE,(170-(z-1)*470,95-(z-1)*210),z)
  if dt>3.30:reveal(im,Image.new('RGBA',(W,H),(*G,255)),(640,330),1450*ease((dt-3.30)/.45))
 elif t<22.5:
  dt=t-18.75;im.paste(G,(0,0,W,H))
  center(im,'forlearners',105+70*(1-spring(dt/.4)))
  center(im,'noaccount',260+280*(1-spring((dt-.25)/.44)))
  center(im,'nowallet',456+280*(1-spring((dt-.75)/.44)))
  # The dot keeps moving while the words remain easy to read.
  x=160+960*ease((dt-1.3)/2.2);shape(im,'ellipse',(x,635,x+16,651),O)
 elif t<26.25:
  dt=t-22.5
  if dt<1.95:
   center(im,'keep',80+180*(1-spring(dt/.42)))
   for i,(x,y,a) in enumerate([(255,340,-8),(390,330,1),(530,345,8)]):
    q=spring((dt-i*.12)/.55);put(im,COVER,(x+850*(1-q),y),.84,1,angle=a*(1-ease((dt-.9)/.7)))
  else:
   im.paste(O,(0,0,W,H));center(im,'share',180+180*(1-spring((dt-1.95)/.38)))
   center(im,'forever',435+180*(1-spring((dt-2.24)/.38)))
 elif t<=30:
  dt=t-26.25
  put(im,LOGO,(585,28+3*math.sin(dt*2)),.43)
  center(im,'sunsetg',190+160*(1-spring(dt/.42)))
  center(im,'tag',390+65*(1-ease((dt-.23)/.45)))
  center(im,'url',505+100*(1-spring((dt-.38)/.44)))
  width=960*ease((dt-.7)/.6);shape(im,'line',(160,610,160+width,610),O,4)
  # Only the sun stroke continues; the address is stable for the final2.8 seconds.
  x=640+460*math.sin(dt*.75);shape(im,'ellipse',(x-6,604,x+6,616),O)
 if t>1.875:
  chip=Image.new('RGBA',(p(170),p(35)),(*G,240));chip.alpha_composite(T['testnet'],(p(13),p(8)));put(im,chip,(1088,20))
 if caption:captions(im,t)
 return im.convert('RGB')
def sound():
 rate=24000;beat_duration=60/128;buf=array.array('h')
 cuts=[1.125,1.55,1.875,3.75,7.5,9.375,11.25,13.0,15,17.10,18.75,22.5,24.45,26.25]
 for n in range(round(rate*DURATION)):
  t=n/rate;b=t%beat_duration
  kick=math.sin(2*math.pi*(52*b+50*(1-math.exp(-35*b))/35))*math.exp(-b*30)*.28
  hat=(math.sin(2*math.pi*6200*t)+.32*math.sin(2*math.pi*8761*t))*math.exp(-(t%(beat_duration/2))*115)*.022
  bass=math.sin(2*math.pi*[65.4064,82.4069,87.3071,73.4162][int(t/3.75)%4]*t)*(.034+.025*math.exp(-b*10))
  fx=0
  for cut in cuts:
   dt=t-cut
   if -.10<dt<.13:fx+=(math.sin(2*math.pi*(1300+2800*dt)*t)+math.sin(2*math.pi*2100*t))*.025*math.exp(-((dt-.005)/.05)**2)
  for tap in [5.55,12.46]:
   dt=t-tap
   if 0<=dt<.1:fx+=.16*math.sin(2*math.pi*2100*t)*math.exp(-dt*95)
  for at in [5.68,17.1,26.55]:
   dt=t-at
   if 0<=dt<.40:fx+=(math.sin(2*math.pi*659.255*t)+.5*math.sin(2*math.pi*987.767*t))*.055*math.exp(-dt*10)
  env=min(1,t/.025,(DURATION-t)/.22)
  value=max(-.8,min(.8,(kick+hat+bass+fx)*max(0,env)));buf.append(round(value*32767))
 path=OUT/'sound-design-128bpm.wav'
 with wave.open(str(path),'wb') as f:f.setparams((1,2,rate,len(buf),'NONE','not compressed'));f.writeframes(buf.tobytes())
 return path
def timestamp(v):
 ms=round(v*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
def main():
 p1=argparse.ArgumentParser();p1.add_argument('--preview',action='store_true');p1.add_argument('--duration',type=float,default=30);a=p1.parse_args();assert 0<a.duration<=30
 OUT.mkdir(parents=True,exist_ok=True)
 points=[0,.6,1.35,2.35,3.1,4.4,5.42,6.4,7.9,9.9,11.8,12.5,13.9,15.8,17.8,19.5,20.5,22.9,24.9,26.6,27.6,29.2]
 sheet=Image.new('RGB',(480*4,270*6),C)
 for i,t in enumerate(points):
  im=frame(t);im.save(OUT/f'full-keyframe-{i:02}.png');sheet.paste(im.resize((480,270)),((i%4)*480,(i//4)*270))
 sheet.save(OUT/'full-motion-contact-sheet.jpg');poster().save(OUT/'sunset-launch-v2-poster.png')
 cues=[]
 for i,(start,phrase) in enumerate(zip(STARTS,VOICE['phrases'])):cues.append(f'{i+1}\n{timestamp(start)} --> {timestamp(start+phrase["duration"])}\n'+ '\n'.join(textwrap.wrap(phrase['text'],64))+'\n')
 (OUT/'sunset-launch-v2.srt').write_text('\n'.join(cues))
 if a.preview:return
 silent=OUT/'sunset-launch-v2-silent.mp4'
 process=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','4',str(silent)],stdin=subprocess.PIPE)
 try:
  for n in range(round(a.duration*FPS)):process.stdin.write(frame(n/FPS).tobytes())
  process.stdin.close();assert process.wait()==0
 finally:
  if process.poll() is None:process.kill()
 music=sound();target=OUT/'sunset-launch-v2.mp4';cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(silent),'-i',str(music)]
 for phrase in VOICE['phrases']:cmd+=['-i',str(OUT/'voice'/phrase['audio_file'])]
 filters=['[1:a]volume=0.31[bed]']
 for i,start in enumerate(STARTS):filters.append(f'[{i+2}:a]adelay={round(start*1000)}|{round(start*1000)},apad[v{i}]')
 filters.append('[bed]'+''.join(f'[v{i}]' for i in range(6))+'amix=inputs=7:duration=longest:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=8[a]')
 cmd+=['-filter_complex',';'.join(filters),'-map','0:v','-map','[a]','-t',str(a.duration),'-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-metadata','title=SUNSET — Learning, worth sharing.','-metadata','comment=Native frame-based motion design; genuine UI excerpts; edited existing synthetic voice; NEAR testnet.',str(target)]
 subprocess.run(cmd,check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(target)]));(OUT/'full-ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
 print(json.dumps({'video':str(target),'seconds':probe['format']['duration'],'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()},indent=2))
if __name__=='__main__':main()
