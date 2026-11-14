'use client';
import {createContext,useContext,useEffect,useState} from 'react';
import WalletProvider,{useWallet,WalletControl,WalletStatus} from '../../components/WalletProvider';
import CampaignActions,{date} from '../../components/CampaignActions';
import CreatorStudio from '../../components/CreatorStudio';
import SunsetMark from '../../components/SunsetMark';
import {SiteHeader,SiteFooter,ResourceCard,Icon} from '../../components/Protocol';
import {resources} from '../../lib/library.mjs';
import {formatNear,toYocto} from '../../lib/ledger.mjs';
import {DEPLOYMENT} from '../../lib/live.mjs';
import {Address,CopyChip,Fingerprint} from '../../components/Onchain';
import {accountUrl} from '../../lib/proof.mjs';

const views=['Explore','Funding','My activity','Studio','Stewardship'];
const legacy:Record<string,string>={Discover:'Explore','Creator studio':'Studio',Activity:'My activity','My library':'Explore','Access budgets':'My activity'};
const stateLabels:Record<string,string>={Draft:'Awaiting review',Active:'Open for sponsorship',Funded:'Ready for release',Released:'Released',Refundable:'Refunds open'};
const Navigate=createContext<(event:React.MouseEvent<HTMLAnchorElement>,view:string)=>void>(()=>{});
function ViewLink({view,className,children}:{view:string,className?:string,children:React.ReactNode}){
  const navigate=useContext(Navigate);
  return <a className={className} href={`/app/?view=${encodeURIComponent(view)}`} onClick={event=>navigate(event,view)}>{children}</a>;
}
const host=(uri:string)=>{try{return new URL(uri).hostname;}catch{return uri;}};
function PageHead({title,children}:{title:string,children:React.ReactNode}){return <div className="p-page-head"><h1>{title}</h1><p>{children}</p></div>;}
function LiveState(){
  const wallet=useWallet();
  if(wallet.loading)return <div className="p-network-state" role="status"><span className="p-spinner"/> Reading NEAR testnet…</div>;
  if(wallet.snapshot)return null;
  return <div className="p-empty p-network-down"><span className="p-empty-icon"><Icon name="alert" size={22}/></span><h2>Live network data is unavailable.</h2><p>The reading library still works. Try again to use campaigns and account actions.</p><button className="p-button" onClick={()=>void wallet.refresh()}><Icon name="refresh"/>Try again</button></div>;
}
function Stages({campaign:c}:{campaign:any}){
  const funded=!!c.funded_at_ns&&c.funded_at_ns!=='0',refundable=c.state==='Refundable';
  const reached=refundable?(funded?2:1):['Draft','Active','Funded','Released'].indexOf(c.state);
  const status=(i:number)=>i<reached?'done':i===reached?(refundable?'failed':'current'):'pending';
  const goal=`${formatNear(c.target)} testNEAR`;
  const items=[
    ['Review',{done:`Approved by ${c.reviewer}`,current:`Waiting for ${c.reviewer}`}],
    ['Funding',{done:`${goal} goal met`,current:`${goal} goal, closes ${date(c.funding_deadline_ns)}`,failed:`Goal not met by ${date(c.funding_deadline_ns)}`,pending:`${goal} goal`}],
    ['Release',{done:'Public under CC0',current:funded?`Key due ${date(c.release_deadline_ns)}`:'',failed:'Key not published in time',pending:'Opens when the key is published'}]
  ] as const;
  return <ol className="p-stages" aria-label="Campaign progress">{items.map(([label,detail],i)=>{const s=status(i);return <li key={label} className={'p-stage-'+s}><span className="p-stage-dot" aria-hidden="true">{s==='done'?<Icon name="check" size={14}/>:s==='failed'?<Icon name="close" size={14}/>:i+1}</span><div><strong>{label}<span className="sr-only">: {s==='done'?'complete':s==='failed'?'missed':s==='current'?'in progress':'not started'}</span></strong><small>{refundable&&s==='pending'?'':(detail as Record<string,string>)[s]||''}</small></div></li>;})}
    {refundable&&<li className="p-stage-refund"><span className="p-stage-dot" aria-hidden="true"><Icon name="back" size={14}/></span><div><strong>Refunds open</strong><small>Sponsors can claim their contribution</small></div></li>}</ol>;
}
function Campaign({campaign:c,open=false}:{campaign:any,open?:boolean}){
  const wallet=useWallet();
  const percent=BigInt(c.target)>0n?Math.min(100,Number(BigInt(c.total_contributed)*100n/BigInt(c.target))):0;
  const note=c.state==='Active'?`Closes ${date(c.funding_deadline_ns)}`:c.state==='Funded'?`Release due ${date(c.release_deadline_ns)}`:c.state==='Released'?'Public under CC0':c.state==='Refundable'?'Contributions refundable':`Reviewer: ${c.reviewer}`;
  return <details className={'p-campaign p-campaign-'+c.state.toLowerCase()} id={'campaign-'+c.id} open={open}><summary>
      <Fingerprint hash={c.plaintext_hash}/><span className="p-campaign-main"><span className={'p-state p-state-'+c.state.toLowerCase()}>{stateLabels[c.state]}</span><strong>{c.title}</strong><small>by {c.creator}</small></span>
      <span className="p-campaign-funding"><span><b>{formatNear(c.total_contributed)}</b> of {formatNear(c.target)} testNEAR</span><span className="p-meter" aria-hidden="true"><i style={{width:percent+'%'}}/></span><small>{note}</small></span>
      <span className="p-campaign-expand" aria-hidden="true"><Icon name="chevron" size={20}/></span></summary>
    <div className="p-campaign-body"><Stages campaign={c}/><CampaignActions campaign={c} snapshot={wallet.snapshot} onRefresh={()=>void wallet.refresh()}/></div>
  </details>;
}
function Funding({campaignId}:{campaignId:string}){
  const wallet=useWallet(),s=wallet.snapshot;
  const head=<PageHead title="Campaigns">Each campaign has a fixed goal, a named creator and two deadlines. It ends in a public release or in refunds.</PageHead>;
  if(!s)return <section>{head}<LiveState/></section>;
  const current=s.campaigns.filter((c:any)=>['Active','Draft','Funded'].includes(c.state)),history=s.campaigns.filter((c:any)=>['Released','Refundable'].includes(c.state));
  return <section>{head}
    {campaignId&&!s.campaigns.some((c:any)=>c.id===campaignId)&&<p className="p-notice"><Icon name="info"/><span>That campaign is not in the live catalog. The available campaigns are listed below.</span></p>}
    {current.length?<div className="p-campaign-list">{current.map((c:any)=><Campaign key={c.id} campaign={c} open={c.id===campaignId||c.state==='Active'}/>)}</div>
      :<div className="p-empty"><span className="p-empty-icon"><SunsetMark/></span><h2>No campaign is open for sponsorship right now.</h2><p>Every campaign on this deployment has finished, either with a release or with refunds. You can inspect them below, or read the open library while the next resource is reviewed.</p><div className="p-actions"><ViewLink view="Explore" className="p-button p-button-accent">Read the library</ViewLink><a className="p-button" href="/#how-it-works">How funding works</a></div></div>}
    {!!history.length&&<section className="p-history" aria-labelledby="history-title"><div className="p-list-head"><h2 id="history-title">Completed campaigns</h2><p>{history.length} finished on this deployment. Open one to read its resource or claim a refund.</p></div><div className="p-campaign-list">{history.map((c:any)=><Campaign key={c.id} campaign={c} open={c.id===campaignId}/>)}</div></section>}
  </section>;
}
function Activity(){
  const wallet=useWallet(),account=wallet.snapshot?.account,[amount,setAmount]=useState('');
  useEffect(()=>{setAmount(account?.account_id===wallet.accountId?formatNear(account.credit):'');},[account?.account_id,account?.credit,wallet.accountId]);
  const head=<PageHead title="My activity">Your contributions, withdrawable credit and confirmed payouts on NEAR testnet.</PageHead>;
  if(!wallet.accountId)return <section>{head}<div className="p-empty"><span className="p-empty-icon"><Icon name="wallet" size={22}/></span><h2>Connect a wallet to see your activity.</h2><p>Nothing is signed when you connect. Your contributions, credit and payouts are read from the contract.</p><button className="p-button p-button-accent" disabled={wallet.connecting} onClick={()=>void wallet.connect()}>{wallet.connecting?'Opening wallet…':'Connect a testnet wallet'}</button></div></section>;
  if(!account||account.account_id!==wallet.accountId)return <section>{head}<LiveState/></section>;
  const blocked=wallet.busy||!!wallet.pending||wallet.pendingDamaged||!!account.pending;
  let valid=false;try{const value=BigInt(toYocto(amount));valid=value>0n&&value<=BigInt(account.credit);}catch{}
  const hasCredit=BigInt(account.credit)>0n;
  return <section>{head}<p className="p-account-line">Signed in as <span className="p-account-label">{wallet.accountId}</span></p>
    <div className="p-account-stats"><article className="p-panel"><h2>Withdrawable credit</h2><strong>{formatNear(account.credit)} <small>testNEAR</small></strong><p>Creator credit, claimed refunds and excess sponsorship.</p></article><article className="p-panel"><h2>Payouts confirmed</h2><strong>{formatNear(account.paid)} <small>testNEAR</small></strong><p>Transfers whose onchain callback recorded success.</p></article></div>
    <div className="p-panel"><h2>Withdraw to your wallet</h2>{account.pending?<p className="p-notice"><Icon name="clock"/><span>A withdrawal is pending onchain: operation {account.pending.operation_id}, {formatNear(account.pending.amount)} testNEAR. Check the original receipt before trying again.</span></p>:!hasCredit?<p className="p-quiet">You have no withdrawable credit at this block. Credit appears after a refund claim or a release you created.</p>:<><div className="p-inline-form"><label>Amount in testNEAR<input value={amount} inputMode="decimal" onChange={e=>setAmount(e.target.value)} disabled={blocked} aria-invalid={!!amount&&!valid}/></label><button className="p-button p-button-accent" disabled={blocked||!valid} onClick={()=>void wallet.submit('withdraw',{amount:toYocto(amount)})}>{wallet.busy?'Processing request…':'Withdraw credit'}</button></div><p className="p-small">{amount&&!valid?`Enter an amount up to ${formatNear(account.credit)} testNEAR.`:'Credit becomes a payout once the transfer and its callback complete. Network gas is paid separately.'}</p></>}</div>
    <div className="p-panel"><h2>Your contributions</h2>{account.contributions.length?<div className="p-contributions">{account.contributions.map((contribution:any)=>{const c=wallet.snapshot.campaigns.find((c:any)=>c.id===contribution.campaign_id);const status=contribution.refunded?'Refund claimed':c?.state==='Refundable'?'Refund available':c?.state==='Released'?'Resource released':'Sponsorship recorded';return <article key={contribution.campaign_id}><div><a href={`/app/?view=Funding&campaign=${encodeURIComponent(contribution.campaign_id)}`}>{c?.title||contribution.campaign_id}</a><span className={status==='Refund available'?'p-state p-state-refundable':'p-contribution-status'}>{status}</span></div><strong>{formatNear(contribution.amount)} testNEAR</strong></article>;})}</div>:<><p className="p-quiet">This account has not sponsored a campaign yet.</p><ViewLink view="Funding" className="p-text-button">Browse campaigns<Icon name="forward"/></ViewLink></>}</div>
  </section>;
}
function Stewardship(){
  const wallet=useWallet(),s=wallet.snapshot;
  const head=<PageHead title="Stewardship">Each released resource has one transferable token. Its holder maintains the recovery mirror; readers keep their copies either way.</PageHead>;
  if(!s)return <section>{head}<LiveState/></section>;
  const tokens=s.campaigns.filter((c:any)=>c.state==='Released');
  return <section>{head}{tokens.length?tokens.map((c:any)=>{const mine=wallet.accountId===c.stewardship.owner_id;return <article className="p-panel p-token" key={c.id}><div className="p-token-heading"><SunsetMark/><div><h2>{c.title}</h2><p>Stewardship token{mine&&<span className="p-state p-state-released">You hold this</span>}</p></div></div><dl><div><dt>Current steward</dt><dd><Address id={c.stewardship.owner_id}/></dd></div><div><dt>Token ID</dt><dd>{c.id}</dd></div><div><dt>Preferred mirror</dt><dd>{host(c.stewardship.mirror_uri||c.manifest_uri)}</dd></div></dl>{!mine&&<p className="p-small">Only the current steward’s wallet can transfer this token or change its mirror.</p>}<CampaignActions campaign={c} snapshot={s} onRefresh={()=>void wallet.refresh()}/></article>;}):<div className="p-empty"><span className="p-empty-icon"><SunsetMark/></span><h2>No stewardship tokens yet.</h2><p>A token is created when a campaign releases its resource.</p><ViewLink view="Funding" className="p-button">Browse campaigns</ViewLink></div>}</section>;
}
function Explore(){
  const wallet=useWallet(),s=wallet.snapshot;
  return <section><PageHead title="Library">Original technical guides with worked examples and calculations you can change. No wallet needed to read.</PageHead>
    <div className="p-resource-grid">{resources.map(resource=><ResourceCard key={resource.id} resource={resource} heading="h2"/>)}</div>
    <div className="p-chain-band"><div><h2>Funded releases on NEAR testnet</h2><p>Campaigns are read from the live contract. Sponsoring, refunds and withdrawals are signed in your own wallet.</p><ViewLink view="Funding" className="p-button">Browse campaigns<Icon name="forward"/></ViewLink>
      <div className="p-band-proof"><span>Contract</span><CopyChip value={DEPLOYMENT.contract} label="contract address" href={accountUrl(DEPLOYMENT.contract)} head={24} tail={0}/>{s&&<span className="p-verified"><Icon name="check" size={14}/>Code hash verified</span>}</div></div>{s?<dl><div><dt>Campaigns</dt><dd>{s.campaigns.length}</dd></div><div><dt>Released</dt><dd>{s.campaigns.filter((c:any)=>c.state==='Released').length}</dd></div><div><dt>Open now</dt><dd>{s.campaigns.filter((c:any)=>c.state==='Active').length}</dd></div></dl>:<LiveState/>}</div>
  </section>;
}
function LiveApp(){
  const wallet=useWallet(),[view,setView]=useState('Explore'),[campaignId,setCampaignId]=useState('');
  useEffect(()=>{function read(){const query=new URLSearchParams(location.search),requested=query.get('view')||'Explore';if(requested==='Handbook'){location.replace('/try-maintainer-handbook.html');return;}if(requested==='How it works'){location.replace('/#how-it-works');return;}setView(views.includes(requested)?requested:legacy[requested]||'Explore');setCampaignId(query.get('campaign')||'');}read();window.addEventListener('popstate',read);return()=>window.removeEventListener('popstate',read);},[]);
  function navigate(event:React.MouseEvent<HTMLAnchorElement>,next:string){if(event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;event.preventDefault();history.pushState(null,'',`/app/?view=${encodeURIComponent(next)}`);setView(next);setCampaignId('');window.scrollTo({top:0,behavior:'auto'});requestAnimationFrame(()=>document.getElementById('app-content')?.focus({preventScroll:true}));}
  const s=wallet.snapshot;
  return <Navigate.Provider value={navigate}><div className="protocol-site p-app"><a className="p-skip" href="#app-content">Skip to content</a><SiteHeader compact wallet={<WalletControl/>}><></></SiteHeader>
    <div className="p-app-bar"><div className="p-container p-app-bar-row"><nav className="p-app-nav" aria-label="App navigation">{views.map(item=><a key={item} href={`/app/?view=${encodeURIComponent(item)}`} aria-current={view===item?'page':undefined} onClick={event=>navigate(event,item)}>{item}</a>)}</nav>
      <div className="p-chain"><span className={'p-network '+(s?'p-network-ready':wallet.loading?'':'p-network-down')}><span className="p-live-dot"/>{s?`Testnet block ${Number(s.height).toLocaleString('en-US')}`:wallet.loading?'Connecting to testnet':'Testnet unavailable'}</span><button className="p-refresh" disabled={wallet.loading||wallet.busy} onClick={()=>void wallet.refresh()}><Icon name="refresh" size={16}/><span>{wallet.loading?'Reading chain…':'Refresh state'}</span></button></div></div></div>
    <main id="app-content" className="p-container p-app-main" tabIndex={-1}><WalletStatus/><div key={view} className="p-view">{view==='Explore'?<Explore/>:view==='Funding'?<Funding campaignId={campaignId}/>:view==='My activity'?<Activity/>:view==='Studio'?<CreatorStudio snapshot={wallet.snapshot} onRefresh={()=>void wallet.refresh()}/>:<Stewardship/>}</div></main>
    <SiteFooter network={<a href={`https://explorer.testnet.near.org/accounts/${DEPLOYMENT.contract}`} target="_blank" rel="noreferrer">Contract {DEPLOYMENT.contract} on NEAR testnet<Icon name="external" size={14}/></a>}/>
  </div></Navigate.Provider>;
}
export default function App(){return <WalletProvider><LiveApp/></WalletProvider>;}
