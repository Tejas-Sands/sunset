# SUNSET — Support once. Share forever.

SUNSET pools adult sponsorship for a useful digital resource. The creator receives a capped payment when its committed key is published on time. Missed funding/release conditions allow refunds. Learners can keep a self-contained offline game without a wallet or account.

**Built locally on 1 November 2026:** runnable Next.js application, encrypted learning packs, independent recovery tools and compiled NEAR Wasm contract. **Not yet deployed or submission-ready:** browser execution, NEAR Sandbox receipt scenarios and live testnet settlement remain unverified. The interface labels every local financial action as rehearsal. No actual tokens move there.

The [LLM council decision](../../research/2026-11-01-council/README.md) explains why SUNSET was retained, why purchase acceptance was replaced with sponsorship, and which hackathon tracks are defensible. The October architecture below is historical planning, not a list of completed features.

## Run

Requires Node.js 22.9+ (tested with 24.17). Dependencies are already installed in this workspace. On a fresh checkout:

```sh
cd projects/sunset
npm ci
npm run dev
```

Open `http://127.0.0.1:3000`. No environment variables, database, model API key or wallet are needed for rehearsal. For a static build, run `npm run build` then `npm start` (uses Python 3's static server for `out/`). Deploying the static `out/` directory to free hosting is a separate action. Hosted browser state remains local to each visitor and does not form a shared service.

A ready-to-open standalone sample is [public/try-lantern-trail.html](public/try-lantern-trail.html). Its gameplay is self-contained; actual offline browser execution must still be checked on the target machine.

## Rehearse the complete story

1. Discover → The Lantern Trail. As `grove.testnet`, sponsor **1.6** simulated NEAR to finish the 8-NEAR goal. Excess contribution becomes claimable change.
2. Switch the role-play account to `teacher.testnet`. Use the saved demo backup or restore an exported private backup. Verify and publish the release key. The creator receives credit exactly once.
3. Play the released adventure and download the standalone HTML game. Open it with networking disabled. Local answers are not uploaded.
4. Open River Routes as `grove.testnet` and claim its expired contribution refund. Activity displays claimable balances and allows a simulated withdrawal; events and CSV are explicitly not blockchain receipts.
5. Creator studio prepares an original sample or strictly validated custom JSON pack. Save/check a private release backup; the named reviewer verifies and inspects the exact decrypted questions before approving the bound agreement.
6. Access budgets demonstrates finite, separate provider spending, approved claims and expired remainder refunds. Coordination lab demonstrates independently capped deterministic strategies and rejected overspending. **These extensions are local; they are not in the current Wasm contract.**

How it works can advance the rehearsal clock eight days and reset this browser's sample data. Keep important private backups independently before resetting. Demo keys in browser storage are not a production key-management service. Roles are simulated, not authenticated wallet identities.

## NEAR contract and real deployment preparation

[Contract README and JSON ABI](contracts/sunset/README.md) covers initialization, storage allowances, review, contribution, release, both refund paths, withdrawals and direct recovery. [Compiled contract](contracts/sunset/res/sunset_contract.wasm) is real Wasm. It uses the NEAR host ABI directly, with pinned Borsh/Serde dependencies. Its private one-time initializer is `new {owner}`; only that owner creates campaigns. No real account name is assumed to exist.

Testnet setup in the app reads an actual configured contract only after verifying `chain_id`, pinned code hash and block identity. It is a read-only viewer. The coordination lab exports unsigned `contribute` plans; adults must separately verify and sign with their own wallet/CLI. The UI does not implement live wallet authentication or signing.

Prepare the exact artifact/manifest and onchain terms without making any network request:

```sh
mkdir -p private
node scripts/prepare-campaign.mjs \
  --pack public/packs/lantern-trail.json \
  --reviewer YOUR_ACTUAL_REVIEWER.testnet \
  --manifest-uri https://YOUR_ACTUAL_HOST/manifest.json \
  --target 8 --deadline 2026-11-10T00:00:00Z \
  --out private/lantern-trail
```

Replace placeholders with real identities and hosting. Use an output directory that does not already exist and keep it outside any public document root. The script writes `create-campaign.json`, an encrypted `artifact.json`, exact `manifest.json`, private backup and secret release arguments. **Publish only the encrypted artifact and exact manifest before release. Never upload the private backup or release arguments prematurely.** Add private output directories to your own ignore rules; `private/` is already ignored. The script directory is not itself a deployed resource.

Independent offline recovery with the application stopped:

```sh
node scripts/recover-pack.mjs artifact.json private-release-backup.json offline-game.html
```

This verifies manifest, ciphertext, key and plaintext commitments before writing the standalone game. It works entirely locally. For onchain disclosure, refunds and withdrawals use the contract ABI and your actual signer directly; see the contract recovery documentation. A secret in any submitted transaction is public even when the transaction fails.

## Verification

```sh
npm test
npm run typecheck
npm run build
npm run test:contract
cargo test --locked --offline --manifest-path contracts/sunset/Cargo.toml
cargo fmt --manifest-path contracts/sunset/Cargo.toml --check
cargo clippy --locked --offline --manifest-path contracts/sunset/Cargo.toml --all-targets -- -D warnings
bash contracts/sunset/scripts/build.sh
```

The Wasm host tests execute the compiled artifact with transactional host doubles. They do **not** simulate NEAR protocol gas, real account balances, actual receipts or Sandbox. [Evidence](evidence/verification.json) records checked and unverified items separately. [Independent contract review](../../research/2026-11-01-council/contract-review.md) and [frontend review](../../research/2026-11-01-council/frontend-review.md) retain findings.

Caps: five curated contract campaigns, 100 permanent registered contract accounts, bounded serialized state. Public contributors can exhaust the participant slots. Callback uncertainty leaves a withdrawal pending, without speculative recredit. The contract checks key commitments, not licensing rights, educational quality, decryptability or artifact availability. Development deployments remain upgradeable while full-access keys exist. Testnet only; no mainnet readiness or immutable deployment is claimed.

## Hackathon positioning

Primary targets: **Open Innovation**, **Social Money**. **Real-World Money** requires actual creator-payment/refund/withdrawal evidence. Agent Economy, Security and Swarms remain conditional future claims; local policy simulations do not establish autonomous onchain authority. Do not select Games, Privacy, DeFi, NFTs, Memecoins or Investment Thesis for superficial associations. [All thirteen tracks and current rules](../../research/2026-11-01-council/track-verification.md).

Before submission: real browser/mobile/offline QA, protocol Sandbox failure scenarios, actual reviewed testnet deployment and independent-user receipts, educator review, real sponsor feedback, public repository, approved public demo and accurate team/payout details. No publication or submission has occurred.

## Original design and research

Selected October 22. [Architecture](ARCHITECTURE.md), [original contract specification](CONTRACT.md), [workflows](WORKFLOWS.md), [operations](OPERATIONS.md), [original multiweek plan](BUILD_PLAN.md), [domain research](research/2026-10-22/README.md). The larger Supabase/order/managed-release architecture is deferred. [Current build decisions](docs/BUILD_LEDGER.md) govern this implementation. Software: MIT; original sample pack: CC0-1.0.
