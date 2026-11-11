import {RPC,ACCOUNT_STORAGE,CAMPAIGN_STORAGE,isCampaignCatalog} from './chain.mjs';
import {buildTransactionPlan,verifyPlannedOutcome} from './plans.mjs';
import {fetchVerifiedMirror} from './mirror.mjs';
import {hashBytes} from './pack.mjs';
import {validateMirrorUri} from './stewardship.mjs';

export const DEPLOYMENT=Object.freeze({network:'testnet',contract:'sunset.shiftultra.testnet',
  codeHash:'9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx',owner:'shiftultra.testnet'});
const encoder=new TextEncoder(),decoder=new TextDecoder('utf-8',{fatal:true});
const methods=new Set(['create_campaign','approve_campaign','contribute','publish_release','claim_refund','withdraw','nft_transfer','nft_transfer_call','set_mirror']);
let requestId=0;
function requireValue(value,message){if(!value)throw Error(message);}
function accountId(value){return typeof value==='string'&&value.length>=2&&value.length<=64&&/^[a-z0-9]+(?:[-_.][a-z0-9]+)*$/.test(value);}
function uint(value,bits=128){requireValue(typeof value==='string'&&/^(0|[1-9]\d*)$/.test(value)&&value.length<=39,'Invalid onchain amount or timestamp');const n=BigInt(value);requireValue(n<2n**BigInt(bits),'Onchain value exceeds its integer limit');return n;}
function hash(value){return typeof value==='string'&&/^[a-f0-9]{64}$/.test(value);}
export function transactionHash(value){return typeof value==='string'&&/^[1-9A-HJ-NP-Za-km-z]{43,44}$/.test(value);}

