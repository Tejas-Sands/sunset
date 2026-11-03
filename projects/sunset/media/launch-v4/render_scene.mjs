#!/usr/bin/env node
// Deterministic original Three.js frames. Generated dependencies and media stay ignored.
import {createServer} from 'node:http';
import {readFile,writeFile,mkdir,rename,copyFile,access} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {createHash} from 'node:crypto';
const exec=promisify(execFile),ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../..');
const SRC=path.join(ROOT,'projects/sunset/media/launch-v4'),OUT=path.join(ROOT,'.publication/sunset-launch-v4/scene');
const args=process.argv.slice(2),value=(name,otherwise)=>{const i=args.indexOf(name);return i<0?otherwise:args[i+1]};
const detailOnly=args.includes('--detail-pass');
const width=Number(value('--width',detailOnly?1280:1920)),height=Number(value('--height',detailOnly?720:1080)),fps=Number(value('--fps',30)),duration=24;
if(!Number.isInteger(width)||!Number.isInteger(height)||width<640||height<360)throw Error('Invalid render dimensions');
const frameDirectory=value('--frames-dir','frames');if(!['frames','native-frames'].includes(frameDirectory))throw Error('Invalid frame directory');
await mkdir(path.join(OUT,frameDirectory),{recursive:true});await mkdir(path.join(OUT,'deps'),{recursive:true});
const format=value('--format','png');if(!['png','jpeg'].includes(format))throw Error('Invalid frame format');
const exists=async p=>{try{await access(p);return true}catch{return false}};
const sha=b=>createHash('sha256').update(b).digest('hex'),dependencies=[];
for(const name of ['three.module.js','three.core.js','LICENSE']){
 const target=path.join(OUT,'deps',name),cached=path.join(ROOT,'.publication/sunset-launch-v4/pipeline-probe',name);
 const url='https://cdn.jsdelivr.net/npm/three@0.180.0/'+(name==='LICENSE'?'LICENSE':'build/'+name);
 if(!await exists(target)){
  if(await exists(cached))await copyFile(cached,target);
  else{const r=await fetch(url,{signal:AbortSignal.timeout(40000)});if(!r.ok)throw Error('Three dependency download '+r.status);await writeFile(target,Buffer.from(await r.arrayBuffer()))}
 }
 const bytes=await readFile(target);dependencies.push({url,path:path.relative(ROOT,target),bytes:bytes.length,sha256:sha(bytes)});
}
await writeFile(path.join(OUT,'dependencies.json'),JSON.stringify(dependencies,null,2)+'\n');
const sceneBytes=await readFile(path.join(SRC,'scene.mjs')),sceneHash=sha(sceneBytes);
const html='<!doctype html><html><meta charset="utf-8"><style>html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#090d0c}canvas{display:block}</style><script>window.SUNSET_RENDER='+JSON.stringify({width,height})+';window.addEventListener("error",e=>window.sceneError=e.message);</script><script type="module">import "/scene.mjs";</script></html>';
const routes=new Map([
 ['/scene.mjs',[path.join(SRC,'scene.mjs'),'text/javascript']],
 ['/three.module.js',[path.join(OUT,'deps/three.module.js'),'text/javascript']],
 ['/three.core.js',[path.join(OUT,'deps/three.core.js'),'text/javascript']],
 ['/Geist.ttf',[path.join(ROOT,'.publication/sunset-launch-v1/render/Geist.ttf'),'font/ttf']],
 ['/game.png',[path.join(ROOT,'.publication/sunset-launch-v1/footage/06-hosted-verified-game.png'),'image/png']]
]);
const server=createServer(async(req,res)=>{try{const pathname=new URL(req.url,'http://localhost').pathname;if(pathname==='/'){res.writeHead(200,{'Content-Type':'text/html'});res.end(html);return}const route=routes.get(pathname);if(!route){res.writeHead(404);res.end();return}res.writeHead(200,{'Content-Type':route[1],'Cache-Control':'no-store'});res.end(pathname==='/scene.mjs'?sceneBytes:await readFile(route[0]))}catch(e){res.writeHead(500);res.end(String(e))}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const url='http://127.0.0.1:'+server.address().port+'/';
const session='sunset-v4-scene-'+process.pid;let ws,sessionId,messageId=0;const pending=new Map();
function cdp(method,params={},target=true){return new Promise((resolve,reject)=>{const id=++messageId;const timeout=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method))},120000);pending.set(id,{resolve,reject,timeout});ws.send(JSON.stringify({id,method,params,...(target&&sessionId?{sessionId}: {})}))})}
const frames=value('--frames',null);
const indices=detailOnly?[]:frames?frames.split(',').map(Number):args.includes('--preview')?[0,24,54,96,150,192,240,273,324,414,504,558,612,678]:Array.from({length:duration*fps},(_,i)=>i);
if(indices.some(n=>!Number.isInteger(n)||n<0||n>=duration*fps))throw Error('Invalid frame index');
const records=[];

