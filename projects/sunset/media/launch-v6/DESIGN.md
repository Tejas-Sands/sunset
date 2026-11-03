---
colors:
  cream: "#FFF3DD"
  ink: "#203B36"
  coral: "#E45B35"
  cobalt: "#244DDD"
  mint: "#CBE5D5"
  butter: "#F2D267"
typography:
  display: "Bricolage Grotesque"
  display_weight: 800
  display_optical_size: 96
  display_width: 100
  captions: "Space Grotesk"
  caption_weight: 600
format: "1920×1080, 30fps"
timing: "Provisional until the new relaxed narration is measured"
---

# SUNSET v6 — warm, playful, flat motion

The user rejected v5's dark metal and formal delivery as serious and scary. Their replacement direction is explicit: chill narration, fun kinetic 2D objects and expressive fonts. This is a change of visual medium, not another lighting pass. The original warm SUNSET mark and truthful public-learning story stay.

The latest operator direction is to **start with a sunset, then bring in the kinetic jazz**. Open on a real flat sunset/horizon for about 1.3 seconds: a warm coral disk sinks behind an ink horizon on cream, with two clean horizontal bands. The sunset becomes the original sun geometry, then its disk/stripes expand into the first word and the flat-shape world. Keep that opening simple enough to recognise immediately; do not substitute an isolated logo/title card.

The picture should feel like a clever animated poster: generous cream, confident ink, flat coral suns, mint paper, cobalt type and moving cutout shapes. Large mixed-case letters have personality. Objects are graphic pieces on the same plane: circles, flat keys, arrows, paper packs and copy fans. No metallic highlights, glass, 3D camera, menacing black stage, warning sirens or repeated left-heading/right-object chapters. Fun comes from composition, timing and shape transformations; no emoji faces, classroom stickers or constant rubbery bouncing.

## Fonts and colour

The font files are original unmodified variable TrueType downloads from exact commits in the official Google Fonts repository, both SIL OFL 1.1. [Provenance](fonts-provenance.json) contains exact URLs, bytes, SHA-256, cached license identity and Pillow axis tests. Generated fonts and font proof remain ignored.

- Display: Bricolage Grotesque, usually weight 800, optical 96, width 100. **Pillow axis order is Optical size, Weight, Width**, so use `[96, 800, 100]`. The file-name order is different. Lowering width to 85–95 can be used deliberately for an oversized transition; required phrases land at one fixed width for reading.
- Captions: Space Grotesk 600 (`[600]`). Its clean shapes balance the heavy, characterful display; it is supporting type, not the film's visual identity.
- At 1080p, aim for display 140–220px, secondary line 76–108px and exact captions 52–58px. Adapt size to the real bounding box rather than clipping a required word. At 360px player width, a 156px title appears about 29px and a 54px caption about 10px.
- Essential type pairs measured in linear sRGB: ink/cream 10.985:1; cream/cobalt 6.010:1; ink/mint 9.026:1; ink/butter 8.154:1. Coral/cream 3.270:1 and ink/coral 3.360:1 are unsuitable for essential text under the 4.5:1 production target. Coral is a moving shape/accent; protect words with cream or ink planes when a coral object fills the frame.
- Do not put big required words on top of detailed resource art. Titles may touch/overlap decorative cutouts during transition, then occupy clear negative space for at least 0.3 seconds per word plus 0.5 seconds. Captions retain their own lower safe band.

## Six-beat picture map

These ranges are provisional, not an instruction to compress or stretch the new voice. Root will replace them with the actual measured phrase boundaries.

