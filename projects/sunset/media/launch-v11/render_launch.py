#!/usr/bin/env python3
"""Encode native V11 frames once; retain exact picture, sound and text identities.

The eight-second export is a motion/feel proof. Source checks and decode checks
do not establish tactile quality; that requires the separate visual review.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
SRC = Path(__file__).resolve().parent
OUT = ROOT / '.publication/sunset-launch-v11'
W, H, FPS, DURATION = 1920, 1080, 30, 8
SAFE = [100, 70, 1820, 1010]
READS = [{'id': 'community', 'window': [2.6, 5.1],
          'lines': ['Fund public knowledge.'], 'minimum_read_seconds': 1.4}]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def run(*args):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True,
                          text=True).stdout


def validate_record(record, duration=DURATION, reads=READS):
    n = record['frame']
    assert isinstance(n, int) and 0 <= n < FPS * duration, ('frame', n)
    assert math.isclose(record['time'], n / FPS, abs_tol=1e-9), ('timestamp', n)
    assert [record['width'], record['height']] == [W, H], ('canvas', n)
    assert [record['drawingBufferWidth'], record['drawingBufferHeight']] == [W, H], ('buffer', n)
    assert record['pixelRatio'] == 1 and record['actual_context_antialias'] is True
    assert record['actual_samples'] >= 4, ('MSAA', n)
    visible = set()
    for text in record['essential_text']:
        assert text['kind'] == 'screen-text' and text['visible'] and text['essential']
        b = text['screen_bbox']
        assert SAFE[0] <= b[0] < b[2] <= SAFE[2] and SAFE[1] <= b[1] < b[3] <= SAFE[3], ('text bounds', n, text)
        assert text['contrast_ratio'] >= 4.5, ('authored contrast', n, text)
        visible.add(text['text'])
    for read in reads:
        if read['window'][0] - 1e-9 <= n / FPS < read['window'][1] - 1e-9:
            assert set(read['lines']) <= visible, ('missing essential read', n)


def validate_capture(path, partial=False, duration=DURATION, expected_indices=None, reads=READS):
    capture = json.loads(path.read_text())
    native, records = capture['native'], capture['records']
    assert [native[k] for k in ['width', 'height', 'fps', 'duration']] == [W, H, FPS, duration]
    assert native['format'] == 'png' and native['antialias'] and native['samples'] >= 4
    assert len(records) == native['frames'] and records, 'No native frames'
    ids = [r['frame'] for r in records]
    assert len(set(ids)) == len(ids) and ids == sorted(ids), 'Duplicated or unordered native frame'
    if not partial:
        required = expected_indices if expected_indices is not None else list(range(FPS * duration))
        assert not capture['preview'] and ids == required, 'Complete promised native capture required'
    identities = {**capture['source_hashes']}
    identities.update({asset['url']: asset for asset in capture['assets']})
    for key, source in identities.items():
        assert sha(ROOT / source['path']) == source['sha256'], ('changed source', key)
    sources = []
    for record in records:
        validate_record(record, duration, reads)
        png = ROOT / native['folder'] / f"{record['frame']:06d}.png"
        assert sha(png) == record['sha256'] and png.stat().st_size == record['bytes'], ('changed PNG', png)
        with Image.open(png) as im:
            assert im.size == (W, H) and im.format == 'PNG', ('native PNG', png)
            im.verify()
        sources.append({'frame': record['frame'], 'time': record['time'], 'path': relative(png),
                        'sha256': record['sha256'], 'dimensions': [W, H],
                        'phase': record['phase'], 'text': record['essential_text']})
    return capture, sources


def validate_audio(duration=DURATION, full=False):
    folder = OUT / ('audio' if full else 'audio-proof')
    qa = json.loads((folder / 'qa.json').read_text())
    cues = json.loads((SRC / ('sound-cues.json' if full else 'sound-cues-proof.json')).read_text())
    assert qa['duration_seconds'] == duration and qa['sample_rate'] == 48000 and qa['channels'] == 2
    assert qa['voice_present'] is False and qa['recorded_foley_only'] is True and cues['voice'] is None
    assert cues['duration_seconds'] == duration and len(cues['effects']) == qa['cue_count']
    assert sha(folder / 'mix.wav') == qa['master_sha256'], 'Changed audio master'
    for name, stem in qa.get('stems', {}).items():
        assert sha(folder / name) == stem['sha256'], ('Changed audio stem', name)
    assert sha(SRC.parent / 'launch-v10/prepare_audio.py') == cues['shared_helper_sha256']
    for source in cues['sources']:
        assert sha(ROOT / source['file']) == source['sha256'], ('Changed licensed source', source['id'])
    probe = json.loads(run('ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', folder / 'mix.wav'))
    audio = probe['streams'][0]
    assert audio['codec_name'] == 'pcm_s24le' and audio['sample_rate'] == '48000' and audio['channels'] == 2
    assert math.isclose(float(probe['format']['duration']), duration, abs_tol=1/48000)
    return qa, cues


def encode_command(audio, target, duration=DURATION, raw=False):
    # The scale filter only converts full RGB range to limited BT.709; it does not resize.
    picture = ['-f', 'rawvideo', '-pixel_format', 'rgb24', '-video_size', f'{W}x{H}',
               '-framerate', str(FPS)] if raw else ['-f', 'image2pipe', '-framerate', str(FPS), '-vcodec', 'png']
    return ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *picture, '-i', '-', '-i', str(audio),
            '-map', '0:v:0', '-map', '1:a:0', '-vf',
            'scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-g', '60', '-threads', '4',
            '-color_range', 'tv', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
            '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-t', str(duration),
            '-frames:v', str(FPS * duration), '-movflags', '+faststart', str(target)]


def validate_movie(path, duration=DURATION):
    probe = json.loads(run('ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path))
    video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    audio = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
    assert video['codec_name'] == 'h264' and video['pix_fmt'] == 'yuv420p'
    assert [video['width'], video['height'], video['r_frame_rate'], int(video['nb_frames'])] == [W, H, '30/1', duration * FPS]
    assert all(video[k] == 'bt709' for k in ['color_space', 'color_transfer', 'color_primaries'])
    assert video['color_range'] == 'tv' and audio['codec_name'] == 'aac'
    assert audio['sample_rate'] == '48000' and audio['channels'] == 2
    assert math.isclose(float(probe['format']['duration']), duration, abs_tol=1/FPS)
    run('ffmpeg', '-v', 'error', '-xerror', '-i', path, '-f', 'null', '-')
    # Top-level MP4 atoms establish faststart without matching bytes inside compressed data.
    atoms = []
    with path.open('rb') as f:
        while header := f.read(8):
            assert len(header) == 8
            size, kind = int.from_bytes(header[:4], 'big'), header[4:].decode('ascii')
            if size == 1:
                size = int.from_bytes(f.read(8), 'big'); head = 16
            else:
                head = 8
            assert size >= head
            atoms.append(kind); f.seek(size - head, 1)
    assert atoms.index('moov') < atoms.index('mdat'), 'Missing faststart'
    return {'full_decode': True, 'mp4_atoms': atoms, 'video': video, 'audio': audio,
            'format_duration': float(probe['format']['duration'])}


def inspection_sheets(sources):
    for label, indices in [('contact', range(9, 43, 2)), ('gather', range(81, 130, 3)),
                           ('open', range(156, 240, 4))]:
        sheet = Image.new('RGB', (W, 294 * math.ceil(len(indices) / 4)), '#fcf0db')
        for cell, frame in enumerate(indices):
            source = sources[frame]
            with Image.open(ROOT / source['path']) as im:
                sheet.paste(im.resize((480, 270), Image.Resampling.LANCZOS), ((cell % 4) * 480, (cell // 4) * 294))
            ImageDraw.Draw(sheet).text(((cell % 4) * 480 + 8, (cell // 4) * 294 + 275),
                                      f"{frame / FPS:.3f}s  frame {frame}", fill='#203b36')
        sheet.save(OUT / 'composite' / f'proof-{label}-strip.jpg', quality=96)


def proof(manifest):
    capture, sources = validate_capture(manifest)
    qa, cues = validate_audio()
    target = OUT / 'render/sunset-v11-motion-proof.mp4'
    target.parent.mkdir(parents=True, exist_ok=True)
    (OUT / 'composite').mkdir(parents=True, exist_ok=True)
    recipe = OUT / 'composite/proof-render_launch.py'
    recipe.write_bytes(Path(__file__).read_bytes())
    cmd = encode_command(OUT / 'audio-proof/mix.wav', target)
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for source in sources:
            data = (ROOT / source['path']).read_bytes()
            assert hashlib.sha256(data).hexdigest() == source['sha256'], 'PNG changed after preflight'
            process.stdin.write(data)
        process.stdin.close()
        assert process.wait() == 0, 'Native proof encode failed'
    finally:
        if process.poll() is None:
            process.kill(); process.wait()
    movie = validate_movie(target)
    inspection_sheets(sources)
    hashes = {'renderer': sha(recipe), 'capture_manifest': sha(manifest),
              'audio_master': qa['master_sha256'], 'audio_qa': sha(OUT / 'audio-proof/qa.json'),
              'sound_cues': sha(SRC / 'sound-cues-proof.json'),
              'audio_arrangement_recipe': sha(SRC / 'prepare_audio.py')}
    write_json(OUT / 'composite/proof-readability-spec.json', {
        'schema': 1, 'stage': 'eight_second_feel_proof', 'dimensions': [W, H], 'fps': FPS,
        'duration': DURATION, 'frame_count': len(sources), 'safe_bbox': SAFE,
        'essential_read_windows': READS, 'all_frames': sources, 'source_hashes': hashes,
        'measurement_limit': 'Author records and source identities support independent decoded-frame QA; they do not prove tactile material, contact, weight or camera quality.'})
    provenance = {'schema': 1, 'stage': 'eight_second_feel_proof', 'path': relative(target),
                  'sha256': sha(target), 'bytes': target.stat().st_size, 'duration': DURATION,
                  'frames': len(sources), 'dimensions': [W, H], 'fps': FPS,
                  'video_encode_passes': 1, 'native_png_direct': True, 'resized': False,
                  'motion_interpolated': False, 'crf': 14, 'encode_command': cmd,
                  'source_hashes': hashes, 'capture_manifest': relative(manifest),
                  'renderer_recipe': relative(recipe),
                  'capture': capture, 'audio_qa': qa, 'sound_cues': cues, 'codec_verification': movie,
                  'readability_proof': relative(OUT / 'composite/proof-readability-spec.json'),
                  'no_generated_voice': True, 'no_product_url_or_music_credit_in_picture': True,
                  'creative_status': 'Await root and independent normal-speed visual review. Not full launch delivery.'}
    write_json(OUT / 'composite/proof-composite-provenance.json', provenance)
    print(json.dumps({k: provenance[k] for k in ['stage', 'path', 'sha256', 'bytes', 'frames']}, indent=2))


def full_helpers():
    """Reuse original raster/font/actual-PNG helpers, never frames from an old film."""
    path = SRC.parent / 'launch-v10/render_launch.py'
    spec = importlib.util.spec_from_file_location('sunset_v10_raster_helpers', path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    return helper


def full_reads(timeline):
    reads = READS + [{'id': 'problem', 'window': [.6, 2.4],
                      'lines': ['Good work needs backing.'], 'minimum_read_seconds': 1.7}]
    for phase in timeline['phases']:
        if phase['text']:
            minimum = .3 * sum(len(re.findall(r'[A-Za-z]+', s)) for s in phase['text']) + .5
            start = math.ceil((phase['start'] + .2 - 1e-8) * FPS) / FPS
            assert phase['end'] - start >= minimum - 1e-8, ('read duration', phase['id'])
            reads.append({'id': phase['id'], 'window': [start, phase['end']],
                          'lines': phase['text'], 'minimum_read_seconds': minimum})
    return reads


def full_inputs():
    timeline = json.loads((SRC / 'timeline.json').read_text())
    assert timeline['duration'] == 34 and timeline['fps'] == FPS and timeline['dimensions'] == [W, H]
    assert timeline['actual_ui_mapping']['speed'] == 1
    assert timeline['native_continuation_frames'] == [[240, 570], [720, 900]]
    reads = full_reads(timeline)
    proof_capture, opening = validate_capture(OUT / 'scene/native-render.json')
    ids = list(range(240, 570)) + list(range(720, 900))
    continuation, native = validate_capture(OUT / 'scene/full-native-render.json', duration=34,
                                           expected_indices=ids, reads=[])
    qa, cues = validate_audio(34, full=True)
    helper = full_helpers()
    actual = helper.ActualGuide()
    assert actual.spec and actual.spec['failed_takes_used'] is False
    assert sha(ROOT / actual.spec['source_capture_provenance']) == actual.spec['source_capture_provenance_sha256']
    for segment in actual.spec['segments']:
        for source in segment['sourceframes']:
            assert sha(ROOT / source['path']) == source['sha256'], ('actual source identity', source['path'])
    for identity in [actual.spec['download_identity'], actual.spec['source_pack']]:
        assert sha(ROOT / identity['path']) == identity['sha256']
    for font_path in helper.FONTS.glob('*.ttf'):
        assert any(a['path'] == relative(font_path) and a['sha256'] == sha(font_path)
                   for a in proof_capture['assets']), ('uncaptured font source', font_path)
    hashes = {'renderer': sha(Path(__file__)), 'timeline': sha(SRC / 'timeline.json'),
              'proof_capture': sha(OUT / 'scene/native-render.json'),
              'continuation_capture': sha(OUT / 'scene/full-native-render.json'),
              'v10_raster_helpers': sha(SRC.parent / 'launch-v10/render_launch.py'),
              'actual_manifest': sha(actual.path), 'audio_master': qa['master_sha256'],
              'audio_qa': sha(OUT / 'audio/qa.json'),
              'audio_arrangement_recipe': sha(SRC / 'prepare_full_audio.py'),
              'sound_cues': sha(SRC / 'sound-cues.json'), 'logo': sha(helper.LOGO_PATH)}
    return timeline, reads, {r['frame']: r for r in opening + native}, helper, actual, qa, cues, hashes, proof_capture, continuation


def add_copy(im, helper, lines, dt, kind='normal'):
    cream = (252, 240, 219)
    if kind == 'refund':
        placements = [(135, 790, 44), (135, 850, 64), (135, 925, 68)]
        box = [115, 775, 1805, 1010]
    elif kind == 'ui':
        placements, box = [(125, 105, 84)], [110, 90, 1810, 215]
    else:
        placements = [(135, 905, 76)] if len(lines) == 1 else [(135, 805, 76), (135, 895, 76)]
        box = [115, placements[0][1] - 15, 1805, 1010]
    # Protect only the phrase's ink area, leaving the physical scene visible beside it.
    box[2] = max(x + helper.word(value, size, helper.INK, False, 750).width + 15
                 for value, (x, y, size) in zip(lines, placements))
    helper.rect(im, box, cream)
    alpha = helper.ease(dt / .2)
    records = []
    for value, (x, y, size) in zip(lines, placements):
        helper.put(im, helper.word(value, size, helper.INK, False, 750), x, y, alpha)
        record = helper.record(value, x, y, size, helper.INK, cream)
        record.update(stable=dt >= .2 - 1e-8, opacity=alpha)
        records.append(record)
    helper.measure(im, [r for r in records if r['stable']], dt)
    for record in records:
        record.update(kind='screen-text', coordinate_space='screen', essential=True,
                      visible=alpha > 0, screen_bbox=record['bbox'],
                      safe_bbox=record['bbox'], contrast_ratio=record.get('contrast'),
                      source='native_1080_compositor')
    return records


def full_frame(frame, timeline, native, helper, actual):
    t = frame / FPS
    source, ui, records = native.get(frame), None, []
    if source:
        with Image.open(ROOT / source['path']) as image:
            im = image.convert('RGBA')
        records.extend(source['text'])
    else:
        im = Image.new('RGBA', (W, H), (252, 240, 219))
    if .4 <= t < 2.4:
        records += add_copy(im, helper, ['Good work needs backing.'], t - .4)
    if 8 <= t < 30:
        phase = next(p for p in timeline['phases'] if p['start'] <= t < p['end'])
        if 19 <= t < 24:
            old_time = timeline['actual_ui_mapping']['source_v10_film_start'] + t - 19
            ui = actual.panel(im, old_time)
            assert ui['source_context'] == 'guide_file' and ui['network_offline_verified']
            # Keep true source clocks; changing this output offset does not accelerate the take.
            ui.update(film_time=t, mapped_v10_film_time=old_time, playback_speed=1)
        records += add_copy(im, helper, phase['text'], t - phase['start'],
                            'refund' if phase['id'] == 'conditional-refunds' else
                            'ui' if phase['id'] == 'genuine-handbook' else 'normal')
    elif t >= 30:
        helper.put(im, helper.LOGO.resize((250, 250), Image.Resampling.LANCZOS), 835, 200,
                   helper.ease((t - 30) / .2))
        for value, y, size, body in [('SUNSET', 510, 185, False),
                                     ('Support once. Share forever.', 765, 62, True)]:
            tile = helper.word(value, size, helper.INK, body, 700 if body else 750)
            x = (W - tile.width) / 2
            helper.put(im, tile, x, y, helper.ease((t - 30) / .2))
            r = helper.record(value, x, y, size, helper.INK, (252, 240, 219), body, 700 if body else 750)
            stable = t >= 30.2 - 1e-8
            if stable:
                helper.measure(im, [r], t)
            r.update(kind='screen-text', coordinate_space='screen', essential=True, visible=t > 30,
                     opacity=helper.ease((t - 30) / .2), stable=stable,
                     screen_bbox=r['bbox'], safe_bbox=r['bbox'], contrast_ratio=r.get('contrast'))
            records.append(r)
    return im.convert('RGB'), records, source, ui


def full_render(check=False):
    timeline, reads, native, helper, actual, qa, cues, hashes, opening, continuation = full_inputs()
    if check:
        for n in [18, 240, 321, 396, 468, 577, 648, 700, 726, 819, 912, 1019]:
            full_frame(n, timeline, native, helper, actual)
        print(json.dumps({'native_source_frames': len(native), 'duration': 34,
                          'essential_read_windows': reads, 'source_hashes': hashes}, indent=2))
        return
    target = OUT / 'render/sunset-launch-v11.mp4'
    target.parent.mkdir(parents=True, exist_ok=True)
    (OUT / 'composite').mkdir(parents=True, exist_ok=True)
    cmd = encode_command(OUT / 'audio/mix.wav', target, 34, raw=True)
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    frames = []
    try:
        for n in range(34 * FPS):
            im, text, source, ui = full_frame(n, timeline, native, helper, actual)
            visible = {r['text'] for r in text if r.get('stable', True) and r.get('visible', True)}
            for read in reads:
                if read['window'][0] - 1e-8 <= n / FPS < read['window'][1] - 1e-8:
                    assert set(read['lines']) <= visible, ('missing final read', n, read['id'])
            process.stdin.write(im.tobytes())
            frames.append({'frame': n, 'time': n / FPS, 'text': text,
                           'native_source': source, 'actual_recording': ui,
                           'picture_kind': 'actual_png_hold' if ui else 'native_3d' if source else 'original_brand_hold'})
            if n % 120 == 119:
                print(f'Composed {n + 1}/1020 native1080 frames', flush=True)
        process.stdin.close()
        assert process.wait() == 0
    finally:
        if process.poll() is None:
            process.kill(); process.wait()
    movie = validate_movie(target, 34)
    assert sha(SRC / 'timeline.json') == hashes['timeline']
    write_json(OUT / 'composite/readability-spec.json', {
        'schema': 1, 'dimensions': [W, H], 'fps': FPS, 'duration': 34, 'frame_count': 1020,
        'safe_bbox': SAFE, 'all_frames': frames, 'essential_read_windows': reads,
        'source_hashes': hashes, 'actual_recording_frame_uses': actual.uses})
    provenance = {'schema': 1, 'path': relative(target), 'sha256': sha(target),
                  'bytes': target.stat().st_size, 'duration': 34, 'frames': 1020,
                  'dimensions': [W, H], 'fps': FPS, 'video_encode_passes': 1, 'crf': 14,
                  'native_picture_source_count': len(native), 'old_film_pixels_used': False,
                  'motion_interpolated': False, 'native_3d_picture_upscaled': False,
                  'actual_ui_editorial_scale_disclosed_per_frame': True,
                  'source_hashes': hashes, 'encode_command': cmd, 'codec_verification': movie,
                  'opening_capture': opening, 'continuation_capture': continuation,
                  'actual_demo': actual.spec, 'actual_demo_frame_uses': actual.uses,
                  'audio_qa': qa, 'sound_cues': cues,
                  'no_generated_voice': True, 'no_product_url_or_music_credit_in_picture': True,
                  'readability_proof': relative(OUT / 'composite/readability-spec.json'),
                  'creative_status': 'Decoded motion and independent full-film review required before delivery.'}
    write_json(OUT / 'composite/composite-provenance.json', provenance)
    print(json.dumps({k: provenance[k] for k in ['path', 'sha256', 'bytes', 'duration', 'frames']}, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', type=Path, default=OUT / 'scene/native-render.json')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--partial', action='store_true', help='Validate a pose/probe subset; never encode it.')
    ap.add_argument('--proof', action='store_true')
    ap.add_argument('--full-check', action='store_true')
    ap.add_argument('--render', action='store_true', help='Full34s film after the tactile proof gate.')
    args = ap.parse_args()
    if args.full_check or args.render:
        assert args.full_check != args.render and not args.proof and not args.check and not args.partial
        full_render(check=args.full_check)
        return
    assert args.check != args.proof, 'Choose --check or --proof'
    assert not args.proof or not args.partial, 'Partial capture cannot become a movie'
    if args.check:
        capture, sources = validate_capture(args.manifest, args.partial)
        qa, _ = validate_audio()
        print(json.dumps({'native_frames_checked': len(sources), 'partial': args.partial,
                          'capture_manifest_sha256': sha(args.manifest), 'audio_master_sha256': qa['master_sha256'],
                          'average_frame_ms': capture['average_frame_ms'], 'creative_review': 'Separate normal-speed review required'}, indent=2))
    else:
        proof(args.manifest)


if __name__ == '__main__':
    main()
