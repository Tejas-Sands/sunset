import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createOfflineHtml,validatePack,encryptPack,decryptPack} from '../src/lib/pack.mjs';
import {prepareArtifact} from '../src/lib/demo.mjs';
import {recoverPack} from '../scripts/recover-pack.mjs';

const packUrl=new URL('../public/packs/workshop-kit.json',import.meta.url);
const htmlUrl=new URL('../public/try-workshop-kit.html',import.meta.url);

test('the actual workshop kit is a valid data-only guide',async()=>{
  const pack=JSON.parse(await readFile(packUrl,'utf8'));
  assert.equal(validatePack(pack),pack);
  assert.equal(pack.id,'workshop-kit');
  assert.equal(pack.kind,'guide');
});

test('the public workshop HTML is the exact self-contained export of its source',async()=>{
  const pack=JSON.parse(await readFile(packUrl,'utf8'));
  const html=await readFile(htmlUrl,'utf8');
  assert.equal(html,createOfflineHtml(pack));
  const embedded=html.match(/<script type="application\/json" id="pack-data">([\s\S]*?)<\/script>/);
  assert.ok(embedded,'The retained HTML must include the complete guide data.');
  assert.deepEqual(JSON.parse(embedded[1]),pack);
  assert.match(html,/default-src 'none'/);
  assert.match(html,/connect-src 'none'/);
  assert.doesNotMatch(html,/\b(?:src|href)\s*=\s*["'](?:https?:|\/\/)/i);
  assert.doesNotMatch(html,/\b(?:fetch|XMLHttpRequest|WebSocket|sendBeacon|importScripts)\s*\(/);
});

test('the workshop retains exact encrypted bytes and recovers from a separate artifact and backup',async()=>{
  const source=new Uint8Array(await readFile(packUrl));
  const key=new Uint8Array(32).fill(7);
  assert.deepEqual(await decryptPack(await encryptPack(source,key),key),source);

  const pack=JSON.parse(new TextDecoder().decode(source));
  const artifact=await prepareArtifact(pack);
  const backup={manifestHash:artifact.manifestHash,keyBase64:artifact.key};
  const retainedArtifact=JSON.parse(JSON.stringify({manifestText:artifact.manifestText,envelope:artifact.envelope}));
  assert.equal(await recoverPack(retainedArtifact,backup),await readFile(htmlUrl,'utf8'));
  await assert.rejects(recoverPack(retainedArtifact,{...backup,keyBase64:Buffer.alloc(32).toString('base64')}),/Wrong release backup/);
});
