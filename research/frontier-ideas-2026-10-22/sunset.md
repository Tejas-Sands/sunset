# SUNSET and revenue financed public ownership

**Subsequently selected for the build.** This file preserves the original research proposal. The [maintained project architecture](../../projects/sunset/README.md) specifies the selected learning application, zero-cost prototype and NEAR testnet workflow.

**A creator launches a paid digital product with a fixed exit price. Customer purchases help pay that price. Once the agreed buyout is funded and completed, everyone receives the committed asset under a specified open license.**

Imagine a useful specialist tool whose purchase screen says: “Your use pays the creator and brings this version closer to being available to everyone.” Its users can help end the restriction they are paying to pass through. The creator chooses this arrangement at launch and gets a defined reward for making something useful.

The first audience would be independent creators who want both compensation and widespread reuse: authors of specialist datasets, educational material, software components or model adaptations they have the right to release. The long-term ambition is a way to create public resources through ordinary commercial demand.

This is a proposed product and mechanism, not an existing service.

## A concrete transaction

Suppose a creator offers a service based on an original data pack. The following amounts are illustrative testnet parameters, not pricing research:

- A completed use costs 1 NEAR before release: 0.2 for service delivery and 0.8 toward the asset's buyout.
- The asset's fixed buyout cap is 8 NEAR.
- Ten completed purchases would fund that buyout. Only the remaining amount is collected on a purchase that would exceed the cap; the excess stays with the buyer as a claimable balance.
- The committed pack and its release license are identified before the first purchase. Completing the buyout publishes the decryption key and credits the agreed creator payment.
- An unrelated person obtains the pack, checks its hash, and uses it without buying the asset. A hosted service can still charge separately for computation or support.

This caps the charge for the specified asset. It does not claim to cap a company's total lifetime profit or make cloud computing free. A creator can develop a genuinely new version under a new agreement; the released version must remain usable and available under its granted terms.

Users buy immediate service value. That is the initial reason to pay before release. It does not eliminate the incentive to wait near the finish line. An optional sponsor could complete a nearly funded buyout, but a sponsor is not assumed in the base design.

## What NEAR would enforce

One native-NEAR contract would record the asset commitment, agreed license reference, cap, payment split, creator beneficiary and release state. It would account for service charges and buyout contributions separately. Funding means actual credited deposits under the contract's rules, rather than an operator's report of offchain sales.

The important boundary is between funding and fulfillment. Reaching the cap should enter a visible `FUNDED_AWAITING_RELEASE` state. Public release is recorded only after a valid key and the agreed release evidence arrive. A progress bar is not evidence that a usable asset was delivered.

The creator's buyout payment must remain escrowed until valid disclosure. If disclosure fails by a specified deadline, contributors recover the buyout portion under the published refund rule. Fees for service already delivered remain separate. This provides a narrower, defensible release-or-refund outcome even if unattended release cannot be achieved.

To claim that the founder cannot change the deal, the deployed contract must have no route for the founder to change its cap, replace its asset, redirect its beneficiary or upgrade away its restrictions. Removing an account's keys alone is insufficient if its code can add keys or update itself. NEAR documents both restricted keys and contract-controlled locked accounts. [NEAR access keys](https://docs.near.org/protocol/accounts-contracts/access-keys).

There is no claim that other chains cannot implement the idea. NEAR offers the shared account and settlement state, scoped agent interaction, and an ecosystem of confidential execution and community treasury tools that can make this a coherent application.

## The ambitious part is unattended release

A public smart contract cannot hide a decryption key. An ordinary creator-controlled server can withhold it. The stronger design needs a release mechanism whose operation does not depend on the creator pressing a button at the end.

One candidate is a pinned OutLayer module with access to the correct asset key, callable by parties other than its creator. OutLayer documents confidential secrets and binding to exact WASM bytes; it also documents owner-controlled access changes. A creator-owned revocable secret would therefore fail this project's promise. Key ownership, deletion authority, future invocation and payment for execution must all be demonstrated. [OutLayer secrets](https://app.outlayer.ai/docs/secrets).

