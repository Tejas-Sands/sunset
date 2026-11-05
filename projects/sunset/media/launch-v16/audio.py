"""Build the 29.5-second V16 licensed-score/recorded-Foley-only soundtrack.

Run from any directory with Python, NumPy and FFmpeg. Source recordings, stems,
waveform analysis and outputs remain ignored. No voice, model, API or synthesis.
"""
from pathlib import Path
import hashlib
import importlib.util
import json

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / '.publication/sunset-launch-v16/audio'
RATE, DURATION, MUSIC_START = 48000, 29.5, 32.18
COUNT = round(RATE * DURATION)


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
        'excerpt_start_seconds': MUSIC_START,
        'excerpt_end_seconds': MUSIC_START + DURATION,
        'changes': 'One continuous 32.18–61.68s excerpt, EQ, smooth gain and stereo-width arrangement, fades, mixed recorded Foley and mastering.',
    }}
    for source in json.loads((ROOT / '.publication/sunset-launch-v9/audio-research/foley-provenance.json').read_text()):
        if source['id'] in {'page-turn-1', 'page-turn-2', 'mouse-clicks'}:
            sources[source['id']] = source
    for source in sources.values():
        assert sha(ROOT / source['file']) == source['sha256'], source['file']

    clock = np.arange(COUNT) / RATE
    music_filter = 'highpass=f=48,lowpass=f=15500,equalizer=f=2800:t=q:w=0.8:g=-0.5,loudnorm=I=-18:TP=-4:LRA=9'
    music = audio.decode(ROOT / sources['music']['file'], music_filter, MUSIC_START, DURATION)
    assert music.shape == (COUNT, 2)
    # Keep the groove continuous. The UI has a mild dip; the only substantial
    # internal breath belongs to the one minimal passage, 23–26 seconds.
    gain_knots = [[0, 0], [1.8, 0], [4.8, .3], [7, .3], [12, .3],
                  [15.9, .3], [16.4, -1.7], [18.9, -1.7], [19.1, .5],
                  [22.7, .5], [23.0, -4.3], [25.7, -4.3], [26, .8],
                  [27.9, .8], [29.5, .8]]
    gain = 10 ** (np.interp(clock, *np.array(gain_knots).T) / 20)
    gain *= np.minimum(np.clip(clock / .065, 0, 1), np.clip((DURATION - clock) / .95, 0, 1))
    width = np.interp(clock, [0, 1.8, 7, 16.2, 16.4, 19.1, 22.7, 23, 25.7, 26, DURATION],
                      [.86, 1, 1, 1, .86, 1, 1, .68, .68, 1, 1])
    mid = music.mean(axis=1)
    side = (music[:, 0] - music[:, 1]) / 2
    music = np.column_stack([mid + side * width, mid - side * width]) * gain[:, None]
    effects = np.zeros_like(music)
    cues = []

    def add(label, source_id, when, crop, peak_dbfs, pan, cause):
        a, b = crop
        sample = audio.decode(ROOT / sources[source_id]['file'], 'highpass=f=135,lowpass=f=11200', a, b-a)
        edge = min(round(.004 * RATE), len(sample) // 4)
        sample[:edge] *= np.linspace(0, 1, edge)[:, None]
        sample[-edge:] *= np.linspace(1, 0, edge)[:, None]
        sample *= np.array(pan)
        peak = int(np.argmax(np.max(np.abs(sample), axis=1)))
        start = round(when * RATE) - peak
        end = start + len(sample)
        assert 0 <= start < end <= COUNT
        sample *= 10 ** (peak_dbfs / 20) / np.max(np.abs(sample))
        effects[start:end] += sample
        local_rms = float(np.sqrt(np.mean(music[start:end] ** 2)))
        cues.append({'id': label, 'source_id': source_id, 'peak_seconds': when,
                     'measured_peak_seconds': (start + peak) / RATE,
                     'start_seconds': start / RATE, 'end_seconds': end / RATE,
                     'source_crop_seconds': crop, 'stereo_channel_gains': pan,
                     'peak_dbfs_before_master': peak_dbfs,
                     'rms_above_local_music_db': float(20 * np.log10(np.sqrt(np.mean(sample ** 2)) / local_rms)),
                     'cause': cause, 'added_practical_recording': True})

    paper = [
        ('hook-paper-punch', .20, 'page-turn-2', [.66, .91], -15.5, [1, .9], 'Sunset punches into the giant cut-paper letter.'),
        ('letter-aperture', 1.00, 'page-turn-1', [.02, .24], -18, [.9, 1], 'Paper letter foreground crosses the lens.'),
        ('lesson-world', 1.80, 'page-turn-2', [.58, 1.04], -16.5, [1, 1], 'Pull through the paper aperture into the lesson world.'),
        ('lesson-to-kit', 2.80, 'page-turn-1', [.02, .32], -18, [1, .8], 'Lesson marks become the workshop-kit diagram.'),
        ('kit-to-guide', 3.80, 'page-turn-2', [.66, .92], -18, [.8, 1], 'Diagram line becomes ink on the guide.'),
        ('maker-ribbon', 4.99, 'page-turn-1', [.02, .46], -16.5, [1, .9], 'Ink ribbon reveals the maker portrait.'),
        ('ideas-field', 5.80, 'page-turn-2', [.65, .92], -19, [.8, 1], 'Sideways camera travel reveals further ideas.'),
        ('edition-forward', 6.50, 'page-turn-1', [.14, .30], -18, [1, 1], 'Prepared edition breaks forward from the idea field.'),
        ('ticket-left', 7.40, 'page-turn-1', [.14, .30], -17, [1, .72], 'First sponsorship ticket seats in the capped strip.'),
        ('ticket-right', 8.20, 'page-turn-2', [.69, .88], -18, [.72, 1], 'Second sponsorship ticket seats from another depth.'),
        ('ticket-perforation', 9.20, 'page-turn-2', [.55, 1.00], -16.5, [1, .9], 'Camera follows the ticket through its perforation.'),
        ('deposit-seats', 9.80, 'page-turn-1', [.14, .30], -18, [.9, 1], 'Deposit seats inside the printed custody sleeve.'),
        ('binding-to-key', 11.48, 'page-turn-2', [.66, 1.04], -18, [1, .9], 'Sleeve binding transforms into the committed-key shape.'),
        ('matching-key', 12.00, 'page-turn-1', [.02, .40], -16.5, [.9, 1], 'Timely matching key clears the committed release condition.'),
        ('public-page', 12.60, 'page-turn-2', [.58, 1.04], -18, [1, .9], 'Released public page opens in the material passage.'),
        ('claimable-slip', 13.40, 'page-turn-1', [.14, .30], -19, [.9, 1], 'Claimable creator credit slip becomes available; payment is not yet claimed.'),
        ('reader-entry', 16.40, 'page-turn-2', [.60, 1.04], -20, [.9, .9], 'Physical square opens into genuine downloaded-reader pixels.'),
        ('authored-return', 19.10, 'page-turn-1', [.02, .46], -16.5, [1, .9], 'Clear cut leaves the real reader and returns to authored ink.'),
        ('fresh-page', 19.75, 'page-turn-2', [.55, 1.04], -18, [.9, 1], 'Paid maker starts a fresh illustrated page.'),
        ('new-world-entry', 20.60, 'page-turn-1', [.02, .46], -18, [1, .8], 'Camera passes through the page drawing into a new useful-work world.'),
        ('new-world-depth', 21.55, 'page-turn-2', [.66, .92], -19, [.8, 1], 'Foreground paper exposes another depth in the new world.'),
        ('last-world-discovery', 22.35, 'page-turn-1', [.14, .30], -20, [1, .9], 'Final material discovery before the minimal contraction.'),
        ('minimal-window', 23.00, 'page-turn-2', [.66, .92], -21, [.9, .9], 'New page contracts into the single centered moving window.'),
        ('sunset-expansion', 26.00, 'page-turn-1', [.02, .46], -18, [1, .9], 'Point expands into the closing sunset horizon.'),
        ('mark-finishes', 27.25, 'page-turn-2', [.66, .92], -20, [.9, 1], 'Paper edges and ink finish the original SUNSET mark.'),
    ]
    for label, when, source_id, crop, peak, pan, cause in paper:
        add(label, source_id, when, crop, peak, pan, cause)
    # Dry recorded contact ticks are editorial additions, including the actual
    # input marker. They are not captured browser, wallet or blockchain audio.
    ticks = [
        ('funding-cap-contact', 8.88, [.02, .11], -19, 'Sponsorship strip reaches its illustrated fixed cap.'),
        ('custody-fixed-stop', 10.60, [.36, .46], -20, 'Deposits contact the sleeve fixed stop.'),
        ('deliberate-withdrawal', 14.30, [.36, .46], -20, 'Creator deliberately requests the separate illustrated withdrawal.'),
        ('withdrawal-confirmed', 15.45, [.70, .82], -21, 'Successful illustrated withdrawal confirmation precedes paid state.'),
        ('real-checklist-input', 17.600145381, [.02, .11], -23, 'Actual recorded reader input at source 1.200145381s, film origin 16.4s; editorial tick, not captured browser audio.'),
    ]
    for label, when, crop, peak, cause in ticks:
        add(label, 'mouse-clicks', when, crop, peak, [1, 1], cause)

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
    assert pcm.shape == (COUNT, 2) and np.isfinite(pcm).all() and np.max(np.abs(pcm)) < 1
    assert -15.5 <= float(master['input_i']) <= -14.5
    assert -15.5 <= float(encoded['input_i']) <= -14.5
    assert float(master['input_tp']) <= -2 and float(encoded['input_tp']) <= -2
    assert abs(next(c for c in cues if c['id'] == 'real-checklist-input')['measured_peak_seconds'] - 17.600145381) <= 1 / RATE

    # Signal evidence is deliberately named an onset estimate, not a listened
    # beat grid. Ten-millisecond high-band energy rises guide the excerpt start.
    band = audio.decode(ROOT / sources['music']['file'], 'highpass=f=850,lowpass=f=11000', MUSIC_START, DURATION)
    window = 480
    energy = np.sqrt(np.mean(band[:len(band)//window*window].reshape(-1, window, 2) ** 2, axis=(1, 2)))
    flux = np.maximum(0, np.diff(energy, prepend=0))
    candidates = np.where((flux[1:-1] > flux[:-2]) & (flux[1:-1] >= flux[2:]))[0] + 1
    peaks = []
    for index in sorted(candidates, key=lambda i: flux[i], reverse=True):
        if all(abs(index - other) > 18 for other in peaks):
            peaks.append(index)
        if len(peaks) == 40:
            break
    onsets = [{'film_seconds': round(int(i) * .01, 4),
               'source_seconds': round(MUSIC_START + int(i) * .01, 4),
               'positive_energy_change': float(flux[i])} for i in sorted(peaks)]
    (OUT / 'source-onsets.json').write_text(json.dumps({
        'method': '10ms RMS; 850–11000Hz band; positive first difference; local maxima spaced >180ms; top 40.',
        'musical_beat_or_perceptual_sync_claim': False, 'onsets': onsets}, indent=2) + '\n')

    manifest = {'duration_seconds': DURATION, 'voice': None, 'sources': list(sources.values()),
                'music_filter': music_filter, 'music_gain_db': gain_knots,
                'master_filter': master_filter, 'effects': sorted(cues, key=lambda c: c['peak_seconds']),
                'shared_helper': str(helper.relative_to(ROOT)), 'shared_helper_sha256': sha(helper),
                'real_reader_source_origin_seconds': 16.4, 'real_reader_source_interval_seconds': [0, 2.7],
                'real_input_film_interval_seconds': [17.600145381, 17.624610837],
                'real_checked_state_film_seconds': 17.873660363,
                'browser_capture': '.publication/sunset-launch-v15/capture/capture-provenance.json',
                'editing_note': 'Added practical recordings; no captured browser/chain/wallet sound, synthesized effects, generated score or voice. No reload is claimed in the 2.7s reader insert.',
                'selection_basis': 'Pinned official artist description: upbeat electro-jazz/off-kilter groove. Continuous excerpt aligned with measured source energy onsets; no perceptual listening claim.',
                'v15_comparison': {'v15_duration_seconds': 40, 'v15_cue_count': 15,
                                   'v16_duration_seconds': DURATION, 'v16_cue_count': len(cues),
                                   'claim': 'Greater causal recorded-Foley placement density; this count does not establish subjective kinetic quality.'}}
    (OUT / 'cue-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (OUT / 'source-provenance.json').write_text(json.dumps(list(sources.values()), indent=2) + '\n')
    bins = [[start, min(start + 1, DURATION)] for start in np.arange(0, DURATION, 1)]
    rms = [{'start_seconds': float(a), 'end_seconds': float(b),
            'rms_dbfs': round(float(20*np.log10(max(np.sqrt(np.mean(pcm[round(a*RATE):round(b*RATE)]**2)), 1e-12))), 3)}
           for a, b in bins]
    sections = {}
    for name, a, b in [('hook', .1, 1.8), ('main', 1.8, 16.4), ('reader', 16.4, 19.1),
                       ('new-world', 19.1, 23), ('minimal', 23, 26), ('closing', 26, 28.5)]:
        samples = pcm[round(a*RATE):round(b*RATE)]
        sections[name] = {'start_seconds': a, 'end_seconds': b,
                          'rms_dbfs': float(20*np.log10(np.sqrt(np.mean(samples**2))))}
    report = {'duration_seconds': DURATION, 'sample_count_per_channel': COUNT,
              'sample_rate': RATE, 'channels': 2, 'codec': 'pcm_s24le',
              'master_sha256': sha(OUT / 'mix.wav'), 'integrated_lufs': float(master['input_i']),
              'true_peak_dbtp': float(master['input_tp']), 'loudness_range_lu': float(master['input_lra']),
              'sample_peak_dbfs': float(20*np.log10(np.max(np.abs(pcm)))),
              'one_second_rms_dbfs': rms, 'section_rms_dbfs': sections,
              'aac_320k': {'integrated_lufs': float(encoded['input_i']), 'true_peak_dbtp': float(encoded['input_tp'])},
              'stems': {name: {'sha256': sha(OUT/name), 'stage': 'pre-master'} for name in ['music-arranged.wav', 'sfx.wav']},
              'voice_present': False, 'tts_or_voice_models_used': False,
              'recorded_foley_only': True, 'source_hashes_verified': True,
              'perceptual_listening_verified': False, 'cue_count': len(cues),
              'cue_manifest_sha256': sha(OUT / 'cue-manifest.json'),
              'review_limit': 'Measured source identity, exact cue alignment, waveform, loudness and codec checks; no human listening or subjective approval claim.'}
    (OUT / 'qa.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ['duration_seconds', 'integrated_lufs', 'true_peak_dbtp',
                                                 'aac_320k', 'cue_count', 'master_sha256']}, indent=2))


if __name__ == '__main__':
    main()
