# SUNSET testnet showcase — shiftultra

Updated 2 November 2026. **Contract deployment is complete:** `sunset.shiftultra.testnet`, owner `shiftultra.testnet`, code hash `9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx`. [Deployment transaction](https://explorer.testnet.near.org/transactions/BXT7Z3ENkUBFpSPBkiN28x8pqbsoKhNifvinz1r9Eqw7) and account creation are finalized successfully; [deployment evidence](../evidence/testnet-deployment.json) records receipts and exact deployed bytes. All four prepared resource URLs on `https://sunset-lemon.vercel.app` returned HTTP 200 with matching hashes. Reviewer/sponsor accounts remain planned, and no campaign settlement or browser/offline flow is verified. Deployment/initialization do not establish callback gas sufficiency or the remaining business flows. This runbook uses testNEAR only.

The contract account was created with four testNEAR. The remaining reviewer/sponsor commands would create accounts controlled by the same operator as `shiftultra.testnet`; separate account authorities do not prove independent review, sponsors or adoption. The configured owner is also the fixed creator and payout beneficiary. Browser financial controls remain rehearsal/unsigned planning; real signatures below use the local CLI. **Do not rerun contract creation or deployment.**

## 1. Install, fund and identify the exact package

CLI 0.30.1 and the local keychain signer are already verified on the deployment machine; skip installation/import there. These setup commands are for a new machine. Run on a network-enabled machine. The first command below assumes the repository root; all subsequent commands run from `projects/sunset`. Use the existing private package only on the machine where it was prepared; `private/` is ignored and is absent from fresh clones. A fresh clone must prepare a new campaign/package using [DEPLOYMENT.md](DEPLOYMENT.md), with a new ID, future deadline and final hosting URL. Never regenerate encrypted bytes or change committed terms after campaign creation.

```sh
cd projects/sunset
npm install -g near-cli-rs@0.30.1
near --version
near account import-account using-private-key network-config testnet --check-account-id save-to-keychain
```

The [official release](https://github.com/near/near-cli-rs/releases/tag/v0.30.1) is pinned here. The operator's default browser-wallet import failed to add the newly generated public key, and the operator explicitly requested avoiding MyNearWallet. The direct-import command above is accepted by the locally installed CLI's help/parser; it has not been run with a secret here. Export the testnet account's existing private key from the wallet you actually use, enter it only at the local prompt, and enter account **shiftultra.testnet**. Network and keychain storage are preselected; the CLI checks that the derived public key is already on the account.

If your wallet offers recovery words instead of an account-specific private key, use this alternative in your own terminal and enter the recovery words at its prompt:

```sh
near account import-account using-seed-phrase network-config testnet --check-account-id save-to-keychain
```

Use the derivation path belonging to your wallet. If the derived key is not on the account, retain the error and verify the wallet/account/path; do not bypass the check. Keys stay in the local CLI keychain. Never paste secrets, secret-bearing commands or import transcripts into chat. New role keys below are generated and saved locally by the CLI. No browser-wallet import is needed for this route.

Before deployment, RPC independently showed **8 testNEAR** in `shiftultra.testnet`; four were then allocated to the contract. Check the current balance before further account creation or funding. Only if additional tokens are needed, use the [browser faucet](https://near-faucet.io/), linked by [NEAR's faucet documentation](https://docs.near.org/getting-started/faucet): select **NEAR**, enter **shiftultra.testnet**, and follow its displayed amount limit/cooldown. The earlier faucet request itself was not verified by the executor.

**API failure observed on 2 November:** the operator's POST to `https://docs-mcp-f18b.onrender.com/api/faucet` returned HTTP 404 with `Not Found`, despite that route appearing in the [agent-tools documentation](https://docs.near.org/getting-started/tools-for-ai#testnet-faucet-api). The cause is not established; the response does not verify an account or credit any funds. Do not keep retrying that route as a funding step. Browser-page availability is also not evidence that a request succeeded; check the actual balance. After any timeout, check balance before retrying because funding may already have completed.

The 270,188-byte Wasm represents approximately 2.70188 NEAR of raw code collateral before account allowances, plus state and gas. **2 NEAR is insufficient.** [Storage pricing](https://docs.near.org/protocol/storage/storage-staking) is `10^19` yoctoNEAR per byte. Four contract NEAR is a working allocation, not a measured maximum-state guarantee.

```sh
export SUNSET_OWNER=shiftultra.testnet
export SUNSET_CONTRACT=sunset.shiftultra.testnet
export SUNSET_REVIEWER=reviewer.shiftultra.testnet
export SUNSET_SPONSOR=sponsor.shiftultra.testnet
export SUNSET_PRIVATE=private/shiftultra-testnet-v1
export SUNSET_HOST=https://sunset-lemon.vercel.app
export SUNSET_CODE_HASH=9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx
umask 077
sha256sum contracts/sunset/res/sunset_contract.wasm
near account view-account-summary "$SUNSET_OWNER" network-config testnet now
```

Expected Wasm SHA-256: `7a65f94c90eb11c7e7865362ea3386656e9d89334512b12b7ce313e5ed606c6f`. Stop on a mismatch. Keep `release-args.json`, `private-release-backup.json`, `artifact.json` and `offline-check.html` private before intended release. Only manifest/ciphertext belong in the public host.

## 2. Publish and verify the committed public bytes

The prepared public files are already hosted and their exact hashes were verified on 2 November. Recheck these URLs before creating the campaign; after any future file changes, push through the normal Git workflow and wait for the Vercel production build. A local commit or build does not prove hosting. The primary directory is `/testnet/lantern-trail-v1/`; the identical mirror is `/testnet/lantern-trail-mirror-v1/`.

```sh
SUNSET_FETCH_DIR="$(mktemp -d)"
curl --fail --silent --show-error --max-time 30 "$SUNSET_HOST/testnet/lantern-trail-v1/manifest.json" -o "$SUNSET_FETCH_DIR/manifest.json"
curl --fail --silent --show-error --max-time 30 "$SUNSET_HOST/testnet/lantern-trail-v1/ciphertext.sunset" -o "$SUNSET_FETCH_DIR/ciphertext.sunset"
curl --fail --silent --show-error --max-time 30 "$SUNSET_HOST/testnet/lantern-trail-mirror-v1/manifest.json" -o "$SUNSET_FETCH_DIR/mirror-manifest.json"
curl --fail --silent --show-error --max-time 30 "$SUNSET_HOST/testnet/lantern-trail-mirror-v1/ciphertext.sunset" -o "$SUNSET_FETCH_DIR/mirror-ciphertext.sunset"
sha256sum "$SUNSET_FETCH_DIR/"*
```

Both manifest hashes must equal `f808d7472f2e5d31749d02b42f89771e1be26ea80c985422ff8e3ed3e7e9656d`; both ciphertext hashes must equal `465542a09861e53c92463407a59f41cedf773f4119937ba413a63701e7543c38`. No redirects are followed; stop if any download fails or hash differs. Open the hosted frontend and confirm `/app/` loads.

## 3. Create the remaining role accounts; verify the existing deployment

The contract account creation and atomic deploy/initialization are complete. **Do not repeat those signed actions.** Account creation transaction: `HMwHTAPTPegRH9D8wcsqgsVzWTnVw3cfTVCm3CCxBEWn`. Deployment transaction: `BXT7Z3ENkUBFpSPBkiN28x8pqbsoKhNifvinz1r9Eqw7`.

Reviewer and sponsor returned explicit `UNKNOWN_ACCOUNT` before deployment and remain uncreated in the recorded evidence. Recheck each planned ID with `near account view-account-summary ID network-config testnet now` before creating it. An explicit account-not-found result confirms it is unused; a network error does not. If either exists, inspect ownership and its local signer before proceeding; do not overwrite unrelated accounts.

```sh
near account create-account fund-myself "$SUNSET_REVIEWER" '0.5 NEAR' autogenerate-new-keypair save-to-keychain sign-as "$SUNSET_OWNER" network-config testnet sign-with-keychain send
near account create-account fund-myself "$SUNSET_SPONSOR" '0.5 NEAR' autogenerate-new-keypair save-to-keychain sign-as "$SUNSET_OWNER" network-config testnet sign-with-keychain send
```

The completed deployment signed as `sunset.shiftultra.testnet`, satisfying private `new`; `init.json` set owner to `shiftultra.testnet`. [Official deployment source](https://raw.githubusercontent.com/near/near-cli-rs/main/src/commands/contract/deploy/mod.rs) and [batched initializer](https://raw.githubusercontent.com/near/near-cli-rs/main/src/commands/contract/deploy/initialize_mode/call_function_type/mod.rs) confirm this behavior. The deployment remains upgradeable while full-access keys exist.

```sh
near contract call-function as-read-only "$SUNSET_CONTRACT" get_config json-args '{}' network-config testnet now
curl --fail --silent --show-error --max-time 30 https://test.rpc.fastnear.com \
  -H 'Content-Type: application/json' \
  --data '{"jsonrpc":"2.0","id":"sunset-code","method":"query","params":{"request_type":"view_code","finality":"final","account_id":"sunset.shiftultra.testnet"}}' \
  | python3 -c 'import json,os,sys; r=json.load(sys.stdin)["result"]; assert r["hash"]==os.environ["SUNSET_CODE_HASH"], "Wrong deployed code hash"; print(json.dumps({k:r[k] for k in ("hash","block_hash","block_height")},indent=2))'
```

Confirm network `testnet`, owner `shiftultra.testnet`, state layout `2`, and initially zero campaigns. Preserve the finalized block/hash output and deployment transaction ID. `view_code` returns the Base58 code digest in **`hash`**; `view_account` uses a different field, `code_hash`. [RPC `view_code`](https://docs.near.org/api/rpc/contracts#view-contract-code) returns the actual deployed code hash; a local file hash alone is insufficient.

## 4. Create, inspect and approve the exact agreement

The following shell functions only shorten documented CLI commands; they create no helper files. Every amount/time inside an argument file is a decimal string. `file-args` reads exact file bytes without an encoding flag. [Official argument handling](https://raw.githubusercontent.com/near/near-cli-rs/main/src/commands/contract/call_function/call_function_args_type/mod.rs).

```sh
sunset_call() {
  near contract call-function as-transaction "$SUNSET_CONTRACT" "$1" file-args "$2" prepaid-gas '100 Tgas' attached-deposit "$3" sign-as "$4" network-config testnet sign-with-keychain send
}
sunset_view() {
  near contract call-function as-read-only "$SUNSET_CONTRACT" "$1" file-args "$2" network-config testnet now
}
sunset_call create_campaign "$SUNSET_PRIVATE/create-campaign.json" '0.05 NEAR' "$SUNSET_OWNER"
sunset_view get_campaign "$SUNSET_PRIVATE/campaign-query.json"
```

Check ID `lantern-trail-testnet-v1`, target `100000000000000000000000` (0.1 NEAR), reviewer, all hashes and primary URI. Funding deadline is **10 November 2026, 00:00 UTC**; release window is **24 hours after reaching the target**. If the funding deadline has passed, prepare a new campaign rather than running these stale terms. Expected state is `Draft`.

Acting as reviewer, inspect the exact decrypted questions, answers, license and commitments. The prepared `offline-check.html` was generated through independent file recovery locally; browser playability still requires checking. Run recovery again if needed, then open the file privately:

```sh
node scripts/recover-pack.mjs "$SUNSET_PRIVATE/artifact.json" "$SUNSET_PRIVATE/private-release-backup.json" "$SUNSET_PRIVATE/reviewer-offline-check.html"
```

Copy the **actual `agreement_digest` from the current `get_campaign` response**. Run the next command separately, paste only that 64-character lowercase hex digest, then press Enter:

```sh
read -r SUNSET_AGREEMENT_DIGEST
```

```sh
printf '{"id":"lantern-trail-testnet-v1","agreement_digest":"%s"}\n' "$SUNSET_AGREEMENT_DIGEST" > "$SUNSET_PRIVATE/approval-args.json"
sunset_call approve_campaign "$SUNSET_PRIVATE/approval-args.json" '0 NEAR' "$SUNSET_REVIEWER"
sunset_view get_campaign "$SUNSET_PRIVATE/campaign-query.json"
```

Confirm `Active`. Different account IDs satisfy authority separation; the operator must disclose that review was self-controlled.

## 5. Fund, intentionally disclose the key, then withdraw

```sh
sunset_view get_account "$SUNSET_PRIVATE/sponsor-query.json"
sunset_view get_account "$SUNSET_PRIVATE/reviewer-query.json"
```

Both should be `registered:false` before their first contribution. Deposits below include exactly 0.01 NEAR registration allowance. If an account is already registered, attach only its contribution instead; do not repeat funding commands blindly. The owner was registered by campaign creation and has different deposit requirements.

```sh
sunset_call contribute "$SUNSET_PRIVATE/sponsor-contribution.json" '0.07 NEAR' "$SUNSET_SPONSOR"
sunset_view get_campaign "$SUNSET_PRIVATE/campaign-query.json"
sunset_call contribute "$SUNSET_PRIVATE/reviewer-contribution.json" '0.05 NEAR' "$SUNSET_REVIEWER"
sunset_view get_campaign "$SUNSET_PRIVATE/campaign-query.json"
```

The sponsor contributes `60000000000000000000000` (0.06 NEAR); reviewer contributes `40000000000000000000000` (0.04 NEAR). Confirm total/escrow 0.1 NEAR, state `Funded` and actual release deadline. This path demonstrates exact funding; it does not demonstrate cap-change refunds.

Only when ready to make the content public, and before the onchain release deadline:

```sh
sunset_call publish_release "$SUNSET_PRIVATE/release-args.json" '0 NEAR' "$SUNSET_OWNER" > "$SUNSET_PRIVATE/release-cli.log" 2>&1
sunset_view get_campaign "$SUNSET_PRIVATE/campaign-query.json"
sunset_view get_account "$SUNSET_PRIVATE/owner-query.json"
sunset_view nft_token "$SUNSET_PRIVATE/token-query.json"
```

The private log captures CLI previews/results that can contain the release key; do not upload it. **Broadcasting exposes the key even if the call fails.** Confirm `Released`, public key, one NFT owned by creator, and at least 0.1 NEAR creator credit. Storage change can also be credit, so do not assume the entire credit field equals the target.

```sh
sunset_call withdraw "$SUNSET_PRIVATE/creator-withdraw.json" '0 NEAR' "$SUNSET_OWNER"
sunset_view get_account "$SUNSET_PRIVATE/owner-query.json"
near account view-account-summary "$SUNSET_OWNER" network-config testnet now
```

Withdrawal amount is `100000000000000000000000`; its attached deposit is **zero**. Before/after account balances include fees from other owner actions. Verify the actual native transfer and complete callback receipt chain; `pending` must return to null and `paid` increase by the transfer amount. For each transaction, substitute its real hash in the [documented status command](https://docs.near.org/tools/cli#view-status):

```sh
near transaction view-status ACTUAL_TRANSACTION_HASH network-config testnet
```

Record transaction/receipt IDs, finalized blocks, signer/receiver/method/deposit, gas and balances. If execution/callback status is unknown or `pending` persists, retain `(contract,account_id,operation_id)` and investigate the original receipts. No timeout recredit exists; never infer that retrying a withdrawal is safe. These 100-Tgas budgets remain unvalidated by protocol metering; failures must be recorded accurately.

## 6. Verify the hosted reader and stewardship handover

Push the local reader correction and wait for the production build before connecting: the live RPC exposed a `view_code.hash` field mismatch that is fixed locally and covered by regression tests. The corrected reader was verified against the real contract from Node; hosted browser execution remains to be checked.

Open `https://sunset-lemon.vercel.app/app/`, select **Testnet setup**, enter contract `sunset.shiftultra.testnet` and expected Base58 code hash `9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx`, then connect. Confirm verified network/code/block identity. In Public resources, verify the released pack, play it and export/download its standalone HTML. Close the site, disable networking, open the downloaded file in a fresh browser session and complete the game. Record actual browser results; local recovery alone does not prove this flow.

```sh
sunset_call nft_transfer "$SUNSET_PRIVATE/steward-transfer.json" '1 yoctoNEAR' "$SUNSET_OWNER"
sunset_view nft_token "$SUNSET_PRIVATE/token-query.json"
```

Confirm token owner is now `reviewer.shiftultra.testnet` and mirror resets to the original URI. Next call is an **intentional failed authority test**: the old owner must be rejected; retain its failure receipt and verify the mirror stayed unchanged. It uses a public mirror URI, no release secret.

```sh
sunset_call set_mirror "$SUNSET_PRIVATE/steward-mirror.json" '1 yoctoNEAR' "$SUNSET_OWNER"
sunset_view nft_token "$SUNSET_PRIVATE/token-query.json"
sunset_call set_mirror "$SUNSET_PRIVATE/steward-mirror.json" '1 yoctoNEAR' "$SUNSET_REVIEWER"
sunset_view nft_token "$SUNSET_PRIVATE/token-query.json"
```

Confirm new mirror `https://sunset-lemon.vercel.app/testnet/lantern-trail-mirror-v1/manifest.json`; refresh/reconnect the viewer, verify/recover using the steward mirror, and export/play the same committed pack. Transfer and mirror edits require **exactly one yoctoNEAR**, separate from financial escrow. Same-host copying proves maintenance mechanics, not an independently operated availability service.

## 7. Remaining expiry/refund evidence and submission

The released campaign cannot demonstrate expiry refunds. Prepare **two additional campaigns** with unused IDs, fresh packages/URLs and future deadlines (five-campaign contract cap). Give each input pack its own matching `pack.id`, then prepare its own manifest, ciphertext, terms and private backup; copying the main terms and changing only the campaign ID would break the content binding. For one, approve and contribute below target, then wait until its real funding deadline. For the other, approve and reach its target, withhold its key, then wait until its real release deadline (the preparation tool supports a minimum one-hour release window). Never advance the rehearsal clock as evidence of onchain time.

For each separate campaign, read `get_campaign` until `Refundable`; contributing accounts call `claim_refund {id}` with zero deposit, read `get_account`, then `withdraw {amount}` with zero deposit and at least the proposed 100 Tgas. Preserve all finalized receipts and balances, verify duplicate claims cannot repay, and apply the pending rules above. Prepare their JSON files from their actual terms/credit before signing. **These two live refund demonstrations remain a next phase, not completed evidence.** Protocol transfer/callback failure tests and maximum-state gas tests also remain outstanding.

The [official event instructions](https://nearhackathon.com/HACKATHON.md), recorded in the [rules review](../../../research/2026-11-01-council/track-verification.md), permit testnet-only entries (Q-010) and reproducible local demonstrations; judges need video when they cannot open the demo, and the repository must stay public through judging. Recheck current rules before submission. Capture an honest video distinguishing CLI settlement from the read-only browser viewer and local rehearsal. This guide neither publishes a submission nor establishes independent-user, educator, security-audit or mainnet readiness claims.
