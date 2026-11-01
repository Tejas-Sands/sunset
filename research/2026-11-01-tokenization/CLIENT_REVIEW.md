# SUNSET client review — 1 November 2026

Reviewed `src/components/Stewardship.tsx`, `ContractWorkbench.tsx`, `src/lib/plans.mjs`, `mirror.mjs`, `stewardship.mjs` and the changed `src/app/page.tsx`. This is a source/control-flow review plus executed library/type checks. Browser execution remains blocked by the workspace's OS socket restrictions; the reproduction steps below are code-derived and await a real browser run. No product files were edited during this review.

## Findings

### CR-1 — P2: imported receipt feedback survives a different plan, signer or contract

**Location:** [ContractWorkbench.tsx](../../projects/sunset/src/components/ContractWorkbench.tsx), lines 7 and 11–12 at review time.

`receiptResult` is stored as a standalone string and rendered independently of `current`. Import a matching response for contract A, then change the configured contract to B: the old feedback remains visible even though the A plan is hidden. In addition, the file handler captures `current` and `signer`, awaits `f.text()`, then unconditionally sets feedback. If the signer, arguments, method or contract changes during the read, an old response can repopulate feedback after the new context cleared it.

The file caveat correctly says that imported evidence does not prove chain authenticity, but the displayed field-match result can still describe the wrong current context. No wallet action occurs automatically.

**Fix:** bind feedback to the exact captured plan, contract and expected signer; invalidate on configuration changes and discard completed reads whose request/context revision no longer matches. Render feedback only while that binding matches. Clearing a string before an await is insufficient to prevent stale completion.

**Browser regression:** import a valid response, change the contract and confirm feedback disappears; start a delayed import, change signer or arguments, then complete the old import and confirm no stale result appears.

### CR-2 — P2: changing the expected signer preserves another account's registration assumption

**Location:** [ContractWorkbench.tsx](../../projects/sunset/src/components/ContractWorkbench.tsx), lines 8–10 at review time.

The signer input clears only receipt feedback. It preserves `registered` and the existing downloadable plan. Prepare a contribution for registered account A with the checkbox selected, then change the expected signer to unregistered account B. The plan still records `contributor_registered: true` and omits B's new-account storage allowance. Even preparing a new plan retains the old checkbox value. The actual contract rejects the deposit safely, but the displayed/downloaded plan no longer matches the account-specific assumption the user reviewed.

**Fix:** when expected signer changes, invalidate the plan and reset registration to false, or explicitly bind the registration observation and plan to the observed signer. The registration assumption must be reviewed again for a new account.

**Browser regression:** prepare a registered contribution, change signer, and verify the old plan cannot be downloaded and any new plan defaults to including the storage allowance.

### CR-3 — P2: a campaign's stewardship link selects the first released resource

**Location:** released-campaign link in [page.tsx](../../projects/sunset/src/app/page.tsx) and selection initialization at [Stewardship.tsx](../../projects/sunset/src/components/Stewardship.tsx), lines 10–11 at review time.

The link labeled “See its transferable maintenance NFT” closes the campaign and changes route, without passing that campaign ID. The newly mounted stewardship component initializes its internal selection to an empty ID and falls back to `resources[0]`. After The Lantern Trail is released, following this link from The Pebble Market opens Lantern's token. The steward controls then target that first resource despite the navigation's resource-specific promise.

**Fix:** lift the stewardship resource selection into the page, or pass the campaign ID as an explicit route target and bind the component selection to it. Keep the selected title visible before any transfer or mirror action.

**Browser regression:** release Lantern, open Pebble's campaign, follow its stewardship link, and confirm Pebble's title/token ID and owner are selected. Repeat from the other resource.

### CR-4 — P3: a slow backup read can restore a key into a different campaign dialog

**Location:** the **Restore private backup** handler in [page.tsx](../../projects/sunset/src/app/page.tsx).

The handler captures campaign A, awaits the file text and checks the backup against A, then writes global `releaseKey`. Closing A and opening funded campaign B during that read clears the key, but A's completion can subsequently repopulate B's key field. Closing a modal does not cancel the read. Publication rechecks B's commitment and therefore fails closed for a different key; this is an input-context and private-data handling problem rather than a payout bypass.

**Fix:** bind the import completion to the still-selected campaign/agreement and discard it after selection or modal changes. Apply the same request-revision discipline to private imports as to receipt evidence. Do not retain or log backup contents in review evidence.

**Browser regression:** delay a backup file read, close or switch the campaign dialog, then finish the read and confirm the private key stays absent from the new context.

## Boundaries that held in the reviewed code

- Released content's play/export controls and mirror recovery do not require token ownership or payment. Ownership gates maintenance metadata and transfers. The UI explicitly labels ownership and balances as browser-local rehearsal.
- Mirror recovery requires an already-public key, checks exact manifest/ciphertext/plaintext/key commitments and resource identity, accepts only the fixed adjacent ciphertext path, uses bounded streaming, rejects redirects and omits credentials/referrer. The URL validator now rejects trailing-dot hosts and bounds the normalized URL's bytes. Controlled response tests do not prove real hosting or CORS availability.
- A verified mirror pack's play/download controls are keyed to its resource ID, manifest hash and displayed URI. Changing to another resource or URI hides those controls; an obsolete completion can still produce a generic toast, but it does not expose another resource's playable result under the new selection.
- The transaction builder allowlists contract methods, exact argument fields, hashes and integer bounds; contribution storage allowances and one-yocto NFT/mirror deposits are separate. Receipt inspection checks signer, receiver and the exact function-call fields, and distinguishes supplied-file matching from chain authenticity. It supplies no wallet or signing authority.
- RPC evidence imports are limited to 2 MiB before reading. Backup imports are limited to 8 MiB, pack input to 5 MiB, and uploaded pack data is validated instead of executed. Private backup export is explicit; normal public artifact export removes the key. The demo's retained browser keys are disclosed as sample data, not confidential production custody.
- A new steward cannot redirect the creator beneficiary, change released content commitments or revoke an existing independent copy through the reviewed local stewardship API. The contract's receiver/callback and standards behavior require their separate compiled-contract/protocol review.

