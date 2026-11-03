#!/usr/bin/env python3
"""Prepare SUNSET v4's retained synthetic narration and original 150 BPM score."""
import hashlib
import json
import math
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / ".publication/sunset-launch-v4"
ORIGINAL = ROOT / ".publication/sunset-launch-v1/voice"
RATE, DURATION, BPM = 48000, 24.0, 150
CUES = [(2, .4), (8, 4.8), (12, 12.6), (16, 16.4), (20, 20.8)]
BEAT = 60 / BPM


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)], check=True)


def pcm(path):
    with wave.open(str(path), "rb") as f:
        assert f.getsampwidth() == 2 and f.getnchannels() == 1 and f.getframerate() == RATE
        return np.frombuffer(f.readframes(f.getnframes()), "<i2").astype(np.float64) / 32768


def save_wave(path, values):
    values = np.asarray(values)
    with wave.open(str(path), "wb") as f:
        f.setparams((1 if values.ndim == 1 else values.shape[1], 2, RATE, len(values), "NONE", "not compressed"))
        f.writeframes((np.clip(values, -.9999, .9999) * 32767).astype("<i2").tobytes())


def timestamp(seconds):
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def voice():
    retained = {s["index"]: s for s in json.loads((ORIGINAL / "timing.json").read_text())["sentences"]}
    folder = OUT / "voice"
    folder.mkdir(parents=True, exist_ok=True)
    phrases = []
    for index, (number, start) in enumerate(CUES, 1):
        item = retained[number]
        source = ORIGINAL / item["audio_file"]
        target = folder / item["audio_file"]
        ffmpeg("-i", source, "-af", "atempo=1.12,loudnorm=I=-18:TP=-3:LRA=7", "-ar", RATE, "-ac", 1,
               "-c:a", "pcm_s16le", target)
        samples = pcm(target)
        duration = len(samples) / RATE
        phrases.append({
            "index": index, "source_sentence_index": number, "text": item["text"],
            "start": start, "end": start + duration, "duration": duration,
            "audio_file": target.name, "rendered_file": str(target.relative_to(OUT)),
            "source_file": str(source.relative_to(ROOT)), "source_sha256": sha(source),
            "sha256": sha(target), "rendered_sha256": sha(target),
            "pitch_preserving_tempo": 1.12, "sample_rate": RATE,
        })
    assert all(a["end"] <= b["start"] for a, b in zip(phrases, phrases[1:]))
    assert DURATION - phrases[-1]["end"] >= .4
    timing = {
        "schema": 1, "duration": DURATION, "sample_rate": RATE, "bpm": BPM,
        "voice": "Five whole retained Kokoro af_heart synthetic sentences; no fresh synthesis or cloning.",
        "phrases": phrases, "voice_overlap": False,
        "final_voice_tail_seconds": DURATION - phrases[-1]["end"],
    }
    (folder / "timing.json").write_text(json.dumps(timing, indent=2) + "\n")
    (OUT / "sunset-launch-v4.srt").write_text("\n".join(
        f'{i}\n{timestamp(c["start"])} --> {timestamp(c["end"])}\n{c["text"]}\n'
        for i, c in enumerate(phrases, 1)))
    return phrases


