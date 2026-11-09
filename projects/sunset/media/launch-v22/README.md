# SUNSET V22 — a useful thing, made free

The launch film now has the operator's chosen warm synthetic voice A, one real workshop kit, an explicit alternative refund outcome and a qualified recorded testnet proof beat. The same fictional maker and kit connect creation, sponsorship and sharing. Projected paper planes, camera pushes and a foreground pass retain the kinetic collage direction. The original SUNSET logo and Geist typography remain; the ending has no URL or CTA.

Local movie: `.publication/sunset-launch-v22/sunset-launch-v22.mp4` — **44.667 seconds, 1,340 frames, 1920×1080 at 30 fps**. Optional subtitles: `.publication/sunset-launch-v22/narration.srt`. The actual [Community Skill-Swap Kit](../../public/try-workshop-kit.html) is a standalone, original CC0 guide for a 45-minute adult workshop using paper and pens.

[Script](SCRIPT.md), [spoken text](vo-script.md), [review](REVIEW.md), [credits](CREDITS.md), [Bang study](BANG_STUDY.md) and [artifact evidence](../../evidence/launch-video-v22.json) record delivery and limits. This is a new local example, without a kit-specific campaign or hosted update. The receipt identifies the older Lantern Trail testnet run and its one-operator scope. The workshop pictures are illustration, not footage of users or a new payment.

The MP4 uses the established local Pillow/FFmpeg renderer. Bang Motion informed a connected subject, wide/close camera changes and object handoffs. A separate editable browser companion adapts its actual collage starter and deterministic `OPENER` architecture; its MIT notice is retained. Browser startup is blocked in this sandbox, so that companion has source/syntax/input checks only. It was not used to export the MP4 and is not pixel-matched to it.

From the repository root, restore the retained ignored V19 master, V13/V14 artwork, Geist font, V16 music/Foley/GSAP and V5 local Kokoro environment before reproducing. These are production inputs, not application dependencies.

```sh
.publication/sunset-launch-v5/tts-cache/venv/bin/python projects/sunset/media/launch-v22/voice.py narrate --voice af_bella
python3 projects/sunset/media/launch-v22/produce.py prepare
python3 projects/sunset/media/launch-v22/produce.py stills
python3 projects/sunset/media/launch-v22/audio.py
python3 projects/sunset/media/launch-v22/browser.py
python3 projects/sunset/media/launch-v22/browser.py --check
python3 projects/sunset/media/launch-v22/produce.py render
python3 projects/sunset/media/launch-v22/verify.py
```

Takes, final audio, movie and verification refuse overwrites. Python needs Pillow/NumPy; production uses FFmpeg/FFprobe. Voice generation uses the retained isolated Kokoro/ONNX runtime. No network provider, cloning, global installation, shared account change or new protocol action is involved. The browser companion is generated at `.publication/sunset-launch-v22/browser/index.html`; open it with `?debug` for editing controls on a machine with working Chrome. Its playback still needs browser QA there.

The full Node suite includes strict guide/export/encryption/recovery checks. Media checks decode every output frame, compare all 543 retained source frames, sample custom poses against their native renderer, verify all 105 original closing frames and an empty footer, measure encoded audio, and preserve 22 earlier canonical films. The [review](REVIEW.md) distinguishes sampled visual inspection and measured sound from continuous human playback, listening and operator creative approval.

[Post](x-post.txt) and [required music-credit reply](x-reply-credits.txt) are drafts. No social publication, deployment or submission occurred. Generated media/models/caches remain ignored; verified commits stay local for the operator to push.
