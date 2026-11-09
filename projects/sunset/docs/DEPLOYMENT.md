# SUNSET deployment runbook

Operator record: **1 November 2026**, application source `5810ddd`. SUNSET is a bounded **NEAR testnet prototype**. Use free static hosting and faucet-funded testnet accounts for this launch; mainnet funds, paid infrastructure and a custom domain are unnecessary.

**2 November update:** [main testnet showcase](../evidence/testnet-showcase.json) is complete on `sunset.shiftultra.testnet`: agreement approval, 0.1-testNEAR exact funding/release/native creator payout, successful withdrawal callback, NFT handover and mirror authority. Code hash: `9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx`. The actual hosted reader, original/mirror recovery and downloaded game passed [narrow browser/offline checks](../evidence/browser-showcase.json). The [showcase guide](TESTNET_SHOWCASE.md) replays those results without repeating signed actions. [Both real expiry refunds and native principal withdrawals](../evidence/testnet-refunds.json) passed on 3 November. Failure/max-state protocol checks remain open. The initial [deployment record](../evidence/testnet-deployment.json) remains a historical zero-campaign snapshot. Subsequent local commits are pushed by the operator; earlier access failures below are historical.

## What each deployment delivers

| Deliverable | Current position |
| --- | --- |
| Public website | The Next.js static export serves the landing page, `/app/` rehearsal and standalone sample. Financial rehearsal state stays in each visitor's browser. Hosting it does not create shared balances or move tokens. |
| Shared testnet contract | Reviewed Wasm at `sunset.shiftultra.testnet` completed exact funding, public release, native creator payout and NFT mirror handover. Its normal small-state withdrawal callback succeeded. Both live expiry refunds and native withdrawals passed on 3 November. Failure paths and maximum-state gas remain open. |
| Full browser dApp | Additional implementation is required: wallet connection and signing, live action flows, account credit/pending reads, canonical receipt checks and published deployment configuration. The current testnet panel reads a pinned deployment; its workbench exports unsigned plans. |

The current contract is **owner-curated**: only its configured owner creates campaigns, and that owner is their fixed creator/beneficiary. It is not an open multi-creator marketplace. Limits are five campaigns and 100 permanent registered accounts; public contributors can exhaust the account slots. Access budgets and coordination agents remain local demonstrations.

No database, Supabase project, model API key, backend signer or managed release service is needed for this scope. The frontend host can also serve each campaign's public manifest and ciphertext.

## Access and inputs still needed

- **Hosting/QA:** desktop hosted reader/recovery/download, cold-browser offline gameplay and the later 390×844 homepage navigation passed in the recorded 3 November review. Broad accessibility, physical-device and cross-browser checks remain.
- **Independent testnet operators:** owner, contract, reviewer and sponsor accounts all exist and signed the main showcase, but share one operator. Independently controlled humans, educator review and sponsor feedback remain to be established.
- **Signing and testNEAR:** each adult uses their own wallet or locally configured CLI. Fund contract code/state collateral, storage allowances, contributions and transaction fees with testNEAR. Do not paste wallet private keys, seed phrases, access tokens or private release backups into chat, commits or deployment settings.
- **Campaign terms:** actual pack, target, future funding deadline, release window, reviewer and final HTTPS manifest location. The included original sample can support a technical testnet demonstration; educator review remains separate.
- **Execution environment:** a browser and compatible NEAR Sandbox on a machine/runner that permits sockets, plus working testnet RPC access. No real protocol runner is currently supplied by this repository.

### Historical assistant access record — 1 November

Vercel Hobby account `rajavaiktitva-8002` has project `sunset` (`prj_ezDpbJ9JXkcv81x8T31spnpVx7i4`) in its default team (`team_EB4GR68XaqT5BFFfZwzPXXb3`). Project creation succeeded; deployment/upload did not. The provider returned a team-grant **403**, and its consent flow was sent to the operator. Complete the provider authorization before retrying. There is no verified published site URL.

GitHub currently authenticates as `vedantssj`. The intended `Tejas-Sands/sunset` repository returned **404** through that access; this does not distinguish an absent repository from an inaccessible private one. Establish authorized Tejas-Sands access, verify ownership and contents, then publish without overwriting unrelated history. No remote publication is claimed. This workspace uses `git --git-dir=.sunset-git --work-tree=.`; ordinary clones use normal Git commands.

### Publish from a normal terminal, then connect Vercel once

The earlier restricted executor could not resolve GitHub hosts. The operator subsequently published the repository and now pushes from the laptop's normal terminal; keep GitHub authentication local there. Do not reconnect the shared Codex GitHub plugin or paste tokens into the conversation. For subsequent committed batches, run from the repository root:

```sh
git --git-dir=.sunset-git --work-tree=. push origin main
```

The initial publishing helper below is retained for setup on another machine; it is not needed for routine pushes.

From the repository root in a network-enabled terminal, run:

```sh
bash projects/sunset/scripts/publish-github.sh
```

