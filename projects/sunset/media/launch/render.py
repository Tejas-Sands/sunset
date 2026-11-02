#!/usr/bin/env python3
"""Render SUNSET's launch film from real captures and locally synthesized narration.

Run from the repository root. Dependencies already available for this edit:
FFmpeg/ffprobe, Pillow, fontTools (WOFF2 support), and CairoSVG.
Generated media stays in the ignored .publication directory.
"""
import argparse
import array
import hashlib
import json
import math
from pathlib import Path
import subprocess
import textwrap
import wave

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[4]
PUBLIC = ROOT / 'projects/sunset/public'
W, H, FPS = 1920, 1080, 25
CREAM, GREEN, INK, ORANGE = '#f7f5ed', '#304b3e', '#253c30', '#d75835'


def run(args):
    subprocess.run([str(a) for a in args], check=True, stdout=subprocess.DEVNULL)


def font(size, weight=400, serif=False):
    path = Path('/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf') if serif else OUT / 'Geist.ttf'
    f = ImageFont.truetype(str(path), size)
    if not serif:
        f.set_variation_by_axes([weight])
    return f


def lines(draw, text, xy, size=88, fill=INK, weight=600, spacing=7, serif=False):
    draw.multiline_text(xy, text, font=font(size, weight, serif), fill=fill, spacing=spacing)


def label(draw, text, xy=(100, 177), dark=False):
    draw.text(xy, text.upper(), font=font(23, 600), fill='#b9ccb5' if dark else '#6c7b69', spacing=2)


def base(dark=False, chapter=''):
    im = Image.new('RGB', (W, H), GREEN if dark else CREAM)
    d = ImageDraw.Draw(im)
    logo = Image.open(OUT / 'logo.png').convert('RGBA').resize((58, 58), Image.Resampling.LANCZOS)
    im.paste(logo, (96, 42), logo)
    d.text((169, 44), 'SUNSET', font=font(38, 680), fill=CREAM if dark else INK)
    if chapter:
        d.text((100, 873), chapter.upper(), font=font(21, 500), fill='#b9ccb5' if dark else '#6c7b69')
    d.line((100, 129, 1820, 129), fill='#57705f' if dark else '#dadfd3', width=1)
    return im


