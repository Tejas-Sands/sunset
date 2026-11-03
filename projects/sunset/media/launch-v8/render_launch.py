#!/usr/bin/env python3
"""SUNSET v8: original warm kinetic flat-2D film. No CG or product mutations."""
import argparse, functools, hashlib, json, math, subprocess, io, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg
ROOT=Path(__file__).resolve().parents[4]
SRC=Path(__file__).resolve().parent
OUT=ROOT/'.publication/sunset-launch-v8'
V5=ROOT/'.publication/sunset-launch-v5'
V1=ROOT/'.publication/sunset-launch-v1'
W,H,FPS=1920,1080,30
CREAM=(255,243,221);INK=(32,59,54);CORAL=(228,91,53);BLUE=(36,77,221);MINT=(203,229,213);BUTTER=(242,210,103);PEACH=(255,190,151)
SAFE=(192,108,1728,972)
FONT_CACHE=ROOT/'.publication/sunset-launch-v6/fonts'
DISPLAY=FONT_CACHE/'BricolageGrotesque-VF.ttf';BODY=FONT_CACHE/'SpaceGrotesk-VF.ttf'
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


# V8 scenes and actual-recording integration follow below.

def bezier(a,b,c,u):
 return ((1-u)**2*a[0]+2*(1-u)*u*b[0]+u*u*c[0],(1-u)**2*a[1]+2*(1-u)*u*b[1]+u*u*c[1])
def route(im,a,b,c,color,width=6):
 line(im,[bezier(a,b,c,n/36) for n in range(37)],color,width)
def packet(im,x,y,color=CORAL,size=26):
 rect(im,(x-size,y-size,x+size,y+size),color,8)
 line(im,[(x-size*.4,y),(x+size*.4,y)],CREAM,4)
def small(im,value,x,y,size=29,color=INK,body=True,center=False):
 text(im,value,x,y,size,color,600,body,center)
def chain_path(im,t,color=INK,low=False):
 y=765 if low else 190
 for i in range(7):
  x=180+i*260
  if i<6:line(im,[(x+36,y),(x+224,y)],color,3)
  rect(im,(x-26,y-26,x+26,y+26),None,9,color,3)
  if i%2==0:ellipse(im,(x-7,y-7,x+7,y+7),color)
 q=(t*.5)%1;x=180+1560*q
 packet(im,x,y,CORAL,15)

def load_clock():
 path=OUT/'story-timing.json'
 if path.exists():
  data=json.loads(path.read_text());cues=data.get('phrases',data.get('sentences'))
  assert len(cues)==10,'Locked v8 script requires10completephrases'
  duration=float(data['duration']);assert duration>=cues[-1]['end']+1
  return cues,duration,data
 lines=[('When a website disappears, learning shouldn’t.',.2,2.9),('SUNSET locks community funding for learning packs in NEAR escrow.',3.02,6.9),('Release the matching key on time, and creators can withdraw their payout.',7.02,11.2),('Miss the deadline?',11.32,12.4),('Sponsors can claim refunds.',12.52,14.1),('Take a copy offline.',14.22,15.5),('Try it.',16.0,16.7),('It still works.',18.2,19.4),('Support once.',19.6,20.7),('Share forever.',20.9,21.9)]
 return [{'index':i+1,'text':v,'start':a,'end':b} for i,(v,a,b) in enumerate(lines)],24.9,{'provisional':True}

def build_beats(cues,duration):
 starts=[0]+[c['start']-.06 for c in cues[1:]]
 split=cues[2]['start']+(cues[2]['end']-cues[2]['start'])*.46
 demo_end=starts[8];end_start=starts[9]
 raw=[('sunset',0,starts[1],['Learning','should stay.'],CREAM,INK),('fund',starts[1],starts[2],['NEAR escrow.'],BLUE,CREAM),('key',starts[2],split,['Publish','the key.'],BUTTER,INK),('payout',split,starts[3],['Creators','can withdraw.'],MINT,INK),('miss',starts[3],starts[4],['Missed?'],PEACH,INK),('refund',starts[4],starts[5],['Sponsors','claim refunds.'],CREAM,INK),('demo',starts[5],demo_end,['Try it offline.'],CREAM,INK),('support',demo_end,end_start,['Support once.'],CORAL,(5,22,18)),('end',end_start,duration,['SUNSET'],CREAM,INK)]
 return [{'id':i,'start':a,'end':b,'lines':ls,'bg':bg,'fg':fg} for i,a,b,ls,bg,fg in raw]

