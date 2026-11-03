#!/usr/bin/env python3
"""SUNSET v3: editorial protocol objects and genuine UI, without chain actions."""
import argparse,array,functools,hashlib,json,math,random,subprocess,textwrap,wave
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageOps
ROOT=Path(__file__).resolve().parents[4]
V1=ROOT/'.publication/sunset-launch-v1';V2=ROOT/'.publication/sunset-launch-v2'
OUT=ROOT/'.publication/sunset-launch-v3';SRC=Path(__file__).resolve().parent
S=1.5;W,H,FPS=1920,1080,30;DURATION=30.;BPM=128
BG=(6,15,13);FOREST=(21,53,41);INK=(11,28,22);WHITE=(242,242,228)
AMBER=(255,184,83);SUN=(215,88,53);MINT=(134,191,157);DIM=(88,126,104)
FONT=V1/'render/Geist.ttf'
def px(v):return round(v*S)
def clamp(v):return max(0.,min(1.,v))
def ease(v):v=clamp(v);return 1-(1-v)**3
def smooth(v):v=clamp(v);return v*v*(3-2*v)
def spring(v):
 if v<=0:return 0
 return 1-math.exp(-8*v)*(math.cos(11*v)+.20*math.sin(11*v))
def mix(c,k,b=BG):return tuple(round(b[i]+(c[i]-b[i])*clamp(k)) for i in range(3))
@functools.lru_cache(maxsize=80)
def font(size,weight=600):
 f=ImageFont.truetype(str(FONT),px(size));f.set_variation_by_axes([weight]);return f
@functools.lru_cache(maxsize=512)
def label(text,size,color=WHITE,weight=600):
 f=font(size,weight);b=f.getbbox(text);im=Image.new('RGBA',(b[2]-b[0]+px(4),b[3]-b[1]+px(4)))
 ImageDraw.Draw(im).text((px(2)-b[0],px(2)-b[1]),text,font=f,fill=(*color,255));return im
def put(dst,im,xy,scale=1,angle=0,alpha=1,center=False):
 if scale<=.01 or alpha<=0:return
 if abs(scale-1)>.001:im=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.BICUBIC)
 if angle:im=im.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 if alpha<1:im=im.copy();im.putalpha(im.getchannel('A').point(lambda x:round(x*clamp(alpha))))
 x,y=map(px,xy)
 if center:x-=im.width//2;y-=im.height//2
 dst.alpha_composite(im,(x,y))
def text(dst,txt,xy,size=30,color=WHITE,weight=600,alpha=1,center=False):
 put(dst,label(txt,size,color,weight),xy,alpha=alpha,center=center)
def line(dst,points,color=AMBER,width=2):
 ImageDraw.Draw(dst).line([(px(x),px(y)) for x,y in points],fill=color,width=max(1,px(width)),joint='curve')
def ring(dst,x,y,r,color=AMBER,width=2):
 ImageDraw.Draw(dst).ellipse(tuple(px(v) for v in (x-r,y-r,x+r,y+r)),outline=color,width=max(1,px(width)))
def dot(dst,x,y,r=4,color=AMBER):
 ImageDraw.Draw(dst).ellipse(tuple(px(v) for v in (x-r,y-r,x+r,y+r)),fill=color)
def rect(dst,box,fill=INK,outline=None,radius=12,width=1):
 ImageDraw.Draw(dst).rounded_rectangle(tuple(px(v) for v in box),radius=px(radius),fill=fill,outline=outline,width=max(1,px(width)))
def poly(dst,points,fill=None,outline=None,width=1):
 d=ImageDraw.Draw(dst);pts=[(px(x),px(y)) for x,y in points];d.polygon(pts,fill=fill)
 if outline:d.line(pts+[pts[0]],fill=outline,width=max(1,px(width)),joint='curve')
def along(a,b,u):return (a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u)
def packet(dst,a,b,u,color=AMBER):
 x,y=along(a,b,clamp(u));dot(dst,x,y,5,color);ring(dst,x,y,11,mix(color,.35),1)
def curve(a,b,n=32,bend=65):
 return [(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n+math.sin(math.pi*i/n)*bend) for i in range(n+1)]
