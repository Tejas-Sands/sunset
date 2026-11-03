"""Prepare the SUNSET launch film's local narration and measured cue clock.

The isolated runtime/model/voice assets and rendered output stay in .publication.
This program does not generate music; the soundtrack uses a licensed recording.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import time
import math
import subprocess

import numpy as np
import onnxruntime as ort
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(__file__).resolve().parent
OUT = ROOT / ".publication/sunset-launch-v5"
CACHE = OUT / "tts-cache"
RATE = 24000


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(seconds):
    ms = round(seconds * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def captions(sentence):
    if len(sentence) <= 49:
        return sentence
    words = sentence.split()
    pairs = [(" ".join(words[:i]), " ".join(words[i:])) for i in range(1, len(words))]
    return "\n".join(min(pairs, key=lambda pair: abs(len(pair[0]) - len(pair[1]))))


def narrate():
    script = json.loads((SOURCE / "narration-script.json").read_text())
    voice_dir = OUT / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)
    model = CACHE / "kokoro-v1.0.fp16.onnx"
    voices_file = CACHE / "voices-v1.0.bin"
    assert sha256(model) == "f3a290d384fbb27966d462905c71a46cef9e5fd00516b40df32a0b4afe77ac96"
    assert sha256(voices_file) == "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d"
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    options.inter_op_num_threads = 1
    options.log_severity_level = 3
    session = ort.InferenceSession(str(model), sess_options=options, providers=["CPUExecutionProvider"])
    engine = Kokoro.from_session(session, str(voices_file))
    lead_samples = round(.20 * RATE)
    gap_samples = round(.15 * RATE)
    tail_samples = round(1.20 * RATE)
    parts = [np.zeros(lead_samples, dtype=np.float32)]
    offset = lead_samples
    timing = []
    for line in script["sentences"]:
        started = time.monotonic()
        samples, rate = engine.create(
            line["tts_text"], voice=script["voice"], speed=script["speed"],
            lang=script["language"], sentence_pause=.12, clause_pause=.10,
        )
        samples = np.asarray(samples, dtype=np.float32)
        assert rate == RATE and samples.size > RATE // 10 and np.isfinite(samples).all()
        filename = f"sentence-{line['index']:02d}.wav"
        sf.write(voice_dir / filename, samples, RATE, subtype="PCM_24")
        end = offset + len(samples)
        timing.append({
            **line, "start_sample": offset, "end_sample": end,
            "start": offset / RATE, "end": end / RATE, "duration": len(samples) / RATE,
            "audio_file": filename,
        })
        parts.append(samples)
        pause = tail_samples if line is script["sentences"][-1] else gap_samples
        parts.append(np.zeros(pause, dtype=np.float32))
        offset = end + pause
        print(f"{line['index']:02d}: {len(samples)/RATE:.3f}s ({time.monotonic()-started:.2f}s compute) {line['text']}", flush=True)
    audio = np.concatenate(parts)
    peak = float(np.max(np.abs(audio)))
    assert peak > .01
    audio *= 10 ** (-2 / 20) / peak
    audio_path = voice_dir / "narration.wav"
    sf.write(audio_path, audio, RATE, subtype="PCM_24")
    metadata = {
        "voice": script["voice"], "voice_type": script["voice_type"], "speed": script["speed"],
        "sample_rate": RATE, "channels": 1, "duration": len(audio) / RATE,
        "word_count": len(" ".join(s["text"] for s in script["sentences"]).split()),
        "lead_silence": lead_samples / RATE, "sentence_gap": gap_samples / RATE,
        "tail_silence": tail_samples / RATE, "sentences": timing,
        "caption_alignment": "Exact per-sentence synthesis sample boundaries; not word-level forced alignment",
        "script_sha256": sha256(SOURCE / "narration-script.json"),
        "model_sha256": sha256(model), "voices_sha256": sha256(voices_file),
        "narration_sha256": sha256(audio_path), "providers": session.get_providers(),
        "engine": {name: importlib.metadata.version(name) for name in
                   ["kokoro-onnx", "onnxruntime", "numpy", "phonemizer", "espeakng-loader", "soundfile"]},
        "peak_after_normalization": float(np.max(np.abs(audio))),
        "rms": float(np.sqrt(np.mean(np.square(audio)))),
        "perceptual_listening": "Not performed by this tool; objective timing/peak checks only",
    }
    (voice_dir / "timing.json").write_text(json.dumps(metadata, indent=2) + "\n")
    srt = "\n\n".join(
        f"{line['index']}\n{stamp(line['start'])} --> {stamp(line['end'])}\n{captions(line['text'])}"
        for line in timing
    ) + "\n"
    (voice_dir / "captions.srt").write_text(srt)
    print(json.dumps({key: metadata[key] for key in ["voice","speed","duration","word_count","narration_sha256"]},indent=2),flush=True)



DURATION = 24.0
MIX_RATE = 48000
MUSIC_START = 205.0
MUSIC_SHA256 = "678dabce348ecd305ee4c998b258275acd1f4731a858083d11535467207bc5e0"


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)], check=True)


def measure(path, log_path):
    result = subprocess.run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
        "loudnorm=I=-16:TP=-2.2:LRA=8:print_format=json", "-f", "null", "-",
    ], capture_output=True, text=True, check=True)
    log_path.write_text(result.stderr)
    return json.JSONDecoder().raw_decode(result.stderr[result.stderr.rfind("{"):])[0]


def mix():
    audio_dir = OUT / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    narration = OUT / "voice/narration.wav"
    timing = json.loads((OUT / "voice/timing.json").read_text())
    phrases = timing["sentences"]
    assert timing["narration_sha256"] == sha256(narration)
    assert timing["script_sha256"] == sha256(SOURCE / "narration-script.json")
    assert all(a["end"] <= b["start"] for a,b in zip(phrases, phrases[1:]))
    assert DURATION - phrases[-1]["end"] >= .5
    music_source = OUT / "audio-research/music/scott-buckley-computations-no-cello.mp3"
    assert sha256(music_source) == MUSIC_SHA256
    # Existing recorded music only. EQ, fades and gain envelopes are mix processing.
    voice_path = audio_dir / "voice-normalized.wav"
    ffmpeg("-i", narration, "-af",
           "highpass=f=70,equalizer=f=250:t=q:w=1:g=-1.5,"
           "acompressor=threshold=0.1:ratio=2:attack=12:release=100:makeup=1.5,"
           "loudnorm=I=-18:TP=-3:LRA=8,aresample=48000,apad=whole_len=1152000,atrim=end_sample=1152000",
           "-ar", MIX_RATE, "-ac", 1, "-c:a", "pcm_s24le", voice_path)
    bed_path = audio_dir / "licensed-bed-normalized.wav"
    ffmpeg("-ss", MUSIC_START, "-i", music_source, "-t", DURATION, "-af",
           "highpass=f=50,equalizer=f=2500:t=q:w=0.7:g=-2.5,loudnorm=I=-26:TP=-4:LRA=9",
           "-ar", MIX_RATE, "-ac", 2, "-c:a", "pcm_s24le", bed_path)
    voice, voice_rate = sf.read(voice_path, dtype="float64")
    bed, bed_rate = sf.read(bed_path, dtype="float64", always_2d=True)
    count = round(DURATION * MIX_RATE)
    assert voice_rate == bed_rate == MIX_RATE
    assert len(voice) == len(bed) == count and bed.shape == (count, 2)
    times = np.arange(count) / MIX_RATE
    duck = np.ones(count)
    active = np.zeros(count, dtype=bool)
    for phrase in phrases:
        a, b = round(phrase["start"] * MIX_RATE), round(phrase["end"] * MIX_RATE)
        active[a:b] = True
        attack = np.clip((times - (phrase["start"] - .08)) / .08, 0, 1)
        release = np.clip((phrase["end"] + .34 - times) / .34, 0, 1)
        duck = np.minimum(duck, 1 - .5 * np.minimum(attack, release))
    fades = np.minimum(np.clip(times / .18, 0, 1), np.clip((DURATION - times) / .75, 0, 1))
    bed *= (duck * fades)[:, None]
    # Calibrate one overall bed gain from actual speech, keeping the source dynamics.
    voice_active_rms = float(np.sqrt(np.mean(voice[active] ** 2)))
    bed_active_rms = float(np.sqrt(np.mean(bed[active] ** 2)))
    bed_gain = voice_active_rms / (bed_active_rms * 10 ** (12 / 20))
    bed *= bed_gain
    narration_stereo = np.column_stack([voice, voice])
    unmastered = narration_stereo + bed
    assert np.isfinite(unmastered).all() and np.max(np.abs(unmastered)) < .999
    sf.write(audio_dir / "licensed-bed-ducked.wav", bed, MIX_RATE, subtype="PCM_24")
    raw = audio_dir / "mix-unmastered.wav"
    sf.write(raw, unmastered, MIX_RATE, subtype="PCM_24")
    measured = measure(raw, audio_dir / "mastering-first-pass.log")
    filters = (
        "loudnorm=I=-16:TP=-2.2:LRA=8:linear=true"
        f":measured_I={measured['input_i']}:measured_TP={measured['input_tp']}"
        f":measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}"
        f":offset={measured['target_offset']}"
    )
    target = audio_dir / "mix.wav"
    ffmpeg("-i", raw, "-af", filters, "-ar", MIX_RATE, "-ac", 2, "-t", DURATION,
           "-c:a", "pcm_s24le", target)
    final = measure(target, audio_dir / "mastering-verification.log")
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(target)]))
    stream = probe["streams"][0]
    assert stream["sample_rate"] == str(MIX_RATE) and stream["channels"] == 2
    assert stream["codec_name"] == "pcm_s24le"
    assert abs(float(probe["format"]["duration"]) - DURATION) < 1/MIX_RATE
    assert -17 <= float(final["input_i"]) <= -14
    assert float(final["input_tp"]) <= -1.5
    codec_checks = {}
    for bitrate in ["192k", "320k"]:
        encoded = audio_dir / f"aac-roundtrip-{bitrate}.m4a"
        ffmpeg("-i", target, "-c:a", "aac", "-b:a", bitrate, encoded)
        check = measure(encoded, audio_dir / f"aac-roundtrip-{bitrate}.log")
        assert float(check["input_tp"]) <= -1.5
        codec_checks[bitrate] = {
            "integrated_lufs": float(check["input_i"]),
            "true_peak_dbtp": float(check["input_tp"]),
        }
    separation = []
    for phrase in phrases:
        a,b = round(phrase["start"] * MIX_RATE),round(phrase["end"] * MIX_RATE)
        speech_rms = float(np.sqrt(np.mean(voice[a:b] ** 2)))
        bed_rms = float(np.sqrt(np.mean(bed[a:b] ** 2)))
        db = 20 * math.log10(speech_rms / bed_rms)
        assert db >= 8, (phrase["index"], db)
        separation.append({"phrase": phrase["index"], "voice_above_music_rms_db": round(db, 2)})
    source_provenance = json.loads((OUT / "audio-research/music/provenance.json").read_text())
    selected = source_provenance["tracks"][0]
    provenance = {
        **selected, "selected": True, "excerpt_start_seconds": MUSIC_START,
        "excerpt_end_seconds": MUSIC_START + DURATION, "excerpt_duration_seconds": DURATION,
        "selection_basis": "Artist describes no-cello atmospheric electronic/strings underscore; 205–229s has measurable stable energy and avoids the opening. No perceptual listening claim.",
        "one_second_rms_range_db_in_excerpt": 6.16,
        "excerpt_first_second_rms_db": -17.70,
        "processing": {
            "music_highpass_hz": 50, "music_presence_eq_hz": 2500, "music_presence_eq_db": -2.5,
            "fade_in_seconds": .18, "fade_out_seconds": .75,
            "speech_duck_attack_seconds": .08, "speech_duck_release_seconds": .34,
            "speech_duck_gain": .5, "overall_bed_gain": bed_gain,
            "voice_processing": "70Hz highpass, -1.5dB at250Hz, 2:1 compressor, loudness normalization; no pitch shift or time stretch",
            "master": filters,
        },
        "changes_to_disclose": "No Cello alternate mix excerpt205–229s; edited with fades, EQ and ducking beneath narration.",
        "attribution_required": True,
        "attribution_placement": "Burned-in end-card credit plus post/video description and CREDITS.",
        "reference_audio_used": False,
    }
    (audio_dir / "music-provenance.json").write_text(json.dumps(provenance, indent=2)+"\n")
    story_timing = {
        "schema": 1, "duration": DURATION, "sample_rate": MIX_RATE,
        "voice": "Fresh Kokoro am_michael synthetic narration at0.98speed, no cloning or pitch shift.",
        "phrases": [
            {**p, "source_file": str((OUT / "voice" / p["audio_file"]).relative_to(ROOT)),
             "source_sha256": sha256(OUT / "voice" / p["audio_file"]),
             "rendered_file": f"voice/{p['audio_file']}",
             "rendered_sha256": sha256(OUT / "voice" / p["audio_file"]),
             "sample_rate": RATE}
            for p in phrases
        ],
        "voice_overlap": False, "final_voice_tail_seconds": DURATION - phrases[-1]["end"],
        "voice_end_seconds": phrases[-1]["end"],
        "narration_sha256": sha256(narration), "mix_sha256": sha256(target),
    }
    (OUT / "story-timing.json").write_text(json.dumps(story_timing,indent=2)+"\n")
    # Retain the synthesis metadata and add the earlier compositor's phrase alias.
    timing["phrases"] = story_timing["phrases"]
    timing["film_duration"] = DURATION
    (OUT / "voice/timing.json").write_text(json.dumps(timing,indent=2)+"\n")
    (OUT / "sunset-launch-v5.srt").write_text((OUT / "voice/captions.srt").read_text())
    qa = {
        "duration_seconds": DURATION, "sample_rate": MIX_RATE, "channels": 2,
        "codec": "pcm_s24le", "phrase_count": len(phrases), "voice_overlap": False,
        "last_voice_end": phrases[-1]["end"], "final_voice_tail_seconds": DURATION - phrases[-1]["end"],
        "integrated_lufs": float(final["input_i"]), "true_peak_dbtp": float(final["input_tp"]),
        "mix_sha256": sha256(target), "mix_bytes": target.stat().st_size,
        "narration_sha256": sha256(narration), "music_source_sha256": MUSIC_SHA256,
        "voice_to_music_rms": separation, "codec_roundtrips": codec_checks,
        "source_hashes_checked": True, "reference_audio_used": False,
        "procedural_music_or_effects": False, "perceptual_listening_verified": False,
        "scope": "Approved44word fresh male narration with an excerpt of Scott Buckley's CC BY4.0 No Cello recording.",
    }
    (audio_dir / "qa.json").write_text(json.dumps(qa,indent=2)+"\n")
    print(json.dumps(qa,indent=2),flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--voice-only", action="store_true", help="Generate narration and its sample-accurate cue clock")
    mode.add_argument("--mix-only", action="store_true", help="Mix the already generated narration with the verified licensed recording")
    args = parser.parse_args()
    if not args.mix_only:
        narrate()
    if not args.voice_only:
        mix()
