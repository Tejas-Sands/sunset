#!/usr/bin/env python3
"""Finish the verified V19 movie locally; no browser, server or network required.

Run `finish.py stills`, then `audio.py`, then `finish.py render` from any directory.
Generated files live in ignored .publication/sunset-launch-v20. Existing movies
are never overwritten. Original animation plays at its original frame cadence;
the two extra reading holds are explicit in frame-map.json.
"""
import argparse
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / '.publication/sunset-launch-v20'
MASTER = ROOT / '.publication/sunset-launch-v19/sunset-launch-v19.mp4'
CAPTURE = ROOT / '.publication/sunset-launch-v15/capture/unchecked.png'
PROVENANCE = ROOT / '.publication/sunset-launch-v15/capture/capture-provenance.json'
FACE = ROOT / '.publication/sunset-launch-v14/assets/creator-portrait.png'
ROOM = ROOT / '.publication/sunset-launch-v14/assets/workroom.png'
HANDS = ROOT / '.publication/sunset-launch-v13/assets/creator-cutout.png'
FONT = ROOT / '.publication/sunset-launch-v1/render/Geist.ttf'
W, H, FPS, FRAMES = 1920, 1080, 30, 1020
PAPER, INK, CORAL = '#f7f5ed', '#183c2e', '#d25632'
NATIVE_ROI = (665, 350, 1445, 500)
NATIVE_BOX = (310, 511, 1610, 761)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inputs():
    assert sha(MASTER) == '14bce15346a508f90970f15fbb8b0d5243bceedb23179ff8bf9e267900698718'
    proof = json.loads(PROVENANCE.read_text())
    assert proof['source_unchanged'] and proof['browser_offline_before_file_open']
    assert not proof['app_or_pack_edits'] and proof['chain_mutations'] == 0
    assert not proof['performed_underlying_handbook_procedure']
    assert sha(CAPTURE) == proof['samples'][0]['sha256']
    assert Image.open(CAPTURE).size == (W, H)
    paths = [MASTER, CAPTURE, PROVENANCE, ROOT / proof['source_file'], FACE, ROOM, HANDS, FONT,
             ROOT / 'projects/sunset/public/icon.svg']
    return {str(p.relative_to(ROOT)): sha(p) for p in paths}


@lru_cache(maxsize=32)
def font(size, weight=500):
    result = ImageFont.truetype(str(FONT), size)
    result.set_variation_by_axes([weight])
    return result


def text(image, xy, words, size, colour=INK, weight=500, anchor=None):
    ImageDraw.Draw(image).text(xy, words, font=font(size, weight), fill=colour, anchor=anchor)


def ease(value):
    x = max(0, min(1, value))
    return 1 - (1-x)**3


def smooth(value):
    x = max(0, min(1, value))
    return x*x*(3-2*x)


def place(image, layer, xy, width=None, angle=0):
    if width:
        layer = layer.resize((round(width), round(layer.height*width/layer.width)), Image.Resampling.LANCZOS)
    if angle:
        layer = layer.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    image.paste(layer, (round(xy[0]), round(xy[1])), layer if layer.mode == 'RGBA' else None)


@lru_cache(maxsize=1)
def native():
    return Image.open(CAPTURE).convert('RGB').crop(NATIVE_ROI).resize(
        (NATIVE_BOX[2]-NATIVE_BOX[0], NATIVE_BOX[3]-NATIVE_BOX[1]), Image.Resampling.LANCZOS)


