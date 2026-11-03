#!/usr/bin/env python3
"""Verify and transport existing genuine browser samples; never runs the product."""

import hashlib
import json
import shutil
import struct
import zlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / '.publication/sunset-launch-v8/footage'
OUT = ROOT / '.publication/sunset-launch-v9/footage'
GAME_HASH = 'fbe1df06b5eb4a93aae1eb12009f4d910e3ba432862918e3c254fc013ab79738'
PROVENANCE_HASH = 'cfb0d52bcedc8d0e7a770ec1a0073a7c05ae85c88544a533d863887d9ef7e5f9'
FPS = 30


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_check(path, expected_hash):
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected_hash, path
    assert data[:8] == b'\x89PNG\r\n\x1a\n', path
    offset = 8
    chunks = 0
    while offset < len(data):
        size = struct.unpack_from('>I', data, offset)[0]
        payload = data[offset + 4:offset + 8 + size]
        expected_crc = struct.unpack_from('>I', data, offset + 8 + size)[0]
        assert zlib.crc32(payload) & 0xffffffff == expected_crc, path
        chunks += 1
        offset += size + 12
        if payload[:4] == b'IEND':
            break
    assert offset == len(data), path
    with Image.open(path) as im:
        assert im.size == (2560, 1800), (path, im.size)
        im.verify()
    return chunks