def entrance(stage):
 if stage['id']=='sunset':return 1.05
 if stage['id']=='demo':return .25
 minimum=.3*sum(len(v.split()) for v in stage['lines'])+.5
 return min(.24,max(0,stage['end']-stage['start']-minimum-.025))

def read_windows(beats):
 reads=[]
 for b in beats:
  if b['id']=='end':continue
  a=b['start']+entrance(b);z=b['end']
  minimum=.3*sum(len(v.split()) for v in b['lines'])+.5
  assert z-a+1e-8>=minimum,(b['id'],z-a,minimum)
  reads.append({'id':b['id'],'lines':b['lines'],'window':[a,z],'minimum_read_seconds':minimum})
 return reads

def heading(im,stage,t,recs,center=960,top=250,size=190,maxwidth=1450):
 rows=stage['lines'];fg,bg=stage['fg'],stage['bg'];dt=t-stage['start'];entry=entrance(stage)
 while max(word(v,size,fg).width for v in rows)>maxwidth:size-=2
 q=ease(dt/max(.01,entry))
 if stage['id']=='sunset':q=ease((t-.80)/.25)
 stable=dt>=entry
 for i,row in enumerate(rows):
  tile=word(row,size,fg);x=center-tile.width/2;y=top+i*(tile.height+12)
  if stable:
   rect(im,(x-13,y-10,x+tile.width+13,y+tile.height+10),bg)
   text(im,row,x,y,size,fg,800,records=recs,bg=bg)
  else:
   # The complete landing is fixed; independent letters only occupy the entrance.
   f=font(size);adv=[f.getlength(ch) for ch in row];xx=center-sum(adv)/2
   for j,(ch,w) in enumerate(zip(row,adv)):
    lag=.025*j;z=ease(max(0,q-lag)/(1-lag)) if lag<1 else q
    if ch!=' ':put(im,word(ch,size,fg),xx+(1-z)*(260 if i%2 else -260),y+(1-z)*(110+35*(j%3)),angle=(1-z)*((j%3)-1)*18,alpha=clamp(q*3))
    xx+=w

def context(im,kind,dark=False):
 fg=CREAM if dark else INK
 put(im,LOGO,198,113,.16)
 small(im,'NEAR TESTNET',1480,121,30,fg)
 if kind not in ('sunset','end'):
  label='ACTUAL APP RECORDING' if kind=='demo' else 'PROTOCOL ILLUSTRATION'
  label_bg=BLUE if dark else (CREAM if kind=='demo' else {'key':BUTTER,'payout':MINT,'miss':PEACH,'support':CORAL}.get(kind,CREAM))
  yy=799 if kind=='demo' else 785
  rect(im,(190,yy-3,580,yy+28),label_bg)
  small(im,label,198,yy,24,fg)

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
  h=len(rows)*58+24;top=968-h;ww=max(word(v,48,CREAM,500,True).width for v in rows)+40
  rect(im,((W-ww)/2,top,(W+ww)/2,968),INK,18)
  for i,row in enumerate(rows):
   tile=word(row,48,CREAM,500,True)
   text(im,row,W/2,top+12+i*58+tile.height/2,48,CREAM,500,True,True,recs,INK,'caption')

class ActualDemo:
 def __init__(self):
  self.specpath=OUT/'footage/compositor.json';self.spec=json.loads(self.specpath.read_text()) if self.specpath.exists() else None
  self.uses=[]
  if self.spec:
   for sample in self.spec['samples']:
    assert sha(ROOT/self.spec['frames_dir']/sample['file'])==sample['sha256']
 @functools.lru_cache(maxsize=4)
 def source(self,n):
  sample=self.spec['samples'][n];path=ROOT/self.spec['frames_dir']/sample['file'];im=Image.open(path).convert('RGBA')
  assert list(im.size)==self.spec['source_dimensions']
  return im.crop(tuple(self.spec['crop']))
 def panel(self,im,t):
  if self.spec is None:raise RuntimeError('Genuine action/result recording manifest required')
  source_time=clamp((t-self.spec['film_playback_start'])/self.spec['duration'])*self.spec['duration']
  n=max([i for i,v in enumerate(self.spec['samples']) if v['at']<=source_time]+[0])
  tile=self.source(n);scale=min(1,1440/tile.width,500/tile.height)
  disp=tile.resize((round(tile.width*scale),round(tile.height*scale)),Image.Resampling.LANCZOS)
  x=(W-disp.width)//2;y=300+(500-disp.height)//2;put(im,disp,x,y)
  # This ring is an editorial annotation of the actual logged browser click.
  # It is not a custom cursor or a fabricated app state.
  elapsed=t-self.spec['film_annotation_start']
  if 0<=elapsed<.42:
   cx=x+(self.spec['click_source_xy'][0]-self.spec['crop'][0])*scale
   cy=y+(self.spec['click_source_xy'][1]-self.spec['crop'][1])*scale
   rr=35+45*ease(elapsed/.42)
   overlay=Image.new('RGBA',(W,H));ellipse(overlay,(cx-rr,cy-rr,cx+rr,cy+rr),None,(*CORAL,round(230*(1-elapsed/.42))),5);im.alpha_composite(overlay)
  self.uses.append({'output_time':t,'source_frame':n,'source_time':self.spec['samples'][n]['at'],'recording_time':source_time})
  return {'kind':'actual_recording','source':{'path':self.spec['path'],'sha256':self.spec['sha256']},'source_dimensions':list(tile.size),'display_bbox':[x,y,x+disp.width,y+disp.height],'scale':scale,'source_frame':n,'source_time':self.spec['samples'][n]['at']}


