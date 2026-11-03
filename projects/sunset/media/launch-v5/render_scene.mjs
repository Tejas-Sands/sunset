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
const SRC=path.join(ROOT,'projects/sunset/media/launch-v5'),OUT=path.join(ROOT,'.publication/sunset-launch-v5/scene');
const args=process.argv.slice(2),value=(name,otherwise)=>{const i=args.indexOf(name);return i<0?otherwise:args[i+1]};
const width=1920,height=1080,fps=30,duration=24,format='png',frameDirectory='frames';
if(args.some(x=>['--interpolate','--detail-pass','--format','--fps','--width','--height','--frames-dir'].includes(x)))throw Error('v5 requires native1920x1080/30fps/PNG; no interpolation or alternate capture path');
await mkdir(path.join(OUT,frameDirectory),{recursive:true});await mkdir(path.join(OUT,'deps'),{recursive:true});
const exists=async p=>{try{await access(p);return true}catch{return false}};
const sha=b=>createHash('sha256').update(b).digest('hex'),dependencies=[];
for(const name of ['three.module.js','three.core.js','LICENSE']){
 const target=path.join(OUT,'deps',name),cached=path.join(ROOT,'.publication/sunset-launch-v4/scene/deps',name);
 const url='https://cdn.jsdelivr.net/npm/three@0.180.0/'+(name==='LICENSE'?'LICENSE':'build/'+name);
 if(!await exists(target)){
  if(await exists(cached))await copyFile(cached,target);
  else{const r=await fetch(url,{signal:AbortSignal.timeout(40000)});if(!r.ok)throw Error('Three dependency download '+r.status);await writeFile(target,Buffer.from(await r.arrayBuffer()))}
 }
 const bytes=await readFile(target);dependencies.push({url,path:path.relative(ROOT,target),bytes:bytes.length,sha256:sha(bytes)});
}
await writeFile(path.join(OUT,'dependencies.json'),JSON.stringify(dependencies,null,2)+'\n');
const sceneBytes=await readFile(path.join(SRC,'scene.mjs')),sceneHash=sha(sceneBytes);
const html='<!doctype html><html><meta charset="utf-8"><style>html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#111417}canvas{display:block}</style><script>window.SUNSET_RENDER='+JSON.stringify({width,height})+';window.addEventListener("error",e=>window.sceneError=e.message);</script><script type="module">import "/scene.mjs";</script></html>';
const routes=new Map([
 ['/scene.mjs',[path.join(SRC,'scene.mjs'),'text/javascript']],
 ['/three.module.js',[path.join(OUT,'deps/three.module.js'),'text/javascript']],
 ['/three.core.js',[path.join(OUT,'deps/three.core.js'),'text/javascript']],
 ['/Geist.ttf',[path.join(ROOT,'.publication/sunset-launch-v1/render/Geist.ttf'),'font/ttf']]
]);
const server=createServer(async(req,res)=>{try{const pathname=new URL(req.url,'http://localhost').pathname;if(pathname==='/'){res.writeHead(200,{'Content-Type':'text/html'});res.end(html);return}const route=routes.get(pathname);if(!route){res.writeHead(404);res.end();return}res.writeHead(200,{'Content-Type':route[1],'Cache-Control':'no-store'});res.end(pathname==='/scene.mjs'?sceneBytes:await readFile(route[0]))}catch(e){res.writeHead(500);res.end(String(e))}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const url='http://127.0.0.1:'+server.address().port+'/';
const session='sunset-v5-scene-'+process.pid;let ws,sessionId,messageId=0;const pending=new Map();
function cdp(method,params={},target=true){return new Promise((resolve,reject)=>{const id=++messageId;const timeout=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method))},120000);pending.set(id,{resolve,reject,timeout});ws.send(JSON.stringify({id,method,params,...(target&&sessionId?{sessionId}: {})}))})}
const visibleIndices=[...Array.from({length:486},(_,i)=>i),...Array.from({length:42},(_,i)=>588+i)];
const frames=value('--frames',null),preview=args.includes('--preview');
const indices=frames?frames.split(',').map(Number):preview?[0,17,45,88,96,113,150,153,174,218,236,257,300,304,316,368,394,420,435,467,592,615]:visibleIndices;
if(indices.some(n=>!Number.isInteger(n)||!visibleIndices.includes(n))||new Set(indices).size!==indices.length)throw Error('Invalid or hidden frame index');
const records=[];
const rendererHash=sha(await readFile(fileURLToPath(import.meta.url)));
async function capture(n){
 const start=performance.now(),t=n/fps;
 const result=await cdp('Runtime.evaluate',{expression:'(()=>{const meta=window.renderFrame('+JSON.stringify(t)+');const started=performance.now();const data=document.querySelector("canvas").toDataURL("image/png");return {meta,data,encodeMs:performance.now()-started}})()',returnByValue:true});
 if(result.exceptionDetails)throw Error(JSON.stringify(result.exceptionDetails));
 const payload=result.result.value;
 if(!payload.meta.actual_context_antialias||payload.meta.actual_samples<4)throw Error('Native MSAA4 required');
 const bytes=Buffer.from(payload.data.slice(payload.data.indexOf(',')+1),'base64');
 if(bytes.readUInt32BE(16)!==width||bytes.readUInt32BE(20)!==height)throw Error('Native PNG size mismatch');
 const dest=path.join(OUT,'frames',String(n).padStart(6,'0')+'.png');
 await writeFile(dest+'.tmp',bytes);await rename(dest+'.tmp',dest);
 const record={frame:n,time:t,bytes:bytes.length,sha256:sha(bytes),ms:performance.now()-start,encodeMs:payload.encodeMs,...payload.meta};records.push(record);
 return record;
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
 for(const n of indices){
  const record=await capture(n);
  if(preview||n%30===0)console.log(JSON.stringify({stage:'frame',frame:n,time:n/fps,ms:Math.round(record.ms),bytes:record.bytes}));
 }
 if(sha(await readFile(path.join(SRC,'scene.mjs')))!==sceneHash)throw Error('Scene changed during capture');
 const report={
  completed_at:new Date().toISOString(),source_sha256:sceneHash,renderer_sha256:rendererHash,
  native:{width,height,fps,duration,format,frames:indices.length,folder:'frames',antialias:true,samples:4,method:'Direct deterministic Three.js WebGL2 PNG captures at exact n/30 seconds. Native1080 throughout; no JPEG, motion interpolation or intermediate video encode.'},
  sequence:{width,height,fps,duration,format,folder:'frames',frames:indices.length,required_indices:visibleIndices,captured_indices:[...indices].sort((a,b)=>a-b),hidden_ranges:[{start:486,end_exclusive:588,reason:'Opaque actual DPR2 UI'},{start:630,end_exclusive:720,reason:'Clean original-mark endcard'}],nearest_frame_fallback:false},
  preview,dependencies,texture:{dimensions:[2048,1536],source:'Original product SVG landscape rasterized directly at texture resolution; native Geist text; no screenshot enlargement'},
  average_frame_ms:records.reduce((sum,x)=>sum+x.ms,0)/records.length,records:records.sort((a,b)=>a.frame-b.frame)
 };
 await writeFile(path.join(OUT,preview?'preview-render.json':'manifest.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({stage:'complete',frames:records.length,averageFrameMs:report.average_frame_ms,folder:path.join(OUT,'frames')}));

}finally{
 if(ws)ws.close();
 await exec('agent-browser',['--session',session,'close'],{timeout:30000,maxBuffer:1000000}).catch(()=>{});
 server.close();
}
