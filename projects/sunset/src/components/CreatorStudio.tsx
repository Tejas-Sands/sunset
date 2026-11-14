'use client';
import {useEffect,useRef,useState} from 'react';
import {useWallet} from './WalletProvider';
import {PackContent} from './CampaignActions';
import {prepareOnchainCampaign} from '../lib/publishing.mjs';
import {validatePack} from '../lib/pack.mjs';
import {base64ToBytes} from '../lib/demo.mjs';
import {download} from '../lib/download.mjs';
import {formatNear} from '../lib/ledger.mjs';
import {CAMPAIGN_STORAGE} from '../lib/chain.mjs';
import {Icon} from './Protocol';

export default function CreatorStudio({snapshot,onRefresh}:{snapshot:any,onRefresh:()=>void}){
  const wallet=useWallet(),[pack,setPack]=useState<any>(null),[prepared,setPrepared]=useState<any>(null),[saved,setSaved]=useState(false),[backupRequested,setBackupRequested]=useState(false);
  const [working,setWorking]=useState(false),[error,setError]=useState(''),[form,setForm]=useState({reviewer:'',manifestUri:'',target:'0.1',deadline:'',releaseHours:'24'}),epoch=useRef(0);
  const owner=snapshot?.config.owner,isOwner=!!owner&&owner===wallet.accountId;
  const blocked=working||wallet.busy||wallet.loading||!!wallet.pending||wallet.pendingDamaged;
  useEffect(()=>{epoch.current++;setPrepared(null);setSaved(false);setBackupRequested(false);setWorking(false);return()=>{epoch.current++;};},[wallet.accountId]);
  function update(name:keyof typeof form,value:string){epoch.current++;setForm(previous=>({...previous,[name]:value}));setPrepared(null);setSaved(false);setBackupRequested(false);setError('');}
  async function upload(file:File){const token=++epoch.current;setError('');setPack(null);setPrepared(null);setSaved(false);setBackupRequested(false);try{if(file.size>5*1024*1024)throw Error('Resource exceeds the 5 MiB limit.');const value=validatePack(JSON.parse(await file.text()));if(token===epoch.current)setPack(value);}catch(e){if(token===epoch.current){setPack(null);setError((e as Error).message);}}}
  async function prepare(){
    const token=++epoch.current;setWorking(true);setError('');setPrepared(null);setSaved(false);setBackupRequested(false);
    try{if(!pack)throw Error('Import your resource first.');if(form.reviewer===wallet.accountId)throw Error('Choose a reviewer with a different account.');
      const date=new Date(form.deadline);if(!Number.isFinite(date.getTime()))throw Error('Choose a valid future deadline.');
      const value=await prepareOnchainCampaign(pack,{...form,deadline:date.toISOString()});if(token===epoch.current)setPrepared(value);
    }catch(e){if(token===epoch.current)setError((e as Error).message);}finally{if(token===epoch.current)setWorking(false);}
  }
  async function publish(){if(!prepared||!saved)return;const result=await wallet.submit('create_campaign',prepared.terms,prepared.backup.keyBase64);if(result?.status==='success')onRefresh();}
  const template={schema:2,kind:'guide',id:'your-original-resource',title:'Your resource title',description:'Describe the practical value of your original resource.',license:'CC0-1.0',sections:[{id:'first-chapter',title:'Start here',body:'Replace this text with your original lesson, derivation or procedure. Include enough detail for an independent reader to use it.',checklist:[{id:'first-exercise',text:'Replace with a meaningful exercise or check.'}]}]};
  const slots=snapshot?snapshot.config.max_campaigns-snapshot.config.campaign_count:null;
  const termsReady=!!form.reviewer&&!!form.manifestUri&&!!form.target&&!!form.deadline&&!!form.releaseHours;
  const step=prepared?3:pack?2:1;
  const stepState=(n:number)=>n<step?'done':n===step?'current':'pending';
  return <section className="p-studio"><div className="p-page-head"><h1>Creator studio</h1><p>Prepare a finished resource, set its release terms and publish the campaign for review.</p></div>
    {!isOwner&&<div className="p-notice p-notice-callout"><Icon name="lock"/><div><p><strong>Publishing is curated on this deployment.</strong> Only <strong>{owner||'shiftultra.testnet'}</strong> can create campaigns. You can still import a resource and preview how it reads.</p>{!wallet.accountId&&<button className="p-button" disabled={wallet.connecting} onClick={()=>void wallet.connect()}>Connect as creator</button>}</div></div>}
    <ol className="p-stepper" aria-label="Publishing steps">{['Import the resource','Set release terms','Save the key and publish'].map((label,i)=><li key={label} className={'p-stage-'+stepState(i+1)} aria-current={step===i+1?'step':undefined}><span className="p-stage-dot" aria-hidden="true">{i+1<step?<Icon name="check" size={14}/>:i+1}</span><strong>{label}</strong></li>)}</ol>
    <div className="p-panel"><h2>1. Import the resource</h2><p>Import an original CC0 guide or learning pack as JSON. The reader uses data only, so scripts and HTML are not accepted.</p><label>Resource file (JSON, up to 5 MiB)<input type="file" accept=".json,application/json" disabled={blocked} onChange={e=>{const file=e.target.files?.[0];if(file)void upload(file);}}/></label>
      {pack?<p className="p-notice p-notice-success"><Icon name="check"/><span>Imported <strong>{pack.title}</strong>.</span></p>:<button className="p-text-button" onClick={()=>download('sunset-resource-template.json',JSON.stringify(template,null,2))}><Icon name="download"/>Download a guide template</button>}
      {pack&&<details><summary>Preview how it reads</summary><PackContent pack={pack}/></details>}
    </div>
    <div className="p-panel"><h2>2. Set release terms</h2><p>These terms are fixed once the campaign is created.</p><div className="p-form-grid">
      <label>Reviewer account<input value={form.reviewer} onChange={e=>update('reviewer',e.target.value)} disabled={blocked} autoComplete="off" placeholder="reviewer.testnet"/><small>A different account that approves the content.</small></label>
      <label>Funding goal in testNEAR<input value={form.target} onChange={e=>update('target',e.target.value)} disabled={blocked} inputMode="decimal"/><small>Sponsorship above the goal returns to sponsors.</small></label>
      <label>Funding deadline<input type="datetime-local" value={form.deadline} onChange={e=>update('deadline',e.target.value)} disabled={blocked}/><small>In your local time. Unmet goals become refundable.</small></label>
      <label>Release window in hours<input type="number" min="1" max="720" step="1" value={form.releaseHours} onChange={e=>update('releaseHours',e.target.value)} disabled={blocked}/><small>Time you have to publish the key after funding.</small></label>
    </div><label>Public manifest URL<input type="url" value={form.manifestUri} onChange={e=>update('manifestUri',e.target.value)} disabled={blocked} placeholder="https://your-host.example/resource/manifest.json"/><small>You will host the generated manifest and encrypted file together at this HTTPS location. The content key stays in your private backup until release.</small></label>
      <div className="p-actions"><button className="p-button p-button-accent" disabled={blocked||!pack||!isOwner||!snapshot||slots!==null&&slots<=0} onClick={()=>void prepare()}>{working?'Preparing files…':'Prepare release files'}</button>
      <span className="p-small">{!pack?'Import a resource first.':!isOwner?'Only the creator account can prepare a campaign.':slots!==null&&slots<=0?'This deployment has no campaign slots left.':!termsReady?'Fill in every term to continue.':slots!==null?`${slots} campaign ${slots===1?'slot remains':'slots remain'} on this deployment.`:''}</span></div>
    </div>
    {prepared&&<div className="p-panel"><h2>3. Save the key and publish</h2><p>Host the two public files at your manifest URL. Keep the private backup somewhere else: losing the unreleased key can prevent release.</p><div className="p-file-list">
      <button className="p-file" onClick={()=>download('manifest.json',prepared.artifact.manifestText)}><Icon name="file"/><span><strong>manifest.json</strong><small>Public. Host it.</small></span><Icon name="download"/></button><button className="p-file" onClick={()=>download('ciphertext.sunset',base64ToBytes(prepared.artifact.envelope),'application/octet-stream')}><Icon name="file"/><span><strong>ciphertext.sunset</strong><small>Public. Host it beside the manifest.</small></span><Icon name="download"/></button>
      <button className="p-file p-file-private" onClick={()=>{download(prepared.terms.id+'-private-release-backup.json',JSON.stringify(prepared.backup,null,2));setBackupRequested(true);}}><Icon name="lock"/><span><strong>Private release backup</strong><small>Secret. Never host or share it.</small></span><Icon name="download"/></button></div>
      <label className="p-checkbox"><input type="checkbox" disabled={!backupRequested||blocked} checked={saved} onChange={e=>setSaved(e.target.checked)}/><span>I retained the matching private backup and published only the two public files.{!backupRequested&&<small>Download the private backup to continue.</small>}</span></label>
      <p className="p-small">Creating the campaign attaches {formatNear(CAMPAIGN_STORAGE)} testNEAR for storage, plus network gas. The content and hosted files are checked before the wallet opens.</p>
      <button className="p-button p-button-accent" disabled={!saved||blocked||!isOwner} onClick={()=>void publish()}>{wallet.busy?'Confirm in wallet…':'Create campaign on NEAR'}</button>
    </div>}
    {error&&<p className="p-notice p-notice-error" role="alert"><Icon name="alert"/><span>{error}</span></p>}
  </section>;
}
