import {execFile} from 'node:child_process';
import {promisify} from 'node:util';import {mkdir,writeFile,readFile,readdir} from 'node:fs/promises';import path from 'node:path';import {createHash} from 'node:crypto';
const exec=promisify(execFile),ROOT=process.cwd(),OUT=path.join(ROOT,'.publication/sunset-launch-v8/footage'),session='sunset-v8-real-demo-'+process.pid;
await mkdir(path.join(OUT,'downloads-native'),{recursive:true});let ws,sessionId,msgId=0;const pending=new Map(),errors=[],records=[];
const sha=b=>createHash('sha256').update(b).digest('hex'),delay=ms=>new Promise(r=>setTimeout(r,ms));
function cdp(method,params={},target=true){return new Promise((resolve,reject)=>{const id=++msgId,timer=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method))},60000);pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params,...(target&&sessionId?{sessionId}: {})}));})}
async function evaluate(expression){const r=await cdp('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value}
async function evalFn(fn,arg){return evaluate('('+fn.toString()+')('+JSON.stringify(arg)+')')}
async function until(fn,timeout=60000){const end=Date.now()+timeout;while(Date.now()<end){const v=await evalFn(fn);if(v)return v;await delay(250)}throw Error('Timed out waiting for page state')}
async function click(text){if(!await evalFn(text=>{const b=[...document.querySelectorAll('button')].find(x=>x.textContent.trim()===text);if(!b)return false;b.click();return true},text))throw Error('No button '+text);await delay(300)}
async function setInput(placeholder,value){return evalFn(({placeholder,value})=>{const el=[...document.querySelectorAll('input')].find(x=>x.placeholder===placeholder);if(!el)throw Error('No input');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el,value);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));return true},{placeholder,value})}
async function capture(file,selector,extra={}){
 const box=await evalFn(selector=>{const el=document.querySelector(selector);if(!el)return null;el.scrollIntoView({block:'center'});const r=el.getBoundingClientRect();return {x:r.x+scrollX,y:r.y+scrollY,width:r.width,height:r.height}},selector);if(!box)throw Error('No capture element '+selector);await delay(300);
 const shot=await cdp('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{...box,scale:1}});const bytes=Buffer.from(shot.data,'base64');await writeFile(path.join(OUT,file),bytes);
 const rec={file,selector,css_box:box,device_scale_factor:2,pixel_dimensions:[bytes.readUInt32BE(16),bytes.readUInt32BE(20)],bytes:bytes.length,sha256:sha(bytes),...extra};records.push(rec);await writeFile(path.join(OUT,'capture-progress.json'),JSON.stringify(records,null,2));console.log(JSON.stringify(rec));return rec
}
const events=[];let chain,downloadPath,downloadBytes,recording=false,recordState=null;
async function actualClick(label,scope='button'){
 const point=await evalFn(({label,scope})=>{const el=[...document.querySelectorAll(scope)].find(x=>x.textContent.trim()===label);if(!el)throw Error('No real control '+label);el.scrollIntoView({block:'center'});const r=el.getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2}}, {label,scope});
 await cdp('Input.dispatchMouseEvent',{type:'mouseMoved',...point});await delay(180);
 await cdp('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,...point});await cdp('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,...point});
 events.push({action:'actual_browser_click',label,at:new Date().toISOString(),point});return point;
}
async function recordStart(name){
 const stem=name.replace(/\.[^.]+$/,''),directory=path.join(OUT,'native-recording-'+stem);await mkdir(directory,{recursive:true});
 recordState={name,directory,start:performance.now(),running:true,samples:[]};recording=true;
 const state=recordState;
 state.loop=(async()=>{while(state.running){const shot=await cdp('Page.captureScreenshot',{format:'png',captureBeyondViewport:false,fromSurface:true});const at=(performance.now()-state.start)/1000;const bytes=Buffer.from(shot.data,'base64'),file=String(state.samples.length).padStart(6,'0')+'.png';await writeFile(path.join(directory,file),bytes);state.samples.push({file,at,sha256:sha(bytes),width:bytes.readUInt32BE(16),height:bytes.readUInt32BE(20)});await delay(10)}})();
 events.push({action:'record_start',name,at:new Date().toISOString(),method:'Continuous actual nativeDPR2 lossless PNG viewport capture; timestamps preserve wallclock.'});console.log('RECORD nativeDPR2 '+name);
}
async function recordStop(){
 const state=recordState;state.running=false;const end=(performance.now()-state.start)/1000;await state.loop;recording=false;
 if(!state.samples.length)throw Error('No real viewport frames');
 const lines=['ffconcat version 1.0'];for(let i=0;i<state.samples.length;i++){const sample=state.samples[i],next=state.samples[i+1];lines.push('file '+sample.file);lines.push('duration '+Math.max(.001,(next?next.at:end)-sample.at).toFixed(6))}lines.push('file '+state.samples.at(-1).file);
 const concat=path.join(state.directory,'frames.ffconcat');await writeFile(concat,lines.join('\n')+'\n');
 const duration=Math.max(.1,end-state.samples[0].at);
 await exec('ffmpeg',['-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',concat,'-vf','fps=30,scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-preset','fast','-crf','14','-threads','4','-t',String(duration),'-movflags','+faststart',path.join(OUT,state.name)],{timeout:90000,maxBuffer:1000000});
 const result={file:state.name,frames:Math.round(duration*30),capturedFrames:state.samples.length,duration,source_dimensions:[state.samples[0].width,state.samples[0].height],first_capture_offset:state.samples[0].at,method:'Actual continuous Chrome viewport PNG capture; output30fps holds samples by true elapsed timestamps, no interpolation or invented states.',samples:state.samples};
 await writeFile(path.join(state.directory,'samples.json'),JSON.stringify(result,null,2)+'\n');events.push({action:'record_stop',at:new Date().toISOString(),result:{...result,samples:undefined}});return result;
}

