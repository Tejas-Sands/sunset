# SUNSET: direct Intelligence motion match

This private style experiment follows the supplied Intelligence reference’s exact native frame contract. It keeps the stable center, moving circular image windows, abrupt image/point/type handoffs, regular upright lettering, broad white field, character deletion and bracket reflow. It adapts the message to `[FREE] → [FAIR] → [PAID] → [FREE. CREATORS PAID.]`.

The supplied source is **1276×720, 18 fps, 195 decoded frames, 10.833333 seconds of picture**. The study is **1920×1080, 18 fps, 195 frames**, with uniform 1.5× geometry and three white pixels at each side. The earlier 30 fps production specification was explicitly replaced for this direct native comparison. Each source frame maps to the identically numbered output frame. The source audio is excluded; the study is silent.

## Frame contract

| Native frames | Time, seconds | Matched event |
| --- | --- | --- |
| 000–019 | 0.000–1.111 | Original creator work fills the image. Study identification stays in filenames and private review sheets. |
| 020–025 | 1.111–1.444 | Same work continues beneath a huge circular boundary clipped by the frame. Source top-edge wedge positions are approximately 13, 19, 26, 35, 49 and 72 px. |
| 026–046 | 1.444–2.611 | Abrupt handoff to a centered disc, source diameter ≈366 px, settling to ≈323 px. Pale dashed full-frame tangent guides follow the circle. |
| 047–068 | 2.611–3.833 | Hard cut to the creator portrait inside the unchanged mask and guides. |
| 069–090 | 3.833–5.056 | Hard cut to the working desk and drawn diagram. Late contraction reaches source diameter ≈276 px at f090. |
| 091–112 | 5.056–6.278 | Abrupt replacement with a source ≈22 px black point; all guides disappear. The point shrinks to ≈13 px. A brief coral accent and ≈7 output px downward motion finish this beat. |
| 113–129 | 6.278–7.222 | Centered regular `[FREE]`, coral letters settling black while black brackets close slightly. |
| 130–141 | 7.222–7.889 | Singleton F holds at the old word’s left anchor; FA appears, then FAI/FAIR, before characters delete back to F. Brackets expand monotonically, following the observed76→105→113→116→117px source progression with room for the longer SUNSET words. The remaining prefix follows the left bracket with a constant gap. |
| 142–161 | 7.889–9.000 | P replaces F and recenters; PA then PAID appears, settles black and holds. |
| 162–194 | 9.000–10.833 | Abrupt expansion to the final phrase’s width. Remaining letters reveal rightward through f167, brackets overshoot slightly then settle, and the complete phrase holds through f194. |

The point diameters, circle measurements and font proportions are approximate decoded-raster observations, not recovered authoring values. Exact font identity is unsupported. The study uses the installed Nimbus Sans regular face, 75 px with 0.90 horizontal proportion, approximately 55 px capital height. Brackets remain black. Word length changes final width without changing capital size. The longer SUNSET wording and the brief coral emphasis are deliberate message adaptations.

## Original imagery and motion

The first image uses the previously generated creator-at-work asset, close cropped around the work; portions of its generated torn boundary remain visible in the opening. Independently drawn ink and a pen tip change over time. The second uses only the top-left person from the newly generated four-person portrait atlas, composited on the generated workroom; the portrait and its lower work layer move separately. The third crops the workroom desk and adds a moving page and progressively drawn ink. Whole-image camera framing stays fixed during these windows.

These are authored illustrative animation composites, not recorded people, users, educational activity or financial footage. The new portrait/workroom prompt, source output identities and alpha details are in ignored `.publication/sunset-launch-v14/assets/provenance.json`; the older hand-work provenance remains in `.publication/sunset-launch-v13/assets/creator-provenance.json`. The renderer records the exact used image and font SHA-256 hashes in its private manifest. It neither reads nor reuses reference pixels during film rendering. Only the explicitly named local comparison-sheet function opens the reference frame directory.

This is a direct motion comparison, not a new full launch film, resource, product feature, campaign, deployment or payment claim. It does not establish operator approval, natural filmed motion, a recovered source font, continuous human playback assessment or audience response.

## Private review and reproduction

Run from the repository root with installed Python, Pillow, NumPy and FFmpeg; no new dependencies are needed:

```sh
python3 projects/sunset/media/launch-v14/minimal-match.py --gates
# After the native keypose and critical-strip gate:
python3 projects/sunset/media/launch-v14/minimal-match.py --frames
python3 projects/sunset/media/launch-v14/minimal-match.py --encode
```

All outputs stay in ignored `.publication/sunset-launch-v14/minimal/`. Contiguous original window-motion GIFs (GIF timing rounds to50/60ms; the MP4 retains exact18fps), native review PNGs and clearly labelled private side-by-side sheets cover eight main keyposes plus f025/026, f090/091, f112/113, the complete f130–144 deletion/replacement passage and f161–168 phrase expansion. Reference pixels appear only on these private comparison sheets and must not be published as original assets.

The encode command refuses to overwrite an existing movie. It produces one silent CRF14 H.264/yuv420p limited-range BT709/faststart MP4, fully decodes it, checks dimensions/cadence/frame count/no audio, checks `moov` before `mdat`, and writes the exact probe/size/SHA-256 to `verification.json`. A passing codec check is not a claim that the operator accepts the creative result.


## Delivered experiment and metadata repair

The approved movie is private `sunset-minimal-motion-match.mp4`: **1,292,902 bytes**, SHA-256 `c783fa9078a1ffb76d9b2f3517caef3d95efa1f746c352f82688c0b4bf7b5b57`. Full decode passed195 frames at18fps,1920×1080,10.833333s, H.264/yuv420p, limited range, complete BT709 primaries/transfer/matrix, faststart and no audio.

There was exactly one image encode. Its initial output had BT709 matrix/limited-range tags but unspecified primaries and transfer despite the output CLI flags. A stream-copy repair applied `h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0`, explicit BT709 container tags and faststart. **All195 decoded frame MD5 hashes matched before and after repair**. The initial1292883-byte file's identity was `f59318d723d3a37716ee544f4228b16c435f912be5395798d04bb456716f4d73`; its original inode was not retained. Verification records distinguish the initial identity from the repaired final file.

The actual movie-render source SHA-256 is `672a5e1411f92d67d4911f7e6dcd3c03e3f75d5496f9056f747cd7825c88384c`. Its private source snapshot is `private-render-source-before-tagfix.py`. The post-repair reproduction source SHA-256 is `55094ba1d6e9c78b2cfd8fcae74fef01db8d18f5dcbc25ccf7666c3f13bfe854`; its only subsequent code change adds `setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709` after scale and assertions for all colour tags. This future reproduction correction was syntax checked; no second image encode was made.

Root and the independent style reviewer inspected source/keypose pairs, critical event strips, corrected deletion/phrase strips and consecutive local-work frames. The final actual decoded event/typing/phrase sheets were also inspected. The qualified gate establishes the reference-specific center/mask/point/type timing and authored local movement. Still-image layers replace natural footage; coral replaces source blue; the four-letter groups/final phrase are wider. Pixel-identical source footage/type and operator acceptance are not claimed.
