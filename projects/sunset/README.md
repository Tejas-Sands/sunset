# SUNSET — Support once. Share forever.

SUNSET pools adult sponsorship for a useful digital resource. The creator receives a capped payment when its committed key is published on time. Missed funding/release conditions allow refunds. Readers can keep a self-contained learning pack or practical handbook without a wallet or account.

The purpose is to help people who create value keep creating. Lessons, workshop kits and useful guides can be free for people to use while a community compensates the person who made them. SUNSET applies that idea to a prepared resource's public release, with explicit sponsorship and refund conditions.

**Main testnet showcase verified on 2 November 2026:** reviewed contract `sunset.shiftultra.testnet` accepted 0.06 + 0.04 testNEAR, released the committed pack, paid its fixed creator 0.1 testNEAR, and transferred stewardship with enforced mirror authority. [Finalized transactions and state](evidence/testnet-showcase.json) include the successful native payout callback. The hosted [SUNSET app](https://sunset-lemon.vercel.app/app/) recovered the original and steward mirror; its actual downloaded game completed all five questions in a fresh browser with browser offline enabled before file load. [Browser evidence and limits](evidence/browser-showcase.json) distinguish this from an OS network toggle. All demo roles share one operator, and both mirror paths share one host. **Both actual expiry refunds and native principal withdrawals were verified on 3 November:** 0.01 + 0.02 testNEAR returned, with successful callbacks and no pending withdrawal. [Fresh end-to-end review](docs/E2E_AUDIT_2026-11-03.md) and [refund receipts](evidence/testnet-refunds.json) record the scope. Protocol failure/max-state scenarios and independent human validation remain open. Browser financial controls remain rehearsal/unsigned plans; its live testnet reader is read-only.

The [LLM council decision](../../research/2026-11-01-council/README.md) explains why SUNSET was retained, why purchase acceptance was replaced with sponsorship, and which hackathon tracks are defensible. The October architecture below is historical planning, not a list of completed features.

## Run

Requires Node.js 22.9+ (tested with 24.17). Dependencies are already installed in this workspace. On a fresh checkout:

```sh
cd projects/sunset
npm ci
npm run dev
```

Open `http://127.0.0.1:3000` for the public landing page, or `http://127.0.0.1:3000/app/` for the interactive workspace. Homepage links open the appropriate resource or workspace view. Existing browser-local packs and backups keep the same storage key. No environment variables, database, model API key or wallet are needed for rehearsal. For a static build, run `npm run build` then `npm start` (uses Python 3's static server for `out/`). Hosted browser state remains local to each visitor and does not form a shared service. The user has now authorized deployment; [the deployment runbook](docs/DEPLOYMENT.md) separates publishing this frontend from completing a live signing dApp.

A ready-to-open standalone sample is [public/try-lantern-trail.html](public/try-lantern-trail.html). Separately, the actual downloaded live campaign was completed offline in a fresh browser; its recorded hash and exact browser network-disable scope are in [browser evidence](evidence/browser-showcase.json).

The [testnet showcase guide](docs/TESTNET_SHOWCASE.md) now replays the completed `lantern-trail-testnet-v1` campaign through read-only checks and actual receipt links. Reviewer/sponsor accounts exist, the campaign is `Released`, creator `paid` is 0.1 testNEAR with no pending withdrawal, and the NFT holder is `reviewer.shiftultra.testnet`. Do not repeat its signed actions. Two separate campaigns now verify both real-time expiry paths and exact native refunds; do not repeat their completed actions either.

The [V22 narrated launch film](media/launch-v22/README.md) follows one real workshop kit from the same fictional maker to public use. The 44.667-second kinetic collage adds the operator-selected warm synthetic voice, an explicit alternative refund path and a qualified receipt from the earlier Lantern Trail testnet run. The original logo, key/card logic and link-free ending remain. [Script](media/launch-v22/SCRIPT.md), [review](media/launch-v22/REVIEW.md), [credits](media/launch-v22/CREDITS.md), [evidence](evidence/launch-video-v22.json), [Bang Motion study](media/launch-v22/BANG_STUDY.md) and [delivery guide](docs/LAUNCH_VIDEO.md) record scope. Earlier films remain intact; generated media stay ignored. No new campaign, deployment, public post or submission occurred.

## Landing and workspace

The homepage introduces the commons with a custom SUNSET illustration, locally hosted Geist typography, sample resource scenarios, creator guidance, stewardship explanation and an accessible native FAQ. It renders its content without initializing the financial rehearsal or requiring JavaScript. `/app/` contains the full workspace, with a matching cream/terracotta/deep-green palette, larger text and roomier controls.

The static export uses trailing slashes so `/app/?view=...` resolves through the included Python static server. Views are allowlisted and campaign links select only existing resource IDs. Public sample gameplay stays at `/try-lantern-trail.html`.

`npm run test:pages` checks exported routes, links, assets and sample data. Actual hosted desktop reader/recovery/download and fresh-browser offline gameplay now passed; the offline game also fits a 390-pixel viewport. Fresh 3 November desktop and 390×844 viewport navigation passed without horizontal overflow; broad accessibility, physical-device and cross-browser QA remains incomplete. One mirror fetch timed out and succeeded on a bounded retry. [Artwork and exact generation prompt](public/images/README.md); the bundled Geist font keeps its OFL license.

## Practical handbooks

The new [Open-source Maintainer Handbook](public/packs/maintainer-handbook.json) contains four original procedures and sixteen checks: prepare a release, recover a lost commit, hand over maintainership and retain useful material offline. Open `/app/?view=Handbook` or [the standalone sample](public/try-maintainer-handbook.html). Native chapter search and checklists work locally; selected chapter and progress survive reload when browser storage is available. Commands are reference text and never execute.

Creator Studio and the existing encryption/recovery pipeline accept the strictly validated `schema:2, kind:"guide"` format alongside unchanged numeric quiz packs. Content remains inert bounded plain text; no uploaded scripts, markup or remote resources. The same reader handles verified guides and reviewer previews. No contract rewrite is needed because commitments bind content bytes rather than parse lessons.

This is a locally verified new example. It does not replace the content named by earlier finalized testnet transactions, and no handbook-specific onchain release or hosted update is claimed. [Guide checks and actual browser evidence](evidence/handbook-guide.json) include desktop/mobile download/offline/search/check/reload, exact independent encrypted-file recovery, and legacy byte preservation. [Content sources and limits](docs/MAINTAINER_HANDBOOK_SOURCES.md) explain the original CC0 material.

## Community workshop kit

[The Community Skill-Swap Kit](public/try-workshop-kit.html) is an original CC0 guide for a 45-minute adult session with paper and pens: welcome, demonstration, paired practice, teach-back and a next step. Its [source JSON](public/packs/workshop-kit.json) has three chapters and seven local checks. Open the standalone HTML directly, or upload the JSON through the existing Creator Studio. Regenerate the file with `node scripts/export-workshop-kit.mjs`.

Strict content validation, exact self-contained export, encryption and separate-process retained-file recovery pass; [evidence](evidence/workshop-guide.json) records the hashes and 63-test suite. This is a new local example. No new browser/offline-use observation, kit campaign, live payment or hosted update is claimed.

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

The [2 November predeployment review](docs/CONTRACT_PREDEPLOY_REVIEW.md) covers all production Rust modules, fixes malformed resource-URL acceptance and adds a full-capacity host regression. The subsequent [main testnet showcase](evidence/testnet-showcase.json) verifies normal campaign/NFT calls and a successful small-state withdrawal callback: 1.647072781898 Tgas burned from its scheduled 15 Tgas. Both actual expiry refunds and successful native withdrawal callbacks are now verified separately in [refund evidence](evidence/testnet-refunds.json). Maximum-state protocol gas and failed transfers/callbacks remain unverified.

Caps: five curated contract campaigns, 100 permanent registered contract accounts, bounded serialized state. Public contributors can exhaust the participant slots. Callback uncertainty leaves a withdrawal pending, without speculative recredit. The contract checks key commitments, not licensing rights, educational quality, decryptability or artifact availability. Development deployments remain upgradeable while full-access keys exist. Testnet only; no mainnet readiness or immutable deployment is claimed.

## Tokenization with a concrete maintenance right

Each successfully released campaign mints one stewardship NFT to its fixed creator. The current holder can maintain a preferred HTTPS mirror for the same committed manifest and ciphertext. Transfer hands that authority to another account and resets the mirror to the original URI; former holders lose maintenance authority. Existing content access, license, hashes, creator compensation and refund claims stay fixed. Learners need no token.

The contract implements **NEP-171 core and events, NEP-177 metadata, and NEP-181 enumeration**, including receiver acceptance/rejection and private transfer resolution. Token transfers and mirror updates require exactly one yoctoNEAR, retained separately from escrow. It omits approvals, royalties, token sales and revenue shares. It requires a **fresh deployment with state layout 2**; no state migration is supplied. A receiver that reacquires a token before an older callback may still have it returned under reference-standard owner-equality semantics; see the contract README.

Open **Stewardship** after a pack is released. Transfer its local token, try the old account's mirror edit, then use the new holder. Save the exact manifest and ciphertext, host them together yourself, and explicitly verify the mirror. Downloads are bounded, redirects rejected and credentials omitted; all original commitments are checked before the strict pack can run. A URL alone is not evidence of availability. Existing browser packs/backups are preserved when their local state gains the new stewardship fields.

[Tokenization research and alternatives](../../research/2026-11-01-tokenization/RESEARCH.md) · [contract review](../../research/2026-11-01-tokenization/CONTRACT_REVIEW.md) · [client review](../../research/2026-11-01-tokenization/CLIENT_REVIEW.md).

## Reproducible checks and demonstration

`npm run check` runs the application suite, typecheck, nine socket-free workflow scenarios, source/artifact digest checks and compiled-Wasm scenarios. `npm run verify:local` exercises retained-file recovery in a separate process, both refund outcomes, token maintenance handover and conservation of **21.8 simulated NEAR**. [Demonstration guide](docs/DEMO.md), [threat model](docs/THREAT_MODEL.md), [sample arithmetic review](docs/CONTENT_REVIEW.md), [unsubmitted preparation draft](docs/SUBMISSION_DRAFT.json).

GitHub Actions checks are prepared in `.github/workflows/checks.yml`, using the recorded Node/Rust versions; no hosted workflow result is claimed. Earlier socket restrictions were overcome for the recorded browser and testnet showcase. NEAR Sandbox and failure/max-state protocol checks remain open; see [current verification evidence](evidence/verification.json). Historical research gap reports retain their original scope.

The public repository is [Tejas-Sands/sunset](https://github.com/Tejas-Sands/sunset). After a verified local commit, the operator pushes from the repository root with `git --git-dir=.sunset-git --work-tree=. push origin main`. GitHub authentication stays local to the laptop. The [deployment runbook](docs/DEPLOYMENT.md) covers hosting and the remaining work for live browser signing.

## Hackathon positioning

Primary product targets: **Open Innovation**, **Social Money**, and now **NFTs That Do Something** through the implemented transferable maintenance right. NFT fit remains conditional on the required demonstration evidence and organizer judgment. **Real-World Money** requires actual creator-payment/refund/withdrawal evidence. Agent Economy, Security and Swarms remain conditional future claims; local policy simulations do not establish autonomous onchain authority. Do not select Games, Privacy, DeFi, Memecoins or Investment Thesis for superficial associations. [All thirteen tracks and current rules](../../research/2026-11-01-council/track-verification.md).

Official submission needs a public repository with judge steps, a human-posted X demo, actual team/contact details, track choices, a mainnet prize-payout account and consent before the deadline. See [submission process](docs/SUBMISSION.md). Our remaining engineering and product validation goals include protocol failure/max-state scenarios, accessibility/cross-device QA, independently controlled reviewers/sponsors and educator/sponsor feedback; these are not extra organizer eligibility rules. Public repository, hosted recovery, offline game, main release/payout/stewardship and both actual expiry refunds are verified. No hackathon submission, independent adoption, external audit or mainnet readiness is claimed.

## Original design and research

Selected October 22. [Architecture](ARCHITECTURE.md), [original contract specification](CONTRACT.md), [workflows](WORKFLOWS.md), [operations](OPERATIONS.md), [original multiweek plan](BUILD_PLAN.md), [domain research](research/2026-10-22/README.md). The larger Supabase/order/managed-release architecture is deferred. [Current build decisions](docs/BUILD_LEDGER.md) govern this implementation. Software: MIT; original sample pack: CC0-1.0.