## Executed verification

From `projects/sunset`, `npm run typecheck` exited 0, and `npm test` completed with **34 passed, zero failed and zero skipped**. Those tests include the actual local workflow, controlled-response mirror recovery, ownership/authority invariants, and plan/receipt matching. They do not exercise React interaction timing, DOM rendering, browser downloads or real network/protocol execution.

The four findings above identify missing client-context checks that the passing library suite does not cover. After fixes, retain this initial record and append the exact resolution and checks performed. Re-run the listed browser regressions when a browser-capable environment is available.

## Follow-up inspection

The parent implementer addressed CR-1 through CR-3, and the resulting source was inspected:

- **CR-1:** receipt feedback now retains the plan object, expected signer and contract. Rendering checks those identities; an active-context ref rejects obsolete file-read results and errors. The current-plan check also hides feedback after a contract change.
- **CR-2:** editing the expected signer resets registration to false and invalidates the plan and receipt feedback. New plans may record `expectedSignerId` explicitly.
- **CR-3:** the selected stewardship resource is lifted into page state, the campaign link sets that ID, and the controlled dropdown uses it.

These changes address the reviewed control-flow defects at source level. Their browser timing/navigation regression steps remain unexecuted in this environment. The updated application suite completed with **35 passed**. The concurrent typecheck found `TS2353` at `ContractWorkbench.tsx` for the new `signer` planner option; its declared options shape still accepted only `registered`. This was reported to the parent for correction and rechecking.

One narrow follow-up emerged from the new explicit signer field: `verifyPlannedOutcome` did not initially enforce `plan.expectedSignerId`. An executed Node probe built a plan for `alice.testnet`, supplied an otherwise matching response signed by `bob.testnet`, and called the verifier with Bob as its signer argument; it returned `success`. The client now invalidates plans on signer changes, but the library boundary must also reject a mismatch against the exported plan's optional signer binding. This was reported to the parent for a direct guard and regression test.

## Final inspected state

The remaining narrow fixes were then inspected:

- **CR-4 addressed at source level:** private backup import now validates the campaign ID, retained manifest commitment and actual decoded key commitment before exposing the key. It checks the currently selected campaign and its still-current agreement digest after the asynchronous validation, discarding completion after the dialog context changes.
- **Exported signer binding enforced:** `verifyPlannedOutcome` rejects a supplied signer that differs from the plan's optional `expectedSignerId`. A new regression test covers the mismatch. Transfer-call evidence also distinguishes a successful token return (`returned`) from an accepted transfer (`success`).
- **Typecheck corrected:** the planner's declared options include the optional signer. A fresh, separate `npm run typecheck` exited **0**. A fresh `npm test` completed with **37 passed, zero failed and zero skipped**.

All four initial findings and the signer-binding follow-up are addressed in the inspected source. No additional actionable defect remained in this review's scope. The real-browser regression steps, including delayed file reads and campaign-specific navigation, remain unexecuted; neither typecheck nor library tests prove React interaction timing or browser rendering.

## Bounded live-resource reader addendum

Inspected the subsequently added [LiveResources.tsx](../../projects/sunset/src/components/LiveResources.tsx), its parent wiring and the mirror helper's optional license commitment check. It is mounted only for a live snapshot whose contract and code hash still match the configured values; the reader previously checked chain identity and pinned catalog data to the verified code block. No signing or financial mutation was added.

The resource component is keyed by contract, snapshot height and campaign ID, preventing recovered state from carrying into another snapshot/resource. Its effect sets the active ref to true on setup and false on cleanup, including the Strict Mode cleanup/setup sequence. Async completion updates only an active component; the location selector is disabled while recovery is pending and changing location clears its recovered pack. Play and export require the recovered URI to match the displayed one. The released-key gate and inherited manifest/ciphertext limits, exact commitments, credential/referrer omission and redirect rejection remain in place. No wallet or NFT ownership is required for public recovery.

One small fail-closed gap was reported: the live catalog validator did not initially require `license_hash`, whereas the shared helper intentionally checks its optional `licenseHash` only when supplied. A malformed released catalog entry omitting this field could recover without checking an onchain license commitment despite the live panel's description. The live boundary should require a lowercase 64-digit SHA-256 license hash; the helper can remain optional for local rehearsal callers.

The new controlled-response regression rejects a supplied wrong license commitment before ciphertext retrieval. A fresh `npm run typecheck` exited **0**, and `npm test` completed with **38 passed, zero failed and zero skipped**. This addendum establishes source and local-test evidence only; it does not establish a deployed catalog, real-host recovery, DOM behavior or browser execution.

**License-boundary resolution inspected:** the shared `isCampaignCatalog` validator is now called by both `readTestnet` and `LiveResources`. It requires schema version 1, at most five bounded entries, all five SHA-256 commitments including `license_hash`, and a base64 release key for released entries. Missing license commitments, null entries and oversized catalogs are rejected by the added regression test. The live path therefore cannot silently skip the helper's optional license check.

Final fresh checks after this fix: `npm run typecheck` exited **0**; `npm test` completed with **39 passed, zero failed and zero skipped**. The bounded live-reader finding is resolved in the inspected source, with no further actionable issue identified in this reading. Actual browser and deployed-network execution remain unverified.
