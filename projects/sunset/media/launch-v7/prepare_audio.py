#!/usr/bin/env python3
"""Remix the approved unchanged v6 narration with a new relaxed jazz recording.
Uses retained local inputs; never synthesizes speech or music.
"""
import hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[4]
SRC=Path(__file__).resolve().parent
OUT=ROOT/".publication/sunset-launch-v7"
DURATION,RATE=20.,48000
MUSIC_START=16.
MUSIC_SHA="9567e71a213b0026341b2c0ecd226950e7653abd235cf520fb9aee4247d74d96"
VOICE_SHA="debcf3fa3291eaecdbb02da58eea1037ed804b5fe3613d1e2d754efa5d18da5c"
VOICE_FILTER="highpass=f=75,equalizer=f=520:t=q:w=0.9:g=-1.6,equalizer=f=3000:t=q:w=0.8:g=1.0,deesser=i=0.12:m=0.25:f=0.5,acompressor=threshold=0.11:ratio=2:attack=16:release=120:makeup=1.2,loudnorm=I=-17:TP=-3:LRA=6,aresample=48000,apad=whole_len=960000,atrim=end_sample=960000"
MUSIC_FILTER="highpass=f=55,equalizer=f=2500:t=q:w=0.8:g=-3,lowpass=f=14000,loudnorm=I=-24:TP=-4:LRA=8"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ff(*args):subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",*map(str,args)],check=True)
def measure(path,name):
 r=subprocess.run(["ffmpeg","-hide_banner","-nostats","-i",str(path),"-af","loudnorm=I=-15:TP=-2:LRA=7:print_format=json","-f","null","-"],capture_output=True,text=True,check=True)
 (OUT/"audio"/(name+".log")).write_text(r.stderr)
 return json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind("{"):])[0]