def score(phrases):
    """Synthesize every musical/effect sample; no reference audio is read."""
    count = round(RATE * DURATION)
    music = np.zeros((count, 2))
    rng = np.random.default_rng(150042)
    timeline = np.arange(count) / RATE

    def add(start, samples, pan=0):
        samples = np.asarray(samples)
        if samples.ndim == 1:
            samples = samples[:, None] * np.sqrt([(1 - pan) / 2, (1 + pan) / 2])
        index = round(start * RATE)
        skip = max(0, -index)
        index = max(0, index)
        size = min(len(samples) - skip, count - index)
        if size > 0:
            music[index:index + size] += samples[skip:skip + size]

    def times(duration):
        return np.arange(round(duration * RATE)) / RATE

    # Tight synthetic kick, soft clap and eighth-note high-frequency percussion.
    for beat in range(60):
        start = beat * BEAT
        q = times(.34)
        phase = math.tau * (46 * q + 98 * .017 * (1 - np.exp(-q / .017)))
        kick = np.sin(phase) * np.exp(-q * 22) * .49
        kick += rng.uniform(-1, 1, len(q)) * np.exp(-q * 600) * .032
        arrangement = .62 if start < 1.6 or 8.8 <= start < 9.6 else 1
        add(start, kick * arrangement)
        if beat % 4 in [1, 3]:
            q = times(.16)
            noise = rng.uniform(-1, 1, len(q))
            bright = noise - np.r_[0, noise[:-1]] * .85
            envelope = sum(np.where(q >= delay, np.exp(-np.maximum(0, q - delay) * 70), 0)
                           for delay in [0, .011, .025])
            add(start, (bright * .052 + np.sin(math.tau * 185 * q) * .025) * envelope,
                -.15 if beat % 4 == 1 else .15)
    for step in range(120):
        start = step * BEAT / 2
        q = times(.13 if step % 8 != 7 else .24)
        noise = rng.uniform(-1, 1, len(q))
        bright = noise - np.r_[0, noise[:-1]]
        hat = bright * np.exp(-q * (100 if step % 8 != 7 else 24))
        add(start, hat * (.025 if step % 2 else .037), .55 if step % 2 else -.55)

    # Original C-minor sub phrase and bright mallet arpeggio, with stereo echoes.
    roots = [65.4064, 65.4064, 77.7817, 87.3071, 65.4064]
    offsets = [0, 7, 12, 3, 10, 7, 15, 12]
    for bar in range(15):
        root = roots[bar % len(roots)]
        for off in [0, .8]:
            q = times(.67)
            envelope = (1 - np.exp(-q * 85)) * np.exp(-q * 6)
            bass = (np.sin(math.tau * root * q) + .17 * np.sin(math.tau * root * 2 * q))
            add(bar * 1.6 + off, bass * envelope * .27)
        for step, semitone in enumerate(offsets):
            start = bar * 1.6 + step * .2
            q = times(.34)
            frequency = root * 4 * 2 ** (semitone / 12)
            envelope = (1 - np.exp(-q * 550)) * np.exp(-q * 18)
            note = (np.sin(math.tau * frequency * q) + .2 * np.sin(math.tau * frequency * 2.002 * q))
            signal = note * envelope * (.06 if step % 4 else .085)
            pan = .52 if step % 2 else -.52
            add(start, signal, pan)
            add(start + .3, signal * .26, -pan)
            add(start + .6, signal * .10, pan)

    # Quiet spatial texture supplies continuity through macro/whip transitions.
    for frequency, pan in [(130.813, -.5), (155.563, .5), (195.998, 0)]:
        pad = np.sin(math.tau * frequency * timeline + .3 * np.sin(timeline * .75))
        add(0, pad * (.009 + .006 * np.sin(timeline * .4) ** 2), pan)

    # Authored impacts and tape-like risers at the actual editorial handoffs.
    impacts = [0, .8, 1.6, 2.4, 3.2, 4.8, 6.4, 7.2, 8.8, 9.2, 9.6, 10.8, 12.6, 13.6, 15.8, 16.4, 18, 19.6, 20.4]
    for at in impacts:
        q = times(.42)
        sub = np.sin(math.tau * (40 * q + 70 * .035 * (1 - np.exp(-q / .035))))
        tick = rng.uniform(-1, 1, len(q)) * np.exp(-q * 130)
        add(at, (sub * np.exp(-q * 21) * .28 + tick * .09))
    for index, at in enumerate([.8, 2.4, 4.8, 8.8, 9.6, 10.8, 12.6, 15.8, 16.4, 19.6, 20.4]):
        q = times(.38)
        u = q / .38
        noise = rng.uniform(-1, 1, len(q))
        noise = noise - np.r_[0, noise[:-1]] * .55
        rising = np.sin(math.tau * (240 * q + 2600 * q * q))
        sweep = (noise * .095 + rising * .045) * np.sin(np.pi * u) ** 2
        left = np.sqrt(np.clip(1 - u, 0, 1))
        right = np.sqrt(np.clip(u, 0, 1))
        stereo = np.column_stack([sweep * left, sweep * right])
        if index % 2:
            stereo = stereo[:, ::-1]
        add(at - .29, stereo)

    for at in [0, 5.6, 11.5, 19.6, 20.4]:
        q = times(.6)
        bell = (np.sin(math.tau * 783.991 * q) + .45 * np.sin(math.tau * 1174.659 * q))
        bell *= (1 - np.exp(-q * 500)) * np.exp(-q * 10) * .12
        add(at, bell, -.2)

    # A prepared narration envelope preserves strong music in the intentional gaps.
    duck = np.ones(count)
    for cue in phrases:
        attack = np.clip((timeline - (cue["start"] - .12)) / .12, 0, 1)
        release = np.clip(((cue["end"] + .22) - timeline) / .22, 0, 1)
        activity = np.minimum(attack, release)
        duck = np.minimum(duck, 1 - .76 * activity)
    music *= .125 / np.sqrt(np.mean(music ** 2))
    music *= duck[:, None]
    fade = np.minimum(np.clip(timeline / .025, 0, 1), np.clip((DURATION - timeline) / .28, 0, 1))
    music *= fade[:, None]
    return music, duck


