# SUNSET kinetic launch film — v2

This replaces the 82-second narrated-card format with a native frame-driven 30-second app-launch film. Version 1 is preserved. The new composition is 1920×1080 at 30fps, with eight 3.75-second sections on a 128 BPM grid (16 bars). It animates independent text, genuine UI excerpts, masks, camera targets, cursor, file illustration and artwork layers.

From the repository root, with the retained existing media inputs:

    python3 projects/sunset/media/launch-v2/render_motion.py --preview
    python3 projects/sunset/media/launch-v2/render_motion.py
    python3 projects/sunset/media/launch-v2/render_launch.py --preview
    python3 projects/sunset/media/launch-v2/render_launch.py

The first renderer creates the 9.6-second style proof at 1280×720. The second creates the distinct 30-second film at native 1920×1080. Both support --duration for short encoding checks; --preview writes review stills only. They require the already available Pillow, FFmpeg and ffprobe. No new package, paid renderer or model download is used.

Inputs remain in ignored .publication/sunset-launch-v1/ (genuine screenshots, existing logo raster and converted Geist font) and .publication/sunset-launch-v2/voice/ (six edited voice clips and provenance). Retain those inputs to reproduce the edit; a fresh clone does not contain recordings. Original public artwork/font licenses remain under projects/sunset/public/.

Outputs under ignored .publication/sunset-launch-v2/:

- sunset-motion-proof.mp4: 9.6-second style proof.
- sunset-launch-v2.mp4: final 30-second H.264/AAC fast-start film.
- sunset-launch-v2-poster.png, sunset-launch-v2.srt, full-resolution review frames and full-motion-contact-sheet.jpg.
- full-ffprobe.json, media-provenance.json, media-qa.json and credits.

Actual app pixels come from verified hosted/standalone-game captures in projects/sunset/evidence/browser-showcase.json. The animated pointer reenacts the already captured answer-12 and standalone-download actions. The feedback and cold-browser offline completion are genuine captured states. This is motion design, not an uninterrupted screen recording. No fabricated wallet UI, financial click or fresh chain transaction is shown. The HTML file tile and copy fan are editorial illustrations. The film omits protocol walkthroughs, proof tables and NFT/refund claims.

The first frame is a legible SUNSET/learning poster. Regional game camera punch-ins, feedback and download/offline transitions carry the product story. Quiet NEAR TESTNET identification follows the opening. The final URL stays settled for approximately 2.8 seconds.

AI narration edits whole prior Kokoro af_heart phrases (original sentences02,04,11,13,19,20), using pitch-preserving atempo1.12. No voice cloning or fresh synthesis is implied. Forty words occupy about14.69 seconds, leaving music/action gaps. Captions preserve each phrase exactly and run only during speech. The last phrase finishes before the film ends. edit.json records actual assets and final voice placements.

Music and click/whoosh/chime accents are original procedural128BPM synthesis. No commercial sample or third-party music recording is used. Existing hero generation provenance and Geist OFL remain in public assets; Kokoro model/wrapper provenance and licenses remain in the existing voice delivery. Perceptual listening requires actual playback; tool checks cover decoding, timing and levels.

Do not commit generated media, voice/model binaries or caches. Only the isolated source and edit recipe belong in Git.
