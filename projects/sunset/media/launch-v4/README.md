# SUNSET v4 — local-reference motion cut

This 24-second film responds to the two actual videos supplied in Downloads/refs. [Reference study](RESEARCH.md) records timestamped camera, material, typography and edit observations; [input metadata](references.json) identifies their exact hashes. No reference footage, images or music is used in the finished film.

The visual pipeline has two separate jobs: an original Three.js scene creates actual perspective, solid geometry, physical materials and camera motion; a Pillow compositor adds per-glyph typography, changing macro/crop arrangements, original brand graphics and short genuine gameplay excerpts. Final delivery is1920×1080 at 30fps. The exact native3D capture resolution is recorded in the scene-render metadata; do not infer it from the final container dimensions.

## Reproduce locally

From the repository root, with the existing retained inputs and installed tools:

    python3 projects/sunset/media/launch-v4/prepare_audio.py
    node projects/sunset/media/launch-v4/render_scene.mjs --preview --width 1280 --height 720
    python3 projects/sunset/media/launch-v4/render_launch.py --preview
    node projects/sunset/media/launch-v4/render_scene.mjs --width 1280 --height 720 --fps 15 --frames-dir native-frames --format jpeg --interpolate
    python3 projects/sunset/media/launch-v4/render_launch.py --render
    python3 projects/sunset/media/launch-v4/verify.py --mux

The recorded production choice starts with 360 original 3D frames at 1280×720/15fps and uses cut-aware motion interpolation for the background sequence. A text-critical 15.8–19.6s handover receives 57 additional direct 30fps samples; with its existing even samples, that entire 114-frame window is actual 30fps 3D. The final sequence contains 720 frames from 417 distinct directly rendered times. Typography, actual UI and captions are composed at native 1920×1080/30fps. The 3D renderer supports explicit --width, --height and --fps flags. Its final capture method, native resolution, actual frame count and dependency hashes are recorded under .publication/sunset-launch-v4/scene/. Cached dependencies are pinned to Three.js 0.180.0 with its MIT license. The server binds to loopback and serves only allowlisted scene/vendor/font/game assets. It creates a dedicated local agent-browser session with software WebGL; application dependencies and the production website do not change.

Required existing tools: Node.js with native WebSocket, agent-browser with installed Chromium/WebGL2, Python/Pillow/NumPy, FFmpeg and ffprobe. Retained media inputs are .publication/sunset-launch-v1/render/{logo.png,Geist.ttf}, footage/{06-hosted-verified-game.png,07-hosted-game-feedback.png,11-offline-game-complete.png}, and the five original voice/sentence-*.wav files plus timing metadata. A fresh Git clone does not contain those recordings or generated assets. Preview composition may use the nearest available 3D preview frame; final --render requires every exact source frame and fails on a missing frame.

## Editorial sequence

- 0–1.6s: technical specimen/independent SUNSET letters and a macro 3D mark.
- 1.6–4.8s: physical escrow/sun object with whole-frame FUND/ONCHAIN and cropped material-strip punctuation.
- 4.8–8.8s: release capsule opens around the resource, with key/credit typography and changing camera/framing.
- 8.8–9.6s: macro fragments transition into the real game.
- 9.6–12.6s: genuine question, graphical answer12 reenactment and genuine feedback; the result stays readable.
- 12.6–15.8s: physical copies and actual cold-offline completion.
- 15.8–19.6s: thick maintenance credential, holder handover and continued public access.
- 19.6–21.6s: oversized KEEP/IT and public-resource type/crop motion.
- 21.6–24s: original warm mark and settled URL.

Protocol/object scenes are editorial illustrations labeled MOTION VISUALIZATION. Real UI excerpts are labeled ACTUAL GAME. This is not financial browser signing, a new chain event or an uninterrupted recording. Matching-key release credits the creator; withdrawal is separate. The NFT conveys mirror-maintenance authority, not content exclusivity or a financial entitlement.

## Audio and verification

Five whole prior Kokoro af_heart synthetic phrases are edited at pitch-preserving 1.12 tempo with exact captions. No fresh synthesis, cloning or model download is used. Music and effects are original 150 BPM procedural synthesis, with measured voice ducking, mastered headroom and an AAC roundtrip check. No reference audio or external recording is reused. Source voice/model licenses remain in the retained v1 delivery.

verify.py muxes the completed silent picture with the already mixed narration/music WAV at unity, then checks 24s/720frames, codecs/dimensions, faststart atoms, complete decoding, exact captions, original/edited voice hashes, genuine capture hashes, voice overlap/tail, explicit blackdetect thresholds and final encoded loudness/peak. Decoded review frames remain separate from perceptual playback; audio listening is not implied by those measurements.

All generated media, reference samples, dependency caches, browser outputs and QA logs remain ignored under .publication/sunset-launch-v4/. Source recipes, original-reference analysis, public artifact verification and [X post copy](x-post.txt) are tracked. Earlier versions remain preserved. No social post, submission, deployment or signed protocol action occurs in this media pipeline.

The full --interpolate recipe automatically applies the text-detail pass. To repair only that window from retained inputs, use node projects/sunset/media/launch-v4/render_scene.mjs --detail-pass, then the compositor's --start-frame 474 --end-frame 588 --output PATH mode (end exclusive). Final assembly records the frame-exact replacement and its input/output hashes in composite/repair-provenance.json.
