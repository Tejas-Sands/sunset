#!/usr/bin/env python3
"""SUNSET v6: original warm kinetic flat-2D film. No CG or product mutations."""
import argparse, functools, hashlib, json, math, subprocess, io, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg
ROOT=Path(__file__).resolve().parents[4]
SRC=Path(__file__).resolve().parent
OUT=ROOT/'.publication/sunset-launch-v6'
V5=ROOT/'.publication/sunset-launch-v5'
V1=ROOT/'.publication/sunset-launch-v1'
W,H,FPS=1920,1080,30
CREAM=(255,243,221);INK=(32,59,54);CORAL=(228,91,53);BLUE=(36,77,221);MINT=(203,229,213);BUTTER=(242,210,103);PEACH=(255,190,151)
SAFE=(192,108,1728,972)
DISPLAY=OUT/'fonts/BricolageGrotesque-VF.ttf';BODY=OUT/'fonts/SpaceGrotesk-VF.ttf'
LOGO=Image.open(V1/'render/logo.png').convert('RGBA')
PROVISIONAL=[('Good learning deserves to stick around.',.20,3.08),('With SUNSET, communities fund public learning packs through NEAR escrow.',3.23,7.73),('Release the key on time, and creators can claim their payout.',7.88,12.85),('Miss the deadline?',13.0,14.1),('Sponsors can claim refunds.',14.25,16.05),('Download a copy.',16.20,17.74),('Keep it offline.',17.89,19.49),('Support once.',19.64,20.92),('Share forever.',21.07,22.33)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clamp(x):return max(0.,min(1.,x))
def ease(x):return 1-(1-clamp(x))**3
def smooth(x):x=clamp(x);return x*x*(3-2*x)
def spring(x):return 0 if x<=0 else 1-math.exp(-8*x)*(math.cos(11*x)+.18*math.sin(11*x))
def lerp(a,b,t):return a+(b-a)*t
@functools.lru_cache(maxsize=128)
def font(size,weight=800,body=False,width=100):
 f=ImageFont.truetype(str(BODY if body else DISPLAY),round(size))
 f.set_variation_by_axes([weight] if body else [96,weight,width]);return f
@functools.lru_cache(maxsize=512)
def word(value,size,color=INK,weight=800,body=False,width=100):
 f=font(size,weight,body,width);b=f.getbbox(value)
 im=Image.new('RGBA',(max(1,b[2]-b[0]+12),max(1,b[3]-b[1]+12)))
 ImageDraw.Draw(im).text((6-b[0],6-b[1]),value,font=f,fill=(*color,255));return im
@functools.lru_cache(maxsize=512)
def probe(value,size,color,weight,body,width):
 tile=word(value,size,color,weight,body,width)
 alpha=tile.getchannel('A').point(lambda n:255 if n>=254 else 0)
 for patch in (5,3,1):
  m=alpha.filter(ImageFilter.MinFilter(patch)) if patch>1 else alpha
  bbox=m.getbbox()
  if not bbox:continue
  cx,cy=(bbox[0]+bbox[2])/2,(bbox[1]+bbox[3])/2
  best=min(((x-cx)**2+(y-cy)**2,x,y) for y in range(bbox[1],bbox[3]) for x in range(bbox[0],bbox[2]) if m.getpixel((x,y)))
  return best[1],best[2],patch
 raise RuntimeError('No opaque type core')
def ratio(a,b):
 def lum(c):return sum(w*(v/255/12.92 if v/255<=.04045 else ((v/255+.055)/1.055)**2.4) for w,v in zip((.2126,.7152,.0722),c))
 lo,hi=sorted((lum(a),lum(b)));return (hi+.05)/(lo+.05)
def put(dst,tile,x,y,scale=1,angle=0,alpha=1,center=False):
 if alpha<=0 or scale<=0:return
 if abs(scale-1)>.001:tile=tile.resize((max(1,round(tile.width*scale)),max(1,round(tile.height*scale))),Image.Resampling.BICUBIC)
 if angle:tile=tile.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 if alpha<.999:tile=tile.copy();tile.putalpha(tile.getchannel('A').point(lambda n:round(n*clamp(alpha))))
 if center:x-=tile.width/2;y-=tile.height/2
 dst.alpha_composite(tile,(round(x),round(y)))
def rect(im,box,color,r=0,outline=None,width=2):ImageDraw.Draw(im).rounded_rectangle(tuple(round(v) for v in box),r,fill=color,outline=outline,width=width)
def ellipse(im,box,color,outline=None,width=2):ImageDraw.Draw(im).ellipse(tuple(round(v) for v in box),fill=color,outline=outline,width=width)
def line(im,points,color,width=5):ImageDraw.Draw(im).line([(round(x),round(y)) for x,y in points],fill=color,width=width,joint='curve')
def text(im,value,x,y,size=80,color=INK,weight=800,body=False,center=False,records=None,bg=CREAM,kind='headline',width=100):
 tile=word(value,size,color,weight,body,width)
 xx,yy=(x-tile.width/2,y-tile.height/2) if center else (x,y)
 put(im,tile,xx,yy)
 if records is not None:
  b=tile.getchannel('A').getbbox();bbox=[round(xx)+b[0],round(yy)+b[1],round(xx)+b[2],round(yy)+b[3]]
  assert SAFE[0]<=bbox[0]<bbox[2]<=SAFE[2] and SAFE[1]<=bbox[1]<bbox[3]<=SAFE[3],(value,bbox)
  gx,gy,patch=probe(value,size,color,weight,body,width)
  fgxy=[round(xx)+gx,round(yy)+gy];bgxy=[round(xx),round(yy)]
  actual_fg=im.getpixel(tuple(fgxy))[:3];actual_bg=im.getpixel(tuple(bgxy))[:3]
  measured=ratio(actual_fg,actual_bg)
  assert measured>=4.5,(value,actual_fg,actual_bg,measured)
  records.append({'kind':kind,'text':value,'bbox':bbox,'foreground':color,'background':bg,'actual_pixel_foreground':actual_fg,'actual_pixel_background':actual_bg,'probe_foreground_xy':fgxy,'probe_background_xy':bgxy,'foreground_opaque_patch_size':patch,'contrast':measured,'solid_protected':True})
 return tile

def circle_ray(im,x,y,r,color,t):
 for i in range(12):
  a=i*math.pi/6+t*.25
  line(im,[(x+math.cos(a)*(r+18),y+math.sin(a)*(r+18)),(x+math.cos(a)*(r+44),y+math.sin(a)*(r+44))],color,7)
 ellipse(im,(x-r,y-r,x+r,y+r),color)
def sunmark(im,x,y,size,color=CORAL,angle=0):
 tile=Image.new('RGBA',(round(size*2.1),round(size*2.0)));d=ImageDraw.Draw(tile)
 d.pieslice((0,0,round(size*2),round(size*2)),180,360,fill=color)
 for i,wide in enumerate([1.9,1.4,.8]):
  left=(2-wide)*size/2;top=size+(i*.25+.13)*size
  d.rounded_rectangle((left,top,left+wide*size,top+.11*size),.055*size,fill=color)
 put(im,tile,x,y,angle=angle,center=True)
def dots(im,t,color=CORAL):
 # Fidgety perimeter elements leave the reading centre clear.
 for i in range(7):
  a=i*2.399+t*.6;r=25+(i%3)*9
  x=105+32*math.sin(a) if i%2 else W-105+30*math.cos(a)
  y=160+i*108+17*math.sin(t*2+i)
  ellipse(im,(x-r,y-r,x+r,y+r),color)
def arrow(im,x,y,length,color,angle=0):
 tile=Image.new('RGBA',(round(length+100),100));d=ImageDraw.Draw(tile)
 d.line((0,50,length,50),fill=color,width=14);d.polygon([(length-35,14),(length+12,50),(length-35,86)],fill=color)
 put(im,tile,x,y,angle=angle,center=True)
@functools.lru_cache(maxsize=1)
def cover():
 page=(ROOT/'projects/sunset/src/app/app/page.tsx').read_text()
 start=page.index('<svg',page.index('function Landscape'))
 raw=page[start:page.index('</svg>',start)+6]
 raw='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 300">'+raw[raw.index('><rect')+1:]
 raw=re.sub(r"fill=\{\['([^']+)'[^}]+\}",lambda m:'fill="'+m.group(1)+'"',raw)
 raw=raw.replace('strokeWidth','stroke-width').replace('strokeLinecap','stroke-linecap')
 return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=raw.encode(),output_width=1440,output_height=720))).convert('RGBA')