def rounded_image(im, source, box, crop=None, radius=25, contain=False):
    image = Image.open(source).convert('RGB')
    if crop:
        image = image.crop(tuple(crop))
    x, y, w, h = box
    if contain:
        fitted = ImageOps.contain(image, (w, h), method=Image.Resampling.LANCZOS)
        image = Image.new('RGB', (w, h), '#e4e8db')
        image.paste(fitted, ((w-fitted.width)//2, (h-fitted.height)//2))
    else:
        image = ImageOps.fit(image, (w, h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.35))
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    im.paste(image, (x, y), mask)


def make_card(scene, index):
    kind = scene['kind']
    dark = kind in ('hook', 'rule', 'close')
    im = base(dark, scene.get('chapter', ''))
    d = ImageDraw.Draw(im)
    if kind == 'hook':
        label(d, 'A different starting point', dark=True)
        lines(d, 'The sponsors\nneed a wallet.', (100, 235), 108, CREAM, 540, spacing=0)
        lines(d, 'The learners\ndon’t.', (1040, 410), 108, '#f5b28b', 540, spacing=0)
        d.line((974, 245, 974, 772), fill='#738b75', width=2)
        d.text((103, 785), 'Public resources. Shared possibility.', font=font(31), fill='#d4ddc9')
    elif kind in ('brand', 'close'):
        label(d, 'Support once. Share forever.', dark=dark)
        title = 'Fund it once.\nLet everyone\nkeep a copy.' if kind == 'brand' else 'Good things\nbelong to\neveryone.'
        lines(d, title, (100, 240), 102, CREAM if dark else INK, 560, spacing=0)
        rounded_image(im, PUBLIC / 'images/sunset-commons-hero.webp', (1055, 182, 765, 665), radius=30)
        d = ImageDraw.Draw(im)
        if kind == 'close':
            d.rounded_rectangle((100, 700, 933, 784), radius=18, fill=ORANGE)
            d.text((129, 714), 'sunset-lemon.vercel.app', font=font(46, 600), fill=CREAM)
            d.text((102, 818), 'Explore the prototype · Built on NEAR testnet', font=font(27), fill='#d4ddc9')
    elif kind == 'rule':
        label(d, 'The refund rule · not a live expiry demonstration', dark=True)
        lines(d, 'Deadlines\nmean something.', (100, 245), 104, CREAM, 520, spacing=0)
        for y, title, detail in [(270, 'Funding target missed', 'Contribution becomes refundable'), (548, 'Release deadline missed', 'Contribution becomes refundable')]:
            d.rounded_rectangle((1075, y, 1815, y+205), radius=24, fill='#3f5d4b', outline='#7c947e', width=1)
            d.ellipse((1110, y+37, 1130, y+57), fill='#f5b28b')
            d.text((1153, y+26), title, font=font(34, 550), fill=CREAM)
            d.text((1110, y+103), detail, font=font(29), fill='#d4ddc9')
    elif kind == 'proof':
        label(d, 'Finalized public transactions · operator-controlled demo')
        lines(d, scene['title'], (100, 246), 93, INK, 550, spacing=2)
        lines(d, scene['detail'], (105, 655), 29, '#667460', 430, spacing=13)
        d.rounded_rectangle((1000, 204, 1818, 827), radius=30, fill='#e4e8db')
        d.text((1050, 257), scene['proof_label'], font=font(25, 600), fill=GREEN)
        d.text((1044, 318), '0.10', font=font(171, 500), fill=ORANGE)
        d.text((1062, 516), 'testNEAR', font=font(48, 550), fill=GREEN)
        lines(d, scene['proof_detail'], (1062, 610), 30, INK, 450, spacing=11)
        d.rounded_rectangle((1057, 741, 1757, 790), radius=12, fill=GREEN)
        d.text((1082, 750), 'FINAL · ' + scene['tx_short'], font=font(23, 550), fill=CREAM)
    elif kind == 'capture':
        path = ASSETS / 'footage' / scene['file']
        if not path.is_file() or path.stat().st_size < 100:
            raise FileNotFoundError(f'Missing genuine capture: {path}')
        label(d, scene['eyebrow'])
        lines(d, scene['title'], (100, 246), scene.get('title_size', 89), INK, 550, spacing=2)
        lines(d, scene.get('detail', ''), (105, 660), 29, '#667460', 430, spacing=13)
        rounded_image(im, path, (835, 180, 985, 666), scene.get('crop'), radius=22, contain=scene.get('contain',True))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((855, 789, 1800, 829), radius=9, fill=GREEN)
        d.text((877, 794), scene.get('source_label', 'ACTUAL CAPTURE · LIVE NEAR TESTNET'), font=font(20, 550), fill=CREAM)
    else:
        raise ValueError(kind)
    path = OUT / f'card-{index:02d}.png'
    im.save(path)
    return path


def srt_stamp(value):
    ms = round(value * 1000)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, ms = divmod(ms, 1000)
    return f'{hours:02}:{minutes:02}:{seconds:02},{ms:03}'


def ass_stamp(value):
    cs = round(value * 100)
    hours, cs = divmod(cs, 360000)
    minutes, cs = divmod(cs, 6000)
    seconds, cs = divmod(cs, 100)
    return f'{hours}:{minutes:02}:{seconds:02}.{cs:02}'


def captions(timing, scale):
    srt, events = [], []
    for s in timing['sentences']:
        text = '\n'.join(textwrap.wrap(s['text'], 53))
        assert len(text.splitlines()) <= 2, 'Caption needs editing for legibility'
        start, end = s['start'] * scale, s['end'] * scale
        srt.append(f"{s['index']}\n{srt_stamp(start)} --> {srt_stamp(end)}\n{text}\n")
        events.append(f"Dialogue: 0,{ass_stamp(start)},{ass_stamp(end)},Default,,0,0,0,,{{\\fad(90,90)}}" + text.replace('\n', '\\N'))
    (OUT / 'sunset-launch.srt').write_text('\n'.join(srt))
    header = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Geist,44,&H00EDF5F7,&H000000FF,&H00213428,&H00213428,0,0,0,0,100,100,0,0,3,16,0,2,130,130,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    (OUT / 'captions.ass').write_text(header + '\n'.join(events) + '\n')


def ambient(duration):
    """Original quiet chord bed, synthesized here; no third-party music samples."""
    rate = 24000
    chords = [(130.8128,196,246.9417,293.6648), (110,164.8138,196,246.9417), (87.3071,130.8128,164.8138,220), (97.9989,146.8324,196,220)]
    samples = array.array('h')
    for n in range(round(duration * rate)):
        t = n / rate
        chord = chords[int(t / 9) % 4]
        env = min(t / 2, 1, (duration - t) / 3)
        swell = .78 + .22 * math.sin(math.pi * (t % 9) / 9)
        value = sum(math.sin(2*math.pi*f*t) + .1*math.sin(4*math.pi*f*t) for f in chord)
        samples.append(round(32767 * .0065 * max(0, env) * swell * value))
    with wave.open(str(OUT / 'original-ambient.wav'), 'wb') as f:
        f.setparams((1, 2, rate, len(samples), 'NONE', 'not compressed'))
        f.writeframes(samples.tobytes())


def verify(path):
    probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))
    video = next(s for s in probe['streams'] if s['codec_type']=='video')
    audio = next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert video['codec_name']=='h264' and video['pix_fmt']=='yuv420p'
    assert (video['width'],video['height'])==(W,H) and audio['codec_name']=='aac'
    assert 80 <= float(probe['format']['duration']) <= 100
    assert path.stat().st_size < 512*1024*1024
    probe['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT / 'ffprobe.json').write_text(json.dumps(probe, indent=2)+'\n')
    return probe


def provenance(storyboard, timing, storyboard_path):
    inputs=[Path(__file__),storyboard_path,ASSETS/'voice/narration.wav',ASSETS/'voice/timing.json',ASSETS/'voice/provenance.json',ROOT/'projects/sunset/evidence/testnet-showcase.json',ROOT/'projects/sunset/evidence/browser-showcase.json',PUBLIC/'icon.svg',PUBLIC/'images/sunset-commons-hero.webp',PUBLIC/'fonts/geist-latin-variable.woff2']
    inputs += [ASSETS/'footage'/s['file'] for s in storyboard['scenes'] if s['kind']=='capture']
    manifest={'format':'Edited film from genuine browser still captures, gentle camera moves and factual editorial transaction summaries; not a continuous screen recording.','narration':'Local pretrained Kokoro af_heart synthetic narration; no voice cloning.','voice_model_sha256':timing['model_sha256'],'voice_bank_sha256':timing['voices_sha256'],'voice_source_timing':'Per-sentence synthesis sample boundaries, retimed with pitch-preserving atempo.','music':'Original quiet sine-wave chord bed synthesized by render.py; no samples or third-party music.','proof_scope':'Actual main-campaign funding, public release, native creator withdrawal and stewardship handover; refund section describes the contract rule, not an executed expiry-refund demo. Testnet demo roles are operator-controlled.','perceptual_audio_listening':'Not verified by this tool environment; audio codecs, finite samples, levels and synchronization are checked objectively.','inputs':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in dict.fromkeys(inputs)]}
    (OUT/'media-provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (OUT/'sunset-launch-credits.md').write_text('''# SUNSET launch film credits

SUNSET software and renderer: MIT, repository contributors. Original learning-pack content: CC0-1.0.

Visual identity: existing SUNSET SVG icon and site palette. Existing book/sunset hero artwork was generated with OpenAI image generation on 1 November 2026; exact prompt and original asset provenance are in projects/sunset/public/images/README.md. No new generated product screenshots or fabricated wallet UI are used.

Typography: bundled Geist, SIL Open Font License 1.1 (projects/sunset/public/fonts/OFL-Geist.txt). The film uses the existing font converted from WOFF2 to TTF without design changes.

Narration: locally synthesized Kokoro-ONNX 0.6.1 / pretrained af_heart voice, official FP16 model; model Apache-2.0, ONNX wrapper MIT. No voice cloning or paid API. Full upstream provenance and license copies are in the adjacent voice delivery directory; model and voice-bank hashes are in media-provenance.json.

Music: original low-volume sine-wave chord bed synthesized by this renderer. No licensed commercial recording or third-party samples.

Footage: genuine hosted SUNSET browser captures and actual downloaded-game execution in a fresh offline browser, supplied by the browser-verification agent. These stills are edited with gentle camera moves; this is not a continuous screen recording. Financial numbers are labeled editorial summaries of actual finalized NEAR testnet transactions, with full evidence retained in projects/sunset/evidence/testnet-showcase.json. Demo role accounts share one operator. The refund card states a contract rule; a live expiry refund is not shown.

The film has AI narration, a persistent NEAR TESTNET label, burned-in captions and a matching SRT sidecar. Objective media checks are in ffprobe.json and media-provenance.json. Perceptual listening is not verified by the tool environment.
''')


def main():
    global OUT, ASSETS
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets',type=Path,default=ROOT/'.publication/sunset-launch-v1')
    parser.add_argument('--storyboard',type=Path,default=Path(__file__).with_name('storyboard.json'))
    parser.add_argument('--duration',type=float,default=82)
    parser.add_argument('--cards-only',action='store_true')
    args=parser.parse_args()
    ASSETS=args.assets.resolve();OUT=ASSETS/'render';OUT.mkdir(parents=True,exist_ok=True)
    from fontTools.ttLib import TTFont
    import cairosvg
    f=TTFont(PUBLIC/'fonts/geist-latin-variable.woff2');f.flavor=None;f.save(OUT/'Geist.ttf')
    cairosvg.svg2png(url=str(PUBLIC/'icon.svg'),write_to=str(OUT/'logo.png'),output_width=256,output_height=256)
    timing=json.loads((ASSETS/'voice/timing.json').read_text())
    storyboard=json.loads(args.storyboard.read_text())
    scale=args.duration/timing['duration'];sentences=timing['sentences']
    captions(timing,scale)
    segments=[]
    for i,scene in enumerate(storyboard['scenes']):
        start=0 if i==0 else sentences[scene['sentence_start']-1]['start']*scale
        end=args.duration if i==len(storyboard['scenes'])-1 else sentences[storyboard['scenes'][i+1]['sentence_start']-1]['start']*scale
        frames=round(end*FPS)-round(start*FPS);assert frames>0
        card=make_card(scene,i)
        if args.cards_only:continue
        segment=OUT/f'segment-{i:02d}.mp4';segments.append(segment)
        fade_color='0x304b3e' if scene['kind'] in ('hook','rule','close') else '0xf7f5ed'
        vf=f"zoompan=z='1+0.018*on/{frames}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s={W}x{H}:fps={FPS},fade=t=in:st=0:d=0.16:color={fade_color},format=yuv420p"
        run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',card,'-vf',vf,'-frames:v',frames,'-an','-c:v','libx264','-preset','veryfast','-crf','17','-threads','4',segment])
        print(f'Rendered scene {i+1}/{len(storyboard["scenes"])}: {frames/FPS:.2f}s',flush=True)
    poster=Image.open(make_card({'kind':'brand','chapter':'SUPPORT ONCE. SHARE FOREVER.'},99))
    d=ImageDraw.Draw(poster)
    d.rounded_rectangle((100,700,933,784),radius=18,fill=ORANGE)
    d.text((129,714),'sunset-lemon.vercel.app',font=font(46,600),fill=CREAM)
    d.rounded_rectangle((1510,44,1820,102),radius=8,fill=ORANGE)
    d.text((1553,57),'NEAR TESTNET',font=font(27,600),fill=CREAM)
    poster.save(OUT/'sunset-launch-poster.png')
    if args.cards_only:return
    ambient(args.duration)
    concat=OUT/'segments.txt';concat.write_text(''.join(f"file '{p.as_posix()}'\n" for p in segments))
    target=OUT/'sunset-launch.mp4';pace=1/scale
    video_filter=f"subtitles=filename={str(OUT/'captions.ass')}:fontsdir={OUT},drawbox=x=1510:y=44:w=310:h=58:color=0xd75835:t=fill,drawtext=fontfile={str(OUT/'Geist.ttf')}:text='NEAR TESTNET':fontsize=27:fontcolor=0xf7f5ed:x=1556:y=58,drawbox=x=100:y=907:w=1720:h=2:color=0xd75835:t=fill"
    audio_filter=f"[1:a]atempo={pace:.9f},aresample=48000[voice];[2:a]volume=0.7,aresample=48000[bed];[voice][bed]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]"
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',concat,'-i',ASSETS/'voice/narration.wav','-i',OUT/'original-ambient.wav','-filter_complex',audio_filter,'-vf',video_filter,'-map','0:v','-map','[a]','-t',args.duration,'-c:v','libx264','-crf','19','-preset','fast','-threads','4','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-metadata','title=SUNSET — Support once. Share forever.','-metadata','comment=Actual NEAR testnet demonstration; locally synthesized AI narration; see credits and evidence.',target])
    probe=verify(target)
    provenance(storyboard,timing,args.storyboard.resolve())
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',target,'-vf','fps=1/7,scale=480:270,tile=3x4','-frames:v','1',OUT/'contact-sheet.jpg'])
    print(json.dumps({'output':str(target),'duration':probe['format']['duration'],'bytes':target.stat().st_size,'sha256':probe['sha256']},indent=2))


if __name__=='__main__':
    main()
