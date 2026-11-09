# SUNSET accepted launch film

The operator accepted the final 44.667-second film. Its exact delivery is `.publication/sunset-final/sunset-launch.mp4`: **23,121,135 bytes**, SHA-256 **`57348b1f7fea925c31b61650808bcc65f47b70d74b1889831674e8bb2e48022f`**, 1,340 frames, 1920×1080 at 30 fps, H.264/AAC, BT.709 limited range and fast-start MP4. Consolidation copies these bytes; it does not export a replacement film.

The same workshop kit, camera and original fictional maker continue through the key/clasp hinge, separate claim/payment, alternative refund, copies, prior Lantern Trail evidence and dark SUNSET ending. The approved synthetic voice, script, timing, music and Foley remain unchanged. [Script](SCRIPT.md), [credits](CREDITS.md), [original artwork prompts](ARTWORK.md) and [bundle identities](bundle.json) are retained here.

Run from the repository root:

```sh
python3 projects/sunset/media/launch/verify.py
python3 projects/sunset/media/launch/produce.py stills --output /tmp/sunset-final-stills
```

The stills destination must be new. Verification is repeatable and writes `.publication/sunset-final/verification.json`. It checks all required bundle hashes, exact movie identity, complete video/audio decode, frame count/duration/codecs/color/fast-start, all 2,095 AAC packet identities and timing, 48 frozen native frame identities, encoded/native image comparisons, key contact/fixed hinge, continuing open/Paid refund poses and visible planes, phase continuity, protected payoff contrast, dark bookends, clean closing footer and measured audio levels. These checks require only this directory and the final ignored bundle; earlier films, browser tools, models and virtual environments are unnecessary.

The final bundle contains one accepted MP4, `timeline.json`, `narration.srt`, `assets/soundtrack.m4a`, `assets/Geist.ttf` and nine exact RGBA textures. Keep it separately with this source: generated media stay ignored and a fresh Git clone does not contain them. The immutable soundtrack is stream-copied AAC, including its encoder-delay side data; no new speech synthesis or audio remix is needed. The timeline's original `voice/*.wav` names record historical take identities and are not runtime input paths.

`archive/accepted-verification.json` is the original accepted-delivery report. Its preserved earlier-movie and negative-control references describe checks performed before cleanup; they are archival evidence, not dependencies or checks that the current verifier reruns. `archive/consolidation.json` records the one-time 48-frame full-resolution pixel-byte comparison against the original native renderer before consolidation. Every frame matched exactly. Current checks use frozen native pixel hashes instead.

The runtime uses Python 3, Pillow, NumPy, FFmpeg and ffprobe. Consolidation was verified with Python 3.14.6, Pillow 12.2.0, NumPy 2.5.0 and FFmpeg 8.0.1. Exact native pixel hashes may depend on these library versions and their font rasterizer. No application or protocol dependency is added.

To reproduce the picture into a **new** file, with the frozen soundtrack:

```sh
python3 projects/sunset/media/launch/produce.py render --output /tmp/sunset-reproduced.mp4
```

The renderer refuses to replace the accepted movie and refuses existing output/log files. This command was not used to replace the accepted delivery; codec/library changes can change encoded bytes even when native pictures match. `produce.py` contains the accepted animation; `native.py` holds only its reused projection/font/stage helpers. No earlier version paths are imported or read.

The archive receipt names the prior Lantern Trail testnet run, 2 November 2026, 0.1 testNEAR and one operator. The current workshop kit and finance scenes are illustrations. Consolidation performs no browser execution, signed protocol action, deployment or public posting and makes no new continuous-playback/listening claim. Required music attribution belongs in the accompanying description or [credit reply](x-reply-credits.txt).
