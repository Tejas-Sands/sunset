#!/usr/bin/env python3
"""Independently verify the delivered v10 export and decode review artifacts.
Never invokes the renderer, encodes a film, opens a browser or mutates the product.
"""
import datetime
import functools
import hashlib
import json
import math
import re
import struct
import subprocess
from collections import Counter
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat

ROOT = Path(__file__).resolve().parents[4]
SRC = Path(__file__).resolve().parent
OUT = ROOT / ".publication/sunset-launch-v10"
REVIEW = OUT / "review"
W, H, FPS, COUNT = 1920, 1080, 30, 1320
AUDIO_SHA = "7944591e28c2433a086183184312a98503d30b5c5c6e55ce95dac07301d555f2"
CAPTURE_SHA = "ea94abea8db8e1cec01335d9da42399a99e34a7b1ef24c37965226c5109350f0"
GUIDE_SHA = "7333ed5587248cbca671806dd67548d7b8088380f427bed7161734e34d16e72e"



def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def ratio(a, b):
    def lum(c):
        return sum(w * (v / 255 / 12.92 if v / 255 <= .04045 else ((v / 255 + .055) / 1.055) ** 2.4)
                   for w, v in zip((.2126, .7152, .0722), c))
    lo, hi = sorted((lum(a), lum(b)))
    return (hi + .05) / (lo + .05)


@functools.lru_cache(maxsize=8)
def source(path):
    return Image.open(ROOT / path).convert("RGB")


def check_png(path, expected):
    assert sha(path) == expected, path
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    offset = 8
    while offset < len(data):
        size, = struct.unpack_from(">I", data, offset)
        import zlib
        assert zlib.crc32(data[offset + 4:offset + 8 + size]) & 0xffffffff == struct.unpack_from(">I", data, offset + 8 + size)[0]
        offset += size + 12
    assert offset == len(data)
    with Image.open(path) as im:
        assert im.size == (4320, 2700)
        im.verify()


def check_actual(use, output_time, manifest):
    assert abs(use["film_time"] - output_time) < 1e-7
    playback_time = 35.9666666667 if 36 <= output_time < 40 else output_time
    if playback_time != output_time:
        assert "endpoint_freeze" in use
    segment = next(s for s in manifest["segments"] if s["start"] <= playback_time < s["end"])
    samples = segment["sourceframes"]
    expected = max((i for i, f in enumerate(samples) if f["film_time"] <= playback_time + 1e-8), default=0)
    sample = samples[expected]
    assert use["clip"] == segment["id"] and use["source_sample"] == expected
    assert use["network_offline_verified"] == bool(segment.get("network_offline_verified",False))
    assert use["source_context"] == segment.get("context","app_download" if "download" in segment["id"] and "offline" not in segment["id"] else "guide_file")
    if 32 <= output_time < 40:
        assert use["source_context"]=="guide_file" and use["network_offline_verified"] is True
    assert use["source_path"] == sample["path"] and use["source_sha256"] == sample["sha256"]
    assert abs(use["source_capture_time"] - sample["time"]) < 1e-8
    assert abs(use["source_sample_film_time"] - sample["film_time"]) < 1e-8
    assert abs(use["mapped_source_time"] - (playback_time - segment.get("playbackstart",segment["start"]))) < 1e-8
    assert use["source_dimensions"] == segment["source_dimensions"] == [4320,2700]
    roi = use["effective_roi"]
    assert roi == use["crop"] == sample.get("crop",segment["crop"])
    assert all(isinstance(x,int) for x in roi)
    assert 0 <= roi[0] < roi[2] <= 4320 and 0 <= roi[1] < roi[3] <= 2700
    assert 0 < use["scale"] <= min(2.2,segment.get("max_editorial_scale",1)) + 1e-8
    assert use["resampling"] == "LANCZOS"
    assert use["editorial_magnification"] == (use["scale"] > 1)
    x0,y0,x1,y1 = use["display_bbox"]
    dw,dh = round((roi[2]-roi[0])*use["scale"]),round((roi[3]-roi[1])*use["scale"])
    assert abs((x1-x0)-dw) <= 1 and abs((y1-y0)-dh) <= 1
    assert 0 <= x0 < x0+dw <= W and 0 <= y0 < y0+dh <= H
    return roi,(x0,y0,x0+dw,y0+dh),(dw,dh)


