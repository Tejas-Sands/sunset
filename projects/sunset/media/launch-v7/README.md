# SUNSET v7 — audio polish and clean end card

The operator approved v6's sunset-first playful 2D visuals and asked for better audio/background music plus removal of the product URL and entire on-screen music credit. V7 keeps the same 20-second picture, fonts, shapes, captions and timing. Only the URL and both credit lines are removed from the end card; logo, SUNSET, tagline and animated dots retain their positions.

The exact approved male am_puck narration is reused byte-identically. A new mix applies restrained voice EQ, gentle de-essing/compression and a more audible relaxed instrumental groove: *Backbay Lounge* by Kevin MacLeod, excerpt 16–36 seconds. Voice remains above the music with measured 8.50–11.69dB phrase separation. The new mastered WAV measures −15.35LUFS/−2.00dBTP, and AAC320 roundtrip −15.37 LUFS/−1.97 dBTP. Human subjective listening remains separate from these measurements.

The movie intentionally contains no product URL or music-credit text. Required recording attribution is in [post copy](x-post.txt) and [CREDITS](CREDITS.md), outside the picture. The post also omits the product URL. Retain the track/artist/source/license/edit disclosure when sharing the video; CC BY4.0 permits reasonable accompanying attribution rather than a mandatory burned overlay.

## Delivery and reproduction

Final: `.publication/sunset-launch-v7/sunset-launch-v7.mp4`, plus SRT, poster, audio, source/provenance/QA and decoded review sheets. All generated media, recordings, fonts, caches and private material stay ignored. All prior movies are preserved.

From the repository root with retained inputs:

```sh
.publication/sunset-launch-v5/tts-cache/venv/bin/python projects/sunset/media/launch-v7/prepare_audio.py
python3 projects/sunset/media/launch-v7/render_launch.py --render
python3 projects/sunset/media/launch-v7/verify.py
```

Existing v6 OFL font caches and their exact [provenance](fonts-provenance.json), original project mark/vector art and verified v5 DPR2 download/offline captures are reused. V7 voice files are byte-identical copies of v6's approved clips, not fresh synthesis. This source does not require a new voice model, renderer framework or application dependency.

Output is native RGB+master WAV directly into a single x264 CRF14/BT709/AAC320k/faststart generation. Independent checks cover all 600 actual decoded frames, promised reads, font/UI/voice/music/caption hashes, safe bounds/overlap, absence of URL/credit records, clean end-card samples, colour/container/audio properties and all six prior movie identities. No app/contract/signing/social/submission action occurs. Sources/evidence are committed locally; the operator pushes.
