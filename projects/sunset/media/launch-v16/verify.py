#!/usr/bin/env python3
"""Verify the actual HyperFrames MP4, raw-source UI timing/pixels and older films.

verify.py MOVIE --composition PREPARED_DIR --geometry ui-geometry.json --output NEW_REPORT_DIR
Requires Python 3.11+ without optimization (-O/-OO or PYTHONOPTIMIZE).
Required geometry JSON schema (all 81 placements, sorted frames 492 through 572):
  {
    "composition_sha256": "SHA256 of the exact prepared index.html",
    "viewport": [1920, 1080],
    "driver": "HyperFrames __player.renderSeek exact + seekcompletion",
    "placements": [{
      "frame": 492, "time": 16.4, "actualTimelineTime": 16.4,
      "sourcePath": ".publication/sunset-launch-v15/capture/unchecked.png",
      "sourceAt": 0, "speed": 1, "noReloadClaim": true,
      "imageOpacity": "1", "imageVisibility": "visible",
      "sourceBounds": [630, 600, 1462.13797, 934.82141],
      "destinationBounds": {
        "left": 168, "top": 355, "right": 1752.390625, "bottom": 992.5,
        "width": 1584.390625, "height": 637.5
      },
      "pixelTransform": {
        "scaleX": 1.904, "scaleY": 1.904,
        "translateX": -1031.52, "translateY": -787.4
      }
    }]
  }
The one placement above illustrates required fields; collect actual values for
all 81 frames from the compiled HF preview, after renderSeek(frame/30,{exact:true})
and __hfWaitForSeekCompletion. Spread uiPlacements(frame), then add frame, actual
master timeline time and computed image opacity/visibility. The driver string
must identify renderSeek. Additional collected fields are retained but optional.
Uses Python's standard library and FFmpeg/FFprobe; never renders the film itself.
"""
import sys

if sys.flags.optimize:
    raise SystemExit('Verification requires assertions: run Python without -O/-OO or PYTHONOPTIMIZE.')
if sys.version_info < (3, 11):
    raise SystemExit('Python 3.11 or newer is required.')

import argparse
import hashlib
import json
import math
import re
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / '.publication/sunset-launch-v16'
CAPTURE = ROOT / '.publication/sunset-launch-v15/capture/capture-provenance.json'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run(args):
    return subprocess.check_output(args, stderr=subprocess.STDOUT).decode()


def atoms(path):
    result = []
    with path.open('rb') as stream:
        while stream.tell() < path.stat().st_size:
            offset = stream.tell()
            size, kind = struct.unpack('>I4s', stream.read(8))
            if size == 1:
                size = struct.unpack('>Q', stream.read(8))[0]
            if size == 0:
                size = path.stat().st_size - offset
            assert size >= 8 and offset + size <= path.stat().st_size
            result.append(kind.decode('ascii'))
            stream.seek(offset + size)
    assert result.index('moov') < result.index('mdat'), result
    return result


def rgb_crop(data, stride, left, top, width, height):
    return b''.join(data[(y * stride + left) * 3:(y * stride + left + width) * 3] for y in range(top, top + height))


