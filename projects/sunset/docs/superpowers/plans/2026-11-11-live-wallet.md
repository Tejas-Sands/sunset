# SUNSET Live Wallet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Replace the public financial rehearsal with an integrated live NEAR testnet app and a substantial technical resource library.

**Architecture:** The static Next app reads a pinned existing contract and uses NEAR Connect for explicit wallet-approved writes. Shared data-only guides power real resource routes and exact offline exports; existing crypto and transaction planners stay authoritative.

**Tech Stack:** Next 16.4.6, React 19.2.4, TypeScript, native CSS/SVG, Web Crypto, `@hot-labs/near-connect` 0.12.0; existing Rust/WASM unchanged.

**Spec:** `projects/sunset/docs/superpowers/specs/2026-11-11-live-wallet-design.md` (operator approved).

## Global Constraints

- Existing `sunset.shiftultra.testnet`; reviewed code hash `9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx`; owner `shiftultra.testnet`.
- No contract redeployment, operator signatures, completed-action replay, wallet imports, shared-auth changes or assistant push.
- Owner publishing, five campaign slots, 100 participant slots; all financial data comes from real RPC reads.
- Preserve original samples, private backups, original WASM and historical evidence. No private keys or unpublished release keys in persistent browser storage or public exports.
- Reuse strict pack validation, mirror recovery and transaction plans. Reader needs no wallet. Keep logo/home links and both themes.

## Review Focus

- Wallet account changes during async preflight: the old account must never be signed or displayed as the current balance (Task 3).
- RPC outage or changed code: free resources remain readable and finance fails closed (Tasks 1/4).
- A wallet redirects or throws after submitting: preserve a digest-bound pending intent without a secret and never auto-resubmit (Tasks 1/3).
- Native transfer succeeds late or fails in a callback: credit and actual paid status stay distinct (Tasks 1/4).
- Resource deep links, small screens and unavailable storage: correct resource opens; guide still works and original downloads remain intact (Tasks 2/4/5).

### Task 1: Live action and receipt core

**Files:** create `src/lib/live.mjs`, `tests/live.test.mjs`; consume `src/lib/chain.mjs`, `src/lib/plans.mjs`, `src/lib/mirror.mjs`.

**Interfaces:** `DEPLOYMENT`; `loadLiveSnapshot(signer?)` returns `{contract,network,codeHash,blockHash,height,timestampNs,config,campaigns,account}`. `buildLivePlan(snapshot,signer,method,args)` validates live roles/eligibility and returns the existing plan. `prepareLiveAction(method,args,signer,key?)` re-reads and recovers bytes for create/review/release/mirror actions before returning `{plan,snapshot}`. `createIntent(plan,snapshot)` retains signer/action/args digest and relevant paid baseline. `verifyIntentOutcome(outcome,intent)` binds RPC receipts to intent. `readTransaction(hash,signer)` queries testnet; `withdrawalState(intent,account)` distinguishes pending/paid/failed.

- [x] Write tests for pinned network/code/block/config, malformed amounts, exact registration deposits, campaign/role restrictions, commitment recovery, receipt binding and pending withdrawal handling.
- [x] Run `node --test --test-isolation=none tests/live.test.mjs`; observe missing behavior failures.
- [x] Implement the minimal pure guards and async RPC/preflight functions using existing planners/crypto.
- [x] Run the focused tests and `npm test`; both must pass. Commit the completed core.

### Task 2: Technical commons and shared publishing preparation

**Files:** create three `public/packs/` AI/math guides, `src/lib/library.mjs`, `tests/library.test.mjs`, `src/lib/publishing.mjs`; modify `scripts/prepare-campaign.mjs`; create `scripts/export-library.mjs` and add build export command.

**Interfaces:** `resources` entries `{id,title,description,topic,duration,formula,pack,href,download,sources}`; `resourceById(id)` returns an entry or undefined. `prepareOnchainCampaign(pack,options,now?)` is moved intact into a browser-safe module and re-exported by the CLI for compatibility. Library exports are exact `createOfflineHtml(pack)` outputs under `/library/<id>.html`.

- [x] Test strict valid guides, independent attention/gradient/rank arithmetic and full exact self-contained exports; test an untrusted/unknown resource ID resolves to nothing.
- [x] Run focused tests to observe missing resources/exports; implement original CC0 guides with references to the verified primary sources.
- [x] Extract preparation logic without changing its existing CLI interface or backup permissions. Run `tests/prepare.test.mjs`, `tests/library.test.mjs` and `npm test`; commit the tested library/preparation batch.

