# MOLT and conditional community formation

**Let people commit to forming a community service only when the people, money and operators they need are also committed.**

A group may prefer its own service yet remain on a platform because each person is waiting for someone else. A new operator waits for customers. Customers wait for the operator and their friends. A sponsor waits for enough demand. Individually, every participant has a reasonable condition; together, they can remain stuck.

MOLT would represent those conditions as a single formation agreement. Participants authorize a bounded commitment. A solver proposes a coalition, and the contract checks whether the proposed allocation satisfies every included participant. The resulting community receives its agreed membership and budget together inside that contract.

Its first purpose would be launching a small community-owned digital service or shared agent worker pool. The larger ambition is to make otherwise dormant collective intentions actionable.

## Different people need different things

Consider a small group forming an independent service:

| Participant | Conditional commitment |
| --- | --- |
| A member | I will contribute up to my stated amount if six approved members and two operators join |
| Another member | I will join if the first month's budget is funded and my contribution stays below my limit |
| An operator | I will reserve my service capacity if the agreed customer demand and payment are present |
| A second operator | I will join under the same published delivery terms and my own minimum compensation |
| A sponsor | I will contribute the stated amount if the community can launch without needing further launch funding |

The important feature is the combination of separate conditions. All participants need not accept one organizer's universal funding threshold. A valid formation can depend on prospective commitments becoming effective together, even when no participant's conditions are satisfied by joining alone.

The proposed first contract would support only a small, explicit language: minimum approved members, minimum approved operators, a funded budget floor, and maximum personal contribution. These are evaluated against the same proposed coalition and allocation. Human-readable summaries should show precisely those values.

AI agents could represent members and operators under their authorized limits, compare proposals and submit acceptable commitments. They would not decide to spend outside those limits or turn ambiguous natural-language wishes directly into binding rules.

## What becomes binding

Deposits, money allocations and application membership are enforceable inside the proposed contract. Human labor, continued friendship and another website's data exports are not. An operator's bond or capacity offer does not prove that future work will be good.

Before the round closes, participants may revoke under a stated cutoff rule. After sealing, deposits are held only until a bounded activation or refund deadline. A solver's proposal names the exact commitment versions and allocations it uses. The final contract call validates them again; an outdated proposal cannot spend a changed or revoked commitment.

Within a successful activation, all ledger allocations and memberships change in one contract execution. Unused funds remain claimable by their owners. An unsuccessful round makes the deposited principal refundable; participants still bear gas and the temporary cost of tying up their funds.

Different external transfers do not become atomic just because the interface calls them a package. NEAR's cross-contract calls execute independently and can fail without undoing earlier changes. Creating a separate DAO, paying an external host or exporting from an existing platform would need explicit provisioning and recovery states. [NEAR cross-contract behavior](https://docs.near.org/smart-contracts/anatomy/crosscontract).

## What the first version would actually move

The minimum demonstration would form an application-level member registry and funded service budget. It would activate the two operators' offers and let the new members use one bounded service. The demo would establish the formation decision, balances and initial fulfillment.

It would not claim to migrate an existing social network. Importing a workspace or moving accounts requires supported exports, credentials and permission. Continuity of a separately operated agent service belongs to retained candidate LIFEBOAT and would be an optional later integration.

Approved member and operator sets are adequate for the prototype. Counting new wallets is not evidence of distinct people. A production system would need a membership policy that its community accepts.

The base formation round is public. Encrypting agent conversation would not hide public pledges, membership or payments. Confidential conditions are a possible later design with explicit output leakage and verifiability questions, not a default property.

## The demo

1. Show several participant agents with genuinely different authorized conditions and deposited budgets.
2. Try an individually acceptable-looking proposal that fails one participant's condition. Show the contract rejection and unchanged balances.
3. Produce a coalition in which all the conditions can become true together. Inspect its participant-specific allocations.
4. Withdraw or update one commitment before sealing. Try the old proposal and show that it fails.
5. Activate a current valid proposal. Show memberships, budget allocations and a real first service result.
6. Run a separate round that cannot form a viable group. Let the deadline expire and reclaim each deposit without an organizer issuing the refunds.

The mechanism's outcome is a funded group with consent-bound allocations. The outside-world question is whether enough people value the proposed service to participate at all. A solver cannot create that demand.

## Why it matters beyond a launch screen

The same form of commitment could help a small cooperative, shared infrastructure service or community purchase become viable. The hypothesis is that some worthwhile alternatives fail because reasonable commitments depend on one another. Giving those commitments an executable representation could reduce that barrier.

It does not solve every collective-action problem. It cannot produce missing operators, compensate people for every switching cost, guarantee future reliability or resolve antagonistic incentives merely by finding a group. A feasible agreement is also not necessarily a fair or optimal agreement; selection and allocation rules need to be published.

## Existing work and the proposed distinction

CollAction already organizes crowd actions and participant commitments. Snowdrift.coop explicitly develops mutual-assurance funding in which support depends on others' contributions. Assurance contracts and refund-bonus variants have a long research history. A threshold pledge page would therefore be a weak contribution. [CollAction](https://www.collaction.org/), [Snowdrift's mechanism discussion](https://wiki.snowdrift.coop/about/snowdrift-dilemma), [Tabarrok's assurance-contract paper](https://mason.gmu.edu/~atabarro/PrivateProvision.pdf).

The earlier local concept list also proposed collective purchase agents. MOLT goes further only if it demonstrates several roles, different conditions and a correctly validated common allocation. If its implementation collapses to “fund this campaign if the total reaches X,” it does not earn its proposed distinction from that earlier idea.

The local NEAR board includes Dependency Insurance, which proposes shared funding for dependency failures and replacement work, and Verdikt, which uses conditional markets around token-launch decisions. MOLT should not present general migration funding or conditional decision-making as absent from the ecosystem. Its claim must stay tied to the actual formation flow. [Dependency Insurance](https://nearbuilders.org/projects/idea/dependency-insurance-w40jzi), [Verdikt](https://nearbuilders.org/projects/idea/verdikt-2u8yhy).

## NEAR and track fit

NEAR would provide the shared escrow, commitment versions and single-contract activation. Function-call keys can restrict agent calls; the contract must enforce monetary caps because a key's allowance pays for gas rather than defining the application's spending policy. [NEAR access keys](https://docs.near.org/protocol/accounts-contracts/access-keys).

AI Swarms is the natural fit if independent agents actually represent different participants and negotiate a viable allocation. Open Innovation fits the broader collective-action experiment. Agent Economy needs real purchasing and service fulfillment. Social Money requires a useful Sputnik DAO or Trezu integration after formation; it should use their governance and treasury capabilities. A generic replacement multisig is outside the point of the track. [Official tracks](https://nearhackathon.com/HACKATHON.md).

This is the alternative to SUNSET if collective formation is the more compelling product. Before expanding it, identify one real group whose members have different, measurable launch conditions. The mechanism can be demonstrated during the hackathon; its social impact must be earned through adoption.
