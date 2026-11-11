# SUNSET: live wallet app and technical commons

The operator wants a more distinctive Web3 interface, ordinary wallet actions, working resource links, and substantial AI/mathematics material. The public experience should contain usable resources and actual network state. They selected the existing live NEAR testnet contract rather than a new permissionless contract.

## Approaches

1. **Existing reviewed contract — selected by the operator.** Integrate a maintained wallet connector and replace the public rehearsal with its live catalog and role-aware actions. Retains the three recorded campaigns and deployed protocol rules. Publishing remains curated: only `shiftultra.testnet` may create campaigns, and two of five campaign slots remain.
2. **New permissionless contract — not selected.** Could permit open publishing and raise capacity, but would require a new contract design, deployment, funding and protocol verification. This is outside this batch.

## Public experience

- Keep the correct tapered SUNSET mark, home navigation, existing coral/forest identity, and light/dark control.
- Redesign landing and app as one coherent protocol interface: architectural grid, layered orbital/resource diagrams, crisp typography, restrained glass surfaces, coral highlights and purposeful motion. Avoid unrelated dashboard cards, invented financial metrics and decorative crypto prices.
- The landing resources are three original, immediately usable technical guides: **Transformer Attention Lab**, **Backpropagation Field Notes**, and **Low-Rank Adaptation Notebook**. Each card is an ordinary real link to its own reader. No campaign link should land in an unrelated default view.
- Readers work without a wallet, retain chapter/search/check progress, expose primary references, and download a complete standalone HTML file. Provide mathematical derivations, worked numerical examples, assumptions and practical exercises. These are free library resources, with no claim they were funded or released by the contract.
- The app opens to this library and the real onchain catalog. Live funding has an honest empty state if no campaign is accepting contributions. The existing released arithmetic campaign and completed refund campaigns remain accessible in onchain history, without dominating the new learning collection.
- Navigation: Explore, Funding, My activity, Studio, and Stewardship. All links and controls must have a complete destination or state. Existing deep links should map to the closest working destination where practical.
- Remove the account role-play selector, simulated balances, rehearsal clock, unsupported ecosystem/demo cards, unsigned transaction workbench, manual contract address/code-hash setup and the visible “verify contract” step from the public app.
- Retain original sample files, private recovery data, test evidence and protocol code. The rehearsal engine remains available to automated checks but is not a public product route. Do not erase or reinterpret historical onchain evidence.

## Wallet and live data

Builder choice: use the current `@hot-labs/near-connect` SDK recommended by NEAR's wallet-login documentation; it supports the existing transaction action format without adding a general-purpose blockchain SDK. Pin the actual reviewed package version in the lockfile. Load wallet functionality on the client, share one connector instance, restore a previous connection without opening a chooser, and react to account/sign-out changes. Do not request an access key at login. Exclude MyNearWallet to respect the operator's earlier preference.

The header shows **Connect wallet** or the actual connected account with disconnect/change-wallet actions. Financial buttons connect when needed and request explicit wallet approval for the real transaction. Reading never prompts for a wallet.

Use `sunset.shiftultra.testnet` and recorded reviewed code hash `9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx`. Validate network/code automatically when fetching the catalog and again immediately before requesting a signature. Fail closed with a useful retry message when verification or RPC access fails; never substitute local financial data. Hide implementation details from the normal journey; advanced provenance/explorer links remain available.

Read configuration, campaign and account state from the same finalized block where required for a plan. Preserve integer yoctoNEAR and nanosecond arithmetic. A cached UI snapshot is not sufficient authorization for a new payment.

## Complete actions

