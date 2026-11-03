#!/usr/bin/env python3
"""SUNSET v9: one pack / many lives. Native authored 2D + honest browser samples.
No narration generation, chain actions, stock visuals, invented cursor or fake app state.
"""
import argparse, functools, hashlib, io, json, math, re, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg
ROOT=Path(__file__).resolve().parents[4]; SRC=Path(__file__).resolve().parent
OUT=ROOT/'.publication/sunset-launch-v9'; V8=ROOT/'.publication/sunset-launch-v8'
W,H,FPS,DURATION=1920,1080,30,56
CREAM=(255,243,221); INK=(32,59,54); CORAL=(221,79,43); BLUE=(36,77,221)
MINT=(203,229,213); BUTTER=(242,210,103); PEACH=(255,190,151); WHITE=(255,252,244)
SAFE=(125,85,1795,995)
FONT_CACHE=ROOT/'.publication/sunset-launch-v6/fonts'
DISPLAY=FONT_CACHE/'BricolageGrotesque-VF.ttf'; BODY=FONT_CACHE/'SpaceGrotesk-VF.ttf'
LOGO_PATH=ROOT/'.publication/sunset-launch-v1/render/logo.png'
LOGO=Image.open(LOGO_PATH).convert('RGBA')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clamp(x):return max(0.,min(1.,x))
def ease(x):return 1-(1-clamp(x))**3
def smooth(x):x=clamp(x);return x*x*(3-2*x)
def mix(a,b,x):return a+(b-a)*x
def rect(im,box,col,r=0,outline=None,width=2):ImageDraw.Draw(im).rounded_rectangle(tuple(round(v) for v in box),r,fill=col,outline=outline,width=width)
def line(im,points,col,width=5):ImageDraw.Draw(im).line([(round(x),round(y)) for x,y in points],fill=col,width=width,joint='curve')
def ellipse(im,box,col,outline=None,width=2):ImageDraw.Draw(im).ellipse(tuple(round(v) for v in box),fill=col,outline=outline,width=width)
@functools.lru_cache(maxsize=128)
def font(size,weight=800,body=False):
 f=ImageFont.truetype(str(BODY if body else DISPLAY),round(size));f.set_variation_by_axes([min(700,weight)] if body else [96,weight,100]);return f
@functools.lru_cache(maxsize=512)
def word(value,size,col=INK,weight=800,body=False):
 f=font(size,weight,body);b=f.getbbox(value);im=Image.new('RGBA',(max(1,b[2]-b[0]+12),max(1,b[3]-b[1]+12)))
 ImageDraw.Draw(im).text((6-b[0],6-b[1]),value,font=f,fill=(*col,255));return im
@functools.lru_cache(maxsize=512)
def core(value,size,col,weight,body):
 a=word(value,size,col,weight,body).getchannel('A').point(lambda n:255 if n==255 else 0)
 for patch in (5,3,1):
  m=a.filter(ImageFilter.MinFilter(patch)) if patch>1 else a;b=m.getbbox()
  if b:
   cx,cy=(b[0]+b[2])/2,(b[1]+b[3])/2
   _,x,y=min(((x-cx)**2+(y-cy)**2,x,y) for y in range(b[1],b[3]) for x in range(b[0],b[2]) if m.getpixel((x,y)))
   return x,y,patch
 raise AssertionError('No opaque type core')
def contrast(a,b):
 def lum(c):return sum(w*(v/255/12.92 if v/255<=.04045 else ((v/255+.055)/1.055)**2.4) for w,v in zip((.2126,.7152,.0722),c))
 a,b=sorted((lum(a),lum(b)));return (b+.05)/(a+.05)
def put(im,tile,x,y,scale=1,angle=0,alpha=1,center=True):
 if scale<=0 or alpha<=0:return
 if abs(scale-1)>.001:tile=tile.resize((max(1,round(tile.width*scale)),max(1,round(tile.height*scale))),Image.Resampling.BICUBIC)
 if angle:tile=tile.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 if alpha<.999:tile=tile.copy();tile.putalpha(tile.getchannel('A').point(lambda n:round(n*clamp(alpha))))
 if center:x-=tile.width/2;y-=tile.height/2
 im.alpha_composite(tile,(round(x),round(y)))
def text(im,value,x,y,size=80,col=INK,bg=CREAM,recs=None,kind='essential',body=False,weight=800):
 tile=word(value,size,col,weight,body);put(im,tile,x,y,center=False)
 if recs is not None:
  b=tile.getchannel('A').getbbox();bb=[round(x)+b[0],round(y)+b[1],round(x)+b[2],round(y)+b[3]]
  assert SAFE[0]<=bb[0]<bb[2]<=SAFE[2] and SAFE[1]<=bb[1]<bb[3]<=SAFE[3],(value,bb)
  xx,yy,patch=core(value,size,col,weight,body);fg=[round(x)+xx,round(y)+yy];bpx=[round(x),round(y)]
  recs.append({'kind':kind,'text':value,'bbox':bb,'foreground':col,'background':bg,'probe_foreground_xy':fg,'probe_background_xy':bpx,'foreground_opaque_patch_size':patch,'solid_protected':True})
 return tile

