# SUNSET v16 credits and source identities

The 29.5-second soundtrack uses one continuous licensed instrumental performance and 30 placements of recorded paper/contact Foley. No narration, generated score, synthesized effect, chime, pillow recording or captured wallet/browser sound is used. Source media, analysis, stems and masters remain in ignored `.publication/` directories. Required music attribution belongs in the accompanying reply or video description, outside the picture.

**“Origami” by Scott Buckley — released under CC-BY 4.0. www.scottbuckley.com.au**

[Official track and download](https://www.scottbuckley.com.au/library/origami/), [artist's usage instructions](https://www.scottbuckley.com.au/library/using-this-music/), [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). Original full-mix MP3 SHA-256: `8b8edd81ee2110a62169b48e3233e1556c0f9de10003b21f41a28e5b4bcbfe14`.

Changes: continuous **32.18–61.68s** excerpt, EQ, smooth gain and stereo-width arrangement, fades, mixed recorded paper/contact Foley and mastering. The source performance has no music edits or jump cuts. The local source record retains the artist's upbeat electro-jazz/off-kilter-groove description. Measured energy onsets informed excerpt alignment; they do not establish a musical beat grid or perceptual listening. YouTube also requires the credit in the description.

Practical Foley uses the official Freesound HQ preview MP3s retained from V15, rather than the original uploaded WAVs. All three sources are [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/):

| Recording | Creator and source | Source MP3 SHA-256 |
| --- | --- | --- |
| Page Turn (1) | [OwlStorm / Ashe Kirk / Owlish Media](https://freesound.org/people/OwlStorm/sounds/151220/) | `41f51725007894483999812091faf74d0d341092c0a24c55c0778fe245ea45f4` |
| Page Turn (2) | [OwlStorm / Ashe Kirk / Owlish Media](https://freesound.org/people/OwlStorm/sounds/151221/) | `0e6737d635998d90f015249c0215691d3cb63d2ff37d49949914284160b6e9e0` |
| Mouse Clicks | [Breviceps](https://freesound.org/people/Breviceps/sounds/447938/) | `bbbddc66710313d67f0c8d8dc37f68c62728c041ccb3820f04c45554dd9f46e5` |

Recorded paper supports visible material crossings, ticket/deposit contacts, the matching key, credit slip, fresh page and sunset transformation. Dry recorded ticks support illustrated cap/stop/withdrawal/confirmation contacts and the actual checkbox-input time. These are added editorial sounds, not a wallet, blockchain or browser recording. Creator credit precedes the separate illustrated withdrawal, and successful confirmation precedes the paid state. No refund chapter or automatic refund sound is introduced.

The real-reader insert reuses the genuine V15 source interval **0–2.7s at 1×**, beginning at film 16.4s. Actual checkbox input maps to film **17.600145381–17.624610837s**, and the genuine checked capture maps to **17.873660363s**. A recorded editorial tick peaks at the real input time. No tick is added to suggest a separate browser confirmation. This interval contains no reload; saved progress is the genuine reader state. The local handbook is an example, not a newly funded resource. The unchanged source and offline-emulation scope remain in `.publication/sunset-launch-v15/capture/capture-provenance.json` and [V15 credits](../launch-v15/CREDITS.md).

[Audio builder](audio.py) reuses the existing V10 FFmpeg/NumPy helpers. `.publication/sunset-launch-v16/audio/` retains `mix.wav` (48 kHz stereo, 24-bit PCM, exactly 29.5 seconds), `music-arranged.wav`, `sfx.wav`, `mix-unmastered.wav`, an AAC round trip, `cue-manifest.json`, `source-provenance.json`, `source-onsets.json` and `qa.json`. The manifests retain exact source identities, measured cue placement and processing. QA records integrated loudness, true peak, per-second/section RMS and source/master/stem hashes. Automated audio checks do not claim human listening or creative approval.

The implemented picture uses original HTML/CSS/SVG layers, CSS perspective transforms and a Canvas 2D ink/smear overlay, driven by a seekable **GSAP 3.15.1** timeline and rendered with **HyperFrames 0.9.16**. The composition is 1920×1080 at 30 fps, with 885 frames over 29.5 seconds. Paper shapes, diagrams, tickets, the custody sleeve, key, creator-credit/withdrawal artwork, typography animation and SUNSET mark are project artwork. Financial passages carry **NEAR testnet · illustration**; they record no new signed action. The two supplied reference films informed motion direction; their pictures, audio, branding and character artwork are excluded.

The frozen `.publication/sunset-launch-v16/composition-delivery/source-manifest.json` identifies the implemented sources. The earlier `composition-release` and its first full MP4 remain preserved: actual encoded review found low funding-caption contrast, corrected only by adding a tight dark glyph edge and shadow before this delivery.

| Source | SHA-256 |
| --- | --- |
| [film.html](film.html) | `fc3b1abf50d91b964015de96328723441e42106710d503a84c42f756404c17e6` |
| [film.css](film.css) | `599afafd77ed0fe1bf3f41b4e0195bfa5e3cb1d68e869d2bdefdfd0f007cfa85` |
| [film.js](film.js) | `c0181918a0fc3c79b83ac346e2e07a423a13b0a60d8d71765b500a93af5eff9c` |
| Prepared `composition-delivery/index.html` | `67e922c7e7990586f992cbde0552645dd84166c801a93be53730ff5810096626` |

Three retained original bitmap illustrations supply the maker/workroom imagery. Their exact generation prompts are in [V14 assets](../launch-v14/ASSETS.md) and [V13 assets](../launch-v13/ASSETS.md). These fictional people and scenery were generated through the built-in imagegen tool for those earlier studies; they depict no actual SUNSET user, workshop or testimonial. V16 reuses the still images through cropping, layering, masking and transforms.

| Composition asset | Retained source | SHA-256 |
| --- | --- | --- |
| `creators.png` | `.publication/sunset-launch-v14/assets/creator-portrait.png` | `a68f23e7b9578f569cfdbaeb5bd2cef4efa31e8d3052f2ae4815ab5710d08d47` |
| `workroom.png` | `.publication/sunset-launch-v14/assets/workroom.png` | `5838dbf289d795b5e900e9d26241afc1c00fe1318ce81e808c79f1561bbc0465` |
| `hands.png` | `.publication/sunset-launch-v13/assets/creator-cutout.png` | `d88f268d9044448951d19b8bcc08018e906d1f7a7ae3b1e15675d7371926522f` |
| `unchecked.png` | `.publication/sunset-launch-v15/capture/unchecked.png` | `db312ca87fb82aeff8fbd2683bf8f46b4d2c65061a06ba6146688eef89e8b7e1` |
| `checked.png` | `.publication/sunset-launch-v15/capture/checked.png` | `3df2cdf571d86334dd0709ecc1a1c20dd0dfd0c589537666fe77b087ef219cfa` |

The two reader PNGs retain genuine browser pixels from the 17,862-byte downloaded **Open-source Maintainer Handbook**, SHA-256 `7133b9acd18dc6ee55256d817fbd7872e9e2ec4f2cd625a88fff6ab6b69a621a`. Its original content is CC0-1.0 and reader runtime is MIT. Browser offline emulation preceded file navigation; recorded checks report `file:`, `navigator.onLine=false` and zero resource loads. This is browser emulation. The source captures are held at their genuine elapsed timestamps; editorial cropping and framing add no invented UI or cursor. Checking the row demonstrates local reader state, without establishing performance of the handbook procedure. The authored ink/smear overlay is disabled during the real-reader passage.

Rendered lettering uses exactly three installed **URW Base35 Nimbus Sans** font files, copied unchanged into the ignored composition:

| Composition font | Original file under `/usr/share/fonts/opentype/urw-base35/` | SHA-256 |
| --- | --- | --- |
| `display.otf` | `NimbusSans-Bold.otf` | `7f33328e6b4d4cd21b45fa625791928c9407dc702db6780e56b09ca9a3ecaa67` |
| `display-italic.otf` | `NimbusSans-BoldItalic.otf` | `3f47fb34fcb7de09f8cbc9f305191340ddebf7a068419f4bb5f49287dea59b87` |
| `sans.otf` | `NimbusSans-Regular.otf` | `7c25be4d78155523080ab85b10277150657ff7dabbcad7037bdd536c9b6d0d08` |

The installed URW copyright record at `/usr/share/doc/fonts-urw-base35/copyright` identifies **AGPL-3 with Font exception**, copyright URW Software / URW++ Design & Development; [upstream font source](https://github.com/ArtifexSoftware/urw-base35-fonts). Font binaries remain in the ignored composition assets. The published film contains their rendered lettering.

The retained `assets/gsap.min.js` has SHA-256 `3d1bea374ab1b703cc5c4105358eec63c4465efdc573931dc116e34a0a190c1b`. Its header identifies **GSAP 3.15.1**, copyright 2026 GreenSock, author Jack Doyle, under the [GSAP Standard License](https://gsap.com/standard-license). The installed package records that same license. HyperFrames 0.9.16 records Apache-2.0 in its package metadata. The exact ignored toolchain lockfile has SHA-256 `6a889b2dc10c90b7223d5b2cb0273c23101f0ed34cd03a7de6c3173300a5e377`; the frozen manifest retains tool wrapper, source, capture and audio-QA identities. No font or toolchain dependency is added to the application.

The accompanying [main post](x-post.txt) links the recorded testnet demo and public repository; the [credit reply](x-reply-credits.txt) supplies the required music attribution and edit disclosure. Both are drafts for the operator to post. The picture contains no music-credit block or product URL.