@functools.lru_cache(maxsize=8)
def pack(width=500):
 h=round(width*.77);tile=Image.new('RGBA',(width,h));d=ImageDraw.Draw(tile)
 d.rounded_rectangle((2,2,width-3,h-3),22,fill=CREAM,outline=INK,width=4)
 art=cover().resize((width-34,round((width-34)*.5)),Image.Resampling.LANCZOS);tile.alpha_composite(art,(17,18))
 f=font(round(width*.063),800);d.text((18,h-width*.19),'The Lantern Trail',font=f,fill=INK)
 f=font(round(width*.033),600,True);d.text((20,h-width*.09),'A public learning pack',font=f,fill=INK)
 return tile

def cursor(im,x,y,click=0):
 if 0<click<1:
  r=20+45*click;ellipse(im,(x-r,y-r,x+r,y+r),None,CORAL,6)
 d=ImageDraw.Draw(im);d.polygon([(x,y),(x+2,y+48),(x+18,y+37),(x+30,y+59),(x+39,y+54),(x+26,y+33),(x+46,y+29)],fill=CREAM,outline=INK,width=3)

def load_clock():
 path=OUT/'story-timing.json'
 if not path.exists():path=OUT/'voice/timing.json'
 if path.exists():
  data=json.loads(path.read_text());cues=data.get('phrases',data.get('sentences'))
  assert len(cues)==9
  duration=20.0
  assert cues[-1]['end']<=duration-1.5
  return cues,math.ceil(duration*FPS)/FPS,data
 return [{'index':i+1,'text':s,'start':a,'end':b} for i,(s,a,b) in enumerate(PROVISIONAL)],24.,{'provisional':True}

