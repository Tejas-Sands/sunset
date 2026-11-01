# SUNSET offline education and adoption

The promising educational use is a specific, teacher-selected learning resource that can reach a group without reliable internet and remain reusable after its creator has been paid. A funding platform cannot supply curriculum relevance, devices, electricity or teaching by itself. Those delivery conditions determine whether releasing a file is useful.

## Existing offline systems

Kolibri already supports offline resources, locally organized content and distribution through local networks or storage devices. UNICEF's Learning Passport describes classroom hubs, intermittent synchronization and facilitator support. SUNSET should finance and release compatible resources where useful, while relying on educators to select the delivery model. [Kolibri](https://learningequality.org/kolibri/about-kolibri/), [Learning Passport offline model](https://www.unicef.org/learningpassport/offline-learning).

There is a concrete integration path worth testing later: Kolibri Studio accepts packaged HTML5 applications with a root `index.html` and local relative resources, rendered in an iframe. A reviewed SUNSET export could be packaged that way after its standalone form works. Popup restrictions, licensing metadata and actual import/runtime behavior need testing; a working local HTML file is not proof of Kolibri compatibility. [Studio format requirements](https://kolibri-studio.readthedocs.io/en/latest/add_content.html).

Keep that distinction clear in the prototype. The first artifact contains lesson data; it does not accept arbitrary uploaded HTML games. Our reviewed game runtime produces the export. Packaging our runtime is different from evaluating executable code supplied by a creator.

## What the evidence supports

UNESCO's 2023 Global Education Monitoring report describes mixed effects and underestimated technology costs, and emphasizes context, educator capacity and access. That supports a modest design: match one learning objective to a setting and budget the delivery around it. It does not support an assumption that adding AI or a wallet improves education. [GEM report](https://gem-report-2023.unesco.org/technology-in-education/).

Two evaluations illustrate why context and the comparison matter:

| Evaluation | Intervention and comparison | Reported finding | Limit for SUNSET |
| --- | --- | --- | --- |
| Delhi Mindspark, 619 students, 2015–2016 | Offer of access to a program combining adaptive software with instructor-led small groups | After about 4.5 months, the offer increased independently measured math scores by 0.37 standard deviations and Hindi by 0.23 | This evaluates the combined program, not a small game or software alone |
| Rajasthan individualization, 1,528 students, 2017 | Personalized versus grade-level versions of the same software over nine months | No meaningful average math difference; initially low-performing students benefited, with 0.22 standard deviations reported for the bottom quarter | A personalization component is not automatically beneficial for every learner |

[Delhi evaluation](https://www.povertyactionlab.org/evaluation/disrupting-education-evidence-technology-aided-instruction-india), [Rajasthan evaluation](https://www.povertyactionlab.org/evaluation/impacts-computer-based-individualized-instruction-math-learning-india-0?lang=en).

These are findings from particular Indian settings. They are not estimates for SUNSET or for African education systems. The useful lesson is to specify the actual intervention, comparison and measurement, rather than borrowing another product's effect size.

## Choose a setting before promising impact

“Children in Africa” is not a usable product specification. A local partner would need to define the country and curriculum, teaching language, reading level, accessibility requirements, typical devices, group size, power supply and facilitator. Different settings may need shared tablets, printed materials or a local server rather than an individual browser game.

For the hackathon, retain one short original integer-maths module with plain language, clear feedback and keyboard operation. An actual adult reviewer should inspect the arithmetic and wording. If qualified educational review is unavailable, label the result a technical sample rather than teacher-approved content. A named wallet alone does not establish professional qualifications.

Localization should change examples, explanations and curriculum alignment where needed, not just replace text mechanically. Start with the language the author and reviewer can properly assess. Do not claim multilingual coverage because a model produced translations.

## Delivery choices

| Mode | What the prototype can prove | Remaining practical constraint |
| --- | --- | --- |
| Online free intro | A learner starts without an account or wallet | Initial connectivity and a working browser |
| Selected pack cached in browser | A previously downloaded module plays offline | Browser storage may be cleared or evicted |
| Standalone HTML export | A copied file runs with the app, DB and network unavailable | Device/browser compatibility and local-file handling |
| Classroom server or Kolibri channel | A local network distributes reviewed resources | Separate setup, hardware, power and facilitator work; future test |
| Printed adaptation | Released content can be reused without a learner device, if its license permits | Formatting, printing and local delivery costs; future output |

Browser storage is normally subject to browser policy and storage pressure; a PWA cache should not be sold as permanent preservation. Keep an explicit file export and progress export. [Browser storage behavior](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria).

An export must include its resource, attribution, license notice, reviewed runtime and provenance. It should not fetch fonts, images, answers or keys from SUNSET while playing. Test it from a local file on the actual target browser with network disabled, then copy it to another device and repeat. A previously open tab is a weaker test.

## Rights and adaptation

For original lesson content, CC BY 4.0 is a sensible proposed default because it permits sharing and adaptation, including commercial reuse, with attribution and other conditions. That helps local translation, printing and paid support remain possible. The actual terms must be present in the agreement and export. [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The creator must control the rights they offer. Images, fonts, datasets and adapted lessons need their own provenance and compatible permissions. Already-open material remains open under its existing terms; a new annotation or translation must be described as that contribution, not as buying the original public resource into existence. NonCommercial or NoDerivatives conditions can restrict later providers or adaptation. Software needs an appropriate software license rather than treating a lesson license as sufficient for the game engine. [Licensor considerations](https://creativecommons.org/share-your-work/licensing-considerations/version4/), [rights-holder guidance](https://creativecommons.org/cc-license-your-work/).

Public reuse does not mean copyright is transferred to every learner. It means the rights holder grants specified permissions. A hash and contract payout cannot cure missing third-party permissions. A future real-money rollout needs the corresponding enforceable release agreement; the testnet prototype records and demonstrates the proposed arrangement.

## Access grants should buy a defined service

Keep asset funding separate from delivery expenditure. A grant might purchase one teacher orientation, a specified installation check or an agreed support period. Its purpose, unit, provider, adult approver, cap and expiry should be readable before funding.

A completed approval proves that the named account authorized payment. It does not prove attendance or learning. Require the kind of evidence appropriate to that service without collecting individual learner records: for example, a configuration report for a device setup or an adult facilitator's confirmation of a support session. Never present synthetic demo evidence as a delivered real-world service.

For an actual pilot, separately cost staff time, review, translation, devices, electricity, transport, maintenance, replacement and connectivity. Free cloud tiers reduce prototype hosting charges; they do not make those activities free. Offline copies should remain usable when a support grant expires, while new support needs another funded agreement.

## Measure access and learning separately

The technical demonstration can measure successful release, verified file integrity, independent download/export, offline completion, refund correctness and bounded grant spending. These are meaningful product outcomes.

A later education evaluation should use an educator-chosen objective, an assessment separate from the practiced items, a defined period and an appropriate comparison. A small usability pilot can identify confusing instructions and device problems; it cannot establish a causal learning effect. The operator should not infer learning from transaction count, game clicks or funds raised.

Keep individual progress local in the first build. Prefer adult operational reports and appropriately aggregated pilot findings. Any later collection involving learners requires its own locally appropriate consent, safeguarding and data design. It is outside this prototype's data model.
