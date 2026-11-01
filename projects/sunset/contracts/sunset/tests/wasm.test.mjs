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
    async call(method, args = {}, { caller = contract, now = 1n, deposit = 0n, result, resultsCount, gas = 100_000_000_000_000n } = {}) {
      const registers = new Map();
      const previous = new Map(storage);
      const promises = [];
      let instance;
      let response;
      let returnedPromise;
      const isView = method.startsWith('get_') || method === 'list_campaigns';
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
          const name = value(pointer, length).toString('hex');
          const old = storage.get(name);
          if (old) set(id, old);
          storage.set(name, value(dataPointer, dataLength));
          return old ? 1n : 0n;
        },
        value_return: (length, pointer) => { response = JSON.parse(value(pointer, length).toString()); },
        panic_utf8: (length, pointer) => { throw new Error(value(pointer, length).toString()); },
        promise_results_count: () => resultsCount ?? (result === undefined ? 0n : 1n),
        promise_result: () => result === undefined ? 0n : result ? 1n : 2n,
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
        return { response, promises, returnedPromise };
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
  assert.deepEqual(names, ['approve_campaign', 'claim_refund', 'contribute', 'create_campaign', 'get_account', 'get_campaign', 'get_config', 'list_campaigns', 'new', 'on_withdraw_complete', 'publish_release', 'withdraw'].sort());
  const vm = runtime();
  await assert.rejects(vm.call('new', {}, { caller: 'attacker.testnet' }), /private/);
  await vm.call('new', { owner: 'creator.testnet' });
  await assert.rejects(vm.call('new'), /already initialized/);
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
