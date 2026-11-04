#!/usr/bin/env python3
"""Read the actual encoded V11 delivery; never render or encode a movie."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import math
import re
import struct
import subprocess
from collections import Counter
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageStat

ROOT = Path(__file__).resolve().parents[4]
SRC = Path(__file__).resolve().parent
OUT = ROOT / '.publication/sunset-launch-v11'
W, H, FPS, COUNT = 1920, 1080, 30, 1020
SAFE = [100, 70, 1820, 1010]
INK, CREAM = (32, 59, 54), (252, 240, 219)


def native_probe(image):
    # This exact opaque plate is in the reviewed native scene, separate from 3D UV text.
    plate = [115, 905, 1265, 1015]
    mask = ink_mask(image.crop(plate), INK, 0)
    bounds = mask.getbbox()
    assert bounds, 'Native canvas glyphs missing'
    core = mask.filter(ImageFilter.MinFilter(3))
    b = core.getbbox()
    assert b, 'Native opaque glyph core missing'
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    _, x, y = min(((x-cx)**2+(y-cy)**2, x, y)
                  for y in range(b[1], b[3]) for x in range(b[0], b[2]) if core.getpixel((x, y)))
    fg, bg = [x + plate[0], y + plate[1]], [116, 906]
    return {'probe_foreground_xy': fg, 'probe_background_xy': bg,
            'foreground': image.getpixel(tuple(fg)), 'background': image.getpixel(tuple(bg)),
            'bounds': [bounds[0]+plate[0], bounds[1]+plate[1], bounds[2]+plate[0], bounds[3]+plate[1]]}


def ink_mask(image, color, tolerance=24):
    channels = ImageChops.difference(image, Image.new('RGB', image.size, tuple(color))).split()
    delta = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    return delta.point(lambda v: 255 if v <= tolerance else 0)


def self_test():
    with Image.open(OUT / 'scene/frames/000078.png') as im:
        result = native_probe(im.convert('RGB'))
        assert result is not None, 'Native canvas text needs an actual opaque glyph probe'
        assert result['bounds'][3] <= SAFE[3]
        assert result['foreground'] == INK and result['background'] == CREAM
    return {'pass': True, 'checks': ['actual native glyph core and safe bounds']}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def mp4_atoms(path):
    data, offset, atoms = path.read_bytes(), 0, []
    while offset + 8 <= len(data):
        size, kind = struct.unpack_from('>I4s', data, offset)
        if size == 1:
            size, = struct.unpack_from('>Q', data, offset + 8)
        if size == 0:
            size = len(data) - offset
        assert size >= 8
        atoms.append(kind.decode('ascii'))
        offset += size
    assert offset == len(data) and atoms.index('moov') < atoms.index('mdat')
    return atoms


def verify():
    # Reuse existing thorough source validators; independent decoded checks follow below.
    producer = module(SRC / 'render_launch.py', 'v11_source_validators')
    old_path = SRC.parent / 'launch-v10/verify.py'
    assert sha(old_path) == 'f95c58eecabb51784e6fd753f1841ba0e134dcbf73852679a5ca2a89d4c74282'
    old = module(old_path, 'v10_independent_verify_helpers')
    timeline, promised, native, _, actual, audio, cues, hashes, _, _ = producer.full_inputs()
    film = OUT / 'render/sunset-launch-v11.mp4'
    composite = read(OUT / 'composite/composite-provenance.json')
    spec = read(OUT / 'composite/readability-spec.json')
    assert sha(film) == composite['sha256'] and composite['video_encode_passes'] == 1
    assert hashes == composite['source_hashes'] == spec['source_hashes']
    assert composite['native_picture_source_count'] == len(native) == 750
    assert not composite['old_film_pixels_used'] and not composite['motion_interpolated']
    assert not composite['native_3d_picture_upscaled']
    assert spec['safe_bbox'] == SAFE and spec['frame_count'] == COUNT
    assert len(spec['all_frames']) == COUNT and len(promised) == 10
    assert spec['essential_read_windows'] == promised
    assert composite['actual_demo'] == actual.spec
    assert sha(ROOT / actual.spec['source_capture_provenance']) == old.CAPTURE_SHA
    assert sha(ROOT / actual.spec['source_pack']['path']) == old.GUIDE_SHA
    geometry_gates = {}
    for gate, count, live_name, verifier, hash_key in [
            ('proof-native-verification.json', 240, 'native-live.json', 'verify_motion.mjs', 'probe_sha256'),
            ('full-motion-verification.json', 510, 'full-native-live.json', 'verify_full_motion.mjs', 'source_sha256')]:
        checked = read(OUT / 'qa' / gate)
        assert checked['pass'] and checked['live']['pass'] and checked['live']['frames'] == count, ('Geometry gate', gate)
        assert checked['live'][hash_key] == sha(OUT / 'qa' / live_name)
        assert checked['source_hashes']['verifier']['sha256'] == sha(SRC / verifier)
        geometry_gates[gate] = sha(OUT / 'qa' / gate)
    fonts_path = SRC.parent / 'launch-v10/fonts-provenance.json'
    assert sha(fonts_path) == '5d4c03fcd43dd89605dd7b604219add26f20651572cc3b5e6ec02002326a135a'
    for family in read(fonts_path)['fonts']:
        assert family['license'] == 'SIL Open Font License 1.1'
        for item in family['files'].values():
            assert sha(ROOT / item['path']) == item['sha256']
    previous_path = ROOT / '.publication/sunset-launch-v10/media-qa.json'
    assert sha(previous_path) == '88b69f0fe9ebbf670d459d6d419ad67cf4fcbc95fc867d700084684dcc223450'
    previous = read(previous_path)
    preserved = {**previous['preserved_versions'], previous['film_path']: previous['sha256']}
    assert len(preserved) == 10
    for source, digest in preserved.items():
        assert sha(ROOT / source) == digest, ('Preserved movie changed', source)

    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(film)]))
    video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    sound = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
    assert (video['width'], video['height'], video['codec_name'], video['pix_fmt'], video['r_frame_rate']) == (W, H, 'h264', 'yuv420p', '30/1')
    assert int(video['nb_frames']) == COUNT and abs(float(probe['format']['duration']) - 34) < 1/FPS
    assert (video['color_space'], video['color_primaries'], video['color_transfer'], video['color_range']) == ('bt709', 'bt709', 'bt709', 'tv')
    assert (sound['codec_name'], int(sound['sample_rate']), sound['channels']) == ('aac', 48000, 2)
    atoms = mp4_atoms(film)
    assert audio['master_sha256'] == hashes['audio_master'] == sha(OUT / 'audio/mix.wav')
    assert (audio['duration_seconds'], audio['sample_count_per_channel'], audio['sample_rate'], audio['channels']) == (34, 1632000, 48000, 2)
    assert not audio['voice_present'] and not audio['tts_or_voice_models_used']
    assert audio['recorded_foley_only'] and cues['voice'] is None
    for name, identity in audio['stems'].items():
        assert sha(OUT / 'audio' / name) == identity['sha256']
    for source in cues['sources']:
        assert sha(ROOT / source['file']) == source['sha256']
        assert source['license'] == ('CC BY 4.0' if source['id'] == 'music' else 'CC0 1.0')

    assertions, expected_uses = 0, []
    forbidden = re.compile(r'https?://|www\.|Backbay Lounge|Kevin MacLeod|incompetech|7\s*\+\s*5|5\s*\+\s*7|Lantern|worksheet', re.I)
    for entry in promised:
        start, end = entry['window']
        words = sum(len(re.findall(r'[A-Za-z]+', s)) for s in entry['lines'])
        assert end-start+1e-8 >= .3*words+.5
        for n in range(math.ceil(start*FPS-1e-7), math.ceil(end*FPS-1e-7)):
            present = Counter(r['text'] for r in spec['all_frames'][n]['text'] if r.get('stable', True) and r.get('visible', True) and r.get('opacity', 1) >= 1-1e-8)
            assert Counter(entry['lines']) <= present, ('Promised read missing', n, entry['id'])
            assertions += 1
    for n, row in enumerate(spec['all_frames']):
        assert row['frame'] == n and abs(row['time']-n/FPS) < 1e-8
        assert row['native_source'] == native.get(n), ('Native source mapping', n)
        for item in row['text']:
            assert item['kind'] == 'screen-text' and not forbidden.search(item['text'])
            b = item.get('bbox', item['screen_bbox'])
            assert SAFE[0] <= b[0] < b[2] <= SAFE[2] and SAFE[1] <= b[1] < b[3] <= SAFE[3]
        use = row['actual_recording']
        if 570 <= n < 720:
            assert use and use['playback_speed'] == 1 and use['source_context'] == 'guide_file' and use['network_offline_verified']
            mapped = timeline['actual_ui_mapping']['source_v10_film_start'] + n/FPS - 19
            assert abs(use['mapped_v10_film_time']-mapped) < 1e-8 and abs(use['film_time']-n/FPS) < 1e-8
            old.check_actual({**use, 'film_time': mapped}, mapped, actual.spec)
            assert sha(ROOT / use['source_path']) == use['source_sha256']
            expected_uses.append(use)
        else:
            assert use is None
    assert len(expected_uses) == 150
    assert expected_uses == spec['actual_recording_frame_uses'] == composite['actual_demo_frame_uses']

    review = OUT / 'delivery-review'
    review.mkdir(parents=True, exist_ok=True)
    samples = {0,21,87,105,195,239,255,285,330,360,396,414,462,492,522,569,570,621,690,719,720,774,810,861,899,906,1019}
    samples.update(range(360, 436, 5)); samples.update(range(462, 570, 5)); samples.update(range(720, 841, 5))
    minimum, probes, ui_checks, maximum_error, black_run, black_max = math.inf, 0, 0, 0., 0, 0
    native_glyph = None
    decode = subprocess.Popen(['ffmpeg', '-v', 'error', '-xerror', '-i', str(film), '-map', '0:v:0', '-fps_mode', 'passthrough', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for n in range(COUNT):
            raw = decode.stdout.read(W*H*3)
            assert len(raw) == W*H*3, ('Incomplete decoded frame', n)
            image = Image.frombytes('RGB', (W,H), raw)
            histogram = image.resize((192,108), Image.Resampling.BOX).convert('L').histogram()
            black_run = black_run+1 if sum(histogram[:3]) >= 192*108*.98 else 0
            black_max = max(black_max, black_run)
            row = spec['all_frames'][n]
            for item in row['text']:
                if not item.get('stable', True) or item.get('opacity', 1) < 1-1e-8 or not item.get('visible', True):
                    continue  # Fade frames are preserved; only promised full-opacity reads claim contrast.
                b = item.get('bbox', item['screen_bbox'])
                if 'probe_foreground_xy' in item:
                    fg, bg = item['probe_foreground_xy'], item['probe_background_xy']
                    bounds = [max(0,b[0]-4), max(0,b[1]-4), min(W,b[2]+4), min(H,b[3]+4)]
                    measured_bbox = ink_mask(image.crop(bounds), item['foreground']).getbbox()
                    assert measured_bbox, ('Decoded glyph missing', n, item['text'])
                    measured_bbox = [measured_bbox[0]+bounds[0], measured_bbox[1]+bounds[1], measured_bbox[2]+bounds[0], measured_bbox[3]+bounds[1]]
                else:
                    assert item['id'] == 'fund-phrase' and row['native_source']
                    if native_glyph is None:
                        native_glyph = native_probe(old.source(row['native_source']['path']))
                    fg, bg = native_glyph['probe_foreground_xy'], native_glyph['probe_background_xy']
                    decoded_bounds = ink_mask(image.crop((115,905,1265,1015)), INK).getbbox()
                    assert decoded_bounds, ('Decoded native glyphs missing', n)
                    measured_bbox = [decoded_bounds[0]+115, decoded_bounds[1]+905, decoded_bounds[2]+115, decoded_bounds[3]+905]
                    assert max(abs(a-b) for a,b in zip(measured_bbox,native_glyph['bounds'])) <= 3, ('Native glyph bounds changed', n)
                assert SAFE[0] <= measured_bbox[0] < measured_bbox[2] <= SAFE[2] and SAFE[1] <= measured_bbox[1] < measured_bbox[3] <= SAFE[3]
                contrast = old.ratio(image.getpixel(tuple(fg)), image.getpixel(tuple(bg)))
                minimum = min(minimum, contrast); probes += 1
                assert contrast >= 4.5, ('Decoded glyph contrast', n, item['text'], contrast)
            use = row['actual_recording']
            if use:
                mapped = use['mapped_v10_film_time']
                roi, box, size = old.check_actual({**use, 'film_time': mapped}, mapped, actual.spec)
                expected = old.source(use['source_path']).crop(roi).resize(size, Image.Resampling.LANCZOS).resize((256,64), Image.Resampling.BOX)
                delivered = image.crop(box).resize((256,64), Image.Resampling.BOX)
                error = max(ImageStat.Stat(ImageChops.difference(expected, delivered)).mean)
                maximum_error = max(maximum_error, error)
                assert error <= 5, ('Decoded genuine UI differs', n, error)
                ui_checks += 1
            if n in samples:
                image.save(review / f'decoded-{n:06d}.jpg', quality=96)
            if n % 240 == 239:
                print(f'Independently verified {n+1}/{COUNT} decoded frames', flush=True)
        assert not decode.stdout.read(1), 'Extra decoded frames'
        stderr = decode.stderr.read().decode()
        assert decode.wait() == 0, stderr
    finally:
        if decode.poll() is None:
            decode.kill(); decode.wait()
    assert ui_checks == 150 and black_max < 6
    levels = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(film), '-vn', '-af', 'loudnorm=I=-15:TP=-2.5:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    assert levels.returncode == 0, levels.stderr
    loud, _ = json.JSONDecoder().raw_decode(levels.stderr[levels.stderr.rfind('{'):])
    lufs, peak = float(loud['input_i']), float(loud['input_tp'])
    assert -16 <= lufs <= -14 and peak <= -1.5
    assert abs(lufs-audio['aac_320k']['integrated_lufs']) < .1 and abs(peak-audio['aac_320k']['true_peak_dbtp']) < .1
    result = {'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'pass': True,
              'status': 'objective_decoded_checks_passed; creative/listening review separate',
              'film_path': str(film.relative_to(ROOT)), 'sha256': sha(film), 'bytes': film.stat().st_size,
              'duration': 34, 'frames': COUNT, 'dimensions': [W,H], 'fps': FPS,
              'full_decode': True, 'codec': 'H264/yuv420p BT709 limited', 'mp4_atoms': atoms, 'faststart': True,
              'audio': 'AAC stereo48kHz', 'loudness_lufs': lufs, 'true_peak_dbtp': peak,
              'read_windows': len(promised), 'read_window_frame_assertions': assertions,
              'stable_decoded_glyph_probes': probes, 'minimum_decoded_contrast': round(minimum,4),
              'safe_bbox': SAFE, 'native_phrase_actual_glyph_bounds': native_glyph['bounds'],
              'actual_ui_frames': ui_checks, 'actual_ui_max_channel_mean_error': round(maximum_error,4),
              'actual_ui_speed': 1, 'actual_capture_sampling': 'Real screenshot holds at original elapsed times; not30unique browser frames/s',
              'source_hashes': hashes, 'geometry_gate_hashes': geometry_gates, 'font_source_hashes_verified': True, 'native_png_sources': 750,
              'source_validation': 'Reused pure compositor preflight validators; independent actual movie decode/probes/ROI/codec/audio checks follow them.',
              'unexpected_black_intervals': 0, 'preserved_movies': preserved,
              'perceptual_listening_verified': False, 'creative_review_verified': False,
              'no_generated_voice': True, 'guide_onchain_release_claimed': False,
              'verifier_sha256': sha(Path(__file__)), 'prior_verifier_helpers_sha256': sha(old_path),
              'review_frames': sorted(samples)}
    (OUT / 'qa/delivery-verification.json').write_text(json.dumps(result, indent=2)+'\n')
    (review / 'ffprobe.json').write_text(json.dumps(probe, indent=2)+'\n')
    (review / 'decode.log').write_text(stderr)
    (review / 'audio-levels.log').write_text(levels.stderr)
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    if args.self_test:
        print(json.dumps(self_test()))
    else:
        verify()
