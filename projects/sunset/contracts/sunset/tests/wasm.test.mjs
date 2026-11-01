import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

// Executes the compiled ABI with transactional host doubles. This is not NEAR Sandbox.
const wasm = await WebAssembly.compile(await readFile(new URL('../res/sunset_contract.wasm', import.meta.url)));
const contract = 'sunset.testnet';
const accountStorage = 10_000_000_000_000_000_000_000n;
const campaignStorage = 50_000_000_000_000_000_000_000n;
const key = Buffer.alloc(32, 7);
const commitment = createHash('sha256').update('SUNSET:KEY:1:').update(key).digest('hex');

function runtime() {
  let storage = new Map();
  return {
    async call(method, args = {}, { caller = contract, now = 1n, deposit = 0n, result, resultData = 'false', resultsCount, gas = 100_000_000_000_000n } = {}) {
      const registers = new Map();
      const previous = new Map(storage);
      const promises = [];
      const logs = [];
      let instance;
      let response;
      let returnedPromise;
      const isView = method.startsWith('get_') || method === 'list_campaigns' || ['nft_token', 'nft_metadata', 'nft_total_supply', 'nft_tokens', 'nft_supply_for_owner', 'nft_tokens_for_owner'].includes(method);
      const transactionOnly = () => { if (isView) throw new Error('host function prohibited in NEAR view'); };
      const bytes = (pointer, length) => Buffer.from(instance.exports.memory.buffer, Number(pointer), Number(length));
      const value = (pointer, length) => Buffer.from(bytes(pointer, length));
      const set = (id, data) => registers.set(id, Buffer.from(data));
      const amountAt = pointer => {
        const data = bytes(pointer, 16n);
        return data.readBigUInt64LE(0) + (data.readBigUInt64LE(8) << 64n);
      };
      const env = {
        input: id => set(id, JSON.stringify(args)),
        register_len: id => BigInt(registers.get(id)?.length ?? -1),
        read_register: (id, pointer) => bytes(pointer, BigInt(registers.get(id).length)).set(registers.get(id)),
        current_account_id: id => set(id, contract),
        predecessor_account_id: id => { transactionOnly(); set(id, caller); },
        attached_deposit: pointer => {
          transactionOnly();
          const out = bytes(pointer, 16n);
          out.writeBigUInt64LE(deposit & ((1n << 64n) - 1n), 0);
          out.writeBigUInt64LE(deposit >> 64n, 8);
        },
        block_timestamp: () => now,
        prepaid_gas: () => { transactionOnly(); return gas; },
        used_gas: () => { transactionOnly(); return 0n; },
        sha256: (length, pointer, id) => set(id, createHash('sha256').update(value(pointer, length)).digest()),
        storage_read: (length, pointer, id) => {
          const stored = storage.get(value(pointer, length).toString('hex'));
          if (!stored) return 0n;
          set(id, stored);
          return 1n;
        },
        storage_write: (length, pointer, dataLength, dataPointer, id) => {
          transactionOnly();
          const name = value(pointer, length).toString('hex');
          const old = storage.get(name);
          if (old) set(id, old);
          storage.set(name, value(dataPointer, dataLength));
          return old ? 1n : 0n;
        },
        value_return: (length, pointer) => { response = JSON.parse(value(pointer, length).toString()); },
        panic_utf8: (length, pointer) => { throw new Error(value(pointer, length).toString()); },
        log_utf8: (length, pointer) => { transactionOnly(); logs.push(value(pointer, length).toString()); },
        promise_results_count: () => resultsCount ?? (result === undefined ? 0n : 1n),
        promise_result: (_index, id) => {
          if (result === undefined) return 0n;
          if (!result) return 2n;
          set(id, resultData);
          return 1n;
        },
        promise_batch_create: (length, pointer) => {
          promises.push({ receiver: value(pointer, length).toString() });
          return BigInt(promises.length - 1);
        },
        promise_batch_action_transfer: (index, pointer) => { promises[Number(index)].transfer = amountAt(pointer); },
        promise_batch_then: (previousIndex, length, pointer) => {
          promises.push({ receiver: value(pointer, length).toString(), after: previousIndex });
          return BigInt(promises.length - 1);
        },
        promise_batch_action_function_call: (index, nameLength, namePointer, argsLength, argsPointer, amountPointer, callbackGas) => {
          Object.assign(promises[Number(index)], {
            method: value(namePointer, nameLength).toString(), args: JSON.parse(value(argsPointer, argsLength).toString()),
            deposit: amountAt(amountPointer), gas: callbackGas,
          });
        },
        promise_return: index => { returnedPromise = index; },
      };
      instance = await WebAssembly.instantiate(wasm, { env });
      try {
        instance.exports[method]();
        return { response, promises, returnedPromise, logs };
      } catch (error) {
        storage = previous;
        throw error;
      }
    },
    size: () => [...storage.values()].reduce((sum, item) => sum + item.length, 0),
  };
}

