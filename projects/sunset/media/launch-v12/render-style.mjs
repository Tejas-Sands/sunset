#!/usr/bin/env node
// Local throwaway preview. Reuses V11 capture transport and mesh verifier; no installs or network assets.
import {createServer} from 'node:http';
import {readFile,writeFile,mkdir,rename} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {sampleState,motionContract} from '../launch-v11/motion.mjs';
import {checkLiveFrame,verifyAnalyticMotion} from '../launch-v11/verify_motion.mjs';
const exec=promisify(execFile),ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../..');
const SRC=path.join(ROOT,'projects/sunset/media/launch-v12'),OLD=path.join(ROOT,'projects/sunset/media/launch-v11'),OUT=path.join(ROOT,'.publication/sunset-launch-v12');
const poses=process.argv.includes('--poses'),probe=process.argv.includes('--probe'),name=poses?'poses':probe?'probe':'native';
const width=1920,height=1080,fps=30,duration=5.5,count=165,sha=b=>createHash('sha256').update(b).digest('hex');
const indices=poses?[0,14,72,158]:probe?[0,10,11,14,18,60,63,68,71,76,79,158]:Array.from({length:count},(_,i)=>i);
const framesDir=path.join(OUT,'scene',name==='native'?'frames':name),qa=path.join(OUT,'qa');
await mkdir(framesDir,{recursive:true});await mkdir(qa,{recursive:true});
const source_hashes={};
for(const [key,file] of [['wrapper',path.join(SRC,'style-preview.mjs')],['renderer',fileURLToPath(import.meta.url)],['scene',path.join(OLD,'scene.mjs')],['motion',path.join(OLD,'motion.mjs')],['verifier',path.join(OLD,'verify_motion.mjs')]])source_hashes[key]={path:path.relative(ROOT,file),sha256:sha(await readFile(file))};
assert.equal(source_hashes.motion.sha256,'4453a3ddff995d410980add4dc9a29ee96de8de45f4edfcea092fdf943cfd504','V11 reviewed motion changed');
assert.equal(source_hashes.scene.sha256,'665fd540eceee426e9a1b2c4f81c2df3b71355414c1a754ae4d49703db15fe17','V11 reviewed geometry scene changed');
const continuous=verifyAnalyticMotion(sampleState,motionContract);delete continuous.states;assert.ok(continuous.pass,JSON.stringify(continuous.failures));
const html='<!doctype html><meta charset="utf-8"><style>html,body{margin:0;overflow:hidden;background:#fcf0db}canvas{display:block}</style><script>window.addEventListener("error",e=>window.sceneError=e.message);window.addEventListener("unhandledrejection",e=>window.sceneError=String(e.reason?.stack||e.reason))</script><script type="module">import "/style-preview.mjs"</script>';
const logo=path.join(ROOT,'.publication/sunset-launch-v1/render/logo.png');
const routes=new Map([
 ['/style-preview.mjs',[path.join(SRC,'style-preview.mjs'),'text/javascript']],['/v11-scene.mjs',[path.join(OLD,'scene.mjs'),'text/javascript']],['/motion.mjs',[path.join(OLD,'motion.mjs'),'text/javascript']],
 ['/three.module.js',[path.join(ROOT,'.publication/sunset-launch-v5/scene/deps/three.module.js'),'text/javascript']],['/three.core.js',[path.join(ROOT,'.publication/sunset-launch-v5/scene/deps/three.core.js'),'text/javascript']],
 ['/Bricolage.ttf',[path.join(ROOT,'.publication/sunset-launch-v6/fonts/BricolageGrotesque-VF.ttf'),'font/ttf']],['/Space.ttf',[path.join(ROOT,'.publication/sunset-launch-v6/fonts/SpaceGrotesk-VF.ttf'),'font/ttf']],['/original-logo.png',[logo,'image/png']],
 // Frozen scene fetches this legacy URL before the wrapper replaces its page map. Serve the logo, never old screenshot pixels.
 ['/actual-guide.png',[logo,'image/png']]
]);
const assets=[];for(const [url,[file]] of routes)assets.push({url,path:path.relative(ROOT,file),sha256:sha(await readFile(file)),...(url==='/actual-guide.png'?{role:'Unobserved placeholder for frozen scene loader; page map replaced before any capture'}:{})});
const server=createServer(async(req,res)=>{try{const url=new URL(req.url,'http://localhost').pathname;if(url==='/'){res.writeHead(200,{'Content-Type':'text/html'});res.end(html);return}const route=routes.get(url);if(!route){res.writeHead(404);res.end();return}res.writeHead(200,{'Content-Type':route[1],'Cache-Control':'no-store'});res.end(await readFile(route[0]))}catch(e){res.writeHead(500);res.end(String(e))}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const url='http://127.0.0.1:'+server.address().port+'/';
const session='sunset-v12-style-'+process.pid;let ws,sessionId,messageId=0;const pending=new Map();
function cdp(method,params={},target=true){return new Promise((resolve,reject)=>{const id=++messageId,timeout=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method))},120000);pending.set(id,{resolve,reject,timeout});ws.send(JSON.stringify({id,method,params,...(target&&sessionId?{sessionId}:{})}))})}
async function evaluate(expression){const r=await cdp('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value}
const records=[],live={width,height,fps,duration,source_hashes,geometries:[],frames:[]};let vertices=0;
try{
 await exec('agent-browser',['--session',session,'--args','--no-sandbox,--enable-unsafe-swiftshader,--use-angle=swiftshader','open','about:blank'],{timeout:90000,maxBuffer:1000000});
 const endpoint=(await exec('agent-browser',['--session',session,'get','cdp-url'],{timeout:30000})).stdout.match(/ws:\/\/\S+/)?.[0];assert.ok(endpoint,'No isolated browser endpoint');
 ws=new WebSocket(endpoint);await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});ws.onmessage=e=>{const m=JSON.parse(e.data),p=pending.get(m.id);if(p){pending.delete(m.id);clearTimeout(p.timeout);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}};
 const targets=await cdp('Target.getTargets',{},false),target=targets.targetInfos.find(t=>t.type==='page');assert.ok(target,'No browser page');
 ({sessionId}=await cdp('Target.attachToTarget',{targetId:target.targetId,flatten:true},false));await cdp('Page.enable');await cdp('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});await cdp('Page.navigate',{url});
 const deadline=Date.now()+90000;while(true){const state=await evaluate('window.sunsetStyleReady?"ready":(window.sceneError||"loading")');if(state==='ready')break;assert.equal(state,'loading');assert.ok(Date.now()<deadline,'Scene initialization timed out');await new Promise(r=>setTimeout(r,100))}
 const printed=await evaluate('window.sunsetStyle.printed');assert.ok(printed.includes('First Community')&&printed.includes('Workshop Kit')&&printed.includes('SPONSOR')&&printed.includes('Concept preview'));assert.ok(!printed.some(t=>/git|commit|terminal|wallet|matching key|SUNSET server/i.test(t)),'Unexpected developer/protocol text');
 console.log(JSON.stringify({stage:'ready',width,height,frames:indices.length,continuous:continuous.pass}));
 for(const frame of indices){
  const start=performance.now(),time=frame/fps;
  const p=await evaluate('(()=>{const meta=window.renderFrame('+time+');const data=window.captureFrame();const live=window.sunsetStyle.exportLive();'+(live.geometries.length?'delete live.geometries;':'')+'return {meta,data,live}})()');
  assert.ok(p.meta.actual_context_antialias&&p.meta.actual_samples>=4,'Native MSAA4 required');assert.equal(p.meta.drawingBufferWidth,width);assert.equal(p.meta.drawingBufferHeight,height);
  if(!live.geometries.length)live.geometries=p.live.geometries;const geometries=new Map(live.geometries.map(g=>[g.id,g]));assert.equal(geometries.size,6);
  const actual=p.live.frames[0];assert.equal(actual.frame,frame);assert.equal(actual.time,time);assert.equal(actual.physicalTime,time*8/5.5);const check=checkLiveFrame(actual,geometries,sampleState(actual.physicalTime),{width,height});assert.ok(check.pass,JSON.stringify(check.failures));vertices+=check.vertices;live.frames.push(actual);
  const bytes=Buffer.from(p.data.slice(p.data.indexOf(',')+1),'base64');assert.equal(bytes.readUInt32BE(16),width);assert.equal(bytes.readUInt32BE(20),height);
  const dest=path.join(framesDir,String(frame).padStart(6,'0')+'.png');await writeFile(dest+'.tmp',bytes);await rename(dest+'.tmp',dest);records.push({frame,time,physicalTime:actual.physicalTime,bytes:bytes.length,sha256:sha(bytes),ms:performance.now()-start,...p.meta});
  if(indices.length<30||frame%30===0)console.log(JSON.stringify({stage:'frame',frame,time,ms:Math.round(performance.now()-start)}));
 }
 for(const source of Object.values(source_hashes))assert.equal(sha(await readFile(path.join(ROOT,source.path))),source.sha256,'Source changed during capture');
 for(const record of records){const bytes=await readFile(path.join(framesDir,String(record.frame).padStart(6,'0')+'.png'));assert.equal(bytes.readUInt32BE(16),width);assert.equal(bytes.readUInt32BE(20),height);assert.equal(sha(bytes),record.sha256)}
 const metadata={completed_at:new Date().toISOString(),concept:true,silent:true,source_hashes,assets,printed,native:{width,height,fps,duration,frames:records.length,folder:path.relative(ROOT,framesDir),method:'Direct native WebGL2 MSAA4; unchanged V11 physical trajectory retimed by 8/5.5; UV map changes and clean screen recomposite only'},geometry:{pass:true,solid_count:6,frames:records.length,vertex_reads:vertices,continuous,realtime_speed_multiplier:8/5.5},records};
 await writeFile(path.join(qa,name+'-live.json'),JSON.stringify(live)+'\n');await writeFile(path.join(OUT,'scene',name+'-render.json'),JSON.stringify(metadata,null,2)+'\n');
 if(!poses&&!probe){
  const movie=path.join(OUT,'sunset-style-concept.mp4');
  await exec('ffmpeg',['-hide_banner','-loglevel','error','-y','-framerate','30','-i',path.join(framesDir,'%06d.png'),'-an','-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-preset','medium','-crf','16','-color_range','tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-frames:v',String(count),'-movflags','+faststart',movie],{timeout:300000,maxBuffer:2000000});
  const info=JSON.parse((await exec('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',movie])).stdout),video=info.streams.find(s=>s.codec_type==='video');assert.equal(info.streams.length,1,'Preview must be silent');assert.equal(video.codec_name,'h264');assert.equal(video.width,width);assert.equal(video.height,height);assert.equal(video.nb_read_frames,String(count));assert.equal(video.avg_frame_rate,'30/1');assert.equal(Number(info.format.duration),duration);for(const field of ['color_space','color_transfer','color_primaries'])assert.equal(video[field],'bt709');assert.equal(video.color_range,'tv');
  await exec('ffmpeg',['-v','error','-xerror','-i',movie,'-f','null','-'],{timeout:60000,maxBuffer:1000000});const movieBytes=await readFile(movie),atoms=[];for(let o=0;o<movieBytes.length;){let size=movieBytes.readUInt32BE(o);const tag=movieBytes.toString('ascii',o+4,o+8);if(size===1)size=Number(movieBytes.readBigUInt64BE(o+8));if(size===0)size=movieBytes.length-o;assert.ok(size>=8);atoms.push(tag);o+=size}assert.ok(atoms.indexOf('moov')<atoms.indexOf('mdat'),'Faststart required');
  const sheet=path.join(OUT,'decoded-beat-sheet.jpg');await exec('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',movie,'-vf','select=eq(n\\,0)+eq(n\\,14)+eq(n\\,30)+eq(n\\,60)+eq(n\\,72)+eq(n\\,90)+eq(n\\,120)+eq(n\\,145)+eq(n\\,164),scale=640:360,tile=3x3:padding=8:margin=8:color=0xfcf0db','-frames:v','1','-q:v','2',sheet],{timeout:60000,maxBuffer:1000000});
  const contact=path.join(OUT,'decoded-contact-sheet.jpg');await exec('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',movie,'-vf','select=between(n\\,8\\,22),scale=480:270,tile=5x3:padding=6:margin=6:color=0xfcf0db','-frames:v','1','-q:v','2',contact],{timeout:60000,maxBuffer:1000000});
  await writeFile(path.join(qa,'delivery.json'),JSON.stringify({pass:true,concept:true,silent:true,path:path.relative(ROOT,movie),sha256:sha(movieBytes),bytes:movieBytes.length,width,height,fps,duration,decoded_frames:count,codec:video.codec_name,bt709:true,faststart:true,atoms,native_manifest:path.relative(ROOT,path.join(OUT,'scene/native-render.json')),sheets:[{path:path.relative(ROOT,sheet),sha256:sha(await readFile(sheet))},{path:path.relative(ROOT,contact),sha256:sha(await readFile(contact))}],limitations:['Visual concept only; no real browser interaction, financial execution or newly implemented resource.','Authored affine squash and stretch; no general soft-body solver.','Unchanged V11 continuous certificate covers physical trajectory; playback speed is multiplied by 8/5.5.','Automated geometry and delivery checks do not establish audience response or creative approval.']},null,2)+'\n');
 }
 console.log(JSON.stringify({stage:'complete',name,frames:records.length,vertices,folder:path.relative(ROOT,framesDir),average_frame_ms:records.reduce((n,r)=>n+r.ms,0)/records.length}));
}finally{if(ws)ws.close();await exec('agent-browser',['--session',session,'close'],{timeout:30000,maxBuffer:1000000}).catch(()=>{});server.close()}
