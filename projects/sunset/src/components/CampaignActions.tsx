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
import {Icon} from './Protocol';
import {Address,CopyChip,Fingerprint} from './Onchain';

export function PackContent({pack}:{pack:any}){
  if(pack.kind==='guide')return <GuideReader pack={pack as GuidePack}/>;
  return <section className="p-legacy-reader"><h3>{pack.title}</h3><p>{pack.description}</p>{pack.questions.map((q:any)=><details key={q.id}><summary>{q.prompt}</summary><ul aria-label="Answer choices">{q.choices.map((choice:number)=><li key={choice}>{choice}</li>)}</ul><p><strong>Correct answer: {q.answer}</strong></p><p>{q.explanation}</p></details>)}</section>;
}
export const date=(ns:string)=>new Date(Number(BigInt(ns)/1000000n)).toLocaleString(undefined,{dateStyle:'medium',timeStyle:'short'});
function duration(ns:string){const n=BigInt(ns);for(const [unit,label] of [[3600000000000n,'hours'],[60000000000n,'minutes'],[1000000000n,'seconds']] as const)if(n%unit===0n)return `${n/unit} ${label}`;return `${n} nanoseconds`;}
export default function CampaignActions({campaign:c,snapshot,onRefresh}:{campaign:any,snapshot:any,onRefresh:()=>void}){
  const wallet=useWallet(),[amount,setAmount]=useState('0.1'),[key,setKey]=useState(''),[pack,setPack]=useState<any>(null),[inspection,setInspection]=useState<any>(null);
  const [accepted,setAccepted]=useState(false),[working,setWorking]=useState(false),[error,setError]=useState(''),[receiver,setReceiver]=useState(''),[message,setMessage]=useState('');
  const [uri,setUri]=useState(c.stewardship?.mirror_uri||c.manifest_uri),[mirror,setMirror]=useState(c.stewardship?.mirror_uri||c.manifest_uri);
  const active=useRef({id:c.id,digest:c.agreement_digest,account:wallet.accountId});active.current={id:c.id,digest:c.agreement_digest,account:wallet.accountId};
  const epoch=useRef(0);
  useEffect(()=>{epoch.current++;setKey('');setInspection(null);setAccepted(false);setError('');setWorking(false);},[c.id,c.agreement_digest,wallet.accountId]);
  useEffect(()=>{setPack(null);setUri(c.stewardship?.mirror_uri||c.manifest_uri);setMirror(c.stewardship?.mirror_uri||c.manifest_uri);return()=>{epoch.current++;};},[c.id,c.agreement_digest,c.stewardship?.mirror_uri]);
  const blocked=working||wallet.busy||wallet.loading||!!wallet.pending||wallet.pendingDamaged;
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
  const keyInput=<div className="p-key-input"><label>Private release backup (JSON)<input type="file" accept=".json,application/json" disabled={blocked} onChange={event=>{const file=event.target.files?.[0];if(file)void work(()=>restore(file));}}/></label><details><summary>Enter a content key instead</summary><label>Content key<input type="password" value={key} onChange={event=>{setKey(event.target.value);setInspection(null);setAccepted(false);}} autoComplete="off" spellCheck={false}/></label></details></div>;
  return <div className="p-campaign-actions">
    {c.state==='Active'&&<div className="p-sponsor"><h3>Sponsor this release</h3><progress className="sr-only" value={Number(BigInt(c.total_contributed)*10000n/BigInt(c.target))} max={10000} aria-label={`${c.title} funding progress`}/>
      <div className="p-inline-form"><label>Amount in testNEAR<input value={amount} inputMode="decimal" onChange={e=>setAmount(e.target.value)} disabled={blocked} aria-invalid={!total}/></label>
      <button className="p-button p-button-accent" disabled={blocked||!total} onClick={()=>void work(async()=>send('contribute',{id:c.id,amount:toYocto(amount)}))}>{wallet.busy?'Confirm in wallet…':'Sponsor public release'}</button></div>
      <p className="p-small">{!total?'Enter an amount such as 0.1.':account?`Your wallet will ask for ${total} testNEAR${account.registered?'':', including 0.01 for first-time storage'}, plus network gas.`:'First-time sponsors attach 0.01 testNEAR for storage on top of the sponsorship, plus network gas.'}</p>
      <ul className="p-terms"><li><Icon name="check" size={16}/>Funds a public CC0 release.</li><li><Icon name="check" size={16}/>Anything above the goal returns to you as credit.</li><li><Icon name="check" size={16}/>If a deadline is missed you can claim a full refund.</li></ul></div>}
    {c.state==='Draft'&&<>{wallet.accountId===c.reviewer?<><h3>Review this submission</h3><p>Inspect the exact content and its agreement before you approve it.</p>{keyInput}<button className="p-button" disabled={blocked||!key} onClick={()=>void work(inspect)}>{working?'Opening submission…':'Inspect submission'}</button>
      {inspection?.digest===c.agreement_digest&&inspection.account===wallet.accountId&&<><PackContent pack={inspection.pack}/><label className="p-checkbox"><input type="checkbox" checked={accepted} onChange={e=>setAccepted(e.target.checked)}/> I reviewed this exact content, CC0 release and funding agreement.</label><button className="p-button p-button-accent" disabled={blocked||!accepted} onClick={()=>void work(()=>send('approve_campaign',{id:c.id,agreement_digest:c.agreement_digest},key))}>Approve release agreement</button></>}</>:<><p>Waiting for <strong>{c.reviewer}</strong> to review the content. Sponsorship opens once it is approved.</p>{!wallet.accountId&&<button className="p-button" onClick={()=>void wallet.connect()}>Connect as reviewer</button>}</>}</>}
    {c.state==='Funded'&&<><h3>Release the resource</h3><p>The goal is funded. Publish the matching content key by <strong>{date(c.release_deadline_ns)}</strong> to open the resource and credit its creator.</p>{keyInput}<p className="p-notice p-notice-warning"><Icon name="alert"/><span>Submitting makes the content key public, even if the transaction fails. Keep the private backup until the result is confirmed.</span></p><button className="p-button p-button-accent" disabled={blocked||!key} onClick={()=>void work(()=>send('publish_release',{id:c.id,key_base64:key}))}>Release for everyone</button></>}
    {c.state==='Refundable'&&<>{!wallet.accountId?<><p>This campaign missed a deadline, so contributions are refundable. Connect the wallet you sponsored with to check yours.</p><button className="p-button" disabled={wallet.connecting} onClick={()=>void wallet.connect()}>Check my refund</button></>:contribution&&!contribution.refunded&&BigInt(contribution.amount)>0n?<><h3>Your refund</h3><p>You contributed <strong>{formatNear(contribution.amount)} testNEAR</strong>, and all of it is refundable.</p><button className="p-button p-button-accent" disabled={blocked} onClick={()=>void work(()=>send('claim_refund',{id:c.id}))}>Claim contribution refund</button><p className="p-small">Claiming adds the amount to your credit. Withdraw it from My activity.</p></>:<p className="p-quiet">{contribution?.refunded?'You already claimed your refund for this campaign.':'This account has no contribution to refund here.'}</p>}</>}
    {c.state==='Released'&&<><div className="p-actions"><button className="p-button p-button-accent" disabled={working} onClick={()=>void work(open)}>{working?'Verifying and opening…':pack?'Reload resource':'Read resource'}</button>{pack&&<button className="p-button" onClick={()=>download(pack.id+'-offline.html',createOfflineHtml(pack),'text/html')}><Icon name="download"/>Download offline copy</button>}</div>
      <details className="p-source-picker"><summary>Choose where to load it from</summary><label>Source<select value={uri} disabled={working} onChange={e=>{setUri(e.target.value);setPack(null);setError('');}}>{Array.from(new Set([c.stewardship?.mirror_uri,c.manifest_uri].filter(Boolean))).map((value:any)=><option key={value} value={value}>{value===c.manifest_uri?'Original release':'Steward mirror'} ({new URL(value).hostname})</option>)}</select></label></details>
      {pack&&<PackContent pack={pack}/>}
      {wallet.accountId===c.stewardship?.owner_id&&<details className="p-steward-tools"><summary>Manage your stewardship</summary><p>Your token maintains this resource’s recovery mirror. Public copies stay open.</p>
        <label>Preferred mirror (HTTPS URL)<input value={mirror} onChange={e=>setMirror(e.target.value)} disabled={blocked} type="url"/></label><button className="p-button" disabled={blocked||mirror===c.stewardship.mirror_uri} onClick={()=>void work(()=>send('set_mirror',{token_id:c.id,mirror_uri:mirror}))}>Update mirror</button>
        <label>New steward account<input value={receiver} onChange={e=>setReceiver(e.target.value)} disabled={blocked} autoComplete="off" placeholder="recipient.testnet"/></label><button className="p-button" disabled={blocked||!receiver||receiver===wallet.accountId} onClick={()=>void work(()=>send('nft_transfer',{token_id:c.id,receiver_id:receiver}))}>Transfer stewardship</button>
        <p className="p-small">A transfer resets the preferred mirror to the original source. Each mirror or transfer action attaches exactly one yoctoNEAR plus network gas.</p>
        <details><summary>Transfer to a receiving contract</summary><label>Receiver message<textarea value={message} maxLength={1024} onChange={e=>setMessage(e.target.value)} disabled={blocked}/></label><p className="p-small">The receiver must implement NEAR’s NFT callback. It may return the token.</p><button className="p-button" disabled={blocked||!receiver||receiver===wallet.accountId} onClick={()=>void work(()=>send('nft_transfer_call',{token_id:c.id,receiver_id:receiver,msg:message}))}>Request receiver acceptance</button></details>
      </details>}
    </>}
    {error&&<p className="p-notice p-notice-error" role="alert"><Icon name="alert"/><span>{error}</span></p>}
    <details className="p-agreement"><summary>Release agreement and content commitment</summary><dl><div><dt>Creator</dt><dd><Address id={c.creator}/></dd></div><div><dt>Reviewer</dt><dd><Address id={c.reviewer}/></dd></div><div><dt>Funding goal</dt><dd>{formatNear(c.target)} testNEAR</dd></div><div><dt>Funding deadline</dt><dd>{date(c.funding_deadline_ns)}</dd></div><div><dt>Release window</dt><dd>{duration(c.release_window_ns)} after funding</dd></div><div><dt>License</dt><dd>CC0-1.0 on release</dd></div><div><dt>Content commitment (SHA-256)</dt><dd className="p-commitment"><Fingerprint hash={c.plaintext_hash} size={32}/><CopyChip value={c.plaintext_hash} label="content commitment" head={16} tail={16}/></dd></div></dl></details>
  </div>;
}
