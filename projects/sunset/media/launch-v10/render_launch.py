#!/usr/bin/env python3
"""SUNSET v10 editorial motion proof. Whole phrases, real guide substance, no spins.
Full production follows the passed editorial direction and genuine guide-reader footage.
Browser-owner screenshots are interleaved at true elapsed times, not continuous capture.
"""
import argparse,functools,hashlib,json,math,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[4];SRC=Path(__file__).resolve().parent;OUT=ROOT/'.publication/sunset-launch-v10'
W,H,FPS=1920,1080,30
PAPER=(250,247,238);CREAM=(255,243,221);INK=(32,59,54);CORAL=(221,79,43);MINT=(219,232,221);RULE=(168,185,170);PALE=(237,231,215)
FONTS=ROOT/'.publication/sunset-launch-v6/fonts';LOGO_PATH=ROOT/'.publication/sunset-launch-v1/render/logo.png';LOGO=Image.open(LOGO_PATH).convert('RGBA')
PACK_PATH=ROOT/'projects/sunset/public/packs/maintainer-handbook.json'
PACK=json.loads(PACK_PATH.read_text());assert PACK['schema']==2 and PACK['kind']=='guide'
RELEASE=[item['text'] for item in PACK['sections'][0]['checklist']]
CHAPTERS=[section['title'] for section in PACK['sections']]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clamp(x):return max(0.,min(1.,x))
def ease(x):x=clamp(x);return x*x*(3-2*x)
def lerp(a,b,t):return a+(b-a)*t
def rect(im,b,c,r=0,outline=None,width=2):ImageDraw.Draw(im).rounded_rectangle(tuple(round(v) for v in b),r,fill=c,outline=outline,width=width)
def line(im,p,c=INK,width=3):ImageDraw.Draw(im).line([(round(x),round(y)) for x,y in p],fill=c,width=width)
@functools.lru_cache(maxsize=80)
def font(size,body=False,weight=700):
 f=ImageFont.truetype(str(FONTS/('SpaceGrotesk-VF.ttf' if body else 'BricolageGrotesque-VF.ttf')),round(size));f.set_variation_by_axes([min(700,weight)] if body else [96,weight,100]);return f
@functools.lru_cache(maxsize=300)
def word(value,size,col=INK,body=False,weight=700):
 f=font(size,body,weight);b=f.getbbox(value);im=Image.new('RGBA',(b[2]-b[0]+10,b[3]-b[1]+10));ImageDraw.Draw(im).text((5-b[0],5-b[1]),value,font=f,fill=(*col,255));return im
def put(im,tile,x,y,alpha=1):
 if alpha<=0:return
 if alpha<1:tile=tile.copy();tile.putalpha(tile.getchannel('A').point(lambda a:round(a*alpha)))
 im.alpha_composite(tile,(round(x),round(y)))
def text(im,value,x,y,size=42,col=INK,body=False,weight=700):
 tile=word(value,size,col,body,weight);put(im,tile,x,y);return [round(x)+5,round(y)+5,round(x)+tile.width-5,round(y)+tile.height-5]
def wrap(value,size,width,body=True):
 rows=[];row=''
 for item in value.split():
  candidate=(row+' '+item).strip()
  if row and word(candidate,size,INK,body,500).width>width:rows.append(row);row=item
  else:row=candidate
 if row:rows.append(row)
 return rows
def paragraph(im,value,x,y,size=40,width=1000,col=INK,weight=500):
 for row in wrap(value,size,width):text(im,row,x,y,size,col,True,weight);y+=size*1.32
 return y

def phrase(im,rows,x,y,size,dt,recs,bg=PAPER):
 p=ease(dt/.2);alpha=p;dy=(1-p)*24
 for i,row in enumerate(rows):
  tile=word(row,size,INK,False,750);yy=y+i*(size+7)+dy
  rect(im,(x-15,yy-12,x+tile.width+15,yy+tile.height+12),bg)
  put(im,tile,x,yy,alpha)
  if dt>=.2-1e-8:recs.append(record(row,x,yy,size,INK,bg,False,750))

@functools.lru_cache(maxsize=300)
def opaque_core(value,size,col,body,weight):
 a=word(value,size,col,body,weight).getchannel('A').point(lambda v:255 if v==255 else 0)
 for patch in (5,3,1):
  mask=a.filter(ImageFilter.MinFilter(patch)) if patch>1 else a;b=mask.getbbox()
  if not b:continue
  cx,cy=(b[0]+b[2])/2,(b[1]+b[3])/2
  _,x,y=min(((x-cx)**2+(y-cy)**2,x,y) for y in range(b[1],b[3]) for x in range(b[0],b[2]) if mask.getpixel((x,y)))
  return x,y,patch
 raise AssertionError('Opaque glyph core missing')
