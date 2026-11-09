# SUNSET demonstration and local verification

SUNSET sponsors one precisely committed public resource. A timely matching key release credits the fixed creator up to the funding cap. Missed funding or release conditions permit contributor refunds. The released learning game can be retained independently of the website.

The application is a browser-local rehearsal. Accounts are role-played, balances are simulated and withdrawals do not transfer tokens. The testnet panel is a separately configured read-only viewer. No wallet, API key, database or external deployment is needed for the steps below.

## Run the complete socket-free check

From `projects/sunset`:

```sh
node scripts/verify-local.mjs
npm test
npm run test:contract
```

The workflow uses the actual seed, crypto, recovery, ledger and stewardship APIs. It checks nine scenarios: seeded states; capped contribution and change; independent recovery from retained files; corrupt backup rejection; one-time retained-key release; stewardship transfer and mirror authority; underfunded refund; funded missed-release refund; and access-budget claims/remainders plus withdrawals. Final deposits and rehearsal withdrawals both equal **21.8 simulated NEAR**, with no remaining campaign escrow or budget balance on the completed branch.

Recovery runs in a separate Node process from a temporary directory, using an encrypted artifact and private backup saved as files. It compares the exact five-question recovered pack to the original sample and rejects a changed backup key without creating output. Temporary secret files are removed on completion. Child processes use ignored or regular-file streams so the check needs no IPC sockets.

An invariant or subprocess error exits nonzero. The script does not start a website, browser, NEAR protocol runtime or network connection. Its final line preserves that distinction. `test:contract` executes the checked-in Wasm with host doubles; it is not Sandbox or transfer-receipt proof.

## Rehearse in a local browser

These are local rehearsal instructions. Separately, [actual hosted/browser evidence](../evidence/browser-showcase.json) now proves the desktop live reader, original/mirror recovery and actual downloaded game completed in a fresh browser with Chrome DevTools offline enabled before file load. This is not an OS network-adapter toggle. The recorded 3 November review also passed desktop and 390×844 viewport navigation without horizontal overflow. Broad physical-device, accessibility and cross-browser QA remain open.

```sh
npm ci
npm run dev
```

Open `http://127.0.0.1:3000` in a fresh browser profile and select **Open the app**, or go directly to `http://127.0.0.1:3000/app/`. For a static demonstration, use `npm run build` followed by `npm start`. Start in **Local rehearsal**. In **How it works**, use **Reset sample rehearsal** only after saving any private backups you want to keep.

### 1. Inspect the public-release agreement

1. In **Discover**, open **The Lantern Trail** using **Help make it public**.
2. Expand **Agreement, hashes & independent recovery**. Inspect the fixed creator `maker.testnet`, reviewer `teacher.testnet`, funding target, release window and exact hashes.
3. Keep the sponsor role at `grove.testnet`. Explain that sponsorship funds public release and gives no exclusive prerelease copy. The sample adventure can already be tried free.

### 2. Complete capped funding

1. The campaign starts at 6.4 of 8 simulated NEAR. Enter **3** and select **Sponsor public release**.
2. Verify only 1.6 is accepted into campaign escrow and 1.4 becomes Grove's claimable change. The campaign becomes funded.
3. Alternatively, use 1.6 for the shortest story with no excess change. All later balance values must follow the amount actually entered.

### 3. Release independently from a retained backup

1. In **Agreement, hashes & independent recovery**, save the encrypted artifact.
2. Switch the role to `teacher.testnet`. Save a private backup if needed. Use **Restore private backup** to load the retained file; **Use saved demo backup** is the shorter seeded demonstration.
3. Select **Verify & publish release key** before the displayed release deadline. Verification must bind the key, ciphertext, plaintext and manifest to the agreement.
4. Observe public release and fixed creator credit. Switching the account that submits the key must not redirect creator compensation. A repeated release must not credit again.
5. Treat an actual onchain release key as public immediately upon transaction submission, even if that transaction fails. Use only sample secrets in this rehearsal.

