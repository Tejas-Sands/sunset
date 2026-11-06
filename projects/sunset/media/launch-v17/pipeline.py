#!/usr/bin/env python3
"""Prepare a local composition, then check/proof/render with pinned HyperFrames.

Examples (run from the repository root):
  python3 projects/sunset/media/launch-v17/pipeline.py prepare --composition .publication/sunset-launch-v17/composition-final
  python3 projects/sunset/media/launch-v17/pipeline.py check --output .publication/sunset-launch-v17/check-final.json
  python3 projects/sunset/media/launch-v17/pipeline.py proof --end 7 --output .publication/sunset-launch-v17/opening-new.mp4
  python3 projects/sunset/media/launch-v17/pipeline.py render --output .publication/sunset-launch-v17/sunset-v17.mp4

Requires Python 3.11+ without optimization (-O/-OO or PYTHONOPTIMIZE).
Reuses the ignored V16 HyperFrames 0.9.16/GSAP 3.15.1 toolchain.
No installation, network service, login, or global settings changes. Existing
composition/output paths are refused; choose a new name for a later revision.
"""
import sys

if sys.flags.optimize:
    raise SystemExit('Verification requires assertions: run Python without -O/-OO or PYTHONOPTIMIZE.')
if sys.version_info < (3, 11):
    raise SystemExit('Python 3.11 or newer is required.')

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(__file__).resolve().parent
OUT = ROOT / '.publication/sunset-launch-v17'
TOOLCHAIN = ROOT / '.publication/sunset-launch-v16/toolchain'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def record(path):
    return {'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path), 'sha256': sha(path)}


def prepare(destination):
    assert not destination.exists(), f'Refusing to overwrite {destination}'
    inputs = [SOURCE / ('film.' + suffix) for suffix in ['html', 'css', 'js']]
    assets = {'creators.png': ROOT / '.publication/sunset-launch-v14/assets/creator-portrait.png',
              'workroom.png': ROOT / '.publication/sunset-launch-v14/assets/workroom.png',
              'hands.png': ROOT / '.publication/sunset-launch-v13/assets/creator-cutout.png',
              'unchecked.png': ROOT / '.publication/sunset-launch-v15/capture/unchecked.png',
              'checked.png': ROOT / '.publication/sunset-launch-v15/capture/checked.png',
              'geist.woff2': ROOT / 'projects/sunset/public/fonts/geist-latin-variable.woff2',
              'gsap.min.js': TOOLCHAIN / 'node_modules/gsap/dist/gsap.min.js',
              'score.wav': OUT / 'audio/mix.wav'}
    versions = {name: json.loads((TOOLCHAIN / f'node_modules/{name}/package.json').read_text())['version']
                for name in ['hyperframes', 'gsap']}
    assert versions == {'hyperframes': '0.9.16', 'gsap': '3.15.1'}, versions
    content = {path: path.read_bytes() for path in inputs}
    sources = [{'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(content[path]).hexdigest()} for path in inputs]
    provenance = {name: record(path) for name, path in assets.items()}
    qa = json.loads((OUT / 'audio/qa.json').read_text())
    assert provenance['score.wav']['sha256'] == qa['master_sha256'], 'Audio master differs from QA'
    html, css, js = (content[path].decode() for path in inputs)
    link, script = '<link rel="stylesheet" href="film.css">', '<script src="film.js"></script>'
    assert html.count(link) == html.count(script) == 1
    html = html.replace(link, '<style>\n' + css + '\n</style>')
    html = html.replace(script, '<script>\n' + js.replace('</script', '<\\/script') + '\n</script>')
    assert 'window.__timelines' in html and 'assets/gsap.min.js' in html
    (destination / 'assets').mkdir(parents=True)
    for name, path in assets.items():
        shutil.copyfile(path, destination / 'assets' / name)
    (destination / 'index.html').write_text(html)
    manifest = {'versions': versions, 'sources': sources, 'assets': provenance,
                'prepared': record(destination / 'index.html'), 'fps': 30, 'frames': 885, 'duration': 29.5,
                'wrapper': record(TOOLCHAIN / 'hyperframes.sh'),
                'package_lock': record(TOOLCHAIN / 'package-lock.json'),
                'capture': record(ROOT / '.publication/sunset-launch-v15/capture/capture-provenance.json'),
                'audio_qa': record(OUT / 'audio/qa.json')}
    (destination / 'source-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['prepare', 'check', 'proof', 'render'])
    parser.add_argument('--composition', type=Path, default=OUT / 'composition-final')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--end', type=float, default=7)
    args = parser.parse_args()
    composition = args.composition.resolve()
    if args.command == 'prepare':
        prepare(composition)
        return
    assert (composition / 'source-manifest.json').is_file(), 'Run prepare first'
    manifest = json.loads((composition / 'source-manifest.json').read_text())
    assert sha(composition / 'index.html') == manifest['prepared']['sha256'], 'Prepared composition changed'
    for key in ['wrapper', 'package_lock']:
        assert sha(ROOT / manifest[key]['path']) == manifest[key]['sha256'], key
    for name, version in {'hyperframes': '0.9.16', 'gsap': '3.15.1'}.items():
        assert json.loads((TOOLCHAIN / f'node_modules/{name}/package.json').read_text())['version'] == version
    for name, item in manifest['assets'].items():
        assert sha(composition / 'assets' / name) == item['sha256'], name
    assert args.output, '--output is required'
    output = args.output.resolve()
    log = output.with_suffix(output.suffix + '.log')
    assert not output.exists() and not log.exists(), f'Refusing to overwrite {output} or {log}'
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [str(TOOLCHAIN / 'hyperframes.sh')]
    if args.command == 'check':
        command += ['check', str(composition), '--json', '--samples', '15', '--at-transitions',
                    '--max-transition-samples', '60', '--snapshots', '--timeout', '90s']
        with output.open('x') as stdout, log.open('x') as stderr:
            subprocess.run(command, stdout=stdout, stderr=stderr, check=True, cwd=ROOT)
        assert json.loads(output.read_text())['ok'], output
    else:
        command += ['render', str(composition), '--fps', '30', '--quality',
                    'looks' if args.command == 'proof' else 'delivery', '--workers', '2', '--strict', '--output', str(output)]
        if args.command == 'proof':
            assert 0 < args.end <= 29.5
            command += ['--start', '0', '--end', str(args.end)]
        with log.open('x') as stream:
            subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, check=True, cwd=ROOT)
        assert output.stat().st_size > 0, output
    print(output)


if __name__ == '__main__':
    main()
