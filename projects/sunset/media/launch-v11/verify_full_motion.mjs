// Scene-specific continuation QA. Reuse the reviewed proof; do not invent a solver.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {modelIntervals as proofIntervals,checkState,checkLiveFrame,pressureRange,selfTest as proofSelfTest} from './verify_motion.mjs';
import {sampleState} from './motion-full.mjs';

// Plan: independently enclose the frozen authored equations; verify every sampled
// state against them; certify all between-state supports; inspect actual native
// mesh/camera exports. The first eight seconds retain their separate six-body
// live evidence. This model's extra offscreen bodies are not claimed as captured.
const EPS=2e-6,ROUND=1e-12,SKIN=.004;
const IDS=['handbook-core','handbook-cover','sunset-seal','support-left','support-right','support-rear','copy-left','copy-right'];
const R=[[1.65,1,0,.35],[1.78,1.13,0,.22],[.37,.24,.03,.28],[.25,.25,.25,.25],[.25,.25,.25,.25],[.25,.25,.25,.25],[1.65,1,0,.35],[1.65,1,0,.35]];
const CAM=[
 [8,[.15,1.65,5.5],[0,1.35,.35],32],[10.5,[4,3.9,8.2],[0,1.2,0],36],
 [11.5,[-1.8,3.2,6.5],[-1.8,1.8,.4],34],[13.2,[-3.8,1.75,5.2],[-3.5,.45,.5],34],
 [15.4,[-3.2,2.4,7],[-1.6,1.2,0],36],[19,[4.2,4.5,9.2],[0,1.3,-.5],38],
 [24,[.4,3.8,9.4],[0,1.35,0],36],[27.6,[.15,4,14.5],[0,1.35,0],40],
 [30,[.15,3.1,13.4],[0,1.35,0],40],[34,[.15,3.1,13.4],[0,1.35,0],40]
];
const I=x=>Array.isArray(x)?x:[x,x];
const add=(...xs)=>xs.map(I).reduce((a,b)=>[a[0]+b[0]-ROUND,a[1]+b[1]+ROUND],[0,0]);
const neg=x=>{x=I(x);return [-x[1],-x[0]]};
const sub=(a,b)=>add(a,neg(b));
const mul=(a,b)=>{a=I(a);b=I(b);const p=[a[0]*b[0],a[0]*b[1],a[1]*b[0],a[1]*b[1]];return [Math.min(...p)-ROUND,Math.max(...p)+ROUND]};
const mix=(a,b,q)=>add(a,mul(sub(b,a),q));
const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
const move=(t,a,b)=>smooth((t-a)/(b-a));
const travel=(a,b,start,end)=>[move(a,start,end)-ROUND,move(b,start,end)+ROUND];
const bump=(t,a,b,c)=>t<a||t>=c?0:t<b?smooth((t-a)/(b-a)):1-smooth((t-b)/(c-b));
function bumpRange(a,b,start,peak,end) {
 const v=[a,b,...[start,peak,end].filter(t=>t>a&&t<b)].map(t=>bump(t,start,peak,end));
 return [Math.min(...v)-ROUND,Math.max(...v)+ROUND];
}
function ySquash(a,b,contact,amount) {
 const y=sub(1,pressureRange(a,b,contact,amount)),bulge=[y[1]**-.5-ROUND,y[0]**-.5+ROUND];
 return [bulge,y,bulge];
}
function cameraPoint(t) {
 let a=CAM[0],b=a;for(let i=1;i<CAM.length;i++){b=CAM[i];if(t<=b[0])break;a=b;}
 const q=a===b?0:move(t,a[0],b[0]);
 return {position:a[1].map((v,i)=>v+(b[1][i]-v)*q),target:a[2].map((v,i)=>v+(b[2][i]-v)*q),fov:a[3]+(b[3]-a[3])*q};
}
function cameraRange(a,b) {
 const points=[a,b,...CAM.map(k=>k[0]).filter(t=>t>a&&t<b)].map(cameraPoint);
 const range=v=>[Math.min(...v)-ROUND,Math.max(...v)+ROUND];
 return {position:[0,1,2].map(i=>range(points.map(p=>p.position[i]))),target:[0,1,2].map(i=>range(points.map(p=>p.target[i]))),fov:range(points.map(p=>p.fov)),near:.08,far:60,aspect:16/9};
}
const pairKey=(a,b)=>[a,b].sort().join('|');
const lowerAbs=v=>v[0]<=0&&v[1]>=0?0:Math.min(Math.abs(v[0]),Math.abs(v[1]));
function pairLower(a,b) {return Math.max(...[0,1,2].map(k=>lowerAbs(sub(a.position[k],b.position[k]))-a.e[k][1]-b.e[k][1]));}

