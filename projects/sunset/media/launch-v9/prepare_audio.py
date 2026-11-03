"""Build the approved 56-second, music-and-recorded-Foley-only SUNSET v9 mix.

Requires Python + numpy and FFmpeg. No narration, TTS/model imports, generated
music, or synthesized sound effects. Source media and outputs remain ignored.
"""
from pathlib import Path
import hashlib
import json
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(__file__).resolve().parent
OUT = ROOT / '.publication/sunset-launch-v9'
AUDIO = OUT / 'audio'
RATE = 48000
DURATION = 56.0
COUNT = round(RATE * DURATION)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ff(*args):
    return subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                           *map(str, args)], check=True, capture_output=True)


def decode(path, filters=None, start=None, duration=None):
    args = []
    if start is not None:
        args += ['-ss', str(start)]
    args += ['-i', str(path)]
    if duration is not None:
        args += ['-t', str(duration)]
    if filters:
        args += ['-af', filters]
    data = ff(*args, '-ar', RATE, '-ac', 2, '-f', 'f32le', '-').stdout
    return np.frombuffer(data, dtype='<f4').reshape(-1, 2).astype(np.float64)


def write(path, samples):
    samples = np.asarray(samples, dtype='<f4')
    assert np.isfinite(samples).all() and np.max(np.abs(samples)) < 1
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                    '-f', 'f32le', '-ar', str(RATE), '-ac', '2', '-i', '-',
                    '-c:a', 'pcm_s24le', str(path)], input=samples.tobytes(), check=True)


def measure(path, label):
    result = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(path),
                             '-af', 'loudnorm=I=-15:TP=-2.5:LRA=9:print_format=json',
                             '-f', 'null', '-'], check=True, capture_output=True, text=True)
    (AUDIO / f'{label}.log').write_text(result.stderr)
    return json.JSONDecoder().raw_decode(result.stderr[result.stderr.rfind('{'):])[0]


