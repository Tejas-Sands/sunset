# SUNSET value-and-impact finishing plan

> Execute this bounded continuation in the current session. Existing script and visual direction remain approved; changes implement the operator's request to finish their value/impact presentation.

**Goal:** Deliver a reviewable 34-second finishing cut that makes reader benefit and creator continuation visible.
**Architecture:** Verified V19 frames plus deterministic native-resolution Pillow/FFmpeg composites and a remixed licensed score.
**Spec:** [DESIGN.md](DESIGN.md). Original project conventions retain the plan beside its media source.

- [x] Recover earlier operator feedback, reopen both reference overviews, inspect V19 and verify available original assets/capture provenance.
- [x] Implement `finish.py` with exact input hashes, explicit frame mapping, stable real-reader crop, same-maker continuation, paired payoff and demo CTA. Produce representative stills before rendering.
- [x] Implement `audio.py` using the retained score/Foley sources, continuous music and remapped action times; remove the obsolete reader click.
- [x] Render all 1,020 frames at 1920×1080/30fps and run `verify.py` against the actual final movie. Check native pixels, source mapping, finance order, branding and audio.
- [x] Inspect native/390px output and chronological transition samples; record limits/credits/evidence and update the delivery guide. Verified local commit closes this batch; the operator pushes.

Review focus: source holds must be explicit; no slowed prior animation; no invented reader action; no Git/search/checklist pixels; no different maker at the continuation; no lost logo proportions; credit, claim, confirmation and Paid stay ordered; no adoption or financial proof inferred from illustrative scenes.

Final verification: `python3 projects/sunset/media/launch-v20/verify.py` passed all1,020 decoded frames,690 original/brand comparisons,126 native excerpt comparisons,20 prior movies and encoded sound. Initial colour-tag failure reproduced and corrected by explicit H.264 VUI stream-copy finalization; final check passes without relaxing colour requirements. Fresh independent source/sampled-output review found no blocking/important issue. Deferred minor: supporting paragraph/provenance is too dense for full phone reading; the large benefit copy carries that scene.
