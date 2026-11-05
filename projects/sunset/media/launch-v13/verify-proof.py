"""Independent readback of the encoded proof and opaque glyph-core contrasts."""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / '.publication/sunset-launch-v13'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ratio(a, b):
    def luminance(color):
        v = np.array(color, dtype=float) / 255
        v = np.where(v <= .04045, v / 12.92, ((v + .055) / 1.055) ** 2.4)
        return float(v @ [.2126, .7152, .0722])
    lo, hi = sorted([luminance(a), luminance(b)])
    return (hi + .05) / (lo + .05)


def main():
    report = json.loads((OUT / 'render-report.json').read_text())
    assert sha(ROOT / report['movie']['path']) == report['movie']['sha256']
    assert report['full_240_frame_decode'] and report['frames'] == 240
    for source, digest in report['source_hashes'].items():
        assert sha(ROOT / source) == digest
    assert len(report['records']) == 240
    cache, probes, minimum = {}, 0, 1000
    for row in report['records']:
        n = row['frame']
        assert n / 30 == row['time'] and sha(ROOT / row['path']) == row['sha256']
        with Image.open(OUT / 'decoded' / f'{n:06d}.png') as actual:
            actual.load()
            assert actual.size == (1920, 1080)
            actual = actual.convert('RGB')
            for item in row['essential_text']:
                x0, y0, x1, y1 = map(int, item['bbox'])
                assert 90 <= x0 < x1 <= 1830 and 70 <= y0 < y1 <= 1010
                key = (item['text'], tuple(item['bbox']), item['foreground'])
                if key not in cache:
                    with Image.open(ROOT / row['path']) as source:
                        crop = source.convert('RGB').crop((x0, y0, x1, y1))
                    color = np.array([int(item['foreground'][i:i+2], 16) for i in [1, 3, 5]])
                    mask = Image.fromarray((np.max(np.abs(np.array(crop, dtype=int)-color), axis=2) <= 1).astype('uint8')*255)
                    core = np.array(mask.filter(ImageFilter.MinFilter(3)))
                    ys, xs = np.where(core > 0)
                    assert len(xs), ('No actual opaque glyph core', item['text'])
                    k = np.argmin((xs-(x1-x0)/2)**2+(ys-(y1-y0)/2)**2)
                    cache[key] = ((int(xs[k])+x0, int(ys[k])+y0), (x0-8, y0-8))
                fg, bg = cache[key]
                measured = ratio(actual.getpixel(fg), actual.getpixel(bg))
                minimum = min(minimum, measured)
                assert measured >= 4.5, (n, item['text'], measured)
                probes += 1
    assert probes == 368
    result = {'pass': True, 'movie_sha256': report['movie']['sha256'],
              'decoded_native_images_inspected': 240, 'authored_png_identities_checked': 240,
              'stable_encoded_glyph_core_probes': probes,
              'minimum_measured_encoded_contrast': round(minimum, 4),
              'method': 'Derive opaque stroke-core positions from actual authored raster; sample those foreground/background points in every stable encoded caption frame.',
              'safe_bbox_checked': [90, 70, 1830, 1010], 'source_identities_checked': True,
              'limits': ['One core probe per stable line is not OCR or exhaustive glyph-edge inspection.',
                         'Decoded visual review and operator creative approval remain separate.'],
              'verifier_sha256': sha(Path(__file__))}
    (OUT / 'decoded-verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
