import {prepareLiveAction,createIntent,validateIntent,verifyIntentOutcome,readTransaction,loadLiveSnapshot,withdrawalState,transactionHash} from './live.mjs';

export const pendingStorageKey=signer=>`sunset-pending-v1:${signer}`;
export function transactionHashFromUrl(value){
  let url;try{url=new URL(value);}catch{return undefined;}
  const hashes=['transactionHashes','transactionHash','transaction_hash'].flatMap(key=>url.searchParams.getAll(key)).flatMap(value=>value.split(','));
  return hashes.length===1&&transactionHash(hashes[0])?hashes[0]:undefined;
}
export function loadPendingIntent(storage,signer){
  const raw=storage.getItem(pendingStorageKey(signer));
  if(raw===null)return null;
  if(typeof raw!=='string'||raw.length>4096)throw Error('Saved transaction reference needs recovery. Check your wallet activity.');
  let intent;try{intent=validateIntent(JSON.parse(raw));}catch{throw Error('Saved transaction reference needs recovery. Keep a copy and check your wallet activity.');}
  if(intent.signer!==signer)throw Error('Saved transaction reference belongs to a different account.');
  return intent;
}
function writePending(storage,intent,previous){
  const key=pendingStorageKey(intent.signer),raw=JSON.stringify(intent);
  if(storage.getItem(key)!==previous)throw Error('Another pending wallet request was recorded. Check its status first.');
  try{storage.setItem(key,raw);if(storage.getItem(key)!==raw)throw Error('not retained');}
  catch{throw Error('Allow browser storage to track this wallet request safely. Reading resources does not require storage.');}
  return raw;
}
function clearPending(storage,signer,previous){
  if(storage.getItem(pendingStorageKey(signer))!==previous)throw Error('Transaction tracking changed in another tab. Refresh its status.');
  storage.removeItem(pendingStorageKey(signer));
}
async function checkAccount(wallet,signer,isCurrent){
  const changed=()=>Object.assign(Error('Wallet account changed. Please reconnect before continuing.'),{code:'SUNSET_WALLET_CHANGED'});
  if(!isCurrent())throw changed();
  const accounts=await wallet.getAccounts({network:'testnet'});
  if(!isCurrent()||!Array.isArray(accounts)||!accounts.some(a=>a.accountId===signer))throw changed();
}

/** @param {{wallet:any,signer:string,method:string,args:any,key?:string,storage:any,isCurrent:()=>boolean,onIntent?:(value:any)=>void}} options */
export async function sendWalletAction({wallet,signer,method,args,key,storage,isCurrent,onIntent=()=>{}}){
  if(loadPendingIntent(storage,signer))throw Error('An existing wallet request is pending. Check it before sending another.');
  await checkAccount(wallet,signer,isCurrent);
  const {plan,snapshot}=await prepareLiveAction(method,args,signer,key);
  await checkAccount(wallet,signer,isCurrent);
  const intent=await createIntent(plan,snapshot);
  if(!isCurrent())throw Error('Wallet account changed. Please try again with the current account.');
  const original=writePending(storage,intent,null);onIntent(intent);
  let result;
  try{
    result=await wallet.signAndSendTransaction({network:'testnet',signerId:signer,receiverId:plan.receiverId,actions:plan.actions});
  }catch(error){
    if(error?.code===4001||error?.name==='UserRejectedRequestError'){
      clearPending(storage,signer,original);onIntent(null);return {status:'cancelled',intent};
    }
    throw Error('The wallet request was interrupted. Check your wallet activity before sending again.');
  }
  const hash=result?.transaction?.hash;
  if(!transactionHash(hash))return {status:'pending',intent};
  const submitted={...intent,hash};writePending(storage,submitted,original);onIntent(submitted);
  return checkWalletIntent({storage,signer});
}

/** @param {{storage:any,signer:string,hash?:string}} options */
export async function checkWalletIntent({storage,signer,hash}){
  const intent=loadPendingIntent(storage,signer);
  if(!intent)throw Error('There is no pending wallet request for this account.');
  const previous=storage.getItem(pendingStorageKey(signer)),reference=hash||intent.hash;
  if(!transactionHash(reference))throw Error('Your wallet has not returned a transaction hash. Check wallet activity, then paste its hash here.');
  if(intent.hash&&reference!==intent.hash)throw Error('This hash differs from the submitted request. Check the original transaction status.');
  const outcome=await readTransaction(reference,signer),status=await verifyIntentOutcome(outcome,intent);
  const submitted={...intent,hash:reference};
  if(status==='pending'){
    if(!intent.hash)writePending(storage,submitted,previous);
    return {status,intent:submitted};
  }
  const snapshot=await loadLiveSnapshot(signer);
  const payout=intent.method==='withdraw'?withdrawalState(intent,snapshot.account):undefined;
  if(payout==='pending'){
    if(!intent.hash)writePending(storage,submitted,previous);
    return {status:'pending',intent:submitted,snapshot,payout};
  }
  clearPending(storage,signer,previous);
  return {status,intent:submitted,snapshot,payout};
}

/** Explicit user recovery only; a known submitted hash can never be silently discarded. */
export function forgetUnsubmittedIntent(storage,signer,{confirmed=false}={}){
  let intent;
  try{intent=loadPendingIntent(storage,signer);}catch(error){if(!confirmed)throw error;}
  if(intent?.hash)throw Error('A transaction hash was submitted. Check its status before clearing the request.');
  if(!confirmed)throw Error('Check wallet activity and explicitly confirm that no transaction was submitted.');
  storage.removeItem(pendingStorageKey(signer));
}
