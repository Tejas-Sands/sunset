import {test} from 'node:test';
import assert from 'node:assert/strict';
import {sendWalletAction,checkWalletIntent,loadPendingIntent,forgetUnsubmittedIntent,transactionHashFromUrl} from '../src/lib/wallet.mjs';
import {snapshot,signer,rpcFixture,outcome,response,withFetch} from './helpers/live-fixtures.mjs';
import {buildLivePlan,createIntent} from '../src/lib/live.mjs';
function storage(){const values=new Map();return {values,getItem:key=>values.get(key)??null,setItem:(key,value)=>values.set(key,value),removeItem:key=>values.delete(key)};}
function wallet(send){return {getAccounts:async()=>[{accountId:signer}],signAndSendTransaction:send};}
const args={id:'resource',amount:'50000000000000000000000'};
const sendOptions=(store,wallet)=>({storage:store,wallet,signer,method:'contribute',args,isCurrent:()=>true});
function chain(s,receipt){const rpc=rpcFixture(s);return (url,options)=>{
 const q=JSON.parse(options.body);
 if(q.method==='tx'){assert.equal(q.params.sender_account_id,signer);assert.equal(q.params.wait_until,'FINAL');return Promise.resolve(response({jsonrpc:'2.0',id:q.id,result:receipt}));}
 return rpc(url,options);
};}
test('wallet action confirms fetched final RPC receipts and clears only its matching pending reference',async()=>{
 const s=snapshot(),store=storage(),plan=buildLivePlan(s,signer,'contribute',args),receipt=outcome(plan);
 await withFetch(chain(s,receipt),async()=>{
  const result=await sendWalletAction(sendOptions(store,wallet(async request=>{
   assert.equal(request.signerId,signer);assert.equal(request.network,'testnet');assert.equal(request.receiverId,'sunset.shiftultra.testnet');
   assert.equal(request.actions[0].params.deposit,'50000000000000000000000');
   assert.ok(loadPendingIntent(store,signer));return {transaction:{hash:receipt.transaction.hash}};
  })));
  assert.equal(result.status,'success');assert.equal(loadPendingIntent(store,signer),null);
 });
});
test('wallet or UI account switching during preflight prevents any signature request',async()=>{
 const s=snapshot();await withFetch(rpcFixture(s),async()=>{
  for(const kind of ['wallet','ui']){
   const store=storage();let sent=0;
   const w=wallet(async()=>{sent++;});if(kind==='wallet')w.getAccounts=async()=>[{accountId:'other.testnet'}];
   const options={...sendOptions(store,w),isCurrent:()=>kind!=='ui'};
   await assert.rejects(()=>sendWalletAction(options),/account changed/i);assert.equal(sent,0);assert.equal(store.values.size,0);
  }
 });
});
test('blocked tracking storage fails before signing; an unknown wallet error retains the intent and prevents duplicate sending',async()=>{
 const s=snapshot();await withFetch(rpcFixture(s),async()=>{
  let sent=0;const blocked=storage();blocked.setItem=()=>{throw Error('denied');};
  await assert.rejects(()=>sendWalletAction(sendOptions(blocked,wallet(async()=>{sent++;}))),/storage|track/i);assert.equal(sent,0);
  const store=storage(),w=wallet(async()=>{sent++;throw Error('transport closed after possible broadcast');});
  await assert.rejects(()=>sendWalletAction(sendOptions(store,w)),/interrupted|wallet activity/i);
  assert.ok(loadPendingIntent(store,signer));assert.equal(sent,1);
  await assert.rejects(()=>sendWalletAction(sendOptions(store,w)),/pending|existing/i);assert.equal(sent,1);
 });
});
test('explicit wallet rejection code clears an unsubmitted request without reporting settlement',async()=>{
 const store=storage();await withFetch(rpcFixture(snapshot()),async()=>{
  const result=await sendWalletAction(sendOptions(store,wallet(async()=>{throw Object.assign(Error('Rejected'),{code:4001});})));
  assert.equal(result.status,'cancelled');assert.equal(loadPendingIntent(store,signer),null);
 });
});
test('a hash-only or unfinished RPC result remains pending and can later resume against the exact original intent',async()=>{
 const s=snapshot(),store=storage(),plan=buildLivePlan(s,signer,'contribute',args),receipt=outcome(plan),partial={...receipt,final_execution_status:'EXECUTED_OPTIMISTIC'};
 await withFetch(chain(s,partial),async()=>{
  const result=await sendWalletAction(sendOptions(store,wallet(async()=>({transaction:{hash:receipt.transaction.hash}}))));
  assert.equal(result.status,'pending');assert.equal(loadPendingIntent(store,signer).hash,receipt.transaction.hash);
  assert.throws(()=>forgetUnsubmittedIntent(store,signer),/submitted|hash|status/i);
 });
 await withFetch(chain(s,receipt),async()=>{assert.equal((await checkWalletIntent({storage:store,signer})).status,'success');});
 assert.equal(loadPendingIntent(store,signer),null);
});
test('bad receipt bindings and damaged saved references stay unresolved without being overwritten',async()=>{
 const s=snapshot(),store=storage(),plan=buildLivePlan(s,signer,'contribute',args),receipt=outcome(plan);receipt.transaction.receiver_id='different.testnet';
 await withFetch(chain(s,receipt),async()=>{await assert.rejects(()=>sendWalletAction(sendOptions(store,wallet(async()=>({transaction:{hash:receipt.transaction.hash}})))));});
 assert.ok(loadPendingIntent(store,signer));
 const [key]=store.values.keys();store.setItem(key,'{broken');
 assert.throws(()=>loadPendingIntent(store,signer));assert.equal(store.getItem(key),'{broken');
});
test('an intent with no returned hash can be recovered from a user-supplied matching hash, without persisting private arguments',async()=>{
 const s=snapshot(),store=storage(),plan=buildLivePlan(s,signer,'contribute',args),intent=await createIntent(plan,s),receipt=outcome(plan);
 await withFetch(chain(s,receipt),async()=>{
  const first=await sendWalletAction(sendOptions(store,wallet(async()=>undefined)));assert.equal(first.status,'pending');
  const raw=[...store.values.values()].join('');assert.equal(raw.includes('"args"'),false);assert.equal(raw.includes('key_base64'),false);
  assert.equal((await checkWalletIntent({storage:store,signer,hash:receipt.transaction.hash})).status,'success');
 });
 assert.equal(loadPendingIntent(store,signer),null);assert.equal(intent.method,'contribute');
});
test('wallet redirects accept one valid transaction reference and reject arbitrary or multiple hashes',()=>{
 const hash='T'.repeat(44);
 assert.equal(transactionHashFromUrl('https://sunset.example/app/?transactionHashes='+hash),hash);
 assert.equal(transactionHashFromUrl('https://sunset.example/app/?transactionHashes='+hash+','+hash),undefined);
 assert.equal(transactionHashFromUrl('https://sunset.example/app/?transactionHashes=javascript:alert(1)'),undefined);
 assert.equal(transactionHashFromUrl('https://sunset.example/app/?view=Funding'),undefined);
});
test('a failed withdrawal callback retains the transaction reference while the onchain operation is still pending',async()=>{
 const initial=snapshot(),after=snapshot(),store=storage(),plan=buildLivePlan(initial,signer,'withdraw',{amount:'1'}),receipt=outcome(plan);
 receipt.receipts_outcome[0].outcome.status={Failure:{error:'callback failed'}};
 after.account.pending={operation_id:'1',amount:'1'};after.account.credit='399999999999999999999999';
 let submitted=false;const first=rpcFixture(initial),later=rpcFixture(after);
 await withFetch((url,options)=>{const q=JSON.parse(options.body);if(q.method==='tx'){submitted=true;return Promise.resolve(response({jsonrpc:'2.0',id:q.id,result:receipt}));}return (submitted?later:first)(url,options);},async()=>{
  const result=await sendWalletAction({...sendOptions(store,wallet(async()=>({transaction:{hash:receipt.transaction.hash}}))),method:'withdraw',args:{amount:'1'}});
  assert.equal(result.status,'pending');assert.equal(loadPendingIntent(store,signer).hash,receipt.transaction.hash);
 });
});
