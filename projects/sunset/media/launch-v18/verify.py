#!/usr/bin/env python3
"""Verify the actual HyperFrames MP4, raw-source UI timing/pixels and older films.

verify.py MOVIE --composition PREPARED_DIR --geometry ui-geometry.json --output NEW_REPORT_DIR
Requires Python 3.11+ without optimization (-O/-OO or PYTHONOPTIMIZE).
Required geometry: {composition_sha256, viewport:[1920,1080], driver containing
"renderSeek", placements:[81 sorted frame entries 492..572]}. Each entry has frame,
time, actualTimelineTime, sourceAt, state (initial/result), query, title, speed:1,
noReloadClaim:true, and fragments:[search,chapter]. Each fragment has id, sourcePath,
sourceBounds:[x0,y0,x1,y1], destinationBounds:{left,top,right,bottom,width,height},
pixelTransform:{scaleX,scaleY,translateX,translateY}, imageOpacity:"1", and
imageVisibility:"visible". Collect actual DOM values after the compiled HF player's
renderSeek(frame/30,{exact:true}) and __hfWaitForSeekCompletion; add each fragment's
live image identity/visibility. Geometry also records logo_source_sha256, logo_staged_sha256, logo_view_box and
brands at1.2/28.2s: loadedBytesSha256, naturalWidth/Height, renderedBounds, scaleX/Y,
fontSize, iconWidth, gap, tracking, weight, word and colour. Both fragments must use the same timestamp-selected
native PNG. The original capture determines the query and chapter title separately.
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
OUT = ROOT / '.publication/sunset-launch-v18'
CAPTURE = OUT / 'capture/capture-provenance.json'


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
    assert capture['source_unchanged'] and capture['browser_offline_before_file_open']
    assert not capture['performed_underlying_handbook_procedure'] and not capture['app_or_pack_edits']
    assert capture['chain_mutations'] == 0 and capture['playback_speed'] == 1
    assert capture['viewport'] == [1920, 1080] and capture['source_window_seconds'] == [0, 2.7]
    assert sha(CAPTURE) == manifest['capture']['sha256']
    for item in capture['files'].values():
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
    assert capture['files']['html']['sha256'] == '7133b9acd18dc6ee55256d817fbd7872e9e2ec4f2cd625a88fff6ab6b69a621a'
    samples = capture['samples']
    assert [s['name'] for s in samples] == ['initial', 'result'] and samples[0]['at'] == 0
    assert abs(samples[1]['at'] - 1.3277030990011554) < 1e-10
    assert samples[0]['sha256'] == '911a9069e9b7feb45127fdee3d058daf4e83cc2783c742792d3327d3335d3136'
    assert samples[1]['sha256'] == '2510e2c2cd058532e6a456946bf1d42179003438207d4192257caa2cf3d1431c'
    assert [(s['query'], s['title']) for s in samples] == [('', 'Prepare a public release'), ('successor', 'Hand over maintainership')]
    for key, sample in zip(['before', 'after'], samples):
        observed = capture[key]
        assert not observed['online'] and observed['scheme'] == 'file:' and observed['resources'] == 0
        assert (observed['query'], observed['title']) == (sample['query'], sample['title'])
    safe = {'search': [350, 305, 610, 425], 'chapter': [630, 305, 1562, 525]}
    assert capture['native_rois'] == safe
    markers = {'search': [360, 340, 596, 385], 'chapter': [665, 337, 1220, 383]}
    assert capture['localized_state_rois'] == {'query': markers['search'], 'chapter_title': markers['chapter']}
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
            assert item['state'] == sample['name'] and item['query'] == sample['query'] and item['title'] == sample['title']
            assert abs(item['sourceAt'] - source_time) < 1e-7 and abs(item['time'] - n / 30) < 1e-7
            assert item['speed'] == 1 and item['noReloadClaim'] is True
            assert abs(item['actualTimelineTime'] - n / 30) < 1e-5
            assert sorted(f['id'] for f in item['fragments']) == ['chapter', 'search']
            frame = decoder.stdout.read(1920 * 1080 * 3)
            assert len(frame) == 1920 * 1080 * 3, n
            fragments = []
            for fragment in item['fragments']:
                identity = fragment['id']
                assert fragment['sourcePath'] == sample['path'], (n, identity)
                assert fragment['imageOpacity'] == '1' and fragment['imageVisibility'] == 'visible'
                x0, y0, x1, y1 = fragment['sourceBounds']; rx0, ry0, rx1, ry1 = safe[identity]
                assert rx0-.05 <= x0 < x1 <= rx1+.05 and ry0-.05 <= y0 < y1 <= ry1+.05
                # These two narrow ROIs contain only search/status and title/first prose,
                # and end far above both real fieldsets/progress and any command content.
                assert y1 < min(capture[k]['boxes']['fieldset']['top'] for k in ['before', 'after'])
                assert y1 < min(capture[k]['boxes']['#guide-progress']['top'] for k in ['before', 'after'])
                d, transform = fragment['destinationBounds'], fragment['pixelTransform']
                sx, sy, tx, ty = (transform[k] for k in ['scaleX', 'scaleY', 'translateX', 'translateY'])
                assert sx > 0 and abs(sx-sy) < 1e-5
                assert abs((d['left']-tx)/sx-x0) < .02 and abs((d['top']-ty)/sy-y0) < .02
                assert abs(d['width']/sx-(x1-x0)) < .02 and abs(d['height']/sy-(y1-y0)) < .02
                left, top, right, bottom = math.ceil(d['left'])+6, math.ceil(d['top'])+6, math.floor(d['right'])-6, math.floor(d['bottom'])-6
                assert 0 <= left < right <= 1920 and 0 <= top < bottom <= 1080
                width, height = right-left, bottom-top
                key = (sample['path'], round(1920*sx), round(1080*sy), round(left-tx), round(top-ty), width, height)
                expected = expected_crop(key); actual = rgb_crop(frame, 1920, left, top, width, height)
                error = mae(actual, expected)
                mx0, my0, mx1, my1 = markers[identity]
                marker = (math.ceil(tx+mx0*sx)-left, math.ceil(ty+my0*sy)-top, round((mx1-mx0)*sx), round((my1-my0)*sy))
                mx, my, mw, mh = marker
                assert 0 <= mx < mx+mw <= width and 0 <= my < my+mh <= height
                actual_marker = rgb_crop(actual, width, *marker)
                correct_error = mae(actual_marker, rgb_crop(expected, width, *marker))
                opposite = samples[1 if sample is samples[0] else 0]['path']
                wrong_error = mae(actual_marker, rgb_crop(expected_crop((opposite, *key[1:])), width, *marker))
                assert error < 6 and correct_error < 20 and correct_error+1 < wrong_error, (n, identity, error, correct_error, wrong_error)
                fragments.append({'id': identity, 'mean_channel_error_255': round(error, 5),
                    'state_correct_mae': round(correct_error, 5), 'state_opposite_mae': round(wrong_error, 5)})
            errors.append({'frame': n, 'source_at': source_time, 'state': sample['name'], 'query': sample['query'],
                'title': sample['title'], 'source_png': sample['path'], 'source_sha256': sample['sha256'], 'fragments': fragments})
    finally:
        decoder.stdout.close()
        if decoder.poll() is None:
            decoder.terminate()
        decoder.wait()
    comparisons = [f for p in errors for f in p['fragments']]
    return {'frames': 81, 'fragments': len(comparisons), 'mapping': '16.4–19.1 film = source0–2.7 at1x; actual search successor selects Hand over maintainership; no chapter-click/reload/procedure claim',
        'capture_sha256': sha(CAPTURE), 'max_mean_channel_error_255': max(f['mean_channel_error_255'] for f in comparisons),
        'max_state_correct_mae': max(f['state_correct_mae'] for f in comparisons),
        'min_state_opposite_mae': min(f['state_opposite_mae'] for f in comparisons),
        'min_state_winning_margin': min(f['state_opposite_mae']-f['state_correct_mae'] for f in comparisons), 'per_frame': errors}


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
    assert sha(args.composition / 'assets/original-logo.svg') == sha(ROOT / 'projects/sunset/public/icon.svg') == manifest['assets']['original-logo.svg']['sha256']
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
    previous = json.loads((ROOT / '.publication/sunset-launch-v17/verification-delivery/final-report.json').read_text())
    retained = {**previous['older_movies_preserved'], previous['movie']: previous['sha256']}
    assert len(retained) == 18
    for path, expected in retained.items():
        assert sha(ROOT / path) == expected, path
    geometry = json.loads(args.geometry.read_text())
    original_logo = sha(ROOT / 'projects/sunset/public/icon.svg')
    assert geometry['logo_source_sha256'] == geometry['logo_staged_sha256'] == original_logo
    assert geometry['logo_view_box'] == '0 0 64 64'
    assert [b['time'] for b in geometry['brands']] == [1.2, 28.2]
    for brand, factor in zip(geometry['brands'], [4, 6]):
        assert brand['loadedBytesSha256'] == original_logo and brand['naturalWidth'] > 0
        assert brand['naturalWidth'] == brand['naturalHeight']
        assert abs(brand['renderedBounds']['width']-brand['renderedBounds']['height']) < .01
        assert abs(brand['scaleX']-brand['scaleY']) < 1e-5
        for key, base in [('fontSize', 26), ('iconWidth', 36), ('gap', 12), ('tracking', 3)]:
            assert abs(brand[key]-base*factor) < .01, (key, brand[key])
        assert brand['weight'] == 680 and brand['word'] == 'SUNSET' and brand['colour'] == 'rgb(41, 45, 39)'
    ui = verify_ui(args.movie, geometry, manifest)
    result = {'ok': True, 'movie': str(args.movie), 'sha256': sha(args.movie), 'bytes': args.movie.stat().st_size,
              'probe': probe, 'atoms': order, 'full_decode': True, 'encoded_integrated_lufs': integrated,
              'encoded_true_peak_dbtp': peak, 'genuine_ui': ui, 'older_movies_preserved': retained,
              'composition_sha256': manifest['prepared']['sha256'], 'geometry_sha256': sha(args.geometry),
              'original_logo_sha256': original_logo, 'brand_geometry': geometry['brands'],
              'limits': ['Original timed PNG states, not continuous browser footage.', 'Technical checks do not establish creative approval or perceptual listening.']}
    args.output.mkdir(parents=True)
    (args.output / 'encoded-loudness.txt').write_text(loudness)
    (args.output / 'final-report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'ok': True, 'sha256': result['sha256'], 'frames': 885, 'ui_frames': ui['frames'],
                      'ui_max_mae': ui['max_mean_channel_error_255'], 'lufs': integrated, 'true_peak': peak,
                      'preserved_movies': len(retained)}, indent=2))


if __name__ == '__main__':
    main()
