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
  return <section className="p-studio"><div className="p-section-heading"><div><span className="p-kicker">CREATOR STUDIO</span><h1>Give good work<br/>a public future.</h1></div><p>Prepare the exact resource. Keep your backup. Invite a named reviewer.</p></div>
    {!isOwner&&<div className="p-notice"><p>Publishing is curated on this testnet deployment. Its creator account is <strong>{owner||'shiftultra.testnet'}</strong>. Everyone can read released resources; an active campaign accepts public sponsorship.</p>{!wallet.accountId&&<button className="p-button" disabled={wallet.connecting} onClick={()=>void wallet.connect()}>Connect creator wallet ↗</button>}</div>}
    <div className="p-panel"><span className="p-step">01 / YOUR RESOURCE</span><h2>Start with the content.</h2><p>Import an original CC0 guide or learning pack. Its reader uses data only; uploaded scripts or HTML are not accepted.</p><label>Resource JSON<input type="file" accept=".json,application/json" disabled={blocked} onChange={e=>{const file=e.target.files?.[0];if(file)void upload(file);}}/></label><button className="p-text-button" onClick={()=>download('sunset-resource-template.json',JSON.stringify(template,null,2))}>Download a guide template ↓</button>
      {pack&&<details><summary>Preview {pack.title}</summary><PackContent pack={pack}/></details>}
    </div>
    <div className="p-panel"><span className="p-step">02 / RELEASE TERMS</span><h2>Make the agreement clear.</h2><div className="p-form-grid">
      <label>Reviewer account<input value={form.reviewer} onChange={e=>update('reviewer',e.target.value)} disabled={blocked} autoComplete="off" placeholder="reviewer.testnet"/></label>
      <label>Funding goal · testNEAR<input value={form.target} onChange={e=>update('target',e.target.value)} disabled={blocked} inputMode="decimal"/></label>
      <label>Funding deadline · your local time<input type="datetime-local" value={form.deadline} onChange={e=>update('deadline',e.target.value)} disabled={blocked}/></label>
      <label>Release window · hours after funding<input type="number" min="1" max="720" step="1" value={form.releaseHours} onChange={e=>update('releaseHours',e.target.value)} disabled={blocked}/></label>
    </div><label>Public manifest URL<input type="url" value={form.manifestUri} onChange={e=>update('manifestUri',e.target.value)} disabled={blocked} placeholder="https://your-host.example/resource/manifest.json"/></label><p className="p-small">You will host the generated manifest and encrypted file together at this HTTPS location. The content key stays in your private backup until release.</p>
      <button className="p-button p-button-accent" disabled={blocked||!pack||!isOwner||!snapshot||snapshot.config.campaign_count>=snapshot.config.max_campaigns} onClick={()=>void prepare()}>{working?'Preparing files…':'Prepare release files'} ↗</button>
      {snapshot&&<p className="p-small">{snapshot.config.max_campaigns-snapshot.config.campaign_count} campaign slots remain in this deployment.</p>}
    </div>
    {prepared&&<div className="p-panel"><span className="p-step">03 / RETAIN & PUBLISH</span><h2>Keep the key. Publish the commitment.</h2><div className="p-actions">
      <button className="p-button" onClick={()=>download('manifest.json',prepared.artifact.manifestText)}>Download public manifest ↓</button><button className="p-button" onClick={()=>download('ciphertext.sunset',base64ToBytes(prepared.artifact.envelope),'application/octet-stream')}>Download encrypted file ↓</button>
      <button className="p-button" onClick={()=>{download(prepared.terms.id+'-private-release-backup.json',JSON.stringify(prepared.backup,null,2));setBackupRequested(true);}}>Save private release backup ↓</button></div>
      <p>Host only the public manifest and encrypted file. Keep the private backup outside public hosting. Losing the unreleased key can prevent release.</p>
      <label className="p-checkbox"><input type="checkbox" disabled={!backupRequested||blocked} checked={saved} onChange={e=>setSaved(e.target.checked)}/> I retained the matching private backup and published only the two public files.</label>
      <p className="p-small">Creating the campaign attaches {formatNear(CAMPAIGN_STORAGE)} testNEAR for storage, plus network gas. The content and hosted files are checked before the wallet opens.</p>
      <button className="p-button p-button-accent" disabled={!saved||blocked||!isOwner} onClick={()=>void publish()}>{wallet.busy?'Confirm in wallet…':'Create campaign on NEAR'} ↗</button>
    </div>}
    {error&&<p className="p-notice p-notice-error" role="alert">{error}</p>}
  </section>;
}
