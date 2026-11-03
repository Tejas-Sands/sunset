# SUNSET kinetic launch-film research — 3 November 2026

The requested deliverable is a short, energetic X launch film: a memorable product hook, a few moments that convey the app’s feel, and a clear invitation to try it. The previous 82-second narrated deck is preserved as v1; it is not the creative target for the remake.

## What was inspected

- [Brag’s official gallery](https://latent-spaces.github.io/brag/) and [creative guidance](https://raw.githubusercontent.com/latent-spaces/brag/main/skills/brag-slim/SKILL.md). Actual sampled frames from the maintainer’s Brag-slim demo and Fish Flight School example were inspected, rather than relying on third-party launch-video summaries. The examples reveal text progressively, move separate visual elements, and give the interface or illustration the frame. The maintainer recommends short films, deliberate music/cut timing and reuse of actual UI/components. Audio playback of these reference clips was not verified in the tool environment.
- [Raycast’s own Hype Team account](https://www.raycast.com/blog/hype-team) distinguishes educational YouTube content from release updates and sneak peeks on Twitter. Its stated aim is to motivate people to try the product. The [official launch surface](https://www.raycast.com/new) and announcement were read; its film was not successfully played here, so no frame-by-frame Raycast analysis is claimed.
- [Ordinary Folk’s Procreate Dreams case study](https://www.ordinaryfolk.co/project/procreate-dreams) establishes a 17-second branded piece with credited animation, music and effects. Its page was read as production context; the film itself was not played here.

## NEAR’s actual requirement

The current [official event instructions](https://nearhackathon.com/HACKATHON.md) ask for one complete user moment with a visible result and advise avoiding long introductions, architecture slides and setup. They do not prescribe a full end-to-end product walkthrough or a minimum video duration. A clear game answer → feedback moment can satisfy that guidance within a short launch edit; this scene choice is our recommendation.

The public X post still needs the built-at-NEAR-HACKATHON wording, @NEARProtocol, #NEARHackathon and attached demonstration media. Repository and demo-post links are used in the submission. The [X help page](https://help.x.com/en/using-x/x-videos) currently allows non-Premium uploads up to 140 seconds and 512 MB. The event’s shorter creative target is our choice, not an organizer-imposed limit.

## Why v1 felt static

Inspection of `../launch/render.py` found that each scene was flattened into one PNG. The only picture motion was a 1.8% global zoom and a short fade. Twelve scenes averaged 6.83 seconds; long explanation and repeated split layouts governed the pacing. The voice was stretched from 73.69 to 82 seconds. That architecture could not animate words, interface elements or transitions independently.

## Direction for the replacement

Target approximately 30 seconds, with a 128 BPM music grid and sparse AI speech. Keep SUNSET’s original cream, deep green, terracotta, sun mark, book artwork and Geist type. Use large two-to-five-word messages and let short actual app excerpts occupy the frame.

- Open with kinetic FUND / IT / ONCE and a fast product reveal.
- Carry the same orange circle into the logo/artwork through a mask transition.
- Briefly establish that this funds the public release of learning resources.
- Show one legible genuine answer selection and its successful feedback. Tight framing should emphasize the action, not the surrounding debug/read-only setup.
- Use a short download/offline moment to make retained access tangible.
- Resolve benefit typography and the existing mark into the stable URL and tagline.

Independent layer movement, spring settling, masks, object continuity, camera acceleration and integrated sound accents supply the energy. Important words retain readable settled time. Fast transitions should not become muddy crossfades or repeated whole-frame flashes. The edit must not be the nine-second motion test stretched to thirty seconds.

The old 161-word explanation, protocol tables, transaction hashes, chapter footers and refund-rule scene are excluded from the public trailer. Technical proof remains in the repository and post. A small NEAR TESTNET label stays with the prototype presentation. No browser wallet-signing flow, adoption statistics or unimplemented feature is invented.

## Verification and preservation

The new renderer lives separately under `media/launch-v2/`; generated outputs remain in ignored `.publication/sunset-launch-v2/`. The nine-second motion proof is reviewed at intermediate transition frames before the full edit. V1, its evidence and all onchain state stay unchanged. UI excerpts reuse genuine captures from the completed showcase, with staged pointer choreography disclosed in delivery provenance; no settled transaction is rerun for footage.
