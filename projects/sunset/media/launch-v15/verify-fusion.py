#!/usr/bin/env python3
"""Independent export/source checks; genuine UI is compared to raw browser pixels."""
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / '.publication/sunset-launch-v15'
MOVIE = OUT / 'sunset-launch-fusion.mp4'
SILENT = OUT / 'sunset-fusion-silent-40s.mp4'


def sha(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()


def run(args):
    return subprocess.check_output(args, stderr=subprocess.STDOUT).decode()


def packet_hash(path):
    return run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0',
                '-c', 'copy', '-f', 'hash', '-hash', 'sha256', '-']).strip()


def atoms(path):
    data, offset, result = path.read_bytes(), 0, []
    while offset + 8 <= len(data):
        size, kind = struct.unpack_from('>I4s', data, offset)
        if size == 1:
            size = struct.unpack_from('>Q', data, offset + 8)[0]
        if size == 0:
            size = len(data) - offset
        assert size >= 8 and offset + size <= len(data), (offset, size)
        result.append(kind.decode('ascii'))
        offset += size
    assert result.index('moov') < result.index('mdat'), result
    return result


def verify_ui(manifest):
    capture = json.loads((ROOT / manifest['capture_manifest']['path']).read_text())
    assert capture['browser_offline_before_file_open'] is True
    assert capture['performed_underlying_handbook_procedure'] is False
    assert capture['playback_speed'] == 1
    for item in capture['files'].values():
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
    placements = manifest['browser_frames']
    assert [p['output_frame'] for p in placements] == list(range(780, 942))
    destination = OUT / 'verification/ui'
    destination.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(MOVIE), '-vf',
                    'select=between(n\\,780\\,941)', '-fps_mode', 'passthrough',
                    '-start_number', '780', str(destination / '%06d.png')], check=True)
    max_error, errors = 0, []
    for item in placements:
        n = item['output_frame']
        source_time = min(5, max(0, n / 30 - 26))
        assert abs(item['source_time'] - source_time) < 1e-7, item
        sample = next(x for x in reversed(capture['samples']) if x['at'] <= source_time + 1e-9)
        assert item['source_png'] == sample['path'], item
        assert item['source_sha256'] == sample['sha256'], item
        x0, y0, x1, y1 = item['source_crop']
        # Parent ROI excludes all command pixels in the actual browser take.
        assert 630 <= x0 < x1 <= 1562 and 600 <= y0 < y1 <= 975, item
        dx0, dy0, dx1, dy1 = item['destination_bbox']
        assert 0 <= dx0 < dx1 <= 1920 and 0 <= dy0 < dy1 <= 1080, item
        expected = Image.open(ROOT / sample['path']).convert('RGB').crop((x0, y0, x1, y1))
        expected = expected.resize((dx1 - dx0, dy1 - dy0), Image.Resampling.LANCZOS)
        actual = Image.open(destination / f'{n:06d}.png').convert('RGB').crop((dx0, dy0, dx1, dy1))
        a, b = np.asarray(actual).astype(float), np.asarray(expected).astype(float)
        error = float(np.abs(a[5:-5, 5:-5] - b[5:-5, 5:-5]).mean())
        assert error < 6, (n, error)
        max_error = max(max_error, error)
        errors.append({'frame': n, 'mean_channel_error_255': round(error, 5)})
    return {'frames': len(placements), 'max_mean_channel_error_255': max_error,
            'mapping': '26–31s source at1x;31–31.4s editorial hold of the retained state',
            'native_browser_pngs': len(capture['samples']),
            'capture_manifest_sha256': sha(ROOT / manifest['capture_manifest']['path']),
            'per_frame': errors}


def main():
    manifest = json.loads((OUT / 'render-manifest.json').read_text())
    probe = json.loads(run(['ffprobe', '-v', 'error', '-count_frames',
                            '-show_streams', '-show_format', '-of', 'json', str(MOVIE)]))
    videos = [s for s in probe['streams'] if s['codec_type'] == 'video']
    audio = [s for s in probe['streams'] if s['codec_type'] == 'audio']
    assert len(videos) == len(audio) == 1 and len(probe['streams']) == 2, probe
    video, sound = videos[0], audio[0]
    assert (video['width'], video['height']) == (1920, 1080)
    assert video['codec_name'] == 'h264' and video['pix_fmt'] == 'yuv420p'
    assert video['r_frame_rate'] == '30/1' and int(video['nb_read_frames']) == 1200
    assert abs(float(video['duration']) - 40) < .001
    assert video['color_range'] == 'tv'
    assert all(video[k] == 'bt709' for k in ['color_space', 'color_primaries', 'color_transfer'])
    assert sound['codec_name'] == 'aac' and sound['channels'] == 2 and sound['sample_rate'] == '48000'
    assert abs(float(sound['duration']) - 40) < .05
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(MOVIE), '-f', 'null', '-'], check=True)
    assert packet_hash(SILENT) == packet_hash(MOVIE)
    for item in manifest['asset_files'] + manifest['helpers'] + manifest['fonts']:
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
    assert sha(ROOT / manifest['capture_manifest']['path']) == manifest['capture_manifest']['sha256']
    qa = json.loads((OUT / 'audio/qa.json').read_text())
    assert sha(OUT / 'audio/mix.wav') == qa['master_sha256']
    loudness = run(['ffmpeg', '-hide_banner', '-i', str(MOVIE), '-vn', '-af',
                    'ebur128=peak=true', '-f', 'null', '-'])
    integrated = float(re.findall(r'I:\s*(-?[\d.]+) LUFS', loudness)[-1])
    peak = float(re.findall(r'Peak:\s*(-?[\d.]+) dBFS', loudness)[-1])
    assert -16.5 <= integrated <= -13.5 and peak <= -1.5, (integrated, peak)
    (OUT / 'verification').mkdir(exist_ok=True)
    (OUT / 'verification/encoded-loudness.txt').write_text(loudness)
    previous = json.loads((ROOT / '.publication/sunset-launch-v14/independent-verification.json').read_text())
    retained = dict(previous['older_movies_preserved'])
    retained.update({x['path']: x['sha256'] for x in previous['outputs']})
    for path, expected in retained.items():
        assert sha(ROOT / path) == expected, path
    ui = verify_ui(manifest)
    result = {'movie': str(MOVIE.relative_to(ROOT)), 'sha256': sha(MOVIE),
              'bytes': MOVIE.stat().st_size, 'probe': probe, 'atoms': atoms(MOVIE),
              'full_decode': True, 'video_stream_copy_identity': True,
              'encoded_integrated_lufs': integrated, 'encoded_true_peak_dbtp': peak,
              'audio_source_sha256': qa['master_sha256'], 'genuine_ui': ui,
              'older_movies_preserved': retained,
              'limits': ['Native screenshot states, not continuous30fps browser footage.',
                         'Technical checks do not establish creative approval or perceptual listening.']}
    (OUT / 'verification/final-report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['probe', 'genuine_ui', 'older_movies_preserved']}, indent=2))
    print(json.dumps({'genuine_ui_frames': ui['frames'], 'max_ui_error': ui['max_mean_channel_error_255'],
                      'older_movies_preserved': len(retained)}))


if __name__ == '__main__':
    main()
