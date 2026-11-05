# SUNSET: eight-second collage motion study

This private throwaway style prototype reconstructs the **first eight seconds** of the supplied Feel Good reference, with original SUNSET photo/print artwork. It is not a product demonstration or evidence of protocol execution. The source picture is 960×720 at 20 fps; the proof is 1920×1440 at the same 20 fps, 160 frames, eight seconds, silent. Its picture aperture changes by chapter like the source: source upper/lower bars are approximately 70 px for grid/macros/type/photo/corridor and 34 px for mustard/strips/HUD, represented by output bars of 140 px and 68 px respectively.

Eight separate material chapters follow the actual source frames. Their internal changes retain the reference's rapid arrivals and short landings. This deliberately replaces the three-scene fixed-heading structure of v13. Foreground text, portrait prints, letter slips, arrows, ribbons, photographic environment and HUD are independent layers.

| Source frames / exact seconds | Motion and original translation |
| --- | --- |
| 000–017 / 0.00–0.85 | Four photo prints assemble independently, contract at 009, and tear locally at 015–017. |
| 018–040 / 0.90–2.00 | Tilted camera dives through two near-full portrait prints; smears at 019 and 029–031. |
| 041–058 / 2.05–2.90 | Print drops below crop. Physical oblique FREE/PAID word units assemble at 043–046, thin rust arrows and miniature panels accumulate through 049, another arrow crosses at 054, directional departure at 058. |
| 059–080 / 2.95–4.00 | Mustard ground, creator hands, independent mixed letter slips at 061–067, thick foreground arrows at 064/069, separate dotted depth ribbons, sideways travel at 072, tall strips assemble at 073–076, radial departure at 080. |
| 081–091 / 4.05–4.55 | Four tall printed portrait strips, caution tape and scratch lines. Pale near-plane occlusion at 087, black sweep at 088, blurred return at 089, white flash at 090–091. |
| 092–108 / 4.60–5.40 | Photographic workroom with separate magazine/paper planes and foreground work crates. Stack builds at 093–099; camera pulls back and changes focus at 107–108. |
| 109–124 / 5.45–6.20 | Defocused foreground print crosses at 109; narrow portrait and side-wall print drift at separate depths in the workroom. Small word stack builds at 113–117; dark dip at 124. |
| 125–159 / 6.25–7.95 | Halftone/dark entry, camera HUD, face planes occupy screen at 128, 135, 145. Whips and focus-square flashes at 133–134 and 141–142. Pullback at 150–155 exposes the overlapping portrait stack. Ring 156, dot texture 157, spot 159. |

The renderer records 74 source-timed micro-events in the private manifest. Rendering uses independent raster planes projected through 3D rotations/translation, inverse perspective homographies, per-plane depth, selective blur, directional smears and focus overlays. No reference image or audio is loaded by the proof rendering path. Only the separately labelled `--compare` path opens supplied reference frames for private analysis.

Export uses explicit full-range RGB to limited-range BT.709 conversion, BT.709 metadata, H.264 CRF 14, and no picture footer. The resulting filename is `sunset-collage-motion-match-8s.mp4`. Color conversion/codec validation does not establish visual fidelity.

Run from the repository root after the two generated original assets exist:

```sh
python projects/sunset/media/launch-v14/collage-match.py --gate --compare
python projects/sunset/media/launch-v14/collage-match.py --render
```

All generated media and manifests remain under ignored `.publication/sunset-launch-v14/collage/`. The first command makes native keyposes and a transition contact sheet before a complete encode. The second makes the silent proof only after visual review.

The root and independent reviewer found all eight chapters recognizably related to the source at the keypose/transition gate. This is a reviewable direct motion test, **not an exact or finished match**. At source f052, the replacement word mass is thinner, narrower and shifted farther right than the reference's heavy oblique type. At f117, the photo-head/outlined-vector body and projected room walls are flatter and less integrated than the reference's richly illustrated full figure and photographic corridor. Original photographic people also differ deliberately from the supplied illustrated characters. These are visible reconstruction limits, not claims that matching timing or export settings resolves them. Gate review examined rendered native stills and transition sheets; it did not establish continuous-playback approval.
