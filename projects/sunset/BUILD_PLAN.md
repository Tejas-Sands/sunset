# SUNSET Implementation Plan

> Historical full design, prepared 22 October. The 1 November council replaced pending-order sales with immediate sponsorship and reduced the initial integration scope. See [the current implementation README](README.md) and [build ledger](docs/BUILD_LEDGER.md) for what is implemented and verified; this document is not a completion claim.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Execute directly in the current session; no delegation is needed.

**Goal:** Ship a playable, offline-capable educational pack whose capped testnet buyout ends in public release or the specified refund, with separately funded access services.

**Architecture:** One Next.js application on Vercel serves the interface and Node.js API. Supabase stores adult application data and artifacts; one Rust NEAR contract controls all economic state. Browsers encrypt and verify content, and licensed adults retain independent release backups.

**Tech Stack:** Next.js, React, TypeScript, Web Crypto, Supabase Postgres/Storage, NEAR Connect, near-api-js, Rust near-sdk, NEAR Sandbox. Resolve and pin compatible stable versions when implementation starts.

**Spec:** [ARCHITECTURE.md](ARCHITECTURE.md), [CONTRACT.md](CONTRACT.md), [WORKFLOWS.md](WORKFLOWS.md), [OPERATIONS.md](OPERATIONS.md).

## Global Constraints

- Initial provider cost must be zero within Free/Hobby plan eligibility and usage limits.
- Frontend and application API share one Vercel project using the Node.js runtime.
- Settlement uses NEAR testnet only; no mandatory paid inference or mainnet integration.
- Learners have no required wallet, account or uploaded individual progress.
- Packs contain validated data, never uploaded executable scripts; maximum pack size is 5 MiB.
- API metadata bodies are limited to 64 KiB; files transfer directly through Storage.
- Initially at most five demonstration campaigns, 100 orders per campaign and 50 MiB total pack data.
- Monetary JSON values are decimal strings, contract arithmetic is checked u128, and JavaScript uses BigInt.
- Funding and release deadlines are exclusive; equality takes the expired path.
- No financial deadline or eligible direct refund depends on a cron job, API or SQL row.
- The documented development window is 1 November 2026 00:00 UTC through 14 November 2026 23:59 UTC. That is 1 November 05:30 IST through 15 November 05:29 IST. This document is preparation, not an implementation or a scheduled job.