async function rpc(method,params){
  const id=`sunset-${++requestId}`;
  const response=await fetch(RPC,{method:'POST',credentials:'omit',redirect:'error',headers:{'content-type':'application/json'},
    body:JSON.stringify({jsonrpc:'2.0',id,method,params}),signal:AbortSignal.timeout(15000)});
  requireValue(response.ok,'Live NEAR data is temporarily unavailable. Please retry.');
  const text=await response.text();requireValue(text.length<=2*1024*1024,'RPC response exceeds the supported size');
  const result=JSON.parse(text);
  requireValue(result.jsonrpc==='2.0'&&result.id===id&&!result.error&&result.result!==undefined,'NEAR could not confirm this request. Check again before sending another transaction.');
  return result.result;
}
async function view(method,args,blockHash,height){
  const bytes=encoder.encode(JSON.stringify(args));
  const args_base64=btoa(Array.from(bytes,b=>String.fromCharCode(b)).join(''));
  const result=await rpc('query',{request_type:'call_function',block_id:blockHash,account_id:DEPLOYMENT.contract,method_name:method,args_base64});
  requireValue(result.block_hash===blockHash&&result.block_height===height,'NEAR returned data from a different block. Please refresh.');
  requireValue(Array.isArray(result.result)&&result.result.length<=65536&&result.result.every(n=>Number.isInteger(n)&&n>=0&&n<=255),'Invalid onchain response');
  return JSON.parse(decoder.decode(Uint8Array.from(result.result)));
}
function validateAccount(value,signer){
  requireValue(value?.schema_version===1&&value.account_id===signer&&accountId(signer)&&typeof value.registered==='boolean','Connected account differs from the live account view');
  uint(value.credit);uint(value.paid);
  requireValue(value.pending===null||(value.pending&&uint(value.pending.amount)>0n&&uint(value.pending.operation_id,64)>0n),'Invalid pending withdrawal');
  requireValue(Array.isArray(value.contributions)&&value.contributions.length<=5,'Invalid contribution records');
  const ids=new Set();
  for(const c of value.contributions){requireValue(c&&typeof c.campaign_id==='string'&&!ids.has(c.campaign_id)&&typeof c.refunded==='boolean','Invalid contribution record');uint(c.amount);ids.add(c.campaign_id);}
  if(!value.registered)requireValue(value.credit==='0'&&value.paid==='0'&&value.pending===null&&value.contributions.length===0,'Unregistered account contains financial state');
  return value;
}
function validateSnapshot(s){
  requireValue(s?.network===DEPLOYMENT.network&&s.contract===DEPLOYMENT.contract&&s.codeHash===DEPLOYMENT.codeHash,'The live deployment differs from the reviewed SUNSET contract');
  requireValue(typeof s.blockHash==='string'&&Number.isSafeInteger(s.height)&&s.height>0,'Missing finalized block identity');
  uint(s.timestampNs,64);
  const c=s.config;
  requireValue(c?.schema_version===1&&c.state_layout_version===2&&c.network==='testnet'&&c.contract_id===DEPLOYMENT.contract&&c.owner===DEPLOYMENT.owner&&c.max_campaigns===5&&c.max_accounts===100&&c.account_storage_allowance===ACCOUNT_STORAGE&&c.campaign_storage_allowance===CAMPAIGN_STORAGE,'Unsupported live contract configuration');
  requireValue(Number.isInteger(c.account_count)&&c.account_count>=0&&c.account_count<=100&&Number.isInteger(c.campaign_count)&&c.campaign_count>=0&&c.campaign_count<=5,'Invalid contract capacity');
  requireValue(isCampaignCatalog(s.campaigns)&&s.campaigns.length===c.campaign_count,'Invalid live resource catalog');
  const ids=new Set();
  for(const campaign of s.campaigns){
    requireValue(!ids.has(campaign.id)&&accountId(campaign.creator)&&accountId(campaign.reviewer)&&hash(campaign.agreement_digest),'Invalid live campaign identity');ids.add(campaign.id);
    requireValue(uint(campaign.target)>0n&&uint(campaign.total_contributed)<=uint(campaign.target)&&uint(campaign.escrow)<=uint(campaign.total_contributed),'Invalid campaign accounting');
    for(const k of ['funding_deadline_ns','release_window_ns','funded_at_ns'])uint(campaign[k],64);
    if(campaign.release_deadline_ns!==null)uint(campaign.release_deadline_ns,64);
    validateMirrorUri(campaign.manifest_uri);
    if(campaign.stewardship){requireValue(accountId(campaign.stewardship.owner_id),'Invalid steward account');validateMirrorUri(campaign.stewardship.mirror_uri);}
  }
  if(s.account!==null)validateAccount(s.account,s.account?.account_id);
  return s;
}

/** All financial inputs are read at the same finalized block, including the code identity. */
export async function loadLiveSnapshot(signer){
  if(signer!==undefined&&signer!==null)requireValue(accountId(signer),'Invalid connected account');
  requireValue((await rpc('status',[])).chain_id==='testnet','Wallet actions require NEAR testnet');
  const code=await rpc('query',{request_type:'view_account',finality:'final',account_id:DEPLOYMENT.contract});
  requireValue(code.code_hash===DEPLOYMENT.codeHash,'SUNSET’s deployed code has changed. Signing is unavailable until it is reviewed.');
  requireValue(typeof code.block_hash==='string'&&Number.isSafeInteger(code.block_height),'Missing finalized deployment block');
  const block=code.block_hash,height=code.block_height;
  const [header,config,campaigns,account]=await Promise.all([
    rpc('block',{block_id:block}),view('get_config',{},block,height),view('list_campaigns',{},block,height),
    signer?view('get_account',{account_id:signer},block,height):Promise.resolve(null)
  ]);
  requireValue(header.header?.hash===block&&header.header?.height===height,'NEAR returned a different timestamp block');
  return validateSnapshot({...DEPLOYMENT,blockHash:block,height,timestampNs:header.header.timestamp_nanosec,config,campaigns,account});
}

