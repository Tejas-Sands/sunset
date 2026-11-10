import {conservation, MAX} from './ledger.mjs';

// Stored browser data is untrusted. Accounting equality alone is not a schema check.
const record = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const text = (value, max = 4096) => typeof value === 'string' && value.length <= max;
const account = value => text(value, 64) && /^[a-z0-9]+(?:[-_.][a-z0-9]+)*$/.test(value) && value.length >= 2;
const id = value => text(value, 48) && /^[a-z0-9-]+$/.test(value);
const hash = value => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
const time = value => Number.isSafeInteger(value) && value >= 0 && value <= 8.64e15;
const amount = value => typeof value === 'string' && value.length <= 39
  && /^(0|[1-9]\d*)$/.test(value) && BigInt(value) <= MAX;
const base64 = value => text(value, 8 * 1024 * 1024) && value.length > 0
  && value.length % 4 === 0 && /^[A-Za-z0-9+/]*={0,2}$/.test(value);
function check(ok) { if (!ok) throw Error('Saved rehearsal data is incomplete or invalid.'); }
function moneyMap(value, max) {
  check(record(value) && Object.keys(value).length <= max);
  check(Object.entries(value).every(([key, value]) => account(key) && amount(value)));
}

export function validateRehearsalData(value) {
  check(record(value) && value.schema === 1 && Number.isSafeInteger(value.offset)
    && time(Date.now() + value.offset));
  const {ledger, artifacts} = value;
  check(record(ledger) && ledger.version === 1 && record(artifacts));
  check(Array.isArray(ledger.campaigns) && ledger.campaigns.length >= 1 && ledger.campaigns.length <= 5);
  check(Array.isArray(ledger.grants) && ledger.grants.length <= 20);
  check(Array.isArray(ledger.events) && ledger.events.length <= 10000);
  check(amount(ledger.deposits) && amount(ledger.withdrawn));
  moneyMap(ledger.credits, 1000);
  const campaignIds = new Set();
  for (const c of ledger.campaigns) {
    check(record(c) && id(c.id) && !campaignIds.has(c.id));
    campaignIds.add(c.id);
    check(text(c.title, 100) && c.title.length > 0 && (c.description === undefined || text(c.description)));
    check(account(c.creator) && account(c.reviewer) && c.creator !== c.reviewer);
    check(['draft', 'active', 'released'].includes(c.status) && text(c.digest));
    check(amount(c.target) && BigInt(c.target) > 0n && amount(c.raised) && amount(c.escrow));
    check(BigInt(c.escrow) <= BigInt(c.raised) && BigInt(c.raised) <= BigInt(c.target));
    check(time(c.fundingDeadline) && time(c.releaseWindow) && c.releaseWindow > 0
      && (c.fundedAt === null || time(c.fundedAt)));
    check(['keyCommitment', 'plaintextHash', 'ciphertextHash', 'manifestHash'].every(k => hash(c[k])));
    check(c.publicKey === null || (base64(c.publicKey) && c.publicKey.length === 44));
    if (c.status === 'released') check(c.publicKey !== null && c.escrow === '0');
    moneyMap(c.contributions, 100);
    check(record(c.refunded) && Object.entries(c.refunded).every(([key, value]) =>
      account(key) && Object.hasOwn(c.contributions, key) && typeof value === 'boolean'));
    check(c.manifestUri === undefined || text(c.manifestUri, 2048));
    if (c.steward != null) {
      const token = c.steward;
      check(record(token) && token.tokenId === c.id && account(token.ownerId) && text(token.mirrorUri, 2048)
        && Number.isSafeInteger(token.revision) && token.revision >= 0);
      check(Array.isArray(token.history) && token.history.length <= 200);
      check(token.history.every(h => record(h) && text(h.type, 100) && account(h.owner)
        && time(h.time) && (h.uri === undefined || text(h.uri, 2048))));
    }
    const a = artifacts[c.id];
    check(record(a) && record(a.manifest) && [1, 2].includes(a.manifest.schema) && id(a.manifest.packId));
    check(base64(a.envelope) && (a.key === undefined || a.key === null || a.key === ''
      || (base64(a.key) && a.key.length === 44)));
    check(a.manifestText === undefined || text(a.manifestText, 65536));
    check(['manifestHash', 'plaintextHash', 'ciphertextHash', 'keyCommitment'].every(k => hash(a[k]) && a[k] === c[k]));
  }
  const grantIds = new Set();
  for (const g of ledger.grants) {
    check(record(g) && id(g.id) && !grantIds.has(g.id));
    grantIds.add(g.id);
    check([g.sponsor, g.provider, g.approver].every(account) && text(g.purpose, 200));
    check(amount(g.unitPrice) && BigInt(g.unitPrice) > 0n && amount(g.budget) && amount(g.remaining)
      && BigInt(g.remaining) <= BigInt(g.budget));
    check(time(g.expiresAt) && typeof g.refunded === 'boolean' && Array.isArray(g.claims) && g.claims.length <= 100);
    check(g.claims.every(c => record(c) && id(c.id) && Number.isSafeInteger(c.units)
      && c.units > 0 && c.units <= 1000 && hash(c.evidence) && amount(c.amount)));
  }
  check(ledger.events.every(e => record(e) && text(e.id, 100) && text(e.type, 100)
    && text(e.actor, 100) && text(e.details) && time(e.time)));
  check(conservation(ledger));
  return value;
}

// Protect ordinary stale-tab saves. This is not an atomic multi-process lock.
export function commitRehearsal(storage, expectedRaw, nextData) {
  validateRehearsalData(nextData);
  if (storage.getItem('sunset-rehearsal-v1') !== expectedRaw) {
    throw Error('The saved rehearsal changed in another tab. Keep any local backups, then reload to use the latest data.');
  }
  const serialized = JSON.stringify(nextData);
  storage.setItem('sunset-rehearsal-v1', serialized);
  return serialized;
}