export function fullIntervals(a,b) {
 const copies=[[-1,24,26.7],[1,24.3,27]].map(([sign,start,land],j)=>{
  const scale=ySquash(a,b,land,.18),e=scale.map((q,k)=>mul(R[j+6][k]+R[j+6][3],q));
  const lift=mul(1.1,bumpRange(a,b,start,(start+land)/2,land));
  return {id:IDS[j+6],scale,e,position:[mul(sign,mix(12,4.5,travel(a,b,start,land))),add(e[1],SKIN,lift),I(0)],floor:add(SKIN,lift)};
 });
 if(b<=8) {const proof=proofIntervals(a,b);return {...proof,bodies:[...proof.bodies,...copies]};}
 const scale=[[[1,1],[1,1],[1,1]],[[1,1],[1,1],[1,1]],ySquash(a,b,13.2,.22),ySquash(a,b,18.3,.22),ySquash(a,b,18.3,.22),ySquash(a,b,18.7,.22)];
 const e=scale.map((s,i)=>s.map((q,k)=>mul(R[i][k]+R[i][3],q)));
 const sealAir=mul(3.88,sub(1,travel(a,b,11.5,13.2))),sideAir=mul(1.3,bumpRange(a,b,15.4,16.7,18.3)),rearAir=mul(1.1,bumpRange(a,b,15.8,17.1,18.7));
 const sideX=mix(add(2.504,mul(.05,travel(a,b,8,8.6))),6,travel(a,b,16.3,18.3));
 const rearZ=mix(add(.854,mul(.05,travel(a,b,8,8.6))),4.5,travel(a,b,15.8,18.7));
 const positions=[
  [I(0),I(1.354),I(0)],[I(0),mix(4.354,8,travel(a,b,8,10.5)),I(2.224)],
  [mix(.25,-4.4,travel(a,b,10.3,11.5)),add(e[2][1],SKIN,sealAir),I(1.108)],
  [neg(sideX),add(e[3][1],SKIN,sideAir),mul(-2,travel(a,b,15.4,16.3))],
  [sideX,add(e[4][1],SKIN,sideAir),mul(-2,travel(a,b,15.4,16.3))],
  [I(0),add(e[5][1],SKIN,rearAir),neg(rearZ)]
 ];
 const floor=[I(SKIN),sub(positions[1][1],e[1][1]),add(SKIN,sealAir),add(SKIN,sideAir),add(SKIN,sideAir),add(SKIN,rearAir)];
 return {bodies:[...IDS.slice(0,6).map((id,i)=>({id,position:positions[i],scale:scale[i],e:e[i],floor:floor[i]})),...copies],camera:cameraRange(a,b),pairs:{}};
}

