"""Arrange the 34-second launch: licensed performance and recorded Foley only.

The eight-second proof and its exact soundtrack stay independently reproducible.
This uses the existing FFmpeg helpers; all recordings and renders stay ignored.
"""
from pathlib import Path
import hashlib
import importlib.util
import json

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
SRC = Path(__file__).resolve().parent
OUT = ROOT / '.publication/sunset-launch-v11/audio'
RATE, DURATION = 48000, 34


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    helper = ROOT / 'projects/sunset/media/launch-v10/prepare_audio.py'
    spec = importlib.util.spec_from_file_location('sunset_full_audio', helper)
    audio = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audio)
    audio.AUDIO = OUT
    proof = json.loads((SRC / 'sound-cues-proof.json').read_text())
    sources = {s['id']: s.copy() for s in proof['sources']}
    sources['music'].update(
        excerpt_start_seconds=16, excerpt_end_seconds=50,
        changes='Continuous 34-second excerpt, EQ, smooth gain and stereo-width arrangement, fades and mastering.')
    for source in sources.values():
        assert sha(ROOT / source['file']) == source['sha256']

    count = RATE * DURATION
    time = np.arange(count) / RATE
    music_filter = 'highpass=f=45,lowpass=f=15000,loudnorm=I=-20:TP=-4:LRA=8'
    music = audio.decode(ROOT / sources['music']['file'], music_filter, 16, DURATION)
    assert len(music) == count
    gain_knots = [[0, -2], [2.4, 0], [7, 1], [13, .5], [18.5, 0],
                  [19, -3.5], [23.7, -3.5], [24.2, 1.5], [30, 1], [34, 0]]
    gain = 10 ** (np.interp(time, *np.array(gain_knots).T) / 20)
    gain *= np.minimum(np.clip(time / .24, 0, 1), np.clip((DURATION - time) / 1.2, 0, 1))
    width = np.interp(time, [0, 2.4, 8, 19, 24, 27, 34], [.7, .85, 1, .8, .8, 1, 1])
    mid = music.mean(axis=1)
    side = (music[:, 0] - music[:, 1]) / 2
    music = np.column_stack([mid + side * width, mid - side * width]) * gain[:, None]
    effects = np.zeros_like(music)
    cues = []

    def add(label, source_id, when, pan, peak_dbfs, crop_seconds, filters):
        sample = audio.decode(ROOT / sources[source_id]['file'], filters)[:round(crop_seconds * RATE)].copy()
        edge = min(round(.003 * RATE), len(sample) // 4)
        sample[:edge] *= np.linspace(0, 1, edge)[:, None]
        sample[-edge:] *= np.linspace(1, 0, edge)[:, None]
        sample *= np.array(pan)
        peak = int(np.argmax(np.max(np.abs(sample), axis=1)))
        start = round(when * RATE) - peak
        end = start + len(sample)
        assert 0 <= start < end <= count
        sample *= 10 ** (peak_dbfs / 20) / np.max(np.abs(sample))
        effects[start:end] += sample
        cues.append({'id': label, 'source_id': source_id, 'peak_seconds': when,
                     'measured_peak_seconds': (start + peak) / RATE,
                     'start_seconds': start / RATE, 'end_seconds': end / RATE,
                     'stereo_channel_gains': pan, 'max_peak_dbfs_before_master': peak_dbfs,
                     'source_crop_seconds': [0, crop_seconds],
                     'added_recorded_foley': True})

    # Peaks coincide with actual authored contacts, not unrelated animated text.
    contacts = [
        ('seal-contact', .55, [1, 1], -10),
        ('community-left', 2.9, [1, .7], -10),
        ('community-right', 3.3, [.7, 1], -10),
        ('community-rear', 3.7, [.9, .9], -10),
        ('creator-lane-landing', 13.2, [1, .65], -11),
        ('refund-left-landing', 18.3, [1, .5], -17),
        ('refund-right-landing', 18.3, [.5, 1], -17),
        ('refund-rear-landing', 18.7, [.8, .8], -15),
        ('retained-copy-left', 26.7, [1, .7], -11),
        ('retained-copy-right', 27, [.7, 1], -11),
    ]
    for label, when, pan, peak in contacts:
        add(label, 'pillow-impact', when, pan, peak, .396, 'highpass=f=45,lowpass=f=7000')
    add('cover-clears', 'page-turn-1', 6.2, [1, 1], -17, .46,
        'highpass=f=100,lowpass=f=10000')

    for name, samples in [('music-arranged', music), ('sfx', effects),
                          ('mix-unmastered', music + effects)]:
        audio.write(OUT / (name + '.wav'), samples)
    first = audio.measure(OUT / 'mix-unmastered.wav', 'first')
    filt = ('loudnorm=I=-15:TP=-2.5:LRA=8:linear=true'
            f":measured_I={first['input_i']}:measured_TP={first['input_tp']}"
            f":measured_LRA={first['input_lra']}:measured_thresh={first['input_thresh']}"
            f":offset={first['target_offset']}")
    audio.ff('-i', OUT / 'mix-unmastered.wav', '-af', filt, '-ar', RATE, '-ac', 2,
             '-t', DURATION, '-c:a', 'pcm_s24le', OUT / 'mix.wav')
    master = audio.measure(OUT / 'mix.wav', 'master')
    audio.ff('-i', OUT / 'mix.wav', '-c:a', 'aac', '-b:a', '320k', OUT / 'roundtrip.m4a')
    encoded = audio.measure(OUT / 'roundtrip.m4a', 'encoded')
    pcm = audio.decode(OUT / 'mix.wav')
    assert pcm.shape == (count, 2) and np.isfinite(pcm).all() and np.max(np.abs(pcm)) < 1
    assert -16 <= float(master['input_i']) <= -14
    assert -16 <= float(encoded['input_i']) <= -14
    assert float(master['input_tp']) <= -1.5 and float(encoded['input_tp']) <= -1.5
    (SRC / 'sound-cues.json').write_text(json.dumps({
        'stage': 'full_launch', 'duration_seconds': DURATION, 'voice': None,
        'sources': list(sources.values()), 'music_filter': music_filter,
        'music_gain_db': gain_knots, 'effects': sorted(cues, key=lambda c: c['peak_seconds']),
        'master_filter': filt, 'shared_helper_sha256': sha(helper),
        'editing_note': 'Foley is added practical sound. No browser audio, synthesized effects or generated narration.'
    }, indent=2) + '\n')
    report = {'duration_seconds': DURATION, 'sample_count_per_channel': count,
              'sample_rate': RATE, 'channels': 2, 'codec': 'pcm_s24le',
              'master_sha256': sha(OUT / 'mix.wav'),
              'integrated_lufs': float(master['input_i']), 'true_peak_dbtp': float(master['input_tp']),
              'aac_320k': {'integrated_lufs': float(encoded['input_i']),
                           'true_peak_dbtp': float(encoded['input_tp'])},
              'stems': {name: {'sha256': sha(OUT / name), 'stage': 'pre-master'}
                        for name in ['music-arranged.wav', 'sfx.wav']},
              'voice_present': False, 'tts_or_voice_models_used': False,
              'recorded_foley_only': True, 'perceptual_listening_verified': False,
              'cue_count': len(cues)}
    (OUT / 'qa.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
