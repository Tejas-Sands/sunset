import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';

export function extents(body) {
  const {core, radius} = body.rest;
  return core.map((v, i) => (v + radius) * body.scale[i]);
}
export function support(body, n) {
  const local = n.map((v,i)=>v*body.scale[i]);
  return body.rest.core.reduce((sum,c,i)=>sum+c*Math.abs(local[i]),0) + body.rest.radius*Math.hypot(...local);
}
export function axisGap(a, b, axis) {
  return Math.abs(b.position[axis]-a.position[axis])-extents(a)[axis]-extents(b)[axis];
}
export function intervalLowerBound(g0, g1, speed, dt) {
  return Math.min(g0,g1)-speed*dt/2;
}
export function insideRoundedBox(vertex, rest, tolerance=1e-6) {
  const distance=Math.hypot(...vertex.map((v,i)=>Math.max(0,Math.abs(v)-rest.core[i])));
  return distance<=rest.radius+tolerance;
}


const EPS=2e-6;
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const sub=(a,b)=>a.map((v,i)=>v-b[i]);
function pairKey(a,b) { return [a,b].sort().join('|'); }
function sameSolid(contract,a,b) {
  // Only an explicit, reviewed continuous SAME solid can overlap itself.
  return (contract.continuousAssemblies||[]).some(x=>x.ids.includes(a)&&x.ids.includes(b)&&x.justification);
}
function cameraRadius(camera) {
  return camera.near*Math.sqrt(1+Math.tan(camera.fov*Math.PI/360)**2*(1+camera.aspect**2));
}
export function checkState(state, contract={}) {
  const failures=[], gaps={floor:{},pairs:{},camera:{}};
  const ids=new Set();
  for (const b of state.bodies) {
    if(!b.id||ids.has(b.id)) failures.push('missing or duplicate body ID');
    ids.add(b.id);
    if(b.rest?.kind!=='roundedBox'||b.rest.core?.length!==3||!b.rest.core?.every(x=>Number.isFinite(x)&&x>=0)||!Number.isFinite(b.rest.radius)||!(b.rest.radius>=0)||b.scale?.length!==3||!b.scale?.every(x=>Number.isFinite(x)&&x>0)||b.position?.length!==3||!b.position?.every(Number.isFinite)) {
      failures.push(`invalid support shape:${b.id}`); continue;
    }
    if(b.rotation?.some(v=>Math.abs(v)>EPS)) failures.push(`unsupported rotation:${b.id}`);
    if(b.quaternion&&Math.max(...b.quaternion.slice(0,3).map(Math.abs),Math.abs(b.quaternion[3]-1))>EPS) failures.push(`unsupported rotation:${b.id}`);
    const e=extents(b), fg=b.position[1]-e[1]-state.floorY;
    gaps.floor[b.id]=fg;
    if(fg < -EPS) failures.push(`floor penetration:${b.id}:${fg}`);
    for(const plane of state.planes||[]) {
      const gap=dot(plane.normal,b.position)-support(b,plane.normal)-plane.offset;
      if(gap < -EPS) failures.push(`plane penetration:${b.id}:${plane.id}`);
    }
    if(state.supportBounds) {
      for(const axis of [0,2]) if(b.position[axis]-e[axis]<state.supportBounds.min[axis]-EPS||b.position[axis]+e[axis]>state.supportBounds.max[axis]+EPS) failures.push(`unsupported platform footprint:${b.id}`);
    }
    if(state.camera) {
      const radius=cameraRadius(state.camera)+(contract.cameraClearance||.01);
      const gap=Math.max(...[0,1,2].map(i=>Math.abs(state.camera.position[i]-b.position[i])-e[i]-radius));
      gaps.camera[b.id]=gap;
      if(gap < -EPS) failures.push(`camera near-plane safety unresolved:${b.id}:${gap}`);
    }
  }
  for(let i=0;i<state.bodies.length;i++) for(let j=i+1;j<state.bodies.length;j++) {
    const a=state.bodies[i],b=state.bodies[j];
    if(sameSolid(contract,a.id,b.id)) continue;
    const gap=Math.max(...[0,1,2].map(axis=>axisGap(a,b,axis)));
    gaps.pairs[pairKey(a.id,b.id)]=gap;
    if(gap < -EPS) failures.push(`pair separation unresolved:${a.id}:${b.id}:${gap}`);
  }
  return {pass:failures.length===0,failures,gaps};
}
function transformPoint(p,m) {
  const w=m[3]*p[0]+m[7]*p[1]+m[11]*p[2]+m[15];
  return [0,1,2].map(i=>(m[i]*p[0]+m[i+4]*p[1]+m[i+8]*p[2]+m[i+12])/w);
}
function projectPoint(p,cam,width,height) {
  const m=cam.matrixWorld, d=sub(p,[m[12],m[13],m[14]]);
  const v=[dot(d,[m[0],m[1],m[2]]),dot(d,[m[4],m[5],m[6]]),dot(d,[m[8],m[9],m[10]])];
  const q=transformPoint(v,cam.projectionMatrix);
  return [(q[0]+1)*width/2,(1-q[1])*height/2,-v[2]];
}
export function verifyCamera(live,expected) {
  const failures=[];
  if(!live?.matrixWorld||!live?.projectionMatrix) return ['actual camera matrices missing'];
  const m=live.matrixWorld,p=live.projectionMatrix;
  if(m.length!==16||p.length!==16||!m.every(Number.isFinite)||!p.every(Number.isFinite)) return ['actual camera matrices invalid'];
  for(let i=0;i<3;i++) if(Math.abs(m[12+i]-expected.position[i])>EPS) failures.push('actual camera position differs');
  for(const k of ['near','far','fov','aspect']) if(!Number.isFinite(live[k])||Math.abs(live[k]-expected[k])>EPS) failures.push(`actual camera ${k} differs`);
  const back=sub(expected.position,expected.target),length=Math.hypot(...back);
  for(let i=0;i<3;i++) if(Math.abs(m[8+i]-back[i]/length)>EPS) failures.push('actual camera target differs');
  const basis=[m.slice(0,3),m.slice(4,7),m.slice(8,11)];
  for(let i=0;i<3;i++) for(let j=i;j<3;j++) if(Math.abs(dot(basis[i],basis[j])-(i===j?1:0))>EPS) failures.push('actual camera is not rigid orthonormal');
  const f=1/Math.tan(expected.fov*Math.PI/360),n=expected.near,z=expected.far;
  const wanted=[f/expected.aspect,0,0,0,0,f,0,0,0,0,-(z+n)/(z-n),-1,0,0,-2*z*n/(z-n),0];
  if(p.some((v,i)=>Math.abs(v-wanted[i])>EPS)) failures.push('actual camera projection differs');
  return failures;
}