def ratio(a,b):
 def lum(c):return sum(w*(v/255/12.92 if v/255<=.04045 else ((v/255+.055)/1.055)**2.4) for w,v in zip((.2126,.7152,.0722),c))
 a,b=sorted((lum(a),lum(b)));return (b+.05)/(a+.05)
def record(value,x,y,size,col,bg,body=False,weight=750,kind='essential'):
 tile=word(value,size,col,body,weight);b=tile.getchannel('A').getbbox();gx,gy,patch=opaque_core(value,size,col,body,weight)
 return {'kind':kind,'text':value,'bbox':[round(x)+b[0],round(y)+b[1],round(x)+b[2],round(y)+b[3]],'foreground':col,'background':bg,'probe_foreground_xy':[round(x)+gx,round(y)+gy],'probe_background_xy':[round(x),round(y)],'foreground_opaque_patch_size':patch,'solid_protected':True}
def essential(im,value,x,y,size,recs,bg=PAPER,body=False,weight=750,kind='essential'):
 tile=word(value,size,INK,body,weight);rect(im,(x-14,y-12,x+tile.width+14,y+tile.height+12),bg)
 text(im,value,x,y,size,INK,body,weight);recs.append(record(value,x,y,size,INK,bg,body,weight,kind))
def measure(im,recs,t):
 for r in recs:
  b=r['bbox'];assert 100<=b[0]<b[2]<=1820 and 70<=b[1]<b[3]<=1010,('Unsafe essential type',t,r['text'],b)
  fg=im.getpixel(tuple(r['probe_foreground_xy']))[:3];bg=im.getpixel(tuple(r['probe_background_xy']))[:3];c=ratio(fg,bg);assert c>=4.5,('Contrast',t,r['text'],fg,bg,c)
  r.update(actual_pixel_foreground=fg,actual_pixel_background=bg,contrast=c)
 for i,a in enumerate(recs):
  for b in recs[i+1:]:
   aa,bb=a['bbox'],b['bbox'];assert max(aa[0],bb[0])>=min(aa[2],bb[2]) or max(aa[1],bb[1])>=min(aa[3],bb[3]),('Essential overlap',t,a['text'],b['text'])

def guide_page():
 """Designed manuscript plate, not browser UI; verbatim original handbook copy."""
 im=Image.new('RGBA',(1120,1400),PAPER)
 text(im,'OPEN-SOURCE',55,55,34,CORAL,True)
 text(im,'Maintainer',50,115,86)
 text(im,'Handbook',50,215,86)
 line(im,[(55,350),(1065,350)],RULE,2)
 text(im,'01',55,405,34,CORAL,True)
 paragraph(im,CHAPTERS[0],150,392,49,900,weight=650)
 y=545
 for value in RELEASE:
  rect(im,(62,y+5,87,y+30),None,4,INK,2)
  yy=paragraph(im,value,125,y,41,930);y=yy+36
 line(im,[(55,1260),(1065,1260)],RULE,2)
 text(im,'Original practical guide · CC0',55,1310,29,INK,True,500)
 return im
PAGE=guide_page()

def page(im,x,y,scale=1):
 # The only camera transform is a controlled crop/scale/translation. No rotation.
 tile=PAGE
 if scale!=1:tile=tile.resize((round(tile.width*scale),round(tile.height*scale)),Image.Resampling.LANCZOS)
 rect(im,(x+10,y+13,x+tile.width+10,y+tile.height+13),PALE,10)
 put(im,tile,x,y)

def sunset(im,t):
 # Brief original warm horizon; a page edge then occludes it into the manuscript.
 im.paste(CREAM,(0,0,W,H));r=180;cy=430+100*ease(t/.6)
 ImageDraw.Draw(im).ellipse((1180-r,cy-r,1180+r,cy+r),fill=CORAL)
 rect(im,(0,560,W,H),MINT)
 for i,wide in enumerate((310,235,140)):
  rect(im,(1180-wide/2,600+i*44,1180+wide/2,617+i*44),CORAL,9)