def main():
 audio=OUT/"audio";audio.mkdir(parents=True,exist_ok=True)
 narration=OUT/"voice/narration.wav";assert sha(narration)==VOICE_SHA
 old=json.loads((ROOT/".publication/sunset-launch-v6/story-timing.json").read_text())
 phrases=old["phrases"];assert len(phrases)==9 and phrases[-1]["end"]==17.6645
 music=OUT/"audio-research/music/kevin-macleod-backbay-lounge.mp3";assert sha(music)==MUSIC_SHA
 ff("-i",narration,"-af",VOICE_FILTER,"-ar",RATE,"-ac",1,"-c:a","pcm_s24le",audio/"voice-enhanced.wav")
 ff("-ss",MUSIC_START,"-i",music,"-t",DURATION,"-af",MUSIC_FILTER,"-ar",RATE,"-ac",2,"-c:a","pcm_s24le",audio/"new-music-normalized.wav")
 voice,vr=sf.read(audio/"voice-enhanced.wav",dtype="float64")
 bed,br=sf.read(audio/"new-music-normalized.wav",dtype="float64",always_2d=True)
 count=round(DURATION*RATE);assert len(voice)==len(bed)==count and vr==br==RATE
 times=np.arange(count)/RATE;active=np.zeros(count,dtype=bool);duck=np.ones(count)
 for p in phrases:
  a,b=round(p["start"]*RATE),round(p["end"]*RATE);active[a:b]=True
  attack=np.clip((times-(p["start"]-.06))/.06,0,1)
  release=np.clip((p["end"]+.28-times)/.28,0,1)
  duck=np.minimum(duck,1-.32*np.minimum(attack,release))
 fade=np.minimum(np.clip(times/.09,0,1),np.clip((DURATION-times)/.60,0,1))
 bed*=(duck*fade)[:,None]
 vrms=float(np.sqrt(np.mean(voice[active]**2)));mrms=float(np.sqrt(np.mean(bed[active]**2)))
 gain=vrms/(mrms*10**(9/20));bed*=gain
 # Reduce only locally crowded phrases, with soft fades: speech remains clearly ahead.
 for p in phrases:
  a,b=round(p["start"]*RATE),round(p["end"]*RATE)
  v=float(np.sqrt(np.mean(voice[a:b]**2)));m=float(np.sqrt(np.mean(bed[a:b]**2)))
  db=20*math.log10(v/m)
  if db<8.5:
   reduction=10**((db-8.5)/20)
   attack=np.clip((times-(p["start"]-.05))/.05,0,1)
   release=np.clip((p["end"]+.12-times)/.12,0,1)
   bed*= (1-(1-reduction)*np.minimum(attack,release))[:,None]
 sf.write(audio/"music-ducked.wav",bed,RATE,subtype="PCM_24")
 raw=np.column_stack([voice,voice])+bed
 # Pure gain if required before mastering; no hard sample clipping.
 if np.max(np.abs(raw))>.97:raw*=.97/np.max(np.abs(raw))
 sf.write(audio/"mix-unmastered.wav",raw,RATE,subtype="PCM_24")
 first=measure(audio/"mix-unmastered.wav","master-first")
 filt=("loudnorm=I=-15:TP=-2:LRA=7:linear=true"+f":measured_I={first['input_i']}:measured_TP={first['input_tp']}:measured_LRA={first['input_lra']}:measured_thresh={first['input_thresh']}:offset={first['target_offset']}")
 ff("-i",audio/"mix-unmastered.wav","-af",filt,"-ar",RATE,"-ac",2,"-t",DURATION,"-c:a","pcm_s24le",audio/"mix.wav")
 final=measure(audio/"mix.wav","master-verification")
 assert -16<=float(final["input_i"])<=-14 and float(final["input_tp"])<=-1.5
 ff("-i",audio/"mix.wav","-c:a","aac","-b:a","320k",audio/"aac-roundtrip-320k.m4a")
 codec=measure(audio/"aac-roundtrip-320k.m4a","aac-roundtrip-320k")
 assert float(codec["input_tp"])<=-1.5
 separation=[]
 for p in phrases:
  a,b=round(p["start"]*RATE),round(p["end"]*RATE)
  db=20*math.log10(float(np.sqrt(np.mean(voice[a:b]**2)))/float(np.sqrt(np.mean(bed[a:b]**2))))
  assert db>=8.45,(p["index"],db)
  separation.append({"phrase":p["index"],"voice_above_music_rms_db":round(db,2)})
 newphrases=[]
 for p in phrases:
  source=OUT/"voice"/p["audio_file"];assert sha(source)==p["source_sha256"]
  newphrases.append({**p,"source_file":str(source.relative_to(ROOT)),"rendered_file":"voice/"+p["audio_file"]})
 clock={**old,"phrases":newphrases,"mix_sha256":sha(audio/"mix.wav"),"narration_sha256":VOICE_SHA,"voice":"Unchanged approved v6 am_puck narration; new EQ/de-essing/compression mix, no regeneration or timing/pitch alteration."}
 (OUT/"story-timing.json").write_text(json.dumps(clock,indent=2)+"\n")
 provenance={"title":"Backbay Lounge","artist":"Kevin MacLeod","album":"Teh Jazzes","isrc":"USUAN1700068","tempo_bpm":120,"page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1700068","primary_detail":"https://remote.incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1700068","download":"https://incompetech.com/music/royalty-free/mp3-royaltyfree/Backbay%20Lounge.mp3","file":music.name,"sha256":MUSIC_SHA,"bytes":music.stat().st_size,"license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/","artist_description":"Jazz; bright, grooving and relaxed; piano, guitar, drums and bass.","excerpt_start_seconds":MUSIC_START,"excerpt_end_seconds":MUSIC_START+DURATION,"excerpt_duration_seconds":DURATION,"selection_basis":"New recording fits the requested relaxed groove based on the primary artist metadata;120bpm and20s allow ten4/4bars. No perceptual listening claim.","attribution":"Backbay Lounge by Kevin MacLeod (incompetech.com), licensed under CC BY4.0.","changes_to_disclose":"Edited16–36s excerpt, EQ, fades and speech ducking.","attribution_required":True,"attribution_placement":"Accompanying post/video description plus CREDITS.md; no burned-in credit.","on_screen_credit_required":False,"processing":{"voice_filter":VOICE_FILTER,"music_filter":MUSIC_FILTER,"music_active_target_separation_db":9,"minimum_phrase_separation_db":8.5,"duck_depth":.32,"attack_seconds":.06,"release_seconds":.28,"fade_in_seconds":.09,"fade_out_seconds":.60,"overall_music_gain":gain,"master":filt},"reference_audio_used":False,"perceptual_listening_verified":False}
 (audio/"music-provenance.json").write_text(json.dumps(provenance,indent=2)+"\n")
 qa={"duration_seconds":DURATION,"sample_rate":RATE,"channels":2,"codec":"pcm_s24le","phrase_count":9,"voice_overlap":False,"voice_regenerated":False,"voice_timing_changed":False,"narration_sha256":VOICE_SHA,"last_voice_end":17.6645,"final_voice_tail_seconds":DURATION-17.6645,"integrated_lufs":float(final["input_i"]),"true_peak_dbtp":float(final["input_tp"]),"mix_sha256":sha(audio/"mix.wav"),"mix_bytes":(audio/"mix.wav").stat().st_size,"music_source_sha256":MUSIC_SHA,"voice_to_music_rms":separation,"codec_roundtrips":{"320k":{"integrated_lufs":float(codec["input_i"]),"true_peak_dbtp":float(codec["input_tp"]) }},"source_hashes_checked":True,"reference_audio_used":False,"procedural_music_or_effects":False,"perceptual_listening_verified":False,"scope":"Same approved voice and picture clock; clearer voice processing and new more-audible relaxed jazz bed, attribution outside video."}
 (audio/"qa.json").write_text(json.dumps(qa,indent=2)+"\n")
 print(json.dumps(qa,indent=2),flush=True)
if __name__=="__main__":main()
