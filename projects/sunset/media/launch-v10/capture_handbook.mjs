/** Real handbook browser proof. One browser owner controls input, emulation and captures. */
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
const exec=promisify(execFile),ROOT=process.cwd();
const OUT=path.join(ROOT,'.publication/sunset-launch-v10/footage');
const BASE=process.env.SUNSET_CAPTURE_BASE||'http://127.0.0.1:4407';
const session='sunset-v10-native-'+process.pid,DOWNLOADS=path.join(OUT,'downloads-'+process.pid);
const pause=ms=>new Promise(r=>setTimeout(r,ms)),sha=b=>createHash('sha256').update(b).digest('hex');
const events=[],recordings=[];let active;
function mark(action,data={}) {events.push({action,utc:new Date().toISOString(),...(active?{recording:active.name,seconds:(performance.now()-active.start)/1000}:{}),...data});}
async function cli(...args) {return (await exec('agent-browser',['--session',session,...args],{timeout:25000,maxBuffer:2000000})).stdout;}
async function evaluate(fn) {
 let value=JSON.parse((await cli('eval','JSON.stringify(('+fn.toString()+')())')).trim());
 if(typeof value==='string')value=JSON.parse(value);return value;
}
function browserState() {
 const box=r=>r?[r.x,r.y,r.right,r.bottom].map(n=>Math.round(n*devicePixelRatio)):null;
 const selectors=['#guide-reader','#guide-chapter','#guide-section-title','#guide-progress','#check-recovery-inspect','#download-maintainer-handbook'];
 const boxes=Object.fromEntries(selectors.map(s=>[s,box(document.querySelector(s)?.getBoundingClientRect())]));
 const body=document.querySelector('.guide-body');
 for(const command of ['git reflog --date=iso','git show --stat COMMIT_ID','git show COMMIT_ID']) {
  const i=body?.textContent.indexOf(command)??-1;
  if(i>=0&&body.firstChild?.nodeType===3){const r=document.createRange();r.setStart(body.firstChild,i);r.setEnd(body.firstChild,i+command.length);boxes[command]=box(r.getBoundingClientRect());}
 }
 return {url:location.href,scheme:location.protocol,onLine:navigator.onLine,resources:performance.getEntriesByType('resource').length,title:document.title,
 chapter:document.querySelector('#guide-section-title')?.textContent,progress:document.querySelector('#guide-progress')?.textContent,
 checks:[...document.querySelectorAll('[data-check-id]')].map(x=>({id:x.dataset.checkId,checked:x.checked})),boxes,
 viewport:[innerWidth,innerHeight,devicePixelRatio],overflow:document.documentElement.scrollWidth>innerWidth};
}
async function start(name){await mkdir(path.join(OUT,name),{recursive:true});active={name,start:performance.now(),samples:[]};mark('record_start',{method:'Native browser PNG samples interleaved with real controls at true elapsed times; transitions between samples are not invented or interpolated.'});}
async function shot(){
 const before=await evaluate(browserState),began=(performance.now()-active.start)/1000;
 const file=String(active.samples.length).padStart(6,'0')+'.png',dest=path.join(OUT,active.name,file);
 await cli('screenshot',dest);const at=(performance.now()-active.start)/1000,bytes=await readFile(dest),after=await evaluate(browserState);
 active.samples.push({file,at,capture_started_seconds:began,sha256:sha(bytes),dimensions:[bytes.readUInt32BE(16),bytes.readUInt32BE(20)],before,after});
}
async function stop(){const r={name:active.name,seconds:(performance.now()-active.start)/1000,samples:active.samples};await writeFile(path.join(OUT,r.name,'samples.json'),JSON.stringify(r,null,2)+'\n');recordings.push(r);active=null;return r;}
async function input(command,selector){mark('native_browser_'+command+'_started',{selector});await cli(command,selector);mark('native_browser_'+command+'_completed',{selector});}
await mkdir(DOWNLOADS,{recursive:true});
try {
 await cli('--args','--no-sandbox','open',BASE+'/app/?view=Handbook');
 await cli('set','viewport','1440','900','3');
 await writeFile(path.join(OUT,'app-snapshot.txt'),await cli('snapshot','-i'));
 await start('actual-download');await shot();await pause(450);
 const downloadedPath=path.join(DOWNLOADS,'maintainer-handbook-offline.html');
 mark('native_browser_download_action_started',{selector:'#download-maintainer-handbook'});
 await cli('download','#download-maintainer-handbook',downloadedPath);mark('native_browser_download_action_completed');
 const bytes=await readFile(downloadedPath),expected=await readFile('projects/sunset/public/try-maintainer-handbook.html');
 if(sha(bytes)!==sha(expected))throw Error('Actual downloaded file differs from checked-in sample');
 mark('actual_download_complete',{filename:path.basename(downloadedPath),bytes:bytes.length,sha256:sha(bytes)});
 await shot();await pause(400);await shot();await stop();
 await cli('open','about:blank');await cli('set','offline','on');
 const blankOffline=await evaluate(browserState);if(blankOffline.onLine!==false)throw Error('Networking must be disabled before file load');
 mark('browser_offline_before_file_navigation');await cli('open','file://'+downloadedPath);
 const offlineBefore=await evaluate(browserState);
 if(offlineBefore.onLine!==false||offlineBefore.resources!==0||offlineBefore.scheme!=='file:')throw Error('Offline file proof conditions failed');
 await start('actual-offline-procedure');await shot();
 await input('click','[data-section-id="recover-commit"]');await pause(450);await shot();
 mark('native_browser_scroll_started');await cli('scroll','down','350');mark('native_browser_scroll_completed');await shot();await pause(500);await shot();
 await input('check','#check-recovery-inspect');await shot();await pause(500);await shot();
 const checked=await evaluate(browserState);
 if(!checked.checks.find(x=>x.id==='recovery-inspect')?.checked)throw Error('Actual checklist input did not persist in the reader');
 mark('actual_checked_result',{state:checked});
 mark('native_browser_reload_started');await cli('reload');mark('native_browser_reload_completed');await shot();await pause(450);await shot();
 const offlineAfter=await evaluate(browserState);
 if(!offlineAfter.checks.find(x=>x.id==='recovery-inspect')?.checked||offlineAfter.onLine!==false||offlineAfter.resources!==0)throw Error('Reload did not retain the offline chapter and check');
 await stop();
 const retainedPath=path.join(OUT,'retained-after-reload.png');await cli('screenshot',retainedPath);const retained=await readFile(retainedPath);
 const consoleErrors=(await cli('errors')).trim();
 if(consoleErrors&&!/no (?:errors|page errors)|\[\]|^$|No errors/i.test(consoleErrors))throw Error('Browser reported errors: '+consoleErrors);
 const provenance={checked_at:new Date().toISOString(),status:'actual_download_offline_procedure_and_retained_check_passed',base:BASE,example_resource:true,guide_onchain_release_claimed:false,underlying_git_steps_executed:false,
 network_scope:'Browser-owner Chrome networking disabled before file navigation and verified before/after. Not an OS network adapter toggle.',
 capture_method:'Native browser-owner screenshots interleaved with real input at recorded elapsed times. Honest held states and cuts, not 30 unique UI frames per second or uninterrupted full-rate recording.',
 dimensions:[retained.readUInt32BE(16),retained.readUInt32BE(20)],dpr:3,
 download:{path:path.relative(ROOT,downloadedPath),bytes:bytes.length,sha256:sha(bytes)},source_pack:{path:'projects/sunset/public/packs/maintainer-handbook.json',sha256:sha(await readFile('projects/sunset/public/packs/maintainer-handbook.json'))},
 blank_offline_before_file:blankOffline,offline_before:offlineBefore,checked_result:checked,offline_after:offlineAfter,
 retained_after_reload:{path:path.relative(ROOT,retainedPath),sha256:sha(retained),dimensions:[retained.readUInt32BE(16),retained.readUInt32BE(20)]},
 recordings,events,console_errors:[],capture_source_sha256:sha(await readFile(new URL(import.meta.url))),chain_mutations:0};
 await writeFile(path.join(OUT,'capture-provenance.json'),JSON.stringify(provenance,null,2)+'\n');
 console.log(JSON.stringify({status:provenance.status,download:provenance.download,dimensions:provenance.dimensions,recording_samples:recordings.map(x=>({name:x.name,seconds:x.seconds,samples:x.samples.length}))},null,2));
} catch(error) {
 await writeFile(path.join(OUT,'capture-failure-'+process.pid+'.json'),JSON.stringify({error:String(error),events,state:await evaluate(browserState).catch(()=>null)},null,2)+'\n');throw error;
} finally {await cli('close').catch(()=>{});}