def node(dst,x,y,title=None,active=False,r=21):
 ring(dst,x,y,r+6,mix(AMBER if active else MINT,.20),1)
 ring(dst,x,y,r,AMBER if active else mix(MINT,.5),2);dot(dst,x,y,5,AMBER if active else MINT)
 if title:text(dst,title,(x,y+r+25),16,MINT,500,center=True)
LOGO=Image.open(V1/'render/logo.png').convert('RGBA').resize((px(112),px(112)),Image.Resampling.LANCZOS)
COVER=Image.open(V1/'footage/06-hosted-verified-game.png').convert('RGBA').crop((765,203,1155,399))
COVER=ImageOps.fit(COVER,(px(230),px(126)),method=Image.Resampling.LANCZOS)
def image_crop(name,box,width):
 im=Image.open(V1/'footage'/name).convert('RGBA').crop(box)
 return im.resize((px(width),round(im.height*px(width)/im.width)),Image.Resampling.LANCZOS)
GAME_A=image_crop('06-hosted-verified-game.png',(620,405,1300,878),480)
GAME_B=image_crop('07-hosted-game-feedback.png',(620,405,1300,985),480)
OFFLINE=image_crop('11-offline-game-complete.png',(604,293,1316,638),500)
# Background geometry is cached. Foreground orbit phases continue between scenes.
BASE=Image.new('RGBA',(W,H),(*BG,255))
glow=Image.new('RGBA',(W,H));gd=ImageDraw.Draw(glow)
gd.ellipse((px(430),px(-100),px(1320),px(850)),fill=(25,68,42,145));gd.ellipse((px(790),px(30),px(1220),px(500)),fill=(127,72,22,35))
BASE.alpha_composite(glow.filter(ImageFilter.GaussianBlur(px(100))))
bd=ImageDraw.Draw(BASE)
for y in range(95,700,42):
 for x in range(30,1280,42):bd.ellipse((px(x),px(y),px(x+1),px(y+1)),fill=(35,56,43,255))
def backdrop(t):
 im=BASE.copy();d=ImageDraw.Draw(im)
 for i in range(8):
  x=((i*182+t*13)%1500)-120
  line(im,[(x,-20),(x-330,740)],(16,36,27),1)
 cx,cy=915,340
 for r in [176,225,278]:
  box=tuple(px(v) for v in (cx-r,cy-r*.58,cx+r,cy+r*.58));a=(t*11+r)%360
  d.arc(box,start=a,end=a+216,fill=(36,71,49),width=px(1))
 for i in range(13):
  a=i*math.tau/13+t*.075;r=225+22*math.sin(i*1.7)
  x=cx+math.cos(a)*r;y=cy+math.sin(a)*r*.58;dot(im,x,y,2,MINT if i%4==0 else (57,90,65))
 return im
def brand(dst,t,protocol=True):
 put(dst,LOGO,(42,28),.38);text(dst,'SUNSET',(101,40),25,WHITE,650)
 rect(dst,(1090,30,1238,62),INK,mix(MINT,.25),8)
 dot(dst,1104,46,3,AMBER);text(dst,'NEAR TESTNET',(1116,38),13,MINT,600)
 if protocol:text(dst,'PROTOCOL VISUALIZATION',(44,683),13,DIM,500)
def caps(dst,txt,xy,alpha=1):text(dst,txt,xy,17,AMBER,600,alpha=alpha)
def filecard(title='PUBLIC COPY'):
 im=Image.new('RGBA',(px(250),px(240)));rect(im,(0,0,250,240),(14,36,27),mix(AMBER,.65),17,2)
 put(im,COVER,(10,10),1);text(im,'.HTML',(19,154),40,WHITE,650);text(im,title,(20,209),13,MINT,550)
 return im
