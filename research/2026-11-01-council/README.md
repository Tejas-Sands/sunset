# SUNSET council decision — 1 November 2026

> Subsequent authorized work added a functional stewardship NFT. See [the tokenization research/reviews](../2026-11-01-tokenization/RESEARCH.md) and current product README for the implemented feature and updated NFT-track candidate; this council record preserves the earlier scope decision.

**Decision: keep SUNSET, simplify the mechanism, build the proof.** The research is worth using. It supports a plausible hackathon prototype, not demonstrated school demand, educational effectiveness or a validated business.

SUNSET lets adults jointly sponsor one precisely committed resource. The fixed creator receives the capped escrow after the matching decryption key is published on time. If the funding/release conditions fail, contributors can claim refunds. Learners can keep an independently usable offline copy. This shared financial agreement gives NEAR a substantive role.

## Council method and limits

Applied the [LLM Council workflow](https://github.com/elihuvillaraus/skills/blob/main/llm-council/SKILL.md): independent answers → anonymized peer evaluation → chairman synthesis. Adapted to three independent seats (product/demand, engineering/security, live event evidence) and one fresh blind peer reviewer, followed by separate contract and frontend code reviews. All agents use the session model family; this is **not a cross-vendor council**, human validation or an independent audit. No paid inference service was used. Original response texts and peer review are retained:

- [Response A](response-A.md)
- [Response B](response-B.md)
- [Response C](response-C.md)
- [Blind peer review](blind-review.md): B > A > C. With one peer reviewer this is a single ranking, not a multi-reviewer aggregate.
- [Contract review](contract-review.md)
- [Frontend review](frontend-review.md)
- [Current event and complete track matrix](track-verification.md)

## What survives scrutiny

All three reviewers recommend keeping the selected product rather than pivoting. SUNSET's strongest evidence will be another person releasing and using a resource after the application operator disappears. COMMONS has a useful recurring worker decision but adds substantial privacy/runtime/cohort risks. LIFEBOAT still needs to establish an advantage over existing service recovery infrastructure. Neither alternative has validated demand.

Public buyouts are not new: Unglue.it described a related purchase-to-open-release mechanism in 2013. Offline education is already supported by Kolibri and others. Differentiate through a complete inspectable agreement, fixed beneficiaries, verified artifact, independent disclosure, refunds and genuinely independent reuse. Do not claim SUNSET invented open-content financing or offline learning. [Historical buyout proposal](https://blog.unglue.it/2013/08/06/a-new-kind-of-ungluing-campaign/), [Kolibri](https://learningequality.org/kolibri/about-kolibri/).

The strongest objection remains economic: a sponsor could commission an openly licensed resource directly. A real creator and adult sponsor must explain why collective funding and shared recoverable terms improve that arrangement. A small arithmetic game demonstrates software behavior; it does not prove commercial or educational value.

## The consequential correction

The October design gave a buyer a reusable decrypted pack before acceptance and then allowed a full pending-order refund. A strategic buyer could retain the pack and refuse payment. Offline revocation cannot fix that. The current build **replaces the sale/acceptance lifecycle with immediate public-release sponsorship**. Sponsors receive a free sample and clear funding terms; their contribution does not buy exclusive secret access. No pending orders or delivery-acceptance marketplace is claimed.

The original full architecture remains as historical planning. [Current runnable implementation](../../projects/sunset/README.md) documents the smaller implemented system and outstanding integration gates.

## Track choices follow evidence

The official 2026 event has thirteen tracks. Live rules now permit development since the October 19 announcement, testnet-only projects, multiple track selection and implementations without the named example integrations. The previous research's uncertainty about pre-event code and required integrations is stale. [Official rules](https://nearhackathon.com/HACKATHON.md), [official examples](https://github.com/nearai/near-hackathon-prompt-examples).

| Track | Recommendation for this build |
| --- | --- |
| Open Innovation | Primary target: substantive public-resource sponsorship and release/refund agreement. |
| Social Money | Strong secondary target: demonstrate independent contributors funding the same public outcome. |
| Real-World Money | Conditional third: show a usable creator compensation/refund/withdrawal journey with actual receipts. Sponsorship must remain sponsorship, not revert to unsafe purchase acceptance. |
| AI Security & Defense | Conditional extension only; local spending-policy checks do not enforce a malicious agent's onchain authority. |
| Agent Economy | Conditional extension only; deterministic procurement plans need consequential signed settlement and useful autonomous decisions. |
| AI Swarms | Conditional extension only; scripted strategies are allowed by the official example, but the local coordination lab alone does not prove a live swarm economy. |
| Autonomous Business | Defer until there is a complete useful autonomous seller/delivery/revenue loop. |
| Privacy / Games / DeFi / NFTs / Memecoins / Thesis | Do not claim: current product lacks their defining implemented behavior. |

The track reviewer favored broad coherent extensions; the blind reviewer favored a narrower core. Chairman ruling: build the release/refund core first. Retain lightweight, explicitly local access-budget and coordination experiments, but do not promote them into onchain or AI track claims. **Two primary targets, one conditional adjacent target, three contingent future extensions.** There is no demonstrated scoring benefit or guaranteed prize stacking from selecting more tracks.

## What was actually built

A Next.js static application contains campaign browsing, free sample gameplay, capped sponsorship, release/refund rehearsal, creator encryption, exact-pack reviewer preview, private backup restoration, public library, standalone offline exports, separate access-budget rehearsal, deterministic agent plans, protected CSV receipts and a fail-closed testnet viewer pinned to a reviewed contract code hash and block. The core needs no model key, database or paid provider.

A real Rust Wasm contract implements owner-curated campaigns, independent reviewer approval, capped native-NEAR contributions, exact key commitment disclosure, both deadline refunds, fixed creator credit and guarded asynchronous withdrawals. Rust dependencies were already cached; the contract uses the NEAR host ABI directly. This makes protocol-runtime validation particularly important. Browser localStorage is rehearsal state, never settlement authority.

Independent code review fixed prohibited transaction-context imports during RPC views, campaign-slot exhaustion by arbitrary creators, CSV formula injection, stale contract-view presentation, stale reviewer binding, mismatched custom pack identities and inaccessible custom-provider credit accounts. The global 100-account ceiling remains a disclosed availability limitation.

No Supabase resource, live contract, public hosted site, social post or hackathon submission has been created. No learner records or wallet private keys are collected. Runtime browser/offline execution could not be established because the OS refused browser socket operations; source/content/runtime packaging checks are not relabeled as browser proof. See [verification evidence](../../projects/sunset/evidence/verification.json) for final executed checks.

## Remaining submission work

Before calling this submission-ready: run protocol-appropriate NEAR Sandbox receipt tests including transfer/callback failure, deploy reviewed code to an actual testnet account, exercise independent participants' release/refund/withdrawal without the app, and complete real browser/mobile/offline checks. Obtain an independent educator's content review and one adult sponsor's problem feedback. Preserve source/artifact/receipt identities.

Deadline: **14 November 2026, 23:59 UTC / 15 November, 05:29 IST**. The official process requires a public repository, public human-approved X demonstration and real team/payout details. Prepare those concrete materials before requesting publication/submission approval. Do not submit invented identities, placeholder addresses or simulated transaction evidence.
