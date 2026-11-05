# The two exact references — every-frame study

The operator supplied `/home/citrux/Downloads/refs/drafff` and explicitly requested a frame-by-frame study of both videos. All **595 decoded frames** were extracted at native resolution and visually inspected through **21 complete indexed atlases**, with selected native enlargements. This is a new reference set, distinct from the earlier SaasWAVE/LILIUM study.

| Supplied file | Picture | Decoded frames | Exact source SHA-256 |
| --- | --- | --- | --- |
| feel good inc2.0… | 960×720, supplied20fps,20.000s | 400, f000–399 | `768e13d8359c7eb39b45c8cb2089b235e6fd675bd5325f16c95f913a4c200fa6` |
| when intelligence is everywhere… | 1276×720, supplied18fps,10.833333s | 195, f000–194 | `289999ba2aa77973d302be6d23414613d51b3f708df11be2f89d9a8cbbe6a699` |

The supplied rates establish file cadence, not original authoring rates. Container/audio tails extend beyond picture endpoints. Source files are unchanged. Reference frames/audio stay ignored and do not become SUNSET output assets.

## What the study found

- **Feel Good:** editorial mixed media—printed illustration, photographic space, device shots, collage, variable type, aggressive crops and brief blur/occlusion handoffs. Recurring portraits, grids and circles connect changing scenes. Near-black tail starts at f348/17.40s; it is not an instruction to append dead time to a launch film.
- **Intelligence:** stable focal centre, moving footage inside a geometric mask, abrupt scale/content handoffs, then sparse bracketed type. The major image-to-small-circle handoff is f026/1.444s; image-to-point is f091/5.056s; point-to-type is f113/6.278s. Substantial quiet holds matter as much as the short transitions.
- **Shared principle:** change what the viewer understands while preserving recognition. The mask, printed edge, subject, focal location or word acts as a bridge. Constant movement around one unchanged object misses this grammar.
- **SUNSET correction:** make useful work and the human maker the visual subjects. Keep the creator-compensation why, whole readable phrases and purposeful depth. Use compositional variety, original collage surfaces and semantic mask/type handoffs rather than a persistent orbiting padded book and fixed subtitle plate.

[Feel Good frame ranges and mechanics](FEEL_GOOD_STUDY.md) cover every source frame in17 contiguous event ranges. [Intelligence frame ranges and mechanics](INTELLIGENCE_STUDY.md) cover every source frame in10 ranges. [SUNSET translation](SUNSET_TRANSLATION.md) separates observed facts from one proposed original eight-second treatment. Neither editing software, recovered project structure nor perceptual audio synchronisation is claimed.

## Inspectable local artifacts

Open `.publication/sunset-reference-study-20261105/reference-study.html` in a browser to step through every native frame with PTS, shot notes, source identity and image-change/audio-energy curves. It has previous/next controls, a seek range, keyboard stepping and an original-file link. Browser QA exercised both references, actual frame stepping and the final intelligence frame; the native image widths were960/1276 with720px height. No product or financial browser state was touched.

All595 frame hashes/PTS are in the two `index.json` files. Twenty-one atlases, selected overview sheets, native PNGs, audio RMS/positive-flux measurements and viewer QA remain in the ignored study directory. All27 note ranges were checked for contiguous coverage. Image-change/flux measurements nominate inspection points; they are not certified cuts, beat detections or listening results.

`extract.py` reproduces native extraction and atlases using the two local inputs, installed FFmpeg/Pillow/numpy, without temporal resampling. `viewer.py` builds the local viewer from those exact manifests and the annotated Markdown tables. No package installation or hosted service is needed. These are analysis tools, not SUNSET reader requirements.