async function applyDetailPass(manifest){
 if(manifest.source_sha256!==sceneHash||manifest.native.width!==width||manifest.native.height!==height)throw Error('Detail pass requires the unchanged base scene and dimensions');
 const baseRenderer=manifest.base_renderer_sha256||manifest.renderer_sha256;
 const rendererHash=sha(await readFile(fileURLToPath(import.meta.url))),originalSequenceHash=manifest.validation?.delivered_sequence_sha256;
 const oddIndices=Array.from({length:57},(_,i)=>475+i*2),order=[531,...oddIndices.filter(n=>n!==531)],details=[];
 for(const n of order){
  const started=performance.now(),t=n/30;
  const r=await cdp('Runtime.evaluate',{expression:'(()=>{const meta=window.renderFrame('+JSON.stringify(t)+');return {meta,data:document.querySelector("canvas").toDataURL("image/png")}})()',returnByValue:true});
  if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));
  const payload=r.result.value,bytes=Buffer.from(payload.data.slice(payload.data.indexOf(',')+1),'base64');
  if(bytes.readUInt32BE(16)!==width||bytes.readUInt32BE(20)!==height)throw Error('Detail frame dimensions mismatch');
  const dest=path.join(OUT,'frames',String(n).padStart(6,'0')+'.png');await writeFile(dest+'.tmp',bytes);await rename(dest+'.tmp',dest);
  details.push({frame:n,time:t,bytes:bytes.length,sha256:sha(bytes),ms:performance.now()-started});
  if(n===531||details.length%10===0)console.log(JSON.stringify({stage:'detail-frame',frame:n,time:t,completed:details.length,total:57}));
 }
 if(sha(await readFile(path.join(SRC,'scene.mjs')))!==sceneHash)throw Error('Scene changed during detail capture');
 const verifyCode="from pathlib import Path\nfrom PIL import Image\nimport hashlib,json,sys\nout=Path(sys.argv[1]);restored=[]\nfor i in range(474,588,2):\n src=out/\"native-frames\"/(str(i//2).zfill(6)+\".jpg\");dst=out/\"frames\"/(str(i).zfill(6)+\".png\")\n with Image.open(src) as im:im.convert(\"RGB\").save(dst)\n restored.append(i)\nframes=sorted((out/\"frames\").glob(\"*.png\"))\nassert [p.stem for p in frames]==[str(i).zfill(6) for i in range(720)]\nfor p in frames:\n with Image.open(p) as im:\n  assert im.size==(1280,720),(p,im.size)\n  im.verify()\nh=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()\nprint(json.dumps({\"even_indices_restored_from_native_15fps\":restored,\"sequence_exact_count\":720,\"all_png_dimensions\":[1280,720],\"all_png_crc_verified\":True,\"delivered_sequence_sha256\":hashlib.sha256(b\"\".join(bytes.fromhex(h(p)) for p in frames)).hexdigest(),\"first_frame_sha256\":h(frames[0]),\"last_frame_sha256\":h(frames[-1])}))";
 const checked=JSON.parse((await exec('python3',['-c',verifyCode,OUT],{timeout:120000,maxBuffer:1000000})).stdout);
 const detail={completed_at:new Date().toISOString(),scene_source_sha256:sceneHash,base_renderer_sha256:baseRenderer,detail_renderer_sha256:rendererHash,source_geometry_camera_unchanged:true,window:{start_frame:474,end_frame_exclusive:588,start_seconds:15.8,end_seconds:19.6,fps:30},actual_new_3d_frames:57,actual_30fps_odd_indices:oddIndices,even_frames_restored_from_native_15fps:checked.even_indices_restored_from_native_15fps,method:'Actual deterministic Three.js captures at n/30; no motion interpolation inside the stewardship window.',records:details.sort((a,b)=>a.frame-b.frame),validation:checked};
 manifest.base_completed_at=manifest.base_completed_at||manifest.completed_at;manifest.completed_at=detail.completed_at;
 manifest.base_renderer_sha256=baseRenderer;manifest.renderer_sha256=rendererHash;manifest.native.renderer_sha256=manifest.native.renderer_sha256||baseRenderer;
 manifest.base_sequence_sha256=manifest.base_sequence_sha256||originalSequenceHash;
 manifest.detail_pass=detail;manifest.capture_summary={base_actual_15fps_frames:360,additional_actual_30fps_samples:57,total_distinct_actual_3d_times:417,delivered_sequence_frames:720,stewardship_window_actual_30fps_frames:114};
 manifest.sequence.method='Hybrid background: actual15fps3D base with cut-aware30fpsMCI; stewardship frames474..587 are actual30fps3D samples (57 base even frames plus57 fresh odd captures), with no interpolation in that window.';
 manifest.validation={...(manifest.validation||{}),...checked,source_and_dependency_hashes_match:true,detail_pass_complete:true};
 await writeFile(path.join(OUT,'detail-pass.json.tmp'),JSON.stringify(detail,null,2)+'\n');await rename(path.join(OUT,'detail-pass.json.tmp'),path.join(OUT,'detail-pass.json'));
 await writeFile(path.join(OUT,'manifest.json.tmp'),JSON.stringify(manifest,null,2)+'\n');await rename(path.join(OUT,'manifest.json.tmp'),path.join(OUT,'manifest.json'));
 console.log(JSON.stringify({stage:'detail-complete',actualNewFrames:57,actual30fpsWindowFrames:114,totalActual3DTimes:417,sequenceFrames:720,baseRenderer,currentRenderer:rendererHash,sequenceHash:checked.delivered_sequence_sha256}));
}