FILE=filecard();SMALL_FILE=filecard('CC0 CONTENT')
def credential():
 im=Image.new('RGBA',(px(270),px(225)));pts=[(24,0),(246,0),(270,30),(270,195),(246,225),(24,225),(0,195),(0,30)]
 poly(im,pts,(23,49,35),AMBER,2);put(im,LOGO,(22,20),.32);text(im,'MAINTENANCE',(24,88),26,WHITE,650)
 text(im,'LANTERN TRAIL',(24,131),16,MINT,550);line(im,[(24,168),(246,168)],mix(AMBER,.4),1)
 text(im,'MIRROR AUTHORITY',(24,188),13,AMBER,550);return im
TOKEN=credential()
def vault(dst,x,y,fill=0,opened=0):
 # Isometric capped escrow, an editorial object rather than fabricated app UI.
 poly(dst,[(x-110,y-78),(x-30,y-128),(x+150,y-128),(x+70,y-78)],(34,58,38),AMBER,2)
 poly(dst,[(x+70,y-78),(x+150,y-128),(x+150,y+60),(x+70,y+110)],(18,39,28),mix(AMBER,.65),2)
 rect(dst,(x-110,y-78,x+70,y+110),(11,30,22),AMBER,4,2)
 level=168*clamp(fill)
 if level>0:rect(dst,(x-100,y+99-level,x+60,y+99),mix(AMBER,.20),None,2)
 for j in range(5):
  yy=y+78-j*30;line(dst,[(x-100,yy),(x+60,yy)],mix(AMBER,.2),1)
 if opened<.05:text(dst,str(round(fill*100))+'%',(x-20,y+20),45,AMBER,650,center=True)
 if opened>0:
  shift=55*ease(opened)
  poly(dst,[(x-110,y-78-shift),(x-30,y-128-shift),(x+150,y-128-shift),(x+70,y-78-shift)],(31,55,37),AMBER,2)
  put(dst,COVER,(x-20,y-15),.7*ease(opened),center=True)
def public_mesh(dst,t,small=False):
 center=(875,355);points=[]
 for i in range(7):
  a=i*math.tau/7-.5+t*.08;r=225
  points.append((center[0]+math.cos(a)*r,center[1]+math.sin(a)*r*.67))
 for i,p in enumerate(points):
  q=points[(i+2)%len(points)];line(dst,[p,q],mix(MINT,.16),1)
  line(dst,[center,p],mix(MINT,.3),1)
  packet(dst,center,p,(t*.35+i*.13)%1,MINT)
 for i,p in enumerate(points):
  put(dst,SMALL_FILE,p,.31 if not small else .23,angle=math.sin(t*.9+i)*3,center=True)
 return points
def key(dst,x,y,k=1):
 ring(dst,x,y,30*k,AMBER,5);ring(dst,x,y,15*k,mix(AMBER,.45),2)
 line(dst,[(x+30*k,y),(x+153*k,y)],AMBER,6)
 line(dst,[(x+111*k,y),(x+111*k,y+26*k),(x+135*k,y+26*k),(x+135*k,y)],AMBER,5)
def pointer(dst,x,y,click=0):
 d=ImageDraw.Draw(dst);pts=[(x,y),(x+2,y+26),(x+10,y+20),(x+17,y+31),(x+23,y+28),(x+16,y+17),(x+27,y+16)]
 poly(dst,pts,WHITE,BG,2)
 if 0<click<1:ring(dst,x,y,13+click*30,mix(AMBER,1-click),3)
def caption(dst,t,cues):
 for cue in cues:
  if cue['start']<=t<cue['end']:
   rows=textwrap.wrap(cue['text'],66);ims=[label(row,23,WHITE,500) for row in rows]
   width=max(a.width for a in ims)/S+36;top=644-(len(rows)-1)*31
   rect(dst,((1280-width)/2,top-10,(1280+width)/2,top+len(rows)*31+4),(8,20,15),mix(MINT,.25),8)
   for i,im in enumerate(ims):put(dst,im,((1280-im.width/S)/2,top+i*31))