### Task 3: Wallet connection and complete account actions

**Files:** add the pinned SDK to `package.json`/lock; create `src/components/WalletProvider.tsx`, `src/components/CampaignActions.tsx`, `src/components/CreatorStudio.tsx`; replace public `src/app/app/page.tsx` while retaining the old rehearsal component privately in source if necessary.

**Interfaces:** wallet hook exposes `{accountId,connecting,connect,disconnect,submit,pending,checkPending,message,error}`. `submit(method,args,key?)` invokes Task 1 fresh preflight, checks the account again, persists a secret-free intent before the wallet call, and verifies fetched RPC receipts; it never mutates financial state optimistically. `CampaignActions({campaign,snapshot,onRefresh})` exposes only applicable real actions. `CreatorStudio({snapshot,onRefresh})` uses Task 2 preparation and Task 1 preflight.

- [x] Add a meaningful signing orchestration test for account switching, cancellation/interruption, duplicate submission prevention and digest-only recovery; observe RED before implementing orchestration.
- [x] Verify official SDK tarball integrity, install 0.12.0 without scripts, and configure testnet/supported signing wallets with MyNearWallet excluded and automatic login prompts disabled.
- [x] Implement connection restore, explicit chooser/disconnect, the real action forms, owner publishing/backup downloads, reviewer inspection, key release, claim/refund/withdraw and token/mirror controls.
- [x] Run focused orchestration, application and type checks. No human wallet transaction is part of automation. Commit once these functional controls are integrated.

### Task 4: Coherent protocol UI and actual resource routes

**Files:** replace `src/app/page.tsx`; create `src/components/Protocol.tsx`, `src/app/protocol.css`, `src/app/resources/[slug]/page.tsx`; update layout imports/metadata; integrate app display from Task 3.

**Interfaces:** shared `SiteHeader`, `Arrow`, and `ResourceArt` use existing mark/theme control. Resource routes statically generate from Task 2 metadata and render the original guide reader. Public app navigation uses real views and maps useful legacy links to their corresponding live destinations.

- [x] Update static page assertions for the real guides, working routes/downloads, correct logo links and absent rehearsal/manual verification surfaces; watch old build fail the new expectations.
- [x] Implement shared CSS/SVG protocol visuals, semantic states, responsive layout and reduced-motion behavior. Show actual loading/error/empty funding states and keep historic campaigns in the onchain archive.
- [x] Build, run static pages and inspect both themes in an owned browser where available. Check no horizontal overflow, keyboard focus and readable technical formulas. Commit integrated UI after appropriate checks.

### Task 5: Full gate, review and delivery

**Files:** update `scripts/test-browser.mjs`, `scripts/check-pages.mjs`, README/current runbooks/BUILD_LEDGER; add dated evidence.

- [x] Replace obsolete public rehearsal assertions with actual resource navigation, themes, search/progress, wallet chooser open/close, exact downloads and cold offline library use. Keep legacy standalone-byte coverage and hard nonzero failures; no skipped success.
- [x] Run `npm run check`, production build, static pages and dependency advisories; verify contract source/artifact hashes are unchanged. Run browser scope available in this environment and explicitly record blocked/controlled/live distinctions.
- [x] Get a fresh whole-change review against the spec, including the Review Focus cases. Fix important defects with reproducing tests, then run the relevant final gate.
- [x] Update current documentation/evidence and record every task's completion/verification. Commit all verified changes, leave worktree clean and give the operator the authorized root push command. Do not claim deployment or new signed settlement occurred.

All paths above are relative to `projects/sunset/` except the fully qualified spec/plan paths. Existing repository author and `.sunset-git` workflow apply. The operator's “Approve and implement” authorizes continuous execution; routine execution-method choices do not require another approval round.

Execution completed locally on 11 November 2026. Final gate: 109 application tests, types, nine model workflows, eleven WASM host scenarios, nineteen native Rust tests/format/Clippy/rebuild, production export and static pages. Fresh whole-change review was addressed in one reproducing-test fix pass. The strict standard HTTP browser runner failed at denied local socket creation; owned-browser component/live-read/chooser and controlled-wallet checks are recorded separately in evidence/live-wallet-2026-11-11.json. New CI/deployed smoke and human signing remain post-deployment acceptance, not claimed successes. Operator pushes verified local commits under AGENTS.md.