RECOVERY=PACK['sections'][1]
INSPECT='Inspect both its summary and actual changes before choosing it:'
assert INSPECT in RECOVERY['body']
@functools.lru_cache(maxsize=1)
def procedure_plate():
 im=Image.new('RGBA',(1680,700),PAPER)
 text(im,RECOVERY['title'],0,0,65)
 paragraph(im,INSPECT,0,112,48,1630)
 rect(im,(0,295,1680,675),MINT,5)
 text(im,'git show --stat COMMIT_ID',42,345,70,INK,True,500)
 text(im,'git show COMMIT_ID',42,445,66,INK,True,500)
 text(im,'Reference text · not executed',45,605,28,INK,True,500)
 return im

def procedure(im,x,y,scale=1):
 tile=procedure_plate()
 if abs(scale-1)>.001:tile=tile.resize((round(tile.width*scale),round(tile.height*scale)),Image.Resampling.LANCZOS)
 put(im,tile,x,y)

def handbook(im,yshift=0,alpha=1):
 tile=Image.new('RGBA',(W,H),PAPER)
 text(tile,'Open-source Maintainer Handbook',125,105+yshift,70)
 line(tile,[(125,225+yshift),(1795,225+yshift)],RULE,2)
 for i,value in enumerate(CHAPTERS):
  text(tile,f'{i+1:02d}',125,310+i*105+yshift,28,CORAL,True,500)
  paragraph(tile,value,185,305+i*105+yshift,32,375,weight=550)
 procedure(tile,635,300+yshift,.68)
 put(im,tile,0,0,alpha)

def opening(t):
 im=Image.new('RGBA',(W,H),PAPER);recs=[]
 if t<3.3:
  pull=ease((t-2.0)/1.3)
  # Start inside a useful actual procedure, then reveal the work's larger handbook structure.
  if pull>0:
   structure=Image.new('RGBA',(W,H),PAPER)
   text(structure,'Open-source Maintainer Handbook',125,235,46)
   for i,value in enumerate(CHAPTERS):
    text(structure,f'{i+1:02d}',125,360+i*103,28,CORAL,True,500)
    paragraph(structure,value,180,355+i*103,31,355,weight=550)
   put(im,structure,0,0,pull)
  procedure(im,lerp(125,635,pull),lerp(285,350,pull),lerp(1,.68,pull))
  phrase(im,['Good documentation takes work.'],125,95,77,max(0,t-.6),recs)
  if t<.8:
   sun=Image.new('RGBA',(W,H));sunset(sun,t);edge=round(W*ease((t-.45)/.35));im.alpha_composite(sun.crop((edge,0,W,H)),(edge,0))
 elif t<5.7:
  handbook(im,-30*ease((t-3.3)/2.4))
  phrase(im,['Who pays for it?'],125,875,102,t-3.3,recs)
 else:
  q=ease((t-5.7)/.55);promote=ease((t-7.9)/.3)
  manuscript=Image.new('RGBA',(W,H),PAPER);handbook(manuscript,-30)
  put(im,manuscript,-1920*q,0)
  left=lerp(lerp(1920,695,q),0,promote);rect(im,(left,0,W,H),MINT)
  if q>.98:
   xx=lerp(800,125,promote)
   text(im,'Public release agreement',xx,lerp(140,95,promote),round(lerp(39,65,promote)))
   text(im,'Open-source',xx,lerp(250,250,promote),round(lerp(65,76,promote)))
   text(im,'Maintainer Handbook',xx,lerp(335,345,promote),round(lerp(65,76,promote)))
   line(im,[(xx,455),(1770,455)],RULE,2)
   if promote<.99:
    text(im,'ONE GUIDE · ONE PUBLIC RELEASE',xx,535,28,INK,True,500)
   if t>=8.3:
    alpha=ease((t-8.3)/.2);tile=Image.new('RGBA',(1660,145),MINT)
    text(tile,'REVIEWED TERMS',0,0,28,CORAL,True,600);text(tile,'Reviewed before funding.',0,58,52,INK,True,500);put(im,tile,125,540,alpha)
   if t>=8.5-1e-8:recs.append(record('Reviewed before funding.',125,598,52,INK,MINT,True,500,'agreement'))
   if t>=8.65:
    alpha=ease((t-8.65)/.2);tile=Image.new('RGBA',(1660,145),MINT)
    text(tile,'COMMUNITY INTEREST',0,0,28,CORAL,True,600);text(tile,'Community sponsorship.',0,58,52,INK,True,500);put(im,tile,125,785,alpha)
  if t>=8.85-1e-8:recs.append(record('Community sponsorship.',125,843,52,INK,MINT,True,500,'agreement'))
  if t<7.9:phrase(im,['Fund its','public release.'],110,200,84,t-5.7,recs)
  text(im,'PROTOCOL ILLUSTRATION · EXAMPLE RESOURCE',130,1005,22,INK,True,500)
 return im.convert('RGB'),recs

