# SUNSET — Support once. Share forever.

SUNSET pools adult sponsorship for a useful digital resource. The creator receives a capped payment when its committed key is published on time. Missed funding/release conditions allow refunds. Learners can keep a self-contained offline game without a wallet or account.

**Deployed to NEAR testnet on 2 November 2026:** reviewed contract `sunset.shiftultra.testnet`, initialized for owner `shiftultra.testnet`; [finalized deployment evidence](evidence/testnet-deployment.json) records the exact artifact, transactions and receipts. The frontend is [sunset-lemon.vercel.app](https://sunset-lemon.vercel.app), and its four prepared manifest/ciphertext files returned HTTP 200 with their committed hashes. **Campaign settlement and submission evidence remain incomplete:** browser execution, protocol callback/failure scenarios and actual sponsorship/release/refund/withdrawal still need verification. The interface labels every local financial action as rehearsal. Its testnet reader is read-only; browser rehearsal does not move tokens.

The [LLM council decision](../../research/2026-11-01-council/README.md) explains why SUNSET was retained, why purchase acceptance was replaced with sponsorship, and which hackathon tracks are defensible. The October architecture below is historical planning, not a list of completed features.

## Run

Requires Node.js 22.9+ (tested with 24.17). Dependencies are already installed in this workspace. On a fresh checkout:

```sh
cd projects/sunset
npm ci
npm run dev
```

Open `http://127.0.0.1:3000` for the public landing page, or `http://127.0.0.1:3000/app/` for the interactive workspace. Homepage links open the appropriate resource or workspace view. Existing browser-local packs and backups keep the same storage key. No environment variables, database, model API key or wallet are needed for rehearsal. For a static build, run `npm run build` then `npm start` (uses Python 3's static server for `out/`). Hosted browser state remains local to each visitor and does not form a shared service. The user has now authorized deployment; [the deployment runbook](docs/DEPLOYMENT.md) separates publishing this frontend from completing a live signing dApp.

A ready-to-open standalone sample is [public/try-lantern-trail.html](public/try-lantern-trail.html). Its gameplay is self-contained; actual offline browser execution must still be checked on the target machine.

For the operator's `shiftultra.testnet` wallet, the [testnet showcase guide](docs/TESTNET_SHOWCASE.md) provides a prepared 0.1-testNEAR campaign, private local release files and verified public encrypted resource locations. The contract account was funded with four testNEAR and deployed; reviewer/sponsor accounts remain to be created. Skip the completed contract creation/deployment steps. The observed owner balance was eight testNEAR before that allocation; check current balances before further transactions.

## Landing and workspace

The homepage introduces the commons with a custom SUNSET illustration, locally hosted Geist typography, sample resource scenarios, creator guidance, stewardship explanation and an accessible native FAQ. It renders its content without initializing the financial rehearsal or requiring JavaScript. `/app/` contains the full workspace, with a matching cream/terracotta/deep-green palette, larger text and roomier controls.

The static export uses trailing slashes so `/app/?view=...` resolves through the included Python static server. Views are allowlisted and campaign links select only existing resource IDs. Public sample gameplay stays at `/try-lantern-trail.html`.

`npm run test:pages` checks the exported landing, app route, CTA destinations, same-page anchors, local asset/font references and standalone sample data. It is static-output verification; real browser/mobile appearance and interaction remain unverified in the socket-restricted workspace. [Artwork and exact generation prompt](public/images/README.md); the bundled Geist font keeps its OFL license.

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

Testnet setup in the app reads an actual configured contract only after verifying `chain_id`, pinned code hash and block identity. It is a read-only viewer. Its public-resource catalog can explicitly recover, verify, play and export a released pack from the original or steward-selected manifest location; the onchain license commitment is checked as well. The coordination lab exports unsigned `contribute` plans. The transaction workbench prepares the complete core/NFT ABI, calculates separate storage/security deposits, optionally binds an expected signer, and checks imported RPC evidence against exact action fields. Supplied evidence files do not prove chain authenticity. Adults must separately verify and sign with their own wallet/CLI; the UI does not implement live wallet authentication or signing.

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

Replace placeholders with real identities and hosting. Use an output directory that does not already exist and keep it outside any public document root. The script writes `create-campaign.json`, an encrypted recovery `artifact.json`, exact `manifest.json`, raw `ciphertext.sunset`, private backup and secret release arguments. **Publish the exact manifest.json and ciphertext.sunset together in one directory. Retain artifact.json for independent file recovery. Never upload the private backup or release arguments prematurely.** Newly prepared schema-2 manifests commit the fixed relative ciphertext path; older schema-1 retained files remain recoverable without rewriting their commitments. Add private output directories to your own ignore rules; `private/` is already ignored. The script directory is not itself a deployed resource.

Independent offline recovery with the application stopped:

```sh
node scripts/recover-pack.mjs artifact.json private-release-backup.json offline-game.html
```

This verifies manifest, ciphertext, key and plaintext commitments before writing the standalone game. It works entirely locally. For onchain disclosure, refunds and withdrawals use the contract ABI and your actual signer directly; see the contract recovery documentation. A secret in any submitted transaction is public even when the transaction fails.

## Verification

```sh
npm run check
npm run build
npm run test:pages
cargo test --locked --offline --manifest-path contracts/sunset/Cargo.toml
cargo fmt --manifest-path contracts/sunset/Cargo.toml --check
cargo clippy --locked --offline --manifest-path contracts/sunset/Cargo.toml --all-targets -- -D warnings
bash contracts/sunset/scripts/build.sh
```

The Wasm host tests execute the compiled artifact with transactional host doubles. They do **not** simulate NEAR protocol gas, real account balances, actual receipts or Sandbox. [Evidence](evidence/verification.json) records checked and unverified items separately. [Independent contract review](../../research/2026-11-01-council/contract-review.md) and [frontend review](../../research/2026-11-01-council/frontend-review.md) retain findings.

The [2 November predeployment review](docs/CONTRACT_PREDEPLOY_REVIEW.md) covers all production Rust modules, fixes malformed resource-URL acceptance and adds a full-capacity accounting regression. The revised artifact and operator guide are pinned together; actual protocol gas, signatures and settlement remain unverified.

Caps: five curated contract campaigns, 100 permanent registered contract accounts, bounded serialized state. Public contributors can exhaust the participant slots. Callback uncertainty leaves a withdrawal pending, without speculative recredit. The contract checks key commitments, not licensing rights, educational quality, decryptability or artifact availability. Development deployments remain upgradeable while full-access keys exist. Testnet only; no mainnet readiness or immutable deployment is claimed.

## Tokenization with a concrete maintenance right

Each successfully released campaign mints one stewardship NFT to its fixed creator. The current holder can maintain a preferred HTTPS mirror for the same committed manifest and ciphertext. Transfer hands that authority to another account and resets the mirror to the original URI; former holders lose maintenance authority. Existing content access, license, hashes, creator compensation and refund claims stay fixed. Learners need no token.

The contract implements **NEP-171 core and events, NEP-177 metadata, and NEP-181 enumeration**, including receiver acceptance/rejection and private transfer resolution. Token transfers and mirror updates require exactly one yoctoNEAR, retained separately from escrow. It omits approvals, royalties, token sales and revenue shares. It requires a **fresh deployment with state layout 2**; no state migration is supplied. A receiver that reacquires a token before an older callback may still have it returned under reference-standard owner-equality semantics; see the contract README.

Open **Stewardship** after a pack is released. Transfer its local token, try the old account's mirror edit, then use the new holder. Save the exact manifest and ciphertext, host them together yourself, and explicitly verify the mirror. Downloads are bounded, redirects rejected and credentials omitted; all original commitments are checked before the strict pack can run. A URL alone is not evidence of availability. Existing browser packs/backups are preserved when their local state gains the new stewardship fields.

[Tokenization research and alternatives](../../research/2026-11-01-tokenization/RESEARCH.md) · [contract review](../../research/2026-11-01-tokenization/CONTRACT_REVIEW.md) · [client review](../../research/2026-11-01-tokenization/CLIENT_REVIEW.md).

## Reproducible checks and demonstration

`npm run check` runs the application suite, typecheck, nine socket-free workflow scenarios, source/artifact digest checks and compiled-Wasm scenarios. `npm run verify:local` exercises retained-file recovery in a separate process, both refund outcomes, token maintenance handover and conservation of **21.8 simulated NEAR**. [Demonstration guide](docs/DEMO.md), [threat model](docs/THREAT_MODEL.md), [sample arithmetic review](docs/CONTENT_REVIEW.md), [unsubmitted preparation draft](docs/SUBMISSION_DRAFT.json).

GitHub Actions checks are prepared in the root `.github/workflows/checks.yml`, using the recorded Node/Rust versions. They test and build without deploying. No hosted workflow run is claimed. The current OS rejects TCP/Unix socket creation and has no NEAR protocol runtime; [exact remaining verification gaps](../../research/2026-11-01-tokenization/VERIFICATION_GAPS.md) are recorded rather than replaced by simulated proof.

For publication from a network-enabled terminal, run `bash scripts/publish-github.sh` from this directory. It prompts privately for a temporary GitHub token, verifies Tejas-Sands ownership and remote history, publishes the preserved commits without forcing, and checks the remote commit. The [deployment runbook](docs/DEPLOYMENT.md) includes persistent Vercel Git integration and the separate work still needed for a live NEAR browser dApp.

## Hackathon positioning

Primary product targets: **Open Innovation**, **Social Money**, and now **NFTs That Do Something** through the implemented transferable maintenance right. NFT fit remains conditional on the required demonstration evidence and organizer judgment. **Real-World Money** requires actual creator-payment/refund/withdrawal evidence. Agent Economy, Security and Swarms remain conditional future claims; local policy simulations do not establish autonomous onchain authority. Do not select Games, Privacy, DeFi, Memecoins or Investment Thesis for superficial associations. [All thirteen tracks and current rules](../../research/2026-11-01-council/track-verification.md).

Before submission: real browser/mobile/offline QA, protocol callback/failure scenarios, actual campaign settlement and independent-user receipts, educator review, real sponsor feedback, a verified public repository/demo and accurate team/payout details. Contract deployment/initialization and hosted resource hashes are verified; repository publication was reported by the operator. No actual hackathon submission or campaign settlement is claimed.

## Original design and research

Selected October 22. [Architecture](ARCHITECTURE.md), [original contract specification](CONTRACT.md), [workflows](WORKFLOWS.md), [operations](OPERATIONS.md), [original multiweek plan](BUILD_PLAN.md), [domain research](research/2026-10-22/README.md). The larger Supabase/order/managed-release architecture is deferred. [Current build decisions](docs/BUILD_LEDGER.md) govern this implementation. Software: MIT; original sample pack: CC0-1.0.
