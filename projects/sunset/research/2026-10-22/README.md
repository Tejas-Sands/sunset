# SUNSET domain research

SUNSET has a credible role as infrastructure for financing the public release of useful resources. Its strongest first application is a small, locally relevant learning resource that a teacher can inspect, a sponsor can fund, and a community can retain independently of the original website. The release agreement and offline survival are the product's distinctive work; educational content, public-goods finance and offline distribution all have substantial precedents.

**Research date:** 22 October 2026. This package contains research and illustrative calculations, not product implementation or evidence of a school pilot.

## Main findings

1. **Purchases financing public release are established prior art.** Unglue.it described Buy-to-Unglue in 2013, including the incentive to wait near completion. SUNSET should acknowledge that lineage and demonstrate an implementation advantage. [Original proposal](https://blog.unglue.it/2013/08/06/a-new-kind-of-ungluing-campaign/).
2. **A funded counter is insufficient.** The creator's buyout must depend on disclosure of the committed key; the exact resource still needs valid rights, review and available copies. Independent disclosure and refunds are separate proofs. [Technical feasibility](TECHNICAL_FEASIBILITY.md).
3. **Offline education includes people and infrastructure.** Existing delivery systems combine local distribution with educator support. A local pilot should choose its curriculum, language, devices and facilitator with a partner before making impact claims. [Education and adoption](OFFLINE_EDUCATION_AND_ADOPTION.md).
4. **The economics need validation before expansion.** Buyers receive immediate licensed access; sponsors can value later public reuse. Neither implies enough buyers will complete the target. A separate access grant cannot be counted as asset-buyout funding. [Prior art and economics](PRIOR_ART_AND_ECONOMICS.md).
5. **November 1 is explicitly the submission opening and the event start.** The site also describes a two-week development period. Its published pages do not explicitly settle eligibility for pre-event code. [Exact timing analysis](HACKATHON_RULES.md).

## Read in this order

| File | Decision it supports |
| --- | --- |
| [Prior art and economics](PRIOR_ART_AND_ECONOMICS.md) | What already exists, who pays, why they might pay, and where funding fails |
| [Offline education and adoption](OFFLINE_EDUCATION_AND_ADOPTION.md) | Which educational problem to test and how to deliver responsibly |
| [Technical feasibility](TECHNICAL_FEASIBILITY.md) | What NEAR enforces, remaining trust, and necessary design refinements |
| [Hackathon timing](HACKATHON_RULES.md) | Confirmed dates versus unresolved eligibility policy |
| [Economic scenarios](economic_scenarios.csv) | Exact illustrative cash flows, including partial final orders |
| [Research calculation](analyze_economics.py) | Reproduce the scenario CSV using decimal arithmetic |
| [Source register](sources.json) | Primary sources, access notes, support and limits |
| [Rules evidence](rules-evidence.json) | Timestamped page hashes and targeted browser observations |
| [Verification](verification.json) | File integrity, links and calculation checks |

## Recommended first demonstration

An adult educator authors a short original integer-maths module and identifies its release rights. A second adult reviews it. Sponsors buy licenses for adult learning-group administrators, receive usable copies and accept delivery. The capped buyout is completed; a teacher discloses the key while the creator's process and Vercel API are stopped. A new visitor verifies the released bytes and opens a previously exported game with networking disabled. A second campaign demonstrates the promised refund, and a separate grant demonstrates bounded teacher support.

This is a proposed technical demonstration. Its language and content need actual educator review. It does not establish a partnership, curriculum approval, learning improvement or demand from paying institutions.

## Research decisions to carry into implementation

Keep the selected architecture and first milestone. Make three refinements explicit before contract implementation: define which sensitive methods require deposit-capable authorization; specify the exact license and provenance included in each export; and distinguish source-content size from ciphertext and export size. Keep Kolibri packaging as an optional compatibility experiment after the independent export works. [Specific changes and checks](TECHNICAL_FEASIBILITY.md#changes-to-make-before-implementation).

No outreach, private community access, submission, financial transaction or hosted resource creation is part of this research.
