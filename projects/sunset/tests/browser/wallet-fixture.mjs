// Installed only by browser tests, before application code. Never imported by src/.
// The standard SDK injection API exercises the real UI without signing or writing to NEAR.
export function installWalletFixture(data, allowedOrigin) {
  if (location.origin !== allowedOrigin) return;
  const copy = value => JSON.parse(JSON.stringify(value));
  const add = (a, b) => (BigInt(a) + BigInt(b)).toString();
  const originalFetch = window.fetch.bind(window);
  const state = {...copy(data), connected: false, signer: 'sponsor.testnet', requests: [], receipts: {},
    reject: false, delay: 0, outage: false, errors: [], hostedManifest: null, hostedEnvelope: null, privateBackup: null};
  window.__sunsetQA = state;
  window.addEventListener('error', event => state.errors.push(event.message));
  window.addEventListener('unhandledrejection', event => state.errors.push(String(event.reason)));
  const account = id => state.accounts[id] ||= {schema_version: 1, account_id: id, registered: false,
    credit: '0', paid: '0', pending: null, contributions: []};
  const json = value => new Response(JSON.stringify(value), {headers: {'content-type': 'application/json'}});
  window.fetch = async (input, options) => {
    const url = typeof input === 'string' ? input : input.url;
    if (url === data.rpc) {
      if (state.outage) throw Error('Controlled RPC outage');
      if (state.delay) await new Promise(resolve => setTimeout(resolve, state.delay));
      const q = JSON.parse(options.body), s = state.snapshot;
      let result;
      if (q.method === 'status') result = {chain_id: 'testnet'};
      else if (q.method === 'block') result = {header: {hash: s.blockHash, height: s.height, timestamp_nanosec: s.timestampNs}};
      else if (q.method === 'tx') result = state.receipts[q.params.tx_hash];
      else if (q.params.request_type === 'view_account') result = {block_hash: s.blockHash, block_height: s.height, code_hash: s.codeHash};
      else {
        const args = JSON.parse(atob(q.params.args_base64));
        const value = {get_config: s.config, list_campaigns: s.campaigns,
          get_account: q.params.method_name === 'get_account' ? account(args.account_id) : undefined}[q.params.method_name];
        result = {block_hash: s.blockHash, block_height: s.height,
          result: Array.from(new TextEncoder().encode(JSON.stringify(value)))};
      }
      return json({jsonrpc: '2.0', id: q.id, result});
    }
    if (url.startsWith('https://qa.sunset.example/')) {
      if (url.endsWith('manifest.json')) return new Response(state.hostedManifest || state.artifact.manifestText);
      return new Response(state.hostedEnvelope || Uint8Array.from(atob(state.artifact.envelope), c => c.charCodeAt(0)));
    }
    if (url.includes('near-selector/') || url.includes('hot-connector/')) return json({version: '1.0.0', wallets: []});
    return originalFetch(input, options);
  };
  const createObjectURL = URL.createObjectURL.bind(URL);
  URL.createObjectURL = blob => {
    void blob.arrayBuffer().then(buffer => {
      const bytes = new Uint8Array(buffer);
      try {
        const text = new TextDecoder().decode(bytes), value = JSON.parse(text);
        if (value.ciphertext_path) state.hostedManifest = text;
        if (value.keyBase64) state.privateBackup = value;
      } catch { if (blob.type === 'application/octet-stream') state.hostedEnvelope = bytes; }
    });
    return createObjectURL(blob);
  };
  const wallet = {
    manifest: {id: 'sunset-qa-wallet', name: 'Controlled QA wallet', type: 'injected', version: '1.0.0',
      platform: ['browser'], executor: '', website: 'https://qa.sunset.example',
      description: 'Controlled frontend verification; no signatures.', permissions: {},
      icon: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"%3E%3Ccircle cx="12" cy="12" r="10" fill="%23e98764"/%3E%3C/svg%3E',
      features: {testnet: true, mainnet: false, signAndSendTransaction: true, signInWithoutAddKey: true}},
    getAccounts: async () => state.connected ? [{accountId: state.signer}] : [],
    signIn: async ({network}) => {
      if (network !== 'testnet') throw Error('Wrong controlled wallet network');
      state.connected = true;
      return [{accountId: state.signer}];
    },
    signOut: async () => { state.connected = false; },
    signAndSendTransaction: async request => {
      if (state.reject) throw Object.assign(Error('Explicit controlled rejection'), {code: 4001});
      state.requests.push(copy(request));
      const p = request.actions[0].params, args = p.args, a = account(request.signerId);
      const c = state.snapshot.campaigns.find(c => c.id === (args.id || args.token_id));
      if (!a.registered && ['create_campaign', 'contribute'].includes(p.methodName)) {
        a.registered = true; state.snapshot.config.account_count++;
      }
      if (p.methodName === 'approve_campaign') c.state = 'Active';
      if (p.methodName === 'contribute') {
        const accepted = BigInt(args.amount) < BigInt(c.target) - BigInt(c.total_contributed)
          ? BigInt(args.amount) : BigInt(c.target) - BigInt(c.total_contributed);
        c.total_contributed = add(c.total_contributed, accepted); c.escrow = add(c.escrow, accepted);
        const record = a.contributions.find(x => x.campaign_id === c.id);
        if (record) record.amount = add(record.amount, accepted);
        else a.contributions.push({campaign_id: c.id, amount: accepted.toString(), refunded: false});
        a.credit = add(a.credit, BigInt(args.amount) - accepted);
        if (c.total_contributed === c.target) {
          c.state = 'Funded'; c.funded_at_ns = state.snapshot.timestampNs;
          c.release_deadline_ns = add(c.funded_at_ns, c.release_window_ns);
        }
      }
      if (p.methodName === 'publish_release') {
        c.state = 'Released'; c.public_key_base64 = args.key_base64;
        const creator = account(c.creator); creator.credit = add(creator.credit, c.escrow); c.escrow = '0';
        c.stewardship = {token_id: c.id, owner_id: c.creator, mirror_uri: c.manifest_uri};
      }
      if (p.methodName === 'withdraw') { a.credit = (BigInt(a.credit) - BigInt(args.amount)).toString(); a.paid = add(a.paid, args.amount); a.pending = null; }
      if (p.methodName === 'claim_refund') {
        const contribution = a.contributions.find(x => x.campaign_id === c.id);
        a.credit = add(a.credit, contribution.amount); contribution.refunded = true;
        c.escrow = (BigInt(c.escrow) - BigInt(contribution.amount)).toString();
      }
      if (p.methodName === 'set_mirror') c.stewardship.mirror_uri = args.mirror_uri;
      if (p.methodName === 'nft_transfer') { c.stewardship.owner_id = args.receiver_id; c.stewardship.mirror_uri = c.manifest_uri; }
      if (p.methodName === 'create_campaign') {
        state.snapshot.campaigns.push({...args, schema_version: 1, creator: request.signerId, state: 'Draft',
          total_contributed: '0', escrow: '0', funded_at_ns: '0', release_deadline_ns: null,
          public_key_base64: null, stewardship: null, agreement_digest: 'f'.repeat(64)});
        state.snapshot.config.campaign_count++;
      }
      const hash = 'T'.repeat(43) + '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'[state.requests.length % 58];
      const result = {final_execution_status: 'FINAL', transaction: {hash, signer_id: request.signerId,
        receiver_id: request.receiverId, actions: [{FunctionCall: {method_name: p.methodName,
          args: btoa(JSON.stringify(args)), gas: p.gas, deposit: p.deposit}}]},
        transaction_outcome: {outcome: {status: {SuccessReceiptId: 'receipt'}}},
        status: {SuccessValue: ''}, receipts_outcome: [{outcome: {status: {SuccessValue: ''}}}]};
      state.receipts[hash] = result;
      return result;
    }
  };
  window.addEventListener('near-selector-ready', () => window.dispatchEvent(new CustomEvent('near-wallet-injected', {detail: wallet})));
}
