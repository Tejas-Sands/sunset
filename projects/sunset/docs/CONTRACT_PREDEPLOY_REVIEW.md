# SUNSET contract review before testnet deployment

Reviewed 2 November 2026, starting from `428eba6`. The operator explicitly requested a whole-contract check before deployment. Three independent agents reviewed financial accounting, host/runtime boundaries and NFT behavior; the coordinator checked the findings and a separate reviewer inspected the resulting patch. They use the same model family. This is a focused source/test review, not an external security audit or evidence of protocol execution.

## Result and fixed finding

No actionable theft, duplicate payout, unauthorized release/transfer or ledger-conservation defect was established in the reviewed implementation. **One low-severity input-validation defect was confirmed and fixed:** an authorized creator could commit an unusable original manifest URL such as `https://`, and an authorized steward could set malformed mirror authorities such as `https://:` or `https://[`. This could impair discovery; it did not bypass content commitments or financial authority.

Campaign creation and mirror updates now share bounded HTTPS/DNS validation. It rejects malformed/empty authorities, credentials, fragments, controls, whitespace, backslashes, invalid/zero/overflow ports, malformed DNS labels, and IP/local host forms. It accepts the prepared public host, bounded paths/queries and UTF-8 paths. This is a strict syntactic subset, not a guarantee about DNS resolution, availability, content rights or educational quality.

Three native regressions first failed against the old validator, then passed after the fix. They check that rejected calls preserve the complete serialized state, including storage, ownership, escrow, credits and security deposits. Production changes do not alter Borsh layout, amounts, access rules, callback scheduling or the fixed gas allocations. Existing layout-2 fresh-deployment guidance remains applicable.

The browser/preparation URL validator was also aligned with those DNS-label and nonzero-port requirements, including a bare `#` fragment edge case. Its regression first failed, then passed. URL normalization, IDN-to-punycode conversion and valid ports remain supported. The application suite now has 48 passing tests; the contract has 19 native tests and 11 compiled-Wasm host scenarios.

## Financial and host checks

The review traced exact deposits, capped contributions/change, both deadline outcomes, key commitments, release/refund exclusivity, fixed creator credit, pull withdrawals, pending operation IDs, private callbacks, storage charging and integer boundaries. Host checks covered register reuse, little-endian amounts, bounded JSON/state, private initialization and receipt rollback assumptions. NFT checks covered mint-once ownership, one-yocto reserves, mirror authority, pagination, receiver acceptance/rejection and nested transfers.

An additional compiled-Wasm regression fills five campaigns and 100 accounts (29,841 serialized bytes in that fixture), adds release credit during a pending withdrawal, restores the original amount on a mocked failed transfer, refunds the remaining campaigns and withdraws every remaining credit. Deposit conservation and fixed state size hold in the host model. The separately calculated maximum state bound is 30,341 bytes, below the 65,536-byte limit.

These scenarios use **transactional host doubles**. In particular, the harness reports zero consumed gas and invokes callbacks with more gas than their scheduled 15 Tgas. It cannot establish real callback gas sufficiency, actual native balances, receipt execution or protocol compatibility.

## Metadata finding checked and rejected

A reviewer questioned numeric NFT metadata timestamps because the Rust SDK metadata type still uses optional strings. The current [NEP-177 specification](https://raw.githubusercontent.com/near/NEPs/master/neps/nep-0177.md) explicitly specifies numeric epoch milliseconds and explains the former string ambiguity in its errata. Numeric output was retained. Actual wallet/marketplace compatibility remains a live integration check; SDK types alone do not override the current standard.

## Reviewed artifact

- Rust: `1.96.0`, locked offline dependencies.
- Wasm: **270,188 bytes**.
- SHA-256: `7a65f94c90eb11c7e7865362ea3386656e9d89334512b12b7ce313e5ed606c6f`.
- Expected Base58 code hash: `9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx`.
- Code-storage estimate: **2.70188 testNEAR**, before account allowances, state and fees. Four testNEAR remains the proposed contract allocation.
- Separate source checkouts and target directories produced byte-identical Wasm under the pinned compiler and dependencies. The second build used paths and a Cargo-cache symlink containing spaces and replaced ambient Rust flags. No home/checkout paths occur in the artifact.

Exact checks and eight source digests are in [build evidence](../contracts/sunset/build-evidence.json). The [operator guide](TESTNET_SHOWCASE.md) pins this revised artifact; the previously prepared encrypted resource and release backup remain the same resource commitment.

## Required live verification

The result supports controlled testnet verification, not production or mainnet use. Before claiming successful operation, verify the exact deployed code hash and perform:

1. Actual initialization/owner/reviewer authority and native contributions at the intended deposits.
2. Release, creator withdrawal and both expiry refunds, with finalized state, native balances, gas and complete receipt chains.
3. Maximum-state withdrawal/NFT callbacks at their actual scheduled gas, transfer failure and callback failure. A pending withdrawal must never be guessed failed or recredited after a timeout.
4. NFT handover, old-owner rejection and verified mirror recovery, plus real downloaded-file execution with networking disabled.

Documented limits remain: five curated campaigns, 100 permanent registered accounts, participant-slot exhaustion, trusted human content/rights review, external artifact hosting, retained full-access upgrade authority and reference-standard NFT receiver-reacquisition behavior. No protocol result or independent human review is claimed here.

## Deployment execution check

The operator reports seven testNEAR in `shiftultra.testnet`. In this executor, `near` and `near-sandbox` are absent; no cached CLI package or imported signer has been verified. Testnet RPC and npm registry DNS fail, and no configured network proxy/connection manifest is exposed. A read-only RPC check requested outside the sandbox was rejected by the execution policy because sandbox escalation is disabled. No deployment transaction was submitted, no wallet key was requested/read, and no testNEAR was moved.

Deploying from a Codex terminal is supported when that terminal has the CLI, local signing authorization and RPC access. This session must obtain those capabilities through its supported environment/permission setup; the contract review and successful local build do not provide them.
