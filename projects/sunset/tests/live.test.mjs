import {test} from 'node:test';
import assert from 'node:assert/strict';
import * as live from '../src/lib/live.mjs';
import {prepareArtifact,base64ToBytes} from '../src/lib/demo.mjs';
import {introPack,hashBytes} from '../src/lib/pack.mjs';

const contract='sunset.shiftultra.testnet',signer='sponsor.testnet',blockHash='H'.repeat(44);
const hashes={manifest_hash:'a'.repeat(64),plaintext_hash:'b'.repeat(64),ciphertext_hash:'c'.repeat(64),key_commitment:'d'.repeat(64),license_hash:'e'.repeat(64)};
function snapshot(state='Active',registered=true){return {
 contract,network:'testnet',codeHash:'9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx',blockHash,height:50,timestampNs:'100000000000',
 config:{schema_version:1,state_layout_version:2,network:'testnet',contract_id:contract,owner:'shiftultra.testnet',max_campaigns:5,max_accounts:100,campaign_count:1,account_count:3,account_storage_allowance:'10000000000000000000000',campaign_storage_allowance:'50000000000000000000000'},
 campaigns:[{schema_version:1,id:'resource',title:'Resource',creator:'shiftultra.testnet',reviewer:'reviewer.testnet',manifest_uri:'https://content.example/manifest.json',...hashes,target:'500000000000000000000000',total_contributed:'200000000000000000000000',escrow:'200000000000000000000000',funding_deadline_ns:'200000000000',release_window_ns:'50000000000',funded_at_ns:'0',release_deadline_ns:null,agreement_digest:'f'.repeat(64),state,public_key_base64:null,stewardship:null}],
 account:{schema_version:1,account_id:signer,registered,credit:registered?'400000000000000000000000':'0',paid:'0',pending:null,contributions:registered?[{campaign_id:'resource',amount:'200000000000000000000000',refunded:false}]:[]}
};}
function released(){const s=snapshot('Released');Object.assign(s.campaigns[0],{funded_at_ns:'50000000000',release_deadline_ns:'100000000000',public_key_base64:btoa('x'.repeat(32)),stewardship:{token_id:'resource',owner_id:signer,mirror_uri:'https://content.example/manifest.json'}});return s;}
function response(value){return new Response(JSON.stringify(value),{headers:{'content-type':'application/json'}});}
function rpcFixture(s,mutate=()=>{}){return async(url,options)=>{
 const q=JSON.parse(options.body);let result;
 if(q.method==='status')result={chain_id:'testnet'};
 else if(q.method==='block')result={header:{hash:blockHash,height:s.height,timestamp_nanosec:s.timestampNs}};
 else if(q.params.request_type==='view_account')result={block_hash:blockHash,block_height:s.height,code_hash:s.codeHash};
 else {assert.equal(q.params.block_id,blockHash);const value={get_config:s.config,list_campaigns:s.campaigns,get_account:s.account}[q.params.method_name];assert.notEqual(value,undefined);result={block_hash:blockHash,block_height:s.height,result:[...new TextEncoder().encode(JSON.stringify(value))]};}
 mutate(q,result);return response({jsonrpc:'2.0',id:q.id,result});
};}
async function withFetch(fetcher,work){const original=globalThis.fetch;globalThis.fetch=fetcher;try{return await work();}finally{globalThis.fetch=original;}}
function outcome(plan){const p=plan.actions[0].params;return {final_execution_status:'FINAL',transaction:{hash:'T'.repeat(44),signer_id:plan.expectedSignerId,receiver_id:plan.receiverId,actions:[{FunctionCall:{method_name:p.methodName,args:btoa(JSON.stringify(p.args)),gas:p.gas,deposit:p.deposit}}]},transaction_outcome:{outcome:{status:{SuccessReceiptId:'receipt'}}},status:{SuccessValue:''},receipts_outcome:[{outcome:{status:{SuccessValue:''}}}]};}

