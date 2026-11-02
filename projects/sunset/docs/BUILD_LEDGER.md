# SUNSET build ledger — 1 November 2026

Existing approved direction: SUNSET, as recorded October 22. User requests council audit then main product. At the first build the standard .git mount was empty/read-only. Subsequent user authorization established README-first history in .sunset-git, with small verified local commits; GitHub access remains blocked.

Ruling: replace pre-acceptance sales with immediate capped sponsorship. The former delivered a reusable copy before acceptance and permitted full refund by refusal. Sponsorship funds a specified public release; preview is free, contributions buy no secret copy.

Ruling: first deliverable is a complete local rehearsal plus a deployable NEAR WASM and explicit live configuration. Provider credentials and network downloads unavailable. Do not represent browser simulation as testnet settlement. Keep original multiweek architecture as future design, not implemented claims.

Ruling: use original Next.js stack if packages can be recovered from read-only local cache. No new external accounts or paid resources. Rust uses minimal NEAR host ABI with cached serde/Borsh, because near-sdk cannot be downloaded. Native tests do not substitute for Sandbox.

Work: council independent assessments → anonymized peer review → synthesis; strict encrypted pack + independent offline game; sponsorship release/refund ledger and state tests; compiled contract; campaign UI, creator/reviewer workflow, budgets, recovery; browser/build verification and candid delivery record.

Completed locally: 24 JavaScript assertions; strict authenticated pack encryption; independently recoverable self-contained game; static Next.js app/typecheck/build; compiled NEAR contract with 10 Rust tests and 3 actual-WASM host scenarios; independent contract and frontend reviews. Exact test commands and limits are in evidence/verification.json.

Review rulings: fix RPC view-context imports; curate campaign creation to fixed owner; retain and disclose 100-account capacity; bind asynchronous reviewer and testnet results to the verified agreement/configuration; neutralize CSV formulas; expose exact uploaded pack for review; keep rehearsal budgets/agents outside claims about current WASM.

Not complete: real browser/mobile/offline execution (OS socket restrictions), NEAR Sandbox protocol gas/receipts/callback failures, live deployment and wallet signing, independent educator review, actual sponsor feedback and final public submission. No resources provisioned or publication performed.

## Tokenization completion batch

The user delegated all non-deployment work and asked for researched tokenization. Primary-source comparisons selected a nonfinancial stewardship NFT; revenue/copyright fractions, token sales and service vouchers were rejected/deferred as different products. Full design/plan is under docs/superpowers at repository root.

Implemented NEP-171 core/events, NEP-177 metadata and NEP-181 enumeration, one token per released campaign, fixed-capacity owner/mirror storage, separate security deposits and current-owner-only maintenance. Creator/reviewer IDs must differ; different IDs do not prevent collusion. Reference-standard callback behavior is retained and its receiver-reacquisition caveat is documented/tested. Fresh state-layout-2 deployment is required; no migration is supplied.

Implemented exact schema-2 manifests plus adjacent ciphertext.sunset, bounded credential-free mirror retrieval and all original commitment checks, including a supplied onchain license hash. Existing schema-1 files and local packs/backups are preserved. Added stewardship interface, read-only configured-contract public resources, unsigned core/NFT transaction workbench and exact signer/action evidence matching. Supplied RPC files are not chain-authenticity proof.

Prepared nine real local workflow scenarios, source/artifact digest validation, canonical path-remapped binary reproducibility across two separate checkouts, a checks-only CI workflow, demo/threat/content guides and an unsubmitted draft. Current final counts/artifact hashes are in evidence/verification.json. Browser/protocol and live/deployment evidence remain explicitly unverified. No account, hosting, provider, signed transaction or submission was created.

## Public landing and visual refresh

User requested a stronger landing page and said the interface looked mid. Added a static public homepage at `/`, moved the unchanged workspace business logic to `/app/`, and preserved browser-local state. The landing uses original generated book/sunset artwork, locally hosted licensed Geist, distinct resource scenarios, creator/stewardship sections and native FAQ controls. Workspace CSS improves type, spacing, contrast and responsive navigation.

