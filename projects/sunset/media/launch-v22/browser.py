#!/usr/bin/env python3
"""Generate the optional, editable Bang-adapted SUNSET V22 browser companion.

This is a separate composition, not the MP4 renderer or a pixel-matched player.
Chrome could not launch in the production sandbox; generated-source checks do
not establish browser playback, camera geometry or perceptual audio quality.

Run after timeline.json, frame-map.json and browser/assets have been prepared:
    python3 projects/sunset/media/launch-v22/browser.py
    python3 projects/sunset/media/launch-v22/browser.py --check
The self-check uses synthetic metadata and Node syntax/mapping checks only:
    python3 projects/sunset/media/launch-v22/browser.py --self-check

Shared-world/camera/OPENER architecture adapted from Bang Motion v1.19.0,
c1aa65e921c970d858705fcb4a53a8294d1a4131; preserve BANG_LICENSE.txt.
https://github.com/bangtutorial/bang-motion
"""

import argparse
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import subprocess


SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parents[3]
OUT = ROOT / '.publication/sunset-launch-v22/browser'
IDS = ('intro', 'why', 'kit', 'sponsor', 'custody', 'release', 'claim',
       'refund', 'use', 'proof', 'next', 'payoff', 'closing')
FINANCE = {'sponsor', 'custody', 'release', 'claim'}
ASSETS = ('creator.png', 'hands.png', 'kit-cover.png', 'kit-agenda.png',
          'refund.png', 'proof.png', 'original-logo.svg', 'geist.woff2',
          'gsap.min.js', 'master.mp4', 'audio.m4a')


def validated(timeline, frames):
    """Reject incomplete clocks and any loss of the reviewed finance mapping."""
    if timeline.get('fps') != 30:
        raise ValueError('The reviewed source and output clocks are both 30 fps.')
    duration = timeline.get('duration')
    if not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0:
        raise ValueError('duration must be finite and positive')
    phases = timeline.get('phases', [])
    if [p.get('id') for p in phases] != list(IDS):
        raise ValueError('Expected all thirteen ordered V22 phase IDs')
    previous = 0.0
    for phase in phases:
        a, b = phase['start'], phase['end']
        if not all(isinstance(n, (int, float)) and math.isfinite(n) for n in (a, b)):
            raise ValueError('Phase boundaries must be finite numbers')
        if abs(a - previous) > 1e-6 or b <= a:
            raise ValueError('Phases must be contiguous, positive intervals')
        for key in ('voice_start', 'voice_end'):
            if key in phase and not a <= phase[key] <= b:
                raise ValueError(f'{key} must lie inside {phase["id"]}')
        previous = b
    if abs(previous - duration) > 1e-6:
        raise ValueError('The last phase must end at duration')
    count = math.ceil(duration * 30 - 1e-7)
    if len(frames) != count or [r.get('frame') for r in frames] != list(range(count)):
        raise ValueError('frame-map must contain every output frame once, in order')
    phase_index = 0
    for record in frames:
        t = record['frame'] / 30
        while phase_index < len(phases) - 1 and t >= phases[phase_index]['end'] - 1e-8:
            phase_index += 1
        source = record.get('source')
        if source not in (*IDS, 'v19'):
            raise ValueError(f'Unknown frame source: {source}')
        if source == 'v19':
            sf = record.get('source_frame')
            if type(sf) is not int or sf < 0:
                raise ValueError('v19 frames need a non-negative integer source_frame')
        if phases[phase_index]['id'] in FINANCE and source != 'v19':
            raise ValueError('All finance frames must retain reviewed v19 source frames')
    return {'fps': 30, 'duration': duration, 'phases': phases, 'frameMap': frames}