export function verifyFullMotion(sample) {
 const failures=[],min={floor:Infinity,pair:Infinity,camera:Infinity},maxDisplacement=Object.fromEntries(IDS.map(id=>[id,0]));
 for(let i=0;i<=34*240;i++) {
  const t=i/240,s=sample(t),wanted=fullIntervals(t,t),check=checkState(s,{cameraClearance:.01});
  failures.push(...check.failures.map(x=>`sample:t=${t}:${x}`));
  if(s.bodies.length!==8)failures.push(`body count differs:t=${t}`);
  for(const [j,id] of IDS.entries()) {
   const body=s.bodies.find(x=>x.id===id),expect=wanted.bodies.find(x=>x.id===id);
   if(!body){failures.push(`body missing:${id}:t=${t}`);continue;}
   for(const field of ['position','scale'])for(let k=0;k<3;k++)if(body[field][k]<expect[field][k][0]-EPS||body[field][k]>expect[field][k][1]+EPS)failures.push(`reviewed equation mismatch:${id}:${field}:${k}:t=${t}`);
   if(body.rest.kind!=='roundedBox'||body.rest.core.some((v,k)=>Math.abs(v-R[j][k])>EPS)||Math.abs(body.rest.radius-R[j][3])>EPS)failures.push(`rest support differs:${id}`);
   if(Math.abs(body.scale.reduce((a,b)=>a*b,1)-1)>1e-10)failures.push(`volume changed:${id}:t=${t}`);
  }
  for(const field of ['position','target'])for(let k=0;k<3;k++)if(s.camera[field][k]<wanted.camera[field][k][0]-EPS||s.camera[field][k]>wanted.camera[field][k][1]+EPS)failures.push(`camera equation mismatch:${field}:t=${t}`);
  if(s.floorY!==0||s.camera.fov<wanted.camera.fov[0]-EPS||s.camera.fov>wanted.camera.fov[1]+EPS||s.camera.near!==.08||s.camera.far!==60||Math.abs(s.camera.aspect-16/9)>1e-12)failures.push(`camera/stage constants differ:t=${t}`);
 }
 for(let i=0;i<34*240;i++) {
  const a=i/240,b=(i+1)/240,v=fullIntervals(a,b),start=sample(a);
  for(const body of v.bodies) {
   min.floor=Math.min(min.floor,body.floor[0]);if(body.floor[0]<SKIN-1e-8)failures.push(`continuous floor unresolved:${body.id}:${a}-${b}`);
   const at=start.bodies.find(x=>x.id===body.id),j=IDS.indexOf(body.id);
   const centre=Math.hypot(...[0,1,2].map(k=>Math.max(Math.abs(body.position[k][0]-at.position[k]),Math.abs(body.position[k][1]-at.position[k]))));
   const deformation=Math.hypot(...[0,1,2].map(k=>(R[j][k]+R[j][3])*Math.max(Math.abs(body.scale[k][0]-at.scale[k]),Math.abs(body.scale[k][1]-at.scale[k]))));
   maxDisplacement[body.id]=Math.max(maxDisplacement[body.id],centre+deformation);
  }
  for(let j=0;j<8;j++)for(let k=j+1;k<8;k++) {
   const gap=v.pairs[pairKey(IDS[j],IDS[k])]?.[0]??pairLower(v.bodies[j],v.bodies[k]);
   min.pair=Math.min(min.pair,gap);if(gap<SKIN-1e-8)failures.push(`continuous pair unresolved:${IDS[j]}:${IDS[k]}:${a}-${b}:${gap}`);
  }
  const camera=v.camera,radius=camera.near*Math.sqrt(1+Math.tan(camera.fov[1]*Math.PI/360)**2*(1+camera.aspect**2))+.01;
  for(const body of v.bodies) {
   const gap=Math.max(...[0,1,2].map(k=>lowerAbs(sub(camera.position[k],body.position[k]))-body.e[k][1]-radius));
   min.camera=Math.min(min.camera,gap);if(gap<0)failures.push(`continuous camera clearance unresolved:${body.id}:${a}-${b}:${gap}`);
  }
 }
 return {pass:!failures.length,failures:failures.slice(0,100),failure_count:failures.length,samples:8161,intervals:8160,substep_hz:240,pairs_per_interval:28,min_gaps:min,max_enclosed_substep_surface_displacement:maxDisplacement,certificate:'Independent interval replay of the frozen scene-specific equations, including exact anchored floor gaps and the reviewed proof contact cancellations. Every interval and all28pairs are certified; unresolved bounds reject.'};
}

