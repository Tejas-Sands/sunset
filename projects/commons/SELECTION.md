# Project selection and research audit

Recommendation on 22 October 2026: COMMONS, a community-owned private statistical service starting with effective earnings for independent workers. This is a selection judgment; adoption and implementation feasibility remain to be tested.

## Alternatives considered

| Candidate | Attractive outcome | Decisive reason it was not selected |
| --- | --- | --- |
| SpendProof and general agent procurement | Automate paid work | Retired; substantial overlap with published coordination, acceptance, payment and guard infrastructure |
| Portable work-history passport | Help independent workers reuse employment evidence | Confidential parsing of an editable document does not authenticate income; credential and attestation infrastructure already exists |
| Parametric disaster or crop cover | Pay people quickly after an objective event | Depends on credible event data, capital and an operational distribution path; established deployments already exist |
| Confidential treasury autopilot | Protect treasury strategy and execute across chains | NEAR Business and confidential Intents already provide much of the foundation; an additional UI has weak differentiation |
| Agent completion receipts | Make paid work inspectable | Execution integrity does not establish work quality, and OutLayer already produces execution evidence |
| General contract replay or ABI tooling | Improve NEAR integrations | Worthwhile ecosystem work, but close to Sandbox+, Wallet Twin and Interface Commons in the collected board; no independently reproduced new failure selected |
| Generic private data marketplace | Let contributors license data | Strong prior work from Ocean, Vana and others; insufficient product focus or novelty by itself |
| COMMONS with a bounded worker benchmark | Improve collective information while limiting individual disclosure | Selected for the combination of human outcome, explicit shared-resource governance, paid agent consumption and a falsifiable release boundary |

The last two rows are deliberately separate: COMMONS is worth pursuing only if the specific worker outcome and release-control implementation distinguish it from a generic data marketplace.

## Deep research audit

A dedicated deep-research run completed after approximately twelve minutes and returned a portable gig-worker attestation recommendation. Its recommendation was not adopted. Its output contained issues that require correction before use:

- A function-call key is unnecessary for public view calls, does not turn public state private, and its allowance is a gas budget.
- A genuine TEE execution over an uploaded PDF cannot establish that the PDF was issued by a platform or remained unmodified.
- A permanent public earnings band is a disclosure, not selective private access.
- Removing access keys does not by itself make contract behavior immutable if the code retains an upgrade path.
- The report mixed primary sources, secondary summaries and unsupported competitor characterizations. Its large worker-count and adoption claims were excluded.
- It used dated OutLayer references rather than consistently checking current application documentation.

The report provided candidates and leads. Current primary documentation, the local NEAR Builders corpus, and independent mechanism analysis determine the recommendation in PROPOSAL.md. No claim is made that a research tool audited an implementation.

## Source currency corrections

Vana search snippets expose older `/docs/*` pages describing query and DataDAO infrastructure. Direct requests returned 404. The current documentation at https://docs.vana.org/ and https://docs.vana.org/applications/confidential-compute distinguishes live individual data portability from planned pooled multi-source confidential jobs. The proposal uses these current pages and treats Vana as a serious competitor. Its documentation explicitly discusses differential privacy, so the proposal makes no claim that adding DP to private pooled compute is new.

NEAR AI Cloud model-response evidence and OutLayer application-execution evidence have different scopes. The proposal uses an actual confidential statistical application for raw records and gives the explanatory LLM only released aggregates.

## Research boundaries

The local collection contains 125 native project-board records and 11 claimed catalogue records, 100 recent activity events, 16 open issues and 18 public issue replies. Activity events are not discussion transcripts. The collection is not a complete archive of past hackathon winners. No private community messages were obtained.

No user interviews, pilot agreements, product implementation, private API calls, live paid compute executions or mainnet transactions were performed for this recommendation. The preparation consists of research and a scoped proposal; product code belongs in the development window.