HTML = r'''<!doctype html>
<html lang="en">
<!-- SUNSET V22 editable browser companion. Separate camera geometry from the MP4.
Adapted from Bang Motion's collage starter and OPENER API, v1.19.0,
c1aa65e921c970d858705fcb4a53a8294d1a4131.
https://github.com/bangtutorial/bang-motion
@@LICENSE@@
-->
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SUNSET — Support once. Share forever.</title>
<style>
@font-face{font-family:SunsetGeist;src:url('assets/geist.woff2') format('woff2');font-weight:100 900;font-display:block}
:root{--paper:#f7f5ed;--ink:#292d27;--green:#3d5941;--muted:#65755e;--terra:#d75835}
*{box-sizing:border-box}figure{margin:0}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#18251d}
body{font-family:SunsetGeist,Arial,sans-serif;color:var(--ink)}
#stage{position:absolute;left:50%;top:50%;width:1920px;height:1080px;overflow:hidden;background:var(--paper)}
#world{position:absolute;left:0;top:0;width:16000px;height:1080px;transform-origin:0 0;will-change:transform}
.paper{position:absolute;left:-6000px;top:-6000px;width:28000px;height:14000px;background:var(--paper)}
.paper:after{content:"";position:absolute;inset:0;opacity:.18;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='.7' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='200' height='200' opacity='.28' filter='url(%23n)'/%3E%3C/svg%3E")}
.wash{position:absolute;width:1800px;height:1500px;border-radius:50%;background:radial-gradient(ellipse,#b6c7a644,transparent 70%);pointer-events:none}
.object{position:absolute;opacity:0;will-change:transform,opacity}.object img{display:block;width:100%;height:100%;object-fit:contain}
.bob{width:100%;height:100%;will-change:transform;filter:drop-shadow(0 20px 18px #203a2525)}
.sheet{padding:18px;background:#fffdf7;box-shadow:0 22px 42px #263b2826}
.line{position:absolute;margin:0;width:1640px;font-size:94px;line-height:1.08;letter-spacing:-3.5px;font-weight:500;opacity:0}
.w{display:inline-block;white-space:nowrap;opacity:0;margin-right:.22em;will-change:transform,opacity}
.label{position:absolute;font-size:36px;line-height:1.35;font-weight:500;color:var(--muted);opacity:0}
.seal{padding:18px 28px;border:3px solid currentColor;color:var(--terra);font-size:52px;line-height:1.1;font-weight:550;letter-spacing:-1px;background:var(--paper);transform:rotate(-3deg)}
.proof-note{width:1500px;font-size:38px;line-height:1.45;color:var(--ink);background:var(--paper);padding:18px 24px;border-left:5px solid var(--terra)}
.lockup{position:absolute;width:1000px;height:300px;display:flex;align-items:center;gap:60px}
.lockup img{width:256px;height:256px;flex:none}.wordmark{font-size:164px;font-weight:680;letter-spacing:-6.56px;line-height:1;color:#292d27}
#brand{left:460px;top:330px}.tagline{position:absolute;left:460px;top:680px;width:1000px;font-size:48px;letter-spacing:-1px;font-weight:500;text-align:center;opacity:0}
#finance-plane{position:absolute;left:6500px;top:0;width:1920px;height:1080px;visibility:hidden;background:var(--paper)}
#master{display:block;width:1920px;height:1080px;object-fit:contain}
#finance-note{position:absolute;left:6552px;top:34px;padding:12px 20px;background:var(--paper);font-size:32px;color:var(--green);visibility:hidden}
#dbg{position:fixed;left:50%;bottom:16px;transform:translateX(-50%);display:none;align-items:center;gap:14px;max-width:95vw;padding:12px 18px;border-radius:12px;background:#203a25f0;color:#f7f5ed;z-index:20;font:14px SunsetGeist,Arial,sans-serif}
#dbg button{font:inherit;color:inherit;background:none;border:1px solid #cad3bb;border-radius:6px;padding:7px 12px}#dbg input{width:min(460px,48vw)}#clock{min-width:85px;font-variant-numeric:tabular-nums}
#error{position:fixed;inset:0;display:none;place-items:center;padding:60px;background:var(--paper);color:var(--ink);font:24px SunsetGeist,Arial,sans-serif;z-index:30}
</style>
</head>
<body>
<svg width="0" height="0" style="position:fixed" aria-hidden="true"><defs id="filters"></defs></svg>
<main id="stage" aria-label="SUNSET animated workshop-kit story">
 <div id="world">
  <div class="paper"></div>
  <div class="wash" style="left:1900px;top:-200px"></div><div class="wash" style="left:10300px;top:-200px"></div>
  <div class="lockup" id="brand"><img src="assets/original-logo.svg" alt=""><span class="wordmark">SUNSET</span></div>
  <div class="tagline" id="tagline">Support once. Share forever.</div>
  <figure class="object" id="maker" style="left:2380px;top:260px;width:580px;height:660px"><div class="bob" data-float="0"><img src="assets/creator.png" alt="Fictional maker illustration"></div></figure>
  <figure class="object" id="hands" style="left:3030px;top:495px;width:580px;height:380px"><div class="bob" data-float="1"><img src="assets/hands.png" alt="Making useful work"></div></figure>
  <h1 class="line" id="why-line" style="left:2280px;top:60px">Useful work can be free</h1>
  <div class="label" id="why-label" style="left:2300px;top:943px">Without leaving its creator unpaid</div>
  <figure class="object" id="kit" style="left:4370px;top:260px;width:600px;height:660px"><div class="bob" data-float="2"><img src="assets/kit-cover.png" alt="Community Skill-Swap Kit cover"></div></figure>
  <figure class="object" id="agenda" style="left:5050px;top:290px;width:540px;height:620px"><div class="bob" data-float="3"><img src="assets/kit-agenda.png" alt="The kit's workshop agenda"></div></figure>
  <div class="line" id="kit-line" style="left:4260px;top:60px">Learn something together</div>
  <div class="label" id="kit-label" style="left:4280px;top:943px">Community Skill-Swap Kit · 45 minutes · example resource</div>
  <div id="finance-plane"><video id="master" src="assets/master.mp4" muted playsinline preload="auto" aria-label="Reviewed protocol illustration"></video></div>
  <div id="finance-note">Protocol / testnet illustration · not this kit's payment history</div>
  <figure class="object" id="refund-art" style="left:8840px;top:235px;width:1320px;height:630px"><div class="bob" data-float="4"><img src="assets/refund.png" alt="Alternative refund outcome illustration"></div></figure>
  <div class="label" id="refund-label" style="left:8620px;top:65px;color:var(--terra)">Alternative outcome</div>
  <div class="line" id="refund-line" style="left:8620px;top:130px">Conditions missed</div>
  <div class="label seal" id="refund-seal" style="left:8960px;top:901px">Refunds claimable</div>
  <figure class="object" id="copy-one" style="left:10750px;top:300px;width:520px;height:610px"><div class="bob" data-float="5"><img src="assets/kit-cover.png" alt="A retained copy of the same kit"></div></figure>
  <figure class="object" id="copy-two" style="left:11220px;top:270px;width:520px;height:610px"><div class="bob" data-float="6"><img src="assets/kit-agenda.png" alt="The kit's usable agenda"></div></figure>
  <figure class="object" id="copy-three" style="left:11700px;top:325px;width:520px;height:610px"><div class="bob" data-float="7"><img src="assets/kit-cover.png" alt="A shareable copy of the same kit"></div></figure>
  <div class="line" id="use-line" style="left:10540px;top:70px">Keep it. Use it. Share it.</div>
  <div class="label seal" id="offline-label" style="left:10800px;top:923px;color:var(--green)">Even offline</div>
  <figure class="object sheet" id="proof-art" style="left:12870px;top:248px;width:1420px;height:590px"><img src="assets/proof.png" alt="Prior recorded testnet and offline evidence"></figure>
  <div class="line" id="proof-line" style="left:12650px;top:65px;font-size:82px">Recorded Lantern Trail proof</div>
  <div class="label proof-note" id="proof-label" style="left:12670px;top:873px">2 Nov 2026 · 0.1 testNEAR creator payout<br>Prior offline reader evidence · separate earlier sample</div>
  <div class="line" id="next-line" style="left:2280px;top:60px;font-size:86px">Make the next free thing possible</div>
  <div class="label" id="next-label" style="left:2300px;top:943px">The same maker. The next useful idea.</div>
  <div class="line" id="payoff-line" style="left:4260px;top:80px">Free to use</div>
  <div class="label seal" id="paid-label" style="left:4300px;top:925px;color:var(--green)">Creator paid</div>
 </div>
</main>
<audio id="audio" src="assets/audio.m4a" preload="auto"></audio>
<div id="dbg"><button id="play" type="button">Play</button><input id="scrub" type="range" min="0" max="1000" value="0" aria-label="Animation time"><span id="clock">0.00s</span></div>
<div id="error" role="alert"></div>
<script src="assets/gsap.min.js"></script>
<script id="sunset-animation">
'use strict';
const DATA=@@DATA@@;
const W=1920,H=1080,FPS=DATA.fps,DUR=DATA.duration,FRAME_MAP=DATA.frameMap;
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const P=Object.fromEntries(DATA.phases.map(p=>[p.id,p]));
const q=new URLSearchParams(location.search),clean=q.has('clean'),debug=q.has('debug')&&!clean;
const rig=$('#world'),video=$('#master'),audio=$('#audio');
const C={x:960,y:540,z:1},tl=gsap.timeline({paused:true});
let ready=false,starting=false,seekQueue=Promise.resolve();
const clamp=t=>Math.max(0,Math.min(DUR,t));
function mapped(t){return FRAME_MAP[Math.max(0,Math.min(FRAME_MAP.length-1,Math.floor((t+1e-8)*FPS)))];}
function fit(){const s=Math.min(innerWidth/W,innerHeight/H);$('#stage').style.transform=`translate(-50%,-50%) scale(${s})`;}
addEventListener('resize',fit);fit();
function applyCam(){rig.style.transform=`translate(${W/2-C.x*C.z}px,${H/2-C.y*C.z}px) scale(${C.z})`;}
const look=(at,x,y,z,dur=1.1,ease='sine.inOut')=>tl.to(C,{x,y,z,duration:dur,ease,onUpdate:applyCam},at);
const home=(at,x=960,y=540,dur=1.0)=>look(at,x,y,1,dur,'power2.inOut');
const into=(cutAt,x,y,z)=>look(Math.max(0,cutAt-.8),x,y,z,Math.min(.8,cutAt),'power2.in');
const settle=(cutAt,x,y,z)=>look(cutAt,x,y,z,.4,'power3.out');
let filterCount=0;
function blurTween(target,at,from,to,dur){
 const ns='http://www.w3.org/2000/svg',filter=document.createElementNS(ns,'filter'),blur=document.createElementNS(ns,'feGaussianBlur');
 filter.id='motion-blur-'+filterCount++;for(const [k,v] of Object.entries({x:'-70%',y:'-70%',width:'240%',height:'240%'}))filter.setAttribute(k,v);
 blur.setAttribute('stdDeviation','0 0');filter.appendChild(blur);$('#filters').appendChild(filter);const state={v:from};
 tl.set(target,{filter:`url(#${filter.id})`},at);tl.to(state,{v:to,duration:dur,ease:'power3.out',onUpdate(){blur.setAttribute('stdDeviation',`${state.v*.1} ${state.v}`);}},at);
 tl.set(target,{filter:'none'},at+dur);
}
$$('.line').forEach(el=>{const words=el.textContent.trim().split(/\s+/);el.textContent='';words.forEach(word=>{const span=document.createElement('span');span.className='w';span.textContent=word;el.appendChild(span);});});
function say(sel,at){const el=$(sel),ws=$$('.w',el);tl.set(el,{opacity:1},at);tl.fromTo(ws,{opacity:0,y:60,scaleY:1.12},{opacity:1,y:0,scaleY:1,duration:.5,stagger:.065,ease:'power4.out',immediateRender:false},at);blurTween(el,at,17,0,.55+ws.length*.065);}
function unsay(sel,at){tl.to(sel+' .w',{opacity:0,y:-34,duration:.2,stagger:.018,ease:'power2.in'},at);}
function label(sel,at,end){tl.fromTo(sel,{opacity:0,y:18},{opacity:1,y:0,duration:.4,ease:'power3.out',immediateRender:false},at);tl.to(sel,{opacity:0,duration:.18},end-.18);}
function fly(sel,at,from={x:0,y:180,rotate:5}){tl.fromTo(sel,{opacity:0,...from},{opacity:1,x:0,y:0,rotate:0,duration:.8,ease:'power4.out',immediateRender:false},at);}
function phrase(id,line,note){const p=P[id],at=p.start+Math.min(.45,(p.end-p.start)*.12);say(line,at);unsay(line,p.end-.22);if(note)label(note,at+.2,p.end);}
// One persistent maker and kit. Objects remain in the paper world after arrival.
fly('#maker',P.why.start+.12);fly('#hands',P.why.start+.5,{x:200,y:50,rotate:-4});
fly('#kit',P.kit.start+.1);fly('#agenda',P.kit.start+.34,{x:220,y:0,rotate:6});
fly('#refund-art',P.refund.start+.14);
['#copy-one','#copy-two','#copy-three'].forEach((s,i)=>fly(s,P.use.start+.08+i*.16,{x:240+i*100,y:110,rotate:(i-1)*6}));
fly('#proof-art',P.proof.start+.12,{x:160,y:20,rotate:-2});
phrase('why','#why-line','#why-label');phrase('kit','#kit-line','#kit-label');
phrase('refund','#refund-line');tl.set('#refund-label',{opacity:1},P.refund.start);tl.to('#refund-label',{opacity:0,duration:.18},P.refund.end-.18);label('#refund-seal',P.refund.start+.85,P.refund.end);
phrase('use','#use-line','#offline-label');phrase('proof','#proof-line','#proof-label');
phrase('next','#next-line','#next-label');phrase('payoff','#payoff-line','#paid-label');
// Camera follows the same world; finance is one fixed plane at native geometry.
tl.set(C,{x:960,y:540,z:1,onUpdate:applyCam},0);look(.05,960,540,1.035,Math.max(.1,P.intro.end-.1));
settle(P.why.start,3000,540,1.0);
into(P.kit.start,4850,550,1.36);settle(P.kit.start,4940,540,1.0);
tl.set(C,{x:7460,y:540,z:1,onUpdate:applyCam},P.sponsor.start);
tl.set(C,{x:9460,y:540,z:1,onUpdate:applyCam},P.refund.start);look(P.refund.start+.1,9460,550,1.025,Math.max(.2,P.refund.end-P.refund.start-.2));
into(P.use.start,11200,560,1.25);settle(P.use.start,11400,540,1.0);
into(P.proof.start,13600,500,1.3);settle(P.proof.start,13600,540,1.0);
tl.set(C,{x:3000,y:540,z:1.06,onUpdate:applyCam},P.next.start);home(P.next.start+.1,3000,540,Math.max(.3,P.next.end-P.next.start-.2));
tl.set(C,{x:4940,y:540,z:1.02,onUpdate:applyCam},P.payoff.start);
tl.set(C,{x:960,y:540,z:1,onUpdate:applyCam},P.closing.start);look(P.closing.start,960,540,1.035,P.closing.end-P.closing.start);
label('#tagline',P.closing.start+.25,P.closing.end);tl.to({},{duration:.001},DUR-.001);
function pauseMedia(){audio.pause();video.pause();}
function pause(){tl.pause();pauseMedia();}
function syncVideo(t,playing){
 const m=mapped(t),active=m.source==='v19';$('#finance-plane').style.visibility=active?'visible':'hidden';
 const finance=['sponsor','custody','release','claim'].some(id=>t>=P[id].start&&t<P[id].end);
 $('#finance-note').style.visibility=active&&finance?'visible':'hidden';
 if(!active){video.pause();return;}
 // A single source plane, including held frames, always follows frame-map.json.
 rig.style.transform=`translate(${-6500}px,0px) scale(1)`;
 // Live playback corrects drift; seekFrame below waits for the exact decoded frame.
 const sourceTime=m.source_frame/FPS,n=mapped(Math.min(DUR-1/FPS,t+1/FPS));
 const run=playing&&n.source==='v19'&&n.source_frame===m.source_frame+1;
 if(!run)video.pause();
 if(!video.seeking&&Math.abs(video.currentTime-sourceTime)>(run?1/FPS+.004:1/10000))video.currentTime=sourceTime;
 if(run&&video.paused)video.play().catch(()=>{});
}
function render(t,playing=false){
 applyCam();$$('[data-float]').forEach(el=>{const n=+el.dataset.float;el.style.transform=`translateY(${Math.sin(t*1.05+n*.7)*9}px) rotate(${Math.sin(t*.7+n)*.45}deg)`;});
 syncVideo(t,playing);
 if(!playing)audio.pause();else if(Math.abs(audio.currentTime-t)>.08)audio.currentTime=t;
 if(debug){$('#scrub').value=String(t/DUR*1000);$('#clock').textContent=t.toFixed(2)+'s';$('#play').textContent=playing?'Pause':'Play';}
}
function seek(t){pause();tl.pause(clamp(t),false);applyCam();if(gsap.ticker.tick)gsap.ticker.tick();render(tl.time(),false);}
function waitFrames(){return new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));}
function seekVideo(t){
 const m=mapped(t);video.pause();if(m.source!=='v19')return Promise.resolve();const target=m.source_frame/FPS;
 if(!video.seeking&&Math.abs(video.currentTime-target)<1/10000&&video.readyState>=2)return waitFrames();
 return new Promise((resolve,reject)=>{
  const timer=setTimeout(()=>finish(new Error('Timed out seeking reviewed source video')),10000);
  function finish(error){clearTimeout(timer);video.removeEventListener('seeked',done);video.removeEventListener('error',failed);error?reject(error):resolve();}
  function done(){finish();}function failed(){finish(new Error('Reviewed source video could not decode'));}
  video.addEventListener('seeked',done,{once:true});video.addEventListener('error',failed,{once:true});video.currentTime=target;
 });
}
function seekFrame(t){seekQueue=seekQueue.then(async()=>{seek(t);await seekVideo(clamp(t));await waitFrames();});return seekQueue;}
function showError(error){pause();$('#error').textContent='This companion could not load: '+error.message;$('#error').style.display='grid';}
async function play(t=tl.time()){
 if(!ready||starting)return;starting=true;pause();const at=t>=DUR-1/FPS?0:clamp(t);seek(at);audio.currentTime=at;
 try{await audio.play();tl.play(at);render(at,true);}catch(error){pause();waitForGesture();}finally{starting=false;}
}
let gesturePending=false;
function waitForGesture(){if(gesturePending)return;gesturePending=true;const go=()=>{removeEventListener('pointerdown',go);removeEventListener('keydown',go);gesturePending=false;play(tl.time());};addEventListener('pointerdown',go,{once:true});addEventListener('keydown',go,{once:true});}
function mediaReady(el,state){if(el.error)return Promise.reject(new Error('Failed local media: '+el.getAttribute('src')));if(el.readyState>=state)return Promise.resolve();return new Promise((resolve,reject)=>{const event=state===1?'loadedmetadata':'loadeddata';const timer=setTimeout(()=>finish(new Error('Local media readiness timed out')),15000);function finish(error){clearTimeout(timer);el.removeEventListener(event,done);el.removeEventListener('error',failed);error?reject(error):resolve();}function done(){finish();}function failed(){finish(new Error('Failed local media: '+el.getAttribute('src')));}el.addEventListener(event,done,{once:true});el.addEventListener('error',failed,{once:true});el.load();});}
tl.eventCallback('onUpdate',()=>render(tl.time(),!tl.paused()));
tl.eventCallback('onComplete',()=>{if(!tl.paused()&&!clean)play(0);});
window.OPENER={W,H,DURATION:DUR,tl,ready:false,seek,seekFrame,play,pause,clipsReady:()=>video.readyState>=2,frameMap:FRAME_MAP,companion:true};
addEventListener('keydown',event=>{if(event.target.matches('input,button'))return;if(event.code==='Space'){event.preventDefault();tl.paused()?play():pause();}if(/^[rR]$/.test(event.key))play(0);});
if(debug){$('#dbg').style.display='flex';$('#play').onclick=()=>tl.paused()?play():pause();$('#scrub').oninput=event=>seekFrame(+event.target.value/1000*DUR).catch(showError);}
Promise.all([document.fonts.load('680 164px SunsetGeist'),document.fonts.ready,...$$('img').map(img=>img.decode()),mediaReady(video,2),mediaReady(audio,1)]).then(async()=>{
 const last=Math.max(...FRAME_MAP.filter(m=>m.source==='v19').map(m=>m.source_frame))/FPS;
 if(!Number.isFinite(video.duration)||video.duration<=last)throw new Error('Reviewed source video is shorter than its mapped frame range');
 if(!Number.isFinite(audio.duration)||audio.duration<DUR-.15)throw new Error('Mixed audio is shorter than the composition');
 ready=true;window.OPENER.ready=true;await seekFrame(0);if(!clean)play(0);
}).catch(showError);
</script>
</body>
</html>
'''