export function selfTest() {
  const valid=verifyFullMotion(sampleState);
  assert.equal(valid.pass,true,'reviewed continuation must enclose all 34 seconds without intersections');
  const bad=verifyFullMotion(t=>{const s=sampleState(t);if(t>=24&&t<24.1){const copy=s.bodies.find(b=>b.id==='copy-left');copy.position=[0,1.354,0];}return s;});
  assert.ok(!bad.pass&&bad.failures.some(x=>x.includes('pair separation unresolved')),'an actual kept copy crossing the core must reject');
  return {pass:true,checks:['eight-body continuation','copy/core penetration rejects']};
}

const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const SOURCE={
 motion:['motion-full.mjs','a40653d3b7e37c4a697a571944594186754adcdceb31170c048ececcbd6fba8a'],
 scene:['scene-full.mjs','b1c48414882543d3bb7c7b2cc417918224c9f02a067ccd83c36b30b998251ba9'],
 renderer:['render_full_scene.mjs','6bd29b6440dff380e8afa76db48e773c8e14be42cae5210ee5af4bcd98b5123c'],
 proof_motion:['motion.mjs','4453a3ddff995d410980add4dc9a29ee96de8de45f4edfcea092fdf943cfd504'],
 proof_scene:['scene.mjs','665fd540eceee426e9a1b2c4f81c2df3b71355414c1a754ae4d49703db15fe17']
};
const NATIVE=[...Array.from({length:330},(_,i)=>240+i),...Array.from({length:180},(_,i)=>720+i)];
export function runVerification({livePath,probe=false}) {
 const failures=[],analytic=verifyFullMotion(sampleState),sources={};
 if(!analytic.pass)failures.push('full dense/continuous certificate failed');
 const live=JSON.parse(fs.readFileSync(livePath)),liveFailures=[];
 for(const [key,[name,pin]] of Object.entries(SOURCE)) {
  const sourcePath=new URL(name,import.meta.url),actual=sha(fs.readFileSync(sourcePath)),reported=live.source_hashes?.[key];
  sources[key]={path:path.relative('.',sourcePath.pathname),sha256:actual};
  if(actual!==pin)failures.push(`source differs from reviewed pin:${key}`);
  if(reported?.sha256!==actual||path.resolve(reported?.path||'')!==sourcePath.pathname)liveFailures.push(`actual live source identity differs:${key}`);
 }
 sources.verifier={path:path.relative('.',new URL(import.meta.url).pathname),sha256:sha(fs.readFileSync(new URL(import.meta.url)))};
 sources.proof_verifier={path:'projects/sunset/media/launch-v11/verify_motion.mjs',sha256:sha(fs.readFileSync(new URL('verify_motion.mjs',import.meta.url)))};
 const proofPath=path.resolve('.publication/sunset-launch-v11/qa/proof-native-verification.json'),proof=JSON.parse(fs.readFileSync(proofPath));
 if(!proof.pass||proof.live?.frames!==240||proof.live?.status!=='full-native-geometry'||proof.source_hashes?.motion?.sha256!==SOURCE.proof_motion[1]||proof.source_hashes?.scene?.sha256!==SOURCE.proof_scene[1]||proof.source_hashes?.verifier?.sha256!==sources.proof_verifier.sha256)failures.push('separate original240-frame proof gate is missing or stale');
 if(live.width!==1920||live.height!==1080||live.fps!==30||live.duration!==34)liveFailures.push('native dimensions/timebase differ');
 const geometries=new Map((live.geometries||[]).map(g=>[g.id,g])),unique=new Set();let vertexReads=0;
 if(geometries.size!==8)liveFailures.push('eight actual solid geometries required');
 for(const frame of live.frames||[]) {
  if(!Number.isInteger(frame.frame)||!Number.isFinite(frame.time)||Math.abs(frame.time-frame.frame/30)>1e-9||unique.has(frame.frame)||!NATIVE.includes(frame.frame))liveFailures.push(`bad native continuation frame:${frame.frame}`);
  unique.add(frame.frame);
  if(!frame.camera||!frame.render_elements)liveFailures.push(`actual camera/render inventory missing:${frame.frame}`);
  const checked=checkLiveFrame(frame,geometries,sampleState(frame.time),{width:1920,height:1080,checkSolidDepthRange:false});
  vertexReads+=checked.vertices;liveFailures.push(...checked.failures.map(x=>`frame${frame.frame}:${x}`));
 }
 if(probe?unique.size<4:unique.size!==510||NATIVE.some(i=>!unique.has(i)))liveFailures.push(probe?'at least4native continuation probe frames required':'exactly510native continuation geometry frames required');
 const renderPath=path.join(path.dirname(path.dirname(livePath)),'scene',path.basename(livePath).replace(/-live\.json$/,'-render.json'));
 const metadata=JSON.parse(fs.readFileSync(renderPath)),records=metadata.records||[],recordIds=new Set(records.map(r=>r.frame));
 if(records.length!==unique.size||recordIds.size!==unique.size||[...unique].some(i=>!recordIds.has(i)))liveFailures.push('native renderer records do not cover live frames');
 for(const record of records)if(record.drawingBufferWidth!==1920||record.drawingBufferHeight!==1080||record.width!==1920||record.height!==1080||record.pixelRatio!==1||record.actual_context_antialias!==true||record.actual_samples<4||Math.abs(record.time-record.frame/30)>1e-9)liveFailures.push(`actual native renderer metadata differs:${record.frame}`);
 for(const key of Object.keys(SOURCE))if(metadata.source_hashes?.[key]?.sha256!==sources[key].sha256)liveFailures.push(`renderer source identity differs:${key}`);
 if(liveFailures.length)failures.push('actual continuation mesh/camera/native-source gate failed');
 return {schema:1,pass:!failures.length,failures,scope:'Frozen34s authored affine-deformation timeline, not a full soft-body solver',source_hashes:sources,selftests:proofSelfTest(),analytic,
  original_proof:{pass:proof.pass,frames:240,bodies:6,time_interval:[0,8],report:path.relative('.',proofPath),sha256:sha(fs.readFileSync(proofPath))},
  live:{pass:!liveFailures.length,status:probe?'native-continuation-probe-only':'full-native-continuation',frames:unique.size,geometries:geometries.size,vertex_reads:vertexReads,failures:liveFailures.slice(0,100),failure_count:liveFailures.length,source_sha256:sha(fs.readFileSync(livePath)),render_metadata_sha256:sha(fs.readFileSync(renderPath)),native:{width:1920,height:1080,fps:30,samples:4},expected_frame_ranges:[[240,570],[720,900]]},
  visibility_policy:'Every solid has spatial camera near-plane clearance. Deliberately offscreen copies may lie outside the view frustum; essential text/framing is a separate review gate.',
  phase_scope:'Actual0–8s proof has6bodies under the original source. Continuation capture has8bodies at8–19s and24–30s. The8body mathematical model at0–8s is not claimed as actual8body capture. Opaque genuine UI19–24s and endcard30–34s are separate composition gates.',
  limitations:['Analytic certificates and mesh containment do not establish tactile quality or perceptual pacing.','All supports and camera checks are conservative; any unresolved certificate rejects.','Screen occlusion, essential text and physical intersections remain separate gates.'],
  certification:failures.length?'REJECT / PENDING: no full continuation claim':probe?'PROBE PASS; all510actual continuation frames still required':'PASS: original240proof frames +510continuation frames, dense and continuous support certificates'};
}
async function main() {
 const args=process.argv.slice(2),value=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1]};
 if(args.includes('--self-test')){console.log(JSON.stringify(selfTest()));return;}
 const root=path.resolve('.publication/sunset-launch-v11'),out=path.resolve(value('--out',path.join(root,'qa/full-motion-verification.json')));
 if(!out.startsWith(root+path.sep))throw Error('QA output must remain inside ignored v11 directory');
 const livePath=value('--live',null);if(!livePath)throw Error('Actual continuation live export required');
 const report=runVerification({livePath,probe:args.includes('--probe')});
 fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({pass:report.pass,certification:report.certification,analytic:report.analytic.pass,frames:report.live.frames,failures:report.failures,live_failures:report.live.failures,report:out}));
 if(!report.pass)process.exitCode=1;
}
if(process.argv[1]&&path.resolve(process.argv[1])===new URL(import.meta.url).pathname)main().catch(e=>{console.error(e);process.exitCode=1});