VOICE_RECIPE=[
 (1,.46875,1.12),
 (6,3.75,1.12),
 (8,7.5,1.12),
 (12,15.,1.12),
 (16,18.75,1.12),
 (19,23.4375,1.12),
 (20,26.71875,1.12),
]
def prepare_voice():
 source=json.loads((V1/'voice/timing.json').read_text());cues=[];(OUT/'voice').mkdir(parents=True,exist_ok=True)
 for index,start,tempo in VOICE_RECIPE:
  sent=source['sentences'][index-1];src=V1/'voice'/sent['audio_file'];target=OUT/'voice'/f'sentence-{index:02}.wav'
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(src),'-af',f'atempo={tempo},loudnorm=I=-18:TP=-2:LRA=7','-ar','24000','-ac','1',str(target)],check=True)
  with wave.open(str(target)) as f:duration=f.getnframes()/f.getframerate()
  cues.append({'source_sentence_index':index,'text':sent['text'],'source_file':str(src.relative_to(ROOT)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'rendered_file':str(target.relative_to(OUT)),'start':start,'end':start+duration,'duration':duration,'pitch_preserving_tempo':tempo})
 return cues
def frame(t,cues,with_caption=True):
 im=backdrop(t);scene=min(7,int(t/3.75));u=t-scene*3.75
 if scene==0:
  caps(im,'FUND LEARNING. RELEASE IT PUBLICLY.',(75,142))
  text(im,'FUNDED',(70,215+80*(1-spring((u+.1)/.5))),106,WHITE,700)
  text(im,'ONCHAIN.',(70+20*(1-ease((u-.15)/.45)),355),106,AMBER,700)
  ring(im,903,345,148,mix(AMBER,.35),2);ring(im,903,345,160,mix(MINT,.25),1)
  put(im,FILE,(903,340),.91+.025*math.sin(t*2),angle=-6+4*math.sin(t*.9),center=True)
  for i in range(5):
   a=i*math.tau/5+t*.36;x=903+math.cos(a)*242;y=345+math.sin(a)*184
   line(im,[(903,345),(x,y)],mix(MINT,.22),1);node(im,x,y,r=14)
   packet(im,(x,y),(903,345),(u*.32+i*.15)%1)
  text(im,'COMMUNITY / COMMONS',(78,546),24,MINT,500)
 elif scene==1:
  caps(im,'SPONSOR THE PUBLIC RELEASE',(75,143))
  text(im,'CAPPED',(70,205),98,WHITE,700);text(im,'ESCROW.',(70,320),98,AMBER,700)
  v=ease((u-.2)/2.65);vault(im,865,355,v)
  for i,(a,b) in enumerate([((150,520),(755,365)),((400,500),(755,435)),((1115,180),(1015,300))]):
   line(im,curve(a,b,bend=45 if i!=2 else -35),mix(MINT,.30),2);node(im,*a,r=17)
   for j in range(3):
    phase=(u*.70+j/3+i*.15)%1
    if v<.995:packet(im,a,b,phase)
  text(im,'TARGET',(1090,355),16,MINT,550)
  text(im,'100%',(1084,392),32,AMBER,650)
  line(im,[(1018,382),(1070,382)],AMBER,2)
  text(im,'RULES LIVE IN THE CONTRACT',(78,582),19,MINT,500)
  text(im,'0.10 testNEAR target',(870,535),24,AMBER,600,center=True)
  text(im,'sunset.shiftultra.testnet',(870,585),18,MINT,500,center=True)
 elif scene==2:
  fade=1-ease((u-2.60)/.25)
  caps(im,'COMMITTED KEY · ON-TIME RELEASE',(75,143),fade)
  text(im,'KEY MATCH.',(70,215),88,WHITE,700,alpha=fade)
  text(im,'PUBLIC RELEASE.',(72,324),55,AMBER,650,alpha=fade)
  match=ease((u-.35)/1.15);unlock=ease((u-1.4)/.65);vault(im,865,355,1,unlock)
  kx=170+400*match;ky=465-105*match;key(im,kx,ky,.72)
  for i in range(4):
   x=640+i*29;rect(im,(x,348,x+16,372),AMBER if u>i*.16+.5 else FOREST,None,3)
  if u>1.5:
   a=(970,465);b=(1100,530);line(im,curve(a,b,bend=25),AMBER,2)
   packet(im,a,b,(u-1.5)/.85);node(im,*b,active=True,r=19)
   text(im,'CREATOR CREDIT',(1045,577),17,AMBER,550,center=True)
  text(im,'CONTENT BECOMES RECOVERABLE',(77,565),19,MINT,500,alpha=fade)
 elif scene==3:
  fade=1-ease((u-.05)/.20)
  caps(im,'THE REAL PRODUCT',(75,143),fade)
  text(im,'JUST',(70,225),115,WHITE,700,alpha=fade);text(im,'PLAY.',(70,365),115,AMBER,700,alpha=fade)
  text(im,'No learner wallet.',(78,535),27,MINT,500,alpha=fade)
  enter=ease(u/.36);post=u>=1.7;asset=GAME_B if post else GAME_A
  x=690+170*(1-enter);y=150 if post else 160
  # Short genuine UI excerpts, separate from protocol illustrations.
  put(im,asset,(x,y),1,angle=0)

  if u<1.98:
   target=(x+262*(480/680),y+344*(480/680));q=ease((u-.35)/1.1)
   pointer(im,1185+(target[0]-1185)*q,580+(target[1]-580)*q,(u-1.62)/.28)

 elif scene==4:
  fade=1-ease((u-1.25)/.25)
  caps(im,'A COPY THAT OUTLIVES THE WEBSITE',(75,143),fade)
  text(im,'YOURS.',(70,225),109,WHITE,700,alpha=fade);text(im,'OFFLINE.',(70,356),99,AMBER,700,alpha=fade)
  pts=public_mesh(im,t)
  if u<1.5:
   put(im,FILE,(875,355),1.0+.04*math.sin(t*3),angle=-5+u*5,center=True)
  else:
   # Actual completed standalone-game state captured in a browser.
   put(im,OFFLINE,(875,355),.85+.06*ease((u-1.5)/1.5),center=True)
  text(im,'LOCAL HTML · CC0 CONTENT',(78,548),21,MINT,500,alpha=fade)
 elif scene==5:
  caps(im,'A TOKEN WITH A JOB',(75,140))
  text(im,'PASS ON',(70,215),85,WHITE,700);text(im,'THE CARE.',(70,320),85,AMBER,700)
  public_mesh(im,t,True)
  a=(690,520);b=(1100,520);mirror=(930,170);q=ease((u-.45)/2.3);holder=along(a,b,q)
  node(im,*a,'HOLDER A',active=q<.90,r=24);node(im,*b,'HOLDER B',active=q>=.90,r=24)
  line(im,[a,b],mix(AMBER,.35),2)
  # Only the mirror-authority edge follows the credential. Public edges are unchanged.
  line(im,[a,mirror],AMBER if q<.90 else mix(AMBER,.08),3)
  line(im,[b,mirror],AMBER if q>=.90 else mix(AMBER,.08),3)
  node(im,*mirror,'DISCOVERY MIRROR',active=True,r=19)
  text(im,'MIRROR AUTHORITY: A TO B',(900,105),23,AMBER,600,center=True)
  put(im,TOKEN,(holder[0],350),.63,angle=-8+16*q,center=True)
  line(im,[(holder[0],428),holder],mix(AMBER,.5),1);dot(im,*holder,5,AMBER)
  packet(im,a if q<.90 else b,mirror,(u*.5)%1)
  text(im,'PUBLIC COPIES STAY OPEN',(78,551),21,MINT,550)
  text(im,'MAINTENANCE NFT',(886,602),16,AMBER,550,center=True)
 elif scene==6:
  caps(im,'THE CONTENT STAYS PUBLIC',(75,143))
  text(im,'SUPPORT',(70,218),104,WHITE,700)
  text(im,'ONCE.',(70,345),109,AMBER,700)
  pts=public_mesh(im,t)
  put(im,LOGO,(875,355),1.12+.04*math.sin(u*2),center=True)
  for i,p in enumerate(pts):
   ring(im,*p,68+8*math.sin(t*1.6+i),mix(AMBER,.14),1)
  text(im,'SHARE FOREVER.',(78,553),35,MINT,600)
 else:
  # End address settles early; ring and packet movement keeps the close alive.
  q=ease(u/.45);put(im,LOGO,(640,172+45*(1-q)),1.03,center=True)
  text(im,'SUNSET',(640,330+45*(1-q)),125,WHITE,650,center=True)
  text(im,'Support once. Share forever.',(640,440),35,AMBER,550,center=True)
  text(im,'sunset-lemon.vercel.app',(640,542),42,WHITE,550,center=True)
  line(im,[(260,590),(1020,590)],mix(AMBER,.45),1)
  packet(im,(260,590),(1020,590),(u*.24)%1)
  ring(im,640,172,98+5*math.sin(u*2),mix(AMBER,.2),1)
 # Full-frame camera pushes follow the resource into release and then real UI.
 if scene in [2,3,4]:
  q=ease((u-2.85)/.90) if scene==2 else ease((u-.22)/.70) if scene==3 else ease((u-1.50)/.70)
  targetx=865 if scene in [2,3] else 875
  z=1+(2.1 if scene==2 else .55 if scene==3 else .65)*q
  cx=640+(targetx-640)*q;cy=360-5*q
  box=(px(cx-640/z),px(cy-360/z),px(cx+640/z),px(cy+360/z))
  im=im.crop(box).resize((W,H),Image.Resampling.BICUBIC)
 # A narrow luminous scanner signals cuts without whole-frame flashes.
 if 0<u<.18 and scene>0:
  x=-100+1480*ease(u/.18);line(im,[(x-15,90),(x+15,621)],mix(AMBER,.65),2)
 brand(im,t,protocol=scene not in [3,7])
 if with_caption:caption(im,t,cues)
 return im.convert('RGB')
def sound(cues):
 rate=24000;buf=array.array('h');rng=random.Random(47);beat=60/BPM
 events=[.46875,3.75,6.55,7.5,8.8,9.375,11.25,12.9,15,16.5,18.75,21.2,22.5,26.25]
 for n in range(round(rate*DURATION)):
  t=n/rate;b=t%beat;sub=t%(beat/2);bar=int(t/3.75)
  kick=math.sin(math.tau*(48*b+48*(1-math.exp(-35*b))/35))*math.exp(-b*32)*.27
  hat=(rng.random()*2-1)*math.exp(-sub*110)*.035
  base=[65.4064,65.4064,77.7817,87.3071][bar%4]
  bass=(math.sin(math.tau*base*t)+.18*math.sin(math.tau*base*2*t))*.045*math.exp(-b*3)
  arpf=[261.626,311.127,391.995,523.251][int(t/(beat/2))%4]
  arp=math.sin(math.tau*arpf*t)*math.exp(-sub*18)*.018
  fx=0
  for at in events:
   dt=t-at
   if -.07<dt<.12:fx+=(rng.random()*2-1)*.06*math.exp(-((dt-.005)/.04)**2)
  for at in [9.0,12.98,16.6,21.25,26.25]:
   dt=t-at
   if 0<=dt<.6:fx+=(math.sin(math.tau*659.255*t)+.4*math.sin(math.tau*987.767*t))*.065*math.exp(-dt*8)
  duck=.50 if any(c['start']-.07<=t<=c['end']+.1 for c in cues) else 1
  env=max(0,min(1,t/.04,(DURATION-t)/.22))
  v=(kick+hat+bass+arp+fx)*env*duck;buf.append(round(max(-.8,min(.8,v))*32767))
 target=OUT/'sound-design-128bpm.wav'
 with wave.open(str(target),'wb') as f:f.setparams((1,2,rate,len(buf),'NONE','not compressed'));f.writeframes(buf.tobytes())
 return target
def timestamp(v):
 ms=round(v*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--preview',action='store_true');ap.add_argument('--duration',type=float,default=30);a=ap.parse_args();assert 0<a.duration<=30
 OUT.mkdir(parents=True,exist_ok=True);cues=prepare_voice()
 assert all(c['end']<=30 for c in cues)
 for first,second in zip(cues,cues[1:]):assert first['end']<=second['start']
 edit={'duration':DURATION,'dimensions':[W,H],'fps':FPS,'bpm':BPM,'scope':'Editorial protocol visualization; genuine UI excerpts; no new wallet, chain or social action.','voice':cues,'shots':[{'start':i*3.75,'end':(i+1)*3.75,'name':name} for i,name in enumerate(['community resource','capped escrow','committed-key public release and creator credit','genuine game answer and feedback','actual offline copy and public mesh','maintenance authority handover','public copies remain open','SUNSET URL close'])]}
 (SRC/'edit.json').write_text(json.dumps(edit,indent=2)+'\n')
 srt='\n'.join(f'{i+1}\n{timestamp(c["start"])} --> {timestamp(c["end"])}\n{c["text"]}\n' for i,c in enumerate(cues))
 (OUT/'sunset-launch-v3.srt').write_text(srt)
 points=[0,.55,1.5,2.8,3.84,4.7,6.7,7.6,8.65,9.6,10.65,11.6,12.7,13.5,14.5,15.5,16.8,17.9,18.9,20.2,21.5,22.9,24.5,25.8,26.5,27.5,28.6,29.5]
 sheet=Image.new('RGB',(480*4,270*7),BG)
 for i,t in enumerate(points):
  im=frame(t,cues);im.save(OUT/f'keyframe-{i:02}.png');sheet.paste(im.resize((480,270)),((i%4)*480,(i//4)*270))
 sheet.save(OUT/'contact-sheet.jpg',quality=94)
 frame(1.5,cues,False).save(OUT/'sunset-launch-v3-poster.png')
 provenance={'format':edit['scope'],'voice':'Seven whole previously generated Kokoro af_heart sentences, pitch-preserving atempo 1.12; no new synthesis or cloning.','sound':'Original deterministic 128 BPM procedural music, noise hats, bass, arp, whoosh and chime accents.','illustrations':'Escrow, key, credential, file tiles, copy mesh and holder nodes are editorial illustrations labeled PROTOCOL VISUALIZATION. They are not signing screens or new transactions.','ui':'Genuine verified hosted answer12/feedback captures and actual cold-offline completion from retained v1 footage; pointer is graphical reenactment of the already observed answer action.','claim_limits':'Maintenance NFT controls discovery-mirror authority; content remains public. Key match credits creator, separate withdrawal is required. No price, investment, exclusive content ownership, automatic payout or decentralized-hosting guarantee.','source_files':[str(p.relative_to(ROOT)) for p in [Path(__file__).resolve(),V1/'render/logo.png',FONT,V1/'footage/06-hosted-verified-game.png',V1/'footage/07-hosted-game-feedback.png',V1/'footage/11-offline-game-complete.png']]}
 (OUT/'media-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
 if a.preview:print(json.dumps({'preview':str(OUT/'contact-sheet.jpg'),'voiceCues':len(cues)}));return
 silent=OUT/'sunset-launch-v3-silent.mp4'
 p=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','4',str(silent)],stdin=subprocess.PIPE)
 try:
  for n in range(round(a.duration*FPS)):
   p.stdin.write(frame(n/FPS,cues).tobytes())
   if n%150==0:print(f'rendered {n}/{round(a.duration*FPS)}',flush=True)
  p.stdin.close();assert p.wait()==0
 finally:
  if p.poll() is None:p.kill()
 music=sound(cues);target=OUT/'sunset-launch-v3.mp4';cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(silent),'-i',str(music)]
 for c in cues:cmd+=['-i',str(OUT/c['rendered_file'])]
 filters=['[1:a]volume=.40[bed]']
 for i,c in enumerate(cues):filters.append(f'[{i+2}:a]adelay={round(c["start"]*1000)}|{round(c["start"]*1000)},apad[v{i}]')
 filters.append('[bed]'+''.join(f'[v{i}]' for i in range(len(cues)))+f'amix=inputs={len(cues)+1}:duration=longest:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=8[a]')
 cmd+=['-filter_complex',';'.join(filters),'-map','0:v','-map','[a]','-t',str(a.duration),'-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-metadata','title=SUNSET — Public by design','-metadata','comment=NEAR testnet; editorial protocol visualization and genuine UI; synthetic voice.',str(target)]
 subprocess.run(cmd,check=True);print(json.dumps({'video':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}),flush=True)
if __name__=='__main__':main()