function terms(id = 'pack', target = '100') {
  return {
    id, title: 'Original arithmetic pack', reviewer: 'reviewer.testnet', manifest_uri: 'https://example.test/pack.json',
    manifest_hash: '01'.repeat(32), plaintext_hash: '02'.repeat(32), ciphertext_hash: '03'.repeat(32),
    key_commitment: commitment, license_hash: '04'.repeat(32), target, funding_deadline_ns: '100', release_window_ns: '20',
  };
}

async function active(target = '100') {
  const vm = runtime();
  await vm.call('new', { owner: 'creator.testnet' });
  const { response } = await vm.call('create_campaign', terms('pack', target), { caller: 'creator.testnet', deposit: campaignStorage });
  await vm.call('approve_campaign', { id: 'pack', agreement_digest: response.agreement_digest }, { caller: 'reviewer.testnet', now: 2n });
  return vm;
}

test('compiled Wasm exports only the intended callable ABI and guards initialization', async () => {
  const names = WebAssembly.Module.exports(wasm).filter(entry => entry.kind === 'function').map(entry => entry.name).sort();
  assert.deepEqual(names, ['approve_campaign', 'claim_refund', 'contribute', 'create_campaign', 'get_account', 'get_campaign', 'get_config', 'list_campaigns', 'new', 'on_withdraw_complete', 'publish_release', 'withdraw', 'nft_transfer', 'nft_transfer_call', 'nft_resolve_transfer', 'set_mirror', 'nft_token', 'nft_metadata', 'nft_total_supply', 'nft_tokens', 'nft_supply_for_owner', 'nft_tokens_for_owner'].sort());
  const vm = runtime();
  await assert.rejects(vm.call('new', {}, { caller: 'attacker.testnet' }), /private/);
  await vm.call('new', { owner: 'creator.testnet' });
  await assert.rejects(vm.call('new'), /already initialized/);
});

test('compiled Wasm rejects creator as reviewer without registering or charging storage', async () => {
  const vm = runtime();
  await vm.call('new', { owner: 'creator.testnet' });
  const size = vm.size();
  await assert.rejects(vm.call('create_campaign', { ...terms('self-reviewed'), reviewer: 'creator.testnet' }, { caller: 'creator.testnet', deposit: campaignStorage }), /reviewer must differ/);
  const config = (await vm.call('get_config')).response;
  assert.equal(config.campaign_count, 0);
  assert.equal(config.account_count, 0);
  assert.equal(config.storage_deposits, '0');
  assert.equal(config.storage_retained, '0');
  assert.equal(vm.size(), size);
  const created = await vm.call('create_campaign', terms(), { caller: 'creator.testnet', deposit: campaignStorage });
  assert.equal(created.response.reviewer, 'reviewer.testnet');
});

function events(result) {
  return result.logs.map(log => {
    assert.ok(log.startsWith('EVENT_JSON:'));
    const event = JSON.parse(log.slice('EVENT_JSON:'.length));
    assert.equal(event.standard, 'nep171');
    assert.equal(event.version, '1.2.0');
    return event;
  });
}
async function released() {
  const vm = await active('50');
  await vm.call('contribute', { id: 'pack', amount: '50' }, { caller: 'buyer.testnet', now: 3n, deposit: 50n + accountStorage });
  await vm.call('publish_release', { id: 'pack', key_base64: key.toString('base64') }, { now: 4n });
  return vm;
}
async function tokenView(vm) { return (await vm.call('nft_token', { token_id: 'pack' })).response; }
async function mirror(vm, caller, uri = 'https://mirror.test/manifest.json') {
  return vm.call('set_mirror', { token_id: 'pack', mirror_uri: uri }, { caller, deposit: 1n });
}
async function transferCall(vm, caller, receiver) {
  return vm.call('nft_transfer_call', { token_id: 'pack', receiver_id: receiver, msg: 'inspect', approval_id: null, memo: null }, { caller, deposit: 1n });
}
async function resolve(vm, started, resultData = 'false', result = true) {
  const callback = started.promises[1];
  return vm.call(callback.method, callback.args, { result, resultData });
}