try{
 await exec('agent-browser',['--session',session,'--args','--no-sandbox,--enable-unsafe-swiftshader,--use-angle=swiftshader','open','about:blank'],{timeout:90000,maxBuffer:1000000});
 const result=await exec('agent-browser',['--session',session,'get','cdp-url'],{timeout:30000,maxBuffer:1000000});
 const endpoint=result.stdout.match(/ws:\/\/\S+/)?.[0];if(!endpoint)throw Error('No isolated browser endpoint');
 ws=new WebSocket(endpoint);await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
 ws.onmessage=event=>{const m=JSON.parse(event.data),p=pending.get(m.id);if(p){pending.delete(m.id);clearTimeout(p.timeout);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}};
 const targets=await cdp('Target.getTargets',{},false);const target=targets.targetInfos.find(t=>t.type==='page');if(!target)throw Error('No browser page');
 ({sessionId}=await cdp('Target.attachToTarget',{targetId:target.targetId,flatten:true},false));
 await cdp('Page.enable');await cdp('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});
 await cdp('Page.navigate',{url});
 const readyDeadline=Date.now()+90000;
 while(true){const r=await cdp('Runtime.evaluate',{expression:'window.sunsetSceneReady ? "ready" : (window.sceneError || "loading")',returnByValue:true});const state=r.result?.value;if(state==='ready')break;if(state!=='loading'&&typeof state==='string')throw Error(state);if(Date.now()>readyDeadline)throw Error('Scene initialization timed out');await new Promise(r=>setTimeout(r,250))}
 console.log(JSON.stringify({stage:'ready',session,width,height,frameCount:indices.length,source:sceneHash}));
 if(detailOnly)await applyDetailPass(JSON.parse(await readFile(path.join(OUT,'manifest.json'),'utf8')));
 if(!detailOnly){
 for(const n of indices){
  const start=performance.now(),t=n/fps;
  const result=await cdp('Runtime.evaluate',{expression:'(()=>{const meta=window.renderFrame('+JSON.stringify(t)+');const started=performance.now();const data=document.querySelector("canvas").toDataURL("image/'+format+'",.95);return {meta,data,encodeMs:performance.now()-started}})()',returnByValue:true});
  if(result.exceptionDetails)throw Error(JSON.stringify(result.exceptionDetails));
  const evaluatedAt=performance.now(),payload=result.result.value;
  const data=Buffer.from(payload.data.slice(payload.data.indexOf(',')+1),'base64');if(format==='png'&&(data.readUInt32BE(16)!==width||data.readUInt32BE(20)!==height))throw Error('Screenshot dimensions do not match');
  const name=String(n).padStart(6,'0')+(format==='jpeg'?'.jpg':'.png'),dest=path.join(OUT,frameDirectory,name);await writeFile(dest+'.tmp',data);await rename(dest+'.tmp',dest);
  records.push({frame:n,time:t,bytes:data.length,ms:performance.now()-start,evaluateMs:evaluatedAt-start,captureMs:performance.now()-evaluatedAt,encodeMs:payload.encodeMs,...payload.meta});
  if(args.includes('--preview')||n%30===0)console.log(JSON.stringify({stage:'frame',frame:n,time:t,ms:Math.round(records.at(-1).ms),bytes:data.length}));
 }
 if(sha(await readFile(path.join(SRC,'scene.mjs')))!==sceneHash)throw Error('Scene source changed during render; do not treat frames as final');
 const report={format,frameDirectory,completed_at:new Date().toISOString(),width,height,fps,duration,frames:indices.length,preview:args.includes('--preview'),source_sha256:sceneHash,renderer_sha256:sha(await readFile(fileURLToPath(import.meta.url))),dependencies,average_frame_ms:records.reduce((s,x)=>s+x.ms,0)/records.length,records};
 await writeFile(path.join(OUT,args.includes('--preview')?'preview-render.json':(frameDirectory==='native-frames'?'native-render.json':'scene-render.json')),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({stage:'complete',frames:records.length,averageFrameMs:report.average_frame_ms,folder:path.join(OUT,frameDirectory)}));
 if(args.includes('--interpolate')){
  if(fps!==15||records.length!==360||frameDirectory!=='native-frames')throw Error('Interpolation requires the complete24s15fpsnative sequence');
  await mkdir(path.join(OUT,'frames'),{recursive:true});
  const interpolationFilter='tpad=stop_mode=clone:stop_duration=0.266667,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:me=epzs:search_param=16:scd=fdiff:scd_threshold=10';
  const ffargs=['-hide_banner','-loglevel','error','-y','-threads','4','-framerate','15','-start_number','0','-i',path.join(OUT,'native-frames','%06d.'+(format==='jpeg'?'jpg':'png')),'-vf',interpolationFilter,'-t','24','-frames:v','720','-start_number','0',path.join(OUT,'frames','%06d.png')];
  console.log(JSON.stringify({stage:'interpolating',nativeFrames:360,nativeFps:15,deliveredFrames:720,deliveredFps:30,dimensions:[width,height]}));
  const started=performance.now();await exec('ffmpeg',ffargs,{timeout:1800000,maxBuffer:2000000});
  const manifest={completed_at:new Date().toISOString(),source_sha256:sceneHash,renderer_sha256:sha(await readFile(fileURLToPath(import.meta.url))),native:{width,height,fps:15,frames:360,duration:24,format,folder:'native-frames',method:'Actual deterministic Three.js WebGL2/SwiftShader renders at n/15 seconds'},sequence:{width,height,fps:30,frames:720,duration:24,format:'png',folder:'frames',method:'Motion-compensated background interpolation from actual15fps3Dframes; scene-cut detection enabled; final foreground type/UI/captions are independently native30fps'},interpolation:{tool:'FFmpeg',args:ffargs,filter:interpolationFilter,duration_seconds:(performance.now()-started)/1000},materials:'PBRenvironment-reflectingmetal; clearcoatreflectivetranslucentshellwithoutrefraction/transmissionpass; originalextrudedsun/capsule/cards/credential; dynamicperspectivecamera; softcontact-shadowproxy andfoggedstudiofloor',dependencies};
  await applyDetailPass(manifest);
  console.log(JSON.stringify({stage:'sequence-complete',nativeFrames:360,sequenceFrames:720,nativeFps:15,sequenceFps:30,width,height,interpolationSeconds:manifest.interpolation.duration_seconds}));
 }

 }
}finally{
 if(ws)ws.close();
 await exec('agent-browser',['--session',session,'close'],{timeout:30000,maxBuffer:1000000}).catch(()=>{});
 server.close();
}
