# SUNSET v9 sound credits

This 56-second export contains instrumental music and licensed recordings of physical objects. It contains no narration, generated speech, voice samples, TTS runtime or voice model. A later human recording needs a separate mix.

Music: **Backbay Lounge** by **Kevin MacLeod** (incompetech.com), **Creative Commons Attribution 4.0 International**.

- [Artist track](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1700068), ISRC USUAN1700068; [artist detail](https://remote.incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1700068).
- [License](https://creativecommons.org/licenses/by/4.0/); [artist licensing](https://incompetech.com/music/royalty-free/licenses/).
- Retained source SHA-256: `9567e71a213b0026341b2c0ecd226950e7653abd235cf520fb9aee4247d74d96`.
- Changes: edited 16–72 second excerpt, EQ, smooth gain and stereo-width automation, fades and loudness mastering. No speech ducking. The continuous performance starts restrained, opens with the matching-key release, lowers for the genuine UI action, rises through retained copies, then fades under the mark.

Use this music credit in the accompanying public post/video description:

> Backbay Lounge by Kevin MacLeod (incompetech.com), licensed under Creative Commons Attribution 4.0. Edited excerpt, EQ, gain/stereo-width automation, fades and mastering. https://creativecommons.org/licenses/by/4.0/

The required attribution belongs in that description/post and these source credits. No credit block is required in the picture.

Recorded Foley, each verified on its primary Freesound source page as **CC0 1.0**:

| Recording | Author | Use |
| --- | --- | --- |
| [Page Turn (1)](https://freesound.org/people/OwlStorm/sounds/151220/) | OwlStorm / Ashe Kirk / Owlish Media | Foreground pack flip and two outward copy movements |
| [Page Turn (2)](https://freesound.org/people/OwlStorm/sounds/151221/) | OwlStorm / Ashe Kirk / Owlish Media | Initial page handoff and a different take for the second copy |
| [Metallic latch release.wav](https://freesound.org/people/Crinkem/sounds/481789/) | Crinkem | Matching-key contact; the source describes a physical door latch recorded on Sony PCM-A10 |
| [Mouse clicks](https://freesound.org/people/Breviceps/sounds/447938/) | Breviceps | One isolated recorded mouse click at the first captured actual offline answer result |

[CC0 1.0 license](https://creativecommons.org/publicdomain/zero/1.0/). Courtesy Foley credit: “Recorded page Foley: OwlStorm / Ashe Kirk; latch: Crinkem; mouse: Breviceps, via Freesound (CC0).” Attribution is optional for these CC0 recordings. The official HQ MP3 previews were downloaded, not the original uploaded WAV files. Source URLs, hashes and saved primary license-page snapshots are recorded in `sound-cues.json` and ignored audio-research provenance. These are edited real recordings, not synthesized interface sounds.

The real UI proof has no native cursor/audio recording. The one mouse sound is explicitly added licensed Foley on the first captured result frame, not native browser sound or evidence of a new signing action. There are no added click sounds on financial illustrations, no toy tones, chimes, alarms, coin shower, or repeated transition whoosh.

`prepare_audio.py` checks source hashes, writes 48 kHz stereo 24-bit PCM `mix.wav` plus separate pre-master music/SFX stems, and measures loudness, true peak, exact 56-second sample count and a 320 kb/s AAC encode. The target is −16 to −14 LUFS and no higher than −1.5 dBTP, including that AAC roundtrip. Stems are pre-master and require a fresh final master after a human voice is added. Final measured values and output hashes are in ignored `audio/qa.json`.

Perceptual listening has not been performed by this tool. Waveform, source provenance, placement, loudness and codec checks are measured; an audition is not claimed.
