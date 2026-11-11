'use client';
import {useEffect,useRef,useState} from 'react';
import GuideReader,{type GuidePack} from './GuideReader';
import {useWallet} from './WalletProvider';
import {fetchVerifiedMirror} from '../lib/mirror.mjs';
import {resourceCommitments} from '../lib/live.mjs';
import {validateReleaseBackup} from '../lib/backups.mjs';
import {createOfflineHtml} from '../lib/pack.mjs';
import {formatNear,toYocto} from '../lib/ledger.mjs';
import {ACCOUNT_STORAGE} from '../lib/chain.mjs';
import {download} from '../lib/download.mjs';

export function PackContent({pack}:{pack:any}){
  if(pack.kind==='guide')return <GuideReader pack={pack as GuidePack}/>;
  return <section className="p-legacy-reader"><h3>{pack.title}</h3><p>{pack.description}</p>{pack.questions.map((q:any)=><details key={q.id}><summary>{q.prompt}</summary><p>{q.explanation}</p></details>)}</section>;
}
const date=(ns:string)=>new Date(Number(BigInt(ns)/1000000n)).toLocaleString(undefined,{dateStyle:'medium',timeStyle:'short'});
function duration(ns:string){const n=BigInt(ns);for(const [unit,label] of [[3600000000000n,'hours'],[60000000000n,'minutes'],[1000000000n,'seconds']] as const)if(n%unit===0n)return `${n/unit} ${label}`;return `${n} nanoseconds`;}
export default function CampaignActions({campaign:c,snapshot,onRefresh}:{campaign:any,snapshot:any,onRefresh:()=>void}){
  const wallet=useWallet(),[amount,setAmount]=useState('0.1'),[key,setKey]=useState(''),[pack,setPack]=useState<any>(null),[inspection,setInspection]=useState<any>(null);
  const [accepted,setAccepted]=useState(false),[working,setWorking]=useState(false),[error,setError]=useState(''),[receiver,setReceiver]=useState(''),[message,setMessage]=useState('');
  const [uri,setUri]=useState(c.stewardship?.mirror_uri||c.manifest_uri),[mirror,setMirror]=useState(c.stewardship?.mirror_uri||c.manifest_uri);
  const active=useRef({id:c.id,digest:c.agreement_digest,account:wallet.accountId});active.current={id:c.id,digest:c.agreement_digest,account:wallet.accountId};
  const epoch=useRef(0);
  useEffect(()=>{epoch.current++;setKey('');setInspection(null);setAccepted(false);setError('');setWorking(false);},[c.id,c.agreement_digest,wallet.accountId]);
  useEffect(()=>{setPack(null);setUri(c.stewardship?.mirror_uri||c.manifest_uri);setMirror(c.stewardship?.mirror_uri||c.manifest_uri);return()=>{epoch.current++;};},[c.id,c.agreement_digest,c.stewardship?.mirror_uri]);
  const blocked=working||wallet.busy||!!wallet.pending||wallet.pendingDamaged;
  const account=snapshot.account?.account_id===wallet.accountId?snapshot.account:null;
  const contribution=account?.contributions.find((entry:any)=>entry.campaign_id===c.id);
  async function work(action:()=>Promise<void>){const token=epoch.current;setWorking(true);setError('');try{await action();}catch(e){if(epoch.current===token)setError((e as Error).message);}finally{if(epoch.current===token)setWorking(false);}}
  async function send(method:string,args:object,contentKey?:string){const result=await wallet.submit(method,args,contentKey);if(result&&result.status!=='cancelled'){setKey('');setInspection(null);setAccepted(false);onRefresh();}}
  async function open(){const token=epoch.current;const recovered=await fetchVerifiedMirror(uri,resourceCommitments(c));if(token===epoch.current)setPack(recovered);}
  async function restore(file:File){
    if(file.size>8*1024*1024)throw Error('Release backup exceeds 8 MiB.');
    const token=epoch.current,backup=JSON.parse(await file.text());
    const restored=await validateReleaseBackup(backup,{id:c.id,manifestHash:c.manifest_hash,keyCommitment:c.key_commitment});
    if(token===epoch.current){setKey(restored);setInspection(null);setAccepted(false);}
  }
  async function inspect(){
    const token=epoch.current,id=wallet.accountId,recovered=await fetchVerifiedMirror(c.manifest_uri,resourceCommitments(c,key));
    if(token===epoch.current&&active.current.account===id)setInspection({digest:c.agreement_digest,account:id,pack:recovered});
  }
  let total='';try{total=formatNear((BigInt(toYocto(amount))+(account?.registered?0n:BigInt(ACCOUNT_STORAGE))).toString());}catch{}
  const keyInput=<div className="p-key-input"><label>Private release backup<input type="file" accept=".json,application/json" disabled={blocked} onChange={event=>{const file=event.target.files?.[0];if(file)void work(()=>restore(file));}}/></label><details><summary>Enter a content key instead</summary><label>Content key<input type="password" value={key} onChange={event=>{setKey(event.target.value);setInspection(null);setAccepted(false);}} autoComplete="off" spellCheck={false}/></label></details></div>;
  return <div className="p-campaign-actions">
    {c.state==='Active'&&<><div className="p-funding-meter"><div><strong>{formatNear(c.total_contributed)} <small>testNEAR</small></strong><span>of {formatNear(c.target)} goal</span></div><progress value={Number(BigInt(c.total_contributed)*10000n/BigInt(c.target))} max={10000} aria-label={`${c.title} funding progress`}/><p>Funding closes {date(c.funding_deadline_ns)}.</p></div>
      <label>Sponsorship · testNEAR<input value={amount} inputMode="decimal" onChange={e=>setAmount(e.target.value)} disabled={blocked}/></label>
      <p className="p-small">{account?`Wallet deposit: ${total||'enter an amount'} testNEAR${account.registered?'':', including 0.01 for first-time storage'}.`:'First-time sponsors attach 0.01 testNEAR for storage, in addition to sponsorship.'} Network gas is separate.</p>
      <button className="p-button p-button-accent" disabled={blocked||!total} onClick={()=>void work(async()=>send('contribute',{id:c.id,amount:toYocto(amount)}))}>{wallet.busy?'Confirm in wallet…':'Sponsor public release'} ↗</button>
      <p className="p-small">Sponsorship funds a public CC0 release. Excess support becomes your withdrawable credit. Missed funding or release conditions allow contributor refunds.</p></>}
    {c.state==='Draft'&&<>{wallet.accountId===c.reviewer?<><p>Inspect the exact submission and its agreement before you approve it.</p>{keyInput}<button className="p-button" disabled={blocked||!key} onClick={()=>void work(inspect)}>{working?'Opening submission…':'Inspect submission'}</button>
      {inspection?.digest===c.agreement_digest&&inspection.account===wallet.accountId&&<><PackContent pack={inspection.pack}/><label className="p-checkbox"><input type="checkbox" checked={accepted} onChange={e=>setAccepted(e.target.checked)}/> I reviewed this exact content, CC0 release and funding agreement.</label><button className="p-button p-button-accent" disabled={blocked||!accepted} onClick={()=>void work(()=>send('approve_campaign',{id:c.id,agreement_digest:c.agreement_digest},key))}>Approve release agreement ↗</button></>}</>:<p>Awaiting review by <strong>{c.reviewer}</strong>.{!wallet.accountId&&<button className="p-text-button" onClick={()=>void wallet.connect()}>Connect reviewer wallet ↗</button>}</p>}</>}
    {c.state==='Funded'&&<><p>The goal is funded. Publish the matching content key by <strong>{date(c.release_deadline_ns)}</strong> to open the resource and credit its creator.</p>{keyInput}<p className="p-small">Submitting makes the content key public, including when execution fails. Retain the private backup until the result is confirmed.</p><button className="p-button p-button-accent" disabled={blocked||!key} onClick={()=>void work(()=>send('publish_release',{id:c.id,key_base64:key}))}>Release for everyone ↗</button></>}
    {c.state==='Refundable'&&<>{!wallet.accountId?<><p>The campaign’s release conditions expired. Connect your wallet to check your contribution.</p><button className="p-button" disabled={wallet.connecting} onClick={()=>void wallet.connect()}>Connect wallet</button></>:contribution&&!contribution.refunded&&BigInt(contribution.amount)>0n?<><p>Your refundable contribution is <strong>{formatNear(contribution.amount)} testNEAR</strong>.</p><button className="p-button p-button-accent" disabled={blocked} onClick={()=>void work(()=>send('claim_refund',{id:c.id}))}>Claim contribution refund ↗</button><p className="p-small">This credits your account. Withdraw the balance from My activity.</p></>:<p>No unclaimed refund for this account.</p>}</>}
    {c.state==='Released'&&<><div className="p-actions"><button className="p-button p-button-accent" disabled={working} onClick={()=>void work(open)}>{working?'Opening resource…':pack?'Reload resource':'Read resource'} ↗</button>{pack&&<button className="p-button" onClick={()=>download(pack.id+'-offline.html',createOfflineHtml(pack),'text/html')}>Download offline copy ↓</button>}</div>
      <details className="p-source-picker"><summary>Recovery source</summary><label>Choose a copy<select value={uri} disabled={working} onChange={e=>{setUri(e.target.value);setPack(null);setError('');}}>{Array.from(new Set([c.stewardship?.mirror_uri,c.manifest_uri].filter(Boolean))).map((value:any)=><option key={value} value={value}>{value===c.manifest_uri?'Original release':'Steward mirror'} · {new URL(value).hostname}</option>)}</select></label></details>
      {pack&&<PackContent pack={pack}/>}
      {wallet.accountId===c.stewardship?.owner_id&&<details className="p-steward-tools"><summary>Manage your stewardship</summary><p>Your token maintains this resource’s recovery mirror. Public copies stay open.</p>
        <label>Preferred mirror · HTTPS<input value={mirror} onChange={e=>setMirror(e.target.value)} disabled={blocked} type="url"/></label><button className="p-button" disabled={blocked||mirror===c.stewardship.mirror_uri} onClick={()=>void work(()=>send('set_mirror',{token_id:c.id,mirror_uri:mirror}))}>Update mirror ↗</button>
        <label>New steward account<input value={receiver} onChange={e=>setReceiver(e.target.value)} disabled={blocked} autoComplete="off" placeholder="recipient.testnet"/></label><button className="p-button" disabled={blocked||!receiver||receiver===wallet.accountId} onClick={()=>void work(()=>send('nft_transfer',{token_id:c.id,receiver_id:receiver}))}>Transfer stewardship ↗</button>
        <p className="p-small">A transfer resets the preferred mirror to the original source. Each mirror or transfer action attaches exactly one yoctoNEAR plus network gas.</p>
        <details><summary>Transfer to a receiving contract</summary><label>Receiver message<textarea value={message} maxLength={1024} onChange={e=>setMessage(e.target.value)} disabled={blocked}/></label><p className="p-small">The receiver must implement NEAR’s NFT callback. It may return the token.</p><button className="p-button" disabled={blocked||!receiver||receiver===wallet.accountId} onClick={()=>void work(()=>send('nft_transfer_call',{token_id:c.id,receiver_id:receiver,msg:message}))}>Request receiver acceptance ↗</button></details>
      </details>}
    </>}
    {error&&<p className="p-notice p-notice-error" role="alert">{error}</p>}
    <details className="p-agreement"><summary>Release agreement</summary><dl><div><dt>Creator</dt><dd>{c.creator}</dd></div><div><dt>Reviewer</dt><dd>{c.reviewer}</dd></div><div><dt>Funding goal</dt><dd>{formatNear(c.target)} testNEAR</dd></div><div><dt>Funding deadline</dt><dd>{date(c.funding_deadline_ns)}</dd></div><div><dt>Release window</dt><dd>{duration(c.release_window_ns)} after funding</dd></div><div><dt>License</dt><dd>CC0-1.0 on release</dd></div><div><dt>Content commitment</dt><dd className="p-hash">{c.plaintext_hash}</dd></div></dl></details>
  </div>;
}
