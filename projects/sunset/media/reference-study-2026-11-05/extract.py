"""Decode every supplied reference frame, preserve PTS and make indexed atlases.

Read-only inputs; reference pixels/audio and generated analysis stay ignored.
Metrics nominate changes for visual inspection; they do not identify editing tools.
"""
from pathlib import Path
import hashlib
import json
import math
import subprocess

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
INPUT = Path('/home/citrux/Downloads/refs/drafff')
OUT = ROOT / '.publication/sunset-reference-study-20261105'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(*args):
    return subprocess.check_output(list(map(str, args)))


def study(path, alias):
    folder = OUT / alias
    frames = folder / 'frames'
    atlases = folder / 'atlases'
    frames.mkdir(parents=True, exist_ok=True)
    atlases.mkdir(parents=True, exist_ok=True)
    identity = sha(path)
    probe = json.loads(command('ffprobe', '-v', 'error', '-count_frames',
                              '-show_streams', '-show_format', '-of', 'json', path))
    video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    timing = json.loads(command('ffprobe', '-v', 'error', '-select_streams', 'v:0',
                               '-show_frames', '-show_entries',
                               'frame=best_effort_timestamp_time,pkt_duration_time,pict_type,key_frame',
                               '-of', 'json', path))['frames']
    count = int(video['nb_read_frames'])
    assert len(timing) == count
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-xerror', '-y',
                    '-i', str(path), '-map', '0:v:0', '-fps_mode', 'passthrough',
                    '-start_number', '0', str(frames / '%06d.png')], check=True)
    paths = sorted(frames.glob('*.png'))
    assert len(paths) == count
    records, previous, previous_hist = [], None, None
    for n, (image_path, timestamp) in enumerate(zip(paths, timing)):
        assert image_path.name == f'{n:06d}.png'
        with Image.open(image_path) as image:
            assert image.size == (video['width'], video['height'])
            image.load()
            pixels = np.array(image.convert('RGB').resize((192, 144)), dtype=np.float32) / 255
        grey = pixels.mean(axis=2)
        hist = np.concatenate([np.histogram(pixels[:, :, c], bins=16, range=(0, 1))[0]
                               for c in range(3)]).astype(float) / (192 * 144 * 3)
        records.append({'frame': n, 'pts': float(timestamp['best_effort_timestamp_time']),
                        'duration': float(timestamp.get('pkt_duration_time', 1 / eval_rate(video['avg_frame_rate']))),
                        'pict_type': timestamp['pict_type'], 'path': str(image_path.relative_to(ROOT)),
                        'sha256': sha(image_path), 'mean_rgb': pixels.mean(axis=(0, 1)).tolist(),
                        'luma_mean': float(grey.mean()), 'luma_std': float(grey.std()),
                        'dark_fraction': float((grey < .025).mean()),
                        'bright_fraction': float((grey > .96).mean()),
                        'previous_frame_mae': None if previous is None else float(np.abs(pixels - previous).mean()),
                        'histogram_l1': None if previous_hist is None else float(np.abs(hist - previous_hist).sum())})
        previous, previous_hist = pixels, hist
    assert all(a['pts'] < b['pts'] for a, b in zip(records, records[1:]))
    sheets = []
    cell_w, cell_h = 320, round(320 * video['height'] / video['width'])
    for start in range(0, count, 30):
        selected = records[start:start + 30]
        sheet = Image.new('RGB', (6 * cell_w, 5 * (cell_h + 24)), '#ece9e1')
        draw = ImageDraw.Draw(sheet)
        for k, item in enumerate(selected):
            x, y = (k % 6) * cell_w, (k // 6) * (cell_h + 24)
            with Image.open(ROOT / item['path']) as image:
                sheet.paste(image.convert('RGB').resize((cell_w, cell_h), Image.Resampling.LANCZOS), (x, y))
            draw.text((x + 5, y + cell_h + 5), f"f{item['frame']:03d} / {item['pts']:.3f}s", fill='#102a28')
        target = atlases / f'{start:06d}-{selected[-1]["frame"]:06d}.jpg'
        sheet.save(target, quality=95)
        sheets.append({'path': str(target.relative_to(ROOT)), 'first': start,
                       'last': selected[-1]['frame'], 'frames': len(selected), 'sha256': sha(target)})
    # Practical A/V-event evidence; no transcript or claim of perceptual listening.
    samples = np.frombuffer(command('ffmpeg', '-v', 'error', '-i', path, '-vn',
                                    '-ar', '48000', '-ac', '1', '-f', 'f32le', '-'), dtype='<f4')
    audio, prior_spectrum = [], None
    for start in range(0, max(0, len(samples) - 2048), 480):
        block = samples[start:start + 2048].astype(float)
        spectrum = np.abs(np.fft.rfft(block * np.hanning(2048)))
        audio.append({'seconds': start / 48000, 'rms': float(np.sqrt(np.mean(block * block))),
                      'positive_spectral_flux': 0 if prior_spectrum is None else float(np.maximum(spectrum - prior_spectrum, 0).mean())})
        prior_spectrum = spectrum
    (folder / 'audio-events.json').write_text(json.dumps(audio, indent=2) + '\n')
    metrics = sorted((r for r in records if r['previous_frame_mae'] is not None),
                     key=lambda r: r['previous_frame_mae'], reverse=True)[:50]
    report = {'alias': alias, 'source_path': str(path), 'source_sha256': identity,
              'source_bytes': path.stat().st_size, 'probe': probe,
              'decoded_frames': count, 'native_dimensions': [video['width'], video['height']],
              'encoded_frame_rate': video['avg_frame_rate'], 'visual_duration_seconds': float(video['duration']),
              'frame_extraction': 'Every native decoded video frame, passthrough timestamps; no temporal sampling/interpolation.',
              'atlas_cell_dimensions': [cell_w, cell_h], 'atlases': sheets,
              'all_frames': records,
              'largest_frame_change_candidates': [{'frame': r['frame'], 'pts': r['pts'], 'mae': r['previous_frame_mae'], 'histogram_l1': r['histogram_l1']} for r in metrics],
              'limitations': ['Change scores are visual-inspection candidates, not certified cuts.',
                             'Encoded cadence is the supplied file cadence, not proof of original project frame rate.',
                             'Audio RMS/flux are event evidence; no human listening or transcript is claimed.',
                             'Reference pixels/audio stay ignored and are not authorised output-film assets.']}
    assert sha(path) == identity
    (folder / 'index.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'alias': alias, 'frames': count, 'atlases': len(sheets),
                      'index': str((folder / 'index.json').relative_to(ROOT))}), flush=True)
    return report


def eval_rate(value):
    a, b = map(int, value.split('/'))
    return a / b


if __name__ == '__main__':
    files = sorted(INPUT.glob('*.mp4'))
    assert len(files) == 2, 'Expected exactly the two supplied videos'
    OUT.mkdir(parents=True, exist_ok=True)
    reports = [study(path, alias) for path, alias in zip(files, ['feel-good', 'intelligence'])]
    (OUT / 'manifest.json').write_text(json.dumps({
        'total_native_frames': sum(r['decoded_frames'] for r in reports),
        'references': [{'alias': r['alias'], 'source_path': r['source_path'],
                        'sha256': r['source_sha256'], 'frames': r['decoded_frames'],
                        'index': str((OUT / r['alias'] / 'index.json').relative_to(ROOT))} for r in reports]
    }, indent=2) + '\n')
