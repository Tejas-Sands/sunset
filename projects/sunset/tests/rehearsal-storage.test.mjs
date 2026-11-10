import test from 'node:test';
import assert from 'node:assert/strict';
import {seedDemo,prepareArtifact} from '../src/lib/demo.mjs';
import {emptyLedger,createCampaign,toYocto} from '../src/lib/ledger.mjs';
import {hashBytes,introPack} from '../src/lib/pack.mjs';
import {recoverPack} from '../scripts/recover-pack.mjs';
import {validateRehearsalData,commitRehearsal} from '../src/lib/rehearsal.mjs';

test('saved rehearsal validation preserves valid current and legacy data before stewardship migration',async()=>{
  const data=await seedDemo();
  assert.equal(validateRehearsalData(data),data);
  const legacy=structuredClone(data);
  for(const campaign of legacy.ledger.campaigns){
    delete campaign.steward;
    const artifact=legacy.artifacts[campaign.id];
    artifact.manifest.schema=1;delete artifact.manifest.ciphertext_path;
    artifact.manifestText=JSON.stringify(artifact.manifest);
    artifact.manifestHash=await hashBytes(new TextEncoder().encode(artifact.manifestText));
    campaign.manifestHash=artifact.manifestHash;
    campaign.digest=JSON.stringify([campaign.id,campaign.creator,campaign.reviewer,campaign.target,campaign.fundingDeadline,campaign.releaseWindow,campaign.keyCommitment,campaign.plaintextHash,campaign.ciphertextHash,campaign.manifestHash]);
    assert.match(await recoverPack(artifact,{keyBase64:artifact.key,manifestHash:artifact.manifestHash}),/<!doctype html>/i);
  }
  const retained=JSON.stringify(legacy);
  assert.equal(validateRehearsalData(legacy),legacy);
  assert.equal(JSON.stringify(legacy),retained,'validation must preserve original campaign and artifact bytes');
});

test('saved rehearsal rejects conserving campaign corruption before rendering',async()=>{
  const source=await seedDemo();
  for(const mutate of [
    data=>delete data.ledger.campaigns[0].raised,
    data=>data.ledger.campaigns[0].contributions=null,
    data=>{data.ledger=emptyLedger();data.artifacts={};},
  ]){
    const data=structuredClone(source);mutate(data);
    assert.throws(()=>validateRehearsalData(data));
  }
});

test('saved rehearsal rejects missing artifact entries instead of exposing broken recovery controls',async()=>{
  const data=await seedDemo();
  data.artifacts={};
  assert.throws(()=>validateRehearsalData(data));
});

test('saved rehearsal rejects malformed grants and event records before their views open',async()=>{
  const source=await seedDemo();
  for(const mutate of [
    data=>delete data.ledger.events,
    data=>delete data.ledger.grants[0].claims,
    data=>data.ledger.grants[0].unitPrice='invalid',
  ]){
    const data=structuredClone(source);mutate(data);
    assert.throws(()=>validateRehearsalData(data));
  }
});

test('saved rehearsal rejects a string clock offset instead of coercing deadlines',async()=>{
  const data=await seedDemo();data.offset='0';
  assert.throws(()=>validateRehearsalData(data));
});

function storageWith(raw){
  return {raw,writes:0,getItem(key){assert.equal(key,'sunset-rehearsal-v1');return this.raw;},setItem(key,value){assert.equal(key,'sunset-rehearsal-v1');this.raw=value;this.writes++;}};
}

test('a current browser snapshot can commit valid rehearsal changes',async()=>{
  const data=await seedDemo(),original=JSON.stringify(data),storage=storageWith(original);
  data.offset=86400000;
  const serialized=commitRehearsal(storage,original,data);
  assert.equal(serialized,JSON.stringify(data));
  assert.equal(storage.raw,serialized);
  assert.equal(storage.writes,1);
});

test('a stale tab cannot erase a newer draft and its retained release artifact',async()=>{
  const data=await seedDemo(),original=JSON.stringify(data),storage=storageWith(original);
  const newer=structuredClone(data),pack={...introPack,id:'other-tab-resource'},artifact=await prepareArtifact(pack),now=Date.now();
  createCampaign(newer.ledger,{id:pack.id,title:pack.title,description:pack.description,creator:'maker.testnet',reviewer:'teacher.testnet',target:toYocto('8'),fundingDeadline:now+86400000,releaseWindow:86400000,keyCommitment:artifact.keyCommitment,plaintextHash:artifact.plaintextHash,ciphertextHash:artifact.ciphertextHash,manifestHash:artifact.manifestHash},now);
  newer.artifacts[pack.id]=artifact;
  const latest=commitRehearsal(storage,original,newer);
  const stale=structuredClone(data);stale.offset=86400000;
  assert.throws(()=>commitRehearsal(storage,original,stale));
  assert.equal(storage.raw,latest);
  assert.equal(storage.writes,1);
  assert.equal(JSON.parse(storage.raw).artifacts[pack.id].key,artifact.key);
});

test('a first-visit seed cannot overwrite data another tab saved during initialization',async()=>{
  const data=await seedDemo(),latest=JSON.stringify(data),storage=storageWith(latest);
  assert.throws(()=>commitRehearsal(storage,null,data));
  assert.equal(storage.raw,latest);
  assert.equal(storage.writes,0);
});