The helper uses installed Git and GitHub CLI. Enter the temporary token at its hidden prompt, or supply `GH_TOKEN` through your local credential tooling. It checks the authenticated account, creates the intended public repository only after an explicit not-found response, verifies ownership/write access and remote history, pushes existing `main` commits without forcing, and checks the remote commit. It does not save the token, rewrite history or alter unrelated origins. The token needs repository write access and permission to publish the checked-in GitHub Actions workflow; creating a missing repository also requires repository-creation access. Revoke a token shared in conversation after use; no replacement needs to be pasted here.

After the repository is published, complete the persistent Vercel Git integration in the dashboard:

1. In Vercel account settings, ensure the GitHub login connection is `Tejas-Sands`. For a personal GitHub repository, its owner must connect it.
2. Open the existing **sunset → Settings → Git → Connect Git Repository** and select **Tejas-Sands/sunset**. If it is missing, grant the Vercel GitHub App access to that repository in GitHub's installed-app settings.
3. Under **Settings → Build and Deployment**, set **Root Directory** to `projects/sunset`, **Framework Preset** to `Next.js`, **Build Command** to `npm run build`, **Install Command** to `npm ci`, **Node.js Version** to `24.x`, and leave **Output Directory override off**. The Next.js integration handles `output: 'export'`; do not override its output directory to `out`.
4. Verify **Settings → Environments → Production → Branch Tracking** is `main`. For the first build, open **Deployments → Create Deployment** and select `main`. Later pushes trigger deployment automatically. No environment variables, database or Vercel token are required for the current static application.
5. Check the stable production domain from **Domains** in a signed-out browser. Standard deployment protection can keep generated preview URLs behind login; verify the intended public production domain separately.

