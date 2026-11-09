#!/usr/bin/env python3
"""Narration-led SUNSET film. Native render; Bang-adapted browser source is separate."""
import argparse
from functools import lru_cache
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image,ImageDraw

SOURCE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('kinetic',SOURCE.parent/'launch-v21/produce.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
ROOT,MASTER=old.ROOT,old.MASTER
OUT=ROOT/'.publication/sunset-launch-v22'
W,H,FPS=1920,1080,30
text,font,sha,ease,smooth,sheet=old.text,old.font,old.sha,old.ease,old.smooth,old.sheet
PAPER,INK,CORAL=old.PAPER,old.INK,old.CORAL


def timeline():
    config=json.loads((SOURCE/'narration.json').read_text())
    takes=json.loads((OUT/'voice/takes.json').read_text())
    assert takes['voice']=='af_bella' and takes['synthetic']
    phases=[{'id':'intro','start':0,'end':1.8,'frames':54}];cursor=54
    mapping=[{'frame':n,'source':'v19','source_frame':n,'phase':'intro'} for n in range(54)]
    for line,take in zip(config['lines'],takes['takes'],strict=True):
        if line['id']=='closing':
            phases.append({'id':'payoff','start':cursor/FPS,'end':(cursor+72)/FPS,'frames':72})
            mapping.extend({'frame':cursor+n,'source':'payoff','phase':'payoff','scene_frame':n} for n in range(72));cursor+=72
        duration=max(line['min_seconds'],take['duration']+.40)
        count=math.ceil(duration*FPS)
        lead=.12 if line['id']!='closing' else .30
        assert lead+take['duration']<=count/FPS
        phase={'id':line['id'],'start':cursor/FPS,'end':(cursor+count)/FPS,'frames':count,
               'voice_start':cursor/FPS+lead,'voice_end':cursor/FPS+lead+take['duration'],
               'spoken':line['spoken'],'take':f'voice/{take["index"]:02}-{take["id"]}.wav','take_sha256':take['sha256']}
        phases.append(phase)
        spans={'sponsor':(210,276),'custody':(276,360),'release':(360,429),'claim':(429,492),'closing':(780,885)}
        if line['id'] in spans:
            first,last=spans[line['id']];sequence=list(range(first,last));extra=count-len(sequence)
            assert extra>=0,(line['id'],count)
            if line['id']=='release':
                seat=min(21,extra);position=sequence.index(375)+1
                sequence[position:position]=[375]*seat
                sequence.extend([428]*(extra-seat))
            else:
                at={'sponsor':252,'custody':330,'claim':488,'closing':884}[line['id']]
                position=sequence.index(at)+1;sequence[position:position]=[at]*extra
            assert len(sequence)==count
            mapping.extend({'frame':cursor+n,'source':'v19','source_frame':f,'phase':line['id']} for n,f in enumerate(sequence))
        else:
            mapping.extend({'frame':cursor+n,'source':line['id'],'phase':line['id'],'scene_frame':n} for n in range(count))
        cursor+=count
    assert [r['frame'] for r in mapping]==list(range(cursor))
    result={'fps':FPS,'frames':cursor,'duration':cursor/FPS,'phases':phases,'synthetic_voice':takes['voice']}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'timeline.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'frame-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
    return result,mapping


@lru_cache(maxsize=1)
def art():
    pages,portrait,draft,hands,edge,room=old.artwork()
    pack=json.loads((ROOT/'projects/sunset/public/packs/workshop-kit.json').read_text())
    assert pack['id']=='workshop-kit' and pack['license']=='CC0-1.0'
    body=next(s['body'] for s in pack['sections'] if s['id']=='session')
    for span in ['00–05','05–15','15–30','30–40','40–45']:assert span in body
    cover=Image.new('RGBA',(920,1200),'#f4edda');d=ImageDraw.Draw(cover)
    d.rectangle((0,0,920,40),fill=CORAL)
    text(cover,(70,90),'A COMMUNITY WORKSHOP',40)
    text(cover,(70,180),'Skill swap',104)
    text(cover,(70,310),'Workshop kit',98)
    d.ellipse((200,510,720,1030),fill='#e6b83b')
    text(cover,(460,610),'45',190,anchor='mt');text(cover,(460,835),'MINUTES',52,anchor='mt')
    text(cover,(70,1115),pack['title'],37)
    agenda=Image.new('RGBA',(1020,1200),'#fffdf7');d=ImageDraw.Draw(agenda)
    text(agenda,(70,70),'Run the workshop',78)
    text(agenda,(70,190),'Five steps. One useful skill.',45,'#526b58')
    rows=[('00–05','Welcome'),('05–15','Demonstrate'),('15–30','Practise in pairs'),('30–40','Teach it back'),('40–45','Choose a next step')]
    for i,(stamp,label) in enumerate(rows):
        y=325+i*150;d.line((70,y+107,950,y+107),fill='#d5dfca',width=3)
        text(agenda,(70,y),stamp,52,CORAL);text(agenda,(330,y),label,52)
    proof_data=json.loads((ROOT/'projects/sunset/evidence/testnet-showcase.json').read_text())
    browser=json.loads((ROOT/'projects/sunset/evidence/browser-showcase.json').read_text())
    assert proof_data['native_creator_transfer']['amount_yocto']=='100000000000000000000000'
    assert proof_data['final_state']['creator_account']['pending'] is None
    assert browser['offline']['network_disable_scope'].startswith('Chrome DevTools offline')
    receipt=Image.new('RGBA',(1180,1000),'#fffdf7');d=ImageDraw.Draw(receipt)
    text(receipt,(70,75),'RECORDED NEAR TESTNET',42,'#536759')
    text(receipt,(70,185),'Creator payout',88)
    text(receipt,(70,310),'0.1 testNEAR',112)
    d.line((70,495,1110,495),fill='#cbd5c0',width=3)
    text(receipt,(70,555),'Offline reader checked',67)
    text(receipt,(70,695),'Lantern Trail · 2 November 2026',43)
    text(receipt,(70,800),'Recorded run · one operator',42,'#536759')
    refund=Image.new('RGBA',(1050,920),'#fffdf7');d=ImageDraw.Draw(refund)
    text(refund,(65,70),'SPONSOR REFUND',43,'#536759')
    text(refund,(65,190),'Claimable',112)
    d.line((65,380,985,380),fill='#ced8c1',width=3)
    text(refund,(65,455),'Conditions missed',66)
    text(refund,(65,580),'A separate refund claim',51)
    text(refund,(65,665),'and withdrawal follow',51)
    return {'creator':portrait,'hands':hands,'kit-cover':cover,'kit-agenda':agenda,'refund':refund,'proof':receipt,
            'room':room,'draft':draft,'edge':edge}


def caption(frame,lines,top=90,size=108):
    d=ImageDraw.Draw(frame)
    for i,line in enumerate(lines):
        y=top+i*(size+25);width=round(d.textlength(line,font=font(size)))
        d.rectangle((82,y-8,128+width,y+size+22),fill=INK)
        text(frame,(106,y),line,size,'#f6efdf')


def maker(t,duration,next_work=False):
    a=art();p=smooth(t/duration);travel=190*p if not next_work else 1500*smooth((t-.6)/max(duration-.6,.1))
    push=120*math.sin(math.pi*p)+240*(smooth((t-.8)/.5)-smooth((t-1.6)/.5))
    camera=(960+travel,540+40*p,push)
    frame=a['room'].crop((90-round(60*p),0,2010-round(60*p),1080))
    if next_work:
        for i in [2,1,0]:
            sheet(frame,a['kit-cover'],(2300+i*400,690+(i%2)*90,250+i*140),(560,730),camera,ry=[-12,14,-7][i],rz=[10,-8,5][i])
    sheet(frame,a['creator'],(1370,625,110),(620,745),camera,ry=15-23*ease(t/.8),rz=-5)
    sheet(frame,a['draft'],(540,850,20),(800,1000),camera,ry=8,rz=3)
    sheet(frame,a['kit-cover'],(730,790,-80),(590,770),camera,ry=-12,rz=5)
    sheet(frame,a['hands'],(480,1010,-220),(1250,833),camera,ry=-5,rz=-3)
    if next_work:sheet(frame,a['edge'],(2100,700,-470),(140,1400),camera,ry=-12,rz=9)
    caption(frame,['Make the next','free thing possible.'] if next_work else ['Help creators make','useful work free.'],size=108)
    return frame


def kit_world(t,duration,using=False):
    a=art();p=t/duration
    frame=Image.new('RGB',(W,H),PAPER)
    camera=(960+95*smooth(p),540,80+140*math.sin(math.pi*p))
    for i in [2,1,0]:
        arrive=ease((t-.1-i*.12)/.6)
        sheet(frame,a['kit-cover'],(530+(i-1)*(100+50*p)+700*(1-arrive),690+(i-1)*50,300+i*130),
              (630,820),camera,ry=(i-1)*12,rz=(i-1)*(8+5*p))
    sheet(frame,a['kit-agenda'],(1390,600,0),(700,825),camera,ry=-7+5*p,rz=3-3*p)
    caption(frame,['Use it. Share it. Offline.'] if using else ['A useful workshop.','Ready to share.'],size=104)
    # World labels are factual descriptions of this newly built local example.
    d=ImageDraw.Draw(frame);d.rectangle((70,985,1000,1080),fill=PAPER)
    text(frame,(108,1000),'Workshop kit · local example',39,'#46634e')
    return frame


def refund_world(t,duration):
    a=art();frame=Image.new('RGB',(W,H),PAPER);p=t/duration
    d=ImageDraw.Draw(frame)
    # The fork makes this a separate outcome, never a refund after successful payment.
    d.line([(600,690),(980,690),(1120,510)],fill='#7a9274',width=15)
    d.line([(980,690),(1120,850)],fill=CORAL,width=18)
    sheet(frame,a['kit-cover'],(520,720,220),(480,630),(960,540,60),ry=-14,rz=-6)
    sheet(frame,a['refund'],(1390,730,30),(850,745),(960,540,50+60*math.sin(math.pi*p)),ry=7-7*ease(t/.7),rz=0)
    text(frame,(108,76),'Alternative outcome',53,CORAL)
    caption(frame,['Missed conditions.','Refunds claimable.'],top=155,size=96)
    text(frame,(108,1005),'Protocol illustration · no new transaction',35,'#46634e')
    return frame


def proof_world(t,duration):
    a=art();frame=Image.new('RGB',(W,H),PAPER);p=t/duration
    sheet(frame,a['proof'],(1125,620,0),(1000,850),(960,540,70*math.sin(math.pi*p)),ry=9-9*ease(t/.8),rz=-2)
    caption(frame,['Core flow, verified.'],size=105)
    return frame


def picture(phase,t):
    duration=phase['end']-phase['start'];kind=phase['id']
    if kind in ['why','next']:return maker(t,duration,kind=='next')
    if kind in ['kit','use']:return kit_world(t,duration,kind=='use')
    if kind=='refund':return refund_world(t,duration)
    if kind=='proof':return proof_world(t,duration)
    if kind=='payoff':return old.payoff(t)
    raise ValueError(kind)


def assets():
    target=OUT/'browser/assets';target.mkdir(parents=True,exist_ok=True)
    for name,image in art().items():image.save(target/(name+'.png'))
    for name,path in {'original-logo.svg':ROOT/'projects/sunset/public/icon.svg',
                      'geist.woff2':ROOT/'projects/sunset/public/fonts/geist-latin-variable.woff2',
                      'gsap.min.js':ROOT/'.publication/sunset-launch-v16/toolchain/node_modules/gsap/dist/gsap.min.js',
                      'master.mp4':MASTER}.items():
        if not (target/name).exists():shutil.copyfile(path,target/name)


def render():
    tl,mapping=timeline();phases={p['id']:p for p in tl['phases']}
    movie=OUT/'sunset-launch-v22.mp4';raw=OUT/'picture-before-colour-tags.mp4'
    assert not movie.exists() and not raw.exists()
    assert (OUT/'audio/mix.wav').exists()
    decoder=subprocess.Popen(['ffmpeg','-v','error','-i',str(MASTER),'-an','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
    with (OUT/'render.log').open('x') as log:
        encoder=subprocess.Popen(['ffmpeg','-v','warning','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-',
            '-i',str(OUT/'audio/mix.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-preset','medium','-crf','15','-pix_fmt','yuv420p',
            '-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709','-c:a','aac','-b:a','320k','-ar','48000','-ac','2',
            '-movflags','+faststart','-t',str(tl['duration']),str(raw)],stdin=subprocess.PIPE,stderr=log)
        source_n=-1
        try:
            for item in mapping:
                if item['source']=='v19':
                    while source_n<item['source_frame']:
                        data=decoder.stdout.read(W*H*3);assert len(data)==W*H*3;source_n+=1
                    image=Image.frombytes('RGB',(W,H),data)
                else:image=picture(phases[item['phase']],item['scene_frame']/FPS)
                encoder.stdin.write(image.tobytes())
                if item['frame']%180==0:print(f"Rendered {item['frame']}/{len(mapping)}",flush=True)
            encoder.stdin.close();assert encoder.wait()==0 and decoder.wait()==0
        finally:
            for process in [decoder,encoder]:
                if process.poll() is None:process.terminate();process.wait()
    old.base.tag_colour(raw,movie)
    source_files=[*SOURCE.glob('*.py'),SOURCE/'narration.json',SOURCE.parent/'launch-v21/produce.py',SOURCE.parent/'launch-v20/finish.py',
        ROOT/'projects/sunset/public/packs/workshop-kit.json',ROOT/'projects/sunset/public/try-workshop-kit.html',
        ROOT/'projects/sunset/evidence/testnet-showcase.json',ROOT/'projects/sunset/evidence/browser-showcase.json',ROOT/'projects/sunset/evidence/testnet-refunds.json']
    (OUT/'source-manifest.json').write_text(json.dumps({'sources':{str(p.relative_to(ROOT)):sha(p) for p in source_files},
        'master_sha256':sha(MASTER),'timeline_sha256':sha(OUT/'timeline.json'),'audio_sha256':sha(OUT/'audio/mix.wav'),
        'native_renderer':True,'browser_rendered':False},indent=2)+'\n')
    print(movie)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['prepare','stills','render']);args=parser.parse_args()
    tl,_=timeline()
    if args.command=='prepare':assets();print(json.dumps(tl));return
    if args.command=='stills':
        for p in tl['phases']:
            if p['id'] in ['intro','sponsor','custody','release','claim','closing']:continue
            image=picture(p,min(1.5,(p['end']-p['start'])/2));image.save(OUT/(p['id']+'.png'))
            image.resize((390,219),Image.Resampling.LANCZOS).save(OUT/(p['id']+'-390.png'))
        print(OUT);return
    render()


if __name__=='__main__':
    if sys.flags.optimize:raise SystemExit('Run without Python optimization.')
    main()
