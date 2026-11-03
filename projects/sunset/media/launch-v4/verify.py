#!/usr/bin/env python3
"""Mux and verify the local v4 film. Generated outputs stay ignored."""
from pathlib import Path
import argparse, datetime, hashlib, json, re, struct, subprocess, wave
ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / ".publication/sunset-launch-v4"
SRC = Path(__file__).resolve().parent
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def run(args, name):
    result = subprocess.run(args, capture_output=True, text=True)
    (OUT / (name + ".log")).write_text(result.stderr)
    assert result.returncode == 0, result.stderr[-3000:]
    return result.stderr
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mux", action="store_true")
    args = parser.parse_args()
    film = OUT / "sunset-launch-v4.mp4"
    if args.mux:
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-i", str(OUT / "sunset-launch-v4-silent.mp4"),
             "-i", str(OUT / "audio/mix.wav"),
             "-map", "0:v:0", "-map", "1:a:0", "-t", "24",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
             "-movflags", "+faststart", "-metadata", "title=SUNSET - Funded onchain. Kept offline.",
             "-metadata", "comment=Original 3D and kinetic composition; genuine UI excerpts; synthetic narration; NEAR testnet.",
             str(film)], "mux")
    assert film.exists(), "Render and mux the film first"
    probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(film)]))
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    audio = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    assert (video["width"], video["height"], video["codec_name"], video["pix_fmt"], video["r_frame_rate"]) == (1920, 1080, "h264", "yuv420p", "30/1")
    assert int(video["nb_frames"]) == 720 and abs(float(probe["format"]["duration"]) - 24) < .05
    assert audio["codec_name"] == "aac" and int(audio["sample_rate"]) == 48000
    data = film.read_bytes(); offset = 0; atoms = []
    while offset + 8 <= len(data):
        size, kind = struct.unpack_from(">I4s", data, offset)
        if size == 1: size = struct.unpack_from(">Q", data, offset + 8)[0]
        if size == 0: size = len(data) - offset
        assert size >= 8
        atoms.append(kind.decode("ascii")); offset += size
    assert atoms.index("moov") < atoms.index("mdat")
    timing = json.loads((OUT / "voice/timing.json").read_text())
    phrases = timing["phrases"]; assert len(phrases) == 5
    srt_files = [p for p in [OUT / "sunset-launch-v4.srt", OUT / "voice/captions.srt", OUT / "voice/launch.srt"] if p.exists()]
    assert srt_files, "Exact subtitle delivery is missing"
    subtitle_text = srt_files[0].read_text()
    srt = re.sub(r"\s+", " ", subtitle_text)
    blocks = subtitle_text.strip().split("\n\n")
    assert len(blocks) == len(phrases)
    def seconds(stamp):
        hours, minutes, rest = stamp.strip().split(":")
        return int(hours)*3600 + int(minutes)*60 + float(rest.replace(",", "."))
    for block, phrase in zip(blocks, phrases):
        start, end = block.splitlines()[1].split(" --> ")
        assert abs(seconds(start) - phrase["start"]) <= .001
        assert abs(seconds(end) - phrase["end"]) <= .001
    previous = 0
    for phrase in phrases:
        assert previous <= phrase["start"] < phrase["end"] <= 24
        assert sha(ROOT / phrase["source_file"]) == phrase["source_sha256"]
        voice = OUT / phrase["rendered_file"]
        assert sha(voice) == phrase["rendered_sha256"]
        with wave.open(str(voice)) as wav:
            assert abs(wav.getnframes() / wav.getframerate() - phrase["duration"]) < .001
        assert phrase["text"] in srt
        previous = phrase["end"]
    tail = 24 - previous; assert tail >= .4
    browser = json.loads((ROOT / "projects/sunset/evidence/browser-showcase.json").read_text())
    captures = {item["file"]: item["sha256"] for item in browser["capture_files"]}
    used = ["06-hosted-verified-game.png", "07-hosted-game-feedback.png", "11-offline-game-complete.png"]
    for name in used:
        assert sha(ROOT / ".publication/sunset-launch-v1/footage" / name) == captures[name]
    run(["ffmpeg", "-hide_banner", "-v", "error", "-i", str(film), "-f", "null", "-"], "decode")
    black = run(["ffmpeg", "-hide_banner", "-i", str(film), "-vf", "blackdetect=d=.20:pix_th=.01:pic_th=.98", "-an", "-f", "null", "-"], "black-frames")
    assert "black_start:" not in black, "Unexpected near-black interval: inspect black-frames.log"
    levels = run(["ffmpeg", "-hide_banner", "-i", str(film), "-vn", "-af", "loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json", "-f", "null", "-"], "audio-levels")
    loud, _ = json.JSONDecoder().raw_decode(levels[levels.rfind("{"):])
    assert -18 <= float(loud["input_i"]) <= -14
    assert float(loud["input_tp"]) <= -.8
    points = [("opening", .7), ("sculpture", 2.8), ("release", 6.6), ("fragments", 9.05),
              ("answer", 10.35), ("feedback", 11.8), ("offline", 14.4),
              ("stewardship", 17.7), ("type", 20.3), ("close", 22.8)]
    for name, t in points:
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(film), "-frames:v", "1", str(OUT / ("decoded-" + name + ".png"))], "extract-" + name)
    qa = {"checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "status": "objective_checks_passed_visual_review_separate", "sha256": sha(film), "bytes": film.stat().st_size,
          "duration": float(probe["format"]["duration"]), "frames": 720, "dimensions": [1920, 1080], "fps": 30,
          "video_codec": "h264", "pixel_format": "yuv420p", "audio_codec": "aac", "audio_sample_rate": 48000,
          "faststart": True, "top_level_atoms": atoms, "full_decode": "passed", "unexpected_black_intervals": 0,
          "blackdetect_thresholds": {"duration": .2, "pixel": .01, "picture": .98},
          "caption_cues": 5, "exact_caption_text": True, "voice_sources_and_edits_verified": True,
          "voice_overlap": False, "final_voice_tail_seconds": tail,
          "capture_hashes_match_browser_evidence": {name: captures[name] for name in used},
          "loudness_lufs": float(loud["input_i"]), "true_peak_dbtp": float(loud["input_tp"]),
          "decoded_review_samples": [{"name": n, "seconds": t, "file": "decoded-" + n + ".png"} for n, t in points],
          "perceptual_listening_verified": False,
          "scope": "Original 3D/editorial animation, genuine UI capture excerpts, graphical answer reenactment; no financial signing or new chain action."}
    (OUT / "media-qa.json").write_text(json.dumps(qa, indent=2) + "\n")
    (OUT / "ffprobe.json").write_text(json.dumps(probe, indent=2) + "\n")
    print(json.dumps(qa, indent=2))
if __name__ == "__main__":
    main()