def build_beats(cues,duration):
 # Stage boundaries follow complete voice cues, except one concept cut inside cue3.
 starts=[0]+[max(0,c['start']-.07) for c in cues[1:]]
 split=cues[2]['start']+(cues[2]['end']-cues[2]['start'])*.49
 raw=[('sunset',0,starts[1],['Good','learning.'],CREAM,INK),('fund',starts[1],starts[2],['Funded','together.'],CREAM,INK),('key',starts[2],split,['Key out.','Pack open.'],BUTTER,INK),('payout',split,starts[3],['Creators','can withdraw.'],MINT,INK),('miss',starts[3],starts[4],['Missed it?'],PEACH,INK),('refund',starts[4],starts[5],['Sponsors','claim refunds.'],CREAM,INK),('download',starts[5],starts[6],['Download.'],BUTTER,INK),('offline',starts[6],starts[7],['Yours,','offline.'],CREAM,INK),('support',starts[7],16.6,['Support','once.'],CORAL,(5,22,18)),('end',16.6,duration,['SUNSET'],CREAM,INK)]
 return [{'id':i,'start':a,'end':b,'lines':ls,'bg':bg,'fg':fg} for i,a,b,ls,bg,fg in raw]

def read_windows(beats):
 reads=[]
 for stage in beats:
  kind=stage['id'];a,b=stage['start'],stage['end'];rows=stage['lines']
  if kind=='end':continue
  chunks=[(kind,a,b,rows)]
  if kind=='fund':
   split=a+(b-a)*.56
   chunks=[('fund',a,split,rows),('near',split,b,['On NEAR.'])]
  if kind=='offline':chunks=[('offline',a,b,['Yours, offline.'])]
  for ident,start,end,lines in chunks:
   minimum=.3*sum(len(v.split()) for v in lines)+.5
   # Fund's first entry uses the full original stage, matching heading().
   available=(b-a) if ident=='fund' else end-start
   entry=min(.30,max(0,available-minimum-.08))
   if ident=='sunset':entry=1.10
   if ident=='offline':entry=0
   if ident=='near':end-=.20
   assert end-(start+entry)+1e-8>=minimum,(ident,end-start,minimum)
   reads.append({'id':ident,'lines':lines,'window':[start+entry,end],'minimum_read_seconds':minimum})
 return reads