@lru_cache(maxsize=1)
def assets():
    faces = Image.open(FACE).convert('RGBA')
    # The earlier purpose scene uses p0, the top-left portrait in the exact atlas.
    maker = ImageOps.fit(faces.crop((0, 0, faces.width//2, faces.height//2)), (570, 690))
    room = ImageEnhance.Brightness(Image.open(ROOM).convert('RGB')).enhance(.43)
    room = ImageOps.fit(room, (2180, H))
    hands = Image.open(HANDS).convert('RGBA')
    return maker, room, hands


def leaf_print(colour, number):
    page = Image.new('RGBA', (460, 600), colour)
    d = ImageDraw.Draw(page)
    d.line((230, 500, 230, 145), fill=INK, width=12)
    for box in [(65, 220, 225, 355), (240, 120, 400, 255), (240, 340, 410, 465)]:
        d.ellipse(box, fill=INK)
    d.ellipse((204, 95, 254, 145), fill=CORAL)
    text(page, (35, 40), ['LEARN', 'MAKE', 'SHARE'][number % 3], 40)
    d.line((35, 535, 425, 535), fill=INK, width=2)
    text(page, (35, 551), 'A USEFUL IDEA, SHARED', 22)
    return page


@lru_cache(maxsize=1)
def prints():
    return [leaf_print(c, i) for i, c in enumerate(['#e8b83a', '#e2e9cf', '#e1744f'])]


def reader(time):
    frame = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(frame)
    text(frame, (130, 100), 'Use it. Share it. Offline.', 116)
    text(frame, (264, 290), 'FROM THE EXISTING HANDBOOK', 28, '#536759')
    travel = ease((time-.2)/.8)
    # Authored copy sheets move behind the opaque, unaltered native text plane.
    for direction, fill in [(-1, '#e6bb43'), (1, '#d7e2ca')]:
        shift = round(direction*65*travel)
        d.rounded_rectangle((240+shift, 366+abs(shift)//3, 1680+shift, 816+abs(shift)//3),
                            radius=8, fill=fill, outline='#b9c4ad', width=2)
    d.rounded_rectangle((240, 350, 1680, 814), radius=8, fill='#fffdf7', outline='#d4dacb', width=2)
    text(frame, (306, 389), 'Keep a usable offline copy', 64)
    frame.paste(native(), NATIVE_BOX[:2])
    text(frame, (264, 850), 'Actual downloaded handbook · prior browser-offline capture', 27, '#536759')
    for x, phrase in [(264, 'No account.'), (780, 'No wallet.'), (1270, 'Keep the file.')]:
        d.line((x, 910, x+52, 910), fill=CORAL, width=5)
        text(frame, (x, 929), phrase, 48)
    return frame


def continuation(time):
    maker, room, hands = assets()
    camera = -1540*smooth((time-.9)/2.85)
    frame = room.crop((round(120+camera*.065), 0, round(120+camera*.065)+W, H))
    plane = Image.new('RGBA', (W, H))
    d = ImageDraw.Draw(plane)
    # Separate travel depths reveal the same maker, a fresh page, then more work.
    px, py = 1090+camera, 235-40*ease(time/.65)
    board = Image.new('RGBA', (620, 745), '#e5b83a')
    board.paste(maker, (25, 25), maker)
    place(plane, board, (px, py), angle=-5+8*ease(time/.8))
    sheetx = 200+camera*.82
    d.polygon([(sheetx, 380), (sheetx+690, 350), (sheetx+713, 1050), (sheetx-22, 1065)], fill='#f3edd8')
    for i in range(4):
        d.line((sheetx+65, 470+i*65, sheetx+520-i*30, 465+i*65), fill='#6b826c', width=5)
    path = [(sheetx+90+i*4, 820-185*((i/110)**.55)+35*math.sin(i/12))
            for i in range(round(110*ease(time/1.2))+1)]
    if len(path)>1:
        d.line(path, fill=CORAL, width=14, joint='curve')
    place(plane, hands, (15+camera*.68, 492+60*(1-ease(time/.6))), width=1130, angle=-4)
    for i, page in enumerate(prints()):
        x = 2220+i*500+camera*1.1
        y = 355+(i%2)*90+100*(1-ease((time-1.6-i*.2)/.8))
        place(plane, page, (x, y), angle=[11, -9, 6][i])
    frame.paste(plane, (0, 0), plane)
    # Protected, settled type; the world carries the motion.
    d = ImageDraw.Draw(frame)
    for y, phrase in [(88, 'Make the next'), (230, 'free thing possible.')]:
        width = round(d.textlength(phrase, font=font(110)))
        d.rectangle((88, y-4, 140+width, y+132), fill=INK)
        text(frame, (112, y), phrase, 110, '#f7f0df')
    if time<.4:
        previous = reader(4.2)
        frame.paste(previous, (round(-W*smooth(time/.4)), 0))
    return frame


def payoff(time):
    frame = Image.new('RGB', (W, H), '#f8f5ed')
    free_y = round(485-140*ease(time/.38))
    text(frame, (W//2, free_y), '[ FREE TO USE ]', 100, anchor='mt')
    progress = ease((time-.22)/.4)
    if progress:
        layer = Image.new('RGBA', (W, H))
        colour = (*ImageColor_rgb(CORAL), round(255*progress))
        text(layer, (W//2, round(573+32*(1-progress))), '[ CREATOR PAID ]', 100, colour, anchor='mt')
        frame.paste(layer, (0, 0), layer)
    return frame


def ImageColor_rgb(colour):
    return tuple(bytes.fromhex(colour.lstrip('#')))


def closing(frame, time):
    image = frame.copy()
    progress = ease((time-1.45)/.35)
    if progress:
        layer = Image.new('RGBA', (W, H))
        colour = (*ImageColor_rgb(INK), round(progress*255))
        text(layer, (960, round(852+12*(1-progress))), 'TRY THE TESTNET DEMO', 30, colour, anchor='mt')
        text(layer, (960, round(905+12*(1-progress))), 'sunset-lemon.vercel.app', 58, colour, anchor='mt')
        image.paste(layer, (0, 0), layer)
    return image


def frame_map():
    result = []
    def add(source, **extra):
        result.append({'frame': len(result), 'source': source, **extra})
    for n in range(492):
        add('v19', source_frame=n)
        if n in (428, 488):
            for _ in range(21 if n==428 else 18):
                add('v19', source_frame=n, explicit_reading_hold=True)
    for scene, count in [('reader',126), ('continuation',117)]:
        for n in range(count): add(scene, scene_frame=n)
    for n in range(690,714): add('v19', source_frame=n)
    for n in range(87): add('payoff', scene_frame=n)
    for n in range(780,885): add('v19-closing', source_frame=n, scene_frame=n-780)
    for n in range(30): add('v19-closing', source_frame=884, scene_frame=105+n, explicit_reading_hold=True)
    assert len(result) == FRAMES
    return result


def tag_colour(picture, output):
    # FFmpeg's scale sets the matrix but can leave frame primaries/transfer
    # unspecified. Set the H.264 VUI explicitly without re-encoding pixels.
    subprocess.run(['ffmpeg','-v','error','-n','-i',str(picture),'-map','0','-c','copy',
        '-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0',
        '-movflags','+faststart',str(output)],check=True)


def render():
    output = OUT / 'sunset-launch-v20.mp4'
    picture = OUT / 'picture-before-colour-tags.mp4'
    assert not output.exists(), f'Refusing to overwrite {output}'
    assert not picture.exists(), f'Refusing to overwrite {picture}'
    assert (OUT / 'audio/mix.wav').is_file(), 'Run audio.py first'
    mapping = frame_map()
    decoder = subprocess.Popen(['ffmpeg','-v','error','-i',str(MASTER),'-an','-pix_fmt','rgb24','-f','rawvideo','-'], stdout=subprocess.PIPE)
    with (OUT/'render.log').open('x') as log:
        encoder = subprocess.Popen(['ffmpeg','-v','warning','-n','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}',
            '-r','30','-i','-','-i',str(OUT/'audio/mix.wav'),'-map','0:v','-map','1:a',
            '-c:v','libx264','-preset','medium','-crf','15','-pix_fmt','yuv420p',
            '-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709',
            '-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709',
            '-c:a','aac','-b:a','320k','-ar','48000','-ac','2','-movflags','+faststart','-t','34',str(picture)],
            stdin=subprocess.PIPE, stderr=log)
        source_n, source_image = -1, None
        try:
            for item in mapping:
                if item['source'].startswith('v19'):
                    wanted = item['source_frame']
                    while source_n < wanted:
                        data = decoder.stdout.read(W*H*3)
                        assert len(data)==W*H*3, source_n+1
                        source_n += 1
                    source_image = Image.frombytes('RGB',(W,H),data)
                    image = closing(source_image, item['scene_frame']/FPS) if item['source']=='v19-closing' else source_image
                else:
                    image = globals()[item['source']](item['scene_frame']/FPS)
                encoder.stdin.write(image.tobytes())
                if item['frame']%150==0: print(f"Rendered {item['frame']}/{FRAMES}", flush=True)
            encoder.stdin.close()
            assert encoder.wait()==0, 'FFmpeg encoder failed; see render.log'
            assert decoder.wait()==0, 'Master decoding failed'
        finally:
            for process in (decoder, encoder):
                if process.poll() is None: process.terminate(); process.wait()
    (OUT/'frame-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
    tag_colour(picture, output)
    print(output)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['stills','render','check'])
    args=parser.parse_args()
    sources=inputs()
    mapping=frame_map()
    assert [(i['frame'],i['source_frame']) for i in mapping if i.get('source_frame') in [402,429,463,474]][:4] == [(402,402),(450,429),(484,463),(495,474)]
    OUT.mkdir(parents=True,exist_ok=True)
    manifest={'inputs':sources,'frames':FRAMES,'fps':FPS,'duration':34,'native_roi':NATIVE_ROI,'native_destination':NATIVE_BOX,
              'reader_frames':[531,656],'continuation_frames':[657,773],'payoff_frames':[798,884],'closing_frames':[885,1019],
              'source':{str(p.relative_to(ROOT)):sha(p) for p in Path(__file__).parent.glob('*.py')},
              'native_capture_scope':'Prior genuine browser-offline still excerpt; no new capture or procedure performance.',
              'retiming':'Original frames at 1x. Explicit holds after source428 (21 frames),488 (18),884 (30).',
              'new_browser_or_hyperframes_render':False}
    if args.command=='check':
        print(json.dumps({'ok':True,'frames':len(mapping),'inputs':len(sources)})); return
    if args.command=='stills':
        for name, image in [('reader',reader(2)),('same-maker',continuation(1.3)),('more-work',continuation(3.4)),('payoff',payoff(1.2))]:
            image.save(OUT/(name+'.png'))
            image.resize((390,219),Image.Resampling.LANCZOS).save(OUT/(name+'-390.png'))
        print(OUT); return
    render()
    (OUT/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':
    main()
