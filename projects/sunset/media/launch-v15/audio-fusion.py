"""40-second SUNSET fusion score: licensed instrumental and practical Foley.

Reuses the existing FFmpeg/NumPy helpers. All media and measured output stay
ignored; no narration, generated music, synthesized effects or browser audio.
"""
from pathlib import Path
import hashlib
import importlib.util
import json

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / '.publication/sunset-launch-v15/audio'
RATE, DURATION = 48000, 40


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    helper = ROOT / 'projects/sunset/media/launch-v10/prepare_audio.py'
    spec = importlib.util.spec_from_file_location('sunset_audio_helpers', helper)
    audio = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audio)
    audio.AUDIO = OUT
    music_record = json.loads((ROOT / '.publication/sunset-launch-v6/audio-research/music/provenance.json').read_text())['tracks'][0]
    sources = {'music': {
        **music_record, 'id': 'music',
        'file': '.publication/sunset-launch-v6/audio-research/music/scott-buckley-origami.mp3',
        'excerpt_start_seconds': 32, 'excerpt_end_seconds': 72,
        'changes': 'Continuous 32–72s excerpt, EQ, smooth gain and stereo-width arrangement, fades, mixed practical Foley and mastering.',
    }}
    for source in json.loads((ROOT / '.publication/sunset-launch-v9/audio-research/foley-provenance.json').read_text()):
        if source['id'] in {'page-turn-1', 'page-turn-2', 'mouse-clicks'}:
            sources[source['id']] = source
    for source in sources.values():
        assert sha(ROOT / source['file']) == source['sha256'], source['file']

    count = RATE * DURATION
    clock = np.arange(count) / RATE
    music_filter = 'highpass=f=48,lowpass=f=15000,equalizer=f=2800:t=q:w=0.8:g=-1,loudnorm=I=-18:TP=-4:LRA=9'
    music = audio.decode(ROOT / sources['music']['file'], music_filter, 32, DURATION)
    assert music.shape == (count, 2)
    # Keep one continuous performance; smoothly make room for the minimal rests.
    gain_knots = [[0, -1], [1.3, 0], [4.95, 0], [5.3, -3.0], [7.7, -3.0],
                  [8.1, .5], [11.2, .5], [11.6, -2.7], [13.9, -2.7],
                  [14.3, 0], [17.7, .5], [20.9, .5], [21.4, -1.0],
                  [25.1, -1], [25.7, -4.2], [31.1, -4.2],
                  [31.6, -.7], [35.3, -.7], [35.8, .3], [38.3, .3], [40, -2]]
    gain = 10 ** (np.interp(clock, *np.array(gain_knots).T) / 20)
    gain *= np.minimum(np.clip(clock / .18, 0, 1), np.clip((DURATION - clock) / 1.45, 0, 1))
    width = np.interp(clock, [0, 3, 5.2, 8, 11.5, 14.2, 25.4, 31.4, 35.6, 40],
                      [.78, 1, .8, 1, .82, 1, .78, .9, 1, 1])
    mid = music.mean(axis=1)
    side = (music[:, 0] - music[:, 1]) / 2
    music = np.column_stack([mid + side * width, mid - side * width]) * gain[:, None]
    effects = np.zeros_like(music)
    cues = []

    def add(label, source_id, when, crop, peak_dbfs, pan, cause):
        a, b = crop
        sample = audio.decode(ROOT / sources[source_id]['file'], 'highpass=f=130,lowpass=f=10500', a, b-a)
        edge = min(round(.004 * RATE), len(sample) // 4)
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
                     'source_crop_seconds': crop, 'stereo_channel_gains': pan,
                     'peak_dbfs_before_master': peak_dbfs, 'cause': cause,
                     'added_practical_recording': True})

    # Recorded paper movement supplies texture at actual collage/copy transitions.
    paper = [
        ('portrait-print', 1.25, 'page-turn-2', [.65, 1.07], -17, [1, .85], 'Portrait grid settles into the paper print composition.'),
        ('free-type-cut', 3.12, 'page-turn-1', [0, .22], -18, [.9, 1], 'Heavy FREE title enters.'),
        ('ticket-left', 8.36, 'page-turn-1', [0, .22], -18, [1, .7], 'First sponsorship ticket enters.'),
        ('ticket-right', 8.93, 'page-turn-2', [.65, .89], -19, [.7, 1], 'Second sponsorship ticket enters.'),
        ('ticket-cap', 9.55, 'page-turn-1', [0, .22], -19, [.9, .9], 'Sponsorship cap resolves.'),
        ('release-key', 14.55, 'page-turn-2', [.65, 1.07], -18, [.9, 1], 'Matching-key release moves into the claimable credit illustration.'),
        ('refund-alternative', 21.5, 'page-turn-2', [.65, 1.07], -18, [1, .85], 'Separate conditional pre-release refund alternative enters.'),
        ('refund-alternative-paper-accent', 23.32, 'page-turn-1', [0, .46], -19, [.85, 1], 'Editorial paper accent supports the held conditional-refund claimability composition.'),
        ('handbook-entry', 25.58, 'page-turn-2', [.65, 1.07], -21, [.9, .9], 'Transition into the real retained-file checklist.'),
        ('free-to-use-return', 31.58, 'page-turn-1', [0, .46], -20, [1, .9], 'Minimal FREE TO USE reading window enters.'),
        ('brand-landing', 35.72, 'page-turn-2', [.65, .89], -20, [.9, 1], 'Original SUNSET mark lands.'),
    ]
    for label, when, source_id, crop, peak, pan, cause in paper:
        add(label, source_id, when, crop, peak, pan, cause)
    # These dry ticks are editorial practical recordings, not wallet/browser audio.
    for label, when, peak, cause in [
        ('withdraw-action', 17.8, -20, 'Illustrated creator withdrawal action.'),
        ('withdrawal-confirmed', 18.7, -21, 'Illustrated successful withdrawal confirmation.'),
        ('creator-paid', 19.6, -20, 'Creator paid resolves after the withdrawal confirmation.'),
        ('real-checklist-input', 27.200145381, -23, 'Actual recorded offline-reader checkbox input, source1.200145381s at film26s.'),
    ]:
        add(label, 'mouse-clicks', when, [0, .13], peak, [1, 1], cause)

    for name, samples in [('music-arranged', music), ('sfx', effects), ('mix-unmastered', music + effects)]:
        audio.write(OUT / (name + '.wav'), samples)
    first = audio.measure(OUT / 'mix-unmastered.wav', 'first')
    master_filter = ('loudnorm=I=-15:TP=-2.5:LRA=9:linear=true'
                     f":measured_I={first['input_i']}:measured_TP={first['input_tp']}"
                     f":measured_LRA={first['input_lra']}:measured_thresh={first['input_thresh']}"
                     f":offset={first['target_offset']}")
    audio.ff('-i', OUT / 'mix-unmastered.wav', '-af', master_filter, '-ar', RATE,
             '-ac', 2, '-t', DURATION, '-c:a', 'pcm_s24le', OUT / 'mix.wav')
    master = audio.measure(OUT / 'mix.wav', 'master')
    audio.ff('-i', OUT / 'mix.wav', '-c:a', 'aac', '-b:a', '320k', OUT / 'roundtrip.m4a')
    encoded = audio.measure(OUT / 'roundtrip.m4a', 'encoded')
    pcm = audio.decode(OUT / 'mix.wav')
    assert pcm.shape == (count, 2) and np.isfinite(pcm).all() and np.max(np.abs(pcm)) < 1
    assert -16 <= float(master['input_i']) <= -14
    assert -16 <= float(encoded['input_i']) <= -14
    assert float(master['input_tp']) <= -1.5 and float(encoded['input_tp']) <= -1.5
    stem_names = ['music-arranged.wav', 'sfx.wav']
    manifest = {'duration_seconds': DURATION, 'voice': None, 'sources': list(sources.values()),
                'music_filter': music_filter, 'music_gain_db': gain_knots,
                'master_filter': master_filter, 'effects': sorted(cues, key=lambda c:c['peak_seconds']),
                'shared_helper': str(helper.relative_to(ROOT)), 'shared_helper_sha256': sha(helper),
                'browser_capture': '.publication/sunset-launch-v15/capture/capture-provenance.json',
                'editing_note': 'Added practical recordings; no recorded browser/chain/wallet audio, no synthesized effects, score generation or voice.',
                'selection_basis': 'Cached official artist description: upbeat electro-jazz/off-kilter groove; source signal profile. Ambient cached alternatives were less suited to the kinetic collage brief. Perceptual listening is not claimed.'}
    (OUT / 'cue-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    per_second_rms = [round(float(20*np.log10(max(np.sqrt(np.mean(pcm[i*RATE:(i+1)*RATE]**2)),1e-12))),3) for i in range(DURATION)]
    report = {'duration_seconds': DURATION, 'sample_count_per_channel': count,
              'sample_rate': RATE, 'channels': 2, 'codec': 'pcm_s24le',
              'master_sha256': sha(OUT / 'mix.wav'), 'integrated_lufs': float(master['input_i']),
              'true_peak_dbtp': float(master['input_tp']), 'loudness_range_lu': float(master['input_lra']),
              'sample_peak_dbfs': float(20*np.log10(np.max(np.abs(pcm)))),
              'one_second_rms_dbfs': per_second_rms,
              'aac_320k': {'integrated_lufs': float(encoded['input_i']), 'true_peak_dbtp': float(encoded['input_tp'])},
              'stems': {name: {'sha256': sha(OUT/name), 'stage': 'pre-master'} for name in stem_names},
              'voice_present': False, 'tts_or_voice_models_used': False,
              'recorded_foley_only': True, 'perceptual_listening_verified': False, 'cue_count': len(cues)}
    (OUT / 'qa.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
