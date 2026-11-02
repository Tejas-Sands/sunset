# SUNSET testnet showcase — shiftultra

Updated 2 November 2026. The main release, native creator payout and stewardship handover are complete on **`sunset.shiftultra.testnet`**. [Finalized showcase evidence](../evidence/testnet-showcase.json) records eleven transactions: ten successes and one intentional former-owner authority rejection. [Browser evidence](../evidence/browser-showcase.json) records actual hosted original/mirror recovery, downloads and cold-browser offline completion. The earlier [deployment record](../evidence/testnet-deployment.json) preserves its initial zero-campaign snapshot.

**Do not repeat the completed account creation, contribution, release, withdrawal, NFT transfer or mirror-update commands.** Demonstrate this campaign through read-only views and existing finalized receipts. Both actual expiry refunds remain a separate phase below.

All role accounts are controlled by one operator. They demonstrate distinct contract authorities, not independent human review, sponsorship or adoption. Both public artifact locations share one host. Browser financial controls remain rehearsal/unsigned planning; actual signatures used the local CLI. TestNEAR only; full-access keys remain retained and the deployment is upgradeable.

## 1. Connect to the actual released campaign

Open [the hosted app](https://sunset-lemon.vercel.app/app/), select **Testnet setup**, and enter:

| Field | Value |
| --- | --- |
| Network | `testnet` |
| Contract | `sunset.shiftultra.testnet` |
| Expected Base58 code hash | `9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx` |
| Campaign | `lantern-trail-testnet-v1` |
| Owner / fixed creator | `shiftultra.testnet` |
| Reviewer / current NFT holder | `reviewer.shiftultra.testnet` |
| Sponsor | `sponsor.shiftultra.testnet` |

Confirm the verified network/code/block and `Released` campaign. The actual final showcase snapshot is block **275928158**; a later read will naturally have a newer block. Campaign escrow is zero, total contributed is `100000000000000000000000` (0.1 testNEAR), and creator `paid` is that same amount with `pending:null`. Remaining creator credit includes unused storage allowance; it is not another 0.1-testNEAR sponsorship payment.

The current mirror is `https://sunset-lemon.vercel.app/testnet/lantern-trail-mirror-v1/manifest.json`. Transfer first reset it to the original URI, after which the new holder selected this mirror. A URL alone proves no availability: explicitly verify its committed bytes in **Public resources**.

## 2. Recheck code and state without signing

Run from the repository root on the configured deployment machine. CLI 0.30.1 and its local keychain signer already work; no repeated import or browser-wallet login is needed for these read-only commands. Never paste wallet secrets or secret-bearing transcripts into chat.

```sh
cd projects/sunset
export SUNSET_CONTRACT=sunset.shiftultra.testnet
export SUNSET_CODE_HASH=9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx
sha256sum contracts/sunset/res/sunset_contract.wasm
near contract call-function as-read-only "$SUNSET_CONTRACT" get_config json-args '{}' network-config testnet now
near contract call-function as-read-only "$SUNSET_CONTRACT" get_campaign json-args '{"id":"lantern-trail-testnet-v1"}' network-config testnet now
near contract call-function as-read-only "$SUNSET_CONTRACT" get_account json-args '{"account_id":"shiftultra.testnet"}' network-config testnet now
near contract call-function as-read-only "$SUNSET_CONTRACT" nft_token json-args '{"token_id":"lantern-trail-testnet-v1"}' network-config testnet now
```

Expected local Wasm SHA-256: `7a65f94c90eb11c7e7865362ea3386656e9d89334512b12b7ce313e5ed606c6f`. The deployed bytes were independently downloaded and matched this 270,188-byte artifact exactly. For the live code digest:

```sh
curl --fail --silent --show-error --max-time 30 https://test.rpc.fastnear.com \
  -H 'Content-Type: application/json' \
  --data '{"jsonrpc":"2.0","id":"sunset-code","method":"query","params":{"request_type":"view_code","finality":"final","account_id":"sunset.shiftultra.testnet"}}' \
  | python3 -c 'import json,os,sys; r=json.load(sys.stdin)["result"]; assert r["hash"]==os.environ["SUNSET_CODE_HASH"], "Wrong deployed code hash"; print(json.dumps({k:r[k] for k in ("hash","block_hash","block_height")},indent=2))'
```

[RPC `view_code`](https://docs.near.org/api/rpc/contracts#view-contract-code) returns the Base58 digest in **`hash`**; account views use `code_hash`. The hosted reader correction is in verified revision `85e0284`. Confirm owner `shiftultra.testnet`, layout `2`, campaign count `1`, and account count `3` at the recorded showcase snapshot. Re-read current state before any future action.

## 3. Inspect the actual completed transactions

All listed transactions are `FINAL`. The authority rejection is an expected failed execution, not an additional successful mirror edit. Its missing CLI hash was recovered from public block/signature data without resubmitting it.

| Completed step | Actual transaction |
| --- | --- |
| Create reviewer, fund 0.5 testNEAR | [A3vANF…](https://explorer.testnet.near.org/transactions/A3vANFNy6j8Jn6R9u7obESr3vXXWcYTubRYY1wAsa2tk) |
| Create sponsor, fund 0.5 testNEAR | [CoUcgx…](https://explorer.testnet.near.org/transactions/CoUcgxzWgAPEiV9h2weV6AkELh7qYL5hwH9DzLH8ey9s) |
| Create bound campaign | [5ffZw3…](https://explorer.testnet.near.org/transactions/5ffZw3hFKThQvypwrkUEEpHkdFwviXCT921AJ2y5PSfA) |
| Reviewer approves exact digest | [FD7itS…](https://explorer.testnet.near.org/transactions/FD7itSMqfXzxkD6mTPcmPWTryK3sNtqGnfMzPoTuxcsj) |
| Sponsor contributes 0.06 testNEAR | [HHJndL…](https://explorer.testnet.near.org/transactions/HHJndL2H5DRXgWoaAg5nndsNwyMS16bqQBGYVc6nEHd8) |
| Reviewer contributes 0.04 testNEAR | [nyoxYN…](https://explorer.testnet.near.org/transactions/nyoxYNWPnFiiqNakxnENbNQnDz6ANSe52fx8FvahePD) |
| Matching key release, NFT mint | [7Z2kZE…](https://explorer.testnet.near.org/transactions/7Z2kZEcTCeHnVC4P59najdsHfZXKNVEn3zumCUAgPUxd) |
| Native creator withdrawal, callback | [4tUbpd…](https://explorer.testnet.near.org/transactions/4tUbpdnkMV52ET6iLMosYVeRwfipyTMS3wQBDFRovcL4) |
| NFT transfer to reviewer | [6GL3kP…](https://explorer.testnet.near.org/transactions/6GL3kPGnE9NyiMQxsgJWfZt1wVS5k49yPdWNT5kVADTp) |
| Former owner's mirror edit rejected | [5oypVS…](https://explorer.testnet.near.org/transactions/5oypVSQ8xp6UDgmzB4EyfrFjdDE2SoVYq8ovhnyXfsMn) |
| New holder's mirror edit accepted | [Emb7kB…](https://explorer.testnet.near.org/transactions/Emb7kB4VCUNYa2CaiYb512nJCedofr5GQCEzr3pEepim) |

First contributions attached 0.07 and 0.05 testNEAR respectively, including separate 0.01 registration allowances. Their economic contributions were exactly 0.06 + 0.04. Campaign creation attached its separate 0.05 storage allowance. Release and withdrawal attached zero. NFT transfer and accepted mirror edit each retained exactly one yoctoNEAR outside escrow, for a final security reserve of two.

The actual native payout receipt transferred `100000000000000000000000` yoctoNEAR to the fixed creator. Its `on_withdraw_complete` callback succeeded, burning **1.647072781898 Tgas** of its scheduled **15 Tgas**. This proves this normal small-state callback, not maximum-state gas or failure recovery. For the existing withdrawal, inspect rather than repeat:

```sh
near transaction view-status 4tUbpdnkMV52ET6iLMosYVeRwfipyTMS3wQBDFRovcL4 network-config testnet
```

If a future withdrawal has unknown execution or persistent `pending`, retain `(contract,account_id,operation_id)` and investigate its original receipts. No timeout recredit exists. Never infer that a second payout is safe.

## 4. Recover, download and show offline independence

In **Public resources**, verify the released pack from the original location, play it and download its standalone HTML. Then select the steward mirror, verify it and download again. The actual browser downloads were byte-identical, **7,246 bytes**, SHA-256 `fbe1df06b5eb4a93aae1eb12009f4d910e3ba432862918e3c254fc013ab79738`.

Close the entire prior browser, open a fresh browser at a blank page, disable browser networking **before** opening the downloaded file, then complete all five questions and restart. Recorded verification used Chrome DevTools offline emulation (`navigator.onLine=false`), not an operating-system adapter toggle. There were zero external resource entries. Offline gameplay also fit a 390×844 viewport without horizontal overflow.

Hosted desktop reader/recovery and downloaded-file gameplay passed. A later mobile homepage navigation timed out; no mobile homepage, broad accessibility or cross-device audit is claimed. Same-host mirror paths demonstrate maintenance selection, not independent hosting resilience.

Retain the matching private package at ignored `private/shiftultra-testnet-v1/`. The sample release key is now public by intentional onchain disclosure; that does not make wallet keys or other unreleased backups public. Do not upload private CLI logs or wallet credentials.

## 5. Remaining live expiry/refund phase

The Released campaign cannot demonstrate expiry refunds. Prepare **two additional campaigns** with unused IDs, fresh packages/URLs and future deadlines (five-campaign contract cap). Each input pack needs its own matching `pack.id`; prepare its own manifest, ciphertext, terms and private backup. Changing only a campaign ID in old terms would break content binding. Use [deployment preparation](DEPLOYMENT.md) and the [contract ABI](../contracts/sunset/README.md).

For one campaign, approve and contribute below target, then wait until its real funding deadline. For the other, approve and reach target, withhold its key, then wait until its real release deadline (minimum preparation window: one hour). Do not advance the browser rehearsal clock as evidence of onchain time.

After each actual campaign becomes `Refundable`, contributing accounts call `claim_refund {id}` with zero deposit, read their credit, then withdraw the exact desired amount with zero deposit. Prepare arguments from that campaign's actual terms and credit, not this completed campaign's old files. Preserve all finalized receipts and balances; verify the native transfer, callback, paid amount and `pending:null`, and ensure duplicate claims cannot repay. Unknown outcomes require receipt investigation before any retry.

Both refund paths remain **unperformed**. Native-transfer failure, callback failure, NFT receiver/resolver scenarios, maximum-state gas and NEAR Sandbox also remain unverified. Independent educator review, independently controlled reviewers/sponsors, demand validation and final submission details remain open. Capture an honest demo distinguishing actual CLI settlement, the read-only browser viewer and local financial rehearsal. Current event rules are linked in the [rules review](../../../research/2026-11-01-council/track-verification.md).
