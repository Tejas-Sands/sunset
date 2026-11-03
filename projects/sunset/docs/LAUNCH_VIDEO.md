# SUNSET launch video — current kinetic cut

The current X launch film is **v2: 30 seconds, 1920×1080 at 30fps, about 3 MB**. It replaces the earlier 82-second narrated-card format for the public launch. The original film and its evidence are preserved as v1.

## Watch and post

From the repository root:

```sh
xdg-open .publication/sunset-launch-v2/sunset-launch-v2.mp4
```

The ignored local delivery directory `.publication/sunset-launch-v2/` contains:

- `sunset-launch-v2.mp4` — the current video to upload natively to X.
- `sunset-launch-v2-poster.png` — cover image.
- `sunset-launch-v2.srt` — exact six-phrase subtitles; captions are also visible in the film.
- `full-motion-contact-sheet.jpg`, decoded review frames, `media-qa.json`, `media-provenance.json` and `CREDITS.md`.
- `sunset-motion-proof.mp4` — the separate 9.6-second style test.

Use the [current X post copy](../media/launch-v2/x-post.txt). Preview the film with sound and in a phone-sized player before posting; perceptual listening was unavailable to the tools. The edit uses 40 words of AI narration with deliberate gaps, independent type/artwork/UI layers, masks, camera movement and original 128 BPM sound design. The app moments show a real answer/feedback state and a retained offline game rather than a full protocol walkthrough.

## Why this format fits

The [official event guidance](https://nearhackathon.com/HACKATHON.md) asks for a complete user action with a visible result and discourages long introductions, architecture slides and setup. It does not require a full end-to-end workflow or prescribe a minimum clip duration. The main answer-selection/feedback moment supplies that visible result. The post must say it was built at NEAR HACKATHON, include @NEARProtocol and #NEARHackathon, and attach the demo media. The provided copy includes those details and NEAR’s concrete release/payout role.

The chosen 30-second length is a creative decision. It also fits the current [non-Premium X upload limits](https://help.x.com/en/using-x/x-videos) of 140 seconds and 512 MB. Keep the existing Vercel URL; no domain purchase or paid renderer is needed.

[Reference research](../media/launch-v2/RESEARCH.md) explains the Brag examples actually inspected, the written primary sources, the problem with the v1 renderer and the replacement’s motion grammar. [Source/edit recipe](../media/launch-v2/README.md) and [current media verification](../evidence/launch-video-v2.json) identify the exact film.

## Truthful scope

The UI pixels come from the [verified hosted/offline captures](../evidence/browser-showcase.json). Pointer actions are choreographed replays of the recorded answer and download actions; the HTML tile and copy fan are illustrations. This is an edited launch film, not an uninterrupted screen recording. No financial browser action, new wallet feature, adoption claim or new onchain event is invented. The underlying [testnet payout and stewardship evidence](../evidence/testnet-showcase.json) remains unchanged.

V1 stays in `.publication/sunset-launch-v1/render/` with its [original source](../media/launch/README.md) and [historical media evidence](../evidence/launch-video.json). Both actual expiry refunds, failure/max-state protocol tests and independent human validation remain open; the current trailer omits those demonstrations.

No social post or final submission has been sent by the assistant. After the human posts the video, retain its public X URL for the [unsubmitted draft](SUBMISSION_DRAFT.json), along with actual team/contact/payout details and approval of the final submission payload. Keep the hosted demo available through the event’s judging period.
