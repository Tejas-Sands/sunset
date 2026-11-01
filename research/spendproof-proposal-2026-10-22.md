# SpendProof hackathon project proposal

**Status: Retired on October 22, 2026 after the user rejected this direction as too generic.** This proposal is historical. The current work is [NEAR Builders project and community research](nearbuilders/2026-10-22/README.md); do not use this document as the active implementation brief.

SpendProof helps a small team buy a useful digital service through agents while retaining control over its budget. A buyer agent compares supplier bids, checks the delivered artifact against agreed rules, and initiates payment. A guard enforces spending authority and records the resulting payment evidence.

The goal is one strong demonstration with broad track coverage. The working scope targets four core tracks and three conditional additions. These are proposed fits; each entry depends on the finished implementation. SpendProof is a working name whose availability has not been checked.

## Project choice

| Approach | Expected coverage | Tradeoff |
| --- | --- | --- |
| SpendProof procurement workflow | Four core tracks and up to three additions | Best fit for the requested breadth; payment state is the main engineering challenge. |
| Invoice Authorization Gate | Two tracks and a possible third | Smaller scope and a clear attack demonstration; less agent coordination. |
| Last Caravan economic game | Two tracks and a possible third | A visible game economy; game design and presentation compete with payment work for time. |

These comparisons are planning judgments based on the existing [24-concept research list](near-hackathon-master-list-2026-10-21.csv), particularly Paid-Agent Quality Broker, Private Supplier Procurement, Atomic Fleet Budget, and Invoice Authorization Gate. They are not estimates of prize odds.

## User and first useful job

The initial user is an operations lead at a small team buying catalog normalization. They provide a messy catalog, required output columns, acceptance rules, a supplier allowlist, and a spending limit. The first output is one cleaned CSV with a record of its acceptance and payment.

The demonstration uses synthetic catalog data and three team-operated supplier agents with separate prices, capabilities, and failure modes. Each supplier independently decides whether to bid and produces a deliverable when hired. The interface identifies these as demonstration suppliers.

## Core workflow

1. The owner sets the budget, allowed suppliers, job requirements, and payment authority.
2. The buyer requests competing offers and compares price with the required output.
3. A reservation holds the selected job's budget before work starts. Other jobs cannot spend that reserved amount. Rejecting or cancelling work can release a reservation only when no payout has started.
4. The hired supplier produces a CSV. Deterministic checks test its schema, expected record identifiers, duplicate constraints, and specified normalization rules. Model commentary cannot override these checks.
5. The payment guard checks the job ID, accepted artifact digest, authorized recipient, asset, amount, and quote expiry before initiating payment.
6. The application reconciles the transaction and relevant receipts. An unresolved outcome stays pending; retrying the same job cannot initiate another payout.

The owner authorizes the policy before execution. Jobs that satisfy it can complete without a fresh approval at every step. Policy changes require the owner's authority.

## Track evidence

| Track | Priority | Evidence to build |
| --- | --- | --- |
| Autonomous Business | Core | A useful procurement job completes under an owner-defined policy. |
| AI Swarms | Core | Independently operating suppliers submit competing offers and deliver the selected work. |
| Agent Economy | Core | A supplier agent earns a payment for an accepted artifact. |
| AI Security & Defense | Core | Changed recipients, duplicate payouts, and concurrent overspending fail at the payment boundary. |
| Real-World Money | First addition | A supplier invoice is bound to the job and reconciled with the actual payment. |
| Privacy & Private AI | Conditional | Sensitive brief processing uses verified private inference, limited supplier views, and reviewed application storage and logging. |
| Social Money | Conditional | A real Sputnik DAO or Trezu workflow authorizes a shared budget used by the procurement flow. |

