# SUNSET — Free didn't make itself

The approved 29.5-second story follows the work behind a free resource, sponsorship of its prepared public release, creator payment and genuine local reader use. [Script](SCRIPT.md) and [motion direction](MOTION.md) preserve the creative brief. Approval of that brief is separate from approval of the finished film.

This version uses the actual local **HyperFrames 0.9.16** engine and **GSAP 3.15.1**, following the pinned Brag project workflow. Independent paper/type layers, CSS perspective cameras, SVG drawing, a page hinge and selective deterministic Canvas accents supply the motion. This is authored 2D/2.5D animation; it does not use a physical soft-body solver or Three.js. No reference pictures or audio, finished earlier films, generated voice, product URL or attribution block enter the picture.

## Production and review

Delivery: `.publication/sunset-launch-v16/sunset-launch-hyperframes-final.mp4` — **29.5 seconds, 1920×1080, 30 fps**, H.264/BT.709, stereo AAC, 35,937,445 bytes. SHA-256: `76c7a4b8223aa982ea186164a7d2b0e05854e3835754208f649e825bbc30819e`. A separate poster is `.publication/sunset-launch-v16/poster-final.png`; the sunset remains the opening rather than being replaced by a poster.

The actual engine check passes with zero errors; 29 retained warnings cover deliberate animation/art-layout choices and the short lesson phrase. Full video/audio decode, all 885 frames, exact inputs, colour/cadence/faststart and all 81 native-reader comparisons pass. Encoded sound measures −15.1 LUFS and −2.3 dBTP. Both the small checkbox and its opposite state are compared, rather than allowing a mostly white crop to mask the wrong state. Sixteen earlier films and the initial V16 full export remain unchanged.

[Review](REVIEW.md), [artifact evidence](../../evidence/launch-video-v16.json) and [production plan](PLAN.md) separate those technical checks from decoded motion review and operator creative approval. The first full V16 export caught an unreadable funding headline over the moving cream cover; a bounded glyph-edge correction was checked in actual preview and encoded frames. Earlier portal, handoff, copy and portrait-plane issues were also corrected through actual sequence review. V15 remains preserved with its explicit operator rejection. Human continuous playback/listening and approval of the finished V16 film are not claimed.

Finance is labelled **NEAR testnet · illustration**. A completed target and timely matching-key release create credit; a separate withdrawal and confirmation precede Paid. This is an illustrated success path, with no new transaction. Conditional refund claims remain in the product documentation rather than becoming another chapter.

The 16.4–19.1s insert uses the existing downloaded Open-source Maintainer Handbook, source interval 0–2.7s at 1×. Two genuine native PNG states preserve the actual checkbox input and checked result timing. It is not continuous browser video, a new funded release, a reload demonstration, or proof that the handbook's underlying procedure was performed. The browser was offline before the local file opened; this does not mean initial resource recovery works without a network. Share means redistributing the licensed copy.

## Source and local reproduction

[film.html](film.html), [film.css](film.css) and [film.js](film.js) are the editable composition. [pipeline.py](pipeline.py) stages a self-contained HTML file with local assets, then invokes the pinned engine. It refuses existing output/staging paths and checks the identities of the prepared document, toolchain lock, wrapper and assets. [audio.py](audio.py) builds the licensed instrumental/recorded-Foley master. [verify.py](verify.py) checks the actual encoded movie and all 81 reader frames, including the small checkbox against both possible states.

These commands are **video-production tools**, not SUNSET user steps. Run from the repository root, using a fresh destination for every new revision:

```sh
python projects/sunset/media/launch-v16/pipeline.py prepare --composition .publication/sunset-launch-v16/composition-new
python projects/sunset/media/launch-v16/pipeline.py check --composition .publication/sunset-launch-v16/composition-new --output .publication/sunset-launch-v16/check-new.json
python projects/sunset/media/launch-v16/pipeline.py proof --composition .publication/sunset-launch-v16/composition-new --end 7 --output .publication/sunset-launch-v16/opening-new.mp4
python projects/sunset/media/launch-v16/pipeline.py render --composition .publication/sunset-launch-v16/composition-new --output .publication/sunset-launch-v16/sunset-new.mp4
```

The scripts use this workspace's ignored local toolchain/assets; a fresh source clone needs those inputs restored first. Required tools are Python 3.11+, Node, FFmpeg/FFprobe, HyperFrames 0.9.16, GSAP 3.15.1, and the engine's compatible local Chrome. Run Python without optimization: the production and verification tools reject `-O`/`-OO` because their assertion gates must execute. The audio builder additionally uses NumPy and retained V10 helpers. Local Nimbus Sans OTFs come from `/usr/share/fonts/opentype/urw-base35/`. Original artwork comes from the V13/V14 ignored assets; the genuine reader PNGs and capture manifest come from V15. The rendered staging manifest records their exact paths and hashes. Dependencies, browser, model-free local configuration, fonts, recordings and media remain ignored; no global login or shared account setup is required.

For documentary verification, collect frame-by-frame placements from the **compiled HyperFrames preview**, after `__player.renderSeek(t, {exact:true})` and its seek barrier, rather than a separate HTML page or invented geometry. The verifier accepts that JSON through `--geometry`; see its docstring for the schema. Run it against the completed MP4 and exact prepared composition with a fresh report directory.

[Credits](CREDITS.md) retain licenses and modifications. [Main post](x-post.txt) and [credit reply](x-reply-credits.txt) are drafts. No application, contract, resource, campaign, signer, deployment, public post or submission is changed by this media batch. The operator pushes verified local source commits.
