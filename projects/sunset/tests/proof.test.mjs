import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {PROOF,fingerprintCells,shorten,transactionUrl} from '../src/lib/proof.mjs';

const evidence=async name=>JSON.parse(await readFile(new URL('../evidence/'+name,import.meta.url),'utf8'));

test('every displayed onchain record matches the finalized testnet evidence',async()=>{
  const showcase=await evidence('testnet-showcase.json'),refunds=await evidence('testnet-refunds.json');
  assert.equal(PROOF.contract,showcase.contract_id);assert.equal(PROOF.codeHash,showcase.code_hash);
  assert.equal(PROOF.verifiedBlock,showcase.finalized_verification_block.block_height);
  assert.equal(refunds.contract,PROOF.contract);assert.equal(refunds.code_hash,PROOF.codeHash);
  for(const row of PROOF.release){
    const tx=showcase.transactions.find(item=>item.step===row.step);
    assert.ok(tx,`Missing showcase step ${row.step}`);
    assert.equal(tx.transaction_hash,row.hash);assert.equal(tx.signer_id,row.signer);
    assert.equal(tx.final_execution_status,'FINAL');assert.equal(tx.intentional_authority_failure,false);
  }
  const amounts=showcase.transactions.filter(item=>item.step.startsWith('contribute-')).map(item=>item.actions[0].FunctionCall.args_json.amount);
  assert.deepEqual(amounts,['60000000000000000000000','40000000000000000000000']);
  assert.equal(showcase.native_creator_transfer.amount_yocto,'100000000000000000000000');
  for(const row of PROOF.refund){
    const tx=refunds.transactions.find(item=>item.case==='funding'&&item.step===row.step);
    assert.ok(tx,`Missing refund step ${row.step}`);
    assert.equal(tx.transaction_hash,row.hash);assert.equal(tx.signer_id,row.signer);assert.equal(tx.final_execution_status,'FINAL');
    assert.equal(tx.explorer_url,transactionUrl(row.hash));
  }
});

test('fingerprints are deterministic, mirrored and differ between digests',()=>{
  const a='17a3c1ffd291d855812276c48c6b600dd19a4706bfa48f0797cee0affc6a8743',b='f808d7472f2e5d31749d02b42f89771e1be26ea80c985422ff8e3ed3e7e9656d';
  assert.deepEqual(fingerprintCells(a),fingerprintCells(a));
  assert.notDeepEqual(fingerprintCells(a),fingerprintCells(b));
  for(const cell of fingerprintCells(a))assert.ok(fingerprintCells(a).some(other=>other.y===cell.y&&other.x===4-cell.x),'pattern must mirror');
  assert.deepEqual(fingerprintCells('not a digest'),[]);
  assert.equal(shorten('sunset.shiftultra.testnet',8,7),'sunset.s…testnet');assert.equal(shorten('short'),'short');
});
