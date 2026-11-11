import {snapshot} from '../helpers/live-fixtures.mjs';
import {resources} from '../../src/lib/library.mjs';
import {prepareArtifact} from '../../src/lib/demo.mjs';
import {hashBytes} from '../../src/lib/pack.mjs';
import {RPC} from '../../src/lib/chain.mjs';

export async function browserFixture() {
  const pack = resources[0].pack, artifact = await prepareArtifact(pack), s = snapshot();
  const now = BigInt(Date.now()) * 1000000n;
  s.timestampNs = now.toString();
  Object.assign(s.campaigns[0], {id: pack.id, title: pack.title,
    manifest_uri: 'https://qa.sunset.example/resource/manifest.json', manifest_hash: artifact.manifestHash,
    plaintext_hash: artifact.plaintextHash, ciphertext_hash: artifact.ciphertextHash, key_commitment: artifact.keyCommitment,
    license_hash: await hashBytes(new TextEncoder().encode('CC0-1.0')),
    funding_deadline_ns: (now + 86400000000000n).toString(), release_window_ns: '86400000000000'});
  s.account.contributions[0].campaign_id = pack.id;
  const sponsor = s.account;
  s.account = null;
  const emptyAccount = id => ({schema_version: 1, account_id: id, registered: true,
    credit: '0', paid: '0', pending: null, contributions: []});
  return {snapshot: s, artifact, pack, rpc: RPC, accounts: {[sponsor.account_id]: sponsor,
    'shiftultra.testnet': emptyAccount('shiftultra.testnet'), 'reviewer.testnet': emptyAccount('reviewer.testnet')}};
}
