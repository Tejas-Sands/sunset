# SUNSET release readiness — 10 November 2026

**11 November follow-up:** [GitHub Actions](https://github.com/Tejas-Sands/sunset/actions/runs/42976384037) now passed the complete CI browser/advisory and contract gates on `e963c6f`. A focused Vercel browser check confirmed passive download notifications and completed all five hosted rehearsal questions with normal clicks. The operator's repeated notification failure was not reproduced; a full deployed smoke rerun remains required. [Exact scope and diagnostic verification](../evidence/browser-smoke-followup-2026-11-11.json). The dated findings below retain their original audit scope.

The supported local journeys pass the release checks after fixing three browser-data defects and preparing the hosted-download routing fix. The security dependency update is installed and verified. **Public sign-off remains conditional on deploying this batch and passing the real-browser test against that deployment.** These checks do not establish mainnet or unrestricted fundraising readiness.

[Machine-readable evidence](../evidence/release-readiness-2026-11-10.json) separates local checks, fresh public reads, controlled component probes and blocked coverage. No signed action, push, deployment, public post or submission was performed during this audit.

## Defects found and corrected

| Finding | Change and verification |
| --- | --- |
| Damaged saved data passed accounting checks, then crashed Discover, Activity, budgets or recovery controls | Validate the complete renderable saved-state shape before loading. Keep invalid raw data unchanged, show a temporary sample and allow private recovery export before explicit reset. Original and legacy schema-1 artifacts remain valid. Actual-component probes cover eight malformed shapes, blocked storage, backup bytes and reset cancellation/confirmation. |
| A stale tab overwrote a newer draft and its release artifact/key | Check the previous serialized snapshot before every save, initialization/migration and reset. Reject an outdated write and tell the user to reload after retaining backups. A two-tab component probe preserved the fourth campaign and its artifact. This is optimistic stale-write protection, not an atomic multi-process lock. |
| The valid account `constructor` resolved an inherited object property as a balance | Read only own credit, contribution and refund properties. The account remains valid; contribution, creator credit, refund, withdrawal and both affected views pass regressions. |
| Three deployed standalone `.html` links returned 404 | The extensionless handbook route served the exact original bytes. Three exact host-only redirects now preserve the existing links without changing Next dev/Python hosting. Static tests validate the rules; the deployed rules still require a runtime pass. |
| Locked framework/image/CSS dependencies had reported advisories | Updated to Next.js 16.4.6, PostCSS 8.5.23 and Sharp 0.35.5 with required transitive changes. Clean offline `npm ci`, native Sharp and installed/lock consistency passed. Fresh official npm bulk lookups returned no advisories for all 60 locked and 28 installed package names. |

The UI also clarifies the documented NFT receiver-reacquisition callback exception. Contract code and its reviewed WASM are unchanged.

## Verified

- **75 application tests**, including saved-data, stale-tab, prototype-name, theme, crypto, guide, mirror and receipt regressions.
- Type generation and strict TypeScript checks; Next.js **16.4.6 production build**; static pages, assets, theme bootstrap, home links and standalone redirect configuration.
- **Nine local workflow scenarios**, independent-process retained-file recovery and conservation of **21.8 simulated NEAR**.
- **19 Rust tests**, formatting, Clippy, **11 compiled-WASM host scenarios** and all eight source digests. The contract rebuild is checked against the reviewed 270,188-byte artifact.
- **34 additional controlled integrity/runtime probes** across hostile content, crypto, mirror transport, recovery and backups. These are distinct from live browser observations.
- Fresh read-only deployed code matched SHA-256 `7a65f94c90eb11c7e7865362ea3386656e9d89334512b12b7ce313e5ed606c6f` and code hash `9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx`, at finalized block **277048545**.
- At that block, three campaigns remain: one Released and two Refundable, all with zero escrow. Recorded creator paid remains **0.1 testNEAR**, sponsor refunds paid **0.03 testNEAR**; both pending withdrawals are null.
- Both freshly downloaded original/mirror byte sets recover against those live commitments and produce the exact **7,246-byte** offline file, SHA-256 `fbe1df06b5eb4a93aae1eb12009f4d910e3ba432862918e3c254fc013ab79738`. Streaming responses were replayed through the existing verifier; this is not browser/CORS execution.

Next uses its supported TypeScript compiler-API mode with the pinned TypeScript 5 compiler. Its new CLI subprocess path could not capture `--showConfig` in this restricted environment. Compiler checks remain enabled and independent `tsc` still runs; no build-error suppression was introduced.

## Repeatable suite and public gate

From `projects/sunset`, after `npm ci` and the recorded Rust compiler/target/crate-cache setup:

```sh
npm run test:release:local
```

This checks the application, build, static export, Rust and rebuilt artifact. The full gate also requires an advisory lookup and real Chromium:

```sh
npm install --global agent-browser@0.37.1
agent-browser install --with-deps
npm run test:release
```

The browser runner self-hosts `out/`, uses a fresh isolated session and fails nonzero if it cannot run. It covers exact public download bytes; malformed-data fallback; desktop/mobile navigation, overflow and theme persistence; handbook search/check persistence; a released local resource; actual downloads; and cold standalone-file use with browser networking disabled. It never signs or funds anything. The GitHub Actions workflow now installs the pinned browser tool and runs the advisory/browser gates on pushes and PRs, alongside the existing Rust job. The revised workflow has not been executed remotely in this session.

After publishing/deploying the batch, run:

```sh
npm run test:browser -- --url https://sunset-lemon.vercel.app
```

This must pass against the intended deployed version. An HTTP 200 app shell alone is insufficient. No Chromium pass is claimed here: Python socket creation is denied with `EPERM`, and the browser daemon cannot start. The native npm audit client also failed DNS; the recorded advisory results came directly from the official registry using the available HTTP transport. Vercel’s connector could not access the owning team, so no private build/runtime-log verification is claimed.

## Remaining production boundaries

The public financial UI is rehearsal/unsigned planning plus a read-only testnet reader. Actual testnet settlement uses the reviewed CLI/contract flow. All demonstration roles share one operator and both resource paths share a host. Do not repeat completed financial actions for a demonstration.

Real failed native/NFT transfer and callback execution, maximum-state protocol gas at the scheduled callback budget, NEAR Sandbox, broad physical-device/accessibility/cross-browser QA and independent user/demand evidence remain unverified. Host doubles report zero consumed gas and cannot prove protocol gas sufficiency. Permanent finite participant slots and retained deployment-key authority also remain disclosed production limitations.

The [submission package](SUBMISSION_PACKAGE.md) remains a draft. Public posting, personal/team fields, mainnet prize account, contact consent and exact-payload approval are separate remaining human steps.
