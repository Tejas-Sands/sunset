# Continued project search on 22 October 2026

COMMONS is retained as a [main project candidate](../../projects/commons/README.md). This round tests its assumptions and checks other directions. No additional project is promoted to main-candidate status.

## Direct precedents for COMMONS

**Worker-owned earnings analytics already exist as a product direction.** Rockefeller's 21 June 2023 account of Driver's Seat describes earnings tracking, cooperative membership and member eligibility for profit sharing. This is historical evidence of substantial product overlap; it does not establish current availability. [Funder's account](https://www.rockefellerfoundation.org/grantee-impact-stories/drivers-seat-puts-data-and-power-in-gig-workers-hands/).

Princeton's Workers' Algorithm Observatory now identifies Driver's Seat as sunsetted and FairFare as carrying the mission forward. FairFare pools fare records for analysis. These are closer comparisons than a generic blockchain data marketplace. A shutdown does not make the original concept novel again. [Current WAO project descriptions](https://wao.cs.princeton.edu/).

Worker Info Exchange also asks workers to request platform data for collective research into dynamic pay, sharing analysis with workers and their unions. This supports the existence of organized demand while raising the question of why a community would adopt another service. [Research programme](https://www.workerinfoexchange.org/dynamic-pay-research).

**Decision:** Keep COMMONS provisional. Its case must rest on a demonstrated privacy/control advantage and a particular underserved community. A worker benchmark plus a DAO is insufficient differentiation. These organizations are precedents and possible future research contacts, not partners; nobody was contacted.

## OpenDP compatibility needs deeper scrutiny

Source inspection at commit `367461d557a8a477558cb3853ff7e7501537b1c8` found OpenSSL in the default features. The random-byte implementation selects OpenSSL private random bytes when enabled; its fallback is labelled “Non-securely fill a byte buffer with random bits.” Removing defaults to ease compilation is therefore not an acceptable shortcut without a separately justified randomness implementation. [Dependency features](https://github.com/opendp/opendp/blob/367461d557a8a477558cb3853ff7e7501537b1c8/rust/Cargo.toml), [sampler source](https://github.com/opendp/opendp/blob/367461d557a8a477558cb3853ff7e7501537b1c8/rust/src/traits/samplers/mod.rs).

This is source inspection, not a compilation failure. No build was attempted. It does not prove WASI is impossible; it establishes a concrete integration question. Secure randomness alone also does not solve repeated-release attacks.

**Decision:** The confidential-runtime and release-construction feasibility gate remains central. Do not mark the prototype technically validated from documentation alone.

## Other directions checked

**Humanitarian coordination:** WFP already documents Building Blocks for coordination between aid organizations while protecting personal information. A general blockchain aid-deduplication proposal would duplicate a mature direction and still need institutional access. No new unmet use case was established. [WFP innovation overview](https://www.wfp.org/innovation).

**Recovery tooling:** The official NEAR Recovery Registry repository already describes hidden recovery-key commitments. Its README states a dependency on protocol 2.14 and testnet-first deployment. Repository availability is not evidence that the required production features are live, or that a registry entry can recover assets on every external chain. An additional recovery UI is not yet a differentiated main candidate. [Official repository](https://github.com/near/recovery).

**NEAR developer infrastructure:** Four issues referenced by the earlier Sandbox+ proposal were checked through GitHub's public API:

| Issue | Current state at collection | Research consequence |
| --- | --- | --- |
| [32](https://github.com/near/devex/issues/32) transaction-status waiting | Closed, last updated 14 September 2026 | Do not repeat it as a missing capability |
| [34](https://github.com/near/devex/issues/34) slow sandbox fast-forward | Open | A reported problem; current performance still needs reproduction |
| [36](https://github.com/near/devex/issues/36) pause sandbox blocks | Open | Could require changes below a normal application integration |
| [44](https://github.com/near/devex/issues/44) ABI schema tooling | Open | A concrete interoperability report, but adjacent to existing ABI proposals |

Issue state is verified; the reported failures were not independently reproduced. None alone establishes a new project with worldwide impact. [Structured observations](observations.json).

## Search priorities after this round

1. Test candidate demand against direct domain products before treating blockchain infrastructure as the closest competition.
2. Investigate technical mechanisms that yield a reproducible result beyond what a new UI or integration already supplies.
3. For COMMONS, resolve secure runtime/randomness compatibility, release consistency, and the identity of a community whose needs existing tools do not meet.

Product development remains reserved for the November window. This round produced research records and candidate documentation, with no product implementation or deployments.