export function checkLiveFrame(frame, geometries, state, options={}) {
  const failures=[];let vertices=0;
  if(frame.camera&&state.camera) failures.push(...verifyCamera(frame.camera,state.camera));
  const observed=new Map(frame.bodies.map(b=>[b.id,b]));
  if(observed.size!==frame.bodies.length) failures.push('duplicate actual solid ID');
  for(const b of state.bodies) {
    const live=observed.get(b.id), geo=live&&geometries.get(live.geometryId);
    if(!live||!geo) { failures.push(`actual solid missing:${b.id}`);continue; }
    const p=live.positions||geo.positions,m=live.matrixWorld;
    if(!Array.isArray(m)||m.length!==16||!m.every(Number.isFinite)||!p||p.length<9||p.length%3||!p.every(Number.isFinite)) {failures.push(`bad actual geometry:${b.id}`);continue;}
    const wanted=[b.scale[0],0,0,0,0,b.scale[1],0,0,0,0,b.scale[2],0,...b.position,1];
    if(m.some((v,i)=>Math.abs(v-wanted[i])>EPS)) failures.push(`live/world pose mismatch:${b.id}`);
    for(let i=0;i<p.length;i+=3) {
      const local=p.slice(i,i+3),world=transformPoint(local,m);vertices++;
      if(!insideRoundedBox(local,b.rest,EPS)) {failures.push(`actual mesh exceeds support hull:${b.id}:${i/3}`);break;}
      if(world[1]<state.floorY-EPS) {failures.push(`actual mesh below floor:${b.id}:${i/3}`);break;}
      if(options.checkSolidDepthRange!==false&&frame.camera?.matrixWorld&&frame.camera?.projectionMatrix) {
        const projected=projectPoint(world,frame.camera,options.width||1920,options.height||1080);
        if(projected[2]<frame.camera.near-EPS||projected[2]>frame.camera.far+EPS) {failures.push(`actual vertex near/far clipping:${b.id}:${i/3}`);break;}
      }
    }
  }
  for(const live of frame.bodies) if(!state.bodies.some(b=>b.id===live.id)) failures.push(`unreported rendered solid:${live.id}`);
  if(frame.render_elements) {
    const solids=frame.render_elements.filter(e=>e.solid===true||e.kind==='solid');
    for(const b of state.bodies) if(!solids.some(e=>(e.bodyId||e.id)===b.id)) failures.push(`solid absent from render inventory:${b.id}`);
    for(const e of solids) if(!state.bodies.some(b=>b.id===(e.bodyId||e.id))) failures.push(`unverified extra rendered solid:${e.id}`);
  }
  for(const element of frame.render_elements||[]) {
    if(element.coordinate_space==='screen'&&element.kind==='screen-text') {
      const box=element.screen_bbox,safe=element.safe_bbox||[96,54,(options.width||1920)-96,(options.height||1080)-54];
      if(element.essential&&element.visible!==false&&(!box||box[0]<safe[0]||box[1]<safe[1]||box[2]>safe[2]||box[3]>safe[3])) failures.push(`screen text outside safe bounds:${element.id}`);
      if(element.essential&&element.visible!==false&&!(element.contrast_ratio>=4.5)) failures.push(`screen text contrast undeclared/low:${element.id}`);
      continue; // Explicit screen typography is not a physical plane or a collision solid.
    }
    if(element.depthTest===false) failures.push(`world render element hides depth intersection:${element.id}`);
    if(element.kind==='text') {
      const mounted=element.placement==='uv-material'&&state.bodies.some(b=>b.id===element.bodyId);
      if(!mounted&&!element.worldVertices) failures.push(`text has no verified physical placement:${element.id}`);
      if(!mounted&&element.worldVertices) {
        const points=[0,1,2].map(k=>element.worldVertices.filter((_,i)=>i%3===k));
        const lo=points.map(a=>Math.min(...a)),hi=points.map(a=>Math.max(...a));
        for(const body of state.bodies) {
          const e=extents(body);
          if(![0,1,2].some(k=>hi[k]<body.position[k]-e[k]-EPS||lo[k]>body.position[k]+e[k]+EPS)) failures.push(`physical text/body separation unresolved:${element.id}:${body.id}`);
        }
      }
    }
    if(element.worldVertices&&element.essential) {
      if(!frame.camera?.matrixWorld||!frame.camera?.projectionMatrix) {failures.push(`text camera metadata missing:${element.id}`);continue;}
      const box=element.safe_bbox||[96,54,(options.width||1920)-96,(options.height||1080)-54];
      for(let i=0;i<element.worldVertices.length;i+=3) {
        const screen=projectPoint(element.worldVertices.slice(i,i+3),frame.camera,options.width||1920,options.height||1080);
        if(screen[0]<box[0]||screen[1]<box[1]||screen[0]>box[2]||screen[1]>box[3]||screen[2]<frame.camera.near) failures.push(`essential text outside safe rectangle:${element.id}`);
      }
    }
  }
  return {pass:failures.length===0,failures,vertices};
}

