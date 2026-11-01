# SUNSET prior art and economics

The problem is financing resources that can become broadly reusable after a finite creator payment. SUNSET's proposed mechanism combines paid licensed access, a capped buyout held in escrow, independent disclosure and separate delivery budgets. The demand question is whether a specific creator and sponsor prefer that arrangement to an ordinary commission followed by an open release.

## Closest precedents

| Precedent | Established mechanism | Consequence for SUNSET |
| --- | --- | --- |
| Unglue.it Buy-to-Unglue | A rights holder specifies a sales target; purchases advance a future Creative Commons release date | Direct economic prior art. SUNSET cannot claim to invent purchase-funded public release |
| Blender community buyout | A community funded a proprietary tool's open release in 2002 | Buyouts can work for an already valuable resource with an existing community; this is not evidence of demand for a new learning module |
| Subscribe to Open | Existing institutional subscriptions collectively enable open publication, renewed by period | Institutions are plausible public-benefit buyers; continuing creation still needs continuing finance |
| Functional Source License | A software version converts to MIT or Apache 2.0 after two years | Time-based conversion is established and differs from revenue-triggered disclosure |
| POTLOCK | An open funding stack with donations, campaigns and funding rounds | NEAR already has public-goods funding infrastructure; a generic campaign dashboard adds little |

