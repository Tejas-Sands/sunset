'use client';
import {createContext,useContext,useEffect,useRef,useState} from 'react';
import type {NearConnector,NearWalletBase,EventMap} from '@hot-labs/near-connect';
import {DEPLOYMENT,loadLiveSnapshot} from '../lib/live.mjs';
import {sendWalletAction,checkWalletIntent,loadPendingIntent,forgetUnsubmittedIntent,pendingStorageKey,transactionHashFromUrl} from '../lib/wallet.mjs';
import {download} from '../lib/download.mjs';
import {createWalletMetadataStorage} from '../lib/wallet-storage.mjs';
import {Icon} from './Protocol';

let connectorPromise:Promise<NearConnector>|null=null;
async function getConnector(){
  if(!connectorPromise)connectorPromise=import('@hot-labs/near-connect').then(({NearConnector})=>new NearConnector({
    network:'testnet',autoConnect:false,features:{testnet:true,signAndSendTransaction:true,signInWithoutAddKey:true},
    excludedWallets:['mynearwallet','my-near-wallet'],footerBranding:null,
    storage:createWalletMetadataStorage(()=>window.localStorage)
  })).catch(error=>{connectorPromise=null;throw error;});
  return connectorPromise;
}
function browserStorage(){try{return window.localStorage;}catch{throw Error('Allow browser storage to track wallet transactions. Resources remain available without it.');}}
type WalletValue={accountId:string,connecting:boolean,busy:boolean,loading:boolean,snapshot:any,pending:any,receipt:any,pendingDamaged:boolean,message:string,error:string,
  connect:()=>Promise<any>,disconnect:()=>Promise<void>,refresh:()=>Promise<any>,submit:(method:string,args:object,key?:string)=>Promise<any>,
  checkPending:(hash?:string)=>Promise<void>,forgetPending:()=>void,savePending:()=>void};
const Context=createContext<WalletValue|null>(null);
export function useWallet(){const value=useContext(Context);if(!value)throw Error('WalletProvider is required');return value;}

