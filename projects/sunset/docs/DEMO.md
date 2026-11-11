# SUNSET demonstration

Updated 11 November 2026 for the live-wallet implementation. Deploy the current source and pass the [post-deployment checks](LIVE_WALLET_2026-11-11.md) before using it as the public demo. The accepted launch film is unchanged.

## Three-minute read-only path

1. Open the landing page. Switch light/dark mode, then choose **Transformer Attention Lab** under **Wide-open possibilities**. Work through the scaled-logit example and turn on the causal mask. Its output changes from `[1.689275, 0.733044]` to `[0.731059, 0.537883]`.
2. Search a chapter, tick an exercise and reload to show local progress. Download the complete guide. Close the website and open the retained HTML with browser networking disabled before navigation. Its reading content, search and checks work independently. The hosted lab is separate from the retained reading copy.
3. Open **Funding**. Show actual testnet data and its no-active-round state. Expand `lantern-trail-testnet-v1` in the archive, choose **Read resource**, and download its verified original pack. Recovery checks run automatically.
4. Open **Stewardship** and show the real current holder. Explain that it maintains the recovery mirror; it cannot revoke public copies or redirect creator payout. Show existing [release/payout/NFT receipts](../evidence/testnet-showcase.json) and [actual refunds](../evidence/testnet-refunds.json).
5. Optionally open **Connect wallet**, show supported testnet choices and cancel. Reading requires no connection. Do not repeat completed campaign transactions for a recording.

The AI/math guides are immediately open library material, separate from the arithmetic resource named by earlier testnet receipts. All earlier demo roles shared one operator, and both mirror paths shared one host.

## First new signed journey

Use the operator's own wallet after deployment, following [the acceptance runbook](LIVE_WALLET_2026-11-11.md). Publishing is restricted to `shiftultra.testnet`, with two slots left at the recorded snapshot. A new campaign needs a unique resource ID, future deadline, hosted encrypted files and matching private backup. A different reviewer account inspects it before approval. A sponsor approves a contribution, the key holder releases, and the creator withdraws its credit. Record exact new receipts and callback/account results; unknown requests must be checked rather than resent.

Do not import wallet secrets through chat, use operator keys in automation or treat controlled-wallet tests as actual protocol receipts. A future signed test consumes a permanent campaign slot and is a deliberate operator action outside this implementation batch.

## Automated checks

From `projects/sunset`, run `npm run check`, `npm run build`, `npm run test:pages`, `npm run test:rust` and `npm run test:browser`. The browser suite accepts `-- --url https://sunset-lemon.vercel.app` after deployment. It must finish successfully; an unavailable browser/server/RPC is a failure, never skipped coverage.

The retained `verify:local` script runs nine model scenarios, including cap/change, retained-file recovery, both expiry refunds, stewardship and simulated budgets. It conserves 21.8 simulated NEAR. Those model APIs no longer appear in the public UI. Compiled-WASM host tests and Rust unit tests remain separate from NEAR Sandbox or testnet execution. [Dated evidence](../evidence/live-wallet-2026-11-11.json) records each scope.
