#!/usr/bin/env python3
"""Verify original outputs and create separately labelled PRIVATE comparisons."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / '.publication/sunset-launch-v14'
STUDY = ROOT / '.publication/sunset-reference-study-20261105'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
CASES = [
    ('collage', 'feel-good', 'sunset-collage-motion-match-8s.mp4', 1920, 1440, 20, 160),
    ('minimal', 'intelligence', 'sunset-minimal-motion-match.mp4', 1920, 1080, 18, 195),
]


def digest(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()


def inspect(path, width, height, fps, count):
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-count_frames', '-show_streams',
        '-show_format', '-of', 'json', str(path)]))
    assert len(probe['streams']) == 1, probe
    stream = probe['streams'][0]
    assert stream['codec_name'] == 'h264', stream
    assert (stream['width'], stream['height']) == (width, height), stream
    assert stream['r_frame_rate'] == f'{fps}/1', stream
    assert int(stream['nb_read_frames']) == count, stream
    assert abs(float(stream['duration']) - count / fps) < .001, stream
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(path),
                    '-f', 'null', '-'], check=True)
    data = path.read_bytes()
    atoms, offset = [], 0
    while offset + 8 <= len(data):
        size, kind = struct.unpack_from('>I4s', data, offset)
        if size == 1:
            size = struct.unpack_from('>Q', data, offset + 8)[0]
        if size == 0:
            size = len(data) - offset
        assert size >= 8 and offset + size <= len(data), (offset, size)
        atoms.append(kind.decode('ascii'))
        offset += size
    assert atoms.index('moov') < atoms.index('mdat'), atoms
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path),
            'bytes': len(data), 'width': width, 'height': height,
            'fps': fps, 'frames': count, 'duration': count / fps,
            'audio_streams': 0, 'full_decode_passed': True, 'atoms': atoms,
            'color_space': stream.get('color_space'),
            'color_range': stream.get('color_range'),
            'color_primaries': stream.get('color_primaries'),
            'color_transfer': stream.get('color_transfer')}


def compare(name, reference, movie, width, height, fps, count):
    index = json.loads((STUDY / reference / 'index.json').read_text())
    source = Path(index['source_path'])
    assert source.is_file(), source
    assert digest(source) == index['source_sha256'], source
    destination = OUT / name / 'PRIVATE-source-vs-study.mp4'
    if not destination.exists():
        left = ('scale=960:720' if name == 'collage' else
                'scale=1914:1080,pad=1920:1080:3:0:white,scale=960:540')
        image_height = height // 2
        graph = (
            f'[0:v]trim=end_frame={count},setpts=PTS-STARTPTS,{left}[a];'
            f'[1:v]setpts=PTS-STARTPTS,scale=960:{image_height}[b];'
            '[a][b]hstack,pad=1920:ih+44:0:44:color=0x161a1a,'
            f"drawtext=fontfile={FONT}:text='PRIVATE REFERENCE':x=24:y=12:fontsize=20:fontcolor=white,"
            f"drawtext=fontfile={FONT}:text='ORIGINAL MOTION STUDY':x=984:y=12:fontsize=20:fontcolor=white[v]")
        subprocess.run(['ffmpeg', '-v', 'error', '-n', '-i', str(source),
                        '-i', str(movie), '-filter_complex', graph, '-map', '[v]',
                        '-frames:v', str(count), '-r', str(fps), '-an',
                        '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast',
                        '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                        str(destination)], check=True)
    return inspect(destination, 1920, height // 2 + 44, fps, count)


def main():
    results = []
    for name, reference, filename, width, height, fps, count in CASES:
        movie = OUT / name / filename
        result = inspect(movie, width, height, fps, count)
        assert result['color_range'] == 'tv', result
        assert all(result[key] == 'bt709' for key in
                   ['color_space', 'color_primaries', 'color_transfer']), result
        result['private_comparison'] = compare(name, reference, movie, width, height, fps, count)
        results.append(result)
    previous = json.loads((ROOT / 'projects/sunset/evidence/launch-concept-v13.json').read_text())
    retained = previous['preserved_movies'] | {
        previous['style_preview']['path']: previous['style_preview']['sha256']}
    for path, expected in retained.items():
        assert digest(ROOT / path) == expected, path
    report = {'outputs': results, 'older_movies_preserved': retained,
              'limits': ['Decode/identity checks do not prove creative fidelity.',
                         'Private comparisons contain supplied reference images; original studies do not.',
                         'Silent motion studies; no continuous human playback or listening assessment claimed.']}
    (OUT / 'independent-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'outputs': results, 'preserved_movies': len(retained)}, indent=2))


if __name__ == '__main__':
    main()