export default function WalletProvider({children}:{children:React.ReactNode}){
  const [accountId,setAccountId]=useState(''),[connecting,setConnecting]=useState(false),[busy,setBusy]=useState(false),[loading,setLoading]=useState(true);
  const [snapshot,setSnapshot]=useState<any>(null),[pending,setPending]=useState<any>(null),[receipt,setReceipt]=useState<any>(null),[pendingDamaged,setPendingDamaged]=useState(false),[message,setMessage]=useState(''),[error,setError]=useState('');
  const current=useRef(''),walletRef=useRef<NearWalletBase|null>(null),generation=useRef(0),working=useRef(false),alive=useRef(true);
  function readPending(id:string){
    if(!alive.current)return;
    try{setPending(id?loadPendingIntent(browserStorage(),id):null);setPendingDamaged(false);}
    catch(e){setPending(null);setPendingDamaged(true);setError((e as Error).message);}
  }
  async function refresh(){
    const id=current.current,token=++generation.current;
    setLoading(true);setSnapshot((previous:any)=>previous?{...previous,account:null}:null);
    try{const result=await loadLiveSnapshot(id||undefined);if(alive.current&&token===generation.current&&id===current.current){setSnapshot(result);setError('');if(id)readPending(id);return result;}}
    catch(e){if(alive.current&&token===generation.current){setSnapshot(null);setError((e as Error).message);}}
    finally{if(alive.current&&token===generation.current)setLoading(false);}
    return null;
  }
  function select(wallet:NearWalletBase|null,id:string){
    walletRef.current=wallet;
    if(id===current.current){readPending(id);return;}
    current.current=id;setAccountId(id);setMessage('');setError('');setReceipt(null);readPending(id);void refresh();
  }
  async function syncConnection(resume=false){
    if(working.current)return;
    try{const connected=await (await getConnector()).getConnectedWallet();if(alive.current){const id=connected.accounts[0]?.accountId||'';select(connected.wallet,id);
      if(resume&&id){try{const pending=loadPendingIntent(browserStorage(),id),hash=transactionHashFromUrl(window.location.href)||pending?.hash;if(pending&&hash)void checkPending(hash);}catch(e){setError((e as Error).message);}}
    }}
    catch{if(alive.current&&current.current)select(null,'');}
  }
  useEffect(()=>{
    alive.current=true;void refresh();
    let connector:NearConnector|undefined,cancelled=false;
    const signedIn=(event:EventMap['wallet:signIn'])=>{if(alive.current&&event.success)select(event.wallet,event.accounts[0]?.accountId||'');};
    const signedOut=()=>{if(alive.current)select(null,'');};
    void getConnector().then(value=>{if(cancelled||!alive.current)return;connector=value;value.on('wallet:signIn',signedIn);value.on('wallet:signOut',signedOut);void syncConnection(true);}).catch(()=>{});
    const focus=()=>{void syncConnection();};
    const storage=(event:StorageEvent)=>{if(event.key===pendingStorageKey(current.current))readPending(current.current);else if(event.key?.includes('selected-wallet'))void syncConnection();};
    window.addEventListener('focus',focus);window.addEventListener('storage',storage);
    return()=>{cancelled=true;alive.current=false;generation.current++;connector?.off('wallet:signIn',signedIn);connector?.off('wallet:signOut',signedOut);window.removeEventListener('focus',focus);window.removeEventListener('storage',storage);};
  },[]);
  async function connect(){
    if(working.current)return null;
    setConnecting(true);setError('');setMessage('');
    try{const connector=await getConnector(),wallet=await connector.connect();const accounts=await wallet.getAccounts({network:'testnet'}),id=accounts[0]?.accountId;
      if(!id)throw Error('The wallet did not share a testnet account.');select(wallet,id);return {wallet,accountId:id};
    }catch(e){if(/cancel|reject|closed/i.test((e as Error).message))setMessage('Wallet connection cancelled.');else setError((e as Error).message);return null;}
    finally{if(alive.current)setConnecting(false);}
  }
  async function disconnect(){
    if(working.current)return;
    setConnecting(true);setError('');
    try{const connector=await getConnector();await connector.disconnect(walletRef.current||undefined);select(null,'');}
    catch(e){setError((e as Error).message);}finally{if(alive.current)setConnecting(false);}
  }
  function report(result:any,id:string){
    if(!alive.current||id!==current.current)return;
    readPending(id);
    setReceipt(result.intent?.hash?{hash:result.intent.hash,status:result.status}:null);
    if(result.snapshot?.account?.account_id===id){setSnapshot(result.snapshot);setLoading(false);}
    const messages:Record<string,string>={contribute:'Sponsorship confirmed onchain.',approve_campaign:'Review approved onchain. This campaign can now receive sponsorship.',
      create_campaign:'Campaign created. Its named reviewer can now inspect and approve it.',publish_release:'Resource released. Creator credit is available to withdraw.',
      claim_refund:'Refund credited onchain. Withdraw your available balance from My activity.',withdraw:result.payout==='paid'?'Native payout confirmed.':result.payout==='restored'?'The transfer did not complete. Your credit was restored.':'Withdrawal recorded; checking settlement.',
      nft_transfer:'Stewardship transferred.',nft_transfer_call:'Stewardship transfer accepted.',set_mirror:'Recovery mirror updated onchain.'};
    setMessage(result.status==='cancelled'?'Wallet request cancelled.':result.status==='pending'?'Waiting for a confirmed transaction result. Check wallet activity before sending another request.':result.status==='failure'?'The transaction failed. Review the updated onchain balance and its receipt.':result.status==='returned'?'The receiving contract returned the stewardship token.':messages[result.intent.method]||'Transaction confirmed.');
  }
  async function submit(method:string,args:object,key?:string){
    if(working.current)return null;
    const connection=walletRef.current&&current.current?{wallet:walletRef.current,accountId:current.current}:await connect();
    if(!connection)return null;
    const id=connection.accountId;working.current=true;setBusy(true);setError('');setMessage('Preparing your wallet request…');
    try{const result=await sendWalletAction({wallet:connection.wallet,signer:id,method,args,key,storage:browserStorage(),
      isCurrent:()=>alive.current&&current.current===id,onIntent:value=>{if(alive.current&&current.current===id){setPending(value);if(value)setMessage(value.hash?'Waiting for NEAR confirmation…':'Confirm this request in your wallet.');}}});report(result,id);return result;
    }catch(e){if(alive.current&&current.current===id){if((e as Error&{code?:string}).code==='SUNSET_WALLET_CHANGED')select(null,'');else readPending(id);setMessage('');setError((e as Error).message);}return null;}
    finally{working.current=false;if(alive.current){setBusy(false);void syncConnection();}}
  }
  async function checkPending(hash?:string){
    const id=current.current;if(!id||working.current)return;
    working.current=true;setBusy(true);setError('');
    try{const result=await checkWalletIntent({storage:browserStorage(),signer:id,hash});report(result,id);
      if(transactionHashFromUrl(window.location.href)===result.intent.hash){const url=new URL(window.location.href);for(const key of ['transactionHashes','transactionHash','transaction_hash'])url.searchParams.delete(key);window.history.replaceState(null,'',url.href);}
    }
    catch(e){if(alive.current&&current.current===id){readPending(id);setError((e as Error).message);}}
    finally{working.current=false;if(alive.current){setBusy(false);void syncConnection();}}
  }
  function forgetPending(){
    if(!current.current||working.current||!window.confirm('First inspect your wallet activity. Clear this local reference only if no transaction was submitted. A confirmed payment cannot be undone here.'))return;
    try{forgetUnsubmittedIntent(browserStorage(),current.current,{confirmed:true});readPending(current.current);setError('');setMessage('Unsubmitted local request cleared.');}catch(e){setError((e as Error).message);}
  }
  function savePending(){try{const raw=browserStorage().getItem(pendingStorageKey(current.current));if(raw)download('sunset-transaction-reference.json',raw);}catch(e){setError((e as Error).message);}}
  return <Context.Provider value={{accountId,connecting,busy,loading,snapshot,pending,receipt,pendingDamaged,message,error,connect,disconnect,refresh,submit,checkPending,forgetPending,savePending}}>{children}</Context.Provider>;
}

