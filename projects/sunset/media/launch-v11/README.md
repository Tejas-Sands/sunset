# SUNSET v11 — tactile 3D launch film

Selected correction: real rounded 3D objects, contact-driven softness, camera travel and clear, brief product messaging. [Direction](DIRECTION.md), [script](SCRIPT.md), [exact timing](timeline.json), [production research](RESEARCH.md) and [credits](CREDITS.md). The eight-second proof is preserved separately; the full cut is 34 seconds.

The padded handbook, coral SUNSET seal and mint sponsorship pieces use new rounded meshes with satin materials and UV print. Each authored contact compresses along its contact axis, bulges laterally and settles with damped recovery. The deformation preserves volume analytically. This is authored squash/stretch with constrained paths, not a full soft-body simulation. The camera changes scale and angle around one coherent scene. The already-open handbook continues after the proof rather than restarting the reveal.

After the financial illustrations, five seconds of genuine downloaded-file footage show a real checklist action and a visible saved result surviving reload. Two physical copies then approach through clear lanes. The film ends with the original mark. It contains no product URL, credit block or generated narration. [Prepared post](x-post.txt) carries demo/repository links and a feedback invitation; [companion reply](x-reply-credits.txt) supplies full music attribution. Nothing is automatically posted or submitted.

## Sources and rendering

The project uses cached Three.js 0.180 and an isolated WebGL2/SwiftShader browser. Frames are rendered directly at 1920×1080 with MSAA4 at exact n/30 timestamps, then encoded once with H.264 CRF14, BT709 limited colour, AAC48k stereo and faststart. No older MP4 pixels, frame interpolation or 3D upscaling are used.

The opening uses 240 original native proof frames. A separate continuation renders 510 native frames over 8–19s and 24–30s. The 19–24s UI sequence uses genuine source PNGs with original elapsed-time holds; the final four seconds are native raster typography and the original logo. The complete film has 1,020 output frames.

Original proof sources remain `motion.mjs`, `scene.mjs`, `render_scene.mjs`. The continuation uses `motion-full.mjs`, `scene-full.mjs`, `render_full_scene.mjs`. The wrapper reuses the accepted geometry/materials and adds two actual padded copies; both preexist offscreen and enter separate paths. The proof's archived compositor recipe is retained in ignored `composite/proof-render_launch.py`, since the current `render_launch.py` also assembles the full cut.

All required raw assets are pinned by exact hash in native/compositor manifests. These include the original SUNSET mark from v1, cached Three.js modules/license from v5, two OFL font files from v6, licensed recordings from v9/v11 and the passed v10 native handbook capture. They remain ignored rather than shipping generated media/dependencies in Git. A fresh clone needs those licensed inputs reacquired at the recorded identities before rendering; the commands alone do not download them.

```sh
# From the repository root, with the pinned ignored inputs present:
node projects/sunset/media/launch-v11/verify_motion.mjs --self-test
node projects/sunset/media/launch-v11/verify_full_motion.mjs --self-test
node projects/sunset/media/launch-v11/render_full_scene.mjs --probe
node projects/sunset/media/launch-v11/verify_full_motion.mjs --probe --live .publication/sunset-launch-v11/qa/full-probe-live.json --out .publication/sunset-launch-v11/qa/full-probe-verification.json
# Inspect the actual native probe and independent geometry gate before the full job.
node projects/sunset/media/launch-v11/render_full_scene.mjs
node projects/sunset/media/launch-v11/verify_full_motion.mjs --live .publication/sunset-launch-v11/qa/full-native-live.json
python projects/sunset/media/launch-v11/prepare_full_audio.py
python projects/sunset/media/launch-v11/render_launch.py --full-check
python projects/sunset/media/launch-v11/render_launch.py --render
python projects/sunset/media/launch-v11/verify_delivery.py
```

The separate proof soundtrack uses `prepare_audio.py` and `audio-proof/`. The full soundtrack uses `prepare_full_audio.py` and `audio/`; rebuilding one does not overwrite the other. Master, music and Foley stems remain separate for a later human voice recording.

## Verification and interpretation

Independent geometry checks inspect actual exported mesh vertices/transforms/camera, finite and nonempty geometry, post-deformation support containment, floor and all solid pairs. A scene-specific interval replay bounds the continuous paths at 240Hz; unresolved intervals reject. Regression cases include lateral squash bulges, floor stretch, crossing between 30fps endpoints and a copied handbook penetrating the original. Ordinary front/behind occlusion is allowed. A camera being physically outside a body is different from an important object being framed legibly.

The six-solid opening proof has separate actual geometry evidence. The full continuation has eight solids; offscreen copies are allowed outside the view but still require physical and camera clearance. The full model does not retroactively claim those copies were captured in the original proof. Source identities are checked before and after capture.

The delivery verifier independently decodes the movie and checks stable reading windows, actual glyph probes, safe bounds, genuine UI crop identity, source/audio/codec identities and old-film preservation. Native poses, dense decoded contact/camera strips and phone samples support a separate visual review. These checks establish specific technical properties; they do not prove an audience will like the edit or replace perceptual listening.

The handbook is a locally verified example, not the resource named in old finalized testnet transactions. Financial images illustrate NEAR custody, timely matching-key release, creator withdrawal eligibility and conditional pre-release sponsor refunds. No new campaign, contract, signature or deployment is part of this video work. The browser capture is real interleaved native screenshots/input, not continuous 30-unique-frame UI recording. Commands are inert handbook reference text and were not executed. See [guide evidence](../../evidence/handbook-guide.json) and [the final delivery guide](../../docs/LAUNCH_VIDEO.md).
