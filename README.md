# SUNSET — Funded onchain. Kept offline.

SUNSET pools capped adult sponsorship to release a finished learning resource. A matching key published on time credits the agreed creator; missed funding or release deadlines allow contributor refunds. Learners keep a self-contained game without a wallet. A transferable NEAR stewardship NFT hands over verified mirror-maintenance authority while the resource stays public.

[Try the hosted app](https://sunset-lemon.vercel.app) · [Product and setup](projects/sunset/README.md) · [Release readiness](projects/sunset/docs/RELEASE_READINESS_2026-11-10.md) · [Submission package](projects/sunset/docs/SUBMISSION_PACKAGE.md)

## Try it: do this, see this

1. Open the [workspace](https://sunset-lemon.vercel.app/app/), choose **Testnet setup**, and enter contract `sunset.shiftultra.testnet` with expected code hash `9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx`. See the verified testnet code/block and `lantern-trail-testnet-v1` in **Released** state.
2. In **Public resources**, recover that resource from its original manifest or steward-selected mirror. See commitment verification, play The Lantern Trail, and answer **12** to the first question: **A little brighter!**
3. Download the standalone game. Open the actual downloaded HTML in a fresh browser with networking disabled before file load. Complete the five questions: **All 5 lanterns are lit.** No learner account or wallet is needed.
4. Inspect [finalized funding, release, creator payout and stewardship receipts](projects/sunset/evidence/testnet-showcase.json), then [both actual deadline-expiry refunds and native withdrawals](projects/sunset/evidence/testnet-refunds.json). These are completed testnet actions; demonstrate them read-only rather than repeating transactions. [Exact showcase steps](projects/sunset/docs/TESTNET_SHOWCASE.md).

## Verified scope and limits

The reviewed Rust contract is deployed on NEAR testnet. The main pack received 0.06 + 0.04 testNEAR, released, paid its fixed creator 0.1 native testNEAR, and transferred stewardship with enforced mirror authority. Two separate real-expiry cases returned 0.01 + 0.02 native testNEAR with successful callbacks and no pending withdrawal. Recorded desktop/mobile-width recovery and cold-browser offline gameplay passed on 3 November; one mirror fetch timed out and succeeded on a bounded retry.

**Browser financial controls are rehearsal or unsigned plans; actual transactions were signed through the local CLI.** The live browser viewer verifies and recovers public data. All demo roles share one operator; mirror paths share one host. Maximum-state protocol gas, failed transfer/callback handling, NEAR Sandbox, independent human validation and broad accessibility/device QA remain open. Testnet only; no external audit, immutable deployment, mainnet readiness or final hackathon submission is claimed.

## Run locally

Requires Node.js 22.9+; tested with 24.17.0.

```sh
cd projects/sunset
npm ci
npm run dev
```

Open `http://127.0.0.1:3000` for the landing page or `/app/` for the workspace. No model key or database is needed for rehearsal. `npm run check` runs the application/type/local-workflow/artifact/compiled-Wasm checks; `npm run build` and `npm run test:pages` verify the static export. Native Rust checks and exact versions are in the [product README](projects/sunset/README.md).

Primary track candidates: **Open Innovation**, **NFTs That Do Something**, and **Social Money**, subject to organizer judgment. No autonomous-agent, trading or player-token economy is claimed. [Council decision](research/2026-11-01-council/README.md) · [Tokenization research](research/2026-11-01-tokenization/RESEARCH.md) · [Research archive](research/README.md)

Software: [MIT](projects/sunset/LICENSE). Original sample: CC0-1.0. Generated launch videos and private release files are ignored; renderer sources and public verification evidence are tracked.