/** Eligibility is independent of UI visibility; the contract remains the final authority. */
export function buildLivePlan(snapshot,signer,method,args){
  const s=validateSnapshot(snapshot);
  requireValue(accountId(signer)&&s.account?.account_id===signer,'Wallet account changed. Refresh before continuing.');
  validateAccount(s.account,signer);
  const plan=buildTransactionPlan(DEPLOYMENT.contract,method,args,{registered:s.account.registered,signer});
  const now=uint(s.timestampNs,64),c=s.campaigns.find(c=>c.id===(args.id??args.token_id));
  if(method==='create_campaign'){
    requireValue(signer===s.config.owner,'Publishing is curated: connect the configured creator account.');
    requireValue(s.config.campaign_count<s.config.max_campaigns,'This testnet deployment has no campaign slots remaining.');
    requireValue(!s.campaigns.some(c=>c.id===args.id),'That resource ID already exists onchain.');
    requireValue(args.reviewer!==signer,'Choose a reviewer with a different account.');
    requireValue(uint(args.funding_deadline_ns,64)>now,'Choose a future funding deadline.');
  }else if(method==='withdraw'){
    requireValue(!s.account.pending,'A withdrawal is already pending. Check its status before trying again.');
    requireValue(uint(args.amount)>0n&&uint(args.amount)<=uint(s.account.credit),'Withdrawal exceeds your available credit.');
  }else{
    requireValue(c,'This campaign is not in the live catalog.');
    if(method==='contribute')requireValue(c.state==='Active'&&now<uint(c.funding_deadline_ns,64),'This campaign is not accepting sponsorship.');
    if(method==='approve_campaign'){
      requireValue(c.state==='Draft'&&now<uint(c.funding_deadline_ns,64),'This agreement is no longer awaiting review.');
      requireValue(c.reviewer===signer,'Only this resource’s named reviewer can approve it.');
      requireValue(args.agreement_digest===c.agreement_digest,'The agreement changed. Reload and review its exact content.');
    }
    if(method==='publish_release')requireValue(c.state==='Funded'&&c.release_deadline_ns!==null&&now<uint(c.release_deadline_ns,64),'The resource is not funded or its release window has ended.');
    if(method==='claim_refund'){
      const contribution=s.account.contributions.find(x=>x.campaign_id===c.id);
      requireValue(c.state==='Refundable'&&contribution&&!contribution.refunded&&uint(contribution.amount)>0n,'There is no unclaimed contribution refund for this account.');
    }
    if(['nft_transfer','nft_transfer_call','set_mirror'].includes(method)){
      requireValue(c.state==='Released'&&c.stewardship?.owner_id===signer,'Only the current steward can change this resource’s stewardship.');
      if(method!=='set_mirror')requireValue(args.receiver_id!==signer,'Choose a different receiving account.');
    }
  }
  if(['contribute','create_campaign'].includes(method)&&!s.account.registered)requireValue(s.config.account_count<s.config.max_accounts,'The testnet participant limit has been reached.');
  return plan;
}

export function resourceCommitments(c,key=c.public_key_base64){return {
  packId:c.id,manifestHash:c.manifest_hash,plaintextHash:c.plaintext_hash,ciphertextHash:c.ciphertext_hash,
  keyCommitment:c.key_commitment,licenseHash:c.license_hash,publicKey:key
};}
/** Re-check immediately before wallet approval; never expose an unverified private key to signing. */
export async function prepareLiveAction(method,args,signer,key){
  const snapshot=await loadLiveSnapshot(signer),plan=buildLivePlan(snapshot,signer,method,args);
  if(['create_campaign','approve_campaign','publish_release','set_mirror'].includes(method)){
    const c=method==='create_campaign'?args:snapshot.campaigns.find(c=>c.id===(args.id??args.token_id));
    const contentKey=method==='publish_release'?args.key_base64:method==='set_mirror'?c.public_key_base64:key;
    requireValue(typeof contentKey==='string'&&contentKey.length>0,'Restore the matching private content backup to inspect this resource.');
    await fetchVerifiedMirror(method==='set_mirror'?args.mirror_uri:c.manifest_uri,resourceCommitments(c,contentKey));
  }
  return {plan,snapshot};
}
function canonical(value){if(Array.isArray(value))return value.map(canonical);if(value&&typeof value==='object')return Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])]));return value;}
const argumentHash=args=>hashBytes(encoder.encode(JSON.stringify(canonical(args))));