def heading(im,rows,center,top,size,stage,t,recs,color,bg,offset=0,width=100):
 maxwidth=1460
 while max(word(v,size,color,800,False,width).width for v in rows)>maxwidth:size-=2
 total=sum(word(v,size,color,800,False,width).height for v in rows)+(len(rows)-1)*14
 durations=stage['end']-stage['start'];minimum=.3*sum(len(v.split()) for v in rows)+.5
 entry=min(.30,max(0,durations-minimum-.08))
 if stage['id']=='sunset':entry=1.10
 local=t-stage['start'];stable=local>=entry
 q=ease((local-.90)/.20) if stage['id']=='sunset' else (ease(local/max(.01,entry)) if entry else 1)
 y=top
 for i,row in enumerate(rows):
  tile=word(row,size,color,800,False,width)
  x=center-tile.width/2+(1-q)*(780 if i%2 else -780)+offset
  yy=y+60*(1-q)
  if stable:
   rect(im,(x-10,yy-9,x+tile.width+10,yy+tile.height+9),bg)
   text(im,row,x,yy,size,color,800,records=recs,bg=bg,width=width)
  else:put(im,tile,x,yy,angle=(1-q)*(12 if i%2 else -12))
  y+=tile.height+14
 return entry

def context(im,bg,dark=False):
 # Bright all the way through; small truthful network label, no dark warning chip.
 fg=CREAM if dark else INK
 put(im,LOGO,198,113,.16)
 text(im,'NEAR TESTNET',1480,121,30,fg,600,True)

def captions(im,t,cues,recs):
 for c in cues:
  if not c['start']<=t<c['end']:continue
  rows=[];current=''
  for w in c['text'].split():
   nxt=(current+' '+w).strip()
   if word(nxt,48,CREAM,500,True).width>1420 and current:rows.append(current);current=w
   else:current=nxt
  if current:rows.append(current)
  assert len(rows)<=2
  h=len(rows)*58+24;top=968-h
  width=max(word(v,48,CREAM,500,True).width for v in rows)+40
  rect(im,((W-width)/2,top,(W+width)/2,968),INK,18)
  for i,row in enumerate(rows):
   tile=word(row,48,CREAM,500,True)
   text(im,row,W/2,top+12+i*58+tile.height/2,48,CREAM,500,True,True,recs,INK,'caption')

class Product:
 def __init__(self):
  self.manifest=json.loads((V5/'footage/manifest.json').read_text())
  self.loaded={}
 def get(self,kind):
  if kind not in self.loaded:
   spec=self.manifest['compositor'][kind];path=ROOT/spec['path'];assert sha(path)==spec['sha256']
   image=Image.open(path).convert('RGBA')
   crop=spec.get('focus_crop') if kind=='download' else spec.get('crop')
   if crop:image=image.crop(tuple(crop))
   self.loaded[kind]=(image,spec)
  return self.loaded[kind]