test('compiled Wasm mints one stewardship on release, exports metadata, and enumerates only released tokens', async () => {
  const vm = await active('50');
  assert.equal((await vm.call('nft_total_supply')).response, '0');
  assert.equal(await tokenView(vm), null);
  assert.equal((await vm.call('nft_token', { token_id: 'missing' })).response, null);
  await assert.rejects(vm.call('nft_token', { token_id: 1 }), /string/);
  await vm.call('contribute', { id: 'pack', amount: '50' }, { caller: 'buyer.testnet', now: 3n, deposit: 50n + accountStorage });
  const size = vm.size();
  const release = await vm.call('publish_release', { id: 'pack', key_base64: key.toString('base64') }, { now: 4n });
  assert.deepEqual(events(release).map(e => e.event), ['nft_mint']);
  assert.deepEqual(events(release)[0].data, [{ owner_id: 'creator.testnet', token_ids: ['pack'] }]);
  assert.equal((await vm.call('publish_release', { id: 'pack', key_base64: key.toString('base64') }, { now: 5n })).logs.length, 0);
  assert.equal(vm.size(), size);
  const token = await tokenView(vm);
  assert.equal(token.token_id, 'pack');
  assert.equal(token.owner_id, 'creator.testnet');
  assert.equal(token.metadata.reference_hash, Buffer.alloc(32, 1).toString('base64'));
  assert.equal(token.metadata.copies, 1);
  assert.equal((await vm.call('nft_metadata')).response.spec, 'nft-1.0.0');
  assert.equal((await vm.call('nft_total_supply')).response, '1');
  assert.equal((await vm.call('nft_supply_for_owner', { account_id: 'creator.testnet' })).response, '1');
  assert.equal((await vm.call('nft_supply_for_owner', { account_id: 'absent.testnet' })).response, '0');
  assert.deepEqual((await vm.call('nft_tokens', { from_index: null, limit: null })).response, [token]);
  assert.deepEqual((await vm.call('nft_tokens_for_owner', { account_id: 'creator.testnet', from_index: '1', limit: 1 })).response, []);
  await assert.rejects(vm.call('nft_tokens', { limit: 0 }), /positive/);
  await assert.rejects(vm.call('nft_tokens', { from_index: 0 }), /string/);
  await assert.rejects(vm.call('nft_tokens', { unknown: true }), /unknown/);
});

test('compiled Wasm transfers a real stewardship right with fixed storage and a separate security reserve', async () => {
  const vm = await released();
  const size = vm.size();
  const before = (await vm.call('get_config')).response;
  const receiver = 'a'.repeat(64);
  for (const deposit of [0n, 2n]) await assert.rejects(vm.call('nft_transfer', { token_id: 'pack', receiver_id: receiver }, { caller: 'creator.testnet', deposit }), /exactly 1/);
  await assert.rejects(vm.call('nft_transfer', { token_id: 'pack', receiver_id: receiver }, { caller: 'attacker.testnet', deposit: 1n }), /owner/);
  await assert.rejects(mirror(vm, 'attacker.testnet'), /owner/);
  await assert.rejects(mirror(vm, 'creator.testnet', 'javascript:alert(1)'), /HTTPS/);
  await mirror(vm, 'creator.testnet', `https://mirror.test/${'p'.repeat(492)}`);
  const transferred = await vm.call('nft_transfer', { token_id: 'pack', receiver_id: receiver, memo: 'custody', approval_id: 7 }, { caller: 'creator.testnet', deposit: 1n });
  assert.deepEqual(events(transferred).map(e => e.event), ['nft_transfer', 'nft_metadata_update']);
  assert.equal(events(transferred)[0].data[0].memo, 'custody');
  const token = await tokenView(vm);
  assert.equal(token.owner_id, receiver);
  assert.equal(JSON.parse(token.metadata.extra).mirror_uri, 'https://example.test/pack.json');
  assert.equal((await vm.call('get_account', { account_id: receiver })).response.registered, false);
  const after = (await vm.call('get_config')).response;
  for (const field of ['account_count', 'storage_retained', 'storage_deposits', 'economic_deposits', 'withdrawn']) assert.equal(after[field], before[field]);
  assert.equal(after.security_deposits, '2');
  assert.equal(vm.size(), size);
  await assert.rejects(mirror(vm, 'creator.testnet'), /owner/);
  assert.equal((await vm.call('get_campaign', { id: 'pack' })).response.creator, 'creator.testnet');
});

