#!/usr/bin/env python3
"""Independently inspect the delivered v5 file; never mux or encode it."""
import datetime, hashlib, json, math, re, struct, subprocess
from pathlib import Path
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[4]
SRC = Path(__file__).resolve().parent
OUT = ROOT / ".publication/sunset-launch-v5"
W, H, FPS, COUNT = 1920, 1080, 30, 720
INDICES = list(range(486)) + list(range(588, 630))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def command(args, name):
    result = subprocess.run(args, capture_output=True, text=True)
    (OUT / (name + ".log")).write_text(result.stderr)
    assert result.returncode == 0, result.stderr[-3000:]
    return result.stderr

def ratio(a, b):
    def luminance(c):
        v = [n / 255 for n in c]
        return sum(w * (n / 12.92 if n <= .04045 else ((n + .055) / 1.055) ** 2.4)
                   for w, n in zip((.2126, .7152, .0722), v))
    low, high = sorted([luminance(a), luminance(b)])
    return (high + .05) / (low + .05)

def seconds(s):
    h, m, rest = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(rest.replace(",", "."))

def main():
    film = OUT / "sunset-launch-v5.mp4"
    probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(film)]))
    v = next(s for s in probe["streams"] if s["codec_type"] == "video")
    a = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    assert (v["width"], v["height"], v["codec_name"], v["pix_fmt"], v["r_frame_rate"]) == (W, H, "h264", "yuv420p", "30/1")
    assert int(v["nb_frames"]) == COUNT and abs(float(probe["format"]["duration"]) - 24) < .02
    assert (v["color_space"], v["color_primaries"], v["color_transfer"], v["color_range"]) == ("bt709", "bt709", "bt709", "tv")
    assert a["codec_name"] == "aac" and int(a["sample_rate"]) == 48000 and a["channels"] == 2
    data = film.read_bytes(); offset = 0; atoms = []
    while offset + 8 <= len(data):
        size, kind = struct.unpack_from(">I4s", data, offset)
        if size == 1: size = struct.unpack_from(">Q", data, offset + 8)[0]
        if size == 0: size = len(data) - offset
        assert size >= 8
        atoms.append(kind.decode("ascii")); offset += size
    assert atoms.index("moov") < atoms.index("mdat")
    composite = read(OUT / "composite/composite-provenance.json")
    assert sha(film) == composite["sha256"] and composite["video_encode_passes"] == 1
    assert composite["source_sha256"] == sha(SRC / "render_launch.py")
    assert composite["source_cg_indices"] == INDICES and composite["nearest_source_fallback"] is False
    scene = read(OUT / "scene/manifest.json")
    assert sha(OUT / "scene/manifest.json") == composite["native_scene_manifest_sha256"]
    assert scene["source_sha256"] == sha(SRC / "scene.mjs")
    assert scene["renderer_sha256"] == sha(SRC / "render_scene.mjs")
    assert scene["native"]["antialias"] and scene["native"]["samples"] >= 4
    assert scene["native"]["width"] == W and scene["native"]["height"] == H and scene["native"]["fps"] == FPS
    assert scene["sequence"]["captured_indices"] == INDICES and scene["preview"] is False
    manifest_frames = {r["frame"]: r for r in scene["records"]}
    seq_hash = hashlib.sha256()
    for n in INDICES:
        p = OUT / f"scene/frames/{n:06d}.png"
        digest = sha(p); record = manifest_frames[n]
        assert digest == record["sha256"] and abs(record["time"] - n/FPS) < 1e-9
        assert record["actual_context_antialias"] and record["actual_samples"] >= 4
        with Image.open(p) as im:
            assert im.size == (W, H) and im.format == "PNG"
            im.verify()
        seq_hash.update(f"{n:06d}:{digest}\n".encode())
    timing = read(OUT / "story-timing.json"); cues = timing["phrases"]
    assert len(cues) == 9 and len(" ".join(c["text"] for c in cues).split()) == 44
    assert timing["mix_sha256"] == sha(OUT / "audio/mix.wav")
    assert composite["audio_master_sha256"] == timing["mix_sha256"]
    assert timing["narration_sha256"] == sha(OUT / "voice/narration.wav")
    blocks = (OUT / "sunset-launch-v5.srt").read_text().strip().split("\n\n")
    assert len(blocks) == len(cues)
    previous = 0
    for cue, block in zip(cues, blocks):
        start, end = block.splitlines()[1].split(" --> ")
        assert abs(seconds(start) - cue["start"]) <= .001
        assert abs(seconds(end) - cue["end"]) <= .001
        assert " ".join(block.splitlines()[2:]) == cue["text"]
        assert previous <= cue["start"] < cue["end"] <= 24
        assert sha(ROOT / cue["source_file"]) == cue["source_sha256"]
        audio_probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_format", "-of", "json", str(ROOT / cue["source_file"])]))
        assert abs(float(audio_probe["format"]["duration"]) - cue["duration"]) < .001
        previous = cue["end"]
    assert abs(24 - previous - 1.672) < .001
    capture = read(OUT / "footage/capture-provenance.json")
    assert capture["dpr"] >= 2 and not capture["console_errors"]
    assert capture["offline"] == {"onLine": False, "resources": 0, "scheme": "file:"}
    for spec in capture["captures"]:
        p = OUT / "footage" / spec["file"]
        assert sha(p) == spec["sha256"]
        with Image.open(p) as im:
            assert list(im.size) == spec["pixel_dimensions"]
            im.verify()
    for ui in composite["actual_ui"].values():
        assert ui["scale"] <= 1 and sha(ROOT / ui["source"]["path"]) == ui["source"]["sha256"]
    music = read(OUT / "audio/music-provenance.json")
    music_file = OUT / "audio-research/music" / music["file"]
    assert sha(music_file) == music["sha256"] and music["license"] == "CC BY 4.0"
    assert music["excerpt_start_seconds"] == 205 and music["excerpt_end_seconds"] == 229
    assert "Scott Buckley" in (SRC / "x-post.txt").read_text() and "Scott Buckley" in (SRC / "CREDITS.md").read_text()
    reads = read(OUT / "composite/readability-spec.json")
    assert len(reads["all_frames"]) == COUNT
    for entry in reads["essential_read_windows"]:
        words = sum(len(line.split()) for line in entry["lines"])
        assert entry["window"][1] - entry["window"][0] + 1e-8 >= .3 * words + .5
        for n in range(math.ceil(entry["window"][0] * FPS), math.ceil(entry["window"][1] * FPS)):
            actual = [r["text"] for r in reads["all_frames"][n]["text"] if r["kind"] == "headline"]
            assert actual == entry["lines"], f"Missing/occluded promised read: frame{n} {entry['id']}"
    safe = reads["safe_bbox"]
    for row in reads["all_frames"]:
        for item in row["text"]:
            x0, y0, x1, y1 = item["bbox"]
            assert safe[0] <= x0 < x1 <= safe[2] and safe[1] <= y0 < y1 <= safe[3]
            assert item["solid_protected"] and item["contrast"] >= 4.5
    for n in range(630, 720):
        assert any(i["kind"] == "url" for i in reads["all_frames"][n]["text"])
    for n in range(672, 720):
        assert len([i for i in reads["all_frames"][n]["text"] if i["kind"] == "music_credit"]) == 2
    # Decode the entire actual delivery. Probe interior glyph and plane pixels, not antialiased edges.
    points = [17, 45, 113, 174, 257, 316, 354, 394, 435, 495, 516, 555, 580, 600, 645, 675, 705]
    boundaries = [3.2, 5.7, 7.8, 10.35, 13.0, 14.7, 16.2, 17.82, 19.6, 21.0]
    cuts = sorted({max(0, min(719, round(t*FPS)+delta)) for t in boundaries for delta in (-6, 0, 6)})
    samples = sorted(set(points + cuts)); saved = []
    review = OUT / "review"; review.mkdir(exist_ok=True)
    pipe = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(film), "-map", "0:v:0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    minimum = math.inf; probes = 0
    for n in range(COUNT):
        raw = pipe.stdout.read(W * H * 3)
        assert len(raw) == W * H * 3, f"Incomplete decoded frame {n}"
        im = Image.frombytes("RGB", (W,H), raw)
        for item in reads["all_frames"][n]["text"]:
            fg = im.getpixel(tuple(item["probe_foreground_xy"]))
            bg = im.getpixel(tuple(item["probe_background_xy"]))
            measured = ratio(fg, bg); minimum = min(minimum, measured); probes += 1
            assert measured >= 4.5, f"Encoded contrast {measured:.3f}: frame{n} {item['text']} {fg} {bg}"
        if n in samples:
            im.save(review / f"decoded-{n:06d}.png"); saved.append(n)
    assert not pipe.stdout.read(1), "Extra decoded frames"
    stderr = pipe.stderr.read().decode(); assert pipe.wait() == 0, stderr
    (OUT / "decode.log").write_text(stderr)
    def sheet(indices, name, width, cols):
        cell_h = round(width * H / W) + 24
        result = Image.new("RGB", (width * cols, cell_h * math.ceil(len(indices)/cols)), "#f2f0e9")
        for k,n in enumerate(indices):
            with Image.open(review / f"decoded-{n:06d}.png") as im:
                result.paste(im.resize((width, round(width*H/W)), Image.Resampling.LANCZOS), ((k%cols)*width,(k//cols)*cell_h))
            ImageDraw.Draw(result).text(((k%cols)*width+8,(k//cols)*cell_h+cell_h-20), f"{n/FPS:.3f}s / {n}", fill="#101316")
        result.save(review / name, quality=97)
    sheet(points, "beat-sheet.jpg", 480, 4)
    sheet(points, "phone-sheet.jpg", 360, 3)
    sheet(cuts, "cut-sheet.jpg", 480, 3)
    black = command(["ffmpeg", "-hide_banner", "-i", str(film), "-vf", "blackdetect=d=.20:pix_th=.01:pic_th=.98", "-an", "-f", "null", "-"], "black-frames")
    assert "black_start:" not in black
    levels = command(["ffmpeg", "-hide_banner", "-i", str(film), "-vn", "-af", "loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json", "-f", "null", "-"], "audio-levels")
    loud, _ = json.JSONDecoder().raw_decode(levels[levels.rfind("{"):])
    assert -18 <= float(loud["input_i"]) <= -14 and float(loud["input_tp"]) <= -1.5
    preserved = {
        ".publication/sunset-launch-v1/render/sunset-launch.mp4": "24e49095284f165a4346adbca0e2653bbea1080f8bf902b98c95a8700b866ad0",
        ".publication/sunset-launch-v2/sunset-launch-v2.mp4": "769948d737168652fdcf531faf47fd7ec183432d862b8149dff7e8d36bbef934",
        ".publication/sunset-launch-v3/sunset-launch-v3.mp4": "cf2eff815d253b2114d5745fcdd4edeef1a492d4e579df99ceed69f1b4dae1cb",
        ".publication/sunset-launch-v4/sunset-launch-v4.mp4": "d9d1c4b74e867da221cc6d8a97e0524576e0575e25e7899dd74db3e246bad42b",
    }
    for path, digest in preserved.items():
        assert sha(ROOT / path) == digest, f"Preserved movie changed: {path}"
    qa = {"checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "status": "objective_checks_passed_visual_and_listening_review_separate", "film_path": str(film.relative_to(ROOT)),
          "sha256": sha(film), "bytes": film.stat().st_size, "duration_seconds": 24, "dimensions": [W,H], "fps": FPS,
          "frames": COUNT, "video_codec": "h264", "pixel_format": "yuv420p", "color": "BT709 limited", "audio_codec": "aac", "audio_sample_rate": 48000,
          "faststart": True, "full_decode": "passed", "unexpected_black_intervals": 0, "video_encode_passes": 1,
          "native_cg_frames": len(INDICES), "native_cg_sequence_sha256": seq_hash.hexdigest(), "native_msaa_samples": 4,
          "motion_interpolation": False, "jpeg_cg": False, "exact_ui_capture_manifest_sha256": sha(OUT / "footage/capture-provenance.json"),
          "ui_enlargement": False, "caption_cues": len(cues), "script_words": 44, "exact_caption_text_and_times": True,
          "voice_overlap": False, "final_voice_tail_seconds": 24-previous, "essential_text_probes": probes,
          "minimum_decoded_text_contrast": round(minimum,4), "essential_safe_bbox": safe,
          "url_stable_seconds": 3.0, "music": music, "music_credit_burned_seconds": 1.6,
          "loudness_lufs": float(loud["input_i"]), "true_peak_dbtp": float(loud["input_tp"]),
          "review_sheets": ["review/beat-sheet.jpg", "review/phone-sheet.jpg", "review/cut-sheet.jpg"],
          "preserved_versions": preserved, "perceptual_listening_verified": False, "chain_mutations": 0}
    (OUT / "ffprobe.json").write_text(json.dumps(probe, indent=2)+"\n")
    (OUT / "media-qa.json").write_text(json.dumps(qa, indent=2)+"\n")
    print(json.dumps(qa, indent=2))

if __name__ == "__main__": main()
