# SUNSET stewardship and non-deployment completion

User direction: research thoroughly, add useful tokenization where justified, finish all work possible except deployment. This delegates implementation choices; do not stop for routine design confirmation. Preserve existing authorization for meaningful verified commits and pushes. Existing GitHub access failure is a separate blocker; do not reattempt it endlessly or provision/deploy anything.

## Decision and alternatives

Implement one nonfinancial **stewardship NFT** per publicly released learning pack. Its sole additional authority is maintaining a bounded HTTPS recovery mirror for the same committed artifact. Transferring the token transfers that maintenance authority. Anyone can keep/use/share CC0 copies without owning a token. Existing immutable economic terms, release key and creator/refund beneficiaries never change.

Compared alternatives: revenue/copyright fractions conflict with the current CC0/open-resource model and add an unrelated investment mechanism; service vouchers require another fulfillment/expiry/refund system; sponsorship receipts need no tradable token. Stewardship supports SUNSET's independent recovery purpose with the smallest distinct right. Its demand remains a hypothesis; compare with simple account reassignment in research.

## Contract

Extend the undeployed Rust contract rather than invent a second money ledger. One token per released campaign, minted atomically with release to the fixed creator. Reserve all mutable owner/mirror/async fields at campaign creation; zero-deposit release remains allocation-free. This is a new state layout requiring a fresh deployment; no migration claim for old contract state.

Implement NEP-171 core (`nft_token`, `nft_transfer`, `nft_transfer_call`, private `nft_resolve_transfer`), NEP-177 collection/token metadata and NEP-297/NEP-171 events. Omit optional approval, enumeration and royalty extensions unless standards verification shows necessity. Security deposits are exactly one yoctoNEAR for NFT transfers and accounted separately from buyout escrow and storage collateral.

Transfers authorize the actual predecessor/current owner. Callback validates self predecessor, exact pending operation and receiver boolean outcome; failure/true/malformed receiver results request return, false keeps. Never claw back from an owner who has already received an onward transfer. Engineering ruling after reference-implementation review: every ownership change resets the mirror to the immutable original URI, including a resolver return. A rejecting receiver cannot retain a mirror side effect, and a later owner’s mirror survives an earlier resolver. This standard-compatible rule avoids a global pending lock and its permanent liveness hazard if a callback fails. Callback results are never guessed.

Only a settled token holder may update a bounded HTTPS mirror. The contract records authority and URL, not remote availability. It cannot fetch or prove mirror bytes. The client explicitly downloads without credentials, bounds time/size, verifies manifest/ciphertext/key/plaintext against independently retained/onchain commitments and only then runs the strict pack. Never fetch arbitrary URLs from a server.

## App and recovery

Add a resource-stewardship interface: current owner, committed pack, canonical mirror, transfer, former-owner rejection, mirror revision and local event history. Distinguish rehearsal actions from unsigned live plans. Migrate existing local demo state without deleting custom packs/backups. Public learning/download remains wallet-free. Add independent recovery verification and useful unsigned transaction planning for all core flows; never ask for wallet private keys.

## Verification and handoff

Test crypto/mirror tampering and URL/redirect/size boundaries, ownership changes, old-owner failures, exact one-yocto deposits, transfer-call success/rejection/failure/forwarded ownership, pending-mirror denial, immutable financial terms, storage-size invariance and conservation. Execute compiled Wasm tests plus Rust tests/clippy/fmt, TypeScript and production build. Attempt real browser/protocol Sandbox only with existing available tooling. Current socket EPERM and missing Sandbox are factual limits; do not relabel host doubles as protocol tests.

Prepare reproducible local end-to-end checks, demonstration script, threat model, track matrix and submission draft with explicit outstanding real-world evidence. NFT track becomes a candidate based on actual authority behavior; no organizer acceptance, live deployment or validated adoption is claimed. Deployment, provisioning, signing, mainnet, social posts and final submission remain outside this turn.
