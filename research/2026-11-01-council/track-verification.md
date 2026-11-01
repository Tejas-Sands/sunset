# Track verification: NEAR HACKATHON, 1 November 2026

> Historical initial-scope assessment. The subsequent [tokenization review](../2026-11-01-tokenization/RESEARCH.md) adds an implemented NEP-171 stewardship capability and a conditional NFT-track case. Entries below describe the earlier design, not the final feature set.

**Council seat:** independent event and track evidence review. **Checked:** 2026-11-01, approximately 04:23 UTC. This report changes no product code. Track-fit conclusions are reviewer judgments, not organizer approval or claims of completed implementation.

## Event and changed rules

The event in the existing research is the **2026 NEAR HACKATHON at nearhackathon.com**, not a similarly named 2025 event. The live homepage and organizer-linked `nearai/near-hackathon-prompt-examples` repository agree on the year, November dates and thirteen tracks. [Event](https://nearhackathon.com/), [organizer-linked repository](https://github.com/nearai/near-hackathon-prompt-examples).

| Milestone | UTC | Asia/Kolkata |
| --- | --- | --- |
| Event/submissions open | 1 Nov 2026, 00:00 | 1 Nov, 05:30 |
| Development/submissions close | 14 Nov 2026, 23:59 | 15 Nov, 05:29 |
| Judging starts | 16 Nov 2026, 00:00 | 16 Nov, 05:30 |
| Results due | 18 Nov 2026, 23:59 | 19 Nov, 05:29 |

The live [HACKATHON.md](https://nearhackathon.com/HACKATHON.md) now settles several questions that the October 22 research correctly left unresolved:

- **Q-001:** work since the October 19 announcement counts. Earlier commits are baseline. Waiting until November 1 is no longer necessary for eligibility.
- **Q-002–005:** existing repositories, templates, libraries and new integrations are allowed; identify the baseline and judged diff in the README.
- **Q-010–011:** testnet-only projects qualify across all tracks. No named integration is mandatory; a fitting native NEAR contract can suffice. Intents has no testnet, so it does not belong in a zero-spend testnet implementation merely to collect a track.
- **Q-012–017:** a reproducible local demo qualifies, but needs video if judges cannot open it. Add a license and keep the repository public through judging. Each person can enter at most two independent, mutually disclosed projects. AI screening informs human judges.

The [homepage FAQ](https://nearhackathon.com/#apply) explicitly allows selecting every fitting track in one submission. The event lists ecosystem partners, but these are not thirteen separate sponsor integration bounties. No published scoring bonus for the number of selected tracks was found. No guarantee that one project can collect multiple track prizes was found; eligibility to select multiple tracks does not establish prize stacking.

## Submission constraints

Public repository plus human-published public X demo are required. The post must identify the event, tag `@NEARProtocol` and `#NEARHackathon`, and attach video/screenshots. Local-only demos require video. The final form also needs real team/contact details, a mainnet NEAR payout account, description and consent. Testnet product deployment does not change the payout-account requirement. [Submission instructions](https://nearhackathon.com/HACKATHON.md).

One repository/project gets one submission, which cannot be edited. Prepare the exact JSON for human confirmation; preserve one request ID across transient retries. Do not submit drafts or test the API by sending placeholders. The rules specifically reserve publication, pushing, signing/deployment and final submission for explicit human confirmation. Recheck these live instructions before those actions. [Submission API and human decisions](https://nearhackathon.com/HACKATHON.md).

## SUNSET: confirmed concepts versus provisional track claims

At review time the maintained SUNSET files describe an **unimplemented plan**: adult-funded educational packs, capped creator buyout, independently verifiable release/refund, finite access-service grants and wallet-free offline learning. The following ratings apply to that plan, not working evidence. [Maintained design](../../projects/sunset/README.md), [contract specification](../../projects/sunset/CONTRACT.md).

| Track/API ID | Judgment for existing design | Evidence needed before selecting it |
| --- | --- | --- |
| **Open Innovation / `open`** | Strong conceptual core fit. Finite paid access becoming a verified public resource is coherent ownership/money experimentation. | Demonstrate capped funding, usable public release from an independent client, and failed-release refunds. [Official prompt](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/tracks/13-open.md). |
| **Social Money / `social`** | Strong core target. Collective buyout plus finite shared access budgets directly express community coordination. Sputnik/Trezu are optional under Q-011; the October research treating them as necessary is too strict now. | Several named contributors fund the same release; approved service spending stays inside a separate cap; unused funds return to the sponsor. Do not claim legal collective copyright ownership merely because funding is collective. [Official prompt](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/tracks/12-social.md). |
| **Real-World Money / `realworld`** | Natural adjacent target, conditional on a usable merchant payment workflow. This is a prototype for ordinary creator/service payments, not evidence of an existing business. | Adult-facing line items/invoice or order, explicit split, verified pending/accepted/paid/refunded states, provider withdrawal and CSV receipts. Stablecoins/Intents are optional; label native testnet NEAR honestly. [Official prompt](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/tracks/08-realworld.md). |
| **AI Security & Defense / `security`** | Provisional extension. Existing caps and scoped release keys provide useful foundations, but a release job alone is not an AI spending-defense product. | Demonstrate an actual autonomous buyer/seller constrained by contract-enforced budgets, methods, counterparties and expiry. Show malicious/overspend actions rejected despite agent requests; distinguish access-key gas allowance from economic spending cap. [Official prompt](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/tracks/06-security.md). |
| **Agent Economy / `agents`** | Provisional extension. Needs a participant that actually earns/spends/purchases, not labels applied to adult wallet buttons. | An institution's buyer agent compares packs/provider offers, makes a consequential decision inside a budget, obtains verified work and settles/refunds with traceable receipts. Clearly disclose deterministic policy agents versus LLM agents. [Official prompt](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/tracks/07-agents.md). |
| **AI Swarms / `swarms`** | Provisional but coherent extension of collective buying. | Independently budgeted buyer and seller agents coordinate a round, select/allocate a pack or service, and perform actual testnet settlement. Separate identities and refusal/cap-exhaustion behavior matter. The official example explicitly supports scripted strategies without LLM calls, so paid inference is unnecessary for its demonstration. [Official prompt](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/tracks/05-swarms.md). |
| **Autonomous Business / `business`** | Stretch after the agent market works. Human-reviewed content alone does not constitute an AI-native business. | One seller performs a complete autonomous sale/delivery/revenue-allocation/service-procurement loop within human-set rules; show a real task decision and costs/revenue. If only deterministic automation is shipped, disclose that and assess conservatively against the AI-native theme. [Official prompt](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/tracks/04-business.md). |
| **Privacy & Private AI / `privacy`** | Weak for current scope. Wallet-free learning, local progress and encrypted pre-release packs are sound product decisions, but currently no confidential intelligence workflow is delivered. | A distinct confidential application with a demonstrated privacy boundary would be needed. Ordinary server encryption is not TEE attestation; an offline privacy claim should be verified by network inspection. Avoid adding sensitive learner data merely to claim this track. [Official prompt](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/tracks/03-privacy.md). |
| **Games With Real Economies / `games`** | Weak for the current maths quiz. Buying access outside play does not make economics part of the game loop. | Meaningful player allocation/trade and reactive NPC/market behavior inside a playable loop, with observable consequences. Offline learning is valuable independently. [Official prompt](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/tracks/09-games.md). |
| **Unstoppable DeFi / `defi`** | No current fit. An escrow is not automatically a trading/lending protocol. | Would require a separate exchange, lending, vault or related financial market mechanism. [Official prompt](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/tracks/01-defi.md). |
| **Investment Thesis / `thesis`** | No current fit. Public buyout analytics do not constitute an investment thesis for NEAR. | Reproducible data-backed investment research would be a different deliverable. [Official prompt](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/tracks/02-thesis.md). |
| **NFTs That Do Something / `nfts`** | No current fit. Access agreements need no NFT. | A meaningful tokenized credential/account with behavior, not decorative minting. [Official prompt](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/tracks/10-nfts.md). |
| **Memecoins With Mechanics / `memecoins`** | No current fit. | A real meme/community token mechanism would alter the product rather than strengthen its core. [Official prompt](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/tracks/11-memecoins.md). |

## Recommended track breadth

Build one coherent product in layers:

1. **Release/refund plus finite community budgets:** target `open`, `social`.
2. **Complete creator/service commerce:** add `realworld` when its receipts and recovery flow work.
3. **Bounded collective procurement agents:** use the same packs, offers, budgets and contract settlement to earn `security`, `agents`, `swarms`, conditional on the demonstrations above.
4. **Autonomous seller loop:** consider `business` only if it actually runs. Do not sacrifice the core release, refund or independent offline proof to reach seven selections.

This yields **three natural targets and three closely related extensions**, with a seventh stretch. It is broader and more defensible than attaching NFTs, a memecoin, an investment dashboard or superficial AI calls. The number entered must be determined by evidence at submission time, not this forecast.

## Source quality and alternatives

The official homepage was fetched with the web tool. Its markdown endpoint returned unsupported content type there, so the full live instructions were independently retrieved read-only with `curl`: 19,923 bytes, SHA-256 `8482c2cae1a4148a9cdb747700516685f10d7e110ac76db8a1b1db3d3f617d90`. This hash identifies the reviewed revision, not an enduring rule guarantee. Official track examples were read on the linked `nearai` GitHub repository. They are examples rather than mandatory product specifications, as the event instructions explicitly say.

The linked October 19 X announcement could not be retrieved directly (403), so no direct verification of its contents is claimed. The live event instructions supply the announcement date and permitted development window. Search also returned event aggregators and an X mirror; none was used to override official rules. No organizers were contacted and no transactions or submissions were sent.

If the user means another NEAR event, retain SUNSET's release/refund core but replace this matrix with that event's primary rules before asserting eligibility. Older Devpost hackathons, partner marketing pages and dated search summaries do not establish this event's tracks. At present, the dates and thirteen-track list match the repository's intended event, so changing events or products is unnecessary.