test('compiled Wasm transfer_call returns on receiver rejection, error, malformed or excessive results', async () => {
  for (const [result, resultData] of [[true, 'true'], [false, ''], [true, ''], [true, 'null'], [true, '"false"'], [true, 'false '], [true, Buffer.from([255])], [true, Buffer.alloc(100_000, 97)]]) {
    const vm = await released();
    const size = vm.size();
    const started = await transferCall(vm, 'creator.testnet', 'receiver.testnet');
    assert.equal(started.returnedPromise, 1n);
    assert.equal(started.promises[0].receiver, 'receiver.testnet');
    assert.equal(started.promises[0].method, 'nft_on_transfer');
    assert.equal(started.promises[0].deposit, 0n);
    assert.deepEqual(started.promises[0].args, { sender_id: 'creator.testnet', previous_owner_id: 'creator.testnet', token_id: 'pack', msg: 'inspect' });
    assert.equal(started.promises[1].receiver, contract);
    assert.equal(started.promises[1].gas, 15_000_000_000_000n);
    await mirror(vm, 'receiver.testnet');
    const resolved = await resolve(vm, started, resultData, result);
    assert.equal(resolved.response, false);
    assert.deepEqual(events(resolved).map(e => e.event), ['nft_transfer', 'nft_metadata_update']);
    const token = await tokenView(vm);
    assert.equal(token.owner_id, 'creator.testnet');
    assert.equal(JSON.parse(token.metadata.extra).mirror_uri, 'https://example.test/pack.json');
    assert.equal(vm.size(), size);
  }
});

test('compiled Wasm acceptance preserves receiver mirror and authenticates resolver callbacks', async () => {
  const vm = await released();
  const args = { token_id: 'pack', receiver_id: 'receiver.testnet', msg: '' };
  await assert.rejects(vm.call('nft_transfer_call', args, { caller: 'creator.testnet', deposit: 1n, gas: 1n }), /40 Tgas/);
  assert.equal((await tokenView(vm)).owner_id, 'creator.testnet');
  const started = await transferCall(vm, 'creator.testnet', 'receiver.testnet');
  const callback = started.promises[1];
  await assert.rejects(vm.call(callback.method, callback.args, { caller: 'attacker.testnet', result: true }), /private/);
  await assert.rejects(vm.call(callback.method, callback.args, { resultsCount: 0n }), /one promise result/);
  await assert.rejects(vm.call(callback.method, callback.args, { resultsCount: 1n }), /not ready/);
  await mirror(vm, 'receiver.testnet');
  assert.equal((await resolve(vm, started)).response, true);
  assert.equal((await tokenView(vm)).owner_id, 'receiver.testnet');
  assert.equal(JSON.parse((await tokenView(vm)).metadata.extra).mirror_uri, 'https://mirror.test/manifest.json');
});

test('compiled Wasm nested transfer callbacks preserve onward owners and reset mirrors on each return', async () => {
  const vm = await released();
  const outer = await transferCall(vm, 'creator.testnet', 'receiver.testnet');
  const inner = await transferCall(vm, 'receiver.testnet', 'next.testnet');
  await mirror(vm, 'next.testnet');
  assert.equal((await resolve(vm, inner)).response, true);
  assert.equal((await resolve(vm, outer, 'true')).response, true);
  assert.equal((await tokenView(vm)).owner_id, 'next.testnet');
  assert.equal(JSON.parse((await tokenView(vm)).metadata.extra).mirror_uri, 'https://mirror.test/manifest.json');
  const returnOuter = await transferCall(vm, 'next.testnet', 'receiver.testnet');
  const returnInner = await transferCall(vm, 'receiver.testnet', 'last.testnet');
  await mirror(vm, 'last.testnet');
  assert.equal((await resolve(vm, returnInner, 'true')).response, false);
  assert.equal((await tokenView(vm)).owner_id, 'receiver.testnet');
  assert.equal(JSON.parse((await tokenView(vm)).metadata.extra).mirror_uri, 'https://example.test/pack.json');
  await mirror(vm, 'receiver.testnet');
  assert.equal((await resolve(vm, returnOuter, '', false)).response, false);
  assert.equal((await tokenView(vm)).owner_id, 'next.testnet');
  assert.equal(JSON.parse((await tokenView(vm)).metadata.extra).mirror_uri, 'https://example.test/pack.json');
});

test('compiled Wasm owner round trip can still be returned by an earlier receiver callback', async () => {
  const vm = await released();
  const started = await transferCall(vm, 'creator.testnet', 'receiver.testnet');
  await vm.call('nft_transfer', { token_id: 'pack', receiver_id: 'next.testnet' }, { caller: 'receiver.testnet', deposit: 1n });
  await vm.call('nft_transfer', { token_id: 'pack', receiver_id: 'receiver.testnet' }, { caller: 'next.testnet', deposit: 1n });
  await mirror(vm, 'receiver.testnet');
  assert.equal((await resolve(vm, started, 'true')).response, false);
  const token = await tokenView(vm);
  assert.equal(token.owner_id, 'creator.testnet');
  assert.equal(JSON.parse(token.metadata.extra).mirror_uri, 'https://example.test/pack.json');
});

