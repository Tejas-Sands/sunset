# SUNSET — Support once. Share forever.

SUNSET lets a community sponsor a precisely committed public resource. A timely matching key release credits its fixed creator up to the funding cap. Missed funding or release conditions allow contributor refunds. Readers keep a complete resource without an account or wallet; a transferable stewardship NFT maintains its recovery mirror.

The current source includes a live NEAR testnet wallet app and three original AI/math guides. The public financial rehearsal has been replaced by actual contract/account reads and wallet-approved actions. This batch still needs the operator's push, deployment and post-deployment acceptance; the production domain is [sunset-lemon.vercel.app](https://sunset-lemon.vercel.app). [Implementation and acceptance](docs/LIVE_WALLET_2026-11-11.md) distinguish these scopes.

## Read and explore

- **Transformer Attention Lab:** tensor shapes, scaled logits, stable softmax, complete weighted-output example, causal masking and context cost. Route: `/resources/transformer-attention/`.
- **Backpropagation Field Notes:** sigmoid/BCE derivation, exact gradients, a numerical update and finite differences. Route: `/resources/backpropagation/`.
- **Low-Rank Adaptation Notebook:** factor dimensions, rank, parameter/weight-memory counts, scaling and merge conditions. Route: `/resources/low-rank-adapters/`.

Each has four chapters, eight exercises/checks, primary references, a working browser calculator and an exact self-contained HTML download. These free CC0 guides are library resources; they have not been funded or released by the contract. Downloads contain the full reading guide and worked examples; hosted calculators are separate. No model API or external math renderer is needed.

Landing, app and readers share the tapered SUNSET mark, coral/forest visuals and a persistent light/dark switch. Brand links return home. Search and chapter/check progress work locally; reading remains available when storage or RPC is unavailable. The original [learning sample](public/try-lantern-trail.html), [maintainer handbook](public/try-maintainer-handbook.html) and [workshop kit](public/try-workshop-kit.html) retain their exact original bytes.

## Run

Requires Node.js 22.9+ (tested with 24.17) and Python 3 for the static server:

```sh
cd projects/sunset
npm ci
npm run dev
```

Open `http://127.0.0.1:3000/` or `/app/`. For the production static export, use `npm run build` then `npm start`. No application environment variables, database, backend signer or model API key are needed. Wallet transactions require a supported testnet wallet, testNEAR, working RPC and HTTPS or localhost.

## Live wallet workflow

The app uses pinned `@hot-labs/near-connect` 0.12.0. Login requests no access key and does not automatically open a wallet. MyNearWallet is excluded. The header shows the actual connected account and change-wallet/disconnect actions. Nothing is signed merely by browsing or connecting.

- **Explore:** free technical library and actual onchain catalog summary.
- **Funding:** current campaigns, explicit empty state and historical released/refund campaigns. Sponsors approve exact integer amounts, plus 0.01 testNEAR for first-time account storage; gas is separate.
- **My activity:** the signer's actual contributions, withdrawable credit, pending withdrawal and callback-confirmed native payouts. A refund claim credits the account; withdrawal is a separate action.
- **Studio:** only `shiftultra.testnet` can publish. Import a strict original resource, set terms, generate encrypted public files/private backup, retain the backup, host the two public files, then approve creation. Hosted bytes are recovered against commitments before signing. The different named reviewer must decrypt/inspect before approval.
- **Stewardship:** the actual holder can transfer its maintenance token or set a verified recovery mirror, with exact one-yocto deposits. Readers keep access and the original creator beneficiary stays fixed. Advanced receiving-contract transfers use the existing callback semantics.

Network, code, configuration, catalog and signer data are checked at a finalized block and refreshed before each action. The public UI has no manual “verify contract” step. Wallet-returned hashes are fetched from testnet RPC and bound to signer, receiver, method, arguments, gas and deposit before success is shown. Withdrawals additionally require settled callback/account state.

Interrupted actions retain a per-account, digest-only transaction reference containing no wallet credentials, raw arguments or unreleased content key. Pending/unknown results block another request and are never automatically resent. Blocked tracking storage prevents signing while reading stays usable. Private release keys remain in memory and retained private files until intentionally published. A key in a submitted transaction is public even if execution fails.

## Existing deployment and evidence

Contract: `sunset.shiftultra.testnet`; owner: `shiftultra.testnet`; reviewed code hash: `9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx`. The fresh 11 November read matched the reviewed bytes and showed three campaigns: one Released and two Refundable, all with zero escrow and no active funding round. Two of five campaign slots remain; the deployment allows 100 permanent registered participants. Publishing is curated.

