"""Eight-second feel test: licensed instrumental and real pillow-contact Foley."""
from pathlib import Path
import hashlib, importlib.util, json
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
SRC = Path(__file__).resolve().parent
OUT = ROOT / '.publication/sunset-launch-v11/audio-proof'
RATE, DURATION = 48000, 8

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    shared = ROOT / 'projects/sunset/media/launch-v10/prepare_audio.py'
    spec = importlib.util.spec_from_file_location('sunset_audio_helpers', shared)
    audio = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audio)
    audio.AUDIO = OUT
    pillow = json.loads((ROOT / '.publication/sunset-launch-v11/audio-research/pillow-impact-provenance.json').read_text())
    previous = json.loads((ROOT / 'projects/sunset/media/launch-v10/sound-cues.json').read_text())
    music_source = next(s for s in previous['sources'] if s['id'] == 'music').copy()
    music_source.update(excerpt_start_seconds=16, excerpt_end_seconds=24,
                        changes='Eight-second proof excerpt, EQ, gain, fades and mastering.')
    page_source = next(s for s in previous['sources'] if s['id'] == 'page-turn-1').copy()
    sources = [music_source, pillow, page_source]
    for source in sources:
        assert sha(ROOT / source['file']) == source['sha256']
    count = RATE * DURATION
    time = np.arange(count) / RATE
    music = audio.decode(ROOT / music_source['file'],
                         'highpass=f=45,lowpass=f=15000,loudnorm=I=-20:TP=-4:LRA=8', 16, DURATION)
    assert len(music) == count
    music *= np.interp(time, [0,.3,2.4,5.3,7.6,8], [0,1,1.1,1.15,1.15,0])[:,None]
    effects = np.zeros_like(music)
    cues = []
    contacts = [('seal-contact',.55,[1,1]), ('community-left',2.9,[1,.7]),
                ('community-right',3.3,[.7,1]), ('community-rear',3.7,[.9,.9])]
    for label, when, pan in contacts:
        sample = audio.decode(ROOT / pillow['file'], 'highpass=f=45,lowpass=f=7000')[:round(.396*RATE)].copy()
        edge = min(144, len(sample)//4)
        sample[:edge] *= np.linspace(0,1,edge)[:,None]
        sample[-edge:] *= np.linspace(1,0,edge)[:,None]
        sample *= np.array(pan)
        peak = int(np.argmax(np.max(np.abs(sample),axis=1)))
        start = round(when*RATE) - peak
        assert start >= 0
        sample *= 10**(-10/20) / np.max(np.abs(sample))
        effects[start:start+len(sample)] += sample
        cues.append({'id':label, 'source_id':'pillow-impact', 'peak_seconds':when,
                     'actual_peak_seconds':(start+peak)/RATE, 'start_seconds':start/RATE,
                     'end_seconds':(start+len(sample))/RATE, 'added_recorded_foley':True})
    page = audio.decode(ROOT / page_source['file'], 'highpass=f=100,lowpass=f=10000')[:round(.46*RATE)].copy()
    peak = int(np.argmax(np.max(np.abs(page),axis=1)))
    start = round(6.2*RATE) - peak
    page *= 10**(-17/20) / np.max(np.abs(page))
    effects[start:start+len(page)] += page
    cues.append({'id':'cover-clears', 'source_id':'page-turn-1', 'peak_seconds':6.2,
                 'start_seconds':start/RATE, 'end_seconds':(start+len(page))/RATE})
    for name, samples in [('music-arranged',music), ('sfx',effects), ('mix-unmastered',music+effects)]:
        audio.write(OUT / (name+'.wav'), samples)
    first = audio.measure(OUT/'mix-unmastered.wav','first')
    filt = ('loudnorm=I=-15:TP=-2.5:LRA=8:linear=true'
            f":measured_I={first['input_i']}:measured_TP={first['input_tp']}"
            f":measured_LRA={first['input_lra']}:measured_thresh={first['input_thresh']}:offset={first['target_offset']}")
    audio.ff('-i',OUT/'mix-unmastered.wav','-af',filt,'-ar',RATE,'-ac',2,
             '-t',DURATION,'-c:a','pcm_s24le',OUT/'mix.wav')
    levels = audio.measure(OUT/'mix.wav','master')
    audio.ff('-i',OUT/'mix.wav','-c:a','aac','-b:a','320k',OUT/'roundtrip.m4a')
    encoded = audio.measure(OUT/'roundtrip.m4a','encoded')
    assert -16 <= float(encoded['input_i']) <= -14 and float(encoded['input_tp']) <= -1.5
    (SRC/'sound-cues-proof.json').write_text(json.dumps({'stage':'eight_second_motion_proof',
        'duration_seconds':8,'voice':None,'sources':sources,'effects':cues,
        'master_filter':filt,'shared_helper_sha256':sha(shared)},indent=2)+'\n')
    report = {'stage':'motion_proof_only','duration_seconds':8,'sample_rate':RATE,'channels':2,
        'master_sha256':sha(OUT/'mix.wav'),'integrated_lufs':float(levels['input_i']),
        'true_peak_dbtp':float(levels['input_tp']),'aac_integrated_lufs':float(encoded['input_i']),
        'aac_true_peak_dbtp':float(encoded['input_tp']),'voice_present':False,
        'recorded_foley_only':True,'perceptual_listening_verified':False,'cue_count':len(cues)}
    (OUT/'qa.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