- **Sponsor:** live Active campaign only, positive amount, actual signer registration read from the contract, exact economic amount plus the contract's one-time storage allowance when necessary. Explain the total before wallet approval and disclose surplus credit/refund terms.
- **Refund:** derive eligibility and the signer's unrefunded contribution from live state. Claim credit, then show a distinct withdrawal action. Do not label credited money as already paid out.
- **Withdraw:** use actual available credit; block while the account has a pending operation. Read subsequent callback/account state before claiming native payout completion. Preserve unknown/pending outcomes and avoid automatic resubmission.
- **Publish:** owner-only contract creation. Studio accepts a strict valid resource pack, prepares encrypted public files and a private release backup, requires the creator to retain the backup, accepts a real HTTPS manifest location, and checks hosted bytes against commitments before creation. Reuse the existing crypto/preparation/transaction-plan rules. Explain that uploading/hosting the encrypted files is a creator step; do not pretend the static site has an upload service. The creator is the connected owner; reviewer must be a different account.
- **Review:** only the named reviewer can approve. The reviewer restores the content backup/key locally, decrypts and inspects the exact committed resource, then approves the actual agreement digest. Merely checking a checkbox does not replace content recovery.
- **Release:** require current Funded state, valid deadline and locally verified content/key commitments before publishing. Explain that submitting publishes the content key even if execution fails. Avoid saving private unreleased keys in persistent browser storage.
- **Stewardship:** actual holder can transfer the NFT and change its verified mirror; reject old-holder/stale-state actions. Use the exact one-yocto deposit. Support ordinary account transfer; an advanced transfer-to-contract action may use the existing transfer-call planner with bounded message and explicit receiver semantics.

Ordinary users see only actions available for their connected account and the current campaign state. Role restrictions must also be checked immediately before asking the wallet to sign.

## Confirmation and interruption

Reuse the validated transaction builder and exact receipt checks. Bind signer, contract, method, gas, attached deposit and arguments. Treat a wallet-returned object/hash as a reference to inspect against testnet RPC, not proof of settlement. Only display confirmed success when receipt validation passes. Withdrawals additionally require callback/account settlement.

Handle modal cancellation, disconnect, account switching, RPC failures and unknown outcomes. Clear stale signer/account data. Retain a minimal pending intent across wallet redirects/reloads without storing wallet credentials or unreleased content keys; an argument digest can bind a resumed receipt without retaining private arguments. Do not automatically retry a potentially submitted action. If no hash is available, tell the user to inspect wallet activity before a new attempt. No optimistic balance mutation.

## Technical resources

Reuse the strict guide schema, data-only reader and self-contained exporter. Content is original CC0 explanatory text, with references to primary papers/course material, not copied paper sections or unsupported research claims.

- Attention: Q/K/V shapes, scaled dot products, stable softmax, a complete three-token numerical example, causal masks and context-memory growth. Reference *Attention Is All You Need*.
- Backpropagation: forward computation, chain rule, sigmoid/BCE gradient, one numeric parameter update and a finite-difference gradient check. Reference Stanford CS231n notes. Distinguish mathematical toy assumptions from real training systems.
- Low-rank adapters: frozen base and trainable factors, dimensions and rank, concrete parameter/memory arithmetic, scaling and merge conditions, and an exercise showing the update's rank ceiling. Reference the original LoRA paper; avoid claiming universal memory/quality guarantees.

Provide source links alongside the reader and plain-text references inside the retained copy. Keep formulas readable without fetching MathJax, a model API or external fonts at runtime. A small native interactive calculation is optional if it directly aids these lessons; the worked examples and downloads are required.

## Verification

- Add meaningful tests for transaction eligibility/roles, exact deposits, new-account registration, signer switching, code mismatch, wrong-chain/receipt mismatch, interrupted/pending outcomes and withdrawal settlement. Use controlled RPC/wallet doubles for signing paths; label that scope.
- Validate every new guide and independently recompute its numerical examples. Confirm the export contains complete data/runtime and no network dependency.
- Update static-page/link checks for the actual public destinations and verify all featured cards resolve to the correct resource.
- Update browser smoke to the new public journey: desktop/mobile themes/home links, resources/search/progress, actual original-byte downloads and cold offline use; wallet chooser open/close without signing. Existing rehearsal assertions no longer describe the public UI and should not silently substitute for live coverage.
- Run the application/type/WASM checks, production build, static pages and dependency review. Preserve Rust/WASM bytes. Use a clean owned browser for visual and interaction review; never use operator keys or repeat the already-completed signed actions.
- Record browser/network/signed-action limits accurately. Code/tests cannot establish a new human-wallet transaction was executed. The operator performs the first new signed journey through their own wallet after deployment.

## Delivery

Produce one integrated implementation with verified local commits; the operator pushes from their terminal. No contract redeployment, signed campaign operation, wallet import, public social post or submission is part of this batch. Update current README/ledger/evidence to describe the live UI and distinguish new automated verification from earlier actual protocol receipts.

Primary connector reference: https://docs.near.org/web3-apps/tutorials/wallet-login

The operator selected the contract approach and approved this design for implementation on 11 November 2026. Visual/component implementation, package version after inspection, layout spacing and exact copy are builder choices under the constraints above.