def frame(t,cues,beats,duration,product,with_records=False,caption=True):
 recs=[];ui=None
 b=next((v for v in beats if v['start']<=t<v['end']),beats[-1]);kind=b['id'];a,z=b['start'],b['end'];dt=t-a;u=clamp(dt/max(.001,z-a));bg=b['bg'];im=Image.new('RGBA',(W,H),bg)
 if kind=='sunset':
  if t<1.05:
   yy=380+235*smooth(t/.88);circle_ray(im,960,yy,235,CORAL,t)
   for i,col in enumerate([PEACH,BUTTER,MINT]):rect(im,(-20,605+i*66,W+20,H),col)
   if t>.80:
    r=1900*ease((t-.80)/.25);ellipse(im,(960-r,540-r,960+r,540+r),CREAM)
    heading(im,b,t,recs,top=255,size=190)
  else:
   # A host window leaves the frame; the exact same resource remains.
   q=ease((dt-1.05)/.55);xx=lerp(1360,-650,q)
   rect(im,(xx-300,505,xx+300,760),MINT,25,INK,5);line(im,[(xx-300,555),(xx+300,555)],INK,4)
   for k in range(3):ellipse(im,(xx-266+k*30,522,xx-254+k*30,534),CORAL)
   put(im,pack(340),1425,680,angle=-7+4*math.sin(t),center=True)
   heading(im,b,t,recs,top=240,size=190)
   arrow(im,440,720,210,INK,180)
 elif kind=='fund':
  # Named-account routes flow into one bounded contract, rather than a coin shower.
  chain_path(im,t,CREAM)
  rect(im,(625,425,1295,765),BLUE,42,CREAM,7)
  small(im,'sunset.shiftultra.testnet',960,476,35,CREAM,center=True)
  small(im,'0.10 testNEAR CAP',960,570,47,CREAM,center=True)
  line(im,[(720,695),(1200,695)],CREAM,8)
  fill=clamp(dt/1.6);line(im,[(720,695),(720+480*fill,695)],BUTTER,18)
  for i,(start,control,target) in enumerate([((220,550),(480,230),(800,630)),((1700,640),(1430,315),(1130,630))]):
   route(im,start,control,target,CREAM,5)
   for k in range(3):
    q=clamp((dt-k*.25)/1.5);x,y=bezier(start,control,target,q);packet(im,x,y,CORAL if i==0 else BUTTER,24)
  small(im,'sponsor.shiftultra.testnet',330,740,24,CREAM,center=True)
  small(im,'reviewer.shiftultra.testnet',1570,740,24,CREAM,center=True)
  heading(im,b,t,recs,top=245,size=176)
 elif kind=='key':
  q=ease(dt/.42);x=lerp(-800,1510,q)
  # Key bar wipes the entire field before the key/pack reads settle.
  if dt<.20:rect(im,(-20,0,W*ease(dt/.20),H),BUTTER)
  ellipse(im,(x-66,610,x+66,742),None,INK,15);line(im,[(x+60,676),(x+300,676),(x+300,720),(x+255,720)],INK,16)
  small(im,'KEY COMMITMENT',470,660,29,INK,center=True)
  small(im,'3937071a…a4a697c5',470,710,34,INK,center=True)
  tile=pack(390);put(im,tile,1000,660,angle=-4+8*u,center=True)
  if dt<.65:
   lid=Image.new('RGBA',tile.size,BLUE);put(im,lid,1000+460*ease(dt/.65),660-400*ease(dt/.65),angle=-30*ease(dt/.65),center=True)
  heading(im,b,t,recs,top=235,size=190)
 elif kind=='payout':
  chain_path(im,t,INK,True)
  # Credit exists first. A distinct claim/withdraw route then moves toward creator.
  rect(im,(250,575,800,735),MINT,28,INK,5);small(im,'CREATOR CREDIT',525,610,32,INK,center=True);small(im,'0.10 testNEAR',525,670,43,INK,center=True)
  route(im,(825,650),(1080,420),(1420,650),INK,7)
  q=ease((dt-.35)/max(.3,z-a-.5));x,y=bezier((825,650),(1080,420),(1420,650),q);packet(im,x,y,CORAL,34)
  rect(im,(1330,585,1670,725),CREAM,30,INK,5);small(im,'shiftultra.testnet',1500,650,30,INK,center=True)
  heading(im,b,t,recs,top=220,size=174)
 elif kind=='miss':
  # The alternate condition is a quick directional reversal, never an alarm.
  route(im,(400,685),(960,350),(1500,685),INK,8)
  q=smooth(u);x,y=bezier((1500,685),(960,350),(400,685),q);packet(im,x,y,CORAL,55)
  heading(im,b,t,recs,top=320,size=250)
 elif kind=='refund':
  route(im,(1500,660),(960,320),(400,660),BLUE,10)
  for i in range(5):
   q=clamp((dt-i*.15)/1.2);x,y=bezier((1500,660),(960,320),(400,660),q);packet(im,x,y,CORAL,25)
  small(im,'CLAIMABLE',960,720,36,INK,center=True)
  heading(im,b,t,recs,top=230,size=184)
 elif kind=='demo':
  # This is recorded browser motion; no custom cursor or fabricated control.
  if product.spec is None:
   rect(im,(240,300,1680,800),MINT,20)
  else:ui=product.panel(im,t)
  heading(im,b,t,recs,top=165,size=118)
 elif kind=='support':
  # Released copies travel to ordinary recipients; access is not token gated.
  for i in range(7):
   x=960+(i-3)*280;y=660+95*math.sin(i*.9+t*.8)
   if i<6:line(im,[(x,y),(x+280,660+95*math.sin((i+1)*.9+t*.8))],INK,4)
   put(im,pack(250),x,y,angle=(i-3)*6,center=True)
  heading(im,b,t,recs,top=260,size=202)
 elif kind=='end':
  # Clean approved branding; links and recording attribution live in post text.
  for i in range(5):
   x=90 if i%2 else 1830;y=220+i*140;packet(im,x,y,CORAL,22+4*(i%2))
  put(im,LOGO,960,265,.50,center=True)
  text(im,'SUNSET',960,450,200,INK,800,center=True,records=recs,bg=CREAM,kind='brand')
  text(im,'Support once. Share forever.',960,620,52,INK,600,True,True,recs,CREAM,'tagline')
 context(im,kind,kind=='fund')
 if caption:captions(im,t,cues,recs)
 for r in recs:
  fg=im.getpixel(tuple(r['probe_foreground_xy']))[:3];bpx=im.getpixel(tuple(r['probe_background_xy']))[:3]
  assert ratio(fg,bpx)>=4.5,('Later layer covered essential text',t,r['text'])
 if with_records:return im.convert('RGB'),recs,ui
 return im.convert('RGB')