def label(im,value,x,y,col=INK,bg=CREAM,size=25):
 tile=word(value,size,col,600,True);rect(im,(x-9,y-7,x+tile.width+9,y+tile.height+7),bg,7);put(im,tile,x,y,center=False)
@functools.lru_cache(maxsize=1)
def landscape():
 page=(ROOT/'projects/sunset/src/app/app/page.tsx').read_text();start=page.index('<svg',page.index('function Landscape'));raw=page[start:page.index('</svg>',start)+6]
 raw='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 300">'+raw[raw.index('><rect')+1:]
 raw=re.sub(r"fill=\{\['([^']+)'[^}]+\}",lambda m:'fill="'+m.group(1)+'"',raw).replace('strokeWidth','stroke-width').replace('strokeLinecap','stroke-linecap')
 return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=raw.encode(),output_width=1600,output_height=800))).convert('RGBA')
@functools.lru_cache(maxsize=12)
def pack(width=700,closed=True,worksheet=False):
 h=round(width*.82);im=Image.new('RGBA',(width+36,h+42));d=ImageDraw.Draw(im)
 for i in range(3,0,-1):rect(im,(8+i*5,8+i*7,width+i*5,h+i*7),MINT,22,INK,3)
 rect(im,(8,8,width,h),WHITE,22,INK,4)
 art=landscape().resize((width-40,round((width-40)*.5)),Image.Resampling.LANCZOS);im.alpha_composite(art,(24,24))
 d.text((28,width*.55),'THE LANTERN TRAIL',font=font(width*.051),fill=INK)
 d.text((30,width*.63),'A learning pack',font=font(width*.032,600,True),fill=INK)
 if worksheet:
  for i in range(3):
   xx=40+i*(width-75)/3;yy=width*.73
   rect(im,(xx,yy,xx+width*.21,yy+width*.055),MINT,8)
 else:
  for i in range(5):rect(im,(30+i*width*.18,width*.715,30+i*width*.18+width*.13,width*.735),BUTTER,4)
 if closed:
  rect(im,(width*.80,8,width*.88,h),BLUE,5)
  ellipse(im,(width*.79,width*.38,width*.89,width*.48),BUTTER,INK,3)
  rect(im,(width*.822,width*.413,width*.858,width*.449),INK,3)
 return im

def shadowpack(im,x,y,width,angle=0,closed=True,alpha=1):
 tile=pack(700,closed);scale=width/tile.width
 # Offset solid paper silhouettes create graphic depth without dark 3D materials.
 sh=tile.copy();sh.putalpha(sh.getchannel('A').point(lambda n:round(n*.17)));sh.paste(INK,(0,0,sh.width,sh.height),sh)
 put(im,sh,x+16,y+23,scale,angle,alpha);put(im,tile,x,y,scale,angle,alpha)
def key(im,x,y,scale=1,angle=0):
 tile=Image.new('RGBA',(520,200));ellipse(tile,(12,24,164,176),None,INK,23);line(tile,[(157,100),(485,100),(485,154),(430,154),(430,104)],INK,25)
 for xx,hh in ((430,35),(465,55),(495,25)):rect(tile,(xx,95,xx+14,100+hh),INK,2)
 put(im,tile,x,y,scale,angle)
def sun(im,x,y,r,col=CORAL):
 d=ImageDraw.Draw(im);d.pieslice((x-r,y-r,x+r,y+r),180,360,fill=col)
 for i,ww in enumerate((1.8,1.35,.8)):
  rect(im,(x-ww*r/2,y+25+i*r*.18,x+ww*r/2,y+25+i*r*.18+r*.085),col,12)
def glyphline(im,value,x,y,size,col,q,seed=0):
 f=font(size);xx=x
 for i,ch in enumerate(value):
  advance=f.getlength(ch)
  if ch!=' ':
   p=ease((q-i*.015)/max(.1,1-i*.015));put(im,word(ch,size,col),xx+(1-p)*(85 if (i+seed)%2 else -85),y+(1-p)*(240 if (i+seed)%3 else -190),angle=(1-p)*((i%5)-2)*13,alpha=clamp(q*3),center=False)
  xx+=advance

def headline(im,rows,x,y,size,dt,bg,recs,col=INK,enter=.42,gap=4):
 maxw=1660-x+125
 while max(word(v,size,col).width for v in rows)>maxw:size-=1
 # Reading begins after authored glyph assembly; a protected local field is painted last.
 step=size+10
 if dt+1e-8>=enter:
  for i,row in enumerate(rows):
   tile=word(row,size,col);yy=y+i*step
   rect(im,(x-12,yy-10,x+tile.width+12,yy+tile.height+10),bg,4)
   text(im,row,x,yy,size,col,bg,recs)
 else:
  for i,row in enumerate(rows):glyphline(im,row,x,y+i*step,size,col,clamp(dt/enter),i)

