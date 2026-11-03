import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {validatePack,encryptPack,decryptPack,createOfflineHtml,introPack} from '../src/lib/pack.mjs';
import {prepareArtifact} from '../src/lib/demo.mjs';
import {recoverPack} from '../scripts/recover-pack.mjs';

const guide = () => ({
  schema:2,kind:'guide',id:'maintainer-example',title:'Maintainer handbook',
  description:'An original example guide for maintainers.',license:'CC0-1.0',
  sections:[
    {id:'release',title:'Prepare a public release',body:'Inspect the exact commit.\n\nRecord the checks before publishing.',checklist:[{id:'record-commit',text:'Record the commit being released.'}]},
    {id:'recover',title:'Recover a lost commit',body:'Inspect the reflog. Create a new recovery branch before making changes.',checklist:[{id:'inspect-reflog',text:'Inspect the candidate commit before restoring work.'}]},
  ],
});
const hash = value => createHash('sha256').update(value).digest('hex');

test('accepts a structured guide without changing its content', () => {
  const input = guide();
  assert.deepEqual(validatePack(input), input);
});

test('guide validation rejects malformed, executable and oversized content', () => {
  const changes = [
    p=>p.schema=1,p=>p.kind='html',p=>p.extra='unknown',p=>p.license='MIT',
    p=>p.sections=[],p=>p.sections=Array.from({length:65},(_,i)=>({...p.sections[0],id:'section-'+i,checklist:[]})),
    p=>p.sections[1].id=p.sections[0].id,
    p=>p.sections[1].checklist[0].id=p.sections[0].checklist[0].id,
    p=>p.sections[0].checklist=Array.from({length:33},(_,i)=>({id:'item-'+i,text:'A check.'})),
    p=>p.sections[0].title='x'.repeat(161),p=>p.sections[0].body='x'.repeat(32769),
    p=>p.sections[0].checklist[0].text='x'.repeat(1025),
    p=>p.sections[0].body='<script>alert(1)</script>',
    p=>p.sections[0].body='Read https://example.com/guide',
    p=>p.sections[0].checklist[0].text='javascript:alert(1)',
    p=>p.sections[0].checklist[0].checked=true,
    p=>p.sections[0].body='',p=>p.sections[0].checklist[0].id='../escape',
  ];
  for (const mutate of changes) {
    const input=guide();mutate(input);
    assert.throws(()=>validatePack(input));
    assert.throws(()=>createOfflineHtml(input));
  }
});

test('guide encryption and independent recovery retain exact data and standalone procedures', async () => {
  const input=guide(),plain=new TextEncoder().encode(JSON.stringify(input)),key=new Uint8Array(32).fill(4);
  assert.deepEqual(await decryptPack(await encryptPack(plain,key),key),plain);
  const artifact=await prepareArtifact(input);
  const html=await recoverPack(artifact,{manifestHash:artifact.manifestHash,keyBase64:artifact.key});
  assert.equal(html,createOfflineHtml(input));
  const embedded=html.match(/<script type="application\/json" id="pack-data">([\s\S]*?)<\/script>/)[1];
  assert.deepEqual(JSON.parse(embedded),input);
  assert.match(html,/default-src 'none'/);
  assert.match(html,/connect-src 'none'/);
  assert.doesNotMatch(html,/\b(?:src|href)\s*=\s*["'](?:https?:|\/\/)/i);
  assert.doesNotMatch(html,/\b(?:fetch|XMLHttpRequest|WebSocket|sendBeacon|importScripts)\s*\(/);
  assert.ok(html.includes('guide-reader') && html.includes('guide-search'));
});

test('legacy sample, committed live export and published standalone bytes remain unchanged', async () => {
  assert.equal(hash(JSON.stringify(introPack)),'ad0d5b6823c9d0d4a3be605f32ac6bb24f1cbf9edb5f2a14e0281427e3cc19f1');
  assert.equal(hash(createOfflineHtml(introPack)),'806c63b034d07a55820e9576d039ca4f9464cfbe53486e459665944769f5393d');
  assert.equal(hash(await readFile(new URL('../public/try-lantern-trail.html',import.meta.url))),'806c63b034d07a55820e9576d039ca4f9464cfbe53486e459665944769f5393d');
  assert.equal(hash(createOfflineHtml({...introPack,id:'lantern-trail-testnet-v1'})),'fbe1df06b5eb4a93aae1eb12009f4d910e3ba432862918e3c254fc013ab79738');
});

test('guide progress restores only the exact version and valid checklist identities', async () => {
  const api=await import('../src/lib/guide.mjs').catch(()=>({}));
  assert.equal(typeof api.loadGuideProgress,'function');
  const values=new Map(),storage={getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,v)};
  const input=guide(),state={section:'recover',checked:['record-commit','inspect-reflog']};
  assert.equal(api.saveGuideProgress(input,state,storage),true);
  assert.deepEqual(api.loadGuideProgress(input,storage),{...state,persistent:true});
  const changed=guide();changed.sections[0].body='A revised procedure.';
  assert.deepEqual(api.loadGuideProgress(changed,storage),{section:'release',checked:[],persistent:true});
  values.set('sunset-guide-progress:'+input.id,JSON.stringify({version:JSON.stringify(input),section:'missing',checked:['record-commit','unknown','record-commit']}));
  assert.deepEqual(api.loadGuideProgress(input,storage),{section:'release',checked:['record-commit'],persistent:true});
});

test('unavailable storage keeps usable in-memory guide progress', async () => {
  const api=await import('../src/lib/guide.mjs').catch(()=>({}));
  assert.equal(typeof api.loadGuideProgress,'function');
  const storage={getItem(){throw Error('Storage blocked')},setItem(){throw Error('Quota exceeded')}};
  assert.deepEqual(api.loadGuideProgress(guide(),storage),{section:'release',checked:[],persistent:false});
  const inMemory={section:'recover',checked:['inspect-reflog']};
  assert.equal(api.saveGuideProgress(guide(),inMemory,storage),false);
  assert.deepEqual(inMemory,{section:'recover',checked:['inspect-reflog']});
});

test('guide search finds procedure bodies and checklist text as well as chapter titles', async () => {
  const api=await import('../src/lib/guide.mjs').catch(()=>({}));
  assert.equal(typeof api.filterGuideSections,'function');
  assert.deepEqual(api.filterGuideSections(guide(),'  REFLOG ').map(s=>s.id),['recover']);
  assert.deepEqual(api.filterGuideSections(guide(),'being released').map(s=>s.id),['release']);
  assert.equal(api.filterGuideSections(guide(),'').length,2);
  assert.deepEqual(api.filterGuideSections(guide(),'no matching text'),[]);
});

test('the public maintainer sample is the exact self-contained export of its guide data',async()=>{
  const input=JSON.parse(await readFile(new URL('../public/packs/maintainer-handbook.json',import.meta.url),'utf8'));
  assert.equal(validatePack(input).kind,'guide');
  const html=await readFile(new URL('../public/try-maintainer-handbook.html',import.meta.url),'utf8').catch(()=>null);
  assert.ok(html,'A discoverable standalone handbook must be generated.');
  assert.equal(html,createOfflineHtml(input));
});