The module must accept authentic finalized funding state, rather than an arbitrary caller's assertion or an unauthenticated RPC response. A hardware attestation establishes something about execution; it does not establish that an input is true, that the data pack is valuable, or that a future worker will remain available. OutLayer's approved worker measurements and hardware assumptions remain part of the trust boundary. [OutLayer verification](https://app.outlayer.ai/docs/trust-verification).

A separate time-based fallback could precommit eventual disclosure even if early revenue-triggered release stalls. drand supports encryption to a future beacon round. Its guarantees depend on the beacon's security and continued operation; a time lock is not a revenue oracle. Binding a fallback to the same correct asset key needs its own proof. [drand timelock documentation](https://docs.drand.love/docs/timelock-encryption/).

The research decision is explicit: the escrow version can promise release or refund. “Automatic release after funding even with the founder offline” is a stronger claim that earns its place only after an independent caller actually demonstrates it. Do not blur these two grades of implementation.

## The first asset

Use one small original data pack, with no personal or third-party restricted data. A practical NEAR-focused example is a set of original annotated transaction-failure scenarios and explanations created during the hackathon. A buyer can use the pack through a paid diagnostic exercise; after release, another developer can download and reuse the same pack.

The pack is the sample commercial asset. The contract, application, agent integration and release machinery belong in the public prototype repository. Do not present already-open application code or someone else's open model as an asset we have newly liberated.

This choice keeps the first proof about the economic transition and delivered asset. Educational collections and specialized model assets are later applications with their own quality and rights requirements. Release can cover only rights the creator controls; a chain entry cannot manufacture copyright or patent ownership.

## The three minute demo

1. Inspect the agreed asset hash, license, split and cap. Download the committed ciphertext before paying.
2. Have independently budgeted buyer agents purchase and receive useful results. Show their actual debits and the creator's service earnings.
3. Attempt to raise the cap, replace the pack or count the same completed purchase twice. The controlling contract rejects each attempt.
4. Make the final purchase. Show the difference between funded, key disclosed and creator credited.
5. Use a fresh client with no purchase history to decrypt and use the exact pack. Continue with the original website stopped to demonstrate what is independently reusable.
6. Exercise a separate failed-release agreement and refund its buyout contributions. If the stronger confidential release mechanism works, separately turn off the founder's process and trigger disclosure from another caller.

The meaningful outcome is successful independent reuse of the asset, alongside the creator's correct payment. Merely changing an “open” label would not establish the product.

## The closest precedents

| Precedent | Established idea | What SUNSET would need to contribute |
| --- | --- | --- |
| Blender's community buyout in 2002 | A community financed the release of a useful proprietary tool | A repeatable, inspectable agreement rather than a one-off organizational campaign |
| Unglue.it Buy-to-Unglue, described in 2013 | Purchases advanced a book's open-license release date; its own design discusses people waiting near the target | This is direct economic prior art. Agent use, asset verification and independent fulfillment must provide a useful implementation difference |
| Functional Source License | Software versions convert to MIT or Apache terms after two years | Revenue-triggered completion and asset delivery, with time-based licensing acknowledged as prior art |
| Purpose Evergreen Capital | Investment without voting rights and with capped returns | Inspiration for finite financial claims; a contract prototype does not establish legal company ownership |

[Blender history](https://www.blender.org/foundation/history/), [Unglue.it's original model](https://blog.unglue.it/2013/08/06/a-new-kind-of-ungluing-campaign/), [Functional Source License](https://fsl.software/), [Purpose Evergreen Capital](https://purpose-economy.org/en/pec/).

SUNSET is not the invention of buying something into the commons. The proposed contribution is a usable agreement connecting paid digital service, capped asset funding and independently checkable release. Demand from suitable creators remains unvalidated.

## Track fit and the first decision

Open Innovation is the most direct conceptual fit. Autonomous Business and Agent Economy become credible if an agent actually sells and delivers a useful service, earns revenue and pays costs. AI Swarms needs independently budgeted agents making consequential choices about use or a buyout; scripted chat personas would add little.

Privacy needs a working confidential application with a clearly stated boundary. Social Money needs a real community budget workflow using Sputnik DAO or Trezu, such as optional maintenance funding after release. Neither is in the minimum proof. A buyout counter alone does not justify the DeFi or Investment Thesis tracks. [Official track descriptions](https://nearhackathon.com/HACKATHON.md).

The first implementation question, once the development window opens, is whether a caller independent of the creator can complete a correctly funded disclosure using the exact committed asset and key. If that fails, retain the honest escrow outcome or stop calling the transition autonomous. This is a research candidate, not a claim of a verified implementation.