The live [hackathon instructions](https://nearhackathon.com/HACKATHON.md) were rechecked on 22 October. They state the event and submission window, but do not explicitly resolve whether pre-event product development is eligible. Retain our existing decision to reserve product coding for that window; do not represent a pre-event exception as confirmed.

## Review Focus

1. A wallet returns a transaction hash but a receipt fails: Task 7 must show verified failure or pending state without an invented payment success.
2. A final-order quote changes between display and execution: Task 3 must enforce the signed maximum and reserve the remaining cap atomically.
3. A key, manifest or export contains malformed bytes or markup: Tasks 1 and 8 must reject corruption and prevent executable pack content.
4. Two server instances consume a nonce or process the same release: Tasks 5 and 9 must produce one session consumption and one economic release.
5. The website, database or creator process disappears: Tasks 2, 4 and 8 must leave direct release/refund procedures and exported learning usable.

## Execution order and first milestone

Build the release/refund mechanism before the creator dashboard. The first milestone is **a real Sandbox campaign funded by accepted orders, released by a different key holder with no API, with a separate expired campaign refunding correctly**. A chain-only milestone is deliberately insufficient for shipping: the final browser, provider and offline checks still have to pass.

| Target dates, UTC | Tasks | Reviewable result |
| --- | --- | --- |
| Nov 1–3 | 1–4 | Safe artifact format; release/refund ledger and withdrawals exercised in Sandbox |
| Nov 4–5 | 5–6 | Adult wallet login, real scoped uploads and reviewer binding |
| Nov 6–7 | 7–8 | Full browser purchase, public release and genuinely offline game |
| Nov 8–9 | 9–10 | Managed release, projection recovery and separate access grants |
| Nov 10–12 | 11 | Provider-backed testnet lifecycle and failure checks |
| Nov 13–14 | Final evidence | Fix failures, rehearse, publish with the human and submit after exact-payload approval |

These are targets, not promises. If a core invariant fails, fix it before adding scope. Defer AI, extra assets, NFTs, bridges and cloud gaming; retain the complete release/refund, learning and access-grant workflow.

## Future source layout

All paths below are relative to `projects/sunset`; they name files to create during development, not files that exist today. Keep this design package at the root.

| Path | Responsibility |
| --- | --- |
| `package.json`, `package-lock.json`, `next.config.ts`, `tsconfig.json` | One web app, pinned dependencies and named check commands |
| `src/app/` | Catalog, game, adult workspace, campaign and balances pages; API route handlers |
| `src/lib/pack/` | Data schema, byte envelope, encryption, manifest verification and safe offline export |
| `src/lib/chain/` | Testnet configuration, views, transaction outcome checks and decimal-string parsing |
| `src/lib/auth/`, `src/lib/db/` | NEP-413 verification, adult sessions and server-only database operations |
| `src/lib/artifacts/`, `src/lib/release/` | Scoped uploads, key wrapping and bounded release processing |
| `src/components/game/`, `src/components/adult/` | Small learning runtime and adult transaction interfaces |
| `contracts/sunset/src/{lib,model,campaigns,orders,release,withdrawals,grants}.rs` | Contract entry points and bounded economic records |
| `contracts/sunset/tests/` | Focused invariant tests and actual asynchronous Sandbox scenarios |
| `supabase/migrations/` | Tables, constraints, RLS, atomic nonce consumption and job leases |
| `tests/`, `scripts/`, `evidence/` | Browser/API checks, recovery commands and redacted verification records |

Do not create framework layers merely to match this map. Keep route handlers thin and colocate small helpers; split files when the responsibilities actually require it.

Create these verification entry points with their owning tasks: `npm test` for TypeScript unit/API checks, `npm run typecheck`, `npm run build`, and `npm run test:e2e` for browser scenarios. For Rust use `cargo fmt --manifest-path contracts/sunset/Cargo.toml --check`, `cargo clippy --manifest-path contracts/sunset/Cargo.toml --all-targets -- -D warnings`, and `cargo test --manifest-path contracts/sunset/Cargo.toml -- --test-threads=1`. Sandbox test modules must actually execute receipt scenarios in that last command. These commands are requirements for future tooling; they are not available or recorded as passing today.

## Task 1: Specify and exercise the exact pack bytes

**Files:** `src/lib/pack/{schema,envelope,manifest}.ts`; `tests/pack.test.ts`; `tests/fixtures/crypto-v1.json`; web package configuration.

**Interfaces:** `validatePack(input: unknown): LearningPackV1`; `encryptPack(plaintext: Uint8Array, key: Uint8Array): Promise<Uint8Array>`; `decryptPack(envelope: Uint8Array, key: Uint8Array): Promise<Uint8Array>`; `keyCommitment(key: Uint8Array): Promise<string>`. Hashes are lowercase 64-character hex. Keys are raw 32 bytes; wire encoding is base64.

- [ ] Write tests for valid pack round-trip, wrong key, changed authentication tag, malformed lengths, a pack exceeding 5 MiB, and attempted embedded scripts/remote resources. Require validation after decryption too.
- [ ] Define v1 envelope as ASCII `SUNSET01`, a fresh 12-byte AES-GCM nonce, then ciphertext with its 16-byte tag. Hash the complete envelope. Manifest hashes bind exact uploaded UTF-8 bytes, not a reserialized object.
- [ ] Implement with Web Crypto and a small strict data schema. Restrict the first game to integer arithmetic questions, plain-text explanations and bounded lists; reject unknown executable fields and unsafe image formats.
- [ ] Publish a non-secret vector using bytes 0 through 31 as the key and the exact `SUNSET:KEY:1:` prefix. Record raw bytes, base64 and resulting SHA-256 for Rust parity. Never reuse this public test key for hosted content.
- [ ] Define `npm test`, `npm run typecheck` and `npm run build`; run the pack tests and typecheck. Pin the selected runtime and dependencies in the lockfile. Save the reviewable changes locally.

**Done when:** authenticated round-trip and every corruption case pass; the fixture records exact bytes. No generated lesson quality is implied.

## Task 2: Prove independent public disclosure in Sandbox

**Files:** contract Cargo/toolchain configuration; `src/{lib,model,campaigns,release}.rs`; `tests/release.rs`; shared crypto fixture from Task 1; `scripts/direct-release.md`.

**Interfaces:** Implement `create_campaign`, `approve_campaign`, `cancel_draft`, `publish_release`, `get_campaign` and `get_release` from CONTRACT.md. `publish_release` accepts base64 decoded to exactly 32 bytes. Read responses expose schema version, immutable terms, agreement digest, effective state and public key after release.

- [ ] Write failing tests for wrong reviewer/digest, wrong key, premature/late disclosure, changed terms and unauthorized cancellation. Assert the Rust key commitment equals Task 1's vector.
- [ ] Define agreement digest v1 as SHA-256 of Borsh-serialized immutable terms, including version, testnet identifier, contract account, campaign ID and the terms in CONTRACT.md's actor/artifact/price/deadline order. Record the exact field order and integer widths in a fixture before implementing a client encoder.
- [ ] Implement draft activation, immutable identities and exclusive chain-time boundaries. Preallocate the fixed 32-byte public-key field and creator credit record so disclosure requires zero attached storage deposit.
- [ ] Add a test-only fixture helper to construct a funded campaign without exposing a funding-bypass method in the deployed ABI. A teacher account publishes; only the fixed creator receives credit. Repeated disclosure never adds credit.
- [ ] Run focused Rust tests and a Sandbox call from the teacher account. Record actual receipt outcomes. Write direct disclosure instructions requiring only the backup, own wallet/CLI and functioning RPC. Task 3 replaces fixture funding with real orders.

**Done when:** disclosure is independent of Vercel and the creator's process; beneficiary substitution, key mismatch and deadline equality are rejected.

## Task 3: Fund through orders and prove both refund paths

**Files:** `contracts/sunset/src/orders.rs`; campaign/release integration; `tests/{orders,refunds,accounting}.rs`.

**Interfaces:** `open_order`, `accept_order`, `cancel_expired_order`, `claim_buyout_refund`, `get_order`, `get_contribution`, `get_balance` and bounded list views. Use CONTRACT.md's method arguments; max-payment, storage allowance and economic portions remain distinct.

- [ ] Write tests asserting `settled + reserved <= target`, a stale maximum cannot be exceeded, partial final orders credit excess change, fully reserved capacity rejects another buyout order, and only the buyer accepts once.
- [ ] Implement checked u128 accounting, actual-growth storage charging, bounded IDs and per-buyer contribution/refund records. Reject repeated deposit-bearing create calls rather than retaining another deposit. Check acceptance deadline against the campaign deadline.
- [ ] Add real-order Sandbox scenarios: ten accepted 1-NEAR orders produce 2 service and 8 escrow; independent release produces exactly 8 creator credit. A five-order campaign expires with 1 service earned and 4 refundable. A fully funded campaign missing disclosure refunds buyout only.
- [ ] Test unaccepted order expiry refunds both portions and frees capacity; duplicate refunds do nothing economically; released funds cannot refund; expired refundable campaigns cannot release.
- [ ] Run invariant sequences including reordered/duplicate calls, timestamp equality and arithmetic extremes. Assert the full economic conservation equation after each successful transition. Run all contract tests so far.

**Done when:** the first milestone's release and both campaign refund outcomes use actual orders, with no backend balance authority.

## Task 4: Withdraw without duplicate payouts

**Files:** `contracts/sunset/src/withdrawals.rs`; `tests/withdrawals.rs`; direct recovery instructions.

**Interfaces:** `withdraw(amount)`, private `on_withdraw_complete(operation_id)` and a withdrawal-operation view. One pending operation per owner; an operation records amount, state and diagnostic identity.

- [ ] Write tests for successful native transfer, confirmed transfer failure, external callback calls, duplicate callbacks, duplicate withdrawal and insufficient prepaid callback gas.
- [ ] Move credit to a preallocated pending operation before scheduling transfer; reserve sufficient callback gas; finalize success or recredit confirmed failure once.
- [ ] Force callback failure in Sandbox and assert funds remain pending, with no guessed recredit or second payout. Document how to inspect receipts. Do not claim automatic recovery unless a separately verified result-based mechanism is actually implemented.
- [ ] Reconcile deposits, pending balances, escrow, grants, credits, in-flight and successful withdrawals. Keep gas/storage outside the equation; unsolicited transfers are surplus.
- [ ] Run Rust unit and Sandbox checks. Add and exercise direct refund/withdraw instructions with the web app absent.

**Done when:** confirmed outcomes settle once; uncertain callback outcomes stay visibly pending rather than paying twice.

## Task 5: Authenticate adults and establish the real database

**Files:** `supabase/migrations/0001_core.sql`; `src/lib/{auth,db}/`; auth route handlers; `tests/auth.integration.test.ts`; `src/lib/chain/config.ts`.

**Interfaces:** `issueChallenge(accountId: string, origin: string): Promise<Challenge>`; `verifyLogin(input: SignedChallenge): Promise<SessionCookie>`; `requireAdult(request: Request): Promise<AdultIdentity>`. Challenges use 32 random bytes, five-minute expiry and exact domain/recipient/network/account binding; sessions last twelve hours.

- [ ] Check installed NEAR Connect APIs and prove an actual testnet wallet supports NEP-413 and transactions before building the adult UI. Implement independent backend Ed25519 verification and current full-access key checks.
- [ ] Write failing integration checks for replay, two simultaneous nonce uses, expired/wrong origin/network/account messages and restricted-key login. Exactly one concurrent nonce consumption may succeed.
- [ ] Provision or reuse one eligible Free Supabase resource through supported tooling. Apply WORKFLOWS.md's tables, unique identities, decimal-text constraints, deny-by-default RLS and atomic session/job functions. Verify server credentials never reach client bundles or logs.
- [ ] Implement opaque secure/httpOnly/sameSite sessions with hashed tokens, origin checks, 64-KiB bodies and database-backed short-lived rate limits. Keep development HTTP cookie exceptions local only.
- [ ] Run integration checks against local Postgres/Supabase and a real Free resource. A valid actual wallet login must work. Record region and resource identity privately; do not fabricate a successful provider setup if account access is unavailable.

**Done when:** adults can authenticate and edit their own drafts, while learners remain unauthenticated and direct unauthenticated DB access is denied.

## Task 6: Upload, review and bind the exact artifact

**Files:** artifact helpers, project/upload/finalize/agreement routes, creator/reviewer pages and `tests/artifacts.integration.test.ts`.

**Interfaces:** `authorizeUpload(actor, projectId, manifest): Promise<ScopedUpload>`; `finalizeArtifact(actor, projectId): Promise<ArtifactVersion>`; `wrapContentKey(key, projectId, artifactHash): Promise<KeyEnvelope>`. Key wrapping binds identity and version to authenticated encryption.

- [ ] Test foreign-project edits, foreign object prefixes, overwrite attempts, malformed packs, oversize objects, hash mismatch and draft changes after activation.
- [ ] Implement direct Storage upload with overwrite disabled, provider-supported token lifetime, bucket limits and content-addressed paths. Finalization reads only our configured bucket/path and verifies actual ciphertext size/hash; no arbitrary URL fetch.
- [ ] Build creator preview/encryption, managed-key opt-in and private backup export. Require backup acknowledgment before launch; do not log keys or tokens.
- [ ] Build reviewer download/decryption, exact-hash preview and own-wallet approval for the onchain digest. A reviewer cannot approve a different artifact by changing SQL metadata.
- [ ] Exercise one real upload and approval, and the rejection cases, against the actual provider. Preserve explicit reviewer/rights assumptions in UI copy.

**Done when:** the reviewer approves the exact uploaded bytes, and creator/reviewer both possess usable independent backups.

## Task 7: Complete purchase, delivery and verified balances

**Files:** chain view/outcome helpers; catalog/campaign/balances pages; quote, licensed-download and reconcile routes; `tests/purchase.integration.test.ts`.

**Interfaces:** `readCampaign(id): Promise<CampaignView>`; `verifyMutation(ref: TransactionReference): Promise<VerifiedOutcome>`; `reconcileKnownIds(ids): Promise<ProjectionResult>`. Outcomes distinguish pending, verified success and verified failure. Amounts stay strings until BigInt arithmetic.

- [ ] Test wallet rejection, returned hash with failed receipt, wrong receiver/method/caller, stale quote, RPC disagreement and refresh after delivery failure. Never open another order merely to retry a download.
- [ ] Show exact service/buyout split, authorized maximum, storage and gas separately. Verify testnet and configured code hash; disable economic actions when verification is unavailable or stale.
- [ ] Implement current pending/accepted entitlement for the buyer or fixed adult licensee; return no key to another account or expired pending order. Buyer signs acceptance only after inspecting delivery.
- [ ] Reconcile finalized contract outcomes and affected records. Use shared catalog caching, bounded visible-tab polling and backoff; preserve large integers in SQL projections.
- [ ] Exercise purchase, acceptance, claim and withdrawal in the browser against testnet. Verify a deliberately altered SQL total cannot change balances or release eligibility.

**Done when:** every displayed payment result has a verified contract outcome, and the adult can recover from refresh/rejection without duplicate economic effects.

## Task 8: Make the game and independent offline export work

**Files:** game components, free intro data, pack export helper, service worker and `tests/offline.spec.ts`.

**Interfaces:** game consumes validated `LearningPackV1`; `createOfflineHtml(pack: LearningPackV1): Promise<Blob>` embeds our reviewed runtime and safely encoded data. Progress has explicit local export/import and no server identity.

- [ ] Write checks for correct/incorrect answers, replayable completion, keyboard operation, hostile text such as closing script tags, altered ciphertext and plaintext mismatch.
- [ ] Implement a short integer-maths puzzle game with objective and feedback, free intro and public released-pack verification. Keep wallet controls in the adult workspace.
- [ ] Implement the self-contained HTML export before optional PWA caching. Embed no remote fonts, model calls or storage URLs. Render content as text, never execute lesson fields.
- [ ] Add PWA caching only for known game shell/chosen packs; exclude adult APIs, private downloads, sessions and wallet callbacks. Explain local storage loss and provide explicit progress export.
- [ ] Open the export from a local file in a fresh browser context with network disabled, complete the game and inspect requests. Confirm no learner data reaches DB/chain. Run hostile-content checks in that same exported runtime.

**Done when:** a new learner plays free online, and an exported pack remains playable independently of Vercel, Supabase, wallets and AI.

## Task 9: Add bounded managed release and rebuild projections

**Files:** release helpers/routes, atomic job SQL, maintenance route, `scripts/rebuild-projections.ts`, release integration checks.

**Interfaces:** `processRelease(campaignId: string): Promise<ReleaseJobResult>` processes at most one leased job; `rebuildProjections(cursor): Promise<NextCursor>` reads bounded contract pages of at most 20 records.

- [ ] Test two workers leasing one job, release success with a lost HTTP response, wrong agreement/code hash, expired release deadline, RPC disagreement and exhausted retry budget.
- [ ] Create one job per network/contract/campaign/digest; lease atomically. Recheck fresh contract state before signing or retrying. Only `publish_release` on the configured testnet contract with zero attached deposit is allowed.
- [ ] Keep all requests short: ordinary API target 15 seconds, reconciliation slice 20 seconds. Process bounded work; optional daily authenticated maintenance never controls refund timing.
- [ ] Test the actual release access key cannot withdraw, change beneficiaries or call another contract. Remove managed-signing access from the environment and prove a teacher still releases directly.
- [ ] Delete disposable SQL projections and rebuild economic records from paginated contract views. Do not claim this restores deleted content, drafts or private key envelopes. Run the release and rebuild checks.

**Done when:** automation is convenient, idempotent and bounded; both independent disclosure and contract-state recovery are demonstrated.

## Task 10: Add finite sponsored access services

**Files:** `contracts/sunset/src/grants.rs`; grant tests; evidence/claim API; adult grants page.

**Interfaces:** `create_access_grant`, `approve_service`, `refund_unused_grant`, grant views and `POST /api/grants/{id}/claims` as specified. One sponsor/provider/approver per grant; claim ID and evidence hash bind each approval.

- [ ] Write contract checks for wrong approver, duplicate/conflicting claim IDs, overflowing unit costs, cap exhaustion, expiry equality and unused-budget refund to the fixed sponsor.
- [ ] Implement grant accounting separately from buyout balances. Re-run the conservation checks with interleaved orders, grants and withdrawals.
- [ ] Store small adult evidence documents; show purpose, unit price, approved spend and remaining budget. Only the adult approver's wallet authorizes payment.
- [ ] Demonstrate one labeled teacher-support or deployment-check service, provider credit and remaining-budget refund. No claim of real school delivery or learning improvement follows from a signed demo receipt.
- [ ] Run contract and browser integration checks, including an expired grant while offline packs continue working.

**Done when:** support can be funded and settled within a finite separate budget without refilling the completed asset buyout.

## Task 11: Verify the complete free deployment and evidence

**Files:** `vercel.json` only if required; private environment setup; `evidence/acceptance.json`; reproducible build record; runnable README and recovery guide.

**Interfaces:** the same deployment serves pages and `/api/*`; actual network, contract account, expected code hash and artifact commitments are recorded. No example identity is presented as a live resource.

- [ ] Recheck current provider terms and supported runtime versions. Keep one eligible Hobby app and one Free Supabase resource, no paid add-ons or mandatory AI. Record configured quotas and actual usage.
- [ ] Run `npm test`, `npm run typecheck`, `npm run build`, Rust formatting/lint/unit checks and Sandbox integration checks. Add the browser runner command to package scripts and run the provider-backed lifecycle.
- [ ] Exercise every OPERATIONS.md acceptance row. Capture receipt IDs and redacted browser/network evidence; failed or unrun checks remain explicitly marked. Demonstrate the API stopped during teacher disclosure and network disabled during offline play.
- [ ] Reproduce the contract artifact from recorded source revision, lockfiles and toolchain. Keep development deployments labeled upgradeable. A separate final immutable deployment and removal of external controls require verification and the human's explicit signing decision; never remove keys silently.
- [ ] Write judge instructions as actions with observable results: play intro, inspect agreement, purchase/deliver, fund/release, independently verify/open export, inspect refund and service-grant examples. Claim only tracks supported by demonstrated behavior; Open Innovation is the baseline.
- [ ] Before the deadline, prepare repository/demo/submission materials. The human decides publication, publishes their X demo, supplies actual personal/payout details and confirms the exact final JSON before submission. Re-read the live rules then; do not send a placeholder submission.

**Done when:** the full lifecycle works on the chosen providers, recovery and offline tests pass, costs remain within the initial envelope, and evidence distinguishes implemented behavior from future ideas.

## Current execution state

Plan written on 22 October 2026 after the user approved proceeding with SUNSET. All implementation checkboxes remain open. No product source, dependency installation, hosted resource, deployed contract or passing implementation-test claim is created by this document. Product development remains reserved for the agreed window; there is no automatic future execution configured.