def mae(a, b):
    assert len(a) == len(b) and a
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def verify_ui(movie, geometry, manifest):
    capture = json.loads(CAPTURE.read_text())
    assert capture['browser_offline_before_file_open'] and not capture['performed_underlying_handbook_procedure']
    assert capture['playback_speed'] == 1 and capture['viewport'] == [1920, 1080]
    assert sha(CAPTURE) == manifest['capture']['sha256']
    for item in capture['files'].values():
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
    samples = capture['samples']
    assert samples[0]['at'] == 0 and abs(samples[1]['at'] - 1.4736603630008176) < 1e-10
    assert samples[0]['sha256'] == 'db312ca87fb82aeff8fbd2683bf8f46b4d2c65061a06ba6146688eef89e8b7e1'
    assert samples[1]['sha256'] == '3df2cdf571d86334dd0709ecc1a1c20dd0dfd0c589537666fe77b087ef219cfa'
    assert geometry['composition_sha256'] == manifest['prepared']['sha256']
    assert geometry['viewport'] == [1920, 1080] and 'renderSeek' in geometry['driver']
    placements = geometry['placements']
    assert [p['frame'] for p in placements] == list(range(492, 573))
    decoder = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(movie), '-vf',
        'select=between(n\\,492\\,572)', '-frames:v', '81', '-fps_mode', 'passthrough',
        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    errors, cache = [], {}
    def expected_crop(key):
        if key not in cache:
            path, scaled_w, scaled_h, cx, cy, w, h = key
            cache[key] = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(ROOT / path),
                '-vf', f'scale={scaled_w}:{scaled_h}:flags=bilinear,format=rgb24,crop={w}:{h}:{cx}:{cy}',
                '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
        return cache[key]
    try:
        for item in placements:
            n, source_time = item['frame'], item['frame'] / 30 - 16.4
            sample = next(s for s in reversed(samples) if s['at'] <= source_time + 1e-9)
            assert sample['path'] == item['sourcePath'] and 'retained' not in item['sourcePath'], item
            assert abs(item['sourceAt'] - source_time) < 1e-7 and abs(item['time'] - n / 30) < 1e-7
            assert item['speed'] == 1 and item['noReloadClaim'] is True
            assert abs(item['actualTimelineTime'] - n / 30) < 1e-5
            assert item['imageOpacity'] == '1' and item['imageVisibility'] == 'visible'
            x0, y0, x1, y1 = item['sourceBounds']
            assert 629.95 <= x0 < x1 <= 1562.05 and 599.95 <= y0 < y1 <= 975.05, item
            d, transform = item['destinationBounds'], item['pixelTransform']
            sx, sy, tx, ty = (transform[k] for k in ['scaleX', 'scaleY', 'translateX', 'translateY'])
            assert sx > 0 and abs(sx - sy) < 1e-5, transform
            assert abs((d['left'] - tx) / sx - x0) < .02 and abs((d['top'] - ty) / sy - y0) < .02
            assert abs(d['width'] / sx - (x1 - x0)) < .02 and abs(d['height'] / sy - (y1 - y0)) < .02
            # Trim six edge pixels; compare the actual native browser content, not its shadow/border.
            left, top, right, bottom = math.ceil(d['left']) + 6, math.ceil(d['top']) + 6, math.floor(d['right']) - 6, math.floor(d['bottom']) - 6
            assert 0 <= left < right <= 1920 and 0 <= top < bottom <= 1080
            width, height = right - left, bottom - top
            key = (sample['path'], round(1920 * sx), round(1080 * sy), round(left - tx), round(top - ty), width, height)
            expected = expected_crop(key)
            frame = decoder.stdout.read(1920 * 1080 * 3)
            assert len(frame) == 1920 * 1080 * 3, n
            actual = rgb_crop(frame, 1920, left, top, width, height)
            error = mae(actual, expected)
            # A white page makes global MAE insensitive to a wrong checkbox. Verify
            # the independently timed state also wins in its small native region.
            marker = (math.ceil(tx + 662 * sx) - left, math.ceil(ty + 775 * sy) - top,
                      round(27 * sx), round(27 * sy))
            mx, my, mw, mh = marker
            assert 0 <= mx < mx + mw <= width and 0 <= my < my + mh <= height
            actual_marker = rgb_crop(actual, width, *marker)
            correct_error = mae(actual_marker, rgb_crop(expected, width, *marker))
            opposite = samples[1 if sample is samples[0] else 0]['path']
            wrong_error = mae(actual_marker, rgb_crop(expected_crop((opposite, *key[1:])), width, *marker))
            assert correct_error < 20 and correct_error + 1 < wrong_error, (n, correct_error, wrong_error)
            errors.append({'frame': n, 'source_at': source_time, 'source_png': sample['path'],
                           'source_sha256': sample['sha256'], 'mean_channel_error_255': round(error, 5),
                           'checkbox_correct_mae': round(correct_error, 5), 'checkbox_opposite_mae': round(wrong_error, 5)})
            assert error < 6, (n, error)
    finally:
        decoder.stdout.close()
        if decoder.poll() is None:
            decoder.terminate()
        decoder.wait()
    return {'frames': 81, 'mapping': '16.4–19.1 film seconds = original source 0–2.7 seconds at 1x; no reload claim',
            'capture_sha256': sha(CAPTURE), 'max_mean_channel_error_255': max(p['mean_channel_error_255'] for p in errors),
            'comparison': 'Encoded RGB crop vs bilinear resize/translation of independently timestamp-selected native PNG; six-pixel edge trim',
            'per_frame': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('movie', type=Path)
    parser.add_argument('--composition', type=Path, required=True)
    parser.add_argument('--geometry', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), f'Refusing to overwrite {args.output}'
    manifest = json.loads((args.composition / 'source-manifest.json').read_text())
    assert manifest['versions'] == {'hyperframes': '0.9.16', 'gsap': '3.15.1'}
    assert sha(args.composition / 'index.html') == manifest['prepared']['sha256']
    for name, item in manifest['assets'].items():
        assert sha(args.composition / 'assets' / name) == item['sha256'], name
    probe = json.loads(run(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(args.movie)]))
    assert len(probe['streams']) == 2
    video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    audio = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
    assert (video['width'], video['height'], video['codec_name'], video['pix_fmt']) == (1920, 1080, 'h264', 'yuv420p')
    assert video['r_frame_rate'] == video['avg_frame_rate'] == '30/1' and int(video['nb_read_frames']) == 885
    assert abs(float(video['duration']) - 29.5) < .001 and abs(float(probe['format']['duration']) - 29.5) < .05
    assert video['color_range'] == 'tv' and all(video[k] == 'bt709' for k in ['color_space', 'color_primaries', 'color_transfer'])
    assert (audio['codec_name'], audio['channels'], audio['sample_rate']) == ('aac', 2, '48000')
    assert abs(float(audio['duration']) - 29.5) < .05
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(args.movie), '-f', 'null', '-'], check=True)
    order = atoms(args.movie)
    loudness = run(['ffmpeg', '-hide_banner', '-i', str(args.movie), '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-'])
    integrated = float(re.findall(r'I:\s*(-?[\d.]+) LUFS', loudness)[-1])
    peak = float(re.findall(r'Peak:\s*(-?[\d.]+) dBFS', loudness)[-1])
    assert -16.5 <= integrated <= -13.5 and peak <= -1.5, (integrated, peak)
    previous = json.loads((ROOT / '.publication/sunset-launch-v15/verification/final-report.json').read_text())
    retained = {**previous['older_movies_preserved'], previous['movie']: previous['sha256']}
    assert len(retained) == 16
    for path, expected in retained.items():
        assert sha(ROOT / path) == expected, path
    ui = verify_ui(args.movie, json.loads(args.geometry.read_text()), manifest)
    result = {'ok': True, 'movie': str(args.movie), 'sha256': sha(args.movie), 'bytes': args.movie.stat().st_size,
              'probe': probe, 'atoms': order, 'full_decode': True, 'encoded_integrated_lufs': integrated,
              'encoded_true_peak_dbtp': peak, 'genuine_ui': ui, 'older_movies_preserved': retained,
              'composition_sha256': manifest['prepared']['sha256'], 'geometry_sha256': sha(args.geometry),
              'limits': ['Original timed PNG states, not continuous browser footage.', 'Technical checks do not establish creative approval or perceptual listening.']}
    args.output.mkdir(parents=True)
    (args.output / 'encoded-loudness.txt').write_text(loudness)
    (args.output / 'final-report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'ok': True, 'sha256': result['sha256'], 'frames': 885, 'ui_frames': ui['frames'],
                      'ui_max_mae': ui['max_mean_channel_error_255'], 'lufs': integrated, 'true_peak': peak,
                      'preserved_movies': len(retained)}, indent=2))


if __name__ == '__main__':
    main()