// Independent interval replay of the reviewed, bounded eight-second equations.
// This is intentionally specific to this scene, rather than a general JS/physics prover.
const ID=['handbook-core','handbook-cover','sunset-seal','support-left','support-right','support-rear'];
const R=[[1.65,1,0,.35],[1.78,1.13,0,.22],[.37,.24,.03,.28],[.25,.25,.25,.25],[.25,.25,.25,.25],[.25,.25,.25,.25]];
const S=.004,ROUND=1e-12;
const interval=x=>Array.isArray(x)?x:[x,x];
const add=(...xs)=>xs.map(interval).reduce((a,b)=>[a[0]+b[0]-ROUND,a[1]+b[1]+ROUND],[0,0]);
const neg=x=>{x=interval(x);return [-x[1],-x[0]]};
const minus=(a,b)=>add(a,neg(b));
const mul=(a,b)=>{a=interval(a);b=interval(b);const p=[a[0]*b[0],a[0]*b[1],a[1]*b[0],a[1]*b[1]];return [Math.min(...p)-ROUND,Math.max(...p)+ROUND]};
const pow=(a,n)=>[a[0]**n,a[1]**n].sort((a,b)=>a-b).map((x,i)=>x+(i?ROUND:-ROUND));
const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
const motion=(t,a,b)=>smooth((t-a)/(b-a));
function pulse(t,a,b,c) {return t<a||t>=c?0:t<b?smooth((t-a)/(b-a)):1-smooth((t-b)/(c-b));}
function pressure(t,contact,amount) {const u=t-contact;return amount*(pulse(u,0,.14,.46)-.18*pulse(u,.46,.62,.94));}
export function pressureRange(a,b,contact,amount) {
  const times=[a,b,...[0,.14,.46,.62,.94].map(x=>x+contact).filter(x=>x>a&&x<b)];
  const values=times.map(t=>pressure(t,contact,amount));
  return [Math.min(...values)-ROUND,Math.max(...values)+ROUND];
}
function moveRange(a,b,start,end) {return [motion(a,start,end)-ROUND,motion(b,start,end)+ROUND];}
function mixRange(a,b,q) {return add(a,mul(minus(b,a),q));}
function scaleRange(axis,k) {
  const scale=[pow(minus(1,k),-.5),pow(minus(1,k),-.5),pow(minus(1,k),-.5)];
  scale[axis]=minus(1,k);return scale;
}
export function modelIntervals(a,b) {
  const p=[0,pressureRange(a,b,.55,.16),pressureRange(a,b,.55,.22),pressureRange(a,b,2.9,.22),pressureRange(a,b,3.3,.22),pressureRange(a,b,3.7,.22)];
  const scale=[[[1,1],[1,1],[1,1]],scaleRange(2,p[1]),scaleRange(2,p[2]),scaleRange(0,p[3]),scaleRange(0,p[4]),scaleRange(2,p[5])];
  const e=scale.map((s,i)=>s.map((q,k)=>mul(R[i][k]+R[i][3],q)));
  const travel=[mul(4.8,minus(1,moveRange(a,b,2.4,2.9))),mul(4.8,minus(1,moveRange(a,b,2.8,3.3))),mul(4.8,minus(1,moveRange(a,b,3.2,3.7)))];
  const open=mul(1.65,moveRange(a,b,6.1,6.5)),lift=mul(3,moveRange(a,b,6.5,7.3));
  const sealLift=mul(2.9,moveRange(a,b,5.3,5.9)),approach=mul(2.15,minus(1,moveRange(a,b,0,.55)));
  const positions=[[[0,0],add(e[0][1],S),[0,0]],[[0,0],add(e[1][1],S,lift),add(e[0][2],e[1][2],S,open)],[[.25,.25],add(e[1][1],S,.15,sealLift),add(e[0][2],mul(2,e[1][2]),e[2][2],2*S,approach)],
    [neg(add(e[0][0],e[3][0],S,travel[0])),add(e[3][1],S),[0,0]],
    [add(e[0][0],e[4][0],S,travel[1]),add(e[4][1],S),[0,0]],
    [[0,0],add(e[5][1],S),neg(add(e[0][2],e[5][2],S,travel[2]))]];
  const macro=moveRange(a,b,0,2.4),wide=moveRange(a,b,2.4,5.3),handoff=moveRange(a,b,6.2,8);
  let cp=[mixRange(2.5,5.2,macro),mixRange(2,3.5,macro),mixRange(4.5,7.3,macro)];
  cp=cp.map((v,i)=>mixRange(v,[7.2,3,-1.4][i],moveRange(a,b,2.4,3.65))).map((v,i)=>mixRange(v,[4,3.2,7][i],moveRange(a,b,3.65,5.3))).map((v,i)=>mixRange(v,[.15,1.65,5.5][i],handoff));
  const target=[mixRange(.25,0,macro),mixRange(1.5,1.3,macro),mixRange(.9,0,macro)].map((v,i)=>mixRange(v,[0,1.35,.35][i],handoff));
  const floor=[interval(S),add(S,lift),add(e[1][1],S,.15,sealLift,neg(e[2][1])),interval(S),interval(S),interval(S)];
  // Cancel shared deformed extents BEFORE interval arithmetic; these identities
  // are directly reviewed against the frozen motion.mjs source.
  const pairs={};const pair=(i,j,v)=>pairs[pairKey(ID[i],ID[j])]=v;
  pair(0,1,add(S,open));pair(0,2,add(mul(2,e[1][2]),2*S,approach));
  if(b<=6.1+1e-11) pair(1,2,add(S,approach));
  else if(a>=6.1-1e-11&&b<=6.5+1e-11) pair(1,2,add(.15,sealLift,neg(lift),neg(e[2][1]),neg(e[1][1])));
  else if(a>=6.5-1e-11) pair(1,2,add(open,neg(mul(2,e[1][2])),neg(mul(2,e[2][2])),-S,neg(approach)));
  for(const [i,j] of [[3,0],[4,1]]) {pair(i,0,add(S,travel[j]));pair(i,1,add(e[0][0],S,travel[j],neg(e[1][0])));pair(i,2,add(e[0][0],S,travel[j],i===3?.25:-.25,neg(e[2][0])));pair(i,5,add(e[0][0],S,travel[j],neg(e[5][0])));}
  pair(5,0,add(S,travel[2]));pair(5,1,add(mul(2,e[0][2]),2*S,travel[2],open));
  pair(5,2,add(mul(2,e[0][2]),mul(2,e[1][2]),3*S,travel[2],approach));
  pair(3,4,add(mul(2,e[0][0]),2*S,travel[0],travel[1]));
  return {bodies:ID.map((id,i)=>({id,position:positions[i],scale:scale[i],e:e[i],floor:floor[i]})),camera:{position:cp,target,fov:mixRange(37,32,handoff),near:.08,far:60,aspect:16/9},pairs};
}
function surfaceSpeedBounds() {
  const kr=.22*1.5/.14, kc=.16*1.5/.14;
  const rates=(i,k,axis)=>R[i].slice(0,3).map((v,j)=>(v+R[i][3])*(j===axis?k:.5*(1-(i===1?.16:.22))**(-1.5)*k));
  const ce=rates(1,kc,2),se=rates(2,kr,2),su=rates(3,kr,0),re=rates(5,kr,2);
  const speed=(centre,extent)=>Math.hypot(...centre)+Math.hypot(...extent);
  return {'handbook-core':0,'handbook-cover':speed([0,ce[1]+3*1.5/.8,ce[2]+1.65*1.5/.4],ce),
    'sunset-seal':speed([0,ce[1]+2.9*1.5/.6,2*ce[2]+se[2]+2.15*1.5/.55],se),
    'support-left':speed([su[0]+4.8*1.5/.5,su[1],0],su),'support-right':speed([su[0]+4.8*1.5/.5,su[1],0],su),'support-rear':speed([0,re[1],re[2]+4.8*1.5/.5],re)};
}
function lowerAbs(v) {return v[0]<=0&&v[1]>=0?0:Math.min(Math.abs(v[0]),Math.abs(v[1]));}
export function verifyAnalyticMotion(sampleState,contract) {
  const failures=[],bounds=surfaceSpeedBounds(),min={floor:Infinity,pair:Infinity,camera:Infinity};
  const cameraSpeedBound=Math.max(...[[[2.7,1.5,2.8],2.4],[[2,-.5,-8.7],1.25],[[-3.2,.2,8.4],1.65],[[-3.85,-1.55,-1.5],1.8]].map(([delta,duration])=>1.5*Math.hypot(...delta)/duration));
  if(cameraSpeedBound>(contract.cameraSpeedBound??-1)) failures.push('understated camera derivative bound');
  const times=Array.from({length:1921},(_,i)=>i/240),states=times.map(sampleState);
  for(let i=0;i<states.length;i++) {
    const state=states[i],expected=modelIntervals(times[i],times[i]),sample=checkState(state,contract);
    failures.push(...sample.failures.map(s=>`t=${times[i]}:${s}`));
    if(state.bodies.length!==6) failures.push(`unexpected body count:t=${times[i]}`);
    for(const eb of expected.bodies) {
      const b=state.bodies.find(b=>b.id===eb.id);
      if(!b) {failures.push(`body missing:${eb.id}`);continue;}
      for(const field of ['position','scale']) for(let k=0;k<3;k++) if(b[field][k]<eb[field][k][0]-EPS||b[field][k]>eb[field][k][1]+EPS) failures.push(`reviewed equations mismatch:${eb.id}:${field}:${k}:t=${times[i]}`);
      const r=R[ID.indexOf(eb.id)];
      if(b.rest.core.some((v,k)=>Math.abs(v-r[k])>EPS)||Math.abs(b.rest.radius-r[3])>EPS) failures.push(`rest support changed:${eb.id}`);
      if(Math.abs(b.scale.reduce((a,b)=>a*b,1)-1)>1e-10) failures.push(`volume changed:${eb.id}`);
    }
    for(const field of ['position','target']) for(let k=0;k<3;k++) if(state.camera[field][k]<expected.camera[field][k][0]-EPS||state.camera[field][k]>expected.camera[field][k][1]+EPS) failures.push(`camera equations mismatch:${field}:t=${times[i]}`);
    if(state.camera.fov<expected.camera.fov[0]-EPS||state.camera.fov>expected.camera.fov[1]+EPS||state.camera.near!==.08||state.camera.far!==60||Math.abs(state.camera.aspect-16/9)>1e-12||state.floorY!==0) failures.push(`camera/stage constants mismatch:t=${times[i]}`);
  }
  let intervals=0;
  for(let i=0;i<times.length-1;i++) {
    const a=times[i],b=times[i+1],v=modelIntervals(a,b);intervals++;
    for(const body of v.bodies) {min.floor=Math.min(min.floor,body.floor[0]);if(body.floor[0]<-1e-9) failures.push(`continuous floor unresolved:${body.id}:${a}-${b}`);}
    if(Object.keys(v.pairs).length!==15) failures.push(`continuous pair certificate coverage incomplete:${a}-${b}`);
    for(const [key,gap] of Object.entries(v.pairs)) {min.pair=Math.min(min.pair,gap[0]);if(gap[0]<S-1e-9) failures.push(`continuous pair separation unresolved:${key}:${a}-${b}:${gap[0]}`);}
    const cam=v.camera,radius=cam.near*Math.sqrt(1+Math.tan(cam.fov[1]*Math.PI/360)**2*(1+cam.aspect**2))+.01;
    for(const body of v.bodies) {
      const gap=Math.max(...[0,1,2].map(k=>lowerAbs(minus(cam.position[k],body.position[k]))-body.e[k][1]-radius));
      min.camera=Math.min(min.camera,gap);if(gap < -1e-9) failures.push(`continuous camera near-plane certificate unresolved:${body.id}:${a}-${b}:${gap}`);
    }
    // Independently-derived all-surface derivative bound also encloses travel
    // between checks. Algebraic interval gaps above retain correlated contacts
    // that a loose endpoint Lipschitz bound would unnecessarily reject.
    for(const id of ID) if(bounds[id]>(contract.worldSurfaceSpeedBounds?.[id]??-1)+1e-8) failures.push(`understated derivative bound:${id}`);
  }
  return {pass:!failures.length,failures:failures.slice(0,100),failure_count:failures.length,samples:states.length,intervals,substep_hz:240,min_gaps:min,derived_world_surface_speed_bounds:bounds,derived_camera_speed_bound:cameraSpeedBound,
    max_half_substep_surface_displacement:Object.fromEntries(Object.entries(bounds).map(([id,v])=>[id,v/480])),certificate:'Independent interval enclosure of reviewed analytic equations; exact shared-support cancellations; every1920 interval covered; unresolved intervals reject.',states};
}