Unglue.it's 2013 proposal explicitly considered buyers waiting near the target. Its solution included a future release date that moves earlier with sales, rather than SUNSET's proposed escrow-and-deadline refund. The currently retrieved rights-holder guide emphasizes Thanks-for-Ungluing for already openly licensed books; the historical proposal does not establish that Buy-to-Unglue is presently offered or commercially successful. [2013 mechanism](https://blog.unglue.it/2013/08/06/a-new-kind-of-ungluing-campaign/), [current guide](https://unglue.it/rightsholders/).

Blender's own manual records €100,000 raised in seven weeks in 2002. Its accumulated users and recognized tool mattered; copying the funding mechanic does not reproduce that audience. [Blender community history](https://docs.blender.org/manual/en/2.90/getting_started/about/community.html).

Subscribe to Open conditions an annual opening on sufficient institutional participation. Annual Reviews reports opening its 2023–2025 volumes through that model. That is publisher-reported adoption, not a controlled comparison of fundraising mechanisms. [Community explanation](https://subscribetoopencommunity.org/), [Annual Reviews](https://www.annualreviews.org/S2O).

FSL converts each software version after two years; it should not be described as a revenue oracle or assumed to be the right license for lesson content. POTLOCK's documented scope includes fundraising and matching. This review does not establish that every possible POTLOCK configuration lacks release conditions. Compare exact contract behavior before claiming a unique protocol. [FSL](https://fsl.software/), [POTLOCK](https://docs.potlock.org/).

The existing local NEAR Builders collection also contains learning-platform and ecosystem-education ideas. It is a limited board sample, not a complete competitor census or a list of winners. It strengthens the case for showing the specific release/recovery behavior instead of presenting another AI learning portal. [Collected project index](../../../../research/nearbuilders/2026-10-22/project-index.md).

## What could be meaningfully different

The defensible contribution is a reusable agreement with observable outcomes: buyers receive the committed resource; the creator cannot receive buyout escrow without the committed disclosure; a different licensed adult can release it; eligible contributors can recover the agreed portion; and released copies remain useful without the original operator.

Each clause needs its own demonstration. A copied key must not redirect the creator payout. A valid key must correspond to reviewed ciphertext. An open license must actually cover the resource. An exported copy must function without a hosted dependency. These are implementation properties, not evidence of global novelty.

## Who might pay

| Actor | Immediate reason to participate | Main uncertainty |
| --- | --- | --- |
| Resource creator or local educator | A defined reward for an original or appropriately licensed adaptation | Is the target enough to justify production, review and delayed buyout income? |
| School or community administrator | A usable licensed module and authorized group distribution | Is the module more useful than available open alternatives? |
| Foundation or public-benefit sponsor | Finance a specific resource becoming reusable beyond its first group | Can the sponsor procure it without wallet and reporting friction? |
| Delivery or teacher-support provider | A separately funded, bounded service commitment | Does the grant cover actual time, logistics and support? |

These are customer hypotheses. No interview, purchase, institutional commitment or willingness-to-pay result is implied.

The learner should not be the fundraising customer. The first workflow keeps wallets and expenditure with adults, while retaining a free introductory resource. For a later field project, a sponsor may buy all required licenses through the existing order mechanism. A direct donation or special completion top-up would require an explicit contract extension; the current design does not have one.

## Incentives and failure modes

**Waiting remains rational for some buyers.** Immediate access must be valuable enough to justify paying before global release. A sponsor may value the broader public benefit, but that preference cannot be assumed. Concealing the target or inventing scarcity would not solve the underlying demand problem.

**Refunds protect a defined contribution, not the buyer's entire experience.** Accepted service fees remain earned. Time spent waiting, transaction friction and the value of an unusable lesson are not automatically compensated. An expired unaccepted order follows the separate full-economic-refund rule.

**Delivery before acceptance has a commercial cost.** A buyer receives bytes before settling, and can refuse acceptance. This design enables inspection and recovery but cannot provide strong DRM for offline recipients. Treat it as an explicit policy to validate with creators.

**The creator may have a cash-flow gap.** Buyout compensation stays escrowed until disclosure. Service fees go to the fixed operator beneficiary, which may be a different account. A creator who needs upfront production funding may prefer a conventional commission; changing to milestone advances changes the guarantee and is outside the chosen first mechanism.

**A small buyout allocation can make the target impractical.** Larger service overhead leaves less of each purchase funding the resource. Equally, an unrealistically large buyout allocation can leave too little for actual delivery costs. The split needs evidence from a real workflow.

**Version churn can undermine the promise.** If a creator immediately replaces a released version with another closed version, public reuse is valuable only if the released version is independently complete and useful. Commit runtime requirements and include the assets needed to use the specified version.

Threshold funding belongs to a much older public-goods literature. Tabarrok's 1998 paper analyzes dominant assurance contracts under specified game assumptions. SUNSET's simple refund rule does not inherit a proof that everyone will contribute; adding failure bonuses would require another funding source and a new mechanism analysis. [Original paper](https://mason.gmu.edu/~atabarro/PrivateProvision.pdf).

## Illustrative cash flows

These amounts are testnet accounting examples, not recommended prices, exchange-rate estimates or observed demand. Gas, storage collateral and provider costs are excluded from the economic columns.

For target `T`, maximum per-order buyout `b` and service portion `s`, completing the buyout needs `ceil(T / b)` accepted orders if all accepted orders use the maximum available buyout. The last contribution is limited to the remaining target. Extra authorized payment is change, not revenue. This arithmetic says nothing about how many buyers will appear.

| Scenario | Target | Buyout per ordinary order | Service per order | Accepted orders | Buyout collected | Service earned |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Half funded | 8 | 0.8 | 0.2 | 5 | 4 | 1 |
| Complete | 8 | 0.8 | 0.2 | 10 | 8 | 2 |
| Smaller buyout allocation | 8 | 0.4 | 0.2 | 20 | 8 | 4 |
| Partial final contribution | 7.5 | 0.8 | 0.2 | 10 | 7.5 | 2 |

In the first row, expiration makes 4 refundable while 1 remains earned service. In the second row, timely disclosure credits 8 to the creator; missed disclosure instead makes that 8 refundable. Funding is not itself creator payment. In the final row, the last economic price is 0.5 rather than 1; if 1 was authorized and deposited, 0.5 becomes change.

The [scenario CSV](economic_scenarios.csv) includes both successful and failed-release outcomes. Refund columns are aggregate eligible entitlements, not evidence that claims were submitted. Each scenario assumes every order authorizes and deposits the ordinary maximum, with final-order excess credited as change. Reproduce it with `python analyze_economics.py` from this directory. The calculation is research tooling and does not simulate reservation races, blockchain receipts or product correctness.

## Validation that could change the decision

Before expanding the product, show the same concrete resource and terms to at least one prospective creator, one reviewing educator and one adult sponsor or purchaser. Ask them to compare it with an ordinary open-content commission: what useful output would they fund, what rights do they need, what target/split is acceptable, and what would prevent procurement? Record rejection reasons as carefully as interest.

Keep the mechanism only if buyers value its release/accountability terms enough to accept the added process. If ordinary commissioning solves their problem better, SUNSET may still be useful as a release and receipt tool, but should not assume a public marketplace is necessary. No outreach is authorized or performed by this research.