Prototype and sample-funding disclosures remain explicit and readable. No adoption statistics, testimonials, wallet connections, funding events or registered trademark claims were fabricated. Static export trailing-slash routing and allowlisted query destinations are verified after build. App/server browser launch still fails under the current socket restrictions; source/static-output checks do not establish visual browser QA.

## Deployment authorization and access check

The user has now requested deployment of the whole product. This supersedes the earlier exclusion of deployment work. Keep the initial deployment on free hosting and NEAR testnet; no mainnet or paid resource is requested.

Fresh checks against source revision `5810dddbc647a4d8e0bcfcd970c2bc5df473d51f` passed: `npm run check` (39 application tests, type generation/typecheck, nine local workflow scenarios, source/artifact digests and ten compiled-Wasm host scenarios), `npm run build`, and `npm run test:pages`. These do not establish real browser or protocol execution.

A Vercel Hobby project named `sunset` was created through the connected account. Uploading the frontend was refused with HTTP 403 because the connection lacks the owning team's grant; the provider's team-authorization link was supplied to the user. No deployment or live URL exists. A 54-file static publication payload was prepared privately from the verified export, with content hashes and no release backups/secrets. This can publish the landing and rehearsal; live browser signing still requires implementation and actual receipt reconciliation.

The GitHub connector now responds, but is authenticated as `vedantssj`; lookup of the intended `Tejas-Sands/sunset` returns 404. That does not distinguish a missing repository from inaccessible private contents. Do not publish under a different owner or claim a push succeeded. Actual funded testnet account names and wallet signers remain missing. See [deployment sequence and remaining gates](DEPLOYMENT.md).

## Persistent Git publishing and Vercel dashboard setup

The user requested a single setup path instead of repeating expiring Vercel consent links and authorized use of a temporary GitHub token. This executor cannot resolve `api.github.com` or `github.com`, and has no configured network proxy; the token was not validated or persisted. Do not label it invalid based on a network failure. The connected GitHub app still uses its own configured account.

Prepared a user-local publishing helper using Git/GitHub CLI, a hidden token prompt, explicit Tejas-Sands identity/repository checks and ordinary fast-forward publication of the preserved README-first history. Remote publication still requires running it in a network-enabled terminal. The runbook now describes a persistent GitHub-to-Vercel connection, with Next.js preset, `projects/sunset` root, `npm run build`, `npm ci`, Node 24.x and framework-default output directory. This corrects the earlier ambiguous repository-host output setting: generic static hosting serves `out/`; Vercel's Next.js integration handles that export itself. No new consent link, paid resource, live account or deployment was created in this batch.

Fresh verification: `npm run check` passed 47 JavaScript tests, types, nine local workflows, artifact/source digests and ten compiled-Wasm host scenarios. The eight added publishing tests use real local Git histories with simulated GitHub/network responses. They cover wrong identity, authentication/non-404 API failure, empty public-repository creation, preserved README-first history, existing-main fast-forward, unrelated history/default branch/origin, missing write permission, dirty files and post-push commit mismatch. Synthetic credential output is checked under shell/API/Git tracing; no real token was used. Shell syntax, documentation links and changed-text credential scans passed. No live publication is claimed.

## Testnet showcase preparation — 2 November 2026

The operator supplied wallet `shiftultra.testnet`, reported a balance of two testNEAR, and provided the published frontend URL `https://sunset-lemon.vercel.app`. They will push completed local commits themselves. GitHub plugin login changes are no longer part of this workflow. Public frontend/repository reports supersede historical publication negatives above; actual testnet deployment remains unverified.