def flight(im,t,start,end,a,b,width=100,col=CORAL):
 q=ease((t-start)/(end-start));x=mix(a[0],b[0],q);y=mix(a[1],b[1],q)-math.sin(q*math.pi)*140
 rect(im,(x-width/2,y-width*.34,x+width/2,y+width*.34),col,15,INK,3)
 line(im,[(x-width*.22,y),(x+width*.22,y)],CREAM,4)

BEATS=[
 {'id':'work','start':0,'end':3.3,'read_start':.65,'lines':['Good learning','takes work.'],'bg':CREAM},
 {'id':'need','start':3.3,'end':6,'read_start':3.7,'lines':['Who pays','for it?'],'bg':CORAL},
 {'id':'public','start':6,'end':11,'read_start':6.45,'lines':['Fund a','public release.'],'bg':BLUE},
 {'id':'review','start':11,'end':14,'read_start':11.42,'lines':['Reviewed','before funding.'],'bg':MINT},
 {'id':'terms','start':14,'end':17,'read_start':14.4,'lines':['One target.','Clear deadlines.'],'bg':CREAM},
 {'id':'escrow','start':17,'end':20,'read_start':17.4,'lines':['Funds held','on NEAR.'],'bg':BLUE},
 {'id':'release','start':20,'end':23.5,'read_start':20.4,'read_end':22.3,'lines':['Release the','matching key.'],'bg':BUTTER},
 {'id':'credit','start':23.5,'end':25.5,'read_start':23.75,'lines':['Creator credit.'],'bg':MINT},
 {'id':'withdraw','start':25.5,'end':29,'read_start':25.9,'lines':['Creator can','withdraw.'],'bg':PEACH},
 {'id':'alternative','start':29,'end':32,'read_start':29.35,'lines':['Target missed?','Release late?'],'bg':CREAM},
 {'id':'refund','start':32,'end':35,'read_start':32.35,'lines':['Sponsors can','claim refunds.'],'bg':MINT},
 {'id':'download','start':35,'end':38,'read_start':35.3,'lines':['Download a working copy'],'bg':CREAM},
 {'id':'offline','start':38,'end':44,'read_start':38.3,'lines':['Works without SUNSET'],'bg':CREAM},
 {'id':'keep','start':44,'end':47.5,'read_start':44.4,'lines':['Keep','your copy.'],'bg':CREAM},
 {'id':'wallet','start':47.5,'end':51,'read_start':47.9,'lines':['No wallet','to learn.'],'bg':BLUE},
 {'id':'brand','start':51,'end':56,'read_start':51.55,'lines':['SUNSET','Support once. Share forever.'],'bg':CREAM},
]
def read_windows():
 out=[]
 for b in BEATS:
  extra=['ALTERNATIVE · BEFORE RELEASE'] if b['id'] in ('alternative','refund') else []
  words=sum(len(re.findall(r'[A-Za-z]+',x)) for x in b['lines']+extra);minimum=.3*words+.5
  assert b.get('read_end',b['end'])-b['read_start']>=minimum-1e-7,(b['id'],minimum,b.get('read_end',b['end'])-b['read_start'])
  out.append({'id':b['id'],'lines':b['lines']+extra,'window':[math.ceil((b['read_start']-1e-9)*FPS)/FPS,b.get('read_end',b['end'])],'minimum_read_seconds':minimum})
 out.append({'id':'release-payoff','lines':['PUBLIC COPY'],'window':[22.3,23.5],'minimum_read_seconds':1.1})
 return out

