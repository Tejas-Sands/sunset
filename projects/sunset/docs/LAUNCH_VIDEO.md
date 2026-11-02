# SUNSET launch video and post

Keep `https://sunset-lemon.vercel.app`. The existing hosted site works; a custom domain adds nothing required for this demonstration.

The delivery is an **82-second, 1920×1080 H.264/AAC MP4**, about **11.3 MB**, with local AI narration, burned-in captions, original ambient chords, the existing SUNSET identity and genuine product captures. The film shows the successful 0.1-testNEAR release/payout, real offline gameplay and stewardship mirror handover. The refund card describes the contract rule and clearly says that a live expiry-refund run is not shown. The film is an edited sequence of genuine captures rather than a continuous screen recording.

## Open the delivery

Generated media stays in the ignored repository-root directory `.publication/sunset-launch-v1/render/`:

- `sunset-launch.mp4` — upload this video.
- `sunset-launch-poster.png` — cover image.
- `sunset-launch.srt` — matching subtitle sidecar; the video already has visible captions.
- `contact-sheet.jpg`, `media-qa.json`, `media-provenance.json`, `sunset-launch-credits.md` — review and provenance.

From the repository root on the Linux laptop:

```sh
xdg-open .publication/sunset-launch-v1/render/sunset-launch.mp4
```

Listen through once and check pacing on a phone before posting. The tools verified codecs, duration, captions, keyframes, full decode, no black frames, loudness and peak levels; perceptual listening was unavailable. Do not replace this with a claim that listening was verified.

## Publish on X

Use [the main post](../media/launch/x-post.txt), attach the MP4 as a native video, and optionally follow with [the five-post thread](../media/launch/x-thread.txt). [The pitch and launch story](../media/launch/pitch.md) provide the longer narrative. Each draft post fits 280 weighted characters, with URLs treated as 23 characters; confirm the composer preview before sending.

The [official event instructions](https://nearhackathon.com/HACKATHON.md) ask the human to post the demo, explicitly say it was built at NEAR HACKATHON, include `@NEARProtocol` and `#NEARHackathon`, and attach the video or screenshots. The supplied main post includes those details. The current [X upload guidance](https://help.x.com/en/using-x/x-videos) permits non-Premium uploads up to 140 seconds and 512 MB; this export is within both limits. No paid X plan, domain or rendering service is needed for this delivery.

After posting, retain the actual public X post URL. The [unsubmitted draft](SUBMISSION_DRAFT.json) still needs that URL, real team/contact information, the prize payout account and explicit approval of the final submission payload. The repository is public at `https://github.com/Tejas-Sands/sunset`. Keep the hosted demo available through 18 November, preferably 25 November, as requested by the event instructions.

## Proof and scope

[Live showcase evidence](../evidence/testnet-showcase.json) records eleven finalized transactions: ten successful steps and the intentional rejected former-steward edit. It includes the native 0.1-testNEAR creator transfer, successful withdrawal callback, pending-null account state, NFT handover and accepted new mirror.

[Browser evidence](../evidence/browser-showcase.json) records actual hosted reader/hash verification, original/mirror recovery and identical browser downloads. A fresh browser had offline emulation enabled before opening the downloaded file, completed all five questions and restarted with no resource requests. Offline mobile layout passed at 390×844. No operating-system network-adapter toggle, mobile-homepage pass, broad device audit or browser wallet signing is claimed.

All demo roles share one operator. Real expiry refunds, maximum-state/callback-failure protocol checks, independent educator review and sponsor demand remain open. The contract retains full-access upgrade control. A second path on the same Vercel host demonstrates mirror selection rather than independent hosting.

[Media verification](../evidence/launch-video.json) · [renderer and source](../media/launch/README.md). The model, voice-bank, raw audio/video and browser captures stay local in the ignored delivery directory. No wallet keys or private release backups belong in this package.