Official NEAR storage pricing is 10^19 yoctoNEAR per byte. The 266,190-byte Wasm alone represents roughly 2.6619 testNEAR before account allowances, state and gas, so the reported two-token balance cannot fund this deployment. The guide uses a free five-token faucet top-up, a proposed dedicated contract funded with four testNEAR, two proposed role accounts with 0.5 each, and a 0.1-testNEAR campaign. All proposed accounts remain uncreated until the operator's signed commands succeed. Accounts controlled by one operator are demonstration roles, not independent humans.

Prepared `lantern-trail-testnet-v1` with deadline 10 November 00:00 UTC and a 24-hour release window. Exact manifest and encrypted bytes plus an identical second location are under `public/testnet/`; the release key, backup, unsigned terms and role arguments are retained only in the ignored private directory. Independent local recovery passed. Two paths on the same host demonstrate mirror selection, not independent hosting. The [showcase guide](TESTNET_SHOWCASE.md) uses documented CLI 0.30.1 syntax; those CLI/network actions cannot be executed in this socket-restricted environment. No wallet access key, account, signed transaction, deployed contract or new hosted bytes is claimed.

Showcase preparation verification passed: 47 application tests, types, nine local scenarios, artifact hashes, ten Wasm host scenarios, production export and static pages. Both public locations match the prepared bytes and build export; independent HTML recovery, seven unsigned deposit plans, 17 shell blocks in Bash/Zsh, documentation links, private file permissions and exclusion of the actual prepared release key from the export were checked. These checks make no claim about executed CLI syntax, live hosted bytes, signatures or protocol receipts.

The operator then reported HTTP 404 / `Not Found` from the documented faucet POST endpoint. No funding is claimed. Replaced that failing runbook step with the NEAR-docs-linked browser faucet, whose NEAR/address/amount/request form was reachable through the web reader. Its current amount limit, request fulfillment and credited balance remain unverified. The endpoint's failure cause is unknown; no replacement API route was guessed.

## Whole-contract check before deployment — 2 November

The operator reports seven testNEAR and explicitly requested assistant deployment after reviewing the entire contract. Three independent agents examined money/state transitions, host ABI/runtime boundaries and NFT behavior, then a separate patch review checked the fix. No actionable theft, duplicate-payment or authority defect was established. A low-severity URL validation defect was reproduced and fixed with a shared bounded HTTPS/DNS validator for both original manifests and mirrors. Three native regressions failed before the fix and passed afterward; rejected calls preserve full serialized state.

Retained an additional compiled-Wasm maximum-capacity scenario: five campaigns, 100 accounts, release credits arriving during a pending withdrawal, confirmed failure restoration, both remaining refunds and complete payout conservation. Nineteen native tests and eleven Wasm-host scenarios passed, along with 47 application tests, types, nine local workflows, formatting and native/Wasm Clippy. Protocol gas and actual balances/receipts remain unverified; the host tests report zero consumed gas and do not meter the scheduled 15-Tgas callbacks.

The revised 270,188-byte artifact has SHA-256 `7a65f94c90eb11c7e7865362ea3386656e9d89334512b12b7ce313e5ed606c6f` and expected Base58 code hash `9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx`. Independent source/target directories produced byte-identical output with the pinned compiler/dependencies. Active deployment guides and preparation evidence now pin that artifact; historical hashes above identify prior revisions. The encrypted learning resource and private backup were preserved.

Actual deployment remains blocked by this executor: `near`/Sandbox are absent, RPC/npm DNS fails, and no imported signer has been verified. The execution policy rejected even a read-only RPC check requested outside the sandbox because sandbox escalation is disabled. No wallet keys were requested/read and no deployment transaction or token transfer was submitted. Full scope, review evidence, remaining gates and the execution check are in [CONTRACT_PREDEPLOY_REVIEW.md](CONTRACT_PREDEPLOY_REVIEW.md).

Aligned browser/preparation URL checks with the hardened contract, including canonical DNS labels, nonzero ports and empty-fragment rejection. The additional regression failed first and passed after correction; normalized valid URLs remain supported. The application suite now passes 48 tests. This changes no resource commitments or private backups.
