import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';

const library = () => import('../src/lib/pack.mjs');
const encoder = new TextEncoder();
const key = Uint8Array.from({ length: 32 }, (_, i) => i);
const bytes = (pack) => encoder.encode(JSON.stringify(pack));
const copy = (pack) => structuredClone(pack);

test('validates a complete original five-question pack without changing its data', async () => {
  const { validatePack, introPack } = await library();
  assert.equal(introPack.questions.length, 5);
  assert.deepEqual(validatePack(copy(introPack)), introPack);
});

test('rejects unknown fields, duplicate identities and invalid integer answers', async () => {
  const { validatePack, introPack } = await library();
  const mutations = [
    (pack) => { pack.script = 'alert(1)'; },
    (pack) => { pack.questions[0].image = 'https://example.com/a.png'; },
    (pack) => { pack.questions[1].id = pack.questions[0].id; },
    (pack) => { pack.questions[0].choices = [1, 1, 2]; },
    (pack) => { pack.questions[0].answer = 999999; },
    (pack) => { pack.questions[0].answer = 1.5; },
    (pack) => { pack.questions[0].choices[0] = Number.MAX_SAFE_INTEGER + 1; },
    (pack) => { pack.questions = []; },
    (pack) => { pack.license = 'all-rights-reserved'; },
    (pack) => { pack.id = '../private'; },
  ];
  for (const mutate of mutations) {
    const pack = copy(introPack);
    mutate(pack);
    assert.throws(() => validatePack(pack));
  }
});

test('rejects markup, script URLs and remote resource references in every text boundary', async () => {
  const { validatePack, createOfflineHtml, introPack } = await library();
  for (const text of ['</script><script>alert(1)</script>', '<img src=x onerror=alert(1)>', 'javascript:alert(1)', 'https://example.com/answer', '//example.com/answer', 'data:text/html,hello']) {
    const pack = copy(introPack);
    pack.questions[0].explanation = text;
    assert.throws(() => validatePack(pack));
    assert.throws(() => createOfflineHtml(pack));
  }
});

test('hashes exact bytes and agrees with the independent domain-separated key vector', async () => {
  const { hashBytes, keyCommitment } = await library();
  assert.equal(await hashBytes(encoder.encode('abc')), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
  const expected = createHash('sha256').update('SUNSET:KEY:1:').update(key).digest('hex');
  assert.equal(await keyCommitment(key), expected);
  await assert.rejects(() => keyCommitment(new Uint8Array(31)));
});

test('authenticates exact pack bytes and uses a fresh nonce for every encryption', async () => {
  const { introPack, encryptPack, decryptPack } = await library();
  const plaintext = bytes(introPack);
  const first = await encryptPack(plaintext, key);
  const second = await encryptPack(plaintext, key);
  assert.equal(new TextDecoder().decode(first.slice(0, 8)), 'SUNSET01');
  assert.equal(first.length, plaintext.length + 36);
  assert.notDeepEqual(first.slice(8, 20), second.slice(8, 20));
  assert.deepEqual(await decryptPack(first, key), plaintext);
});

test('rejects wrong keys, corrupted authentication tags and malformed envelopes', async () => {
  const { introPack, encryptPack, decryptPack } = await library();
  const envelope = await encryptPack(bytes(introPack), key);
  const corrupted = new Uint8Array(envelope);
  corrupted[corrupted.length - 1] ^= 1;
  await assert.rejects(() => decryptPack(corrupted, key));
  await assert.rejects(() => decryptPack(envelope, new Uint8Array(32)));
  await assert.rejects(() => decryptPack(envelope.slice(0, 35), key));
  const wrongHeader = new Uint8Array(envelope);
  wrongHeader[0] = 0;
  await assert.rejects(() => decryptPack(wrongHeader, key));
  await assert.rejects(() => encryptPack(bytes(introPack), new Uint8Array(33)));
});

test('enforces the plaintext limit separately from ciphertext overhead', async () => {
  const { encryptPack, decryptPack, validatePack, introPack } = await library();
  await assert.rejects(() => encryptPack(new Uint8Array(5 * 1024 * 1024 + 1), key));
  await assert.rejects(() => decryptPack(new Uint8Array(5 * 1024 * 1024 + 37), key));
  const oversized = copy(introPack);
  oversized.description = 'x'.repeat(5 * 1024 * 1024);
  assert.throws(() => validatePack(oversized));
});

test('validates decrypted content even when encryption and authentication are valid', async () => {
  const { decryptPack } = await library();
  const nonce = new Uint8Array(12);
  const cryptoKey = await crypto.subtle.importKey('raw', key, 'AES-GCM', false, ['encrypt']);
  const ciphertext = new Uint8Array(await crypto.subtle.encrypt({ name: 'AES-GCM', iv: nonce }, cryptoKey, encoder.encode('{"script":"alert(1)"}')));
  const envelope = new Uint8Array(20 + ciphertext.length);
  envelope.set(encoder.encode('SUNSET01'));
  envelope.set(nonce, 8);
  envelope.set(ciphertext, 20);
  await assert.rejects(() => decryptPack(envelope, key));
});

test('exports the complete pack with a network-blocking policy and no external resources', async () => {
  const { introPack, createOfflineHtml } = await library();
  const html = createOfflineHtml(introPack);
  assert.match(html, /<!doctype html>/i);
  assert.match(html, /connect-src 'none'/);
  assert.match(html, /default-src 'none'/);
  assert.doesNotMatch(html, /\b(?:src|href)\s*=\s*["'](?:https?:|\/\/)/i);
  assert.doesNotMatch(html, /\b(?:fetch|XMLHttpRequest|WebSocket|sendBeacon|importScripts)\s*\(/);
  const embedded = html.match(/<script type="application\/json" id="pack-data">([\s\S]*?)<\/script>/)[1];
  assert.deepEqual(JSON.parse(embedded), introPack);
  assert.doesNotMatch(embedded, /</);
  assert.match(html, /aria-live="polite"/);
  assert.match(html, /type="button"/);
  assert.match(html, /CC0-1.0/);
});