def representative(kind):
 im=Image.new('RGBA',(W,H),PAPER);recs=[]
 if kind=='release':
  # Release changes access: one obscuring paper boundary moves away to reveal the real handbook substance.
  page(im,690,-100,1.0)
  rect(im,(0,0,625,H),MINT)
  phrase(im,['Matching key.','On time.'],75,140,76,1,recs,MINT)
  text(im,'PUBLIC ACCESS',100,615,34,INK,True,600)
  text(im,'Creator credit',100,715,34,INK,True,500)
  text(im,'then withdrawal',100,770,34,INK,True,500)
  text(im,'ILLUSTRATED RELEASE · NO NEW TRANSACTION',90,990,21,INK,True,500)
 else:
  rect(im,(90,90,1830,990),MINT,12)
  text(im,'Keep a usable copy.',150,150,104)
  text(im,'Actual guide-reader recording reserved here',155,320,38,INK,True,500)
  # A literal, useful procedure gives the offline payoff a grown-up subject.
  text(im,'Recover a lost commit',155,470,67)
  y=600
  for value in ['git reflog --date=iso','git show --stat COMMIT_ID','git branch recovered-work COMMIT_ID']:
   text(im,value,165,y,45,INK,True,500);y+=95
 return im.convert('RGB')

READS=[
 ('work',.8,3.3,['Good documentation takes work.']),('need',3.5,5.7,['Who pays for it?']),('public-deal',5.9,7.9,['Fund its','public release.']),
 ('review',8.5,10,['Reviewed before funding.']),('sponsorship',8.85,10,['Community sponsorship.']),
 ('terms',10.2,12.5,['One target.','Clear deadlines.']),('custody',12.7,15,['Funds held on NEAR.']),('matching',15.2,18,['Matching key.','On time.']),
 ('access',18.2,19.8,['Public handbook opens.']),('credit',20,21.6,['Creator credit.']),('withdraw',21.8,24,['Creator can withdraw.']),
 ('refund',24.2,28,['Before release','Target missed? Release late?','Sponsors can claim refunds.']),
 ('actual-copy',28.2,32,['Keep a working handbook.']),('offline',32.2,36,['Works offline.']),('retained',36.2,40,['Keep your copy.','No wallet to read.']),
 ('brand',40.2,44,['SUNSET','Support once. Share forever.'])]
def read_windows():
 import re
 result=[]
 for name,a,b,lines in READS:
  start=math.ceil((a-1e-8)*30)/30;minimum=.3*sum(len(re.findall(r'[A-Za-z]+',v)) for v in lines)+.5
  assert b-start>=minimum-1e-8,(name,b-start,minimum)
  result.append({'id':name,'window':[start,b],'lines':lines,'minimum_read_seconds':minimum})
 return result