def sheet(indices, name, width=480, cols=4):
    height = round(width * H / W)
    result = Image.new("RGB", (width * cols, (height + 24) * math.ceil(len(indices) / cols)), "#fff3dd")
    draw = ImageDraw.Draw(result)
    for k, n in enumerate(indices):
        with Image.open(REVIEW / f"decoded-{n:06d}.jpg") as im:
            result.paste(im.resize((width, height), Image.Resampling.LANCZOS), ((k % cols) * width, (k // cols) * (height + 24)))
        draw.text(((k % cols) * width + 8, (k // cols) * (height + 24) + height + 4), f"{n/FPS:.3f}s / {n}", fill="#203b36")
    result.save(REVIEW / name, quality=97)


def main():
    REVIEW.mkdir(parents=True, exist_ok=True)
    film = OUT / "render/sunset-launch-v10.mp4"
    composite = read(OUT / "composite/composite-provenance.json")
    reads = read(OUT / "composite/readability-spec.json")
    timeline = read(SRC / "timeline.json")
    film_sha = sha(film)
    assert film_sha == composite["sha256"] and composite["video_encode_passes"] == 1
    probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(film)]))
    v = next(s for s in probe["streams"] if s["codec_type"] == "video")
    a = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    assert (v["width"], v["height"], v["codec_name"], v["pix_fmt"], v["r_frame_rate"]) == (W, H, "h264", "yuv420p", "30/1")
    assert int(v["nb_frames"]) == COUNT and abs(float(probe["format"]["duration"]) - 44) < .02
    assert (v["color_space"], v["color_primaries"], v["color_transfer"], v["color_range"]) == ("bt709", "bt709", "bt709", "tv")
    assert a["codec_name"] == "aac" and int(a["sample_rate"]) == 48000 and a["channels"] == 2
    data, offset, atoms = film.read_bytes(), 0, []
    while offset + 8 <= len(data):
        size, kind = struct.unpack_from(">I4s", data, offset)
        if size == 1:
            size, = struct.unpack_from(">Q", data, offset + 8)
        if size == 0:
            size = len(data) - offset
        assert size >= 8
        atoms.append(kind.decode("ascii"))
        offset += size
    assert offset == len(data) and atoms.index("moov") < atoms.index("mdat")
    paths = {
        "renderer": SRC / "render_launch.py", "timeline": SRC / "timeline.json",
        "fonts_provenance": SRC / "fonts-provenance.json",
        "logo": ROOT / ".publication/sunset-launch-v1/render/logo.png",
        "guide_pack": ROOT / "projects/sunset/public/packs/maintainer-handbook.json",
    }
    for key, path in paths.items():
        assert sha(path) == composite["source_hashes"][key] == reads["source_hashes"][key], key
    for family in read(SRC / "fonts-provenance.json")["fonts"]:
        assert family["license"] == "SIL Open Font License 1.1"
        for item in family["files"].values():
            assert sha(ROOT / item["path"]) == item["sha256"]
    manifest_path = ROOT / composite["actual_demo_manifest"]
    manifest = read(manifest_path)
    assert manifest == composite["actual_demo"]
    assert sha(manifest_path) == composite["actual_demo_manifest_sha256"] == timeline["actual_manifest_sha256"]
    assert sha(ROOT / manifest["source_capture_provenance"]) == manifest["source_capture_provenance_sha256"]
    capture_path = ROOT / manifest["source_capture_provenance"]
    assert sha(capture_path) == CAPTURE_SHA
    capture = read(capture_path)
    assert capture["dpr"] == 3 and capture["dimensions"] == [4320,2700]
    assert not capture["console_errors"] and capture["chain_mutations"] == 0
    assert capture["example_resource"] is True and capture["guide_onchain_release_claimed"] is False
    assert capture["underlying_git_steps_executed"] is False
    assert capture["blank_offline_before_file"]["onLine"] is False
    assert sha(ROOT / capture["source_pack"]["path"]) == capture["source_pack"]["sha256"] == GUIDE_SHA
    assert sha(ROOT / "projects/sunset/media/launch-v10/capture_handbook.mjs") == capture["capture_source_sha256"]
    downloaded = ROOT / capture["download"]["path"]
    public_sample = ROOT / "projects/sunset/public/try-maintainer-handbook.html"
    assert sha(downloaded) == capture["download"]["sha256"] == sha(public_sample)
    assert downloaded.stat().st_size == capture["download"]["bytes"]
    if "download_identity" in manifest:
        assert sha(ROOT / manifest["download_identity"]["path"]) == capture["download"]["sha256"]
        assert manifest["download_identity"]["bytes"] == capture["download"]["bytes"]
    for name in ("offline_before","checked_result","offline_after"):
        state=capture[name]
        assert state["onLine"] is False and state["resources"] == 0 and state["scheme"] == "file:"
        assert state["overflow"] is False
    for name in ("checked_result","offline_after"):
        state=capture[name]
        assert state["chapter"] == "Recover a lost commit"
        assert any(x["id"]=="recovery-inspect" and x["checked"] is True for x in state["checks"])
        assert "1 of 16 checks complete" in state["progress"]
    genuine=[]
    source_paths=set()
    capture_times={}
    capture_states={}
    for recording in capture["recordings"]:
        previous=-1
        for item in recording["samples"]:
            assert item["at"] > previous and item["capture_started_seconds"] <= item["at"]
            previous=item["at"]
            path=OUT / "footage" / recording["name"] / item["file"]
            check_png(path,item["sha256"])
            genuine.append(item["sha256"]);source_paths.add(str(path.relative_to(ROOT)))
            capture_times[str(path.relative_to(ROOT))]=item["at"]
            capture_states[str(path.relative_to(ROOT))]=(item["before"],item["after"])
            if "offline" in recording["name"]:
                for state in (item["before"],item["after"]):
                    assert state["onLine"] is False and state["resources"]==0 and state["scheme"]=="file:"
    retained=capture["retained_after_reload"]
    if retained:
        path=ROOT / retained["path"];check_png(path,retained["sha256"])
        source_paths.add(str(path.relative_to(ROOT)));genuine.append(retained["sha256"])
    for segment in manifest["segments"]:
        assert segment.get("max_editorial_scale",1) <= 2.2
        assert segment["source_dimensions"] == [4320,2700]
        previous=-math.inf
        offsets=[]
        for frame in segment["sourceframes"]:
            assert frame["film_time"] >= previous
            previous=frame["film_time"]
            assert frame["path"] in source_paths,("Unknown capture input",frame["path"])
            assert sha(ROOT / frame["path"]) == frame["sha256"]
            assert abs(frame["film_time"]-segment.get("playbackstart",segment["start"])-frame["time"])<1e-7
            if frame["path"] in capture_times:
                offsets.append(capture_times[frame["path"]]-frame["time"])
            if segment.get("network_offline_verified") and frame["path"] in capture_states:
                assert all(state["onLine"] is False and state["resources"]==0 and state["scheme"]=="file:" for state in capture_states[frame["path"]])
        assert not offsets or max(offsets)-min(offsets)<1e-7,("Source capture clock altered",segment["id"],offsets)
    assert len(genuine) >= 4 and len(set(genuine)) >= 3
    assert reads["frame_count"] == COUNT and len(reads["all_frames"]) == COUNT
    assert len(reads["essential_read_windows"]) == 16
    safe = reads["safe_bbox"]
    assert safe == [100, 70, 1820, 1010]
    read_frames = 0
    for entry in reads["essential_read_windows"]:
        start, end = entry["window"]
        words = sum(len(re.findall(r"[A-Za-z]+", line)) for line in entry["lines"])
        assert end - start + 1e-8 >= .3 * words + .5
        required = Counter(entry["lines"])
        for n in range(math.ceil(start * FPS - 1e-7), math.ceil(end * FPS - 1e-7)):
            present = Counter(item["text"] for item in reads["all_frames"][n]["text"])
            assert required <= present, ("Promised readable text missing", n, entry["id"], present)
            read_frames += 1
    forbidden = re.compile(r"https?://|www\.|Backbay Lounge|Kevin MacLeod|incompetech|7\s*\+\s*5|5\s*\+\s*7|Lantern|worksheet", re.I)
    expected_uses = []
    for n, row in enumerate(reads["all_frames"]):
        assert row["frame"] == n and abs(row["time"] - n / FPS) < 1e-8
        for i, item in enumerate(row["text"]):
            x0, y0, x1, y1 = item["bbox"]
            assert safe[0] <= x0 < x1 <= safe[2] and safe[1] <= y0 < y1 <= safe[3]
            assert item["solid_protected"] and item["contrast"] >= 4.5
            assert item["kind"] not in ("url", "music_credit") and not forbidden.search(item["text"])
            for other in row["text"][i + 1:]:
                aa, bb = item["bbox"], other["bbox"]
                assert max(aa[0], bb[0]) >= min(aa[2], bb[2]) or max(aa[1], bb[1]) >= min(aa[3], bb[3]), ("Essential overlap", n)
        if 28 <= n / FPS < 40:
            assert row["actual_recording"] is not None
            check_actual(row["actual_recording"], n / FPS, manifest)
            expected_uses.append(row["actual_recording"])
        else:
            assert row["actual_recording"] is None
    assert expected_uses == reads["actual_recording_frame_uses"] == composite["actual_demo_frame_uses"]
    assert len(expected_uses) == 360
    for n in range(1206, COUNT):
        texts = Counter(item["text"] for item in reads["all_frames"][n]["text"])
        assert Counter(["SUNSET", "Support once. Share forever."]) <= texts
    audio=read(OUT / "audio/qa.json")
    cues=read(SRC / "sound-cues.json")
    audio_sha=sha(OUT / "audio/mix.wav")
    assert audio_sha == AUDIO_SHA == audio["mix_sha256"] == composite["audio_master_sha256"]
    assert (audio["duration_seconds"],audio["sample_rate"],audio["channels"],audio["sample_count_per_channel"]) == (44,48000,2,2112000)
    assert all(audio[k] is False for k in ("voice_present","voice_generated","tts_or_voice_models_used","procedural_music_or_effects"))
    assert cues["voice"] is None
    assert {s["id"] for s in cues["sources"]} <= {"music","page-turn-1","page-turn-2","metallic-latch-release","mouse-clicks"}
    assert any(s["id"]=="music" for s in cues["sources"])
    for item in cues["sources"]:
        assert sha(ROOT / item["file"]) == item["sha256"]
        assert item["license"] == ("CC BY 4.0" if item["id"]=="music" else "CC0 1.0")
        if item["id"]!="music":
            assert "creativecommons.org/publicdomain/zero" in (ROOT / item["source_page_snapshot"]).read_text()
    for name,item in audio["stems"].items():
        assert sha(OUT / "audio" / name) == item["sha256"]
    assert composite["no_generated_voice"] and composite["no_product_url_or_music_credit_in_picture"]
    assert "Kevin MacLeod" in (SRC / "CREDITS.md").read_text()
    preserved = {
        ".publication/sunset-launch-v1/render/sunset-launch.mp4": "24e49095284f165a4346adbca0e2653bbea1080f8bf902b98c95a8700b866ad0",
        ".publication/sunset-launch-v2/sunset-launch-v2.mp4": "769948d737168652fdcf531faf47fd7ec183432d862b8149dff7e8d36bbef934",
        ".publication/sunset-launch-v3/sunset-launch-v3.mp4": "cf2eff815d253b2114d5745fcdd4edeef1a492d4e579df99ceed69f1b4dae1cb",
        ".publication/sunset-launch-v4/sunset-launch-v4.mp4": "d9d1c4b74e867da221cc6d8a97e0524576e0575e25e7899dd74db3e246bad42b",
        ".publication/sunset-launch-v5/sunset-launch-v5.mp4": "a90c5b30c86575db8d0960fa3e2a2b41d0d7e52d0e30db46245552628ab4204d",
        ".publication/sunset-launch-v6/sunset-launch-v6.mp4": "5ef32187788c9126d2a548c19b38243863aab2a99289b776672b6e3345b371d1",
        ".publication/sunset-launch-v7/sunset-launch-v7.mp4": "8c1f850dce269c420ca9553b548a3a030107a2be2dec31864cf30819a210de44",
        ".publication/sunset-launch-v8/sunset-launch-v8.mp4": "b2a96e376a2ab97c7cb8e82e69018eb6f004a5796c9ba45d15eaa29f691058a2",
    }
    preserved[".publication/sunset-launch-v9/render/sunset-launch-v9.mp4"]="f2f4d2e9cc7733af1c7dfa2491b2148217ba9857addd544931e1d710c5592319"
    for path, digest in preserved.items():
        assert sha(ROOT / path) == digest, ("Preserved film changed", path)
    points=sorted({round((w["window"][0]+w["window"][1])*FPS/2) for w in reads["essential_read_windows"]} | {0,24,84,135,195,258,291,324,408,492,564,618,684,774,850,870,900,930,960,990,1020,1050,1079,1119,1260,1319})
    boundaries=[0.6,3.3,5.7,7.9,10,12.5,15,18,19.8,21.6,24,28,32,36,40]
    boundaries += [s["start"] for s in manifest["segments"]]
    cuts=sorted({max(0,min(COUNT-1,round(t*FPS)+delta)) for t in boundaries for delta in (-6,-1,0,1,6)})
    dense={"opening-0-10":list(range(0,301,5)),"release-15-20":list(range(450,601,5)),"offline-28-36":list(range(840,1081,5))}
    samples=set(points+cuts+[n for values in dense.values() for n in values])
    native={850,870,900,930,960,990,1020,1050,1079,1119}
    minimum, probes, maximum_ui_error, ui_checks, black_run, black_max = math.inf, 0, 0., 0, 0, 0
    pipe = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(film), "-map", "0:v:0", "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for n in range(COUNT):
            raw = pipe.stdout.read(W * H * 3)
            assert len(raw) == W * H * 3, ("Incomplete decoded frame", n)
            im = Image.frombytes("RGB", (W,H), raw)
            histogram = im.resize((192,108), Image.Resampling.BOX).convert("L").histogram()
            black_run = black_run + 1 if sum(histogram[:3]) >= 192*108*.98 else 0
            black_max = max(black_max, black_run)
            for item in reads["all_frames"][n]["text"]:
                foreground = im.getpixel(tuple(item["probe_foreground_xy"]))
                background = im.getpixel(tuple(item["probe_background_xy"]))
                measured = ratio(foreground, background)
                minimum = min(minimum, measured)
                probes += 1
                assert measured >= 4.5, ("Encoded glyph contrast", n, item["text"], measured, foreground, background)
            use = reads["all_frames"][n]["actual_recording"]
            if use:
                roi, box, size = check_actual(use, n/FPS, manifest)
                expected = source(use["source_path"]).crop(roi).resize(size, Image.Resampling.LANCZOS)
                actual = im.crop(box)
                # Compare the real decoded delivery against its exact source ROI at a
                # fixed small grid; this tolerates H.264/YUV conversion, not a fake plate.
                expected = expected.resize((256,64), Image.Resampling.BOX)
                actual = actual.resize((256,64), Image.Resampling.BOX)
                error = max(ImageStat.Stat(ImageChops.difference(expected, actual)).mean)
                maximum_ui_error = max(maximum_ui_error, error)
                assert error <= 5, ("Decoded UI differs from genuine source ROI", n, error)
                ui_checks += 1
            if n in samples:
                im.save(REVIEW / f"decoded-{n:06d}.jpg", quality=96)
            if n in native:
                im.save(REVIEW / f"decoded-{n:06d}.png")
                im.resize((390,round(390*H/W)),Image.Resampling.LANCZOS).save(REVIEW / f"phone-{n:06d}.png")
            if n % 300 == 299:
                print(f"Verified {n+1}/{COUNT} decoded frames", flush=True)
        assert not pipe.stdout.read(1), "Extra decoded frames"
        stderr = pipe.stderr.read().decode()
        assert pipe.wait() == 0, stderr
    finally:
        if pipe.poll() is None:
            pipe.kill()
    (OUT / "decode.log").write_text(stderr)
    assert black_max < 6, ("Unexpected black interval", black_max/FPS)
    sheet(points, "beat-sheet.jpg")
    sheet(points, "phone-sheet-390.jpg", 390, 3)
    sheet(cuts, "cut-sheet.jpg", 384, 5)
    for name, indices in dense.items():
        sheet(indices, name + "-6fps.jpg", 390, 6)
    sheet(sorted(native), "actual-proof-sheet.jpg", 480, 3)
    levels = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(film), "-vn", "-af", "loudnorm=I=-15:TP=-2.5:LRA=9:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    assert levels.returncode == 0, levels.stderr
    (OUT / "audio-levels.log").write_text(levels.stderr)
    loud, _ = json.JSONDecoder().raw_decode(levels.stderr[levels.stderr.rfind("{"):])
    measured_lufs, measured_peak = float(loud["input_i"]), float(loud["input_tp"])
    assert -16 <= measured_lufs <= -14 and measured_peak <= -1.5
    assert abs(measured_lufs - audio["aac_320k"]["integrated_lufs"]) < .1
    assert abs(measured_peak - audio["aac_320k"]["true_peak_dbtp"]) < .1
    qa = {
        "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "objective_checks_passed_creative_and_listening_review_separate",
        "film_path": str(film.relative_to(ROOT)), "sha256": film_sha, "bytes": film.stat().st_size,
        "duration_seconds": 44, "dimensions": [W,H], "fps": FPS, "frames": COUNT,
        "video_codec": "h264", "pixel_format": "yuv420p", "color": "BT709 limited",
        "audio_codec": "aac", "audio_sample_rate": 48000, "audio_channels": 2,
        "faststart": True, "full_decode": "passed", "video_encode_passes": 1,
        "unexpected_black_intervals": 0, "essential_read_windows": len(reads["essential_read_windows"]),
        "read_window_frame_assertions": read_frames, "required_text_counter_checked_across_all_kinds": True,
        "essential_text_probes": probes, "minimum_decoded_text_contrast": round(minimum,4),
        "essential_safe_bbox": safe, "onscreen_product_url": False, "onscreen_music_credit": False,
        "source_hashes": composite["source_hashes"], "font_source_hashes_verified": True,
        "genuine_png_count": len(genuine), "genuine_timed_png_samples": sum(len(r["samples"]) for r in capture["recordings"]), "retained_reload_still": True, "genuine_unique_pixel_states": len(set(genuine)),
        "capture_method": capture["capture_method"], "browser_offline_before_file_navigation": True,
        "recording_sampling": "Genuine native DPR3 screenshot samples held by original elapsed timestamps at30fps delivery; not30 unique browser frames/s",
        "actual_demo_output_frames": ui_checks, "retained_plate_frames": 120,
        "retained_plate_original_film_clock": 35.9666666667, "decoded_actual_roi_identity_checks": ui_checks,
        "maximum_ui_roi_mean_absolute_channel_error": round(maximum_ui_error,4),
        "actual_manifest_sha256": sha(manifest_path), "motion_interpolation": False,
        "editorial_magnification": {"allowed": True, "maximum_scale": max(u["scale"] for u in expected_uses), "resampling": "LANCZOS", "native_detail_added": False},
        "audio_master_sha256": audio_sha, "audio_source_ids": [s["id"] for s in cues["sources"]],
        "voice_present": False, "tts_or_voice_models_used": False,
        "music_and_licensed_recorded_foley_only": True,
        "loudness_lufs": measured_lufs, "true_peak_dbtp": measured_peak,
        "perceptual_listening_verified": False, "creative_review_verified": False,
        "preserved_versions": preserved,
        "review_sheets": ["review/beat-sheet.jpg","review/phone-sheet-390.jpg","review/cut-sheet.jpg","review/opening-0-10-6fps.jpg","review/release-15-20-6fps.jpg","review/offline-28-36-6fps.jpg","review/actual-proof-sheet.jpg"],
        "guide_example_resource": True, "guide_onchain_release_claimed": False, "underlying_git_steps_executed": False,
        "chain_mutations": 0, "verifier_source_sha256": sha(Path(__file__)),
    }
    (OUT / "ffprobe.json").write_text(json.dumps(probe, indent=2) + "\n")
    (OUT / "media-qa.json").write_text(json.dumps(qa, indent=2) + "\n")
    print(json.dumps(qa, indent=2))


if __name__ == "__main__":
    main()
