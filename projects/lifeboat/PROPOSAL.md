# LIFEBOAT portable operation for paid agent services

Research candidate dated 22 October 2026. The first question is whether a narrow NEAR implementation offers a useful advantage over established recovery tools. No product implementation is claimed.

**An owner should be able to replace the operator of a paid agent service without replacing its identity, abandoning its customer jobs or giving the old operator continuing access to its money.**

## The first user and failure

A small developer runs an agent that sells one kind of report. Customers prepay the service. The service has accepted jobs, unfinished work and revenue when the hosting process fails or the operator must be replaced.

A restart is one problem. Changing who is allowed to act for the business is another. A replacement needs the service's work state and clear authority over future effects. The old process may later come back online with stale instructions. Both cannot be allowed to charge or release funds for the same work.

The first product would provide an owner-controlled service record and a handover operation. Customers identify the service by its NEAR account or contract ID; their payment and job records do not belong solely to the hosting platform's database.

## Proposed mechanism

One NEAR contract maintains the owner, the service's active operator and execution generation, accepted job IDs, reserved customer credit, and financial operation outcomes. A new operation carries its job ID, operation ID, current generation and exact monetary fields. The contract checks them where the effect is admitted.

An owner-authorized handover advances the generation and names the replacement. Previously unseen financial actions from the old generation are refused. The new operator resumes using the durable job record and any authorized checkpoint.

An operation accepted before handover remains an operation that must be reconciled. A late callback cannot be ignored merely because its generation is old. The new operator must inspect that operation's outcome before attempting the same effect again. Unknown outcomes remain unresolved; handover does not make them safe to repeat.

The guarantee is deliberately limited to effects admitted by the controlling contract. A payment already accepted on another chain, an email already sent, or an API credential copied by a former operator cannot be undone by changing a NEAR field. NEAR cross-contract calls are asynchronous and have independent failure outcomes; callback and reservation handling are part of the core design. [NEAR cross-contract behavior](https://docs.near.org/smart-contracts/anatomy/crosscontract).

## Why NEAR belongs in it

NEAR would hold service ownership, current authority and the financial journal that both operators must obey. A restricted operator key calls the service's limited methods; monetary limits live in contract logic. A replacement does not require the previous hosting platform to edit its private database.

Confidential checkpoint storage and key recovery could use existing infrastructure when its deployment and trust assumptions fit. They are separate from proving correct job recovery. The public demonstration should contain synthetic, non-sensitive jobs until checkpoint confidentiality is implemented and inspected.

## Existing work and proposed contribution

Temporal already preserves execution history and demonstrates an agent resuming after a crash. Ordinary process restart is therefore not a novel contribution. [Temporal's agent-state example](https://docs.temporal.io/ai/featured/memory-state-stripe).

OutLayer already documents sovereign vault takeover and separately documents leased agent accounts with on-chain grants. LIFEBOAT must reuse or complement these mechanisms rather than claim to invent recoverable keys or account leasing. [OutLayer vaults](https://app.outlayer.ai/docs/vaults), [Agent Connect](https://app.outlayer.ai/docs/agent-connect).

Agentplat describes checkpoint takeover and authority fencing. Those ideas also have prior work beyond NEAR. Its documentation is evidence of overlap, not a benchmark we have run. [Agentplat](https://github.com/Agentplat/agentplat).

The proposed contribution is a small, inspectable implementation of **owner-directed service handover with monetary effect fencing on NEAR**, packaged around one paid agent service. It is worthwhile only if that integration makes a real owner's exit or operator replacement easier than existing tools do.

## The decisive demonstration

1. A customer prepays one synthetic report job through the service contract.
2. Operator A records progress and begins a financial operation. The demonstration tracks whether the operation was accepted before stopping A.
3. The owner authorizes B. The contract advances the generation while preserving pending operations.
4. B resumes and reconciles the existing operation rather than charging again.
5. A returns and attempts a new financial action using its old authority. The contract rejects it.
6. Display the service ID, actual generation change, job record, receipts and customer-credit history.

Two processes on one computer demonstrate the authority rule and crash path, not tolerance of an entire datacenter outage or organizational independence. A second independently operated host is a later validation step.

## Hackathon boundary

The first version would handle one paid service, two operator processes, owner-authorized handover and native NEAR financial effects. No automatic seizure of an operator's role, universal export of third-party credentials, cross-chain exactly-once claim or censorship-resistance guarantee is needed.

AI Security and Defense is the strongest track if the stale-operator attempt is demonstrably blocked. Agent Economy fits if a real agent buys or sells the service. Autonomous Business is conditional on the service actually operating under defined constraints. Privacy requires an actual confidential checkpoint path; merely encrypting a file is insufficient evidence of the entire system's privacy.

The first development probe should implement the authority transition and an accepted-but-unacknowledged operation in a controlled environment. Stop if stale authority still works at the monetary boundary, or if the design merely duplicates an existing OutLayer operation without adding service continuity.

The longer-term product could help developers operate services without binding ownership and job state to one host. The business hypothesis is a paid recovery/integration service or managed operator network. Demand and willingness to pay remain unvalidated.
