# Additional NEAR project candidates

Two alternatives investigated after retaining COMMONS as a main candidate. These are research candidates, not approved product builds or claims of unprecedented inventions. Working names have not been checked for brand conflicts.

**LIFEBOAT was subsequently retained by the user and now has a [maintained main-candidate directory](../../projects/lifeboat/README.md).** The later [SUNSET and MOLT proposals](../frontier-ideas-2026-10-22/README.md) pursue new ownership and collective-action mechanisms.

**LIFEBOAT is the stronger next engineering investigation.** It would let an owner move a paid agent service between operators while retaining the service's identity, job ledger and funds, and denying new payment actions from the replaced operator. The first proof must demonstrate the handover at the actual contract that controls effects. A new checkpoint viewer is insufficient. [Candidate brief](lifeboat.md).

**CLEARLOOP has a particularly legible economic mechanism but heavier competitive overlap.** It would settle mutually accepted obligations by collecting only net amounts inside a NEAR service ledger. Cycles, Ophir and Canton implementations are substantial prior work. We need an underserved NEAR integration and a measured advantage before promoting it. [Candidate brief](clearloop.md).

| Criterion | COMMONS | LIFEBOAT | CLEARLOOP |
| --- | --- | --- | --- |
| First user outcome | Community members gain a private earnings comparison | A paid service changes operators without losing its work and monetary state | Consenting participants move less money to settle obligations |
| NEAR responsibility | Shared approved-release and payment state | Owner-controlled service registry, current execution authority and payment ledger | Agreed obligations and one-contract net settlement |
| Hardest first proof | Defensible confidential statistical release | A replaced operator cannot admit another financial action while accepted actions are reconciled | Correct, consent-bound netting and insufficient-funds behavior |
| Closest precedents | Worker analytics, Vana, OpenMined | Temporal, OutLayer vaults/leases, Agentplat | Cycles, Ophir, AtomicNet |
| Two-week implementation risk | High | Medium to high with native NEAR effects only | Medium for public single-asset settlement; much higher with confidentiality or cross-chain atomicity |
| Current selection state | Main candidate retained by user | Main candidate retained by user | Research candidate with significant differentiation risk |

These are engineering judgments rather than measured success probabilities. No idea is ranked by invented market size or prize odds.

## A third direction was rejected

PATCHPOOL would have pooled downstream funding for independently reproduced dependency fixes. The collected NEAR board already contains [Dependency Insurance](https://nearbuilders.org/projects/idea/dependency-insurance-w40jzi) and [DevHub Bounty Sentinel](https://nearbuilders.org/projects/idea/devhub-bounty-sentinel-or-autonomous-builder-agent-d894kv). Drips already funds dependency trees, Google rewards qualifying security patches, and Akrites coordinates confidential remediation. We should not present a combination of these as a newly discovered gap. [Drips](https://www.drips.network/solutions/dependency-funding), [Google Patch Rewards](https://bughunters.google.com/open-source-security/patch-rewards), [Akrites](https://akrites.org/).

## What the crawler added

Crawl4AI was installed in an isolated temporary environment and used on actual public sources. A CSS extraction from the rendered NEAR Builders page returned 136 nonempty project titles. The first short wait returned a loading shell, demonstrating why HTTP success alone is not content verification. The new extract confirms the board coverage; it does not add 136 different projects to the earlier collection.

The wider pass checked eleven distinct URLs over thirteen browser fetches. Two URLs returned 404 and are excluded as usable sources. Raw source text remains temporary; the retained research contains metadata, source links and our analysis. [Crawler evidence and method](../crawl4ai-2026-10-22/README.md).

## Next decisive investigations

For LIFEBOAT, distinguish a handover of service authority from ordinary process recovery or existing wallet recovery. Design the stale-operator failure before adding an LLM.

For CLEARLOOP, find one actual set of consenting counterparties and compare with the existing netting implementations. Avoid a production invoice-finance claim from a simulated ledger.

COMMONS remains in [the main project directory](../../projects/commons/README.md). Product development is reserved for 1–14 November; this round adds research and crawler evidence only.
