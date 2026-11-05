# Two separate reference motion reconstructions

The operator rejected V13 because three poster layouts and wipes looked unlike the supplied films. V14 follows each film separately instead of mixing their styles. The [595-frame study](../reference-study-2026-11-05/README.md) supplies exact source identities and timings; [fidelity review](FIDELITY.md) records the visual gate and its limits.

| Test | Source scope | Original-only output |
| --- | --- | --- |
| Collage | Feel Good f000–159, 8 seconds at 20 fps | `.publication/sunset-launch-v14/collage/sunset-collage-motion-match-8s.mp4` |
| Minimal | Intelligence f000–194, 10.833333 seconds at 18 fps | `.publication/sunset-launch-v14/minimal/sunset-minimal-motion-match.mp4` |

These are silent motion tests, not a finished launch film. Collage follows portrait grid → tilted portrait macros → oblique type → mustard collage → strips → photographic wall → corridor → camera crops. Minimal follows full picture → contained moving windows → point → bracketed changing type. Subject matter and wording are original substitutions; cadence, composition, cuts and scale follow the respective source. Intentional departures and remaining limits are documented in [Collage](COLLAGE.md) and [Minimal](MINIMAL.md).

[Artifact and review evidence](../../evidence/launch-motion-v14.json) records both exact movies, their private comparisons and the qualified visual review. Independent full decode passed 160 + 195 original frames and both comparisons; all thirteen earlier movie hashes are unchanged. Those checks establish the files' identity and export integrity, not an exact aesthetic match or operator approval.

Neither test has a persistent headline, footer or explanatory overlay. The collage's opening portrait grid briefly includes a tiny local “Motion study” print credit; comparison headings stay outside the active picture. No supplied reference pixels or audio enter the original-only output. [Assets and exact prompts](ASSETS.md) document fictional creator illustrations and scenery. Source subjects, artwork and source fonts have not been claimed as original SUNSET assets or recovered authoring files.

All videos, reference extractions, comparison images, generated assets and cached fonts remain ignored. Reproduction needs those locally retained inputs, Pillow, NumPy and FFmpeg; these are developer media tools, not requirements for using SUNSET. Render gates first with `python projects/sunset/media/launch-v14/collage-match.py --gate --compare` and `python projects/sunset/media/launch-v14/minimal-match.py --gates`. Inspect source-matched comparisons before rendering full output with the respective `--render` and `--frames --encode` options. `python projects/sunset/media/launch-v14/verify-and-compare.py` independently decodes both finished files, checks their identity/format and the thirteen older movies, and creates separately labelled private comparison videos.

The [35-second creator-first script](../launch-v12/SCRIPT_DRAFT.md) remains a proposal: valuable work can be free to use while its creator is compensated and able to keep creating. These tests do not demonstrate a workshop release, financial settlement or browser interaction. No application, contract, campaign, signature, deployment, social post or submission changes are part of this batch. Operator creative approval is not claimed.