test('compiled Wasm caps funding, reveals once, and routes native transfer through a private bounded callback', async () => {
  const vm = await active();
  await vm.call('contribute', { id: 'pack', amount: '80' }, { caller: 'buyer.testnet', now: 3n, deposit: 80n + accountStorage });
  await vm.call('contribute', { id: 'pack', amount: '40' }, { caller: 'buyer.testnet', now: 4n, deposit: 40n });
  const funded = (await vm.call('get_campaign', { id: 'pack' }, { now: 4n })).response;
  assert.equal(funded.total_contributed, '100');
  assert.equal(funded.state, 'Funded');
  const credit = (await vm.call('get_account', { account_id: 'creator.testnet' })).response.credit;
  const size = vm.size();
  await assert.rejects(vm.call('publish_release', { id: 'pack', key_base64: Buffer.alloc(32).toString('base64') }, { now: 5n }), /key mismatch/);
  const released = (await vm.call('publish_release', { id: 'pack', key_base64: key.toString('base64') }, { caller: 'reviewer.testnet', now: 5n })).response;
  assert.equal(released.state, 'Released');
  assert.equal(released.public_key_base64, key.toString('base64'));
  await vm.call('publish_release', { id: 'pack', key_base64: key.toString('base64') }, { now: 6n });
  assert.equal(BigInt((await vm.call('get_account', { account_id: 'creator.testnet' })).response.credit), BigInt(credit) + 100n);
  assert.equal(vm.size(), size);
  await assert.rejects(vm.call('withdraw', { amount: '100' }, { caller: 'creator.testnet', gas: 1n }), /40 Tgas/);
  const started = await vm.call('withdraw', { amount: '100' }, { caller: 'creator.testnet' });
  assert.equal(started.promises[0].receiver, 'creator.testnet');
  assert.equal(started.promises[0].transfer, 100n);
  assert.equal(started.returnedPromise, 1n);
  const callback = started.promises[1];
  assert.equal(callback.receiver, contract);
  assert.equal(callback.method, 'on_withdraw_complete');
  assert.equal(callback.deposit, 0n);
  assert.equal(callback.gas, 15_000_000_000_000n);
  await assert.rejects(vm.call(callback.method, callback.args, { caller: 'attacker.testnet', result: true }), /private/);
  await assert.rejects(vm.call('withdraw', { amount: '1' }, { caller: 'creator.testnet' }), /pending/);
  await vm.call(callback.method, callback.args, { result: true });
  await assert.rejects(vm.call(callback.method, callback.args, { result: true }), /completed/);
  assert.equal(vm.size(), size);
  assert.equal((await vm.call('get_account', { account_id: 'creator.testnet' })).response.paid, '100');
});

test('compiled Wasm refunds each expiration outcome and restores only confirmed failed transfers', async () => {
  for (const [target, expiry] of [['100', 100n], ['50', 23n]]) {
    const vm = await active(target);
    await vm.call('contribute', { id: 'pack', amount: '50' }, { caller: 'buyer.testnet', now: 3n, deposit: 50n + accountStorage });
    const before = BigInt((await vm.call('get_account', { account_id: 'buyer.testnet' })).response.credit);
    await assert.rejects(vm.call('claim_refund', { id: 'pack' }, { caller: 'buyer.testnet', now: expiry - 1n }), /not refundable/);
    await vm.call('claim_refund', { id: 'pack' }, { caller: 'buyer.testnet', now: expiry });
    await vm.call('claim_refund', { id: 'pack' }, { caller: 'buyer.testnet', now: expiry });
    assert.equal(BigInt((await vm.call('get_account', { account_id: 'buyer.testnet' })).response.credit), before + 50n);
    await assert.rejects(vm.call('publish_release', { id: 'pack', key_base64: key.toString('base64') }, { now: expiry }), /release expired|not funded/);
    const started = await vm.call('withdraw', { amount: '50' }, { caller: 'buyer.testnet' });
    const callback = started.promises[1];
    await assert.rejects(vm.call(callback.method, callback.args, { resultsCount: 0n }), /one promise result/);
    assert.notEqual((await vm.call('get_account', { account_id: 'buyer.testnet' })).response.pending, null);
    await vm.call(callback.method, callback.args, { result: false });
    const after = (await vm.call('get_account', { account_id: 'buyer.testnet' })).response;
    assert.equal(BigInt(after.credit), before + 50n);
    assert.equal(after.pending, null);
  }
});
