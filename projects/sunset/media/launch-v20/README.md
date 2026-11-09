# SUNSET V20 — visible reader value, creator continuation

The 34-second finishing cut keeps the approved script, original logo and V19's refined key/card animation. The weak title-only reader insert becomes a real retained handbook excerpt with clear benefits: **No account. No wallet. Keep the file.** The same maker returns to create again, **FREE TO USE / CREATOR PAID** remain visible together, and the ending gives a readable testnet demo URL. Narration remains deferred.

Movie: `.publication/sunset-launch-v20/sunset-launch-v20.mp4` — 1920×1080, 30fps, 1,020 frames. Poster: `.publication/sunset-launch-v20/poster.png`. [Script](SCRIPT.md), [design](DESIGN.md), [review](REVIEW.md), [credits](CREDITS.md) and [delivery evidence](../../evidence/launch-video-v20.json) define the exact scope and checks.

This is a finishing edit of the exact verified V19 HyperFrames movie. Original animation retains its cadence; explicit holds add 0.7s to ready credit, 0.6s to Paid and 1s to the ending. New reader/creator/payoff graphics render locally with Pillow/FFmpeg. The current sandbox blocks browser/render servers, so no new HyperFrames render or browser capture is claimed. All earlier movies remain intact.

The native paragraph comes from the previously verified downloaded handbook with browser offline emulation enabled before file load. It is a still excerpt, not a new click/download, continuous footage or completed handbook procedure. No search, checklist or terminal command appears. The paragraph/provenance line is supporting desktop detail; the large headline and three benefits carry the phone message. Moving copies are editorial illustration. Fictional maker imagery shows intended value, not adoption or livelihood evidence.

Release credit, deliberate claim, successful confirmation and Paid remain separate and ordered. Finance stays the existing labelled testnet illustration. The existing handbook is not newly funded and is not the resource named by the old finalized testnet campaign. No app, resource, contract, transaction, signer, hosting, shared-auth, public post or submission changed.

Reproduce from the repository root with Python 3.11+, installed Pillow/NumPy and FFmpeg/FFprobe:

```sh
python3 projects/sunset/media/launch-v20/finish.py check
python3 projects/sunset/media/launch-v20/finish.py stills
python3 projects/sunset/media/launch-v20/audio.py
python3 projects/sunset/media/launch-v20/finish.py render
python3 projects/sunset/media/launch-v20/verify.py
```

Use Python without optimization. Movie/audio/verification outputs refuse overwrites; preserve old outputs before a deliberate fresh run. A fresh clone needs the ignored V19 master, V13/V14 assets, V15 native capture and provenance, retained Geist TTF and original music/Foley restored. Source identities are recorded in the generated manifest; these are production dependencies, not SUNSET user requirements.

`finish.py` records every output frame's source. `verify.py` checks the actual full decode, each retained animation/brand frame, all 126 native excerpt frames, colour tags, cadence, faststart, encoded loudness and all 20 prior canonical movies. H.264 VUI colour tags are explicitly finalized by stream copy; the first export's missing primaries/transfer tags were caught by the verifier and repaired without another pixel encode.

The [post draft](x-post.txt) and [required music-credit reply](x-reply-credits.txt) remain unposted. All generated media stay ignored. Source changes are committed locally; the operator pushes from the root with `git --git-dir=.sunset-git --work-tree=. push origin main`.