try{
 await exec('agent-browser',['--session',session,'--args','--no-sandbox','open','about:blank'],{timeout:90000,maxBuffer:1000000});
 const ep=(await exec('agent-browser',['--session',session,'get','cdp-url'],{maxBuffer:1000000})).stdout.match(/ws:\/\/\S+/)?.[0];if(!ep)throw Error('No isolated CDP');ws=new WebSocket(ep);await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
 ws.onmessage=e=>{const m=JSON.parse(e.data),p=pending.get(m.id);if(p){pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text);if(m.method?.startsWith('Browser.download'))events.push({action:m.method,at:new Date().toISOString(),data:m.params})};
 const targets=await cdp('Target.getTargets',{},false);({sessionId}=await cdp('Target.attachToTarget',{targetId:targets.targetInfos.find(x=>x.type==='page').targetId,flatten:true},false));
 await cdp('Page.enable');await cdp('Runtime.enable');await cdp('Network.enable');await cdp('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:2,mobile:false});
 await cdp('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:path.join(OUT,'downloads-native'),eventsEnabled:true},false);
 await cdp('Page.navigate',{url:'https://sunset-lemon.vercel.app/app/'});await until(()=>document.readyState==='complete'&&document.body.innerText.includes('Testnet setup'));
 await click('Testnet setup');await until(()=>document.querySelector('input[placeholder="Your deployed .testnet account"]')!==null);
 await setInput('Your deployed .testnet account','sunset.shiftultra.testnet');await setInput('Base58 code hash from deployment','9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx');await click('Verify testnet contract');
 await until(()=>document.body.innerText.includes('Public resources from the configured contract'),90000);
 chain=await evalFn(()=>{const pre=document.querySelector('.live-panel pre');return pre?JSON.parse(pre.textContent):null});if(!chain||chain.codeHash!=='9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx')throw Error('Pinned verification missing');
 if(!await evalFn(()=>{const a=[...document.querySelectorAll('article')].find(x=>!x.innerText.includes('E2E')&&x.innerText.includes('Current maintenance holder'));if(!a)return false;a.id='sunset-capture-resource';return true}))throw Error('No released card');
 await evalFn(()=>document.querySelector('#sunset-capture-resource button').click());
 let recovered=await until(()=>{const a=document.querySelector('#sunset-capture-resource');if(a.innerText.includes('Play verified resource'))return 'success';if(a.querySelector('[role=alert]'))return a.querySelector('[role=alert]').textContent;return false},90000);
 if(recovered!=='success'){await evalFn(()=>document.querySelector('#sunset-capture-resource button').click());await until(()=>document.querySelector('#sunset-capture-resource').innerText.includes('Play verified resource'),90000)}
 await evalFn(()=>{const e=[...document.querySelectorAll('button')].find(x=>x.textContent.trim()==='Download standalone game');e.scrollIntoView({block:'center'});return true});await delay(250);
 await capture('01-real-download-before@2x.png','#sunset-capture-resource',{scope:'Actual recovered public resource before recorded download'});
 await recordStart('download-to-offline.mp4');const startDownload=performance.now();await delay(700);await actualClick('Download standalone game');
 let downloaded=[];for(let i=0;i<40;i++){downloaded=(await readdir(path.join(OUT,'downloads-native'))).filter(x=>x.endsWith('.html'));if(downloaded.length)break;await delay(100)}
 if(downloaded.length!==1)throw Error('Expected one actual download');
 downloadPath=path.join(OUT,'downloads-native',downloaded[0]);downloadBytes=await readFile(downloadPath);if(sha(downloadBytes)!=='fbe1df06b5eb4a93aae1eb12009f4d910e3ba432862918e3c254fc013ab79738')throw Error('Download hash differs');
 events.push({action:'download_completed',elapsed:(performance.now()-startDownload)/1000,file:downloaded[0],sha256:sha(downloadBytes)});
 await delay(350);await cdp('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
 await cdp('Page.navigate',{url:'file://'+downloadPath});await until(()=>document.readyState==='complete'&&document.body.innerText.includes('The Lantern Trail'));
 events.push({action:'actual_download_opened_offline',elapsed:(performance.now()-startDownload)/1000,at:new Date().toISOString()});
 await delay(1500);const downloadRecord=await recordStop();
 // A separate uninterrupted actual interaction gives a visible result, not just an edited file handoff.
 await evalFn(()=>{const e=document.querySelector('.card');e.scrollIntoView({block:'center'});return true});await delay(300);
 const offlineBefore=await evalFn(()=>({onLine:navigator.onLine,resources:performance.getEntriesByType('resource').length,scheme:location.protocol,feedback:document.querySelector('#feedback').textContent,buttons:[...document.querySelectorAll('#choices button')].map(x=>x.textContent)}));
 if(offlineBefore.onLine!==false)throw Error('Browser offline state not active before recording');
 await capture('02-offline-action-before@2x.png','.card',{scope:'Actual offline game before recorded answer click'});
 await recordStart('offline-action-result.mp4');const startAction=performance.now();await delay(750);const clickPoint=await actualClick('12','#choices button');
 const clickElapsed=(performance.now()-startAction)/1000;await until(()=>document.querySelector('#feedback').textContent.includes('Your first lantern glows'));
 const resultElapsed=(performance.now()-startAction)/1000;await delay(2300);const actionRecord=await recordStop();
 await capture('03-offline-action-result@2x.png','.card',{scope:'Actual answer12 and visible explanation/progress after uninterrupted recorded click'});
 const offline=await evalFn(()=>({onLine:navigator.onLine,resources:performance.getEntriesByType('resource').length,scheme:location.protocol,feedback:document.querySelector('#feedback').textContent,progress:document.querySelector('#progress').value}));
 if(offline.onLine!==false||offline.resources!==0||offline.progress!==1)throw Error('Offline/action evidence failed');
 const clips=[];for(const file of ['download-to-offline.mp4','offline-action-result.mp4']){const p=path.join(OUT,file),b=await readFile(p);const probe=JSON.parse((await exec('ffprobe',['-v','error','-show_streams','-show_format','-of','json',p],{maxBuffer:1000000})).stdout);const v=probe.streams.find(s=>s.codec_type==='video');clips.push({file,sha256:sha(b),bytes:b.length,width:v.width,height:v.height,fps:v.r_frame_rate,duration:Number(probe.format.duration),frames:v.nb_frames,recording:'Actual Chrome continuous lossless viewport recording in agent-browser-owned session, target30fps from genuine nativeDPR2 captures timed by wallclock; static frames held, no invented cursor or motion interpolation.'})}
 const report={captured_at:new Date().toISOString(),source_site:'https://sunset-lemon.vercel.app/app/',css_viewport:[1280,900],dpr:2,chain:{network:chain.network,contract:chain.contract,code_hash:chain.codeHash,height:chain.height,campaigns:chain.campaigns.map(x=>({id:x.id,state:x.state}))},download:{file:path.relative(OUT,downloadPath),bytes:downloadBytes.length,sha256:sha(downloadBytes)},offline_before:offlineBefore,offline_after:offline,clips,action_clip:{file:'offline-action-result.mp4',click_elapsed_seconds:clickElapsed,result_elapsed_seconds:resultElapsed,click_css_point:clickPoint,visible_result:'Actual explanation7+5=12 plus first-lantern feedback, progress1, enabledcontinue'},recordings:{download:downloadRecord,action:actionRecord},events,captures:records,console_errors:errors,scope:'Task-owned browser only. Public read-only contract verification/recovery and an actual download plus offline gameplay recording. No wallet, signer, transaction, private backup or user profile accessed. No UI/cursor reenactment.'};
 await writeFile(path.join(OUT,'capture-provenance.json'),JSON.stringify(report,null,2)+'\n');console.log('CAPTURE COMPLETE '+JSON.stringify({clips,clickElapsed,resultElapsed,offline,errors}));
}finally{if(recordState?.running){recordState.running=false;await recordState.loop.catch(()=>{})}if(ws)ws.close();await exec('agent-browser',['--session',session,'close'],{timeout:30000,maxBuffer:1000000}).catch(()=>{})}