def build_html(data):
    license_text = (SOURCE / 'BANG_LICENSE.txt').read_text()
    payload = json.dumps(data, separators=(',', ':'), ensure_ascii=False).replace('</', r'<\/')
    return HTML.replace('@@LICENSE@@', license_text.rstrip()).replace('@@DATA@@', payload)


def source_checks(html, output=None):
    """Static checks only: these intentionally never launch Chrome."""
    script = re.search(r'<script id="sunset-animation">(.*?)</script>', html, re.S).group(1)
    subprocess.run(['node', '--check'], input=script, text=True, capture_output=True, check=True)
    for forbidden in ('Date.now(', 'performance.now(', 'Math.random(', 'repeat:-1', 'setInterval('):
        if forbidden in script:
            raise ValueError(f'Non-deterministic or infinite animation: {forbidden}')
    if '<section' in html or 'class="scene"' in html:
        raise ValueError('The companion must remain one shared world')
    for text in ('Alternative outcome', 'Conditions missed', 'Refunds claimable',
                 'Recorded Lantern Trail proof', '2 Nov 2026 · 0.1 testNEAR creator payout',
                 'Prior offline reader evidence · separate earlier sample'):
        if text not in html:
            raise ValueError(f'Missing required story qualifier: {text}')
    resources = []
    class Assets(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for key, value in attrs:
                if key in ('src', 'href') and value:
                    resources.append(value)
    Assets().feed(html)
    resources += re.findall(r'url\([\'"]?(assets/[^\'"\)]+)', html)
    if any(not value.startswith('assets/') for value in resources):
        raise ValueError('External resource or ending link in the companion')
    if output:
        for name in ASSETS:
            path = output / 'assets' / name
            if not path.is_file() or path.stat().st_size == 0:
                raise ValueError(f'Missing local asset: {path}')
        original = ROOT / 'projects/sunset/public/icon.svg'
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        if digest(output / 'assets/original-logo.svg') != digest(original):
            raise ValueError('The companion must use the unchanged original SUNSET logo')
    return {'javascript_syntax': 'passed', 'deterministic_source': 'passed',
            'local_asset_references': len(resources), 'browser_executed': False,
            'pixel_matched_to_mp4': False}


def self_check():
    phases = [{'id': name, 'start': i, 'end': i + 1} for i, name in enumerate(IDS)]
    frames = [{'frame': n, 'source': 'v19' if 90 <= n < 210 else IDS[n // 30],
               **({'source_frame': n - 90} if 90 <= n < 210 else {})}
              for n in range(390)]
    data = validated({'fps': 30, 'duration': 13, 'phases': phases}, frames)
    result = source_checks(build_html(data))
    function = re.search(r'function mapped\(t\)\{.*?\}\n', HTML).group()
    check = ('const assert=require("node:assert/strict");const FPS=30,FRAME_MAP='
             + json.dumps(frames) + ';\n' + function
             + '\nassert.equal(mapped(3).source_frame,0);'
             + 'assert.equal(mapped(6.999999).source_frame,119);'
             + 'assert.equal(mapped(7).source,"refund");'
             + 'assert.equal(mapped(-1).frame,0);assert.equal(mapped(99).frame,389);')
    subprocess.run(['node'], input=check, text=True, capture_output=True, check=True)
    broken = [dict(row) for row in frames]
    broken[90]['source'] = 'sponsor'
    try:
        validated({'fps': 30, 'duration': 13, 'phases': phases}, broken)
    except ValueError as error:
        if 'finance frames' not in str(error):
            raise
    else:
        raise AssertionError('Finance replacement should fail validation')
    return {**result, 'mapping_boundaries': 'passed', 'finance_negative_control': 'passed',
            'assets_checked': False, 'synthetic_metadata_only': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT)
    parser.add_argument('--timeline', type=Path, default=OUT.parent / 'timeline.json')
    parser.add_argument('--frame-map', type=Path, default=OUT.parent / 'frame-map.json')
    parser.add_argument('--check', action='store_true', help='Check the already generated companion')
    parser.add_argument('--self-check', action='store_true', help='Syntax and mapping checks without production assets')
    args = parser.parse_args()
    if args.self_check:
        print(json.dumps(self_check(), indent=2))
        return
    data = validated(json.loads(args.timeline.read_text()), json.loads(args.frame_map.read_text()))
    html = build_html(data)
    result = source_checks(html, args.output)
    target = args.output / 'index.html'
    if args.check:
        if target.read_text() != html:
            raise ValueError('Generated companion differs from current source/timing')
    else:
        args.output.mkdir(parents=True, exist_ok=True)
        target.write_text(html)
    print(json.dumps({**result, 'output': str(target), 'duration': data['duration'],
                      'frames': len(data['frameMap']), 'assets_checked': True}, indent=2))


if __name__ == '__main__':
    main()