| Beat | Approximate place | Picture and motion | Readable landing |
| --- | --- | --- | --- |
| Learning sticks around | 0–3.4s | First ~1.3 seconds: a warm flat sun sets behind a clear horizon. Its disk and horizontal stripes become the SUNSET graphic language; then large independent letters and a paper corner sweep in, and the paper fans into retained copies. | A short mixed-case premise, centred or full-width. Never a logo-only opening. |
| Fund it together | 3.4–7.2s | A sponsor dot becomes a full cobalt field; several flat coloured dots converge into the same paper pack. An oversized word passes through a crop mask and resolves into a differently placed title. | Communities fund a pack through NEAR escrow. No invented money value or wallet chrome. |
| Key, then creator | 7.2–12.5s | A flat key travels through the pack's cutout slot. Its long bar wipes the whole canvas to butter; a payout arrow carries a dot toward the creator label. Type shifts from wide to stacked as the object crosses frame. | On-time matching key, then creator withdrawal as a separate action. No automatic-money-transfer claim. |
| Refund route | 12.5–16.5s | Mint stage, an open curved arrow and returning sponsor dots. One brisk direction reversal replaces a failure alarm or scary timer. | Sponsors can claim refunds when the relevant deadline is missed. |
| A real retained copy | 16.5–20.5s | The flat pack grows into a literal actual Play/Download button-row crop; a circular wipe reveals the genuine downloaded offline resource. Keep this proof brief and crisp. | Exact download/offline captions and genuine labels. No quiz walkthrough or fabricated screen. |
| Keep and share | Final 4–5s | Copies spread across the canvas and become the original flat sun mark. Final type lands on cream with a fixed URL; peripheral pieces exit cleanly. | Support once. Share forever. Final URL holds 3 seconds. Include required music credit without covering the last caption. |

## Three reference techniques translated into 2D

1. **LILIUM 0.83–2.1s: regional image substitution and macro strip collage.** Keep one SUNSET sun/pack silhouette and briefly replace its interior with mint/cobalt/cream fragments. Crop, offset and reassemble the flat pieces; do not borrow the reference flower or frames. This creates motion inside the object without adding 3D.
2. **LILIUM 3.5–4.8s: individual glyph assembly into oversized full-frame type.** Letters can travel separately through masks, become a full readable phrase, then exit together. The final complete phrase gets a genuine static reading window; scattered letters are punctuation, not the only presentation of a claim.
3. **SaasWAVE 18.63–21.33s: the object becomes the actual interface.** Translate its folder/file handoff into flat paper fans, an edge-matched crop and a circular/shape wipe into real source pixels. Source buttons and labels retain their meaning. This earns the UI cut and avoids a pasted screenshot slide.

The local reference sheets were inspected directly at `reference-study/lilium/contact-10fps.jpg` and `reference-study/saaswave/contact-03.jpg`. The observations above concern picture/edit grammar only. No reference footage, sampled image or audio is an output asset.

## Motion and voice discipline

Fast handoffs take roughly 0.3–0.6 seconds, with varied roles: long-tailed arrivals, faster exits, a whip, an object-colour flood and a shape-matched wipe. Brief streak duplicates may follow an object's real movement; required text itself stays sharp while read. Use one controlled overshoot at an object landing, not bounce on everything. A landed title is static while another meaningful object continues the action. No background breathing/pulsing loop standing in for an actual transition.

The voice should sound like a relaxed person explaining a good idea: friendly male delivery, natural phrasing and a slight smile, no dramatic low register, trailer pauses, promotional shout or toy presenter cadence. Root/audio owner chooses a fresh pretrained voice from actual short previews. Music should be a light laidback instrumental groove, quieter under speech, with proper source/license attribution. Visual fun does not require chirps, coin dings or a children's tune.

## Production boundary

Use original code-native flat shapes, original mark/landscape and fresh verified DPR2 product images. Render all graphic/text layers natively at 1080p/30fps; no v4 JPEG/interpolation path and no 3D assets from v5. Genuine UI crops stay at or below source-pixel size. Actual narration timing sets the edit. Preserve all previous movies. Downloads, fonts, models, audio and final video stay ignored; only original recipes, design notes and public evidence are committed by root.

Craft sources read for this revision: local Brand typography specification and current official HyperFrames `references/look.md`, `motion.md` and `story.md`, selectively applied to the existing Pillow workflow. The current user correction overrides v5's sober material grammar. No framework migration or new account connection is required.
