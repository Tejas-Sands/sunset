# Independent SUNSET contract review

Reviewed `projects/sunset/contracts/sunset/src/lib.rs` and `host.rs`, the native tests, compiled-Wasm host-double tests, and relevant design comments on 1 November 2026. Review was read-only except for this report. The architecture agent made the fixes described below after receiving findings.

## Result

No remaining P0/P1 defect was identified in the final source reviewed. Two issues were reported immediately: prohibited host imports broke every real view call, and public campaign creation allowed permanent exhaustion of the five campaign slots. The final source fixes the view dispatch and restricts campaign creation to the fixed configured owner. The permanent 100-account capacity remains an availability limitation described below.

This result covers static review, native execution, compilation, and compiled-Wasm execution against host doubles. **No NEAR Sandbox or live testnet lifecycle was run or verified.** In particular, real receipt execution, protocol Wasm compatibility, account solvency including deployed-code storage, and callback gas consumption remain integration gates.

## Findings and resolution

### P1 — view calls used prohibited transaction context imports — fixed

The original `host::run` unconditionally called `predecessor_account_id`, `attached_deposit`, `prepaid_gas`, and `used_gas` before method dispatch. NEAR prohibits these functions in view execution, so `get_config`, `get_campaign`, `get_account`, and `list_campaigns` would fail on real RPC despite passing native tests. This restriction is explicit in the [NEAR bindings specification](https://nomicon.io/RuntimeSpec/Components/BindingsSpec/).

Reported to the architecture agent and parent immediately. The architecture agent reproduced failures by making the compiled-Wasm host doubles reject those calls in view mode. Final `host.rs:90` classifies view methods before building their context, avoids those imports for views, and avoids state writes. I inspected the corrected source and independently reran the passing compiled-Wasm scenarios with these restrictions enabled.

### P2 — permanent campaign-slot exhaustion by arbitrary creators — mitigated

Originally, anyone could create a draft while `MAX_CAMPAIGNS` permanently limited the deployment to five records. There was no pruning or cancellation, and the unused storage allowance was withdrawable. Five unwanted drafts could block legitimate campaign creation at low retained storage cost.

Final `lib.rs:71` requires the fixed configured owner before any campaign creation. Initialization is private to the contract account, validates the owner account, and records it once. An unauthorized-creator native regression now covers the denial. This is a curated prototype: because the creator beneficiary remains the caller, all campaigns in this deployment pay that configured owner. That restriction should be reflected in the application and deployment instructions.

### P2 — permanent participant-slot exhaustion — retained demo limitation

`MAX_ACCOUNTS = 100` is global across the deployment. New contributor records persist after refunds and withdrawals, and there is no minimum economic contribution beyond one yoctoNEAR. While a campaign remains active, an adversary controlling enough valid accounts can consume the remaining registrations with tiny contributions plus the actual retained storage cost. The storage allowance's unused portion is withdrawable. Future legitimate accounts then cannot contribute, even in subsequent campaigns; registered accounts can continue operating.

This does not redirect escrow or prevent existing users from refunding or withdrawing, but it limits an untrusted public demonstration. The architecture agent retained it explicitly as finite demonstration capacity. For a curated demonstration, monitor and disclose the remaining capacity. A deployment advertised for unrestricted participation needs a deliberate registration policy; increasing the constant alone postpones the same issue.

## Accounting and authorization review

- Contributions distinguish economic amount from a new-account storage allowance. Accepted contributions are capped to the remaining target; excess becomes caller credit. Storage allowance surplus becomes payer credit, while actual serialized growth remains retained.
- `check_accounting` reconciles economic deposits plus storage deposits with retained storage, escrow, credits, pending withdrawals, and completed withdrawals after every successful mutation. Release moves escrow only to the fixed creator credit, once. Refunds credit only the calling contributor, once, and reduce escrow by that contribution.
- Reviewer approval binds to the exact computed agreement digest and named reviewer. Terms and beneficiaries have no mutation route. Disclosure intentionally needs only the correct committed key, not creator authority, and cannot redirect payout.
- Withdrawal moves credit into one pending operation before scheduling any transfer. The recipient is the same registered caller. The callback requires predecessor equal to current account, exactly one promise result, a ready success/failure outcome, and the matching still-pending operation ID. Confirmed failure restores credit once; success records payout once. Stale and duplicate callbacks cannot restore or pay again.
- If a callback fails, pending state remains and prevents another withdrawal. There is no implemented automatic result-based recovery. This favors avoiding duplicate payout, while leaving a real liveness limitation that operations must disclose.

Monetary additions, storage multiplication, operation IDs, and refund subtraction use checked arithmetic. Contribution target subtraction relies on the preserved invariant that total contributions never exceed the target. Release-time addition is safe for reachable states: creation checks `funding_deadline + release_window`, and funding occurs strictly before that deadline.

The Rust `State` methods are not generally transaction-atomic in memory: for example, contribution registration and some fields can change before a later checked addition returns an error. **Persistence safety relies on the wrapper:** `checked(execute(...))` aborts before save on an error, and a later host panic aborts the receipt. The Wasm test double restores its storage snapshot on exceptions. Do not reuse these methods elsewhere while assuming that an `Err` leaves the supplied `State` unchanged. The review found no path that deliberately saves a partially failed transition.

## Physical storage, deadlines, and host ABI

The 32-byte public key, boolean status flags, per-account contribution/refund arrays, pending amount, operation ID, and paid counters are physically present before release/refund/withdrawal completion. Those transitions alter fixed-width fields and create no new beneficiary record. The existing size-regression tests confirm no serialized growth along the tested release/withdrawal path. The record-bound test checks retained charges against serialized growth and bounded state size.

The storage calculation charges growth of the single Borsh value at the configured storage price. Initial state, the `STATE` key and record overhead, and deployed code are outside that incremental charge; the deployment account must separately fund those costs. Rewriting the same key does not add a fresh key overhead on each mutation.

Funding rejects contribution at equality with its deadline. Funded campaigns allow release strictly before `funded_at + release_window`; at equality, refunds become available. A released campaign never becomes refundable. Drafts cannot receive contributions.

The reviewed host declarations use the documented `u64` lengths, pointers and promise indices. Deposit and transfer values use live 16-byte little-endian buffers. Argument, method, account and amount buffers remain alive while their host calls read them. Register contents are copied before later calls reuse register 0; state is loaded after the callback-result read, so that read cannot replace the serialized state used for deserialization. Promise result codes match the documented pending/success/failure mapping. See the [NEAR economics ABI](https://nomicon.io/RuntimeSpec/Components/BindingsSpec/EconomicsAPI) and [promise ABI](https://nomicon.io/RuntimeSpec/Components/BindingsSpec/PromisesAPI).

The final scheduling wrapper also rechecks remaining gas immediately before creating the transfer and callback, after serializing/saving state. It reserves a 15-Tgas callback and requires a further scheduling margin. Host doubles report simulated gas and cannot prove this budget sufficient at maximum state size; measure it in Sandbox/testnet before claiming callback reliability.

The contract validates key commitment, not ciphertext/plaintext correspondence, rights ownership, artifact availability, or educational quality. A failed release transaction can still expose its submitted key. These are mechanism boundaries already acknowledged by the design, not guarantees supplied by the ledger.

## Independent verification

All cargo output was isolated with `CARGO_TARGET_DIR=/tmp/sunset-review-target`.

- `cargo test --locked --offline --manifest-path projects/sunset/contracts/sunset/Cargo.toml`: **10 passed** on the final owner-enabled source.
- `cargo fmt --manifest-path projects/sunset/contracts/sunset/Cargo.toml -- --check`: **passed**.
- `cargo build --release --target wasm32-unknown-unknown --locked --offline --manifest-path projects/sunset/contracts/sunset/Cargo.toml`: **passed** after the final owner change.
- `node projects/sunset/contracts/sunset/tests/wasm.test.mjs`: **3 passed**, executing the compiled binary with transactional host doubles and view restrictions. These tests are not Sandbox.
- The independently built Wasm equals `res/sunset_contract.wasm` byte for byte: **190,561 bytes**, SHA-256 `79a647abecd7f04e36d44dcd4b79f8310395e636f6165755e1a74d97887f4837`.

Reviewed source SHA-256 values:

- `lib.rs`: `3b8be30475bead773e5ed18b4e3c78f64feca1fa19f339d1794c50b4e271d3c2`
- `host.rs`: `272ed3d12ebb56ff2949e8d7e1c8dd76d11bff65f02ff3f8401a0f4f7a0249b3`

The next required evidence is a real Sandbox/testnet lifecycle with actual balances, storage funding, success and confirmed-failure withdrawals, maximum-state gas measurements, and a deliberately failed callback that remains pending. Keep deployment labeled upgradeable while its account retains upgrade authority.