export function selfTest() {
  const b = {rest:{kind:'roundedBox',core:[0,0,0],radius:1},position:[0,1,0],scale:[1.2,25/36,1.2]};
  assert.deepEqual(extents(b), [1.2,25/36,1.2], 'post-deformation support must replace undeformed radius');
  assert.equal(support(b, [1,0,0]), 1.2, 'support includes affine squash and bulge');
  const other = {...b, position:[2.1,1,0]};
  assert.ok(axisGap(b, other, 0) < 0, 'volume-preserving bulge overlaps despite undeformed sphere gap');
  assert.ok(intervalLowerBound(1,1,120,1/30)<0, 'crossing balls between 30fps samples are unresolved');
  assert.ok(intervalLowerBound(1,1,2,1/240)>0, 'separated slow interval has positive certificate');
  assert.equal(insideRoundedBox([1.01,0,0],b.rest),false,'rest mesh outside declared hull must fail');
  const floorBad={floorY:0,bodies:[{...b,position:[0,.5,0]}],camera:{position:[0,0,10],near:.1,far:100,fov:38,aspect:16/9}};
  assert.ok(checkState(floorBad).failures.some(x=>x.startsWith('floor penetration:')),'deformed lower surface crossing floor rejects');
  const live={bodies:[{id:'ball',geometryId:'ball',matrixWorld:[1,0,0,0,0,1,0,0,0,0,1,0,0,1,0,1]}]};
  const gs=new Map([['ball',{positions:[1.01,0,0,0,1,0,0,0,1],rest:b.rest}]]);
  assert.ok(checkLiveFrame(live,gs,{bodies:[{...b,id:'ball',scale:[1,1,1]}]}).failures.some(x=>x.startsWith('actual mesh exceeds support hull:')),'actual mesh outside advertised hull rejects');
  assert.ok(pressureRange(.55,1.01,.55,.22)[1]>=.22,'continuous pressure enclosure catches peak missed at interval endpoints');
  const expectedCamera={position:[0,0,10],target:[0,0,0],near:.1,far:100,fov:38,aspect:16/9};
  const f=1/Math.tan(38*Math.PI/360),n=.1,z=100;
  const badCamera={...expectedCamera,matrixWorld:[1,0,0,0,0,1,0,0,0,0,1,0,0,0,9,1],projectionMatrix:[f/(16/9),0,0,0,0,f,0,0,0,0,-(z+n)/(z-n),-1,0,0,-2*z*n/(z-n),0]};
  assert.ok(verifyCamera(badCamera,expectedCamera).includes('actual camera position differs'),'live camera mismatch must reject');
  const offscreenBody={...b,id:'ball',position:[0,1,20],scale:[1,1,1]};
  const offscreenFrame={camera:{...badCamera,matrixWorld:[1,0,0,0,0,1,0,0,0,0,1,0,0,0,10,1]},bodies:[{id:'ball',geometryId:'ball',matrixWorld:[1,0,0,0,0,1,0,0,0,0,1,0,0,1,20,1]}]};
  const offscreenGeometry=new Map([['ball',{positions:[0,0,1,0,1,0,1,0,0]}]]),offscreenState={floorY:0,bodies:[offscreenBody],camera:expectedCamera};
  assert.ok(!checkLiveFrame(offscreenFrame,offscreenGeometry,offscreenState).pass,'proof keeps strict solid depth visibility by default');
  assert.ok(checkLiveFrame(offscreenFrame,offscreenGeometry,offscreenState,{checkSolidDepthRange:false}).pass,'explicit offscreen solids retain mesh/pose/camera validation without a visibility requirement');
  const floorStretch={...b,id:'floor-stretch',position:[0,1,0],scale:[1/Math.sqrt(1.25),1.25,1/Math.sqrt(1.25)]};
  assert.ok(Math.abs(floorStretch.scale.reduce((a,b)=>a*b,1)-1)<1e-12);
  assert.equal(floorStretch.position[1]-extents(floorStretch)[1],-.25);
  const crossing=t=>[{...b,scale:[.5,.5,.5],position:[-1+60*t,1,0]},{...b,scale:[.5,.5,.5],position:[1-60*t,1,0]}];
  assert.equal(axisGap(...crossing(0),0),1);assert.equal(axisGap(...crossing(1/30),0),1);assert.equal(axisGap(...crossing(1/60),0),-1);
  return {passed:true,counterexamples:{stale_undeformed_pair_gap:.1,deformed_pair_gap:axisGap(b,other,0),volume_preserving_floor_stretch_bottom:-.25,thirty_fps_endpoint_gap:1,between_frame_crossing_gap:-1},checks:['deformed support','volume-preserving bulge','floor anchoring','30fps tunnelling','continuous peak enclosure','live geometry containment','camera identity']};
}
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
// Updated only after independent source review; a changed motion source rejects.
const REVIEWED_MOTION_SHA='4453a3ddff995d410980add4dc9a29ee96de8de45f4edfcea092fdf943cfd504';
const REVIEWED_SCENE_SHA='665fd540eceee426e9a1b2c4f81c2df3b71355414c1a754ae4d49703db15fe17';
export async function runVerification({motionPath,livePath,probe=false}) {
  const source=fs.readFileSync(motionPath),sourceSha=sha(source);
  const motion=await import(pathToFileURL(path.resolve(motionPath)).href+'?qa='+sourceSha);
  const analytic=verifyAnalyticMotion(motion.sampleState,motion.motionContract);
  delete analytic.states;
  const failures=[];
  if(sourceSha!==REVIEWED_MOTION_SHA) failures.push('motion source differs from independently reviewed hash');
  if(!analytic.pass) failures.push('dense/continuous motion checks failed');
  const report={schema:1,scope:'Eight-second real3D contact proof; authored affine deformation, no full soft-body solver',source_hashes:{motion:{path:motionPath,sha256:sourceSha},verifier:{sha256:sha(fs.readFileSync(new URL(import.meta.url)))}},selftests:selfTest(),analytic,live:{pass:false,status:'not supplied'},limitations:['Geometry/collision checks do not establish tactile quality or a perceptual creative pass.','A failed conservative separation certificate is unresolved, never called collision-free.','Screen occlusion and physical intersection are separate gates.']};
  if(livePath) {
    const live=JSON.parse(fs.readFileSync(livePath,'utf8')),frames=live.frames||[];
    const geometries=new Map((Array.isArray(live.geometries)?live.geometries:Object.entries(live.geometries||{}).map(([id,g])=>({id,...g}))).map(g=>[g.id,g]));
    const liveFailures=[],unique=new Set();let vertices=0;
    if(live.width!==1920||live.height!==1080) liveFailures.push('actual renderer is not native1920x1080');
    const sourceHashes=live.source_hashes||{};
    const reportedMotion=sourceHashes.motion?.sha256||sourceHashes.motion;
    if(reportedMotion!==sourceSha) liveFailures.push('live probe motion source identity differs');
    const scenePath=sourceHashes.scene?.path||path.join(path.dirname(motionPath),'scene.mjs');
    const sceneSha=sourceHashes.scene?.sha256||sourceHashes.scene;
    if(!sceneSha||!fs.existsSync(scenePath)||sha(fs.readFileSync(scenePath))!==sceneSha) liveFailures.push('actual scene source identity unverified');
    else {report.source_hashes.scene={path:scenePath,sha256:sceneSha};if(sceneSha!==REVIEWED_SCENE_SHA) liveFailures.push('scene source differs from independently reviewed hash');}
    for(const frame of frames) {
      const frameNo=frame.frame??Math.round(frame.time*30);
      if(!Number.isInteger(frameNo)||!Number.isFinite(frame.time)||unique.has(frameNo)||Math.abs(frame.time-frameNo/30)>1e-9||frameNo<0||frameNo>=240) liveFailures.push(`bad native frame time:${frameNo}`);
      unique.add(frameNo);
      if(!frame.camera) liveFailures.push(`actual camera data missing:${frameNo}`);
      if(!frame.render_elements) liveFailures.push(`actual render inventory missing:${frameNo}`);
      const check=checkLiveFrame(frame,geometries,motion.sampleState(frame.time),live);
      vertices+=check.vertices;liveFailures.push(...check.failures.map(x=>`frame${frameNo}:${x}`));
    }
    if(probe?frames.length<4:unique.size!==240) liveFailures.push(probe?'fewer than4native probe frames':'full240native geometry frames required');
    report.live={pass:!liveFailures.length,status:probe?'native-probe-only':'full-native-geometry',frames:frames.length,vertex_reads:vertices,failures:liveFailures.slice(0,100),failure_count:liveFailures.length,probe_sha256:sha(fs.readFileSync(livePath)),geometry_count:geometries.size};
    if(!report.live.pass) failures.push('actual live mesh/camera checks failed');
  } else failures.push('actual live geometry evidence pending');
  report.pass=!failures.length;report.failures=failures;
  report.certification=report.pass?(probe?'PROBE PASS; full240-frame geometry gate still required':'PASS: dense+continuous+actual-native-geometry gates'):'REJECT / PENDING: no collision-free claim';
  return report;
}
async function main() {
  const args=process.argv.slice(2),value=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1]};
  if(args.includes('--self-test')) {console.log(JSON.stringify(selfTest()));return;}
  const root=path.resolve('.publication/sunset-launch-v11'),out=path.resolve(value('--out',path.join(root,'qa/motion-verification.json')));
  if(!out.startsWith(root+path.sep)) throw new Error('QA output must remain inside ignored v11 directory');
  const report=await runVerification({motionPath:value('--motion','projects/sunset/media/launch-v11/motion.mjs'),livePath:value('--live',null),probe:args.includes('--probe')});
  fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({pass:report.pass,certification:report.certification,analytic:report.analytic.pass,live:report.live.status,failures:report.failures,report:out}));
  if(!report.pass) process.exitCode=1;
}
if(process.argv[1]&&path.resolve(process.argv[1])===new URL(import.meta.url).pathname) main().catch(e=>{console.error(e);process.exitCode=1});