def main():
    (OUT / "audio").mkdir(parents=True, exist_ok=True)
    phrases = voice()
    for cue in phrases:
        assert sha(ROOT / cue["source_file"]) == cue["source_sha256"]
        assert sha(OUT / cue["rendered_file"]) == cue["rendered_sha256"]
    music, duck = score(phrases)
    save_wave(OUT / "audio/original-score.wav", music)
    narration = np.zeros_like(music)
    for cue in phrases:
        samples = pcm(OUT / cue["rendered_file"])
        start = round(cue["start"] * RATE)
        narration[start:start + len(samples)] += samples[:, None] * math.sqrt(.5)
    mix = music + narration
    raw_peak = float(np.max(np.abs(mix)))
    if raw_peak > .98:
        mix *= .98 / raw_peak
    raw = OUT / "audio/mix-unmastered.wav"
    save_wave(raw, mix)

    measure = subprocess.run([
        "ffmpeg", "-hide_banner", "-i", str(raw), "-af",
        "loudnorm=I=-16:TP=-2.2:LRA=7:print_format=json", "-f", "null", "-"
    ], capture_output=True, text=True, check=True)
    loud, _ = json.JSONDecoder().raw_decode(measure.stderr[measure.stderr.rfind("{"):])
    (OUT / "audio/mastering-first-pass.log").write_text(measure.stderr)
    normalize = ("loudnorm=I=-16:TP=-2.2:LRA=7:linear=true"
                 f':measured_I={loud["input_i"]}:measured_TP={loud["input_tp"]}'
                 f':measured_LRA={loud["input_lra"]}:measured_thresh={loud["input_thresh"]}'
                 f':offset={loud["target_offset"]}')
    target = OUT / "audio/mix.wav"
    ffmpeg("-i", raw, "-af", normalize, "-ar", RATE, "-ac", 2, "-t", DURATION,
           "-c:a", "pcm_s24le", target)
    verification = subprocess.run([
        "ffmpeg", "-hide_banner", "-i", str(target), "-af",
        "loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"
    ], capture_output=True, text=True, check=True)
    final, _ = json.JSONDecoder().raw_decode(verification.stderr[verification.stderr.rfind("{"):])
    (OUT / "audio/mastering-verification.log").write_text(verification.stderr)
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(target)]))
    stream = probe["streams"][0]
    assert stream["sample_rate"] == str(RATE) and stream["channels"] == 2
    assert abs(float(probe["format"]["duration"]) - DURATION) < 1 / RATE
    assert -17 <= float(final["input_i"]) <= -15
    assert float(final["input_tp"]) <= -1.5
    # AAC raises intersample peaks; test the exact downstream codec/bitrate too.
    encoded = subprocess.run([
        "ffmpeg", "-v", "error", "-i", str(target), "-c:a", "aac", "-b:a", "192k",
        "-f", "adts", "pipe:1"], capture_output=True, check=True).stdout
    aac_check = subprocess.run([
        "ffmpeg", "-hide_banner", "-i", "pipe:0", "-af",
        "loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"
    ], input=encoded, capture_output=True, check=True)
    aac_log = aac_check.stderr.decode()
    aac, _ = json.JSONDecoder().raw_decode(aac_log[aac_log.rfind("{"):])
    (OUT / "audio/aac-roundtrip.log").write_text(aac_log)
    assert float(aac["input_tp"]) <= -1.5
    speech_music = []
    for cue in phrases:
        a, b = round(cue["start"] * RATE), round(cue["end"] * RATE)
        speech = np.sqrt(np.mean(narration[a:b] ** 2))
        bed = np.sqrt(np.mean(music[a:b] ** 2))
        separation = 20 * math.log10(speech / bed)
        assert separation >= 6, separation
        speech_music.append({"phrase": cue["index"], "voice_above_music_rms_db": round(separation, 2)})
    qa = {
        "duration_seconds": DURATION, "sample_rate": RATE, "channels": 2, "bpm": BPM, "bars": 15,
        "phrase_count": len(phrases), "voice_overlap": False,
        "last_voice_end": phrases[-1]["end"], "final_voice_tail_seconds": DURATION - phrases[-1]["end"],
        "integrated_lufs": float(final["input_i"]), "true_peak_dbtp": float(final["input_tp"]),
        "mix_sha256": sha(target), "mix_bytes": target.stat().st_size,
        "voice_to_music_rms": speech_music, "source_hashes_checked": True,
        "aac_192k_roundtrip_lufs": float(aac["input_i"]),
        "aac_192k_roundtrip_true_peak_dbtp": float(aac["input_tp"]),
        "reference_audio_used": False, "perceptual_listening_verified": False,
        "scope": "Original deterministic150BPM synthesis plus five whole retained synthetic narration sentences.",
    }
    (OUT / "audio/qa.json").write_text(json.dumps(qa, indent=2) + "\n")
    (OUT / "CREDITS.md").write_text(
        "SUNSET launch v4 audio. Original150BPM procedural music and sound effects synthesized by "
        "projects/sunset/media/launch-v4/prepare_audio.py; no reference audio, external music recording or commercial sample. "
        "Five retained Kokoro af_heart synthetic sentences, edited at pitch-preserving1.12tempo; no fresh synthesis or voice cloning. "
        "Original engine/model licenses and provenance are retained in .publication/sunset-launch-v1/voice/ "
        "(engine MIT; model Apache2.0). Captions preserve the full original phrases. "
        "Objective mastering, AAC192k roundtrip peaks, exact duration, source identity and RMS separation were checked; perceptual listening remains unverified.\n")
    print(json.dumps(qa, indent=2), flush=True)


if __name__ == "__main__":
    main()
