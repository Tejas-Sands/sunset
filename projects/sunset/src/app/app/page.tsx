'use client';
import {useEffect,useState} from 'react';
import WalletProvider,{useWallet,WalletControl,WalletStatus} from '../../components/WalletProvider';
import CampaignActions from '../../components/CampaignActions';
import CreatorStudio from '../../components/CreatorStudio';
import SunsetMark from '../../components/SunsetMark';
import {SiteHeader,SiteFooter,ResourceCard} from '../../components/Protocol';
import {resources} from '../../lib/library.mjs';
import {formatNear,toYocto} from '../../lib/ledger.mjs';
import {DEPLOYMENT} from '../../lib/live.mjs';

const views=['Explore','Funding','My activity','Studio','Stewardship'];
const legacy:Record<string,string>={Discover:'Explore','Creator studio':'Studio',Activity:'My activity','My library':'Explore','Access budgets':'My activity'};
function LiveState(){const wallet=useWallet();return wallet.loading?<div className="p-network-state" role="status"><span className="p-spinner"/> Reading NEAR testnet…</div>:!wallet.snapshot?<div className="p-panel p-network-state"><h2>Live network data is unavailable.</h2><p>Your reading library is ready. Retry the connection to use funding and account actions.</p><button className="p-button" onClick={()=>void wallet.refresh()}>Retry network connection ↗</button></div>:null;}
function Campaign({campaign,open=false}:{campaign:any,open?:boolean}){
  const wallet=useWallet();
  const labels:Record<string,string>={Draft:'Awaiting review',Active:'Accepting sponsorship',Funded:'Ready for release',Released:'Released',Refundable:'Refund period'};
  return <details className="p-campaign" id={'campaign-'+campaign.id} open={open}><summary><span><span className={'p-state p-state-'+campaign.state.toLowerCase()}>{labels[campaign.state]}</span><strong>{campaign.title}</strong><small>{campaign.creator}</small></span><span className="p-campaign-total">{formatNear(campaign.total_contributed)} <small>testNEAR sponsored</small></span><span className="p-campaign-expand" aria-hidden="true">+</span></summary>
    <CampaignActions campaign={campaign} snapshot={wallet.snapshot} onRefresh={()=>void wallet.refresh()}/>
  </details>;
}
function Funding({campaignId}:{campaignId:string}){
  const wallet=useWallet(),s=wallet.snapshot;
  if(!s)return <LiveState/>;
  const current=s.campaigns.filter((c:any)=>['Active','Draft','Funded'].includes(c.state)),history=s.campaigns.filter((c:any)=>['Released','Refundable'].includes(c.state));
  return <section><div className="p-section-heading"><div><span className="p-kicker">LIVE CAMPAIGNS</span><h1>Fund the beginning.<br/>Open what follows.</h1></div><p>Fixed goals. Named creators. Public release or contribution refunds.</p></div>
    {!current.length&&<div className="p-empty"><span className="p-kicker">BETWEEN ROUNDS</span><h2>No active funding round right now.</h2><p>The current campaigns have completed their release or refund paths. Explore the open technical library while the next reviewed resource is prepared.</p><a className="p-button" href="/app/?view=Studio">Open creator studio ↗</a></div>}
    {campaignId&&!s.campaigns.some((c:any)=>c.id===campaignId)&&<p className="p-notice">This campaign is not in the current live catalog. Browse the available rounds below.</p>}
    {current.map((c:any)=><Campaign key={c.id} campaign={c} open={c.id===campaignId||c.state==='Active'}/>)}
    {!!history.length&&<section className="p-history"><div className="p-section-heading"><div><span className="p-kicker">ONCHAIN ARCHIVE</span><h2>Every ending stays visible.</h2></div><p>Actual released and refund-eligible campaigns from this deployment.</p></div>{history.map((c:any)=><Campaign key={c.id} campaign={c} open={c.id===campaignId}/>)}</section>}
  </section>;
}
function Activity(){
  const wallet=useWallet(),account=wallet.snapshot?.account,[amount,setAmount]=useState('');
  useEffect(()=>{setAmount(account?.account_id===wallet.accountId?formatNear(account.credit):'');},[account?.account_id,account?.credit,wallet.accountId]);
  if(!wallet.accountId)return <section className="p-empty"><span className="p-kicker">YOUR ACCOUNT</span><h1>Your part of the commons.</h1><p>Connect a testnet wallet to see your actual contributions, credit and native payouts.</p><button className="p-button p-button-accent" disabled={wallet.connecting} onClick={()=>void wallet.connect()}>Connect wallet ↗</button></section>;
  if(!account||account.account_id!==wallet.accountId)return <LiveState/>;
  const blocked=wallet.busy||!!wallet.pending||wallet.pendingDamaged||!!account.pending;
  let valid=false;try{const value=BigInt(toYocto(amount));valid=value>0n&&value<=BigInt(account.credit);}catch{}
  return <section><div className="p-section-heading"><div><span className="p-kicker">MY ACTIVITY</span><h1>Your support.<br/>Your onchain balance.</h1></div><p className="p-account-label">{wallet.accountId}</p></div>
    <div className="p-account-stats"><article className="p-panel"><span className="p-kicker">WITHDRAWABLE CREDIT</span><strong>{formatNear(account.credit)} <small>testNEAR</small></strong><p>Creator credit, claimed refunds and excess sponsorship.</p></article><article className="p-panel"><span className="p-kicker">NATIVE PAYOUTS CONFIRMED</span><strong>{formatNear(account.paid)} <small>testNEAR</small></strong><p>Transfers whose onchain callback recorded a successful payout.</p></article></div>
    <div className="p-panel"><h2>Withdraw to your wallet.</h2>{account.pending?<p className="p-notice">A native withdrawal is pending onchain. Operation {account.pending.operation_id}, {formatNear(account.pending.amount)} testNEAR. Check the original receipt before trying again.</p>:BigInt(account.credit)===0n?<p>No withdrawable credit at this finalized block.</p>:<><label>Amount · testNEAR<input value={amount} inputMode="decimal" onChange={e=>setAmount(e.target.value)} disabled={blocked}/></label><button className="p-button p-button-accent" disabled={blocked||!valid} onClick={()=>void wallet.submit('withdraw',{amount:toYocto(amount)})}>{wallet.busy?'Processing request…':'Withdraw credit'} ↗</button><p className="p-small">Credit becomes a payout after the native transfer and callback complete. Network gas is paid separately.</p></>}</div>
    <div className="p-panel"><h2>Your contributions.</h2>{account.contributions.length?<div className="p-contributions">{account.contributions.map((contribution:any)=>{const c=wallet.snapshot.campaigns.find((c:any)=>c.id===contribution.campaign_id);return <article key={contribution.campaign_id}><div><a href={`/app/?view=Funding&campaign=${encodeURIComponent(contribution.campaign_id)}`}>{c?.title||contribution.campaign_id} ↗</a><span>{contribution.refunded?'Refund claimed':c?.state==='Refundable'?'Refund available':c?.state==='Released'?'Resource released':'Sponsorship recorded'}</span></div><strong>{formatNear(contribution.amount)} testNEAR</strong></article>;})}</div>:<p>No contributions from this account yet.</p>}</div>
  </section>;
}
function Stewardship(){
  const wallet=useWallet(),s=wallet.snapshot;if(!s)return <LiveState/>;
  const tokens=s.campaigns.filter((c:any)=>c.state==='Released');
  return <section><div className="p-section-heading"><div><span className="p-kicker">STEWARDSHIP</span><h1>A responsibility.<br/>Passed forward.</h1></div><p>The token maintains a recovery mirror. Readers keep their public copies.</p></div>{tokens.length?tokens.map((c:any)=><article className="p-panel p-token" key={c.id}><div className="p-token-heading"><SunsetMark/><div><span className="p-kicker">TRANSFERABLE MAINTENANCE RIGHT</span><h2>{c.title}</h2></div></div><dl><div><dt>Current steward</dt><dd>{c.stewardship.owner_id}</dd></div><div><dt>Token ID</dt><dd>{c.id}</dd></div></dl>{wallet.accountId!==c.stewardship.owner_id&&<p className="p-small">Connect the current steward’s wallet to transfer this token or update its mirror.</p>}<CampaignActions campaign={c} snapshot={s} onRefresh={()=>void wallet.refresh()}/></article>):<div className="p-empty"><h2>No stewardship tokens yet.</h2><p>A successful public release creates its maintenance token.</p></div>}</section>;
}
function Explore(){
  const wallet=useWallet(),s=wallet.snapshot;
  return <section><div className="p-section-heading"><div><span className="p-kicker">THE OPEN KNOWLEDGE COMMONS</span><h1>Useful ideas.<br/>Yours to keep.</h1></div><p>Original technical guides. Worked examples. Real calculations. No wallet to read.</p></div>
    <div className="p-resource-grid">{resources.map(resource=><ResourceCard key={resource.id} resource={resource}/>)}</div>
    <div className="p-chain-band"><div><span className="p-kicker">THE RELEASE LAYER</span><h2>Backed by actual chain state.</h2><p>Wallet actions use the existing NEAR testnet contract. New campaigns are curated by its creator account.</p><a className="p-button" href="/app/?view=Funding">Explore onchain campaigns ↗</a></div>{s?<dl><div><dt>Live campaigns</dt><dd>{s.campaigns.length}</dd></div><div><dt>Open releases</dt><dd>{s.campaigns.filter((c:any)=>c.state==='Released').length}</dd></div><div><dt>Active rounds</dt><dd>{s.campaigns.filter((c:any)=>c.state==='Active').length}</dd></div></dl>:<LiveState/>}</div>
  </section>;
}
function LiveApp(){
  const wallet=useWallet(),[view,setView]=useState('Explore'),[campaignId,setCampaignId]=useState('');
  useEffect(()=>{function read(){const query=new URLSearchParams(location.search),requested=query.get('view')||'Explore';if(requested==='Handbook'){location.replace('/try-maintainer-handbook.html');return;}if(requested==='How it works'){location.replace('/#how-it-works');return;}setView(views.includes(requested)?requested:legacy[requested]||'Explore');setCampaignId(query.get('campaign')||'');}read();window.addEventListener('popstate',read);return()=>window.removeEventListener('popstate',read);},[]);
  function navigate(event:React.MouseEvent<HTMLAnchorElement>,next:string){if(event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;event.preventDefault();history.pushState(null,'',`/app/?view=${encodeURIComponent(next)}`);setView(next);setCampaignId('');window.scrollTo({top:0,behavior:'auto'});requestAnimationFrame(()=>document.getElementById('app-content')?.focus({preventScroll:true}));}
  return <div className="protocol-site p-app"><a className="p-skip" href="#app-content">Skip to content</a><SiteHeader compact wallet={<WalletControl/>} network={<span className={'p-network '+(wallet.snapshot?'p-network-ready':'')}><span className="p-live-dot"/>NEAR TESTNET</span>}/>
    <nav className="p-app-nav p-container" aria-label="App navigation">{views.map(item=><a key={item} href={`/app/?view=${encodeURIComponent(item)}`} aria-current={view===item?'page':undefined} onClick={event=>navigate(event,item)}>{item}</a>)}<button className="p-text-button p-refresh" disabled={wallet.loading||wallet.busy} onClick={()=>void wallet.refresh()}>{wallet.loading?'Reading chain…':'Refresh state'}</button></nav>
    <main id="app-content" className="p-container p-app-main" tabIndex={-1}><WalletStatus/>{view==='Explore'?<Explore/>:view==='Funding'?<Funding campaignId={campaignId}/>:view==='My activity'?<Activity/>:view==='Studio'?<CreatorStudio snapshot={wallet.snapshot} onRefresh={()=>void wallet.refresh()}/>:<Stewardship/>}</main>
    <SiteFooter network={<a href={`https://explorer.testnet.near.org/accounts/${DEPLOYMENT.contract}`} target="_blank" rel="noreferrer">NEAR testnet · {wallet.snapshot?`block ${wallet.snapshot.height}`:'network connection pending'} ↗</a>}/>
  </div>;
}
export default function App(){return <WalletProvider><LiveApp/></WalletProvider>;}