This connects GitHub directly to Vercel and does not depend on the assistant connection's expiring consent links. See [Vercel's GitHub integration](https://vercel.com/docs/git/vercel-for-github), [build settings](https://vercel.com/docs/builds/configure-a-build) and [Git deployments](https://vercel.com/docs/git). If Vercel reports an unrecognized commit author, use the actual account's verified GitHub email/noreply setting for future commits; do not rewrite published history to work around it.

## 1. Verify and host the static site

Run from `projects/sunset` with Node.js 22.9+ (24.17 was tested):

```sh
npm ci
npm run check
npm run build
npm run test:pages
```

The `5810ddd` application build passed production export and static page checks. After adding the publishing helper, a fresh `npm run check` passed 47 JavaScript tests (including eight offline publishing scenarios), typecheck, nine local workflows, artifact checks and ten compiled-Wasm host scenarios. `bash -n scripts/publish-github.sh` also passed. Publishing tests use real local Git histories and simulated GitHub responses; no live token or remote publication was verified. These results do not establish browser or protocol execution. See [verification evidence](../evidence/verification.json).

For a generic static host, upload **only `out/`** as its document root. For Vercel's repository integration, use the **Next.js** preset and leave its output directory at the framework default, as described above. Verify `/`, `/app/`, `/app/?view=Discover` and `/try-lantern-trail.html` over HTTPS. No application environment variables are required for the existing rehearsal.

On a socket-capable local machine, `npm start` serves `out/` at `http://127.0.0.1:3000`. Check desktop/mobile layout, keyboard/dialog behavior, persistence and errors. Download the standalone game, close the application, disable networking and complete the downloaded file in a fresh browser session. A cached website tab is insufficient evidence. See the [demonstration guide](DEMO.md).

## 2. Verify the contract in a real protocol runtime

The prepared artifact is `contracts/sunset/res/sunset_contract.wasm`, **270,188 bytes**, SHA-256:

```text
7a65f94c90eb11c7e7865362ea3386656e9d89334512b12b7ce313e5ed606c6f
```

It requires a **fresh state-layout-2 deployment**. No migration from an earlier deployment is provided. The hex digest above identifies the file; the frontend asks for the actual deployment's Base58 code hash.

From `projects/sunset`, the existing native/build commands are:

```sh
cargo test --locked --offline --manifest-path contracts/sunset/Cargo.toml
cargo fmt --manifest-path contracts/sunset/Cargo.toml --check
cargo clippy --locked --offline --manifest-path contracts/sunset/Cargo.toml --all-targets -- -D warnings
bash contracts/sunset/scripts/build.sh
npm run check:artifact
npm run test:contract
```

Rebuilding requires the pinned installed Rust 1.96.0 toolchain, Wasm target and cached locked dependencies; see [build evidence](../contracts/sunset/build-evidence.json). These commands use native tests and transactional Wasm host doubles. **None starts NEAR Sandbox.**

Normal small-state testnet settlement now has real receipts, including the successful native payout callback. Both real expiry refunds and exact native withdrawals are recorded in [refund evidence](../evidence/testnet-refunds.json). Remaining protocol work is native transfer failure, callback failure, cap-change edge cases and NFT receiver/resolver scenarios, plus gas/storage at maximum supported state. Use actual Sandbox scenarios for controlled failure cases. The workbench currently proposes 100 Tgas for most calls and 150 Tgas for `nft_transfer_call`; the contract reserves 15 Tgas for callbacks. The successful small-state withdrawal callback used 1.647072781898 of its scheduled 15 Tgas; the broader budgets still need maximum-state and failure-path metering. Retain runtime/protocol version, source/artifact identity, full receipts and balances. [Detailed remaining scenarios](../../../research/2026-11-01-tokenization/VERIFICATION_GAPS.md).

## 3. Prepare artifacts for the existing deployment or a separate fresh contract

The operator's contract is already deployed; use [TESTNET_SHOWCASE.md](TESTNET_SHOWCASE.md) for its matching retained private package and remaining steps. The generic preparation/deployment instructions below apply to a separate fresh deployment, not a command to overwrite `sunset.shiftultra.testnet`.

Choose the final public artifact URL before creating immutable campaign terms. From `projects/sunset`, replace the placeholders with real inputs:

```sh
mkdir -p private
node scripts/prepare-campaign.mjs \
  --pack public/packs/lantern-trail.json \
  --reviewer YOUR_ACTUAL_REVIEWER.testnet \
  --manifest-uri https://YOUR_ACTUAL_HOST/packs/lantern-trail/manifest.json \
  --target 8 \
  --deadline YOUR_ACTUAL_FUTURE_ISO_DEADLINE \
  --release-hours 24 \
  --out private/lantern-trail
```

The output directory must not already exist. Keep it outside every public document root. Publish **only the exact `manifest.json` and adjacent `ciphertext.sunset`** together, preserving their bytes. Retain `artifact.json`, `private-release-backup.json` and `release-args.json` privately and independently of the website. The last two contain the release secret. Repository ignore rules are not access controls. A separate mirror must allow browser CORS; recovery rejects redirects and verifies all original commitments.

Deploy the verified Wasm to the fresh funded testnet contract account. Initialize once with `new {"owner":"ACTUAL_OWNER_ACCOUNT"}`, signed as the contract account; external callers cannot initialize it. Record network, contract account, actual code hash, source revision and transaction/receipt IDs. Read `get_config` and confirm layout version 2 and the intended owner. Keep development control during verification; no immutable deployment or mainnet readiness is claimed.

Use the [contract JSON ABI](../contracts/sunset/README.md) with the actual wallet/CLI. There is no deployment/signing script here, and an exported workbench plan is not a signed transaction.

## 4. Future independently operated demonstrations

The operator-controlled main flow is complete; replay its receipts and read-only state through [TESTNET_SHOWCASE.md](TESTNET_SHOWCASE.md). The steps below describe a new campaign with actual independent participants. Do not repeat the completed campaign's signed actions.

1. The owner signs `create_campaign` using `create-campaign.json`, with exactly **0.05 testNEAR** storage allowance. The named reviewer verifies and inspects the exact decrypted pack, reads the actual agreement digest and signs `approve_campaign` for that digest.
2. An independent sponsor signs `contribute`. A new registered account adds **0.01 testNEAR** storage allowance to its contribution; an already registered account attaches the contribution only. Read `get_account` before choosing the deposit. Demonstrate cap change becoming credit.
3. After funding and before the release deadline, a retained-key holder signs `publish_release`. Confirm one-time creator credit and stewardship NFT mint. The creator separately signs `withdraw`; release credits the contract ledger before this native transfer. Capture canonical state, actual balances and the complete receipt chain.
4. Use separate campaigns to show underfunded expiry and funded-but-unreleased expiry. Each contributor signs `claim_refund`, reads their credit and signs `withdraw`. Confirm duplicates cannot repay. A failed or unknown callback leaves a withdrawal pending; never infer a replacement payout from elapsed time.
5. Transfer the released NFT, confirm the former holder cannot edit its mirror, then let the current holder set a hosted mirror and recover the same committed pack. NFT transfers/mirror changes attach exactly one yoctoNEAR. The NFT grants maintenance authority, not exclusive learning access or money rights.

Publish a content key only when release is intended: even a rejected transaction exposes its arguments. Use disposable sample secrets for failure testing. All real signers should verify the receiver, arguments, deposits and gas. Imported outcome files can match a plan but cannot establish chain authenticity; verify against real RPC receipts and finalized account/campaign/token state.

For the current reader, enter the actual contract account and Base58 code hash in **Testnet setup**. It verifies network/code/block identity, then can verify, play and export released resources. It currently uses `https://test.rpc.fastnear.com`; availability and browser access must be checked. Configuration starts blank on page load.

For a complete public browser dApp, implement wallet connection/sign-out, signed core/NFT actions, live balances/pending operations, receipt reconciliation and published deployment defaults. Recheck signer/configuration changes and rejected/pending actions, then repeat the independent-user flow through the hosted UI. Preserve the explicit local-rehearsal labels until those financial controls actually use the live contract.

Independent recovery remains available without the app:

```sh
node scripts/recover-pack.mjs \
  private/lantern-trail/artifact.json \
  private/lantern-trail/private-release-backup.json \
  private/lantern-trail/offline-game.html
```

Record hosting, browser, Sandbox and signed testnet results separately. Update evidence only after each succeeds; project creation, local commits, successful builds and simulated withdrawals are not proof of public deployment or settlement.