export function WalletControl(){
  const wallet=useWallet(),menu=useRef<HTMLDetailsElement>(null);
  useEffect(()=>{
    const close=(event:Event)=>{const node=menu.current;if(node?.open&&(event.type==='keydown'?(event as KeyboardEvent).key==='Escape':!node.contains(event.target as Node)))node.open=false;};
    document.addEventListener('pointerdown',close);document.addEventListener('keydown',close);
    return()=>{document.removeEventListener('pointerdown',close);document.removeEventListener('keydown',close);};
  },[]);
  if(!wallet.accountId)return <button className="p-button p-button-accent wallet-connect" disabled={wallet.connecting||wallet.busy} onClick={()=>void wallet.connect()}>{wallet.connecting?'Opening wallet…':'Connect wallet'}</button>;
  return <details className="wallet-menu" ref={menu}><summary className="p-button wallet-account" aria-label={`Wallet ${wallet.accountId}`}><span className="p-live-dot"/><span>{wallet.accountId}</span><Icon name="chevron" size={16}/></summary>
    <div><span className="p-menu-label">Connected on NEAR testnet</span><strong>{wallet.accountId}</strong><button disabled={wallet.busy||wallet.connecting} onClick={event=>{event.currentTarget.closest('details')?.removeAttribute('open');void wallet.connect();}}>Change wallet</button><button disabled={wallet.busy||wallet.connecting} onClick={()=>void wallet.disconnect()}>Disconnect</button></div></details>;
}
export function WalletStatus(){
  const wallet=useWallet(),[hash,setHash]=useState('');
  useEffect(()=>setHash(wallet.pending?.hash||''),[wallet.pending?.hash,wallet.accountId]);
  return <>{wallet.error&&<div className="p-notice p-notice-error" role="alert"><Icon name="alert"/><span>{wallet.error}</span></div>}{wallet.message&&<div className={'p-notice'+(wallet.receipt&&!wallet.pending?' p-notice-success':'')} role="status">{wallet.busy?<span className="p-spinner"/>:<Icon name={wallet.receipt&&!wallet.pending?'check':'info'}/>}<span>{wallet.message}{wallet.receipt&&!wallet.pending&&<a href={`https://explorer.testnet.near.org/transactions/${wallet.receipt.hash}`} target="_blank" rel="noreferrer"> View receipt</a>}</span></div>}
    {(wallet.pending||wallet.pendingDamaged)&&<section className="p-panel p-transaction" aria-label="Pending wallet request"><div><h2>{wallet.pendingDamaged?'Wallet request tracking needs attention':'Track your transaction'}</h2><p>{wallet.pendingDamaged?'Allow browser storage, or keep and inspect any existing reference, before sending a new request.':'Keep this request until its result is clear. Checking a transaction is read-only.'}</p></div>
      {!wallet.pendingDamaged&&<div className="p-inline-form"><label>Transaction hash<input value={hash} onChange={e=>setHash(e.target.value)} placeholder="Copy it from your wallet activity" spellCheck={false} autoComplete="off" disabled={wallet.busy||!!wallet.pending?.hash}/></label><button className="p-button p-button-accent" disabled={wallet.busy||!hash} onClick={()=>void wallet.checkPending(hash)}>{wallet.busy?'Checking…':'Check status'}</button>{wallet.pending?.hash&&<a className="p-button" href={`https://explorer.testnet.near.org/transactions/${wallet.pending.hash}`} target="_blank" rel="noreferrer">View receipt<Icon name="external" size={16}/></a>}</div>}
      <div className="p-actions"><button className="p-text-button" onClick={wallet.savePending}><Icon name="download"/>Save transaction reference</button>{!wallet.pending?.hash&&<button className="p-text-button" disabled={wallet.busy} onClick={wallet.forgetPending}>I checked: no transaction was sent</button>}</div>
    </section>}</>;
}
