#!/usr/bin/env python3
"""Mix chosen synthetic voice, licensed continuous music and recorded Foley."""
import importlib.util
import json
from pathlib import Path
import subprocess

import numpy as np

from produce import ROOT,OUT,SOURCE,sha,timeline

RATE=48000


def main():
    tl,mapping=timeline();duration=tl['duration'];count=round(duration*RATE)
    destination=OUT/'audio';assert not destination.exists();destination.mkdir(parents=True)
    spec=importlib.util.spec_from_file_location('helpers',SOURCE.parent/'launch-v10/prepare_audio.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);helper.AUDIO=destination
    phrases=[p for p in tl['phases'] if 'take' in p]
    voice=np.zeros((count,2),dtype=np.float64)
    for p in phrases:
        path=OUT/p['take'];assert sha(path)==p['take_sha256']
        samples=helper.decode(path);start=round(p['voice_start']*RATE);end=start+len(samples)
        assert end<=round(p['end']*RATE) and end<=count
        voice[start:end]+=samples
    helper.write(destination/'narration-unmastered.wav',voice)
    helper.ff('-i',destination/'narration-unmastered.wav','-af',
        f'highpass=f=70,acompressor=threshold=0.18:ratio=2:attack=5:release=80,loudnorm=I=-18:TP=-3:LRA=8,aresample={RATE},apad=whole_len={count},atrim=end_sample={count},asetpts=PTS-STARTPTS',
        '-ar',RATE,'-ac',2,'-c:a','pcm_s24le',destination/'narration.wav')
    voice=helper.decode(destination/'narration.wav');assert voice.shape==(count,2)
    original=json.loads((ROOT/'.publication/sunset-launch-v16/audio/cue-manifest.json').read_text())
    sources={s['id']:s for s in original['sources']}
    for source in sources.values():assert sha(ROOT/source['file'])==source['sha256']
    music=helper.decode(ROOT/sources['music']['file'],'highpass=f=48,lowpass=f=15500,loudnorm=I=-20:TP=-4:LRA=9',32.18,duration)
    assert music.shape==(count,2)
    clock=np.arange(count)/RATE;duck=np.full(count,.8)
    for p in phrases:
        envelope=np.interp(clock,[p['voice_start']-.2,p['voice_start'],p['voice_end'],p['voice_end']+.4],[.8,.2,.2,.8])
        duck=np.minimum(duck,envelope)
    music*=duck[:,None]
    music*=np.minimum(np.clip(clock/.07,0,1),np.clip((duration-clock)/1.0,0,1))[:,None]
    effects=np.zeros_like(music);cues=[]
    phase_by_id={p['id']:p for p in tl['phases']}
    def place(label,source_id,when,crop=(.02,.28),peak_db=-24):
        a,b=crop;samples=helper.decode(ROOT/sources[source_id]['file'],'highpass=f=180,lowpass=f=11000',a,b-a)
        edge=min(round(.005*RATE),len(samples)//4)
        samples[:edge]*=np.linspace(0,1,edge)[:,None];samples[-edge:]*=np.linspace(1,0,edge)[:,None]
        peak=int(np.argmax(np.max(np.abs(samples),axis=1)));start=round(when*RATE)-peak
        assert 0<=start<start+len(samples)<=count
        samples*=10**(peak_db/20)/max(float(np.max(np.abs(samples))),1e-8)
        effects[start:start+len(samples)]+=samples
        cues.append({'id':label,'source':source_id,'peak_seconds':when,'source_crop_seconds':crop,'recorded_editorial_effect':True})
    for cue in original['effects']:
        if cue['id'] not in ['hook-paper-punch','ticket-left','ticket-right','funding-cap-contact','ticket-perforation',
                             'deposit-seats','custody-fixed-stop','binding-to-key','matching-key','public-page',
                             'claimable-slip','deliberate-withdrawal','withdrawal-confirmed','sunset-expansion','mark-finishes']:continue
        frame=round(cue['peak_seconds']*30)
        candidates=[r['frame'] for r in mapping if r['source']=='v19' and r['source_frame']==frame]
        if not candidates:continue
        place(cue['id'],cue['source_id'],candidates[0]/30,cue['source_crop_seconds'],-24 if cue['source_id']!='mouse-clicks' else -26)
    for name in ['why','kit','refund','use','proof','next','payoff']:
        p=phase_by_id[name]
        place(name+'-paper-entry','page-turn-2',p['start']+.40,(.66,.92),-24)
        if name in ['kit','use','next']:place(name+'-paper-discovery','page-turn-1',p['start']+min(1.8,(p['end']-p['start'])/2),(.02,.28),-25)
    for name,samples in [('music-arranged',music),('sfx',effects),('mix-unmastered',voice+music+effects)]:helper.write(destination/(name+'.wav'),samples)
    first=helper.measure(destination/'mix-unmastered.wav','first')
    master_filter=('loudnorm=I=-15:TP=-2.5:LRA=9:linear=true'
        f":measured_I={first['input_i']}:measured_TP={first['input_tp']}:measured_LRA={first['input_lra']}"
        f":measured_thresh={first['input_thresh']}:offset={first['target_offset']}")
    helper.ff('-i',destination/'mix-unmastered.wav','-af',master_filter+f',aresample={RATE},apad=whole_len={count},atrim=end_sample={count},asetpts=PTS-STARTPTS','-ar',RATE,'-ac',2,'-c:a','pcm_s24le',destination/'mix.wav')
    measured=helper.measure(destination/'mix.wav','master')
    assert -15.7<=float(measured['input_i'])<=-14.3 and float(measured['input_tp'])<=-2
    helper.ff('-i',destination/'mix.wav','-c:a','aac','-b:a','256k',OUT/'browser/assets/audio.m4a')
    def stamp(seconds):
        ms=round(seconds*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    (OUT/'narration.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(p["voice_start"])} --> {stamp(p["voice_end"])}\n{p["spoken"]}' for i,p in enumerate(phrases))+'\n')
    ratios=[]
    for p in phrases:
        a,b=round(p['voice_start']*RATE),round(p['voice_end']*RATE)
        ratio=float(20*np.log10(np.sqrt(np.mean(voice[a:b]**2))/max(np.sqrt(np.mean(music[a:b]**2)),1e-9)))
        ratios.append({'phase':p['id'],'voice_above_music_rms_db':ratio});assert ratio>8,(p['id'],ratio)
    report={'duration':duration,'sample_count':count,'voice':'af_bella','synthetic':True,'sources':list(sources.values()),
        'music_excerpt_seconds':[32.18,32.18+duration],'continuous_music':True,'voice_phrases':phrases,'voice_music_ratios':ratios,
        'cues':cues,'master_sha256':sha(destination/'mix.wav'),'narration_sha256':sha(destination/'narration.wav'),
        'measured':measured,'scope':'Local generic synthetic speech, licensed music and editorial recorded Foley; no perceptual-listening claim.'}
    (destination/'qa.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'ok':True,'duration':duration,'voice':'af_bella','cues':len(cues),'lufs':measured['input_i'],'true_peak':measured['input_tp'],'min_voice_music_db':min(r['voice_above_music_rms_db'] for r in ratios)}))


if __name__=='__main__':main()
