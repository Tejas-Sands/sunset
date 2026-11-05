#!/usr/bin/env python3
"""Private direct motion study of the supplied Intelligence reference.

Reference pixels are opened ONLY by --gates for labelled local comparisons.
The film renderer never reads them. Geometry and edits use native source times;
Native 18 fps samples preserve every supplied pose and content cut.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / '.publication/sunset-launch-v14/minimal'
ASSETS = ROOT / '.publication/sunset-launch-v14/assets'
REFERENCE = ROOT / '.publication/sunset-reference-study-20261105/intelligence'
W, H, FPS, FRAMES = 1920, 1080, 18, 195
SCALE = 1.5
WHITE = (253, 253, 253)
INK = (7, 7, 7)
CORAL = (211, 81, 63)
FONT_PATH = '/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf'
FONT = ImageFont.truetype(FONT_PATH, 75)
SMALL = ImageFont.truetype(FONT_PATH, 16)
LABEL = ImageFont.truetype(FONT_PATH, 24)
FALLBACK = ROOT / '.publication/sunset-launch-v13/assets/creator-cutout.png'

# Native decoded circle diameters. Subpixel values are inferred between measured
# bounds; measurements are approximate because source pixels include compression.
DIAMETERS = {
    26: 366, 27: 356, 28: 348, 29: 342, 30: 337, 31: 333,
    32: 331, 33: 329, 34: 327, 35: 326, 36: 324, 37: 324,
    38: 323, 46: 323, 47: 323, 69: 323, 78: 322,
    80: 321, 82: 319, 84: 316, 85: 314, 86: 312,
    87: 308, 88: 303, 89: 294, 90: 276,
}
EVENTS = [
    (0, 'full-bleed creator work'), (20, 'huge clipped circular boundary'),
    (26, 'abrupt small circle and tangent guides'),
    (47, 'hard cut inside unchanged circular mask: creator portrait'),
    (69, 'hard cut inside unchanged circular mask: workroom'),
    (90, 'last landscape-sized circular window, native diameter 276px'),
    (91, 'abrupt black point; all guides removed'),
    (107, 'brief coral point accent'), (113, 'point replaced by bracketed FREE'),
    (130, 'character deletion / replacement / bracket reflow starts'),
    (142, 'compact PAID word begins'), (144, 'PAID complete, settles then holds'),
    (162, 'abrupt final phrase expansion'), (167, 'phrase complete, hold through194'),
]
_CACHE: dict[str, Image.Image] = {}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * max(0, min(1, t))


def interp(keys: dict[int, float], q: float) -> float:
    ks = sorted(keys)
    if q <= ks[0]:
        return keys[ks[0]]
    for a, b in zip(ks, ks[1:]):
        if a <= q <= b:
            return lerp(keys[a], keys[b], (q - a) / (b - a))
    return keys[ks[-1]]


def source_frame(n: int) -> float:
    return n * 18 / FPS


def first_output_frame(source: int) -> int:
    return math.ceil(source * FPS / 18)


def image_asset(name: str) -> Image.Image:
    path = ASSETS / (name + '.png')
    if not path.exists():
        path = FALLBACK
    key = str(path)
    if key not in _CACHE:
        loaded = Image.open(path).convert('RGBA')
        if name == 'creator-portrait':
            # This generated asset is a four-person atlas. Use ONE original
            # person, never the atlas grid as a film composition.
            loaded = loaded.crop((0, 0, loaded.width // 2, loaded.height // 2))
        _CACHE[key] = loaded
    return _CACHE[key]


def crop_camera(im: Image.Image, n: int, kind: int) -> Image.Image:
    """Fixed framing: local work layers supply movement during geometric holds."""
    if kind == 1:
        room = ImageOps.fit(image_asset('workroom').convert('RGB'), (W, H), Image.Resampling.LANCZOS)
        portrait = im.resize((1000, 1000), Image.Resampling.LANCZOS)
        # Independent body translation is bounded to four pixels; no camera bob.
        dx = round(2 * math.sin((n / FPS - 47 / 18) * 1.7))
        room.paste(portrait, (460 + dx, 100), portrait)
        return room
    target = ImageOps.fit(im.convert('RGB'), (W, H), Image.Resampling.LANCZOS)
    if kind == 0:
        zoom, cx, cy = 1.22, W * .57, H * .51
    else:
        # Desk rather than the asset's blank wall fills this third specimen.
        zoom, cx, cy = 2.50, W * .48, H * .79
    cw, ch = int(W / zoom), int(H / zoom)
    box = (int(cx-cw/2), int(cy-ch/2), int(cx+cw/2), int(cy+ch/2))
    return target.crop(box).resize((W, H), Image.Resampling.LANCZOS)


def draw_polyline(draw: ImageDraw.ImageDraw, pts: list[tuple[float, float]], progress: float,
                  fill: tuple[int, ...], width: int) -> None:
    stop = max(2, min(len(pts), int(progress * len(pts))))
    if progress > 0:
        draw.line(pts[:stop], fill=fill, width=width, joint='curve')


def working_image(n: int, kind: int) -> Image.Image:
    """Original illustrative photographs plus genuinely changing work layers.

    These are authored animation/composites, not filmed creator/user activity.
    No reference still, frame or audio enters these layers.
    """
    name = ['creator-work', 'creator-portrait', 'workroom'][kind]
    im = crop_camera(image_asset(name), n, kind)
    t = n / FPS
    layer = Image.new('RGBA', (W, H))
    d = ImageDraw.Draw(layer)
    if kind == 0:
        # Pen mark writes across the work independently of fixed photo framing.
        phase = min(1, .13 + t * .26)
        pts = [(810 + 280 * i / 140,
                580 + 21 * math.sin(i / 140 * math.pi * 2)) for i in range(141)]
        draw_polyline(d, pts, phase, (*CORAL, 220), 5)
        px, py = pts[min(140, int(phase * 140))]
        d.line((px, py, px + 105, py - 65), fill=(75, 49, 37, 220), width=13)
        d.polygon([(px - 3, py + 2), (px + 14, py - 14), (px + 19, py - 6)], fill=(32, 30, 29, 255))
        # Small independent paper tab slides into place, never changing geometry.
        dx = 12 * math.sin(t * 1.3)
        d.rectangle((1285 + dx, 380, 1390 + dx, 422), fill=(153, 190, 172, 210))
    elif kind == 1:
        # A moving leaf and sheet trace in front of the portrait's work surface.
        shift = 18 * math.sin((t - 2.61) * 1.8)
        d.polygon([(760 + shift, 710), (1060 + shift, 670), (1090 + shift, 805), (780 + shift, 847)],
                  fill=(247, 245, 238, 130))
        for i in range(5):
            length = 130 + 25 * math.sin(t * 1.4 + i)
            d.line((810 + shift, 733 + i * 15, 810 + shift + length, 715 + i * 15),
                   fill=(69, 72, 66, 190), width=3)
        theta = .1 * math.sin(t * 2)
        d.line((1190, 515, 1190 + 80 * math.cos(theta), 515 - 120 * math.sin(theta)),
               fill=(143, 160, 117, 200), width=5)
    else:
        # Separate page/ink layer moves within the stable masked workroom.
        x = 805 + 24 * math.sin((t - 3.83) * 1.3)
        y = 460 + 8 * math.sin(t * 1.7)
        d.polygon([(x, y), (x + 330, y - 30), (x + 350, y + 170), (x + 15, y + 185)],
                  fill=(246, 243, 232, 250))
        phase = (t - 3.83) / 1.22
        pts = [(x + 45 + i * 2.6, y + 64 + 16 * math.sin(i / 16)) for i in range(100)]
        draw_polyline(d, pts, min(1, .2 + phase), (67, 83, 74, 220), 4)
        d.ellipse((x + 195, y + 103, x + 218, y + 126), fill=(*CORAL, 170))
    return Image.alpha_composite(im.convert('RGBA'), layer).convert('RGB')


def mask_disc(im: Image.Image, radius: float) -> Image.Image:
    y, x = np.ogrid[:H, :W]
    distance = np.sqrt((x - W / 2) ** 2 + (y - H / 2) ** 2)
    # One-pixel analytic antialiasing, no softened mask or incoming shot dissolve.
    a = np.clip(radius + .5 - distance, 0, 1)
    mask = Image.fromarray(np.uint8(a * 255), 'L')
    out = Image.new('RGB', (W, H), WHITE)
    out.paste(im, (0, 0), mask)
    return out


def guides(im: Image.Image, radius: float) -> None:
    d = ImageDraw.Draw(im)
    color = (219, 219, 219)
    for y in [H / 2 - radius, H / 2 + radius]:
        for x in range(0, W, 21):
            d.line((x, round(y), x + 10, round(y)), fill=color, width=1)
    for x in [W / 2 - radius, W / 2 + radius]:
        for y in range(0, H, 21):
            d.line((round(x), y, round(x), y + 10), fill=color, width=1)


def text_state(q: float) -> tuple[str, float, float]:
    """Sequential character changes, with brief coral emphasis then black holds.

    Width multipliers represent the brackets' independent reflow/settling. They
    do not stretch glyphs or blend incoming letters with outgoing ones.
    """
    f = math.floor(q)
    if f < 130:
        return 'FREE', max(0, 1 - (q - 113) / 6), 1 + .09 * max(0, 1 - (q - 113) / 5)
    sequence = {
        130: 'F', 131: 'F', 132: 'F', 133: 'FA', 134: 'FA', 135: 'FAI',
        136: 'FAIR', 137: 'FAIR', 138: 'FAIR', 139: 'FAI', 140: 'FA', 141: 'F',
        142: 'P', 143: 'PA', 144: 'PAID',
    }
    if f < 145:
        content = sequence[f]
        accent = 0 if f in [136, 137] else 1
        bracket = 1.35 if f in [130, 131, 132, 141] else 1.12
        return content, accent, bracket
    if f < 162:
        return 'PAID', max(0, 1 - (q - 144) / 5), 1
    sequence = {162: 'FREE. CREATORS P', 163: 'FREE. CREATORS PA',
                164: 'FREE. CREATORS PA', 165: 'FREE. CREATORS PAI',
                166: 'FREE. CREATORS PAI'}
    return sequence.get(f, 'FREE. CREATORS PAID.'), 0, 1 + .03 * max(0, 1 - (q - 162) / 5)


def bracket_text(im: Image.Image, q: float) -> None:
    text, accent, expansion = text_state(q)
    color = tuple(round(lerp(a, b, accent)) for a, b in zip(INK, CORAL))
    # Narrowing here matches the supplied regular sans proportions. Every word
    # keeps the same cap height. The final phrase expands by word length only.
    native_w = math.ceil(FONT.getlength(text))
    glyph = Image.new('RGBA', (native_w + 4, 110))
    ImageDraw.Draw(glyph).text((0, 1), text, font=FONT, fill=(*color, 255))
    glyph = glyph.resize((round(glyph.width * .90), glyph.height), Image.Resampling.LANCZOS)
    width = glyph.width
    # Deletion leaves the remaining prefix at the original left position. The
    # final phrase also reveals rightward inside its already expanded brackets.
    reserved = text
    if 130 <= q < 142:
        reserved = 'FAIR'
    elif q >= 162:
        reserved = 'FREE. CREATORS PAID.'
    layout_width = round((math.ceil(FONT.getlength(reserved)) + 4) * .90)
    x = round(W / 2 - layout_width / 2)
    # Native source group width rises76→105→113→116→117px.
    # SUNSET's four-letter words need twice the source two-letter group width.
    typing_span = interp({130: 228, 131: 236, 132: 270, 133: 315,
                          134: 327, 135: 339, 137: 348, 141: 351}, q)
    if 130 <= q < 142:
        x = round(W / 2 - typing_span / 2 + 29)
    # NimbusSans has cap bounds y=0..55. Center capitals exactly at540.
    im.paste(glyph, (x, 512), glyph)
    # Square brackets remain black; their arms settle independently of letters.
    if q >= 162:
        expansion = interp({162: .97, 167: 1.018, 176: 1}, q)
    half = typing_span / 2 if 130 <= q < 142 else (layout_width / 2 + 29) * expansion
    left, right = round(W / 2 - half), round(W / 2 + half)
    d = ImageDraw.Draw(im)
    top, bottom, arm, thick = 504, 574, 13, 6
    d.line((left + arm, top, left, top, left, bottom, left + arm, bottom), fill=INK, width=thick)
    d.line((right - arm, top, right, top, right, bottom, right - arm, bottom), fill=INK, width=thick)


def render(n: int) -> Image.Image:
    q = math.floor(source_frame(n))
    if q < 91:
        kind = 0 if q < 47 else 1 if q < 69 else 2
        shot = working_image(n, kind)
        if q < 20:
            im = shot
        elif q < 26:
            # Top-edge source wedges measured x≈13,19,26,35,49,72px.
            # This huge boundary stays huge until the abrupt f26 handoff.
            edge = interp({20: 13, 21: 19, 22: 26, 23: 35, 24: 49, 25: 72}, min(q, 25))
            radius = math.sqrt(((W - 6) / 2 - edge * SCALE) ** 2 + (H / 2) ** 2)
            im = mask_disc(shot, radius)
        else:
            radius = interp(DIAMETERS, min(q, 90)) * SCALE / 2
            # Guides drawn behind imagery, tangent to its exact circle.
            im = Image.new('RGB', (W, H), WHITE)
            guides(im, radius)
            disc = mask_disc(shot, radius)
            y, x = np.ogrid[:H, :W]
            mask = Image.fromarray(np.uint8(np.clip(radius + .5 - np.sqrt((x-W/2)**2+(y-H/2)**2), 0, 1)*255))
            im.paste(disc, (0, 0), mask)
    else:
        im = Image.new('RGB', (W, H), WHITE)
        if q < 113:
            diameter = interp({91: 22, 92: 18, 93: 16, 94: 15, 95: 14, 98: 13, 112: 13}, q) * SCALE
            accent = max(0, min(1, (q - 107) / 5))
            color = tuple(round(lerp(a, b, accent)) for a, b in zip(INK, CORAL))
            yy = H / 2 + 7 * max(0, min(1, (q - 107) / 5))
            # Supersampling this tiny point retains its native round silhouette.
            tile = Image.new('RGB', (200, 200), WHITE)
            td = ImageDraw.Draw(tile)
            r = diameter * 2
            td.ellipse((100-r, 100-r, 100+r, 100+r), fill=color)
            tile = tile.resize((50, 50), Image.Resampling.LANCZOS)
            im.paste(tile, (935, round(yy - 25)))
        else:
            bracket_text(im, q)
    # Review sheets and filenames identify the study; picture remains unlabelled.
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 2, H), fill=WHITE)
    d.rectangle((1917, 0, 1919, H), fill=WHITE)
    return im


def manifest() -> dict:
    assets = {}
    for name in ['creator-work', 'creator-portrait', 'workroom']:
        path = ASSETS / (name + '.png')
        if not path.exists():
            path = FALLBACK
        assets[name] = {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}
    return {
        'dimensions': [W, H], 'fps': FPS, 'frames': FRAMES,
        'visual_duration': FRAMES / FPS, 'audio': None,
        'source_contract': {'native_dimensions': [1276, 720], 'fps': 18, 'frames': 195,
            'sha256': '289999ba2aa77973d302be6d23414613d51b3f708df11be2f89d9a8cbbe6a699'},
        'sampling': '195 native source poses map 1:1 to195 output frames at18fps. Uniform1.5x geometry with3px white side margins. Hard content cuts; no crossfades.',
        'events': [{'source_frame': f, 'seconds': f/18, 'first_output_frame': first_output_frame(f),
                    'event': s} for f, s in EVENTS],
        'native_circle_diameters_px': DIAMETERS,
        'font': {'path': FONT_PATH, 'sha256': sha(Path(FONT_PATH)), 'size': 75,
                 'cap_height_px': 55, 'horizontal_proportion': .9},
        'assets': assets,
        'scope': 'Original illustrative image composites. No actual new user, resource, payment or onchain action.',
        'reference_pixels_in_film': False,
    }


def gates() -> None:
    def pose(n: int) -> Image.Image:
        path = OUT / 'frames' / f'{n:06}.png'
        return Image.open(path).convert('RGB') if path.exists() else render(n)

    (OUT / 'gates').mkdir(parents=True, exist_ok=True)
    poses = [0, 25, 26, 47, 69, 90, 91, 112, 113, 130, 136, 141, 144, 161, 162, 167, 194]
    for f in poses:
        n = first_output_frame(f)
        pose(n).save(OUT / 'gates' / f'source-{f:03}-out-{n:03}.png')
    # Every side-by-side sheet stays private because it contains reference pixels.
    for name, frames in [
        ('keyposes', [0, 26, 47, 69, 91, 113, 144, 167]),
        ('critical-25-26', [24, 25, 26, 27]),
        ('critical-90-91', [89, 90, 91, 92]),
        ('critical-112-113', [110, 111, 112, 113, 114, 115]),
        ('typing-130-144', list(range(130, 145))),
        ('typing-162-167', list(range(161, 169))),
    ]:
        cw, ch, header = 640, 360, 36
        sheet = Image.new('RGB', (cw * 2, (ch + header) * len(frames)), (236, 236, 236))
        d = ImageDraw.Draw(sheet)
        for i, f in enumerate(frames):
            y = i * (ch + header)
            n = first_output_frame(f)
            ref = Image.open(REFERENCE / 'frames' / f'{f:06}.png').convert('RGB')
            sheet.paste(ref.resize((cw, ch), Image.Resampling.LANCZOS), (0, y + header))
            sheet.paste(pose(n).resize((cw, ch), Image.Resampling.LANCZOS), (cw, y + header))
            d.text((10, y + 5), f'PRIVATE REFERENCE f{f:03} / {f/18:.3f}s', font=LABEL, fill=INK)
            d.text((cw + 10, y + 5), f'ORIGINAL STUDY f{n:03} / {n/FPS:.3f}s', font=LABEL, fill=INK)
        sheet.save(OUT / 'gates' / f'private-{name}.jpg', quality=95)
    # Actual contiguous native-cadence loops establish local movement, which
    # a set of isolated held poses cannot demonstrate. No reference pixels.
    for name, first, last in [('work', 26, 46), ('portrait', 47, 68), ('desk', 69, 90)]:
        loop = [pose(n).crop((660, 240, 1260, 840)).resize((450, 450), Image.Resampling.LANCZOS)
                for n in range(first, last + 1)]
        loop[0].save(OUT / 'gates' / f'original-window-motion-{name}.gif',
                     save_all=True, append_images=loop[1:],
                     duration=[round((i+1)*100/FPS)*10-round(i*100/FPS)*10
                               for i in range(len(loop))], loop=0)
    (OUT / 'manifest.json').write_text(json.dumps(manifest(), indent=2) + '\n')


def frames() -> None:
    path = OUT / 'frames'
    path.mkdir(parents=True, exist_ok=True)
    for n in range(FRAMES):
        render(n).save(path / f'{n:06}.png', compress_level=2)
        if n % 30 == 0:
            print(f'Rendered {n}/{FRAMES}', flush=True)
    (OUT / 'manifest.json').write_text(json.dumps(manifest(), indent=2) + '\n')


def encode() -> None:
    movie = OUT / 'sunset-minimal-motion-match.mp4'
    if movie.exists():
        raise SystemExit('Refusing to overwrite an existing proof encode.')
    subprocess.run(['ffmpeg', '-v', 'error', '-framerate', str(FPS), '-i',
        str(OUT / 'frames/%06d.png'), '-frames:v', str(FRAMES), '-an', '-c:v', 'libx264',
        '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-color_range', 'tv',
        '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
        '-vf', 'scale=in_range=full:out_range=tv:out_color_matrix=bt709,'
        'setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709',
        '-movflags', '+faststart', str(movie)], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(movie), '-f', 'null', '-'], check=True)
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames',
        '-show_streams', '-show_format', '-of', 'json', str(movie)]))
    st = probe['streams'][0]
    assert st['nb_read_frames'] == str(FRAMES), st
    assert (st['width'], st['height']) == (W, H), st
    assert st['r_frame_rate'] == '18/1', st
    assert st['color_range'] == 'tv', st
    assert all(st[k] == 'bt709' for k in ['color_space', 'color_primaries', 'color_transfer']), st
    assert st['codec_name'] == 'h264' and st['pix_fmt'] == 'yuv420p', st
    assert len(probe['streams']) == 1, probe
    data = movie.read_bytes()
    assert data.index(b'moov') < data.index(b'mdat')
    result = {'file': str(movie.relative_to(ROOT)), 'bytes': len(data), 'sha256': sha(movie),
              'full_decode_passed': True, 'probe': probe}
    (OUT / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['file', 'bytes', 'sha256', 'full_decode_passed']}))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--gates', action='store_true')
    parser.add_argument('--frames', action='store_true')
    parser.add_argument('--encode', action='store_true')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.gates:
        gates()
    if args.frames:
        frames()
    if args.encode:
        encode()


if __name__ == '__main__':
    main()