The [2 November main showcase](evidence/testnet-showcase.json) verified 0.1 testNEAR funding/release/native creator payout and stewardship handover. [Both actual expiry refunds](evidence/testnet-refunds.json) and native principal withdrawals passed on 3 November. [Earlier hosted/offline browser evidence](evidence/browser-showcase.json) records exact original/mirror recovery and actual offline completion. All roles shared one operator and both mirrors shared one host. **Do not replay these completed signed actions.** [Read-only showcase guide](docs/TESTNET_SHOWCASE.md).

The new wallet signing paths use controlled RPC/injected-wallet doubles in automation. No new human-wallet signature, settlement or contract deployment is claimed. Protocol failure/max-state gas, independent users, broad physical-device/accessibility QA and mainnet readiness remain unverified. The contract is upgradeable while full-access keys exist. The [contract README/ABI](contracts/sunset/README.md) explains its limits and NFT callback behavior.

## Verify

```sh
npm run check
npm run build
npm run test:pages
npm run test:rust
npm run test:browser
# After deployment:
npm run test:browser -- --url https://sunset-lemon.vercel.app
```

`check` runs application/type checks, nine local model workflows, artifact digests and compiled-WASM host tests. `test:rust` runs native tests, formatting, Clippy and a reproducible build. Neither host doubles nor the local ledger establish NEAR protocol execution. The unchanged artifact is 270,188 bytes, SHA-256 `7a65f94c90eb11c7e7865362ea3386656e9d89334512b12b7ce313e5ed606c6f`.

The browser suite requires `agent-browser` 0.37.1 and installed Chromium on a machine permitting sockets. It checks real pages/RPC/chooser, six exact public downloads, mobile/theme/search/progress/math interactions and cold offline files, then separately checks controlled-wallet orchestration. Unavailable prerequisites fail nonzero. `test:release` combines local checks, the live npm advisory service and this browser gate. [11 November evidence](evidence/live-wallet-2026-11-11.json) records the local-server restriction and owned-browser component checks separately. New deployment/CI acceptance remains pending; older successful CI runs do not prove this batch.

Independent retained-file recovery works with the website stopped:

```sh
node scripts/recover-pack.mjs artifact.json private-release-backup.json offline-resource.html
```

CLI preparation uses `scripts/prepare-campaign.mjs` with `--pack`, `--reviewer`, `--manifest-uri`, `--target`, `--deadline` and a new private `--out` directory. Keep `private/`, wallet credentials, release backups and secret arguments outside hosting/version control. Publish only the exact manifest and ciphertext together. Original rehearsal libraries and model scenarios remain for automated checks; they are no longer a public product flow. Existing browser-local rehearsal data is not overwritten.

## Publish and demonstrate

From the repository root, the operator pushes verified local commits:

```sh
git --git-dir=.sunset-git --work-tree=. push origin main
```

Vercel uses the Next.js preset, root `projects/sunset`, `npm run build`, Node 24.x and the default output setting. [Deployment guide](docs/DEPLOYMENT.md), [current demo](docs/DEMO.md), [build decisions](docs/BUILD_LEDGER.md) and [submission package](docs/SUBMISSION_PACKAGE.md) give the handoff. GitHub authentication stays local to the laptop.

The accepted [launch film](media/launch/README.md) is unchanged: 44.667 seconds, 1080p30, warm voice and continuous dark-green/coral world. Local movie: `.publication/sunset-final/sunset-launch.mp4`, SHA-256 `57348b1f7fea925c31b61650808bcc65f47b70d74b1889831674e8bb2e48022f`. [Script](media/launch/SCRIPT.md), [credits](media/launch/CREDITS.md), [delivery guide](docs/LAUNCH_VIDEO.md).

Candidate tracks remain Open Innovation, Social Money and NFTs That Do Something, subject to organizer judgment and the human's final choice. The project has not been submitted. [Submission instructions](docs/SUBMISSION.md) retain the required human inputs and final-send approval. Independent adoption and demand are not established.

## Original design and research

[Council decision](../../research/2026-11-01-council/README.md), [architecture](ARCHITECTURE.md), [original contract specification](CONTRACT.md), [workflows](WORKFLOWS.md), [operations](OPERATIONS.md), [October plan](BUILD_PLAN.md) and [research](research/2026-10-22/README.md) retain their historical scope. The larger Supabase/order/managed-release architecture is deferred. Software: MIT; original guides/sample packs: CC0-1.0. Referenced papers retain their own licenses.
