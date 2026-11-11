import assert from 'node:assert/strict';
export const contract='sunset.shiftultra.testnet',signer='sponsor.testnet',blockHash='H'.repeat(44);
export const hashes={manifest_hash:'a'.repeat(64),plaintext_hash:'b'.repeat(64),ciphertext_hash:'c'.repeat(64),key_commitment:'d'.repeat(64),license_hash:'e'.repeat(64)};
export function snapshot(state='Active',registered=true){return {
 contract,network:'testnet',codeHash:'9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx',blockHash,height:50,timestampNs:'100000000000',
 config:{schema_version:1,state_layout_version:2,network:'testnet',contract_id:contract,owner:'shiftultra.testnet',max_campaigns:5,max_accounts:100,campaign_count:1,account_count:3,account_storage_allowance:'10000000000000000000000',campaign_storage_allowance:'50000000000000000000000'},
 campaigns:[{schema_version:1,id:'resource',title:'Resource',creator:'shiftultra.testnet',reviewer:'reviewer.testnet',manifest_uri:'https://content.example/manifest.json',...hashes,target:'500000000000000000000000',total_contributed:'200000000000000000000000',escrow:'200000000000000000000000',funding_deadline_ns:'200000000000',release_window_ns:'50000000000',funded_at_ns:'0',release_deadline_ns:null,agreement_digest:'f'.repeat(64),state,public_key_base64:null,stewardship:null}],
 account:{schema_version:1,account_id:signer,registered,credit:registered?'400000000000000000000000':'0',paid:'0',pending:null,contributions:registered?[{campaign_id:'resource',amount:'200000000000000000000000',refunded:false}]:[]}
};}
export function released(){const s=snapshot('Released');Object.assign(s.campaigns[0],{funded_at_ns:'50000000000',release_deadline_ns:'100000000000',public_key_base64:btoa('x'.repeat(32)),stewardship:{token_id:'resource',owner_id:signer,mirror_uri:'https://content.example/manifest.json'}});return s;}
export function response(value){return new Response(JSON.stringify(value),{headers:{'content-type':'application/json'}});}
export function rpcFixture(s,mutate=()=>{}){return async(url,options)=>{
 const q=JSON.parse(options.body);let result;
 if(q.method==='status')result={chain_id:'testnet'};
 else if(q.method==='block')result={header:{hash:blockHash,height:s.height,timestamp_nanosec:s.timestampNs}};
 else if(q.params.request_type==='view_account')result={block_hash:blockHash,block_height:s.height,code_hash:s.codeHash};
 else {assert.equal(q.params.block_id,blockHash);const value={get_config:s.config,list_campaigns:s.campaigns,get_account:s.account}[q.params.method_name];assert.notEqual(value,undefined);result={block_hash:blockHash,block_height:s.height,result:[...new TextEncoder().encode(JSON.stringify(value))]};}
 mutate(q,result);return response({jsonrpc:'2.0',id:q.id,result});
};}
export async function withFetch(fetcher,work){const original=globalThis.fetch;globalThis.fetch=fetcher;try{return await work();}finally{globalThis.fetch=original;}}
export function outcome(plan){const p=plan.actions[0].params;return {final_execution_status:'FINAL',transaction:{hash:'T'.repeat(44),signer_id:plan.expectedSignerId,receiver_id:plan.receiverId,actions:[{FunctionCall:{method_name:p.methodName,args:btoa(JSON.stringify(p.args)),gas:p.gas,deposit:p.deposit}}]},transaction_outcome:{outcome:{status:{SuccessReceiptId:'receipt'}}},status:{SuccessValue:''},receipts_outcome:[{outcome:{status:{SuccessValue:''}}}]};}