def frame(t,cues,beats,duration,product,with_records=False,caption=True):
 recs=[];ui=None
 stage=next((b for b in beats if b['start']<=t<b['end']),beats[-1]);kind=stage['id'];a,b=stage['start'],stage['end'];u=(t-a)/max(.001,b-a);dt=t-a
 bg=stage['bg'];fg=stage['fg'];im=Image.new('RGBA',(W,H),bg)
 if kind=='sunset':
  if t<1.10:
   # An actual flat sunset opens the film: sun dips into sweeping horizon bands.
   r=245;sun_y=395+220*smooth(t/.95)
   circle_ray(im,960,sun_y,r,CORAL,t)
   for i,color in enumerate([PEACH,BUTTER,MINT]):
    yy=610+i*66+18*math.sin(t*2+i)
    rect(im,(-80,yy,W+80,H),color)
    line(im,[(-50,yy),(W+50,yy)],CREAM,5)
   # Horizon becomes the three stripes of the original mark before the type cut.
   if t>.90:
    q=ease((t-.90)/.20)
    ellipse(im,(960-1500*q,540-1500*q,960+1500*q,540+1500*q),CREAM)
    heading(im,stage['lines'],960,260,218,stage,t,recs,INK,CREAM)
  else:
   dots(im,t,CORAL);sunmark(im,1555,605,190,CORAL,-8*math.sin(t))
   # Perimeter paper copy slides in as the headline arrives, not another chapter card.
   tile=pack(390);put(im,tile,300,720,angle=-9,center=True)
   heading(im,stage['lines'],960,260,218,stage,t,recs,fg,bg)
   line(im,[(690,730),(820,748),(1030,725),(1210,735)],CORAL,13)
 elif kind=='fund':
  split=a+(b-a)*.56
  if t<split:
   dots(im,t,BLUE)
   for i in range(8):
    x=180+i*215;yy=730+35*math.sin(t*3+i)
    ellipse(im,(x-30,yy-30,x+30,yy+30),[CORAL,BLUE,INK][i%3])
    if i<7:arrow(im,x+105,yy,90,INK,0)
   heading(im,stage['lines'],960,260,212,stage,t,recs,INK,CREAM)
  else:
   bg=BLUE;im.paste(bg,(0,0,W,H));dots(im,t,BUTTER)
   sub={**stage,'id':'near','start':split,'lines':['On NEAR.']}
   heading(im,['On NEAR.'],960,365,252,sub,t,recs if t<b-.20 else None,CREAM,BLUE)
   # Flat escrow bowl + contributions; no metallic coin or lock prop.
   line(im,[(600,715),(660,770),(1260,770),(1320,715)],CREAM,13)
   for i in range(5):
    xx=730+i*116;yy=680+26*math.sin(t*3+i)
    ellipse(im,(xx-27,yy-27,xx+27,yy+27),BUTTER if i%2 else CORAL)
 elif kind=='key':
  dots(im,t,CORAL)
  q=ease(dt/.55)
  # Flat key flies across the whole canvas and becomes a line underneath the title.
  x=lerp(120,1530,q);y=650+45*math.sin(t*3)
  ellipse(im,(x-56,y-56,x+56,y+56),None,INK,15);line(im,[(x+50,y),(x+245,y)],INK,15)
  line(im,[(x+170,y),(x+170,y+45),(x+210,y+45),(x+210,y)],INK,13)
  heading(im,stage['lines'],960,225,196,stage,t,recs,INK,BUTTER)
  # A literal flat pack fans open at the edge; required copy never moves on its face.
  put(im,pack(340),390,735,angle=-10+20*u,center=True)
 elif kind=='payout':
  dots(im,t,BLUE)
  # Giant reassuring check circle, cropped deliberately as 2D punctuation.
  ellipse(im,(1400,300,1990,890),CORAL)
  line(im,[(1540,590),(1620,665),(1810,445)],CREAM,35)
  heading(im,stage['lines'],900,255,190,stage,t,recs,INK,MINT)
  for i in range(4):
   x=350+i*320+35*math.sin(t*2+i);yy=745+20*math.cos(t*2+i)
   rect(im,(x-75,yy-32,x+75,yy+32),BUTTER,32,INK,3)
 elif kind=='miss':
  # No alarms, countdowns or threatening clock; a friendly loop asks the condition.
  circle_ray(im,1510,600,200,CORAL,t)
  heading(im,stage['lines'],960,390,260,stage,t,recs,INK,PEACH)
 elif kind=='refund':
  dots(im,t,CORAL)
  # A boomerang return path is causal and playful. The sponsor dots return left.
  d=ImageDraw.Draw(im);d.arc((300,120,1620,960),0,170,fill=BLUE,width=14)
  for i in range(5):
   angle=math.pi*(.1+.78*((u+i*.17)%1));x=960+640*math.cos(angle);y=540+385*math.sin(angle)
   ellipse(im,(x-27,y-27,x+27,y+27),CORAL)
  heading(im,stage['lines'],960,250,194,stage,t,recs,INK,CREAM)
 elif kind=='download':
  heading(im,stage['lines'],960,175,170,stage,t,recs,INK,BUTTER)
  source,spec=product.get('download');scale=min(1,1300/source.width)
  tile=source.resize((round(source.width*scale),round(source.height*scale)),Image.Resampling.LANCZOS)
  x=(W-tile.width)//2;y=640-tile.height//2
  # Real source pixels, single whole row. Decorative arrow is outside the capture.
  put(im,tile,x,y);arrow(im,1610,640,145,INK,180)
  cursor(im,x+tile.width*.70+50*(1-ease(dt/.4)),y+tile.height*.59,clamp((dt-.55)/.3))
  ui={'kind':'download','source':spec,'display_bbox':[x,y,x+tile.width,y+tile.height],'source_dimensions':list(source.size),'scale':scale}
 elif kind=='offline':
  # The actual offline copy headline replaces the abstract world for a short proof.
  source,spec=product.get('offline');scale=min(1,1410/source.width)
  tile=source.resize((round(source.width*scale),round(source.height*scale)),Image.Resampling.LANCZOS)
  x=(W-tile.width)//2;y=350
  put(im,tile,x,y);sunmark(im,1610,730,100,CORAL,10*math.sin(t))
  text(im,'Yours, offline.',960,240,118,INK,800,center=True,records=recs,bg=CREAM)
  ui={'kind':'offline','source':spec,'display_bbox':[x,y,x+tile.width,y+tile.height],'source_dimensions':list(source.size),'scale':scale}
 elif kind=='support':
  dots(im,t,INK)
  # Collage fills the entire scene, not a fixed object panel.
  for i in range(3):
   tile=pack(330);x=240+i*720;y=680+45*math.sin(t*2+i)
   put(im,tile,x,y,angle=-14+i*14,center=True)
  heading(im,stage['lines'],960,220,235,stage,t,recs,(5,22,18),CORAL)
 elif kind=='end':
  # Original brand, lively outer punctuation, quiet stable address.
  dots(im,t,CORAL);put(im,LOGO,960,265,.50,center=True)
  text(im,'SUNSET',960,450,200,INK,800,center=True,records=recs,bg=CREAM,kind='brand')
  text(im,'Support once. Share forever.',960,620,52,INK,600,True,True,recs,CREAM,'tagline')
  text(im,'sunset-lemon.vercel.app',960,735,63,BLUE,600,True,True,recs,CREAM,'url')
  if t>=17.8:
   # License metadata occupies the former caption band after the voice is complete.
   text(im,'Origami — Scott Buckley · CC BY 4.0',960,876,31,INK,500,True,True,recs,CREAM,'music_credit')
   text(im,'www.scottbuckley.com.au',960,922,29,INK,500,True,True,recs,CREAM,'music_credit')
 # Flat transformation handoffs happen outside every promised stable read.
 if kind=='fund' and t>=a+(b-a)*.56:
  seam=a+(b-a)*.56
  if t<seam+.20:
   mask=Image.new('L',(W,H));q=ease((t-seam)/.20);radius=2400*q
   ImageDraw.Draw(mask).ellipse((1450-radius,650-radius,1450+radius,650+radius),fill=255)
   previous=Image.new('RGBA',(W,H),CREAM);previous.paste(im,(0,0),mask);im=previous
  if t>=b-.20:
   q=ease((t-(b-.20))/.20);rect(im,(-20,-20,W*q,H+20),BUTTER)
 if kind=='download' and dt<.22:
  mask=Image.new('L',(W,H));q=ease(dt/.22)
  edge=round(H*q);ImageDraw.Draw(mask).polygon([(0,0),(W,0),(W,edge+120),(0,edge-120)],fill=255)
  previous=Image.new('RGBA',(W,H),CREAM);previous.paste(im,(0,0),mask);im=previous
  line(im,[(0,edge-120),(W,edge+120)],INK,5)
 context(im,bg,kind=='fund'  and t>=a+(b-a)*.56)
 if caption:captions(im,t,cues,recs)
 # Every record must still match after later objects/labels/captions are drawn.
 for r in recs:
  f=im.getpixel(tuple(r['probe_foreground_xy']))[:3];bpx=im.getpixel(tuple(r['probe_background_xy']))[:3]
  assert ratio(f,bpx)>=4.5,('Later layer covered essential text',t,r['text'])
 if with_records:return im.convert('RGB'),recs,ui
 return im.convert('RGB')

