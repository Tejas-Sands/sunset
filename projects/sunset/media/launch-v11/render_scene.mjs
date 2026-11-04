#!/usr/bin/env node
// Native deterministic WebGL2 captures. All inputs are cached locally; no downloads.
import {createServer} from 'node:http';
import {readFile,writeFile,mkdir,rename} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {createHash} from 'node:crypto';
const exec=promisify(execFile),ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../..');
const SRC=path.join(ROOT,'projects/sunset/media/launch-v11'),OUT=path.join(ROOT,'.publication/sunset-launch-v11');
const args=process.argv.slice(2),value=(flag,fallback)=>{const i=args.indexOf(flag);return i<0?fallback:args[i+1]};
const width=1920,height=1080,fps=30,duration=8,sha=b=>createHash('sha256').update(b).digest('hex');
const probe=args.includes('--probe'),pose=args.includes('--poses'),name=value('--name',pose?'poses':probe?'probe':'native');
if(!/^[a-z0-9-]+$/.test(name))throw Error('Invalid output name');
const selected=value('--frames',null),indices=selected?selected.split(',').map(Number):pose?[0,21,105,225]:probe?[0,15,18,21,27,87,91,99,103,111,115,225]:Array.from({length:duration*fps},(_,i)=>i);
if(indices.some(i=>!Number.isInteger(i)||i<0||i>=duration*fps)||new Set(indices).size!==indices.length)throw Error('Invalid native frame indices');
const framesDir=path.join(OUT,'scene',name==='native'?'frames':name);
await mkdir(framesDir,{recursive:true});await mkdir(path.join(OUT,'qa'),{recursive:true});
const source_hashes={};
for(const [key,file] of [['motion','motion.mjs'],['scene','scene.mjs'],['renderer','render_scene.mjs']])source_hashes[key]={path:path.relative(ROOT,path.join(SRC,file)),sha256:sha(await readFile(path.join(SRC,file)))};
const html='<!doctype html><html><meta charset="utf-8"><style>html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#fcf0db}canvas{display:block}</style><script>window.addEventListener("error",e=>window.sceneError=e.message);window.addEventListener("unhandledrejection",e=>window.sceneError=String(e.reason?.stack||e.reason));</script><script type="module">import "/scene.mjs";</script></html>';
const routes=new Map([
 ['/scene.mjs',[path.join(SRC,'scene.mjs'),'text/javascript']],
 ['/motion.mjs',[path.join(SRC,'motion.mjs'),'text/javascript']],
 ['/three.module.js',[path.join(ROOT,'.publication/sunset-launch-v5/scene/deps/three.module.js'),'text/javascript']],
 ['/three.core.js',[path.join(ROOT,'.publication/sunset-launch-v5/scene/deps/three.core.js'),'text/javascript']],
 ['/Bricolage.ttf',[path.join(ROOT,'.publication/sunset-launch-v6/fonts/BricolageGrotesque-VF.ttf'),'font/ttf']],
 ['/Space.ttf',[path.join(ROOT,'.publication/sunset-launch-v6/fonts/SpaceGrotesk-VF.ttf'),'font/ttf']],
 ['/original-logo.png',[path.join(ROOT,'.publication/sunset-launch-v1/render/logo.png'),'image/png']],
 ['/actual-guide.png',[path.join(ROOT,'.publication/sunset-launch-v10/footage/actual-offline-procedure/000002.png'),'image/png']]
]);
const assets=[];for(const [url,[file]] of routes)assets.push({url,path:path.relative(ROOT,file),sha256:sha(await readFile(file))});
const server=createServer(async(req,res)=>{try{const url=new URL(req.url,'http://localhost').pathname;if(url==='/'){res.writeHead(200,{'Content-Type':'text/html'});res.end(html);return}const route=routes.get(url);if(!route){res.writeHead(404);res.end();return}res.writeHead(200,{'Content-Type':route[1],'Cache-Control':'no-store'});res.end(await readFile(route[0]))}catch(e){res.writeHead(500);res.end(String(e))}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const url='http://127.0.0.1:'+server.address().port+'/';
const session='sunset-v11-native-'+process.pid;let ws,sessionId,messageId=0;const pending=new Map();
function cdp(method,params={},target=true){return new Promise((resolve,reject)=>{const id=++messageId;const timeout=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method))},120000);pending.set(id,{resolve,reject,timeout});ws.send(JSON.stringify({id,method,params,...(target&&sessionId?{sessionId}: {})}))})}
async function evaluate(expression){const r=await cdp('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value}
const records=[],live={width,height,fps,duration,source_hashes,geometries:[],frames:[]};
try{
 await exec('agent-browser',['--session',session,'--args','--no-sandbox,--enable-unsafe-swiftshader,--use-angle=swiftshader','open','about:blank'],{timeout:90000,maxBuffer:1000000});
 const endpoint=(await exec('agent-browser',['--session',session,'get','cdp-url'],{timeout:30000})).stdout.match(/ws:\/\/\S+/)?.[0];if(!endpoint)throw Error('No isolated browser endpoint');
 ws=new WebSocket(endpoint);await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
 ws.onmessage=e=>{const m=JSON.parse(e.data),p=pending.get(m.id);if(p){pending.delete(m.id);clearTimeout(p.timeout);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}};
 const targets=await cdp('Target.getTargets',{},false),target=targets.targetInfos.find(t=>t.type==='page');if(!target)throw Error('No browser page');
 ({sessionId}=await cdp('Target.attachToTarget',{targetId:target.targetId,flatten:true},false));
 await cdp('Page.enable');await cdp('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});await cdp('Page.navigate',{url});
 const deadline=Date.now()+90000;while(true){const state=await evaluate('window.sunsetSceneReady?"ready":(window.sceneError||"loading")');if(state==='ready')break;if(state!=='loading')throw Error(state);if(Date.now()>deadline)throw Error('Scene initialization timed out');await new Promise(r=>setTimeout(r,100))}
 console.log(JSON.stringify({stage:'ready',session,width,height,frames:indices.length,source_hashes}));
 for(const frame of indices){
  const start=performance.now(),time=frame/fps;
  const p=await evaluate('(()=>{const meta=window.renderFrame('+time+');const encodeStart=performance.now();const data=window.captureFrame();const live=window.sunsetV11.exportLive();'+(live.geometries.length?'delete live.geometries;':'')+'return {meta,data,live,encodeMs:performance.now()-encodeStart}})()');
  if(!p.meta.actual_context_antialias||p.meta.actual_samples<4)throw Error('Native MSAA4 required');
  if(p.meta.drawingBufferWidth!==width||p.meta.drawingBufferHeight!==height)throw Error('Drawing buffer mismatch');
  const bytes=Buffer.from(p.data.slice(p.data.indexOf(',')+1),'base64');if(bytes.readUInt32BE(16)!==width||bytes.readUInt32BE(20)!==height)throw Error('Native PNG size mismatch');
  const dest=path.join(framesDir,String(frame).padStart(6,'0')+'.png');await writeFile(dest+'.tmp',bytes);await rename(dest+'.tmp',dest);
  if(!live.geometries.length)live.geometries=p.live.geometries;live.frames.push(...p.live.frames);
  const record={frame,time,bytes:bytes.length,sha256:sha(bytes),ms:performance.now()-start,encodeMs:p.encodeMs,...p.meta};records.push(record);
  if(indices.length<30||frame%30===0)console.log(JSON.stringify({stage:'frame',frame,time,ms:Math.round(record.ms),bytes:record.bytes}));
 }
 for(const source of Object.values(source_hashes))if(sha(await readFile(path.join(ROOT,source.path)))!==source.sha256)throw Error('Source changed during capture: '+source.path);
 const metadata={completed_at:new Date().toISOString(),source_hashes,assets,preview:probe||pose,native:{width,height,fps,duration,format:'png',frames:indices.length,folder:path.relative(ROOT,framesDir),antialias:true,samples:4,method:'Direct native1920x1080 WebGL2 at exact n/30; canvas compositing stays native. No interpolation or upscaling.'},average_frame_ms:records.reduce((s,r)=>s+r.ms,0)/records.length,records};
 await writeFile(path.join(OUT,'qa',name+'-live.json'),JSON.stringify(live)+'\n');await writeFile(path.join(OUT,'scene',name+'-render.json'),JSON.stringify(metadata,null,2)+'\n');
 console.log(JSON.stringify({stage:'complete',frames:records.length,averageFrameMs:metadata.average_frame_ms,folder:path.relative(ROOT,framesDir),live:path.relative(ROOT,path.join(OUT,'qa',name+'-live.json'))}));
}finally{
 if(ws)ws.close();await exec('agent-browser',['--session',session,'close'],{timeout:30000,maxBuffer:1000000}).catch(()=>{});server.close();
}