### 4. Retain the game without the website

1. Select **Play the adventure**, then **Download offline game**.
2. Stop the local server and close the website tab. Open a fresh browser profile with networking disabled before opening the downloaded HTML file.
3. Complete all five questions. Verify the title, feedback, progression, completion and restart. Inspect browser requests to confirm gameplay needs no remote resource.
4. Keep the downloaded file and its hash. Merely revisiting a cached website is not this independence check. Browser execution remains a separate check from successful Node artifact generation.

For independent recovery from retained files, with the website stopped:

```sh
node scripts/recover-pack.mjs path/to/encrypted-artifact.json path/to/private-backup.json path/to/offline-game.html
```

The backup contains a release secret. Keep it outside public hosting and do not put its contents in a screenshot, issue, recording or commit. The script verifies commitments before writing output.

### 5. Show both failed-release outcomes

1. As `grove.testnet`, open **River Routes** and select **Claim my contribution refund**. Its underfunded campaign has expired. Grove's 2.4 becomes claimable; a repeated claim must fail.
2. For the funded-but-unreleased outcome, reset a separate rehearsal, fund The Lantern Trail, leave its key unpublished, then use **How it works → Advance rehearsal by 8 days**. Claim Grove's and Cedar's contributions from their own role-play accounts. Release is now unavailable.
3. In **Activity**, inspect each account's balance and **Rehearse withdrawal**. Verify a second withdrawal of the same credit fails. Events and CSV are rehearsal records, not blockchain transaction receipts.

### 6. Prepare and review a new pack

1. In **Creator studio**, choose an unused resource ID and an independent reviewer. Leave the JSON file empty for the original sample or upload a strictly valid data pack.
2. Confirm the rights statement only for content you are entitled to release. Select **Encrypt & prepare draft** and save/check the private release backup.
3. Switch to the named reviewer. Select **Verify as named reviewer** and inspect every decrypted question, choice, correct answer and explanation.
4. Confirm the saved backup and select **Approve committed agreement**. Changed or stale agreement data must require a new review. A reviewer signature or matching hash alone does not establish rights or educational quality.

### 7. Transfer maintenance responsibility

The local verification script exercises mint-on-release, a transfer from Maker to the library, mirror reset on transfer, rejection of Maker's later mirror edit and acceptance of the new steward's edit. It also checks that the public key, committed content, creator beneficiary and money remain fixed.

When demonstrating the integrated stewardship interface, show the current owner and history before and after transfer. Explain the actual right: maintain a recovery mirror for the already-public resource. Ownership does not revoke existing offline copies, redirect creator payment or confer copyright. A mirror URL still needs content verification; setting a URL is not proof of availability.

The final integration record must point to the current UI labels, contract ABI and rebuilt artifact evidence. A passing local transfer scenario does not establish a deployed NFT or successful onchain ownership transfer.

## Record evidence honestly

The [main testnet record](../evidence/testnet-showcase.json) now has eleven finalized transactions: ten successes and one intentional former-steward rejection. The campaign is `Released`; its native creator payout is 0.1 testNEAR, `paid` matches and `pending` is null. Its 15-Tgas withdrawal callback burned 1.647072781898 Tgas and succeeded. The NFT holder is `reviewer.shiftultra.testnet`, whose new mirror recovers the same pack. All roles share one operator and both artifact paths share a host.

The [browser record](../evidence/browser-showcase.json) separately proves actual hosted original/mirror recovery, browser download, cold-browser offline completion (5/5) and restart. Do not rerun the completed signed actions for a recording: show finalized receipts and read-only views. Both real deadline-expiry paths and native principal withdrawals are recorded in [refund evidence](../evidence/testnet-refunds.json); do not rerun them. Failure/max-state protocol cases, independent educator review, sponsor feedback and final submission remain pending. The [threat model](THREAT_MODEL.md) identifies the remaining trust boundaries.