class ActualGuide:
 def __init__(self):
  self.path=OUT/'footage/compositor.json';self.spec=json.loads(self.path.read_text()) if self.path.exists() else None;self.uses=[]
 @functools.lru_cache(maxsize=2)
 def source(self,path):return Image.open(ROOT/path).convert('RGBA')
 def panel(self,im,t,box=None,output_time=None):
  if not self.spec:
   rect(im,(125,295,1795,950),MINT,10);text(im,'Actual offline handbook recording pending',175,440,53);text(im,'New guide reader · useful procedure · checklist · reload',175,550,35,INK,True,500)
   return None
  c=next((v for v in self.spec['segments'] if v['start']<=t<v['end']),self.spec['segments'][-1]);frames=c['sourceframes'];n=max([i for i,f in enumerate(frames) if f['film_time']<=t]+[0]);f=frames[n]
  raw=self.source(f['path']);assert list(raw.size)==c['source_dimensions'];crop=f.get('crop',c['crop']);tile=raw.crop(tuple(crop));box=box or c.get('display_bbox',[125,285,1795,950]);maximum=c.get('max_editorial_scale',1)
  scale=min(maximum,(box[2]-box[0])/tile.width,(box[3]-box[1])/tile.height);size=[round(tile.width*scale),round(tile.height*scale)];tile=tile.resize(tuple(size),Image.Resampling.LANCZOS);x=round((box[0]+box[2]-tile.width)/2);y=round((box[1]+box[3]-tile.height)/2)
  rect(im,(x-3,y-3,x+tile.width+3,y+tile.height+3),INK,6);put(im,tile,x,y)
  use={'kind':'actual_recording','clip':c['id'],'film_time':t if output_time is None else output_time,'mapped_source_time':t-c.get('playbackstart',c['start']),'source_sample_film_time':f['film_time'],'source_capture_time':f['time'],'source_path':f['path'],'source_sha256':f['sha256'],'source_dimensions':list(raw.size),'source_sample':n,'effective_roi':crop,'crop':crop,'scale':scale,'editorial_magnification':scale>1,'resampling':'LANCZOS','display_bbox':[x,y,x+tile.width,y+tile.height],'source_context':c.get('context','app_download' if 'download' in c['id'] and 'offline' not in c['id'] else 'guide_file'),'network_offline_verified':bool(c.get('network_offline_verified',False)),'sampling':'Native browser-owner screenshots interleaved with real input at true elapsed times, held honestly; not continuous full-rate recording. Editorial geometric reframing only; no invented UI, cursor or source motion.'}
  if output_time is not None:use['endpoint_freeze']='Final genuine offline result held as retained copy; mapped playback time and actual capture identity kept separate.'
  self.uses.append(use);return use