def main():
    provenance_path = SOURCE / 'capture-provenance.json'
    assert sha(provenance_path) == PROVENANCE_HASH
    provenance = json.loads(provenance_path.read_text())
    assert provenance['download']['sha256'] == GAME_HASH
    game = SOURCE / provenance['download']['file']
    assert sha(game) == GAME_HASH and game.stat().st_size == 7246
    for state in ('offline_before', 'offline_after'):
        assert provenance[state]['onLine'] is False
        assert provenance[state]['resources'] == 0
        assert provenance[state]['scheme'] == 'file:'
    assert provenance['offline_before']['feedback'] == ''
    assert provenance['offline_after']['feedback'] == (
        '7 + 5 = 12. Your first lantern glows. The gate opens onto a quiet trail.'
    )
    assert provenance['offline_after']['progress'] == 1

    OUT.mkdir(parents=True, exist_ok=True)
    native = {}
    checks = []
    for kind, directory in (
        ('download', 'native-recording-download-to-offline'),
        ('action', 'native-recording-offline-action-result'),
    ):
        record = json.loads((SOURCE / directory / 'samples.json').read_text())
        assert record == provenance['recordings'][kind]
        assert all(a['at'] < b['at'] for a, b in zip(record['samples'], record['samples'][1:]))
        (OUT / directory).mkdir(exist_ok=True)
        native[kind] = []
        for sample in record['samples']:
            src = SOURCE / directory / sample['file']
            chunks = png_check(src, sample['sha256'])
            dest = OUT / directory / sample['file']
            shutil.copy2(src, dest)
            native[kind].append({
                'path': str(dest.relative_to(ROOT)),
                'file': sample['file'],
                'time': sample['at'] - record['first_capture_offset'],
                'capture_clock_seconds': sample['at'],
                'sha256': sample['sha256'],
            })
            checks.append({'path': str(src.relative_to(ROOT)), 'sha256': sample['sha256'], 'png_crc_chunks': chunks})
        shutil.copy2(SOURCE / directory / 'samples.json', OUT / directory / 'samples.json')

    for clip in provenance['clips']:
        assert sha(SOURCE / clip['file']) == clip['sha256']
    shutil.copy2(provenance_path, OUT / 'capture-provenance.json')
    (OUT / 'downloads-native').mkdir(exist_ok=True)
    shutil.copy2(game, OUT / 'downloads-native' / game.name)

    opened_at = native['download'][5]['time']
    scroll_at = native['download'][3]['time']
    # The actual browser scrolls the clicked control before dispatching input.
    # Two native crops follow that real reframe, excluding the product URL in both.
    download_before_crop = [1060, 1160, 1720, 1340]
    download_after_crop = [1060, 815, 1720, 995]
    opened_crop = [568, 80, 1992, 560]
    action_crop = [568, 660, 1992, 1135]

    def segment(name, kind, start, end, playback_start, crop, samples):
        return {
            'id': name, 'start': start, 'end': end,
            'sourcekind': 'actual_native_browser_png_samples',
            'source_dimensions': [2560, 1800], 'crop': crop,
            'playbackstart': playback_start,
            'source_clock_offset': provenance['recordings'][kind]['first_capture_offset'],
            'sourceframes': [{**s, 'film_time': playback_start + s['time']} for s in samples],
            'source_native_pixel_scale': 1.0,
            'max_editorial_scale': 2.2,
            'playback_rate': 1.0,
            'endpoint_holds': 'First/last available genuine sample held; no invented state or interpolation.',
        }

    segments = [
        segment('actual-download-before', 'download', 35.0, 35.0 + scroll_at, 35.0,
                download_before_crop, native['download'][:3]),
        segment('actual-download-clicked', 'download', 35.0 + scroll_at, 35.0 + opened_at, 35.0,
                download_after_crop, native['download'][3:5]),
        segment('actual-opened-offline-copy', 'download', 35.0 + opened_at, 38.0, 35.0,
                opened_crop, [s for s in native['download'][5:] if 35.0 + s['time'] < 38.0]),
        segment('actual-offline-answer-result', 'action', 38.0, 44.0, 38.0,
                action_crop, native['action']),
    ]
    assert segments[0]['start'] == 35.0 and segments[-1]['end'] == 44.0
    assert all(a['end'] == b['start'] for a, b in zip(segments, segments[1:]))
    action_offset = provenance['recordings']['action']['first_capture_offset']
    action_click = 38.0 + provenance['action_clip']['click_elapsed_seconds'] - action_offset
    visible_result = 38.0 + native['action'][3]['time']
    download_click = 35.0 + 1.059 - provenance['recordings']['download']['first_capture_offset']
    manifest = {
        'schema': 2, 'film_start': 35.0, 'film_end': 44.0, 'fps': FPS,
        'delivery_frames': 270, 'segments': segments,
        'source_capture_provenance': str((OUT / 'capture-provenance.json').relative_to(ROOT)),
        'source_capture_provenance_sha256': PROVENANCE_HASH,
        'source_sampling': 'Approximately 3 genuine native DPR2 PNG samples/second, timestamped at capture completion; 30fps delivery uses honest holds.',
        'sample_timestamp_meaning': provenance['recording_quality']['sample_timestamp_meaning'],
        'recording_start_to_first_sample_trimmed': True,
        'interpolation': False, 'cursor_reenactment': False,
        'editorial_magnification': {
            'allowed': True, 'max_scale': 2.2, 'resampling': 'LANCZOS',
            'source_native_pixel_scale': 1.0,
            'meaning': 'Genuine recorded pixels may be enlarged for phone readability; this adds no new UI states or source detail. Renderer records exact ROI, scale and resampling per frame.',
        },
        'chronology': 'Actual download then actual opened downloaded file; editorial cut to later separately captured offline interaction; final recorded result held.',
        'download_identity': {'bytes': 7246, 'sha256': GAME_HASH, 'path': str((OUT / 'downloads-native' / game.name).relative_to(ROOT))},
        'offline_before': provenance['offline_before'], 'offline_after': provenance['offline_after'],
        'events': [
            {'event': 'actual_download_input', 'film_time': download_click, 'at': '2026-11-03T10:23:35.636Z', 'source_xy': [1296.328125, 899.9375]},
            {'event': 'actual_download_opened_offline', 'film_time': 35.0 + 2.113096148999999 - provenance['recordings']['download']['first_capture_offset'], 'first_captured_film_time': 35.0 + opened_at, 'at': '2026-11-03T10:23:36.691Z'},
            {'event': 'actual_offline_12_input', 'film_time': action_click, 'at': '2026-11-03T10:23:44.871Z', 'source_xy': [866.9375, 900.171875]},
            {'event': 'first_captured_visible_feedback', 'film_time': visible_result, 'source_sample': native['action'][3]['path']},
        ],
        'editorial_click_highlight': {
            'kind': 'Optional editorial pulse at logged real input position, beginning on first captured post-click state.',
            'real_input_film_seconds': action_click,
            'annotation_start_film_seconds': visible_result,
            'duration_seconds': 0.42, 'source_xy': [866.9375, 900.171875],
            'not_a_recorded_cursor': True,
        },
        'selection_rule': 'Select segment start <= t < end, then last sourceframe.film_time <= t, holding endpoints. Never interpolate UI. crop coordinates are native pixel left/top/right/bottom.',
    }
    (OUT / 'compositor.json').write_text(json.dumps(manifest, indent=2) + '\n')

    keyframes = []
    for name, src, crop in (
        ('01-download-control-before.png', native['download'][0], download_before_crop),
        ('02-download-control-clicked.png', native['download'][3], download_after_crop),
        ('03-opened-offline-copy.png', native['download'][5], opened_crop),
        ('04-offline-answer-before.png', native['action'][0], action_crop),
        ('05-offline-answer-result.png', native['action'][3], action_crop),
    ):
        target = OUT / name
        with Image.open(ROOT / src['path']) as im:
            im.crop(crop).save(target)
        keyframes.append({'path': str(target.relative_to(ROOT)), 'source_sha256': src['sha256'], 'sha256': sha(target), 'crop': crop, 'scale': 1.0})

    # Review-only contact sheet: labels and gutters are outside genuine pixels.
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font = ImageFont.truetype(font_path, 23)
    sheet = Image.new('RGB', (1000, 2200), '#d6d0c3')
    draw = ImageDraw.Draw(sheet)
    y = 12
    for item in keyframes:
        draw.text((20, y), Path(item['path']).name, fill='#203e35', font=font)
        y += 36
        with Image.open(ROOT / item['path']) as im:
            scale = min(1, 960 / im.width)
            tile = im.resize((round(im.width * scale), round(im.height * scale)), Image.Resampling.LANCZOS)
            sheet.paste(tile, ((1000 - tile.width) // 2, y))
            y += tile.height + 20
    sheet.crop((0, 0, 1000, y)).save(OUT / 'proof-contact-sheet.png')

    report = {
        'passed': True, 'source_png_count': len(checks),
        'unique_source_png_hashes': len({s['sha256'] for s in checks}),
        'source_dimensions': [2560, 1800], 'source_png_sha256_and_crc': checks,
        'provenance_sha256': PROVENANCE_HASH, 'download_sha256': GAME_HASH,
        'offline_before_after_onLine': [False, False], 'offline_before_after_resources': [0, 0],
        'compositor_sha256': sha(OUT / 'compositor.json'), 'keyframes': keyframes,
        'review_contact_sheet': str((OUT / 'proof-contact-sheet.png').relative_to(ROOT)),
        'assertions': ['All PNG CRCs and SHA256 hashes match genuine v8 provenance.', 'Downloaded HTML identity matches pinned release.', 'Offline state and visible actual 12 feedback verified.', 'All four segments cover 35–44 continuously at original elapsed timing.', 'Source PNGs and crops remain unchanged; editorial magnification up to 2.2x uses LANCZOS and adds no new source detail. Final endpoint is an explicit still hold.', 'Product URL excluded by two reframing crops for actual download control.'],
    }
    (OUT / 'proof-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('passed', 'source_png_count', 'unique_source_png_hashes', 'compositor_sha256')}))
    print(str(OUT / 'compositor.json'))


if __name__ == '__main__':
    main()