def preview(cues,beats,duration,product):
 target=OUT/'composite';target.mkdir(parents=True,exist_ok=True)
 times=[0,.5,.95,1.2]+[b['start']+min(.8,(b['end']-b['start'])*.55) for b in beats[1:]]+[duration-.5]
 times=sorted(set(max(0,min(duration-1/FPS,t)) for t in times))
 sheet=Image.new('RGB',(480*4,294*math.ceil(len(times)/4)),CREAM);phone=Image.new('RGB',(360*3,226*math.ceil(len(times)/3)),CREAM);metadata=[]
 for i,t in enumerate(times):
  im,recs,ui=frame(t,cues,beats,duration,product,True);n=round(t*FPS);im.save(target/f'frame-{n:06d}.png')
  sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),((i%4)*480,(i//4)*294));ImageDraw.Draw(sheet).text(((i%4)*480+8,(i//4)*294+274),f'{t:.3f}s',fill=INK)
  phone.paste(im.resize((360,203),Image.Resampling.LANCZOS),((i%3)*360,(i//3)*226));ImageDraw.Draw(phone).text(((i%3)*360+8,(i//3)*226+207),f'{t:.3f}s',fill=INK)
  metadata.append({'time':t,'frame':n,'text':recs,'ui':ui})
 sheet.save(target/'contact-sheet.jpg',quality=97);phone.save(target/'phone-sheet.jpg',quality=97)
 (target/'preview.json').write_text(json.dumps({'dimensions':[W,H],'fps':FPS,'duration':duration,'frames':metadata,'beats':beats,'real_recording_ready':product.spec is not None},indent=2)+'\n')
 print(json.dumps({'contact_sheet':str(target/'contact-sheet.jpg'),'duration':duration,'preview_frames':len(times),'real_recording_ready':product.spec is not None}),flush=True)

def encode(cues,beats,duration,clock,product,proof=False):
 if not proof:
  product.uses=[]
  assert not clock.get('provisional'),'Final narration clock required'
  assert product.spec is not None,'Genuine recorded action/result required'
  assert sha(ROOT/product.spec['path'])==product.spec['sha256']
  assert sha(OUT/'audio/mix.wav')==clock['mix_sha256']
 seconds=4 if proof else duration;target=OUT/('sunset-v8-motion-proof.mp4' if proof else 'sunset-launch-v8.mp4')
 command=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','-']
 if not proof:command+=['-i',str(OUT/'audio/mix.wav'),'-map','0:v:0','-map','1:a:0']
 command+=['-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-preset','medium','-crf','14','-g','60','-threads','4','-color_range','tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
 command+=['-an'] if proof else ['-c:a','aac','-b:a','320k','-ar','48000']
 command+=['-t',str(seconds),'-movflags','+faststart',str(target)]
 process=subprocess.Popen(command,stdin=subprocess.PIPE);records=[];uis={}
 try:
  for n in range(round(seconds*FPS)):
   im,recs,ui=frame(n/FPS,cues,beats,duration,product,True)
   for i,a in enumerate(recs):
    for b in recs[i+1:]:
     aa,bb=a['bbox'],b['bbox']
     assert max(aa[0],bb[0])>=min(aa[2],bb[2]) or max(aa[1],bb[1])>=min(aa[3],bb[3]),('Essential overlap',n,a['text'],b['text'])
   process.stdin.write(im.tobytes());records.append({'frame':n,'time':n/FPS,'text':recs})
   if ui:uis[ui['kind']]=ui
   if n%120==119:print(f'Composed {n+1}/{round(seconds*FPS)} native flat2D frames',flush=True)
  process.stdin.close();assert process.wait()==0
 finally:
  if process.poll() is None:process.kill()
 if not proof:
  font_provenance=SRC/'fonts-provenance.json'
  if not font_provenance.exists():font_provenance=ROOT/'projects/sunset/media/launch-v7/fonts-provenance.json'
  fonts=json.loads(font_provenance.read_text())
  for family in fonts['fonts']:
   for f in family['files'].values():assert sha(ROOT/f['path'])==f['sha256']
  spec={'schema':1,'dimensions':[W,H],'fps':FPS,'duration':duration,'safe_bbox':SAFE,'all_frames':records,'beats':beats,'essential_read_windows':read_windows(beats),'method':'Native flat2D paths/type/protected read cores plus actual time-mapped browser recording. No3D input.'}
  (OUT/'composite/readability-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
  provenance={'schema':1,'path':str(target.relative_to(ROOT)),'sha256':sha(target),'bytes':target.stat().st_size,'duration':duration,'frames':round(seconds*FPS),'dimensions':[W,H],'fps':FPS,'video_encode_passes':1,'crf':14,'flat_2d':True,'three_d_input':False,'motion_interpolation':False,'source_sha256':sha(Path(__file__)),'actual_ui':uis,'actual_demo_manifest':str(product.specpath.relative_to(ROOT)),'actual_demo_manifest_sha256':sha(product.specpath),'actual_demo':product.spec,'actual_demo_frame_uses':product.uses,'font_provenance_sha256':sha(font_provenance),'audio_master_sha256':sha(OUT/'audio/mix.wav'),'readability_proof':str((OUT/'composite/readability-spec.json').relative_to(ROOT))}
  (OUT/'composite/composite-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
 print(json.dumps({'path':str(target),'sha256':sha(target),'bytes':target.stat().st_size}),flush=True)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--proof',action='store_true');parser.add_argument('--render',action='store_true');args=parser.parse_args()
 OUT.mkdir(parents=True,exist_ok=True);cues,duration,clock=load_clock();beats=build_beats(cues,duration);read_windows(beats);product=ActualDemo()
 preview(cues,beats,duration,product)
 if args.proof or args.render:encode(cues,beats,duration,clock,product,args.proof)
if __name__=='__main__':main()