class ActualProof:
 def __init__(self):
  self.path=OUT/'footage/compositor.json';self.spec=json.loads(self.path.read_text()) if self.path.exists() else None;self.uses=[]
 @functools.lru_cache(maxsize=2)
 def source(self,path):return Image.open(ROOT/path).convert('RGBA')
 def panel(self,im,t,box=None,output_time=None):
  if not self.spec:
   rect(im,(150,245,1770,965),WHITE,20,INK,3);label(im,'ACTUAL RECORDING RESERVED',200,350,size=50);return None
  clips=self.spec['segments'];c=next((v for v in clips if v['start']<=t<v['end']),clips[-1])
  samples=c['sourceframes'];n=max([i for i,s in enumerate(samples) if s['film_time']<=t]+[0]);s=samples[n]
  raw=self.source(s['path']);assert list(raw.size)==c['source_dimensions'];original_crop=c['crop'];crop=list(original_crop);maximum=1.;zoom_reason=None
  if output_time is None and c['id'].startswith('actual-download'):
   maximum=2.;box=[300,420,1620,780];zoom_reason='Editorial2x magnification of genuine recorded Download control pixels.'
  elif output_time is None and c['id']=='actual-offline-answer-result' and t<42:
   maximum=2.2;box=[150,245,1770,965]
   # The browser actually scrolls between pre-input and first feedback capture; track that real crop.
   controls=[620,860,1120,1025] if n<3 else [620,810,1120,975]
   feedback=[620,990,1170,1080];q=ease((t-39.0)/.2)
   crop=[round(mix(a,b,q)) for a,b in zip(controls,feedback)]
   zoom_reason='Editorial2.2x camera focus on actual answer controls, then complete first two genuine feedback sentences. No UI or cursor reconstruction.'
  tile=raw.crop(tuple(crop));box=box or [150,245,1770,965];scale=min(maximum,(box[2]-box[0])/tile.width,(box[3]-box[1])/tile.height)
  tile=tile.resize((round(tile.width*scale),round(tile.height*scale)),Image.Resampling.LANCZOS);x=(box[0]+box[2]-tile.width)/2;y=(box[1]+box[3]-tile.height)/2
  rect(im,(x-4,y-4,x+tile.width+4,y+tile.height+4),INK,10);put(im,tile,x,y,center=False)
  rec={'kind':'actual_recording','clip':c['id'],'source_path':s['path'],'source_sha256':s['sha256'],'source_dimensions':list(raw.size),'source_capture_time':s['time'],'mapped_source_time':t-c['playbackstart'],'display_bbox':[round(x),round(y),round(x+tile.width),round(y+tile.height)],'original_manifest_crop':original_crop,'effective_roi':crop,'crop':crop,'scale':scale,'editorial_magnification':scale>1,'editorial_camera_reason':zoom_reason,'resampling':'LANCZOS','film_time':t if output_time is None else output_time,'source_sample':n,'source_sample_film_time':s['film_time'],'sampling':'True-time lossless screenshot sample holds. Geometric editorial crop/scale only; no invented cursor, UI state or source-motion interpolation.'}
  self.uses.append(rec);return rec