def full_frame(t,actual):
 if t<10:
  base,recs=opening(t);im=base.convert('RGBA');measure(im,recs,t);return base,recs,None
 im=Image.new('RGBA',(W,H),PAPER);recs=[];ui=None
 if t<12.5:
  dt=t-10;rect(im,(0,0,W,H),MINT);phrase(im,['One target.','Clear deadlines.'],125,100,112,dt,recs,MINT)
  # Terms are an empty agreed target and two distinct dates, never premature money.
  rect(im,(125,520,1795,690),PAPER,9);text(im,'FUNDING TARGET',160,555,29,CORAL,True,600);text(im,'One agreed cap',160,605,52,INK,True,500)
  line(im,[(125,775),(1795,775)],RULE,2)
  text(im,'FUND BY',125,830,29,CORAL,True,600);text(im,'Funding deadline',125,880,47,INK,True,500)
  text(im,'RELEASE BY',1030,830,29,CORAL,True,600);text(im,'Release deadline',1030,880,47,INK,True,500)
 elif t<15:
  dt=t-12.5;phrase(im,['Funds held on NEAR.'],125,105,105,dt,recs)
  text(im,'NEAR ESCROW',125,325,38,CORAL,True,600);line(im,[(125,395),(1795,395)],RULE,2)
  # Causal accounting entries reveal in place and fill only within the agreed cap.
  for i,value in enumerate(['Community contribution','Community contribution','Community contribution']):
   p=ease((dt-.3-i*.4)/.28);yy=450+i*115
   if p>0:
    row=Image.new('RGBA',(1670,95),MINT);text(row,value,35,25,42,INK,True,500);put(im,row,125,yy,p)
  fill=ease((dt-.55)/1.5);rect(im,(125,865,1795,910),PALE,6);rect(im,(125,865,125+1670*fill,910),INK,6);line(im,[(1795,835),(1795,935)],CORAL,5)
  text(im,'HELD FOR THE AGREED RELEASE · CAPPED AT THE TARGET',125,965,26,INK,True,500)
 elif t<18:
  dt=t-15;phrase(im,['Matching key.','On time.'],125,100,112,dt,recs)
  text(im,'COMMITTED KEY FINGERPRINT',125,470,29,CORAL,True,600);text(im,'PUBLISHED KEY FINGERPRINT',125,695,29,CORAL,True,600)
  for row,yy in enumerate((545,770)):
   progress=1 if row==0 else ease((dt-.35)/.7)
   for i,h in enumerate([38,65,47,76,34,55,75,45,65,40,70,52,38,77,50,65]):
    if i<round(16*progress):rect(im,(125+i*78,yy-h/2,166+i*78,yy+h/2),INK,2)
  if dt>=1.1:text(im,'Matches the commitment · before the release deadline',125,920,42,INK,True,500)
  # A straight access boundary, tied to matching, is removed into the open handbook.
  if dt>2.55:
   q=ease((dt-2.55)/.45);rect(im,(1920-1920*q,0,W,H),MINT)
   recs.clear();phrase(im,['Matching key.','On time.'],125,100,112,dt,recs)
 elif t<19.8:
  dt=t-18;phrase(im,['Public handbook opens.'],125,100,99,dt,recs)
  text(im,CHAPTERS[0],125,335,70)
  excerpt=PACK['sections'][0]['body'].split('\n\n')[0]
  paragraph(im,excerpt,125,475,43,1650)
  line(im,[(125,920),(1795,920)],RULE,2);text(im,'OPEN-SOURCE MAINTAINER HANDBOOK · ORIGINAL CC0 EXAMPLE',125,965,26,INK,True,500)
 elif t<21.6:
  dt=t-19.8;phrase(im,['Creator credit.'],125,110,128,dt,recs)
  q=ease(dt/.28);yy=lerp(1040,455,q);rect(im,(125,yy,1795,yy+320),MINT,8)
  text(im,'RELEASE CONDITIONS MET',165,yy+45,29,CORAL,True,600);text(im,'Agreed creator payment',165,yy+120,72,INK,True,500);text(im,'Available to withdraw',165,yy+240,42,INK,True,500)
 elif t<24:
  dt=t-21.6;phrase(im,['Creator can withdraw.'],125,110,110,dt,recs)
  text(im,'SEPARATE WITHDRAWAL ACTION',125,345,32,CORAL,True,600)
  rect(im,(125,455,1795,845),MINT,8);line(im,[(960,455),(960,845)],RULE,2)
  text(im,'CREATOR CREDIT',165,500,29,INK,True,600);text(im,'CREATOR ACCOUNT',1020,500,29,INK,True,600)
  q=ease((dt-.4)/1.2);xx=lerp(165,1020,q);rect(im,(xx,600,xx+680,755),PAPER,8);text(im,'Agreed payment',xx+30,650,57,INK,True,500)
 elif t<28:
  dt=t-24;line(im,[(125,95),(1795,95)],CORAL,5)
  if dt>=.2-1e-8:
   essential(im,'Before release',125,145,64,recs)
   essential(im,'Target missed? Release late?',125,375,83,recs)
   essential(im,'Sponsors can claim refunds.',125,670,88,recs)
  else:phrase(im,['Before release'],125,145,64,dt,recs)
  text(im,'ALTERNATIVE OUTCOME · THE PRE-RELEASE AGREEMENT',125,980,27,INK,True,500)
 elif t<36:
  ui=actual.panel(im,t)
  if t<32:phrase(im,['Keep a working handbook.'],125,105,84,t-28,recs)
  else:phrase(im,['Works offline.'],125,105,95,t-32,recs)
  caption='ACTUAL APP DOWNLOAD' if ui and ui['source_context']=='app_download' else 'ACTUAL DOWNLOADED GUIDE'
  if ui and ui['network_offline_verified']:caption+=' · BROWSER NETWORKING DISABLED'
  text(im,caption,125,995,24,INK,True,500)
 elif t<40:
  dt=t-36
  # The host's outline leaves behind the retained genuine file, not an illustrated replacement.
  q=ease(dt/.7);x=125+1800*q;rect(im,(x,280,x+1670,950),None,9,RULE,3)
  ui=actual.panel(im,35.9666666667,[125,300,1795,995],output_time=t)
  phrase(im,['Keep your copy.','No wallet to read.'],125,95,84,dt,recs)
 else:
  dt=t-40;q=ease(dt/.2);logo=LOGO.resize((250,250),Image.Resampling.LANCZOS);put(im,logo,835,200,q)
  if dt>=.2-1e-8:
   value='SUNSET';tile=word(value,185);essential(im,value,(W-tile.width)/2,510,185,recs,kind='brand')
   value='Support once. Share forever.';tile=word(value,62,INK,True,600);essential(im,value,(W-tile.width)/2,765,62,recs,body=True,weight=600,kind='tagline')
 if 10<=t<28:text(im,'PROTOCOL ILLUSTRATION · EXAMPLE RESOURCE',125,1032,20,INK,True,500)
 measure(im,recs,t);return im.convert('RGB'),recs,ui

