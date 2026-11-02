# SUNSET testnet contract

This is the bounded SUNSET sponsorship and public-release stewardship contract. It supports immediate capped contributions, reviewed key publication, both campaign refund outcomes, pull withdrawals, and one transferable stewardship NFT per successful public release. The token gives its current owner authority to choose a discovery mirror for the exact committed manifest. It grants no exclusive access, copyright, licensing, campaign editing, refund, escrow or payout authority. The reviewed pack remains an external artifact whose availability and quality depend on its declared reviewer and retained copies. There are no purchase orders, paid prerelease licenses, service vouchers, administrator payouts or upgrade methods.

`res/sunset_contract.wasm` is a real compiled artifact. Native Rust checks and compiled Wasm tests with transactional host doubles run locally. **NEAR Sandbox, protocol gas metering, wallet signing, real testnet deployment and actual transfer receipts have not been verified here.** The host doubles are not a network simulator. Do not present this artifact as deployed or mainnet reviewed.

The source uses NEAR's stable host ABI directly because this build environment has cached Rust serialization dependencies and no available `near-sdk`. Wasm hashes use NEAR's SHA-256 host. Native tests call the system OpenSSL SHA-256 binary; OpenSSL is not a Wasm dependency. The compiled ABI has 22 callable exports and no hidden test funding bypass. The NFT implementation follows [NEP-171 core and 1.2.0 events](https://github.com/near/NEPs/blob/master/neps/nep-0171.md), [NEP-177 metadata](https://github.com/near/NEPs/blob/master/neps/nep-0177.md), and [NEP-181 enumeration](https://github.com/near/NEPs/blob/master/neps/nep-0181.md). Approval management, royalties, sales and burning are not implemented.

The [2 November predeployment review](../../docs/CONTRACT_PREDEPLOY_REVIEW.md) fixed shared original/mirror URL validation and added maximum-capacity accounting coverage. Resource URLs now require lowercase ASCII DNS/punycode authorities, valid bounded ports, HTTPS and at most 512 UTF-8 bytes; credentials, fragments, controls, backslashes, IP/local hosts and malformed DNS labels are rejected. This validates syntax rather than resolution or availability.

**Fresh deployment required:** the stewardship fields change the Borsh state layout. `get_config.state_layout_version` is `2`; JSON campaign/account `schema_version` remains `1` with additive fields. No migration from the earlier sponsorship-only layout is supplied or claimed. No network deployment has occurred.

## Build and checks

The build script requires an already installed `rustc 1.96.0` compiler and preserves Cargo's locked, offline dependency resolution. The verified compiler is `rustc 1.96.0 (ac68faa20 2026-05-25)` with Cargo 1.96.0. The `wasm32-unknown-unknown` target and dependencies pinned in Cargo.lock must already be installed/cached; the script does not install a toolchain. It replaces ambient Rust flags with three canonical `--remap-path-prefix` flags: the contract directory becomes `/sunset-contract`, the Cargo cache root becomes `/cargo-cache`, and the exact compiler sysroot becomes `/rust-toolchain`. Unit-separator `CARGO_ENCODED_RUSTFLAGS` preserves paths containing spaces. Two builds from different source directories with separate target directories produce the same checked-in Wasm with these locked dependencies and this compiler; this is not a cross-compiler reproducibility claim. Exact evidence and the build-script digest are in `build-evidence.json`.

Use a current protocol-compatible Sandbox when performing network-runtime checks. [Nearcore 2.12 / protocol 84](https://github.com/near/nearcore/releases/tag/2.12.0) introduced the Wasmtime runtime and bulk-memory Wasm support; an older Sandbox can reject instructions emitted by a current Rust target.

```sh
CARGO_TARGET_DIR=/tmp/sunset-cargo-target cargo fmt --manifest-path projects/sunset/contracts/sunset/Cargo.toml --check
CARGO_TARGET_DIR=/tmp/sunset-cargo-target cargo clippy --offline --manifest-path projects/sunset/contracts/sunset/Cargo.toml --all-targets -- -D warnings
CARGO_TARGET_DIR=/tmp/sunset-cargo-target cargo test --offline --manifest-path projects/sunset/contracts/sunset/Cargo.toml
bash projects/sunset/contracts/sunset/scripts/build.sh
node --test --test-isolation=none projects/sunset/contracts/sunset/tests/wasm.test.mjs
```

The Node runner loads the actual copied Wasm, checks exact callable exports, enforces prohibited view-host access, and exercises release, deadline refunds, fixed-size settlement, native-transfer promises, NFT receiver promises, standard events and callbacks. NFT scenarios include acceptance, rejection, failed/malformed/oversized receiver results, nested callbacks and onward transfers. A failed withdrawal callback leaves pending credit locked until its result callback completes. These tests do not prove protocol gas costs, instrumented VM compatibility, or account balance settlement. Run actual Sandbox receipt scenarios before those claims.

## JSON ABI

Every method receives one JSON object. Unknown fields and missing required fields are rejected. Optional NFT fields can be omitted or null. All financial amounts, nanosecond timestamps, operation IDs, NFT supplies and pagination indices are **decimal strings**. NFT approval IDs, pagination limits and metadata timestamps are JSON numbers; metadata timestamps use Unix milliseconds. Campaign hashes are lowercase SHA-256 hex; NEP-177 reference hashes use base64. No mainnet account or deployment identity is supplied by this package.

| Method | Arguments | Attached deposit and authority |
| --- | --- | --- |
| `new` | `{owner}` | Zero; predecessor must be contract account; only once; owner is a valid adult creator account |
| `create_campaign` | Fields below | Exactly `50000000000000000000000` yoctoNEAR (0.05 NEAR) storage allowance; configured owner only, creator is predecessor |
| `approve_campaign` | `{id,agreement_digest}` | Zero; named reviewer only |
| `contribute` | `{id,amount}` | `amount` plus `10000000000000000000000` (0.01 NEAR) storage allowance if caller is not registered; otherwise exactly `amount` |
| `publish_release` | `{id,key_base64}` | Zero; any committed key holder, before release expiry |
| `claim_refund` | `{id}` | Zero; contributing predecessor, after effective campaign expiry |
| `withdraw` | `{amount}` | Zero; credit owner, no other pending operation; use at least 100 Tgas in wallet plans |
| `on_withdraw_complete` | `{account_id,operation_id}` | Zero; contract predecessor only; exactly one ready promise result |
| `get_campaign` | `{id}` | View |
| `list_campaigns` | `{}` | View; at most five full records |
| `get_account` | `{account_id}` | View; returns `registered:false` for a new identity |
| `get_config` | `{}` | View; storage allowances, limits and aggregate accounting |
| `nft_transfer` | `{receiver_id,token_id,approval_id?,memo?}` | Exactly 1 yoctoNEAR; current token owner |
| `nft_transfer_call` | `{receiver_id,token_id,msg,approval_id?,memo?}` | Exactly 1 yoctoNEAR; current token owner; use at least 100 Tgas in unsigned plans |
| `nft_resolve_transfer` | `{previous_owner_id,receiver_id,token_id,approved_account_ids?}` | Zero; private callback with exactly one ready result; optional approvals must be null |
| `set_mirror` | `{token_id,mirror_uri}` | Exactly 1 yoctoNEAR; current token owner; bounded HTTPS manifest location |
| `nft_token` | `{token_id}` | View; token or null |
| `nft_metadata` | `{}` | View; contract metadata with `spec:"nft-1.0.0"` |
| `nft_total_supply` | `{}` | View; decimal string supply |
| `nft_tokens` | `{from_index?,limit?}` | View; released tokens in campaign order |
| `nft_supply_for_owner` | `{account_id}` | View; decimal string supply for a valid account |
| `nft_tokens_for_owner` | `{account_id,from_index?,limit?}` | View; owner's released tokens in campaign order |

`create_campaign` uses these flat fields:

```json
{
  "id": "original-maths-v1",
  "title": "Original maths pack",
  "reviewer": "ACTUAL_REVIEWER_ACCOUNT",
  "manifest_uri": "https://ACTUAL_HOST/manifest.json",
  "manifest_hash": "LOWERCASE_HEX_64",
  "plaintext_hash": "LOWERCASE_HEX_64",
  "ciphertext_hash": "LOWERCASE_HEX_64",
  "key_commitment": "LOWERCASE_HEX_64",
  "license_hash": "LOWERCASE_HEX_64",
  "target": "8000000000000000000000000",
  "funding_deadline_ns": "ACTUAL_FUTURE_UNIX_NANOSECONDS",
  "release_window_ns": "3600000000000"
}
```

The placeholders above are intentionally invalid. Replace them with actual artifact/account values; never describe them as deployed resources. Campaign IDs contain 1–64 ASCII letters, digits, `_` or `-`; titles are 1–120 UTF-8 bytes; manifest URIs use HTTPS and at most 512 bytes. Funding deadlines must be future times. Release windows are positive and at most 30 days; timestamp arithmetic must fit u64.

`get_campaign` returns flat fields: `schema_version`, `id`, `title`, `creator`, `reviewer`, `manifest_uri`, `manifest_hash`, `plaintext_hash`, `ciphertext_hash`, `key_commitment`, `license_hash`, `target`, `total_contributed`, `escrow`, `funding_deadline_ns`, `release_window_ns`, `funded_at_ns`, `release_deadline_ns`, `agreement_digest`, `state`, `public_key_base64`, `stewardship`. Money and time fields are strings. `funded_at_ns` is `"0"` before funding; `release_deadline_ns` is null before funding; `public_key_base64` and `stewardship` are null before release. Thereafter stewardship is `{token_id,owner_id,mirror_uri}`. Effective states are `Draft`, `Active`, `Funded`, `Released` and `Refundable`.

`get_account` returns `schema_version`, `account_id`, `registered`, `credit`, `paid`, `pending` and `contributions`. `pending` is null or `{amount,operation_id}`. Each contribution is `{campaign_id,amount,refunded}`. Credited storage change is included in `credit`, separately from contribution records.

Create/approve/release return the campaign view. Contribute returns `{campaign,account}`. Refund returns the account view. Withdrawal returns its callback's final account view if that callback succeeds; before completion the canonical account view shows the pending operation. A failed callback is an uncertain operation and must not trigger another withdrawal automatically.

## Public-release stewardship

The token ID equals its campaign ID. Before release, `nft_token` returns null and enumeration excludes the campaign. The first valid release mints to the fixed creator once, without adding storage. `nft_transfer` returns null; `set_mirror` returns the updated token. Receiving a token needs no financial-account registration and consumes no participant slot. Only its current owner can transfer or choose a mirror; optional numeric approval IDs never confer authority because approval management is disabled.

**Every ownership change resets the mirror to the immutable original manifest URI**, including returns from rejected receiver calls. The immutable URI, manifest/content hashes, agreement, released key, creator credit and refund terms are never changed. Token metadata keeps the immutable original `reference` and base64 `reference_hash`; its JSON-string `extra` exposes `mirror_uri`, `original_manifest_uri`, `manifest_hash` and `agreement_digest`. A mirror is a discovery location, not proof of content availability or authenticity. Readers must verify the exact manifest and ciphertext against the campaign commitments before decryption and validate the resulting plaintext. A steward cannot revoke copies already retained.

`nft_transfer_call` first changes ownership, then calls `nft_on_transfer` on the receiver with `{sender_id,previous_owner_id,token_id,msg}` and zero deposit. It reserves 15 Tgas for a private resolver and forwards the available receiver budget after a scheduling margin. A JSON `false` accepts the NFT; `true`, failed execution, malformed data or more than five return bytes requests return. This follows the [official receiver-resolution implementation](https://github.com/near/near-sdk-rs/blob/master/near-contract-standards/src/non_fungible_token/core/core_impl.rs). If the receiver currently owns the token, return resets the mirror and the resolver returns false. If the current owner differs from that callback's receiver, the resolver preserves that owner and returns true. Acceptance returns true and preserves the current mirror. All callbacks use current stored state; nested transfers are supported without an in-flight ownership lock.

The resolver compares current ownership, not a transfer nonce. For example, after A→B `nft_transfer_call`, B→C and C→B can finish before B's original rejection callback. Because B owns the token again, that older callback can return it to A and reset B's newer mirror. This matches the reference implementation. A party reacquiring a token must account for unresolved earlier receipt chains; onward-transfer protection applies only while the current owner differs from the callback's receiver.

A receiver can update the mirror while it owns the token provisionally; a return resets that choice. If the resolver itself fails, its receipt does not roll back the earlier receiver ownership, and there is no timeout clawback or pending lock. Observe actual receipts and canonical ownership. Protocol callback gas and nested receipt behavior remain unverified until Sandbox tests. Mint, transfer, return, and mirror metadata changes emit NEP-171 1.2.0 events. Token minting and ownership changes do not prove educational quality or rights ownership.

NFT arguments are bounded: receiver messages at most 4096 UTF-8 bytes; optional memos at most 512 bytes; mirror URIs at most 512 bytes with HTTPS and a nonempty authority, without credentials, whitespace, control characters or backslashes. Pagination defaults to index `"0"` and all remaining tokens, at most five; limits must be positive integers. Approval IDs must be nonnegative JSON integers below 2^53 when supplied; they are ignored for an authorized owner.

## Accounting and storage

The hard demonstration ceilings are five campaigns, 100 registered accounts and 64 KiB serialized state. Only the owner fixed during initialization can create campaigns, which prevents another account from consuming all campaign slots. Contribution registration is public; others can consume the finite participant slots by making valid funded contributions. This bounds storage and execution but does not provide a production participant-capacity guarantee. A new deployment is necessary to increase these fixed limits. Do not put real money into this prototype.

Each campaign has at most one creator; creators are preallocated as credit recipients. Each account has five fixed contribution/refund slots, fixed credit counters, and one fixed withdrawal slot. The release key is always a 32-byte array with a separate boolean. Each campaign also prepays a 64-byte token owner buffer and 512-byte mirror buffer. Release, refund, ownership/mirror updates and callback outcomes allocate no new storage.

Storage allowances are separate from economic prices. The contract charges the actual increase in its single Borsh state value at `10^19` yoctoNEAR per byte. It credits unused allowance to the payer and retains the cost as collateral. The contract account's original code/state collateral must be funded at deployment. There is no cleanup/storage-refund method in this bounded demonstration.

For every committed mutation:

```text
economic_deposits + storage_deposits + security_deposits
  = storage_retained + sum(campaign escrow) + sum(account credit)
    + sum(pending withdrawal amounts) + successful withdrawals
    + retained security_deposits
```

Excess cap payment becomes payer credit. NFT transfers and mirror updates retain their exact one-yocto deposits in a dedicated security reserve, reported by `get_config.security_deposits`; this reserve is not withdrawable credit, creator compensation or storage collateral. Unsolicited native transfers are unallocated surplus and are never added to creator compensation. Gas and original deployment funding sit outside this equation. Checked u128 arithmetic and exclusive deadlines apply throughout.

## Commitments and review

The key commitment is SHA-256 of UTF-8 `SUNSET:KEY:1:` followed by the exact 32 key bytes, not textual base64. Public vector key bytes `00` through `1f` produce `e537e7d09b63e03318dc8b601070e14c2804137cc09890fe071f7cfe7e708c22`.

The agreement digest is SHA-256 of this exact Borsh tuple, in order: `(1u8, "testnet", current_contract_account, creator_account, Terms)`. Strings use Borsh length-prefixed UTF-8. `Terms` order is `id:String`, `title:String`, `reviewer:String`, `manifest_uri:String`, `manifest_hash:[u8;32]`, `plaintext_hash:[u8;32]`, `ciphertext_hash:[u8;32]`, `key_commitment:[u8;32]`, `license_hash:[u8;32]`, `target:u128`, `funding_deadline_ns:u64`, `release_window_ns:u64`. Integers are little endian. The browser can read the resulting digest and exact fields instead of introducing another encoder.

A campaign's named reviewer account must differ from its creator account; creation rejects identical IDs before registering accounts or charging storage. Distinct account IDs do not prove different human controllers or prevent creator–reviewer collusion. A reviewer must verify the exact ciphertext decrypts with the committed key to the committed plaintext and then inspect the resulting game. The contract checks only the key commitment; it does not evaluate AES, quality, licensing rights or artifact availability. Any authorized key holder can leak the pack early. A secret in a rejected transaction is already public.

## Direct recovery

Retain the actual testnet network, contract account, campaign ID, all artifact hashes, matching ciphertext/manifest and 32-byte key in an adult's local release backup. It contains no wallet private key. Use a separate wallet/CLI with that adult's own signing key to call `publish_release` with `{id,key_base64}` and zero deposit after verifying the campaign is still `Funded` and unexpired. Never submit a real secret to test an early or late call.

If a campaign is `Refundable`, its contributor directly calls `claim_refund` with `{id}`, then reads their account credit, calls `withdraw` with their desired decimal amount and zero deposit, and checks the canonical account/receipt outcome. These actions need no application session, database or backend signer. The user still needs a working testnet endpoint and signer.

For a pending withdrawal, record `(contract,account_id,operation_id)` and the initiating transaction/receipt chain. No timeout-based recredit method exists. A confirmed failed native transfer is restored once by its private callback. If callback execution fails or its result is unknown, funds remain visibly pending; an operator must not guess a replacement payout. Real Sandbox tests must validate native transfer failure and callback-failure behavior before claiming network recovery is proven.

Development deployments retain external full-access control and are **upgradeable** even though this code has no upgrade method. This package neither removes keys nor claims immutability. Source-to-artifact reproducibility and actual protocol execution must be checked before irreversible key removal is considered.
