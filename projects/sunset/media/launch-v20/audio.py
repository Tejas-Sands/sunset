#!/usr/bin/env python3
"""Remix retained licensed music and recorded Foley for the 34-second finish.

No model, network, generated voice or synthesized sound. Reuses the existing
decode/write/loudness helpers and original source recordings; no new dependency.
"""
import importlib.util
import json
from pathlib import Path

import numpy as np

from finish import ROOT, OUT, sha

RATE, DURATION = 48000, 34
COUNT = RATE*DURATION


def film_time(original):
    return original + (.7 if original>=14.3 else 0) + (.6 if original>=16.3 else 0) + (1.5 if original>=19.1 else 0) + (.7 if original>=26 else 0)


def main():
    destination = OUT/'audio'
    assert not destination.exists(), f'Refusing to overwrite {destination}'
    destination.mkdir(parents=True)
    helper_path = ROOT/'projects/sunset/media/launch-v10/prepare_audio.py'
    spec = importlib.util.spec_from_file_location('sunset_audio', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    helper.AUDIO = destination
    original = json.loads((ROOT/'.publication/sunset-launch-v16/audio/cue-manifest.json').read_text())
    sources = {item['id']: item for item in original['sources']}
    for source in sources.values():
        assert sha(ROOT/source['file'])==source['sha256'], source['file']
    music = helper.decode(ROOT/sources['music']['file'], original['music_filter'], 32.18, DURATION)
    assert music.shape==(COUNT,2)
    clock = np.arange(COUNT)/RATE
    knots = [[0,0],[13.4,.3],[17.4,.3],[17.7,-2],[21.7,-2],[21.9,.5],
             [25.5,.5],[25.8,-4.3],[29.2,-4.3],[29.5,.8],[34,.8]]
    gain = 10**(np.interp(clock,*np.array(knots).T)/20)
    gain *= np.minimum(np.clip(clock/.065,0,1), np.clip((DURATION-clock)/1.25,0,1))
    music *= gain[:,None]
    effects = np.zeros_like(music)
    cues = []
    for cue in original['effects']:
        if cue['id']=='real-checklist-input':
            continue
        source = sources[cue['source_id']]
        a,b = cue['source_crop_seconds']
        sample = helper.decode(ROOT/source['file'], 'highpass=f=135,lowpass=f=11200',a,b-a)
        edge = min(round(.004*RATE),len(sample)//4)
        sample[:edge] *= np.linspace(0,1,edge)[:,None]
        sample[-edge:] *= np.linspace(1,0,edge)[:,None]
        sample *= np.array(cue['stereo_channel_gains'])
        peak = int(np.argmax(np.max(np.abs(sample),axis=1)))
        at = film_time(cue['peak_seconds'])
        start = round(at*RATE)-peak
        end = start+len(sample)
        assert 0<=start<end<=COUNT
        sample *= 10**(cue['peak_dbfs_before_master']/20)/np.max(np.abs(sample))
        effects[start:end] += sample
        cues.append({'id':cue['id'],'source_id':cue['source_id'],'peak_seconds':at,
                     'measured_peak_seconds':(start+peak)/RATE,'original_peak_seconds':cue['peak_seconds'],
                     'source_crop_seconds':[a,b],'editorial_recording':True})
    for name,samples in [('music-arranged',music),('sfx',effects),('mix-unmastered',music+effects)]:
        helper.write(destination/(name+'.wav'),samples)
    first = helper.measure(destination/'mix-unmastered.wav','first')
    master_filter = ('loudnorm=I=-15:TP=-2.5:LRA=9:linear=true'
        f":measured_I={first['input_i']}:measured_TP={first['input_tp']}"
        f":measured_LRA={first['input_lra']}:measured_thresh={first['input_thresh']}:offset={first['target_offset']}")
    helper.ff('-i',destination/'mix-unmastered.wav','-af',master_filter,'-ar',RATE,'-ac',2,
              '-t',DURATION,'-c:a','pcm_s24le',destination/'mix.wav')
    measured = helper.measure(destination/'mix.wav','master')
    assert -15.5<=float(measured['input_i'])<=-14.5 and float(measured['input_tp'])<=-2
    assert len(cues)==29 and all(abs(c['peak_seconds']-c['measured_peak_seconds'])<=1/RATE for c in cues)
    report = {'duration':DURATION,'sample_rate':RATE,'channels':2,'voice':None,'music_excerpt_seconds':[32.18,66.18],
        'music_is_continuous':True,'sources':list(sources.values()),'music_gain_knots':knots,'cues':cues,
        'removed_cue':'real-checklist-input; no reader input is presented in this cut',
        'master_sha256':sha(destination/'mix.wav'),'measured':measured,
        'source_helpers':{'path':str(helper_path.relative_to(ROOT)),'sha256':sha(helper_path)},
        'scope':'Editorial recorded Foley, not browser/chain sound. Signal checks, not perceptual listening.'}
    (destination/'qa.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'ok':True,'duration':DURATION,'cues':len(cues),'lufs':measured['input_i'],'true_peak':measured['input_tp']}))


if __name__=='__main__':
    main()
