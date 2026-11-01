# NEAR Builders findings for project selection

SpendProof should remain retired. The board already contains agent distribution, managed service coordination, escrow, permission controls, task proofs, and reputation proposals. A combination of those features needs a much stronger user problem and a demonstration that distinguishes its contribution.

This is a comparison of published entries and public issue conversations. It establishes what people have proposed and requested; it does not independently establish adoption, implementation quality, or hackathon prize prospects.

## Repeated project directions

| Direction | Examples in the collected board | Implication for our choice |
| --- | --- | --- |
| Agent distribution and coordination | [AgentMarket](https://nearbuilders.org/projects/idea/agentmarket-8hk87b), [managed social coordination](https://nearbuilders.org/projects/scope/scope-agentic-social-coordination-service-8vmgku) | A service that hires agents needs a specific unsolved job beyond discovery and payment. |
| Agent identity and reputation | [Agentic Identity scope](https://nearbuilders.org/projects/scope/agentic-identity-identyclaw-passport-rich-online-digital-tokens-o7o5ga), [B7systems](https://nearbuilders.org/projects/scope/b7systems-staking-based-reputation-layer-for-ai-agents-225ow2), [AgentBond](https://nearbuilders.org/projects/idea/agentbond-ep3r8x) | Passports, staking, ratings, and accountability are already common proposal themes. |
| Wallet explanations and transaction guards | [Wallet Health](https://nearbuilders.org/projects/idea/near-wallet-health-an-ironclaw-skill-that-audits-your-wallet-before-something-goes-wrong-jsc6kb), [Smart Transaction Guard](https://nearbuilders.org/projects/idea/near-smart-transaction-guard-upzzyk), [ContractLens](https://nearbuilders.org/projects/idea/contractlens-ai-smart-contract-explainer-for-near-hysf28) | A chat interface and risk score would have little distinctiveness here. |
| Simulation and developer tools | [Wallet Twin](https://nearbuilders.org/projects/idea/wallet-twin-sandbox-self-6wqa6g), [Sandbox+](https://nearbuilders.org/projects/idea/sandbox-for-near-agentic-web-multi-chain-agentic-sandbox-devex-diagnostic-toolkit-9i1ck9), [Interface Commons](https://nearbuilders.org/projects/idea/near-interface-commons-a-shared-abi-registry-for-the-contracts-that-ship-without-one-3t22ei) | An all-purpose testing dashboard is also an existing idea. A tool needs one reproducible failure it resolves. |
| Escrow and business payments | [Deal Settler](https://nearbuilders.org/projects/idea/deal-settler-cex-style-p2p-escrow-for-real-world-agreements-nlmkfj), Numpay, ZendPay, [Trezu](https://nearcatalog.xyz/project/trezu) | Payment rails and release controls need a distinct workflow, user, or economic mechanism. |

The comparison file [competitor-overlap.csv](competitor-overlap.csv) links additional neighboring entries. Repeated ideas are evidence of a crowded proposal space, not proof that the underlying needs have been solved.

## Useful signals in specific proposals

**Interface Commons describes a concrete integration failure.** Its author reports a sample of widely used contracts without embedded interfaces and links an existing recovery prototype. The useful pattern is a named consumer, a reproducible input problem, explicit evidence levels, and a limited integration target. The author's sample and prototype still require independent verification. Building the same registry would duplicate the published idea.

**VRX describes a specific business operation.** Its proposal concerns multiple parties reserving the same unique inventory and claims use inside an existing property business. The distinction is the operational conflict and who experiences it. The business history and running testnet usage are author claims, not verified customers in this collection.

**Backstop and AgentBond show interest in recourse after failure.** They also depend on difficult assumptions: evidence, dispute rules, collateral, and the ability to pay compensation. A compelling compensation diagram is not a working protection system. An entry in this area would need a precisely defined event and funded demonstration.

**B7systems exposes the hard part of reputation.** The scope asks for reviews tied to completed tasks, duplicate-review prevention, and limits on self-dealing. A wallet address or attestation alone does not establish an independent person or a truthful outcome. Reusing a reputation label would not resolve those constraints.

## What people are actually discussing

The public issue conversations show practical product needs:

- **Getting started:** a single signup route and current building resources. A maintainer explicitly pushed the scope away from hackathon submissions and toward general builder onboarding. [Issue 271](https://github.com/NEARBuilders/nearbuilders.org/issues/271)
- **Reliable feedback workflows:** recruit testers, use the project's existing issue tracker, select meaningful contributions, and show credit. A related request connects project pages directly to feedback rounds. [Issue 221](https://github.com/NEARBuilders/nearbuilders.org/issues/221), [issue 235](https://github.com/NEARBuilders/nearbuilders.org/issues/235)
- **Identity and visibility controls:** changing a linked wallet and keeping an unlisted project out of public directory results. [Issue 75](https://github.com/NEARBuilders/nearbuilders.org/issues/75), [issue 254](https://github.com/NEARBuilders/nearbuilders.org/issues/254)
- **Completing ordinary user flows:** decisions reaching users by email, readable activity categories, explicit language selection, and pages that expose their content to readers and indexing tools. [Issue 267](https://github.com/NEARBuilders/nearbuilders.org/issues/267), [issue 177](https://github.com/NEARBuilders/nearbuilders.org/issues/177), [issue 188](https://github.com/NEARBuilders/nearbuilders.org/issues/188), [issue 122](https://github.com/NEARBuilders/nearbuilders.org/issues/122)

These conversations are useful evidence about this platform's users. They are not a representative poll of the whole NEAR ecosystem. Most of the 18 replies concern implementation ownership; they should not be counted as independent demand endorsements.

## Standard for the replacement project

The next candidate should identify one user with a recurring problem, its closest existing alternatives in this corpus, and a result those alternatives do not already demonstrate. Its first technical probe should reproduce that problem using real data or contract state. A three-minute demonstration should show the result clearly, including a failure that the implementation handles.

NEAR should supply an essential part of the result: for example, enforceable shared state, a particular asynchronous contract behavior, confidential computation with verifiable evidence, or a genuinely cross-chain economic operation. A NEAR transfer added to a generic application is insufficient differentiation for this brief.

Track coverage follows that core contribution. No replacement project or track count is approved by this research alone. The immediate research queue is to inspect the linked prototypes and unresolved issues behind promising entries, then reject candidates whose novelty disappears on that closer comparison. The collected JSON and source links make that comparison concrete.