def source_guards(final=False):
 fonts=json.loads((SRC/'fonts-provenance.json').read_text())
 for family in fonts['fonts']:
  for asset in family['files'].values():assert sha(ROOT/asset['path'])==asset['sha256']
 timeline=json.loads((SRC/'timeline.json').read_text());assert timeline['proposed_full_duration']==44;assert timeline['guide_sha256']==sha(PACK_PATH)
 assert timeline['font_provenance_sha256']==sha(SRC/'fonts-provenance.json') and timeline['logo_sha256']==sha(LOGO_PATH)
 assert timeline['essential_read_windows']==read_windows()
 assert timeline['sound_cues_sha256']==sha(SRC/'sound-cues.json')
 hashes={'renderer':sha(Path(__file__)),'timeline':sha(SRC/'timeline.json'),'fonts_provenance':sha(SRC/'fonts-provenance.json'),'guide_pack':sha(PACK_PATH),'logo':sha(LOGO_PATH)}
 if final:
  actual=ActualGuide();assert actual.spec,'Genuine new guide recording required before final encode'
  capture=OUT/'footage/capture-provenance.json';assert capture.exists(),'Passed capture provenance required'
  assert sha(capture)==timeline['capture_provenance_sha256']
  hashes['capture_provenance']=sha(capture)
  for clip in actual.spec['segments']:
   assert clip.get('context') in ('app_download','guide_file')
   assert isinstance(clip.get('network_offline_verified'),bool)
   if clip['start']<36 and clip['end']>32:assert clip['context']=='guide_file' and clip['network_offline_verified'] is True,'Offline claim requires verified file context'
   for f in clip['sourceframes']:assert sha(ROOT/f['path'])==f['sha256']
  assert sha(actual.path)==timeline['actual_manifest_sha256']
  if 'download_identity' in actual.spec:
   downloaded=actual.spec['download_identity'];assert sha(ROOT/downloaded['path'])==downloaded['sha256']
  qa=json.loads((OUT/'audio/qa.json').read_text());assert qa['duration_seconds']==44 and not qa['voice_present'] and not qa['voice_generated'];assert sha(OUT/'audio/mix.wav')==qa['mix_sha256']==timeline['audio_master_sha256']
  hashes['audio_master']=qa['mix_sha256'];hashes['actual_manifest']=sha(actual.path)
 return hashes

