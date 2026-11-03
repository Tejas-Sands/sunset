"""Prepare the SUNSET launch film's local narration and measured cue clock.

The isolated runtime/model/voice assets and rendered output stay in .publication.
This program does not generate music; the soundtrack uses a licensed recording.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import time
import math
import subprocess

import numpy as np
import onnxruntime as ort
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(__file__).resolve().parent
OUT = ROOT / ".publication/sunset-launch-v8"
CACHE = ROOT / ".publication/sunset-launch-v5/tts-cache"
VOICE_RATE = 24000


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(seconds):
    ms = round(seconds * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def captions(sentence):
    if len(sentence) <= 49:
        return sentence
    words = sentence.split()
    pairs = [(" ".join(words[:i]), " ".join(words[i:])) for i in range(1, len(words))]
    return "\n".join(min(pairs, key=lambda pair: abs(len(pair[0]) - len(pair[1]))))


def narrate():
    script = json.loads((SOURCE / "narration-script.json").read_text())
    voice_dir = OUT / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)
    model = CACHE / "kokoro-v1.0.fp16.onnx"
    voices_file = CACHE / "voices-v1.0.bin"
    assert sha256(model) == "f3a290d384fbb27966d462905c71a46cef9e5fd00516b40df32a0b4afe77ac96"
    assert sha256(voices_file) == "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d"
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    options.inter_op_num_threads = 1
    options.log_severity_level = 3
    session = ort.InferenceSession(str(model), sess_options=options, providers=["CPUExecutionProvider"])
    engine = Kokoro.from_session(session, str(voices_file))
    lead_samples = round(.20 * VOICE_RATE)
    gap_samples = round(.12 * VOICE_RATE)
    tail_samples = round(1.20 * VOICE_RATE)
    parts = [np.zeros(lead_samples, dtype=np.float32)]
    offset = lead_samples
    timing = []
    for line in script["sentences"]:
        started = time.monotonic()
        samples, rate = engine.create(
            line["tts_text"], voice=script["voice"], speed=script["speed"],
            lang=script["language"], sentence_pause=.12, clause_pause=.10,
        )
        samples = np.asarray(samples, dtype=np.float32)
        assert rate == VOICE_RATE and samples.size > VOICE_RATE // 10 and np.isfinite(samples).all()
        filename = f"sentence-{line['index']:02d}.wav"
        sf.write(voice_dir / filename, samples, VOICE_RATE, subtype="PCM_24")
        end = offset + len(samples)
        timing.append({
            **line, "start_sample": offset, "end_sample": end,
            "start": offset / VOICE_RATE, "end": end / VOICE_RATE, "duration": len(samples) / VOICE_RATE,
            "audio_file": filename,
        })
        parts.append(samples)
        pause = tail_samples if line is script["sentences"][-1] else round(line.get("gap_after_seconds", gap_samples / VOICE_RATE) * VOICE_RATE)
        parts.append(np.zeros(pause, dtype=np.float32))
        offset = end + pause
        print(f"{line['index']:02d}: {len(samples)/VOICE_RATE:.3f}s ({time.monotonic()-started:.2f}s compute) {line['text']}", flush=True)
    audio = np.concatenate(parts)
    peak = float(np.max(np.abs(audio)))
    assert peak > .01
    audio *= 10 ** (-2 / 20) / peak
    audio_path = voice_dir / "narration.wav"
    sf.write(audio_path, audio, VOICE_RATE, subtype="PCM_24")
    metadata = {
        "voice": script["voice"], "voice_type": script["voice_type"], "speed": script["speed"],
        "sample_rate": VOICE_RATE, "channels": 1, "duration": len(audio) / VOICE_RATE,
        "word_count": len(" ".join(s["text"] for s in script["sentences"]).split()),
        "lead_silence": lead_samples / VOICE_RATE, "sentence_gap": gap_samples / VOICE_RATE,
        "tail_silence": tail_samples / VOICE_RATE, "sentences": timing,
        "caption_alignment": "Exact per-sentence synthesis sample boundaries; not word-level forced alignment",
        "proof_pause": "Optional complete-sentence gap_after_seconds in the locked script, no speech stretched or cut.",
        "script_sha256": sha256(SOURCE / "narration-script.json"),
        "model_sha256": sha256(model), "voices_sha256": sha256(voices_file),
        "retained_model_cache": str(CACHE.relative_to(ROOT)),
        "narration_sha256": sha256(audio_path), "providers": session.get_providers(),
        "engine": {name: importlib.metadata.version(name) for name in
                   ["kokoro-onnx", "onnxruntime", "numpy", "phonemizer", "espeakng-loader", "soundfile"]},
        "peak_after_normalization": float(np.max(np.abs(audio))),
        "rms": float(np.sqrt(np.mean(np.square(audio)))),
        "perceptual_listening": "Not performed by this tool; objective timing/peak checks only",
    }
    (voice_dir / "timing.json").write_text(json.dumps(metadata, indent=2) + "\n")
    srt = "\n\n".join(
        f"{line['index']}\n{stamp(line['start'])} --> {stamp(line['end'])}\n{captions(line['text'])}"
        for line in timing
    ) + "\n"
    (voice_dir / "captions.srt").write_text(srt)
    print(json.dumps({key: metadata[key] for key in ["voice","speed","duration","word_count","narration_sha256"]},indent=2),flush=True)



SRC=SOURCE
SCRIPT=json.loads((SOURCE/"narration-script.json").read_text())
DURATION,RATE=float(SCRIPT.get("film_duration",24.0)),48000
COUNT=round(DURATION*RATE)
MUSIC_START=16.
MUSIC_SHA="9567e71a213b0026341b2c0ecd226950e7653abd235cf520fb9aee4247d74d96"

VOICE_FILTER=f"highpass=f=75,equalizer=f=520:t=q:w=0.9:g=-1.6,equalizer=f=3000:t=q:w=0.8:g=1.0,deesser=i=0.12:m=0.25:f=0.5,acompressor=threshold=0.11:ratio=2:attack=16:release=120:makeup=1.2,loudnorm=I=-17:TP=-3:LRA=6,aresample=48000,apad=whole_len={COUNT},atrim=end_sample={COUNT}"
MUSIC_FILTER="highpass=f=55,equalizer=f=2500:t=q:w=0.8:g=-3,lowpass=f=14000,loudnorm=I=-24:TP=-4:LRA=8"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ff(*args):subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",*map(str,args)],check=True)
def measure(path,name):
 r=subprocess.run(["ffmpeg","-hide_banner","-nostats","-i",str(path),"-af","loudnorm=I=-15:TP=-2:LRA=7:print_format=json","-f","null","-"],capture_output=True,text=True,check=True)
 (OUT/"audio"/(name+".log")).write_text(r.stderr)
 return json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind("{"):])[0]
def mix():
 audio=OUT/"audio";audio.mkdir(parents=True,exist_ok=True)
 narration=OUT/"voice/narration.wav";VOICE_SHA=sha(narration)
 old=json.loads((OUT/"voice/timing.json").read_text());assert old["narration_sha256"]==VOICE_SHA
 phrases=old["sentences"];assert len(phrases)==len(SCRIPT["sentences"]) and phrases[-1]["end"]<=DURATION-1.5
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
  source=OUT/"voice"/p["audio_file"]
  newphrases.append({**p,"source_file":str(source.relative_to(ROOT)),"source_sha256":sha(source),"rendered_file":"voice/"+p["audio_file"],"rendered_sha256":sha(source),"sample_rate":VOICE_RATE})
 clock={"schema":1,"duration":DURATION,"sample_rate":RATE,"voice":"Fresh am_puck natural1.0 synthesis; new problem/NEAR/action narration, same approved voice identity and v7 processing; no pitch/time alteration.","phrases":newphrases,"mix_sha256":sha(audio/"mix.wav"),"narration_sha256":VOICE_SHA,"voice_overlap":False,"voice_end_seconds":phrases[-1]["end"],"final_voice_tail_seconds":DURATION-phrases[-1]["end"]}
 (OUT/"story-timing.json").write_text(json.dumps(clock,indent=2)+"\n")
 (OUT/"sunset-launch-v8.srt").write_text((OUT/"voice/captions.srt").read_text())
 old["phrases"]=newphrases;old["film_duration"]=DURATION
 (OUT/"voice/timing.json").write_text(json.dumps(old,indent=2)+"\n")
 provenance={"title":"Backbay Lounge","artist":"Kevin MacLeod","album":"Teh Jazzes","isrc":"USUAN1700068","tempo_bpm":120,"page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1700068","primary_detail":"https://remote.incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1700068","download":"https://incompetech.com/music/royalty-free/mp3-royaltyfree/Backbay%20Lounge.mp3","file":music.name,"sha256":MUSIC_SHA,"bytes":music.stat().st_size,"license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/","artist_description":"Jazz; bright, grooving and relaxed; piano, guitar, drums and bass.","excerpt_start_seconds":MUSIC_START,"excerpt_end_seconds":MUSIC_START+DURATION,"excerpt_duration_seconds":DURATION,"selection_basis":"Retained approved relaxed120bpm recording; bar-aligned excerpt starts16s, extended to the measured picture/voice runtime. No perceptual listening claim.","attribution":"Backbay Lounge by Kevin MacLeod (incompetech.com), licensed under CC BY4.0.","changes_to_disclose":f"Edited{MUSIC_START:g}–{MUSIC_START+DURATION:g}s excerpt, EQ, fades and speech ducking.","attribution_required":True,"attribution_placement":"Accompanying post/video description plus CREDITS.md; no burned-in credit.","on_screen_credit_required":False,"processing":{"voice_filter":VOICE_FILTER,"music_filter":MUSIC_FILTER,"music_active_target_separation_db":9,"minimum_phrase_separation_db":8.5,"duck_depth":.32,"attack_seconds":.06,"release_seconds":.28,"fade_in_seconds":.09,"fade_out_seconds":.60,"overall_music_gain":gain,"master":filt},"reference_audio_used":False,"perceptual_listening_verified":False}
 (audio/"music-provenance.json").write_text(json.dumps(provenance,indent=2)+"\n")
 qa={"duration_seconds":DURATION,"sample_rate":RATE,"channels":2,"codec":"pcm_s24le","phrase_count":len(phrases),"voice_overlap":False,"voice_regenerated":True,"voice_timing_changed":True,"narration_sha256":VOICE_SHA,"last_voice_end":phrases[-1]["end"],"final_voice_tail_seconds":DURATION-phrases[-1]["end"],"integrated_lufs":float(final["input_i"]),"true_peak_dbtp":float(final["input_tp"]),"mix_sha256":sha(audio/"mix.wav"),"mix_bytes":(audio/"mix.wav").stat().st_size,"music_source_sha256":MUSIC_SHA,"voice_to_music_rms":separation,"codec_roundtrips":{"320k":{"integrated_lufs":float(codec["input_i"]),"true_peak_dbtp":float(codec["input_tp"]) }},"source_hashes_checked":True,"reference_audio_used":False,"procedural_music_or_effects":False,"perceptual_listening_verified":False,"scope":"Fresh problem/NEAR/action narration in approved am_puck voice; v7 voice processing and retained relaxed jazz bed, genuine-action proof pause, attribution outside video."}
 (audio/"qa.json").write_text(json.dumps(qa,indent=2)+"\n")
 print(json.dumps(qa,indent=2),flush=True)
if __name__=="__main__":
 parser=argparse.ArgumentParser(description=__doc__)
 mode=parser.add_mutually_exclusive_group();mode.add_argument("--voice-only",action="store_true");mode.add_argument("--mix-only",action="store_true")
 args=parser.parse_args()
 if not args.mix_only:narrate()
 if not args.voice_only:mix()
