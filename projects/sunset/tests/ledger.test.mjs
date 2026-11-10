import { test } from 'node:test';
import assert from 'node:assert/strict';
import { emptyLedger, createCampaign, approveCampaign, contribute, release, refund, withdraw, campaignState, createGrant, approveClaim, refundGrant, conservation, toYocto, formatNear } from '../src/lib/ledger.mjs';
const H='a'.repeat(64), K='b'.repeat(64);
function setup(){let s=emptyLedger();createCampaign(s,{id:'one',title:'One',creator:'creator.testnet',reviewer:'teacher.testnet',target:toYocto('8'),fundingDeadline:2000,releaseWindow:1000,keyCommitment:K,plaintextHash:H,ciphertextHash:H,manifestHash:H},0);approveCampaign(s,'one','teacher.testnet',s.campaigns[0].digest,1);return s;}
test('strict exact money, no floating point or excessive precision',()=>{assert.equal(toYocto('0.000000000000000000000001'),'1');assert.equal(formatNear(toYocto('1.25')),'1.25');for(const x of ['1e2','-1','NaN','0.0000000000000000000000001','1.','', '01'])assert.throws(()=>toYocto(x));});
test('cap credits surplus; release pays fixed creator once and conserves money',()=>{const s=setup();contribute(s,'one','alice.testnet',toYocto('6'),2);contribute(s,'one','bob.testnet',toYocto('3'),3);assert.equal(s.campaigns[0].raised,toYocto('8'));assert.equal(s.credits['bob.testnet'],toYocto('1'));assert.equal(campaignState(s.campaigns[0],3),'funded');release(s,'one',K,'public-key',4);assert.equal(s.credits['creator.testnet'],toYocto('8'));assert.throws(()=>release(s,'one',K,'public-key',5));assert.throws(()=>refund(s,'one','alice.testnet',3000));assert.equal(conservation(s),true);});
test('refund and release are exclusive at exact deadline, replay cannot credit twice',()=>{const s=setup();contribute(s,'one','alice.testnet',toYocto('8'),2);assert.equal(campaignState(s.campaigns[0],1002),'refundable');assert.throws(()=>release(s,'one',K,'key',1002));refund(s,'one','alice.testnet',1002);assert.throws(()=>refund(s,'one','alice.testnet',1003));assert.equal(s.credits['alice.testnet'],toYocto('8'));assert.equal(conservation(s),true);});
test('failed funding refundable at equality; wrong approvals/key and unsafe sums rejected',()=>{const s=setup();contribute(s,'one','alice.testnet','4',10);assert.throws(()=>contribute(s,'one','alice.testnet','3',2000));assert.throws(()=>release(s,'one',H,'key',20));refund(s,'one','alice.testnet',2000);assert.equal(conservation(s),true);assert.throws(()=>createCampaign(s,{...s.campaigns[0]},1));});
test('grant provider and approver fixed, cap and expiry enforced, duplicate claim once',()=>{const s=setup();createGrant(s,{id:'school',sponsor:'alice.testnet',provider:'bus.testnet',approver:'teacher.testnet',purpose:'Deliver offline learning',unitPrice:toYocto('0.1'),budget:toYocto('1'),expiresAt:2000},2);assert.throws(()=>approveClaim(s,'school','claim',1,H,'mallory.testnet',3));approveClaim(s,'school','claim',3,H,'teacher.testnet',3);assert.throws(()=>approveClaim(s,'school','claim',3,H,'teacher.testnet',3));assert.throws(()=>approveClaim(s,'school','big',8,H,'teacher.testnet',4));assert.throws(()=>approveClaim(s,'school','late',1,H,'teacher.testnet',2000));refundGrant(s,'school',2000);assert.equal(s.credits['bus.testnet'],toYocto('0.3'));assert.equal(s.credits['alice.testnet'],toYocto('0.7'));assert.equal(conservation(s),true);});

test('the valid constructor account can sponsor, refund, withdraw and receive its fixed creator credit',()=>{
  const sponsor=setup();
  contribute(sponsor,'one','constructor',toYocto('3'),2);
  assert.equal(sponsor.campaigns[0].contributions.constructor,toYocto('3'));
  refund(sponsor,'one','constructor',2000);
  assert.equal(sponsor.credits.constructor,toYocto('3'));
  assert.throws(()=>refund(sponsor,'one','constructor',2001),/No unclaimed contribution/);
  withdraw(sponsor,'constructor',toYocto('3'),2002);
  assert.equal(sponsor.credits.constructor,'0');
  assert.equal(sponsor.withdrawn,toYocto('3'));
  assert.equal(conservation(sponsor),true);

  const creator=emptyLedger();
  createCampaign(creator,{id:'maker',title:'A public resource',creator:'constructor',reviewer:'teacher.testnet',target:toYocto('5'),fundingDeadline:2000,releaseWindow:1000,keyCommitment:K,plaintextHash:H,ciphertextHash:H,manifestHash:H},0);
  approveCampaign(creator,'maker','teacher.testnet',creator.campaigns[0].digest,1);
  assert.throws(()=>withdraw(creator,'constructor','1',2),/Insufficient claimable credit/);
  contribute(creator,'maker','alice.testnet',toYocto('7'),3);
  release(creator,'maker',K,'public-key',4);
  assert.equal(creator.credits.constructor,toYocto('5'));
  assert.equal(creator.credits['alice.testnet'],toYocto('2'));
  withdraw(creator,'constructor',toYocto('5'),5);
  assert.equal(creator.withdrawn,toYocto('5'));
  assert.equal(conservation(creator),true);

  const unchanged=JSON.stringify(sponsor);
  assert.throws(()=>contribute(sponsor,'one','__proto__','1',3),/Invalid adult account/);
  assert.equal(JSON.stringify(sponsor),unchanged);
});