def preview_full():
 actual=ActualGuide();times=[.9,2.8,4.5,6.5,8.6,9.7,10.8,13.6,16.4,18.8,20.6,22.8,25.8,29.5,33.5,35.7,37.3,42]
 sheet=Image.new('RGB',(1920,294*math.ceil(len(times)/4)),PAPER);records=[]
 for i,t in enumerate(times):
  im,recs,ui=full_frame(t,actual);name=f'full-{round(t*30):06d}.png';im.save(OUT/'composite'/name);sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),((i%4)*480,(i//4)*294));ImageDraw.Draw(sheet).text(((i%4)*480+8,(i//4)*294+274),f'{t:.2f}s',fill=INK);records.append({'time':t,'path':name,'text':recs,'actual_ui':ui})
 sheet.save(OUT/'composite/full-contact-sheet.jpg',quality=96)
 (OUT/'composite/full-preview.json').write_text(json.dumps({'source_hashes':source_guards(),'frames':records,'essential_read_windows':read_windows(),'actual_recording_ready':actual.spec is not None},indent=2)+'\n');print('Full direction critical frames ready; actual recording ready='+str(actual.spec is not None),flush=True)

def encode_full():
 hashes=source_guards(True);actual=ActualGuide();target=OUT/'render/sunset-launch-v10.mp4';records=[]
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','-','-i',str(OUT/'audio/mix.wav'),'-map','0:v:0','-map','1:a:0','-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-preset','medium','-crf','14','-g','60','-threads','4','-color_range','tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','aac','-b:a','320k','-ar','48000','-t','44','-movflags','+faststart',str(target)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for n in range(1320):
   t=n/30;im,recs,ui=full_frame(t,actual);visible={r['text'] for r in recs}
   for w in read_windows():
    if w['window'][0]-1e-8<=t<w['window'][1]-1e-8:assert set(w['lines'])<=visible,('Missing promised read',n,w['id'],visible)
   proc.stdin.write(im.tobytes());records.append({'frame':n,'time':t,'text':recs,'actual_recording':ui})
   if n%120==119:print(f'Composed {n+1}/1320 native v10 frames',flush=True)
  proc.stdin.close();assert proc.wait()==0
 finally:
  if proc.poll() is None:proc.kill()
 spec={'schema':1,'dimensions':[W,H],'fps':30,'duration':44,'frame_count':1320,'safe_bbox':[100,70,1820,1010],'all_frames':records,'essential_read_windows':read_windows(),'source_hashes':hashes,'actual_recording_frame_uses':actual.uses,'method':'Native professional editorial2D: whole phrases, useful handbook content, meaningful page/camera transformations and genuine timestamped browser PNG holds. No invented UI/cursor/source motion, generated voice, spins or scattered letters.'}
 (OUT/'composite/readability-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
 provenance={'schema':1,'path':str(target.relative_to(ROOT)),'sha256':sha(target),'bytes':target.stat().st_size,'duration':44,'frames':1320,'dimensions':[W,H],'fps':30,'video_encode_passes':1,'crf':14,'color':'BT.709 limited yuv420p; matrix/trc/primaries tagged','source_hashes':hashes,'audio_master_sha256':sha(OUT/'audio/mix.wav'),'actual_demo_manifest':str(actual.path.relative_to(ROOT)),'actual_demo_manifest_sha256':sha(actual.path),'actual_demo':actual.spec,'actual_demo_frame_uses':actual.uses,'readability_proof':str((OUT/'composite/readability-spec.json').relative_to(ROOT)),'no_generated_voice':True,'no_product_url_or_music_credit_in_picture':True}
 (OUT/'composite/composite-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n');print(json.dumps({'path':str(target),'sha256':sha(target),'bytes':target.stat().st_size}),flush=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--proof',action='store_true');ap.add_argument('--full-preview',action='store_true');ap.add_argument('--render',action='store_true');ap.add_argument('--check',action='store_true');args=ap.parse_args();(OUT/'composite').mkdir(parents=True,exist_ok=True)
 if args.check:print(json.dumps({'source_hashes':source_guards(),'read_windows':read_windows()},indent=2));return
 if args.full_preview or args.render:
  preview_full()
  if args.render:encode_full()
  return
 times=[.25,.9,2.6,3.8,5.4,6.4,8.5,9.7];sheet=Image.new('RGB',(480*4,294*3),PAPER);records=[]
 for i,t in enumerate(times):
  im,recs=opening(t);im.save(OUT/'composite'/f'opening-{round(t*30):06d}.png');sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),((i%4)*480,(i//4)*294));ImageDraw.Draw(sheet).text(((i%4)*480+8,(i//4)*294+275),f'{t:.2f}s',fill=INK);records.append({'time':t,'text':recs})
 for i,kind in enumerate(['release','offline']):
  im=representative(kind);im.save(OUT/'composite'/f'{kind}-direction.png');sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),(i*480,588))
 sheet.save(OUT/'composite/contact-sheet.jpg',quality=96)
 (OUT/'composite/proof-direction.json').write_text(json.dumps({'status':'Preview gate only. No full film exists.','duration':10,'dimensions':[W,H],'fps':FPS,'renderer_sha256':sha(Path(__file__)),'actual_content_copy':{'chapters':CHAPTERS,'release_checklist':RELEASE,'path':str(PACK_PATH.relative_to(ROOT)),'sha256':sha(PACK_PATH),'author':'Original CC0 handbook pack; visible release checklist read directly from source JSON'},'motion':'Full-frame actual recovery excerpt, meaningful handbook pullback, page-edge handoff and full-frame agreement row reveal; only crop/translation/scale and200ms whole-phrase arrival. No spinning, scattered letters, hopping tokens, child worksheets or decorative loops.','preview_frames':records},indent=2)+'\n')
 if args.proof:
  target=OUT/'render/sunset-v10-opening-proof.mp4';audio=OUT/'audio/proof-mix.wav';cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','-']
  if audio.exists():cmd+=['-i',str(audio),'-map','0:v:0','-map','1:a:0']
  cmd+=['-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-preset','medium','-crf','14','-threads','4','-color_range','tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
  cmd+=['-c:a','aac','-b:a','320k','-ar','48000'] if audio.exists() else ['-an']
  cmd+=['-t','10','-movflags','+faststart',str(target)];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
  for n in range(300):im,_=opening(n/30);proc.stdin.write(im.tobytes())
  proc.stdin.close();assert proc.wait()==0;print(json.dumps({'path':str(target),'sha256':sha(target),'bytes':target.stat().st_size}),flush=True)
 else:print('V10 preview keyframes ready; full film rendering is intentionally unavailable until preview approval.',flush=True)
if __name__=='__main__':main()
