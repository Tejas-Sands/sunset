# CLEARLOOP net settlement for consenting counterparties

Research candidate dated 22 October 2026. Strong economic mechanism, substantial existing competition. No product implementation, legal debt discharge or customer adoption is claimed.

**Let a group settle mutually accepted obligations by moving only the net amount.** The first NEAR product would apply this to one asset and one controlled service ledger.

## The simple example

Suppose three businesses or paid agents have accepted these obligations:

| Obligation | Amount |
| --- | ---: |
| A owes B | 100 |
| B owes C | 80 |
| C owes A | 70 |
| Total gross transfers | 250 |

Their net positions are A paying 30, B receiving 20 and C receiving 10. If all parties agree to the netting arrangement, transfers totaling 250 can be replaced by transfers totaling 30. These are illustrative units, not measured dollar savings.

Gross transfer volume is not the same as minimum required liquidity: money may be reused in sequential gross settlement. We should compare actual collateral requirements, timing, fees and exposure under a defined baseline rather than label 220 units of lower transfer volume as newly created cash.

## The first product

Three or more known participants register mutually accepted obligations under a common settlement agreement. A clearing round proposes net positions. Each participant approves its exact position and the obligation-set hash.

A payer funds the residual. Within one contract's internal ledger, a successful clearing round consumes the approved obligations and updates participant balances together. An underfunded or mismatched round leaves the obligations outstanding. Withdrawals are later asynchronous transfers and need their own accounting and failure handling.

One contract's bookkeeping does not make multiple external transfers or multiple chains atomic. Likewise, an API response saying paid does not discharge an external legal invoice. The initial demonstration deals only with obligations explicitly accepted inside this protocol.

## NEAR responsibility

The contract would bind bilateral consent, the exact clearing set, current obligation versions, deposits and settlement outcomes. Agent clients could propose rounds and compare the netted result against paying each accepted obligation separately.

NEAR Intents could later fund or withdraw a residual in another supported asset or chain. That is a routing integration with asynchronous external outcomes, not a promise of atomic multi-chain netting. A first version can run on testnet with one native asset and public synthetic records.

An LLM can help classify or explain records, but deterministic arithmetic and participant approvals govern settlement. AI invoice extraction is unnecessary for the core mechanism.

## Strong prior work

Cycles already proposes and builds privacy-preserving clearing for financial and business flows. Its published product direction is a close competitor, not just an adjacent swap interface. [Cycles architecture and products](https://cycles.money/blog/cycles-raises-8-7-million).

Ophir's agent protocol describes a clearinghouse with multilateral netting, so applying netting to agents is not itself new. Its published claims and code need separate implementation review before we infer maturity. [Ophir](https://github.com/Ophir-Protocol/ophir).

AtomicNet demonstrates the same broad intercompany-netting idea on Canton and documents prototype limitations. Porting its user story to NEAR would not establish originality. [AtomicNet](https://github.com/OoJae/AtomicNet).

The hypothesis worth testing is narrower: a NEAR-native integration for a real group whose accepted service obligations can be cleared more simply than existing alternatives permit. We have not yet established that customer or integration gap.

## A demonstration worth inspecting

1. Show the three obligations and every party's approval.
2. Propose the illustrative 30-unit settlement and inspect its exact obligation-set hash.
3. Change an obligation after approval. The proposal must become invalid.
4. Attempt settlement without enough residual funding. No obligation disappears.
5. Fund it, settle, and reconcile all balances and outstanding obligations.
6. Repeat the same settlement ID. It must not create another credit or consume unrelated obligations.

The most useful visual is the obligation graph changing to the net-payment graph, accompanied by actual ledger state. Any performance or liquidity improvement needs a named baseline and an observable measurement.

## Scope and selection judgment

A two-week prototype could plausibly handle one asset, a small participant roster, mutually signed obligations, approval-bound net positions and one-contract settlement. Confidential records, production credit, regulated business invoicing, multiple chains and default-loss allocation are separate work.

Agent Economy is credible when agents actually transact through it. AI Swarms needs genuine economic coordination between agents; three wallets alone do not qualify. Unstoppable DeFi needs the corresponding financial integration and evidence. Real-World Money requires a credible business-payment use case rather than a synthetic graph labelled real-world.

This remains behind LIFEBOAT for the next investigation because its overlap is particularly direct. Promote it only after finding a specific underserved NEAR use case and a measurable advantage. A large theoretical market does not fill that gap.