The accompanying [13-track matrix](spendproof-track-matrix-2026-10-22.csv) records the evidence required for every track, including deferred possibilities. The event permits selecting multiple relevant tracks in one submission. [Official event FAQ](https://nearhackathon.com/)

## Proposed technical boundary

Use one application, one buyer coordinator, three separately running supplier workers, one payment asset, and one NEAR network for the core demonstration. A small TypeScript web application with a durable job ledger is the preferred starting point; its final framework can be selected during implementation planning.

NEAR testnet is the proposed environment for the first payment demonstration. The payment guard must own the demonstration funds and atomically track reserved and settled amounts across every job using the same budget. Agent credentials must not provide an alternative path to withdraw those funds. The budget invariant is `reserved + settled <= budget_limit`; network fees and storage funding are tracked separately.

A function-call key can restrict contract methods, but its allowance budgets gas rather than supplier spending. The contract must enforce the economic rules. [NEAR access key documentation](https://docs.near.org/protocol/accounts-contracts/access-keys)

Supplier code and model output are untrusted. The acceptance verifier is trusted to attest that the specified artifact checks passed; the owner and verifier authorities must be shown in the demo documentation. Structural checks do not establish the truth of arbitrary research or the quality of every possible service.

Payment state must distinguish reserved, cancelled, pending, paid, and confirmed failed outcomes. Once a payout starts, only a confirmed failure releases its reservation for another attempt. Delayed or missing transaction status cannot trigger a new payment. Recovery must query the existing attempt and inspect contract state. A restart resumes from the durable ledger.

## Why this is worth building

Agent Market already supports jobs, bidding, held payments, acceptance, and disputes. A generic marketplace would duplicate that work. SpendProof's proposed value is the link between objective acceptance, an enforceable budget shared across jobs, and recovery evidence. An Agent Market adapter is optional after the native demonstration works. [Agent Market documentation](https://docs.market.near.ai/)

OutLayer explicitly documents that concurrent requests can exceed cumulative spending limits because they can observe the same usage counter. Its per-transaction limits and other policies have different guarantees. SpendProof should demonstrate its own reservation invariant rather than claim existing wallet limits solve it. [OutLayer custody documentation](https://app.outlayer.ai/docs/agent-custody)

For privacy, a gateway signature and a model-serving TEE signature provide different evidence. The privacy addition requires verified preflight evidence, a matching response signature where required, and a specific explanation of which data is protected. Public receipts must not contain confidential briefs or unsalted hashes of guessable sensitive values. [NEAR AI response verification](https://docs.near.ai/cloud/verification/cloud-api/response-signatures), [model attestations](https://docs.near.ai/cloud/verification/cloud-api/model-attestations)

## Demonstration and acceptance

The primary demonstration should take roughly three minutes. Show three bids, reject an artifact that violates the agreed rules, accept a compliant alternative, and show one payment with its receipt. Replay that job and show no second payout. Then run a separate concurrency scenario: three accepted jobs each request 4 test NEAR against a shared 10 test NEAR allocation; at most two payouts can start.

| Check | Passing evidence |
| --- | --- |
| Invalid artifact | Deterministic failure prevents authorization and payout. |
| Recipient or amount mutation | Execution rejects the changed values. |
| Shared budget | Concurrent reservations never make reserved plus settled exceed the allocation. |
| Duplicate request | The original job and payment attempt are reused without a second payout. |
| Failed transfer | Reconciliation confirms failure before releasing or reusing the reservation. |
| Interrupted application | A restart resumes the existing payment attempt. |
| Successful job | The artifact, acceptance decision, reservation, and final receipt are linked. |

The user interface should show the budget, supplier offers, job state, and payment evidence in one flow. Labels must distinguish simulation, testnet execution, recorded evidence, and any live mainnet operation.

## Scope order

First establish the budget and recovery invariant. Then complete one useful supplier job and its payment. Add the other suppliers and the comparison interface after that flow works. Invoice reconciliation is the first additional track because it reuses the same job and payment record.

Investigate privacy and DAO funding as separate additions after the core is demonstrable. Set November 7 as the decision point for these additions and November 10 as the point to stop adding features. These are proposed internal dates, not event requirements.

An NFT is deferred unless service ownership or transferable credits become a useful part of this flow. DeFi requires a genuine exchange, vault, lending, or trading behavior with settlement evidence; converting an invoice payment does not automatically establish that fit. A game, memecoin, or investment thesis would require a separate product purpose. Open Innovation needs a specific contribution beyond the already-matching categories.

## Event timing and delivery

The published development window opens November 1, 2026 at 00:00 UTC and closes November 14 at 23:59 UTC. In India, those are November 1 at 05:30 IST and November 15 at 05:29 IST. This October 22 proposal is preparation; early implementation remains subject to organizer clarification.

The final submission needs a public repository and a public X demo post, with one submission per team. Track claims should be checked against the finished evidence before submission. [Event website](https://nearhackathon.com/), [participant guide](https://nearhackathon.com/HACKATHON.md)

The guide requires the human to publish the demo and confirm the exact final submission payload. Publishing the repository, mainnet operations, and submission remain separate actions. NEAR Intents-dependent OutLayer endpoints require mainnet; the native testnet workflow avoids making those endpoints a prerequisite for the core demonstration. [OutLayer network support](https://app.outlayer.ai/docs/agent-custody)

The next design decision is whether to accept this single-service procurement scope. A detailed implementation plan follows review of the design; product scaffolding and implementation are outside this preparatory artifact.
