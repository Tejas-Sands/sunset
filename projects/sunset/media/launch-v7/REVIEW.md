# SUNSET v7 final review

The operator approved v6's visuals, requested improved audio/background music, and asked to remove the product URL and whole on-screen music-credit block.

Final movie SHA-256: `8c1f850dce269c420ca9553b548a3a030107a2be2dec31864cf30819a210de44` (3,079,765bytes;20s; 1080p/30fps).

The visual source diff contains only version/cache paths and deletion of the URL/credit lines. The approved logo, brand, tagline, colour, fonts, sunset, shape motion, source UI, narration and cue timing retain their exact definitions. Root inspected the actual decoded 19.5s end card; a separate reviewer also independently decoded that final frame and checked all 600 records. No product URL, Origami, artist-credit line or music_credit/url record remains. Scoped P0: none; P1: none.

Independent verification passed every encoded frame:600-frame full decode, 1,606 authored text probes (minimum 5.123:1), ten promised reads, safe bounds/text separation, exact44words/nine captions, same raw narration/timing, font/UI/music/master identities, all four BT709 limited-range tags, AAC48k stereo and MP4faststart. No unexpected near-black interval. All six previous movie hashes remain unchanged.

New audio uses Backbay Lounge by Kevin MacLeod, edited 16–36s, CC BY4.0 with attribution in accompanying post/description/source credits. Voice EQ reduces520Hz boxiness, adds restrained3kHz presence, gentle de-essing and compression. Music is closer to voice (measured 8.50–11.69dBRMS separation versus v6's roughly12dB target), with smoother speech ducking. Delivered audio measures−15.37 LUFS/−1.97 dBTP, no voice overlap and2.3355s tail. Narration is reused byte-identically, not regenerated or sped up.

These are measured checks and sampled agent visual review. Full subjective listening and human continuous playback remain unassessed; the operator should audition the final video before posting. Required track attribution belongs with the posted video, not in its picture. No app/contract/signing/social/submission action occurred.