test('live snapshot binds network, reviewed code, configuration, time and account to one finalized block',async()=>{
 const s=snapshot();await withFetch(rpcFixture(s),async()=>{const result=await live.loadLiveSnapshot(signer);assert.equal(result.height,50);assert.equal(result.timestampNs,'100000000000');assert.equal(result.account.account_id,signer);assert.equal(result.campaigns[0].id,'resource');});
});
test('live snapshot rejects wrong chain, changed code, mixed blocks and malformed monetary views',async()=>{
 for(const mutate of [
  (q,r)=>{if(q.method==='status')r.chain_id='mainnet';},
  (q,r)=>{if(q.params?.request_type==='view_account')r.code_hash='1'.repeat(44);},
  (q,r)=>{if(q.params?.method_name==='get_account')r.block_hash='other';},
  (q,r)=>{if(q.params?.method_name==='get_account')r.result=[...new TextEncoder().encode(JSON.stringify({...snapshot().account,credit:'-1'}))];},
  (q,r)=>{if(q.params?.method_name==='get_config')r.result=[...new TextEncoder().encode(JSON.stringify({...snapshot().config,owner:'other.testnet'}))];}
 ])await withFetch(rpcFixture(snapshot(),mutate),async()=>{await assert.rejects(()=>live.loadLiveSnapshot(signer));});
});
test('new sponsors attach the exact economic amount and one-time storage allowance',()=>{
 assert.equal(live.buildLivePlan(snapshot('Active',false),signer,'contribute',{id:'resource',amount:'50000000000000000000000'}).actions[0].params.deposit,'60000000000000000000000');
 assert.equal(live.buildLivePlan(snapshot(),signer,'contribute',{id:'resource',amount:'50000000000000000000000'}).actions[0].params.deposit,'50000000000000000000000');
});
test('closed campaigns, exhausted account slots and stale signer views cannot reach a sponsorship plan',()=>{
 assert.throws(()=>live.buildLivePlan(snapshot('Released'),signer,'contribute',{id:'resource',amount:'1'}));
 const full=snapshot('Active',false);full.config.account_count=100;
 assert.throws(()=>live.buildLivePlan(full,signer,'contribute',{id:'resource',amount:'1'}));
 assert.throws(()=>live.buildLivePlan(snapshot(),'other.testnet','contribute',{id:'resource',amount:'1'}));
 const expired=snapshot();expired.timestampNs=expired.campaigns[0].funding_deadline_ns;
 assert.throws(()=>live.buildLivePlan(expired,signer,'contribute',{id:'resource',amount:'1'}));
 for(const amount of ['0','-1','1.2','1e24'])assert.throws(()=>live.buildLivePlan(snapshot(),signer,'contribute',{id:'resource',amount}));
});
test('refund plans require a real unrefunded contribution and withdrawals use credit with no pending operation',()=>{
 const s=snapshot('Refundable');s.timestampNs='200000000001';
 assert.equal(live.buildLivePlan(s,signer,'claim_refund',{id:'resource'}).actions[0].params.deposit,'0');
 s.account.contributions[0].refunded=true;assert.throws(()=>live.buildLivePlan(s,signer,'claim_refund',{id:'resource'}));
 assert.throws(()=>live.buildLivePlan(snapshot('Refundable',false),signer,'claim_refund',{id:'resource'}));
 assert.equal(live.buildLivePlan(s,signer,'withdraw',{amount:'1'}).actions[0].params.deposit,'0');
 assert.throws(()=>live.buildLivePlan(s,signer,'withdraw',{amount:'400000000000000000000001'}));
 s.account.pending={amount:'1',operation_id:'7'};assert.throws(()=>live.buildLivePlan(s,signer,'withdraw',{amount:'1'}));
});
test('review approval binds named reviewer and exact digest; release requires a live funded deadline',()=>{
 const s=snapshot('Draft');assert.throws(()=>live.buildLivePlan(s,signer,'approve_campaign',{id:'resource',agreement_digest:'f'.repeat(64)}));
 s.account.account_id='reviewer.testnet';
 assert.equal(live.buildLivePlan(s,'reviewer.testnet','approve_campaign',{id:'resource',agreement_digest:'f'.repeat(64)}).expectedSignerId,'reviewer.testnet');
 assert.throws(()=>live.buildLivePlan(s,'reviewer.testnet','approve_campaign',{id:'resource',agreement_digest:'a'.repeat(64)}));
 const funded=snapshot('Funded');Object.assign(funded.campaigns[0],{funded_at_ns:'90000000000',release_deadline_ns:'140000000000'});
 assert.equal(live.buildLivePlan(funded,signer,'publish_release',{id:'resource',key_base64:btoa('x'.repeat(32))}).actions[0].params.deposit,'0');
 funded.timestampNs='140000000000';assert.throws(()=>live.buildLivePlan(funded,signer,'publish_release',{id:'resource',key_base64:btoa('x'.repeat(32))}));
});
test('only current token holder can transfer or maintain a mirror, with exact one-yocto deposits',()=>{
 const s=released();for(const method of ['nft_transfer','nft_transfer_call']){
  const args={token_id:'resource',receiver_id:'library.testnet',...(method.endsWith('_call')?{msg:''}:{})};
  const plan=live.buildLivePlan(s,signer,method,args);assert.equal(plan.actions[0].params.deposit,'1');
  assert.throws(()=>live.buildLivePlan(s,signer,method,{...args,receiver_id:signer}));
 }
 assert.equal(live.buildLivePlan(s,signer,'set_mirror',{token_id:'resource',mirror_uri:'https://mirror.example/manifest.json'}).actions[0].params.deposit,'1');
 s.campaigns[0].stewardship.owner_id='new-holder.testnet';
 assert.throws(()=>live.buildLivePlan(s,signer,'set_mirror',{token_id:'resource',mirror_uri:'https://mirror.example/manifest.json'}));
});
test('campaign creation stays owner-only, rejects used IDs and respects the deployed capacity',()=>{
 const s=snapshot();const args={id:'new-resource',title:'New resource',reviewer:'reviewer.testnet',manifest_uri:'https://content.example/manifest.json',...hashes,target:'1',funding_deadline_ns:'200000000000',release_window_ns:'50000000000'};
 assert.throws(()=>live.buildLivePlan(s,signer,'create_campaign',args));
 s.account.account_id='shiftultra.testnet';
 assert.equal(live.buildLivePlan(s,'shiftultra.testnet','create_campaign',args).actions[0].params.deposit,'50000000000000000000000');
 assert.throws(()=>live.buildLivePlan(s,'shiftultra.testnet','create_campaign',{...args,id:'resource'}));
 s.config.campaign_count=5;assert.throws(()=>live.buildLivePlan(s,'shiftultra.testnet','create_campaign',args));
});
test('release preflight actually recovers the committed pack before exposing a signing plan',async()=>{
 const pack={...introPack,id:'resource'},artifact=await prepareArtifact(pack),s=snapshot('Funded');
 Object.assign(s.campaigns[0],{funded_at_ns:'90000000000',release_deadline_ns:'140000000000',manifest_hash:artifact.manifestHash,plaintext_hash:artifact.plaintextHash,ciphertext_hash:artifact.ciphertextHash,key_commitment:artifact.keyCommitment,license_hash:await hashBytes(new TextEncoder().encode('CC0-1.0'))});
 const rpc=rpcFixture(s),fetcher=(url,options)=>options?.method==='POST'?rpc(url,options):Promise.resolve(new Response(String(url).endsWith('ciphertext.sunset')?base64ToBytes(artifact.envelope):artifact.manifestText));
 await withFetch(fetcher,async()=>{
  const ready=await live.prepareLiveAction('publish_release',{id:'resource',key_base64:artifact.key},signer);
  assert.equal(ready.plan.actions[0].params.args.key_base64,artifact.key);
  await assert.rejects(()=>live.prepareLiveAction('publish_release',{id:'resource',key_base64:btoa('z'.repeat(32))},signer));
 });
});
test('redirect intent binds exact args without retaining the unreleased content key',async()=>{
 const s=snapshot('Funded');Object.assign(s.campaigns[0],{funded_at_ns:'90000000000',release_deadline_ns:'140000000000'});
 const secret=btoa('x'.repeat(32)),plan=live.buildLivePlan(s,signer,'publish_release',{id:'resource',key_base64:secret});
 const intent=JSON.parse(JSON.stringify(await live.createIntent(plan,s)));
 assert.equal(JSON.stringify(intent).includes(secret),false);
 assert.equal(await live.verifyIntentOutcome(outcome(plan),intent),'success');
 for(const mutate of [
  r=>{r.transaction.signer_id='other.testnet';},r=>{r.transaction.receiver_id='other.testnet';},
  r=>{r.transaction.actions[0].FunctionCall.deposit='1';},r=>{r.transaction.actions[0].FunctionCall.gas='1';},
  r=>{r.transaction.actions[0].FunctionCall.method_name='withdraw';},
  r=>{r.transaction.actions[0].FunctionCall.args=btoa(JSON.stringify({id:'resource',key_base64:btoa('z'.repeat(32))}));}
 ]){const r=outcome(plan);mutate(r);await assert.rejects(()=>live.verifyIntentOutcome(r,intent));}
 const failed=outcome(plan);failed.receipts_outcome[0].outcome.status={Failure:{error:'failed'}};
 assert.equal(await live.verifyIntentOutcome(failed,intent),'failure');
 assert.equal(await live.verifyIntentOutcome({transaction:outcome(plan).transaction},intent),'pending');
});
test('withdrawal UI distinguishes callback-pending credit restoration and actual native payout',async()=>{
 const s=snapshot(),plan=live.buildLivePlan(s,signer,'withdraw',{amount:'100000000000000000000000'}),intent=await live.createIntent(plan,s);
 assert.equal(live.withdrawalState(intent,{...s.account,pending:{operation_id:'4',amount:'100000000000000000000000'}}),'pending');
 assert.equal(live.withdrawalState(intent,{...s.account,credit:'400000000000000000000000'}),'restored');
 assert.equal(live.withdrawalState(intent,{...s.account,credit:'300000000000000000000000',paid:'100000000000000000000000'}),'paid');
 assert.throws(()=>live.withdrawalState(intent,{...s.account,account_id:'other.testnet'}));
});