def main():
    cues = json.loads((SOURCE / 'sound-cues.json').read_text())
    assert cues['duration_seconds'] == DURATION and cues['voice'] is None
    AUDIO.mkdir(parents=True, exist_ok=True)
    for source in cues['sources']:
        path = ROOT / source['file']
        assert sha(path) == source['sha256'], f'Source hash mismatch: {path}'
    sources = {item['id']: item for item in cues['sources']}
    music = decode(ROOT / sources['music']['file'], cues['music_filter'], 16, DURATION)
    assert len(music) == COUNT
    time = np.arange(COUNT) / RATE
    knots = cues['music_gain_db']
    db = np.interp(time, [p[0] for p in knots], [p[1] for p in knots])
    # The licensed performance stays continuous: arrangement uses smooth gain,
    # stereo width and a restrained start, then opens with the resource.
    envelope = 10 ** (db / 20)
    envelope *= np.minimum(np.clip(time / .18, 0, 1), np.clip((DURATION - time) / 1.7, 0, 1))
    width = np.interp(time, [0, 6, 19.8, 21.5, 34.6, 35.2, 43.8, 44.3, 56],
                     [.62, .78, .85, 1, 1, .82, .82, 1, 1])
    mid = music.mean(axis=1)
    side = (music[:, 0] - music[:, 1]) / 2
    music = np.column_stack([mid + side * width, mid - side * width]) * envelope[:, None]
    sfx = np.zeros_like(music)
    measured_cues = []
    for cue in cues['effects']:
        source = sources[cue['source_id']]
        sample = decode(ROOT / source['file'], 'highpass=f=110,lowpass=f=11000')
        a, b = [round(value * RATE) for value in cue['source_crop_seconds']]
        sample = sample[a:b].copy()
        # Remove only short edge discontinuities; no pitch/time generation.
        edge = min(round(.005 * RATE), len(sample) // 3)
        sample[:edge] *= np.linspace(0, 1, edge)[:, None]
        sample[-edge:] *= np.linspace(1, 0, edge)[:, None]
        sample *= np.array(cue['stereo_channel_gains'])
        peak_index = int(np.argmax(np.max(np.abs(sample), axis=1)))
        start = round(cue['peak_seconds'] * RATE) - peak_index
        end = start + len(sample)
        assert 0 <= start < end <= COUNT
        # A short recording sits a few dB above the local bed. Limit individual
        # Foley peaks so a quiet UI never produces a startling effect.
        rms = lambda x: float(np.sqrt(np.mean(x * x)))
        target = rms(music[start:end]) * 10 ** (cue['above_local_music_rms_db'] / 20)
        gain = min(target / max(rms(sample), 1e-10),
                   10 ** (cue['max_peak_dbfs'] / 20) / np.max(np.abs(sample)))
        sample *= gain
        sfx[start:end] += sample
        measured_cues.append({**cue, 'start_seconds': start / RATE,
                              'end_seconds': end / RATE,
                              'measured_peak_seconds': (start + peak_index) / RATE,
                              'peak_dbfs_before_master': float(20 * np.log10(np.max(np.abs(sample)))),
                              'rms_above_local_music_db': float(20 * np.log10(rms(sample) / rms(music[start:end]))),
                              'gain': float(gain)})
    raw = music + sfx
    # Pre-master stems are useful for the later human recording/remix.
    write(AUDIO / 'music-arranged.wav', music)
    write(AUDIO / 'sfx.wav', sfx)
    write(AUDIO / 'mix-unmastered.wav', raw)
    first = measure(AUDIO / 'mix-unmastered.wav', 'master-first')
    master_filter = ('loudnorm=I=-15:TP=-2.5:LRA=9:linear=true'
                     f":measured_I={first['input_i']}:measured_TP={first['input_tp']}"
                     f":measured_LRA={first['input_lra']}:measured_thresh={first['input_thresh']}"
                     f":offset={first['target_offset']}")
    ff('-i', AUDIO / 'mix-unmastered.wav', '-af', master_filter,
       '-ar', RATE, '-ac', 2, '-t', DURATION, '-c:a', 'pcm_s24le', AUDIO / 'mix.wav')
    final = measure(AUDIO / 'mix.wav', 'master-verification')
    ff('-i', AUDIO / 'mix.wav', '-c:a', 'aac', '-b:a', '320k', AUDIO / 'aac-roundtrip-320k.m4a')
    aac = measure(AUDIO / 'aac-roundtrip-320k.m4a', 'aac-roundtrip-320k')
    pcm = decode(AUDIO / 'mix.wav')
    assert pcm.shape == (COUNT, 2)
    assert -16 <= float(final['input_i']) <= -14
    assert float(final['input_tp']) <= -1.5 and float(aac['input_tp']) <= -1.5
    assert np.isfinite(pcm).all() and np.max(np.abs(pcm)) < 1
    qa = {'duration_seconds': DURATION, 'sample_count_per_channel': COUNT,
          'sample_rate': RATE, 'channels': 2, 'codec': 'pcm_s24le',
          'integrated_lufs': float(final['input_i']), 'true_peak_dbtp': float(final['input_tp']),
          'loudness_range_lu': float(final['input_lra']),
          'aac_320k': {'integrated_lufs': float(aac['input_i']), 'true_peak_dbtp': float(aac['input_tp'])},
          'mix_sha256': sha(AUDIO / 'mix.wav'),
          'stems': {'music-arranged.wav': {'sha256': sha(AUDIO / 'music-arranged.wav'), 'stage': 'pre-master'},
                    'sfx.wav': {'sha256': sha(AUDIO / 'sfx.wav'), 'stage': 'pre-master'}},
          'voice_present': False, 'voice_generated': False, 'tts_or_voice_models_used': False,
          'procedural_music_or_effects': False, 'source_hashes_verified': True,
          'perceptual_listening_verified': False, 'effects': measured_cues,
          'master_filter': master_filter,
          'review_limit': 'Measured waveform/loudness/codec checks; no perceptual listening claim.'}
    (AUDIO / 'qa.json').write_text(json.dumps(qa, indent=2) + '\n')
    (AUDIO / 'music-provenance.json').write_text(json.dumps(sources['music'], indent=2) + '\n')
    (AUDIO / 'sound-cues-measured.json').write_text(json.dumps(measured_cues, indent=2) + '\n')
    print(json.dumps({key: qa[key] for key in ['duration_seconds', 'integrated_lufs', 'true_peak_dbtp',
                                              'loudness_range_lu', 'aac_320k', 'mix_sha256']}, indent=2))


if __name__ == '__main__':
    main()
