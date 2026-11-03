# SUNSET v6 — sunset first, then kinetic 2D

The operator rejected v5's dark metal/formal tone and explicitly chose chill narration, fun kinetic 2D objects and expressive fonts. Their next instruction was to start with a sunset. This cut follows that direction: a warm flat sun sets behind horizon bands, then opens into moving letters, paper packs, keys, sponsor dots and copies. There are no 3D inputs.

[Design and font choices](DESIGN.md) document the warm cream/coral/mint/butter/cobalt palette, Bricolage Grotesque display lettering, Space Grotesk captions and translated reference techniques. The native 1920×1080/30fps composition follows 44 newly spoken words over 20 seconds. The measured voice ends at17.6645s; the final URL holds from 16.6–20s.

Narration uses a fresh pretrained male `am_puck` voice at natural 1.0 synthesis speed, without pitch/time alteration or cloning. Exact words/pronunciation text are in [narration-script.json](narration-script.json). Music is Scott Buckley's *Origami*, CC BY 4.0, excerpt 48–68s: the artist describes it as chill electro-jazz. Keep [credits](CREDITS.md) and the linked attribution in [post copy](x-post.txt). Human listening preference is not established by technical audio measurements.

## Local delivery and reproduction

The final delivery is `.publication/sunset-launch-v6/sunset-launch-v6.mp4`, with matching SRT, poster, voice preview, source provenance, measured QA and decoded beat/cut/360px phone sheets. All output/media/fonts/music/models/caches remain ignored. Previous movies are preserved.

With retained inputs and installed Python/Pillow/CairoSVG, FFmpeg/ffprobe:

```sh
.publication/sunset-launch-v5/tts-cache/venv/bin/python projects/sunset/media/launch-v6/prepare_audio.py
python3 projects/sunset/media/launch-v6/render_launch.py --preview
python3 projects/sunset/media/launch-v6/render_launch.py --proof
python3 projects/sunset/media/launch-v6/render_launch.py --render
python3 projects/sunset/media/launch-v6/verify.py
```

Retained font downloads/OFL licenses under ignored `v6/fonts` are identified by exact upstream commits/URLs/hashes in [fonts-provenance.json](fonts-provenance.json). The original logo/font assets and vector landscape come from the existing project. Reused actual DPR2 product pixels are from the verified v5 capture: real released-pack download control and actual offline HTML. Literal UI crops are not enlarged. The new cursor gesture edits an already verified download action; it is not financial signing or a new chain event.

The final output is generated directly from native RGB layers and the mastered WAV into one x264 CRF14/BT709/AAC320k/faststart generation. No older movie is a render input. Verification checks every decoded frame's recorded essential text probes, exact read windows/bounds, font/UI/audio hashes, nine captions, all colour tags, full decode, black detection, loudness and previous-movie identities. Visual samples and human listening remain separate review steps.

The local Brand typography/voice guidance and current official HyperFrames look/motion/story/review craft references inform this Pillow composition. No hosted video framework, shared account integration or paid service is introduced. The user's new 2D/sunset direction overrides v5's sober material styling. Source and public evidence are committed locally; the operator pushes. No app/contract mutation, deployment, signing, social post or submission occurs.