def preview(cues,beats,duration,product):
 target=OUT/'composite';target.mkdir(parents=True,exist_ok=True)
 times=[0,.5,.95,1.2,1.7,2.8,4.9,6.8,8.7,10.5,11.8,13.5,14.8,15.8,17.2,18.8,duration-.5]
 times=sorted(set(max(0,min(duration-1/FPS,t)) for t in times))
 sheet=Image.new('RGB',(480*4,294*math.ceil(len(times)/4)),CREAM);phone=Image.new('RGB',(360*3,226*math.ceil(len(times)/3)),CREAM);metadata=[]
 for i,t in enumerate(times):
  im,recs,ui=frame(t,cues,beats,duration,product,True);n=round(t*FPS);im.save(target/f'frame-{n:06d}.png')
  sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),((i%4)*480,(i//4)*294));ImageDraw.Draw(sheet).text(((i%4)*480+8,(i//4)*294+274),f'{t:.3f}s',fill=INK)
  phone.paste(im.resize((360,203),Image.Resampling.LANCZOS),((i%3)*360,(i//3)*226));ImageDraw.Draw(phone).text(((i%3)*360+8,(i//3)*226+207),f'{t:.3f}s',fill=INK)
  metadata.append({'time':t,'frame':n,'text':recs,'ui':ui})
 sheet.save(target/'contact-sheet.jpg',quality=97);phone.save(target/'phone-sheet.jpg',quality=97)
 (target/'preview.json').write_text(json.dumps({'dimensions':[W,H],'fps':FPS,'duration':duration,'frames':metadata,'beats':beats},indent=2)+'\n')
 print(json.dumps({'contact_sheet':str(target/'contact-sheet.jpg'),'duration':duration,'preview_frames':len(times)}),flush=True)

def encode(cues,beats,duration,clock,product,proof=False):
 if not proof:assert not clock.get('provisional'),'Final narration clock required'
 seconds=4 if proof else duration;target=OUT/('sunset-v6-motion-proof.mp4' if proof else 'sunset-launch-v6.mp4')
 command=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','-']
 if not proof:command+=['-i',str(OUT/'audio/mix.wav'),'-map','0:v:0','-map','1:a:0']
 command+=['-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-preset','medium','-crf','14','-g','60','-threads','4','-color_range','tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
 command+=['-an'] if proof else ['-c:a','aac','-b:a','320k','-ar','48000']
 command+=['-t',str(seconds),'-movflags','+faststart',str(target)]
 process=subprocess.Popen(command,stdin=subprocess.PIPE);records=[];uis={}
 try:
  for n in range(round(seconds*FPS)):
   im,recs,ui=frame(n/FPS,cues,beats,duration,product,True)
   process.stdin.write(im.tobytes());records.append({'frame':n,'time':n/FPS,'text':recs})
   if ui:uis[ui['kind']]=ui
   if n%120==119:print(f'Composed {n+1}/{round(seconds*FPS)} native flat2D frames',flush=True)
  process.stdin.close();assert process.wait()==0
 finally:
  if process.poll() is None:process.kill()
 if not proof:
  fonts=json.loads((SRC/'fonts-provenance.json').read_text())
  for family in fonts['fonts']:
   for f in family['files'].values():assert sha(ROOT/f['path'])==f['sha256']
  spec={'schema':1,'dimensions':[W,H],'fps':FPS,'duration':duration,'safe_bbox':SAFE,'all_frames':records,'beats':beats,'essential_read_windows':read_windows(beats), 'method':'Native flat2D Pillow masks/paths/type. Source and final interior glyph/plane probes; no 3D input.'}
  (OUT/'composite/readability-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
  provenance={'schema':1,'path':str(target.relative_to(ROOT)),'sha256':sha(target),'bytes':target.stat().st_size,'duration':duration,'frames':round(seconds*FPS),'dimensions':[W,H],'fps':FPS,'video_encode_passes':1,'crf':14,'flat_2d':True,'three_d_input':False,'motion_interpolation':False,'source_sha256':sha(Path(__file__)),'actual_ui':uis,'font_provenance_sha256':sha(SRC/'fonts-provenance.json'),'audio_master_sha256':sha(OUT/'audio/mix.wav'),'readability_proof':str((OUT/'composite/readability-spec.json').relative_to(ROOT))}
  (OUT/'composite/composite-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
 print(json.dumps({'path':str(target),'sha256':sha(target),'bytes':target.stat().st_size}),flush=True)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--proof',action='store_true');parser.add_argument('--render',action='store_true');args=parser.parse_args()
 OUT.mkdir(parents=True,exist_ok=True);cues,duration,clock=load_clock();beats=build_beats(cues,duration);read_windows(beats);product=Product()
 preview(cues,beats,duration,product)
 if args.proof or args.render:encode(cues,beats,duration,clock,product,args.proof)
if __name__=='__main__':main()
