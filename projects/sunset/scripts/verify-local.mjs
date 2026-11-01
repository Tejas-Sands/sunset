import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { access, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { base64ToBytes, bytesToBase64, seedDemo } from '../src/lib/demo.mjs';
import { introPack, keyCommitment } from '../src/lib/pack.mjs';
import { initializeStewardship, setMirror, transferStewardship } from '../src/lib/stewardship.mjs';
import {
  approveClaim, campaignState, conservation, contribute, refund, refundGrant,
  release, toYocto, withdraw,
} from '../src/lib/ledger.mjs';

// Real local APIs and a separate recovery process; no HTTP server, DOM or protocol doubles.
const checks = [];
const directory = await mkdtemp(join(tmpdir(), 'sunset-local-verification-'));
try {
  const demo = await seedDemo();
  const ledger = demo.ledger;
  const now = Date.now();
  assert.deepEqual(ledger.campaigns.map(campaign => campaignState(campaign, now)), ['active', 'refundable', 'released']);
  assert.equal(conservation(ledger), true);
  checks.push('seeded states');

  const lantern = ledger.campaigns.find(campaign => campaign.id === 'lantern-trail');
  const accepted = contribute(ledger, lantern.id, 'grove.testnet', toYocto('3'), now);
  assert.equal(accepted, '1600000000000000000000000');
  assert.equal(lantern.raised, '8000000000000000000000000');
  assert.equal(ledger.credits['grove.testnet'], '1400000000000000000000000');
  assert.equal(conservation(ledger), true);
  checks.push('capped contribution and change');

  const backupFile = join(directory, 'private-release-backup.json');
  const artifactFile = join(directory, 'artifact.json');
  const artifact = { ...demo.artifacts[lantern.id] };
  await writeFile(backupFile, JSON.stringify({ keyBase64: artifact.key, manifestHash: artifact.manifestHash }), { mode: 0o600 });
  delete artifact.key;
  delete demo.artifacts[lantern.id].key;
  await writeFile(artifactFile, JSON.stringify(artifact), { mode: 0o600 });
  assert.equal(Object.hasOwn(artifact, 'key'), false);

  const offlineFile = join(directory, 'offline-game.html');
  const recoveryScript = fileURLToPath(new URL('./recover-pack.mjs', import.meta.url));
  const recovered = spawnSync(process.execPath, [recoveryScript, artifactFile, backupFile, offlineFile], {
    cwd: directory, stdio: 'ignore', timeout: 30_000,
  });
  assert.ifError(recovered.error);
  assert.equal(recovered.status, 0, 'independent recovery process failed');
  const html = await readFile(offlineFile, 'utf8');
  const embedded = html.match(/<script type="application\/json" id="pack-data">([^]*?)<\/script>/);
  assert.ok(embedded, 'recovered game must contain its complete pack');
  assert.deepEqual(JSON.parse(embedded[1]), introPack);
  checks.push('retained-file recovery in a separate process without a website');

  const retained = JSON.parse(await readFile(backupFile, 'utf8'));
  const badKey = base64ToBytes(retained.keyBase64);
  badKey[0] ^= 1;
  const corruptBackup = join(directory, 'corrupt-backup.json');
  const rejectedOutput = join(directory, 'must-not-exist.html');
  await writeFile(corruptBackup, JSON.stringify({ ...retained, keyBase64: bytesToBase64(badKey) }), { mode: 0o600 });
  const rejected = spawnSync(process.execPath, [recoveryScript, artifactFile, corruptBackup, rejectedOutput], {
    cwd: directory, stdio: 'ignore', timeout: 30_000,
  });
  assert.ifError(rejected.error);
  assert.equal(rejected.status, 1, 'corrupted backup was not rejected by the recovery process');
  await assert.rejects(access(rejectedOutput), { code: 'ENOENT' });
  checks.push('corrupted private backup rejected without output');

  // Keep an independent branch to test the same funded campaign missing its release.
  const missedRelease = structuredClone(ledger);
  const commitment = await keyCommitment(base64ToBytes(retained.keyBase64));
  assert.equal(commitment, lantern.keyCommitment);
  release(ledger, lantern.id, commitment, retained.keyBase64, now + 1);
  assert.equal(lantern.publicKey, retained.keyBase64);
  assert.equal(ledger.credits['maker.testnet'], '16000000000000000000000000');
  assert.throws(() => release(ledger, lantern.id, commitment, retained.keyBase64, now + 2));
  assert.throws(() => refund(ledger, lantern.id, 'grove.testnet', now + lantern.releaseWindow + 1));
  assert.equal(conservation(ledger), true);
  checks.push('independent retained-key release credits creator exactly once');

  initializeStewardship(ledger);
  assert.equal(lantern.steward.ownerId, 'maker.testnet');
  const originalToken = lantern.steward;
  initializeStewardship(ledger);
  assert.equal(lantern.steward, originalToken, 'initialization must not mint a second token');
  const fixedTerms = JSON.stringify({
    target: lantern.target, creator: lantern.creator, key: lantern.publicKey,
    plaintextHash: lantern.plaintextHash, ciphertextHash: lantern.ciphertextHash,
    manifestHash: lantern.manifestHash, escrow: lantern.escrow, credits: ledger.credits,
  });
  setMirror(ledger, lantern.id, 'maker.testnet', 'https://example.org/original/manifest.json', now + 2);
  transferStewardship(ledger, lantern.id, 'maker.testnet', 'library.testnet', now + 3);
  assert.equal(lantern.steward.ownerId, 'library.testnet');
  assert.equal(lantern.steward.mirrorUri, lantern.manifestUri || '');
  assert.throws(() => setMirror(ledger, lantern.id, 'maker.testnet', 'https://example.org/old-owner/manifest.json', now + 4));
  setMirror(ledger, lantern.id, 'library.testnet', 'https://example.org/new-owner/manifest.json', now + 4);
  assert.equal(lantern.steward.mirrorUri, 'https://example.org/new-owner/manifest.json');
  assert.equal(JSON.stringify({
    target: lantern.target, creator: lantern.creator, key: lantern.publicKey,
    plaintextHash: lantern.plaintextHash, ciphertextHash: lantern.ciphertextHash,
    manifestHash: lantern.manifestHash, escrow: lantern.escrow, credits: ledger.credits,
  }), fixedTerms);
  assert.equal(conservation(ledger), true);
  checks.push('one stewardship token transfers maintenance authority without changing funds or access');

  const river = ledger.campaigns.find(campaign => campaign.id === 'river-routes');
  assert.equal(refund(ledger, river.id, 'grove.testnet', now), '2400000000000000000000000');
  assert.throws(() => refund(ledger, river.id, 'grove.testnet', now));
  assert.throws(() => release(ledger, river.id, river.keyCommitment, retained.keyBase64, now));
  assert.equal(conservation(ledger), true);
  checks.push('underfunded refund excludes release and duplicate refund');

  const expired = missedRelease.campaigns.find(campaign => campaign.id === lantern.id);
  const expiry = expired.fundedAt + expired.releaseWindow;
  assert.equal(campaignState(expired, expiry - 1), 'funded');
  assert.equal(campaignState(expired, expiry), 'refundable');
  assert.throws(() => release(missedRelease, expired.id, commitment, retained.keyBase64, expiry));
  assert.equal(refund(missedRelease, expired.id, 'grove.testnet', expiry), '5600000000000000000000000');
  assert.equal(refund(missedRelease, expired.id, 'cedar.testnet', expiry), '2400000000000000000000000');
  assert.throws(() => refund(missedRelease, expired.id, 'grove.testnet', expiry));
  assert.equal(expired.escrow, '0');
  assert.equal(conservation(missedRelease), true);
  checks.push('funded missed-release refund at the exclusive deadline');

  const grant = ledger.grants.find(item => item.id === 'village-library');
  approveClaim(ledger, grant.id, 'verified-session', 3, lantern.plaintextHash, 'teacher.testnet', now);
  assert.equal(ledger.credits['library.testnet'], '600000000000000000000000');
  assert.throws(() => approveClaim(ledger, grant.id, 'verified-session', 3, lantern.plaintextHash, 'teacher.testnet', now));
  assert.throws(() => approveClaim(ledger, grant.id, 'overspend', 8, lantern.plaintextHash, 'teacher.testnet', now));
  refundGrant(ledger, grant.id, grant.expiresAt);
  assert.equal(grant.remaining, '0');
  assert.equal(ledger.credits['grove.testnet'], '5200000000000000000000000');
  assert.equal(conservation(ledger), true);
  for (const [account, amount] of Object.entries(ledger.credits)) {
    if (amount === '0') continue;
    withdraw(ledger, account, amount, grant.expiresAt + 1);
    assert.equal(ledger.credits[account], '0');
    assert.throws(() => withdraw(ledger, account, amount, grant.expiresAt + 2));
    assert.equal(conservation(ledger), true);
  }
  assert.equal(ledger.deposits, '21800000000000000000000000');
  assert.equal(ledger.withdrawn, '21800000000000000000000000');
  assert.ok(ledger.campaigns.every(campaign => campaign.escrow === '0'));
  checks.push('approved budget claim, expired remainder and withdrawals conserve all deposits');

  console.log(`Local rehearsal: ${checks.length} workflow scenarios passed; 21.8 simulated NEAR conserved.`);
  console.log('Retained files recovered the exact five-question pack without a website. Browser and NEAR protocol execution remain unverified.');
} catch (error) {
  console.error(`Local verification failed: ${error.message}`);
  process.exitCode = 1;
} finally {
  await rm(directory, { recursive: true, force: true });
}
