# SUNSET v5 — clear story, native picture, calm male voice

The operator approved v4's physical-object/glyph/macro style and requested readable copy, mature sound/colour, better quality and deliberate screenwriting. The [locked screenplay](SCRIPT.md) is44 words over24 seconds. The [storyboard](STORYBOARD.md), [directing specification](SPEC.md) and [skills actually used](SKILLS_USED.md) explain the decisions. The two original local references remain researched under [v4](../launch-v4/RESEARCH.md); none of their media is reused.

## Production

- Same original pack, source SVG illustration and warm SUNSET logo; graphite/ivory stages with restrained copper, perspective camera entrances and two full-frame native macro handoffs. Essential words settle on controlled neutral backgrounds instead of moving reflections.
- Exactly528 visible CG frames rendered directly at 1920×1080, at their true30fps times, as lossless PNG with actual WebGL MSAA 4. Hidden CG intervals486–587 (actual UI) and630–719 (end card) are omitted deliberately. No JPEG intermediate, frame interpolation or lower-resolution CG enlargement.
- New genuine DPR2 browser captures show the public contract's recovered pack, real download control and actual downloaded HTML with browser offline before load. Crops stay at or below source-pixel size. No synthetic financial UI, wallet action, new protocol settlement or long quiz sequence.
- Fresh calm male `am_michael` narration at natural 0.98 synthesis speed, no cloned speaker, pitch shift or time compression. Nine complete sample-timed phrases, exact captions and1.672 seconds after the final voice.
- Scott Buckley's *Computations in a Snowstorm* (No Cello), CC BY 4.0, excerpt205–229 seconds, edited/faded/EQ/ducked. No procedural toy tones or added sound effects. Retain [credits](CREDITS.md) and the linked music credit in [post copy](x-post.txt).
- Final raw native RGB frames plus the mastered stereo WAV go directly into one x264 CRF14/BT709/AAC 320k/faststart encode. Verification never remuxes or re-encodes the output.

## Reproduce with retained local inputs

From the repository root:

```sh
.publication/sunset-launch-v5/tts-cache/venv/bin/python projects/sunset/media/launch-v5/prepare_audio.py
node projects/sunset/media/launch-v5/render_scene.mjs --preview
python3 projects/sunset/media/launch-v5/render_launch.py --preview
node projects/sunset/media/launch-v5/render_scene.mjs
python3 projects/sunset/media/launch-v5/render_launch.py --render
python3 projects/sunset/media/launch-v5/verify.py
```

Requirements: Node with native WebSocket, agent-browser/Chromium/WebGL2, Python/Pillow, FFmpeg/ffprobe, and the isolated Kokoro ONNX runtime. Scene dependencies are pinned to Three.js 0.180.0 with MIT license retained in the ignored cache. The scene server binds loopback and serves only allowlisted scene/vendor/font files. It closes only its dedicated browser.

Retained local inputs are `.publication/sunset-launch-v1/render/{logo.png,Geist.ttf}`, v5 `tts-cache` model/voice files and isolated runtime, licensed original music under `audio-research/music/`, and actual browser captures plus `footage/{manifest,capture-provenance}.json`. Model/music and frame hashes are checked. A fresh Git clone intentionally does not include these generated/media inputs. The PNG logo derives from `public/icon.svg`, the font from the project's OFL Geist asset, and the scene landscape is the original product SVG rather than an enlarged screenshot. To recreate a missing actual capture, recover the public released campaign read-only on the published site, download the exact standalone file, and capture the genuine resource at DPR2 with browser offline; never replace it with a fabricated UI or rerun settled finance.

Both preview and final composition require exact source frame indices; no nearest-frame fallback. Final rendering rejects an old/mixed scene manifest, incorrect source hashes, missing frames, non-native dimensions, unsafe glyph bounds, text overlaps or inadequate protected-plane contrast. Do not modify scene sources during capture.

## Review and delivery

`verify.py` checks the actual final720-frame file, source identities/native PNG CRCs/MSAA metadata, nine exact caption cues, audio sources/master, true peak/loudness, MP4 faststart/BT709, no unexpected black interval, stable promised title records and every encoded frame's essential foreground/background probes. It creates decoded beat, ±0.2-second cut and 360px phone sheets. Source and delivery pixel probes complement actual visual review; neither establishes human listening preference.

The final file is `.publication/sunset-launch-v5/sunset-launch-v5.mp4`, with SRT, voice preview, poster, decoded review sheets and `media-qa.json` beside it. The public [artifact record](../../evidence/launch-video-v5.json) identifies the completed delivery. Prior films remain preserved. All generated frames, movies, audio, models, downloaded music, skill/dependency caches and browser outputs stay ignored. Only original recipes, screenplay, documentation and public evidence are committed.

This is an edited product launch film. Protocol visuals illustrate rules; the actual source captures show read-only recovery/download/offline use. Real payout/refund receipts live in the existing product evidence. Testnet context is visible. No mainnet, permanent hosting, independent-user adoption or complete financial browser flow is claimed. Human sound playback, X upload and final submission remain operator actions.