def scene(t,proof,record=True):
 b=next((v for v in BEATS if v['start']<=t<v['end']),BEATS[-1]);k=b['id'];dt=t-b['start'];u=dt/(b['end']-b['start']);bg=b['bg'];im=Image.new('RGBA',(W,H),bg);recs=[];ui=None
 if k=='work':
  # The sun is already the landscape of this exact pack. Macro-to-page pullback.
  q=ease(dt/1.2);dr=smooth((dt-1.2)/2.1);width=mix(2450,1030,q)+80*dr;xx=mix(1430,1435,q)-70*dr;yy=mix(800,635,q)-20*dr;ang=mix(-26,-12,q)-3*dr
  shadowpack(im,xx,yy,width,ang,False)
  # Off-axis worksheet leaves gather behind the cover, independent foreground depth.
  if dt>.6:
   for i in range(2):
    paper=Image.new('RGBA',(500,540));rect(paper,(5,5,490,530),MINT if i==0 else BUTTER,22,INK,3)
    for j in range(4):line(paper,[(55,100+j*94),(410,100+j*94)],INK,4)
    put(im,paper,1460+i*150,720-i*60,.65,-19+i*15,clamp((dt-.6)/.5))
   shadowpack(im,1435-70*smooth((dt-1.2)/2.1),635-20*smooth((dt-1.2)/2.1),1030+80*smooth((dt-1.2)/2.1),-12-3*smooth((dt-1.2)/2.1),False)
  # Creator's concrete work strokes assemble on the page surface; headline stays untouched.
  for i in range(3):
   p=ease((dt-.7-i*.42)/.32)
   line(im,[(1090,820+i*38),(1090+220*p,820+i*38)],CORAL,9)
  headline(im,b['lines'],155,160,152,dt,bg,recs,enter=.65)
  label(im,'ONE USEFUL LEARNING PACK',160,800,size=25)
  if dt<.6:
   # Literal setting-sun hook, matched to the sun printed on this pack at the pullback handoff.
   hook=Image.new('RGBA',(W,H),(244,214,167));p=ease(dt/.6)
   ellipse(hook,(1454-(267-130*p),247+138*p-(267-130*p),1454+(267-130*p),247+138*p+(267-130*p)),(242,115,68))
   ImageDraw.Draw(hook).polygon([(0,720),(290,510),(560,750),(865,520),(1235,800),(1600,650),(1920,820),(1920,1080),(0,1080)],fill=(126,141,111))
   ImageDraw.Draw(hook).polygon([(0,900),(410,710),(780,920),(1220,700),(1920,990),(1920,1080),(0,1080)],fill=(64,92,78))
   put(im,hook,0,0,alpha=1-smooth((dt-.4)/.2),center=False)

 elif k=='need':
  q=ease(dt/.6);shadowpack(im,mix(1450,450,q),mix(650,740,q),mix(1600,850,q),mix(-12,15,q),False)
  # Huge background question-mark crop is purely graphic, independent of the essential words.
  put(im,word('?',1100,BUTTER),1680,620,angle=-14)
  headline(im,b['lines'],900,230,172,dt,CREAM,recs,INK,enter=.4)
 elif k=='public':
  # Same pack swings through a quarter turn, then anonymous community interests gather around it.
  q=ease(dt/.7);h=ease((dt-4.4)/.6);shadowpack(im,mix(480,950,h),mix(580,560,h),mix(760,1800,h),mix(mix(75,-7,q),75,h),False)
  for i in range(5):
   x=300+i*310;yy=920+110*(1-ease((dt-.6-i*.09)/.6));ellipse(im,(x-26,yy-55,x+26,yy-3),BUTTER if i%2 else PEACH)
   rect(im,(x-48,yy+5,x+48,yy+65),CREAM,22)
   p=ease((dt-1.1-i*.48)/.6)
   if p>0:line(im,[(x,yy-76),(mix(x,620,p),mix(yy-76,800,p))],MINT,4)
  border=ease((dt-2.4)/1.9)
  points=[(130,820),(130,170),(830,170),(830,820),(130,820)];length=border*4
  for j in range(4):
   p=clamp(length-j)
   if p:line(im,[points[j],(mix(points[j][0],points[j+1][0],p),mix(points[j][1],points[j+1][1],p))],CREAM,6)
  headline(im,b['lines'],890,205,138,dt,bg,recs,CREAM,enter=.45)
  label(im,'COMMUNITY → PUBLIC RELEASE',900,645,CREAM,BLUE,25)
 elif k=='review':
  q=ease(dt/.55);shadowpack(im,mix(950,1350,q),mix(560,600,q),mix(1800,830,q),mix(75,7,q))
  headline(im,b['lines'],150,175,140,dt,bg,recs,enter=.42)
  for i,(yy,ww) in enumerate(((650,370),(750,275),(850,330))):
   p=ease((dt-.5-i*.14)/.35);line(im,[(175,yy),(195,yy+20),(235,yy-26)],INK,9);rect(im,(275,yy-5,275+ww*p,yy+10),INK,7)
  label(im,'PACK + RELEASE TERMS',150,545,size=26,bg=MINT)
 elif k=='terms':
  # The same empty agreement boundary is carried into the next custody composition.
  h=ease((dt-2.4)/.6);shadowpack(im,mix(1510,340,h),mix(670,360,h),650,mix(-14,-12,h))
  box=[mix(a,b,h) for a,b in zip((150,550,1770,975),(620,155,1770,620))]
  color=tuple(round(mix(a,b,h)) for a,b in zip(BUTTER,BLUE));edge=tuple(round(mix(a,b,h)) for a,b in zip(INK,CREAM))
  rect(im,box,color,32,edge,5)
  gauge=[mix(a,b,h) for a,b in zip((215,690,1690,735),(680,545,1690,580))]
  rect(im,gauge,CREAM,20,edge,3);line(im,[(gauge[2],gauge[1]-25),(gauge[2],gauge[3]+25)],edge,7)
  if h<.01:
   label(im,'FUNDING TARGET',205,590,bg=BUTTER,size=35)
   for xx,value in ((205,'FUND BY'),(950,'RELEASE BY')):
    line(im,[(xx,810),(xx,860),(xx+570,860)],INK,5);label(im,value,xx+26,795,bg=BUTTER,size=33)
  headline(im,b['lines'],150,140,148,dt,bg,recs,enter=.4)
 elif k=='escrow':
  # Closed resource and bounded custody exchange foreground/background hierarchy.
  dr=smooth(dt/3);shadowpack(im,340-60*dr,360+30*dr,650+90*dr,-12-5*dr)
  rect(im,(620,155,1770,620),BLUE,40,CREAM,6)
  for i in range(7):
   start=17.25+i*.22;flight(im,t,start,start+.8,(700+i*155,-150),(720+i*155,470),110,BUTTER if i%2 else PEACH)
  fill=clamp((dt-.5)/1.65);rect(im,(680,545,680+1010*fill,580),MINT,12)
  line(im,[(1690,520),(1690,605)],CREAM,8)
  headline(im,b['lines'],150,690,134,dt,bg,recs,CREAM,enter=.4)
 elif k=='release':
  # Macro matching teeth, then a single full-frame opening into a recognizable inner lesson.
  q=ease((dt-1.1)/.4);shadowpack(im,1325,650,850,-5,False)
  if dt<1.5:
   band=Image.new('RGBA',(150,850));rect(band,(0,0,150,850),BLUE,10)
   for xx,hh in ((20,28),(48,44),(72,20)):rect(band,(xx,425,xx+13,425+hh),BUTTER,2)
   put(im,band,1530+q*950,650-q*650,1,-5-q*60)
   key(im,mix(650,1340,ease(dt/.8)),665,.8)
  if q>0:
   width=mix(620,1760,q);height=width*.54;xx=mix(1350,960,q);yy=mix(670,550,q)
   sheet=Image.new('RGBA',(1760,950));rect(sheet,(8,8,1750,940),WHITE,32,INK,5)
   # The original cover art becomes the header of the page inside the same released pack.
   art=landscape().resize((650,325),Image.Resampling.LANCZOS);sheet.alpha_composite(art,(1020,55))
   text(sheet,'The Lantern Trail',95,100,86)
   text(sheet,'7 + 5 =',95,360,175)
   for i in range(12):
    cx=130+(i%6)*135;cy=650+(i//6)*120;ellipse(sheet,(cx-34,cy-34,cx+34,cy+34),CORAL if i<7 else BUTTER,INK,3)
   rect(sheet,(1040,485,1620,810),MINT,30,INK,4);text(sheet,'12',1180,535,180)
   put(im,sheet,xx,yy,width/1760,mix(-12,0,q))
  if dt<2.3-1e-8:headline(im,b['lines'],150,160,145,dt,bg,recs,enter=.4)
  else:
   rect(im,(145,860,790,980),BUTTER,14)
   text(im,'PUBLIC COPY',160,875,80,INK,BUTTER,recs,kind='payoff')
 elif k=='credit':
  shadowpack(im,400,620,800,12,False)
  q=ease(dt/.6);rect(im,(790,530+(1-q)*400,1740,825+(1-q)*400),CREAM,28,INK,5)
  if dt>.45:label(im,'AGREED PAYMENT',860,660,bg=CREAM,size=42)
  headline(im,b['lines'],735,210,125,dt,bg,recs,enter=.25)
 elif k=='withdraw':
  shadowpack(im,370,830,490,-13,False)
  rect(im,(1260,450,1750,915),CREAM,40,INK,5);ellipse(im,(1415,495,1595,675),CORAL);rect(im,(1350,700,1660,850),MINT,50)
  line(im,[(640,690),(1215,690)],INK,10);ImageDraw.Draw(im).polygon([(1180,650),(1240,690),(1180,730)],fill=INK)
  flight(im,t,26,27.4,(690,690),(1475,770),220,BUTTER)
  headline(im,b['lines'],150,145,160,dt,bg,recs,enter=.4)
  label(im,'SEPARATE WITHDRAWAL',655,820,bg=PEACH,size=26)
 elif k=='alternative':
  # Explicitly a different pre-release branch. No released campaign is reversed.
  shadowpack(im,1450,660,610,10,True)
  line(im,[(1250,730),(1100,730),(1030,870),(810,870)],INK,9)
  line(im,[(1100,730),(1030,590),(870,590)],INK,9)
  label(im,'ALTERNATIVE · BEFORE RELEASE',150,112,bg=CREAM,size=54)
  if dt>=.35:text(im,'ALTERNATIVE · BEFORE RELEASE',150,112,54,INK,CREAM,recs,kind='condition',body=True,weight=600)
  headline(im,b['lines'],150,275,147,dt,bg,recs,enter=.35)
 elif k=='refund':
  shadowpack(im,1500,690,680,-10,True)
  for i in range(3):
   flight(im,t,32.25+i*.15,33.2+i*.15,(1420,720),(350+i*230,860),110,CORAL)
   ellipse(im,(300+i*230,880,350+i*230,930),INK)
  label(im,'ALTERNATIVE · BEFORE RELEASE',150,112,bg=MINT,size=54)
  if dt>=.35:text(im,'ALTERNATIVE · BEFORE RELEASE',150,112,54,INK,MINT,recs,kind='condition',body=True,weight=600)
  headline(im,b['lines'],150,275,144,dt,bg,recs,enter=.35)
 elif k in ('download','offline'):
  ui=proof.panel(im,t)
  headline(im,b['lines'],150,105,91,dt,bg,recs,enter=.3)
  # The real content is kept as a single genuine sampled plate; no invented cursor or UI layer.
  label(im,'ACTUAL APP RECORDING  ·  '+('DOWNLOAD' if k=='download' else 'LOCAL FILE · NETWORK OFFLINE'),155,987,bg=CREAM,size=22)
 elif k=='keep':
  # Retained genuine offline result remains foremost as the host moves away behind it.
  q=ease(dt/1.1);xx=1400+q*1800
  rect(im,(xx-500,180,xx+500,760),MINT,28,INK,4);line(im,[(xx-500,240),(xx+500,240)],INK,4)
  for i in range(3):
   p=ease((dt-i*.13)/.8);shadowpack(im,mix(1350,1150+i*220,p),mix(600,300+i*85,p),450,(-22+i*13)*p,False)
  ui=proof.panel(im,43.5,[680,575,1790,960],output_time=t)
  if ui:ui['endpoint_freeze']='Final genuine feedback sample held as retained copy; mapped original film playback position43.5s. See source_capture_time and source_sample_film_time for actual capture identity.'
  label(im,'A RETAINED OFFLINE COPY',695,530,bg=CREAM,size=25)
  headline(im,b['lines'],150,155,158,dt,bg,recs,enter=.4)
 elif k=='wallet':
  for i in range(4):
   p=ease((dt-i*.08)/.7);shadowpack(im,270+i*475,mix(1300,840,p),490,(-12+i*8)*p,False)
  headline(im,b['lines'],640,145,175,dt,bg,recs,CREAM,enter=.4)
  # A nearby original landscape macro ties contexts back to the single released pack.
  put(im,landscape(),-220,320,.6,-14)
 elif k=='brand':
  q=ease(dt/.55)
  # Last copy shrinks to the original rounded SUNSET symbol; the clean resolution holds >4s.
  if dt<.55:shadowpack(im,mix(1470,960,q),mix(750,365,q),mix(800,250,q),mix(24,0,q),False,1-q)
  put(im,LOGO,960,320,.94,alpha=q)
  if dt>=.55:
   text(im,'SUNSET',960-word('SUNSET',205).width/2,490,205,INK,CREAM,recs,kind='brand')
   text(im,'Support once. Share forever.',960-word('Support once. Share forever.',65,INK,600,True).width/2,733,65,INK,CREAM,recs,kind='tagline',body=True,weight=600)
 # Small truthful production context is secondary, separate from the essential reading fields.
 if k not in ('work','need','download','offline','brand','keep','wallet'):label(im,'PROTOCOL ILLUSTRATION',135,1018,CREAM if bg==BLUE else INK,bg,21)
 # Every essential glyph gets a final-composite foreground/background pixel probe.
 for r in recs:
  fg=im.getpixel(tuple(r['probe_foreground_xy']))[:3];bc=im.getpixel(tuple(r['probe_background_xy']))[:3];c=contrast(fg,bc)
  assert c>=4.5,('Essential contrast',t,r['text'],fg,bc,c)
  r.update(actual_pixel_foreground=fg,actual_pixel_background=bc,contrast=c)
 for i,a in enumerate(recs):
  for z in recs[i+1:]:
   aa,bb=a['bbox'],z['bbox'];assert max(aa[0],bb[0])>=min(aa[2],bb[2]) or max(aa[1],bb[1])>=min(aa[3],bb[3]),('Essential overlap',t,a['text'],z['text'])
 return im.convert('RGB'),recs,ui

def validate_sources(final=False):
 fonts=json.loads((SRC/'fonts-provenance.json').read_text())
 for fam in fonts['fonts']:
  for p in fam['files'].values():assert sha(ROOT/p['path'])==p['sha256'],p['path']
 timeline=json.loads((SRC/'timeline.json').read_text());assert timeline['duration']==56 and timeline['frames']==1680
 assert timeline['beats']==json.loads(json.dumps(BEATS))
 assert timeline['essential_read_windows']==read_windows()
 if final:
  p=ActualProof();assert p.spec,'Actual proof manifest is required'
  assert sha(p.path)==timeline['actual_proof_manifest_sha256']
  assert (OUT/'audio/mix.wav').exists(),'Background-only mix required'
  qa=json.loads((OUT/'audio/qa.json').read_text());assert sha(OUT/'audio/mix.wav')==qa['mix_sha256']==timeline['audio_master_sha256'];assert qa['duration_seconds']==56 and not qa['voice_present'] and not qa['voice_generated']
  assert sha(ROOT/p.spec['source_capture_provenance'])==p.spec['source_capture_provenance_sha256']
  assert sha(ROOT/p.spec['download_identity']['path'])==p.spec['download_identity']['sha256']
  for c in p.spec['segments']:
   for s in c['sourceframes']:assert sha(ROOT/s['path'])==s['sha256'],s['path']
 return {'renderer':sha(Path(__file__)),'timeline':sha(SRC/'timeline.json'),'fonts_provenance':sha(SRC/'fonts-provenance.json'),'logo':sha(LOGO_PATH),'landscape_source':sha(ROOT/'projects/sunset/src/app/app/page.tsx')}

def preview():
 p=ActualProof();target=OUT/'composite';target.mkdir(parents=True,exist_ok=True)
 times=[.3,1.2,2.5,3.65,4.4,6.7,9.0,11.8,14.8,18.3,21.5,24.3,27.3,30,33.0,36.5,39,42,45.2,49,53]
 sheet=Image.new('RGB',(480*4,294*math.ceil(len(times)/4)),CREAM);meta=[]
 for i,t in enumerate(times):
  im,recs,ui=scene(t,p);name=f'frame-{round(t*FPS):06d}.png';im.save(target/name)
  sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),((i%4)*480,(i//4)*294));ImageDraw.Draw(sheet).text(((i%4)*480+10,(i//4)*294+274),f'{t:.2f}s',fill=INK)
  meta.append({'time':t,'path':name,'text':recs,'ui':ui})
 sheet.save(target/'contact-sheet.jpg',quality=96)
 (target/'preview.json').write_text(json.dumps({'frames':meta,'source_hashes':validate_sources(),'actual_proof_ready':p.spec is not None},indent=2)+'\n')
 print(json.dumps({'contact_sheet':str(target/'contact-sheet.jpg'),'keyframes':len(times),'actual_proof_ready':p.spec is not None}),flush=True)

def strips():
 p=ActualProof()
 for name,start,end in [('community-handoff',7,12),('key-release',20,24)]:
  times=[start+i/6 for i in range(round((end-start)*6))];sheet=Image.new('RGB',(384*6,238*math.ceil(len(times)/6)),CREAM)
  for i,t in enumerate(times):
   im,_,_=scene(t,p);sheet.paste(im.resize((384,216),Image.Resampling.LANCZOS),((i%6)*384,(i//6)*238));ImageDraw.Draw(sheet).text(((i%6)*384+8,(i//6)*238+219),f'{t:.3f}s',fill=INK)
  sheet.save(OUT/'composite'/f'{name}-strip.jpg',quality=96)
 print('Dense 6fps handoff/release strips ready',flush=True)

def encode(proof_only=False):
 sources=validate_sources(not proof_only);p=ActualProof();duration=8 if proof_only else 56;target=OUT/'render'/('sunset-v9-motion-proof.mp4' if proof_only else 'sunset-launch-v9.mp4')
 target.parent.mkdir(parents=True,exist_ok=True)
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','-']
 if not proof_only:cmd+=['-i',str(OUT/'audio/mix.wav'),'-map','0:v:0','-map','1:a:0']
 cmd+=['-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-preset','medium','-crf','14','-g','60','-threads','4','-color_range','tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
 cmd+=['-an'] if proof_only else ['-c:a','aac','-b:a','320k','-ar','48000']
 cmd+=['-t',str(duration),'-movflags','+faststart',str(target)];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);records=[]
 try:
  for n in range(duration*FPS):
   im,recs,ui=scene(n/FPS,p)
   visible={r['text'] for r in recs}
   for window in read_windows():
    if window['window'][0]-1e-8<=n/FPS<window['window'][1]-1e-8:assert set(window['lines'])<=visible,('Missing promised readable text',n,window['id'],visible)
   proc.stdin.write(im.tobytes());records.append({'frame':n,'time':n/FPS,'text':recs,'actual_recording':ui})
   if n%120==119:print(f'Composed {n+1}/{duration*FPS} native frames',flush=True)
  proc.stdin.close();assert proc.wait()==0
 finally:
  if proc.poll() is None:proc.kill()
 doc={'schema':1,'dimensions':[W,H],'fps':FPS,'duration':duration,'frame_count':duration*FPS,'all_frames':records,'essential_read_windows':read_windows(),'safe_bbox':SAFE,'source_hashes':sources,'actual_recording_frame_uses':p.uses,'method':'Native graphic-depth 2D authored pack/glyph camera-like motion and genuine source-time PNG sample holds; no motion interpolation, fake cursor or generated voice.'}
 (OUT/'composite'/('motion-proof-spec.json' if proof_only else 'readability-spec.json')).write_text(json.dumps(doc,indent=2)+'\n')
 if not proof_only:
  doc={'schema':1,'path':str(target.relative_to(ROOT)),'sha256':sha(target),'bytes':target.stat().st_size,'duration':56,'frames':1680,'dimensions':[W,H],'fps':30,'video_encode_passes':1,'crf':14,'color':'BT.709 limited yuv420p, tagged primaries/trc/matrix','audio_master_sha256':sha(OUT/'audio/mix.wav'),'source_hashes':sources,'actual_demo_manifest':str(p.path.relative_to(ROOT)),'actual_demo_manifest_sha256':sha(p.path),'actual_demo':p.spec,'actual_demo_frame_uses':p.uses,'readability_proof':str((OUT/'composite/readability-spec.json').relative_to(ROOT)),'no_generated_voice':True,'no_music_credit_or_product_url_in_picture':True}
  (OUT/'composite/composite-provenance.json').write_text(json.dumps(doc,indent=2)+'\n')
 print(json.dumps({'path':str(target),'sha256':sha(target),'bytes':target.stat().st_size}),flush=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--preview',action='store_true');ap.add_argument('--proof',action='store_true');ap.add_argument('--render',action='store_true');ap.add_argument('--check',action='store_true');ap.add_argument('--strips',action='store_true');args=ap.parse_args()
 read_windows();validate_sources(args.render)
 if args.check:print(json.dumps({'source_hashes':validate_sources(args.render),'read_windows':read_windows()},indent=2));return
 preview()
 if args.strips:strips()
 if args.proof or args.render:encode(args.proof)
if __name__=='__main__':main()
