# Live wallet and technical commons — 11 November 2026

The operator selected the existing reviewed testnet contract and approved [this design](superpowers/specs/2026-11-11-live-wallet-design.md). The implementation follows [the plan](superpowers/plans/2026-11-11-live-wallet.md). Local commits require the operator's push and deployment. This document supersedes older descriptions of the public app as a financial rehearsal or unsigned-plan viewer; dated evidence keeps its original scope.

## What changed

The public experience now shares a coral/forest protocol design, tapered logo/home links, both themes, actual resource routes and three original AI/math guides. Each has worked examples, four chapters, eight checks, primary references and an exact offline reading file. Hosted attention, gradient and low-rank calculators make the numerical examples interactive. The new guides are free library material and have no onchain funding claim.

The real wallet header and account actions replace role-play accounts, simulated balances, manual contract setup and unsigned workbench. `@hot-labs/near-connect` 0.12.0 is pinned; it adds no runtime dependencies. The SDK tarball's SHA-512 was checked against the official registry manifest before installation. The chooser uses testnet signing wallets, excludes MyNearWallet, avoids login access keys and opens only on an explicit action.

The public app supports owner publishing, exact-content reviewer inspection, sponsorship, key release, refund claims, separate native withdrawals and holder-only NFT/mirror actions. It checks a fresh finalized code/configuration/account snapshot before signing, verifies fetched receipts against a digest-bound request, and reads callback/account state for native payout confirmation. A cancelled request clears its unsubmitted reference; unknown/submitted requests remain recoverable and block duplicate sending. Private unreleased keys never enter persistent browser storage.

## Existing chain state

The fresh read at block **277204679** matched contract `sunset.shiftultra.testnet`, owner `shiftultra.testnet` and code hash `9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx`. The owned-browser real-RPC read later reached block **277214517** and showed the same three-campaign catalog: Released, Refundable, Refundable, zero escrow and no active funding round. The UI shows that empty state. Two of five campaign slots remain at this snapshot; there are three registered accounts out of 100.

No contract code, state layout or existing campaign was changed. The original public WASM remains 270,188 bytes, SHA-256 `7a65f94c90eb11c7e7865362ea3386656e9d89334512b12b7ce313e5ed606c6f`. Earlier [main showcase](../evidence/testnet-showcase.json), [refunds](../evidence/testnet-refunds.json) and [browser/offline evidence](../evidence/browser-showcase.json) remain authoritative for their dated actual transactions. Do not replay their completed signed actions.

## Automated and browser evidence

The local gate passed 101 application tests, TypeScript, nine model workflow scenarios, artifact/source checks and 11 compiled-WASM host scenarios. Native Rust tests passed 19/19, with formatting, Clippy and an identical reproducible WASM rebuild. The production export generated landing, app and all three resource routes; static checks verified 20 local targets and six exact downloads.

`npm audit` could not resolve the registry in the restricted Node executor. The complete locked-package map was instead sent with the approved HTTP client to npm's official bulk-advisory endpoint; it returned `{}` for 61 locked package names, including the wallet SDK. This is an advisory lookup, not a claim that the unavailable npm command passed.

The standard `npm run test:browser` failed at Python server startup because this executor denies socket creation (`PermissionError: [Errno 1]`). Its revised assertions therefore do not have a full local HTTP smoke pass. The suite remains strict and must pass in CI and against the deployed site; no skip/success fallback was added.

An owned MCP Chromium session did run interaction checks against the actual production React components, compiled with installed Next webpack/TypeScript in an ignored file fixture. Test-only RPC and the SDK's standard injected-wallet API supplied controlled signing results. A separate `?live=1` run used genuine read-only RPC and the real wallet chooser. The production source has no test hooks or fake-wallet paths. Static production HTML/CSS previews were used only for visual review. Responsive previews used a real 390×844 CSS iframe viewport in desktop Chrome, not physical-device or touch emulation.

Observed browser checks include both themes, native search/empty states, saved chapter/check restoration, all three numerical labs, genuine chooser open/Escape cancellation, and controlled sponsorship/rejection/withdrawal/reviewer/release/mirror/NFT controls. Owner Studio also prepared files, required a saved-backup check and created a Draft with the exact 0.05-testNEAR deposit; no content key appeared in persistent storage. Studio file/date setup used test-only DataTransfer/input events, followed by native prepare/download/confirmation/create clicks. A connection reset of the sponsorship input was reproduced (0.23→0.1), fixed and retested (0.23 retained, zero requests). A cancellation's stale prior receipt link was reproduced, removed and retested. These observations do not establish a real wallet signature, actual new protocol settlement, complete deployed browser coverage or broad accessibility certification. [Structured evidence](../evidence/live-wallet-2026-11-11.json).

## Operator deployment and acceptance

1. From the repository root, publish the verified local commits:

   ```sh
   git --git-dir=.sunset-git --work-tree=. push origin main
   ```

2. Wait for Vercel and GitHub Actions to complete. Vercel remains Next.js, root `projects/sunset`, Node 24.x, `npm run build`, default output setting. This batch needs no environment secret or backend service. Confirm the deployment uses the new commit.
3. From the same root, run:

   ```sh
   npm --prefix projects/sunset run test:browser -- --url https://sunset-lemon.vercel.app
   ```

   Chromium setup on the laptop, if needed: install pinned `agent-browser@0.37.1`, then `agent-browser install`. The suite tests real pages/RPC/chooser and separately uses a controlled injected wallet; it never requests a real transaction signature. Every required step must pass.
4. In your own supported wallet, connect to testnet, confirm the account, open **My activity**, change/disconnect and cancel an approval. Keep keys/recovery phrases in the wallet or local CLI keychain; never paste them here. A new human-wallet signed journey remains an acceptance step after deployment.
5. To test a new full signed release, deliberately use one remaining campaign slot with a unique original guide and modest testNEAR goal. In **Studio**, import JSON, choose a different reviewer, future deadline and final HTTPS manifest location; prepare the files, save the private backup, host only `manifest.json` and `ciphertext.sunset`, then approve creation. The reviewer restores the matching backup and inspects before approval. A sponsor approves an exact contribution, the content-key holder releases before expiry, and the creator withdraws its credit. Retain the new receipts and callback/account observations. Publishing is owner-curated; ordinary accounts cannot create campaigns.
6. Check original and steward-mirror reading/downloads, then a cold retained file with browser networking disabled before opening it. Keep the original released campaign and refund records intact; never rerun their completed actions.

If a wallet redirects, throws or closes after sending, inspect the pending reference and wallet activity, paste the matching hash if needed, and use **Check status**. Do not submit a replacement while the result is unknown. Callback-pending credit is not a paid withdrawal. If the reviewed code changes or RPC is unavailable, financial actions remain unavailable while the free library stays readable.

The accepted movie is unchanged. Hackathon sending, public posts, actual new signed operations and mainnet use are outside this implementation batch. Maximum-state/failure protocol gas, independent reviewer/sponsor validation and broad cross-browser/physical-device accessibility work remain open.
