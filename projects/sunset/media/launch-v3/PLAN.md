# SUNSET v3 implementation plan

Goal: deliver a 30-second 1920×1080/30fps launch film whose moving mechanism explains SUNSET's onchain role.

Architecture: one native Pillow renderer reuses existing font/logo, verified UI captures and retained synthetic voice sentences. FFmpeg creates pitch-preserving voice edits and encodes H.264/AAC. All generated assets remain in ignored .publication/sunset-launch-v3.

Constraints: preserve v1/v2; no product, wallet, signing or chain actions; original warm logo; persistent NEAR TESTNET; PROTOCOL VISUALIZATION labels for editorial mechanism scenes; no investment or content-ownership claims; current holder controls mirror authority while public copies remain usable.

- [x] Write artifact verifier and observe missing-video failure.
- [x] Implement source assets, exact voice cues, 128 BPM object-continuity scenes, captions and procedural music.
- [x] Preview opening, cap, release, UI feedback, offline mesh, maintenance handover and close at intermediate transition frames.
- [x] Render 900 frames, exact 30-second audio mix, poster and source/cue provenance.
- [x] Run complete decode, ffprobe, caption/source consistency and audio-level checks; inspect contact sheet and deliver limitations.

Creative sequence:
0–3.75: SUNSET warm mark, resource capsule and kinetic sponsor nodes.
3.75–7.5: nodes flow into capped escrow; fill stops at target.
7.5–11.25: matching committed key opens resource; creator credit wire lights.
11.25–15: genuine answer12 and success-feedback action.
15–18.75: local HTML copy and genuine cold-offline completion expand into a public mesh.
18.75–22.5: maintenance credential passes A to B; only mirror edge follows it; public copy mesh stays open.
22.5–26.25: intact public copies orbit SUNSET; support once/share forever.
26.25–30: warm original logo, stable URL and NEAR testnet CTA.

Final artifact: .publication/sunset-launch-v3/sunset-launch-v3.mp4

Verified: 30.000seconds, 900frames, H.264/yuv420p 1920×1080/30fps, AAC48kHz; complete decode passed; moov precedes mdat; seven voice/source/caption checks passed; last speech ends29.4478s; -16.63LUFS/-1.41dBTP; zero black intervals at duration.20/pixel.02/picture.98.

Decoded opening and authority-handover images were visually inspected after replacing unsupported arrow glyphs with ASCII wording. Nine decoded review frames and decoded-contact-sheet.jpg match the final binary. Full perceptual audio playback is not verified by these checks.