/** Persist this reference before opening the wallet; the content key and raw args never enter it. */
export async function createIntent(plan,snapshot){
  requireValue(plan?.network==='testnet'&&plan.receiverId===DEPLOYMENT.contract&&plan.actions?.length===1,'Unexpected signing plan');
  const action=plan.actions[0].params;
  const checked=buildLivePlan(snapshot,plan.expectedSignerId,action.methodName,action.args);
  requireValue(JSON.stringify(canonical(checked.actions))===JSON.stringify(canonical(plan.actions)),'Signing plan changed after preflight');
  return {schema:1,signer:plan.expectedSignerId,receiverId:plan.receiverId,method:action.methodName,gas:action.gas,deposit:action.deposit,
    argsHash:await argumentHash(action.args),resourceId:action.args.id??action.args.token_id??null,startedAt:Date.now(),
    ...(action.methodName==='withdraw'?{withdrawAmount:action.args.amount,paidBefore:snapshot.account.paid,creditBefore:snapshot.account.credit}:{})};
}
export function validateIntent(intent){
  requireValue(intent?.schema===1&&accountId(intent.signer)&&intent.receiverId===DEPLOYMENT.contract&&methods.has(intent.method)&&hash(intent.argsHash)&&Number.isSafeInteger(intent.startedAt)&&intent.startedAt>0,'Saved transaction reference is invalid. Inspect wallet activity before sending again.');
  uint(intent.gas,64);uint(intent.deposit);
  if(intent.hash!==undefined)requireValue(transactionHash(intent.hash),'Invalid transaction hash');
  if(intent.method==='withdraw'){requireValue(uint(intent.withdrawAmount)>0n,'Invalid withdrawal reference');uint(intent.paidBefore);uint(intent.creditBefore);}
  return intent;
}
export async function verifyIntentOutcome(outcome,intent){
  validateIntent(intent);
  if(!outcome?.transaction)return 'pending';
  const tx=outcome.transaction;
  requireValue(tx.signer_id===intent.signer&&tx.receiver_id===intent.receiverId&&Array.isArray(tx.actions)&&tx.actions.length===1,'Transaction does not match the connected signer and SUNSET contract.');
  const action=tx.actions[0]?.FunctionCall;
  requireValue(action&&action.method_name===intent.method&&String(action.gas)===intent.gas&&String(action.deposit)===intent.deposit,'Transaction method, gas or deposit differs from the wallet request.');
  requireValue(typeof action.args==='string'&&action.args.length<=131072,'Invalid transaction arguments');
  const args=JSON.parse(decoder.decode(Uint8Array.from(atob(action.args),c=>c.charCodeAt(0))));
  requireValue(await argumentHash(args)===intent.argsHash,'Transaction arguments differ from the wallet request.');
  if(outcome.final_execution_status!=='FINAL')return 'pending';
  const plan={receiverId:intent.receiverId,expectedSignerId:intent.signer,actions:[{type:'FunctionCall',params:{methodName:intent.method,args,gas:intent.gas,deposit:intent.deposit}}]};
  return verifyPlannedOutcome(outcome,plan,intent.signer);
}
export async function readTransaction(hash,signer){
  requireValue(transactionHash(hash)&&accountId(signer),'Use a real NEAR transaction hash and signing account.');
  const result=await rpc('tx',{tx_hash:hash,sender_account_id:signer,wait_until:'FINAL'});
  requireValue(!result.transaction||result.transaction.hash===hash,'RPC returned a different transaction hash.');
  return result;
}
/** Call after the matching finalized receipt; credited funds are never presented as native payout. */
export function withdrawalState(intent,account){
  validateIntent(intent);requireValue(intent.method==='withdraw','Not a withdrawal request');validateAccount(account,intent.signer);
  if(account.pending)return 'pending';
  if(uint(account.paid)>=uint(intent.paidBefore)+uint(intent.withdrawAmount))return 'paid';
  if(uint(account.credit)>=uint(intent.creditBefore))return 'restored';
  return 'pending';
}
