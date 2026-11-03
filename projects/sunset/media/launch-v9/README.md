# SUNSET v9 — one pack, many lives

The operator-approved story follows the cost of making a learning pack, community sponsorship under reviewed terms, NEAR escrow, a matching-key public release, separate creator credit and withdrawal, and conditional sponsor refunds. The payoff is a genuine downloaded game working offline and remaining when its host leaves the picture.

The picture is 56 seconds, 1920×1080 at 30 fps. It uses kinetic flat 2D artwork, Bricolage Grotesque and Space Grotesk, an opening sunset, foreground pack passes, changing scale, individual letter assembly and object handoffs. Readable holds carry the explanation. No generated narration is included; the 111-word [approved voice reference](voiceover-reference.txt) is retained for a later recording.

## Delivery

From the repository root:

```sh
xdg-open .publication/sunset-launch-v9/render/sunset-launch-v9.mp4
```

Background master: `.publication/sunset-launch-v9/audio/mix.wav`. Separate pre-master stems: `audio/music-arranged.wav` and `audio/sfx.wav` in the same ignored version directory. Adding a voice needs timing against a real read and a new audio master. There is no voiced-caption file for this music-only version.

## Screenwriting and motion

| Time | Message and picture |
| --- | --- |
| 0–6s | A literal sunset becomes a lesson page and one pack. Work comes before “Who pays for it?” |
| 6–11s | Community interest becomes one public-release agreement boundary. |
| 11–20s | Review precedes funding. An empty target and separate deadlines carry into the NEAR escrow scene; contributions then fill the target. |
| 20–29s | Matching teeth connect the key to its commitment. A large opening reveals the inner lesson. Creator credit precedes a distinct withdrawal. |
| 29–35s | An explicit alternative **before release** covers a missed target or late release, followed by sponsor refund claims. |
| 35–44s | Genuine Download control → opened standalone file → actual answer 12 → visible feedback. Editorial close-ups keep the control/result readable on a phone. |
| 44–51s | The actual result stays in front as copies spread and the host falls away; no wallet is needed to learn. |
| 51–56s | Original mark, SUNSET, “Support once. Share forever.” |

[Approved screenplay](SCRIPT_DRAFT.md), [production plan](PRODUCTION_PLAN.md), [timeline](timeline.json), and [final review](REVIEW.md) keep story, implementation and review separate.

## Genuine proof and factual limits

The financial scenes are labelled protocol illustrations, not a recording of browser signing. Refunds are a conditional pre-release branch; they do not reverse the successful release. Review is a reviewer action, not a contract guarantee of educational quality. Learners can keep an already downloaded file; this is not a promise of perpetual hosting.

Actual product footage reuses the retained v8 browser recordings: 21 native 2560×1800 PNG samples, six distinct states, sampled at approximately 3 fps and held by source wallclock at 30 fps delivery. It is not 30 unique browser frames per second. Real input/result timing, screenshot hashes and offline-before/after states are retained. The standalone file has zero external resource requests in that recorded browser session.

The camera uses documented crops and up to 2.2× LANCZOS editorial magnification of genuine pixels; no new UI states or detail are generated. The kept-copy shot is explicitly an endpoint hold from the genuine result. Added mouse Foley is licensed sound, not native browser audio. The failed optional higher-DPR takes are excluded. No settled financial action was repeated.

## Sound and posting

Backbay Lounge by Kevin MacLeod supplies the instrumental bed; seven causal effects use licensed recordings of pages, a physical latch and a mouse. No TTS, voice model or procedural score/effect is used. [Full credits and edit disclosure](CREDITS.md) include source/license links and explain the pre-master stems. Measured codec/loudness checks do not substitute for human listening.

Attach the movie natively with the [main post](x-post.txt), then add the [music attribution reply](x-reply-credits.txt). The post contains demo/repository links, event wording/tags and a feedback invitation. The picture has no product URL or music-credit overlay. Nothing has been posted or submitted.

## Reproduce and verify

Run from the repository root with Python 3, Pillow, CairoSVG, NumPy, FFmpeg and the retained ignored inputs available:

```sh
python3 projects/sunset/media/launch-v9/prepare_proof.py
python3 projects/sunset/media/launch-v9/prepare_audio.py
python3 projects/sunset/media/launch-v9/render_launch.py --render
python3 projects/sunset/media/launch-v9/verify.py
```

The renderer creates native graphics and encodes directly once; it does not ingest an older launch MP4. Font provenance pins OFL sources. The verifier checks the actual delivery, source identities, all-frame text, real footage chronology, audio, and unchanged v1–v8 movies. Generated video/audio/captures/fonts/cache and private files remain ignored. A fresh clone needs the ignored source inputs; the recipes alone do not fetch every prior recording. [Public evidence](../../evidence/launch-video-v9.json) records the final artifact and review limits.
