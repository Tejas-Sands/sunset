#!/usr/bin/env python3
"""Objective checks for the rendered launch artifact; visual review remains separate."""
import json,subprocess,sys,wave,hashlib,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'.publication/sunset-launch-v3'
def main():
 video=OUT/'sunset-launch-v3.mp4'
 assert video.exists(), 'Render missing: sunset-launch-v3.mp4'
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)]))
 vs=next(s for s in probe['streams'] if s['codec_type']=='video')
 au=next(s for s in probe['streams'] if s['codec_type']=='audio')
 assert (vs['width'],vs['height'],vs['r_frame_rate'],vs['pix_fmt'],vs['codec_name'])==(1920,1080,'30/1','yuv420p','h264')
 assert int(vs['nb_frames'])==900 and abs(float(probe['format']['duration'])-30)<.05
 assert au['codec_name']=='aac' and int(au['sample_rate'])==48000
 edit=json.loads((ROOT/'projects/sunset/media/launch-v3/edit.json').read_text())
 # Inspect actual top-level MP4 atoms, rather than assuming the encoder flag worked.
 raw_video=video.read_bytes();offset=0;atoms=[]
 while offset+8<=len(raw_video):
  size,kind=struct.unpack_from('>I4s',raw_video,offset)
  if size==1:size=struct.unpack_from('>Q',raw_video,offset+8)[0]
  if size==0:size=len(raw_video)-offset
  assert size>=8
  atoms.append((kind.decode('ascii'),offset));offset+=size
 atom_names=[a[0] for a in atoms]
 assert atom_names.index('moov')<atom_names.index('mdat')
 captures=json.loads((ROOT/'projects/sunset/evidence/browser-showcase.json').read_text())['capture_files']
 actual_captures={}
 for name in ['06-hosted-verified-game.png','07-hosted-game-feedback.png','11-offline-game-complete.png']:
  expected=next(c for c in captures if c['file']==name)
  digest=hashlib.sha256((ROOT/'.publication/sunset-launch-v1/footage'/name).read_bytes()).hexdigest()
  assert digest==expected['sha256'],name
  actual_captures[name]=digest
 source_timing=json.loads((ROOT/'.publication/sunset-launch-v1/voice/timing.json').read_text())
 prev=0
 for cue in edit['voice']:
  original=source_timing['sentences'][cue['source_sentence_index']-1]
  assert cue['text']==original['text']
  assert cue['start']>=prev and cue['end']<=30
  with wave.open(str(OUT/cue['rendered_file'])) as f:
   duration=f.getnframes()/f.getframerate()
  assert abs(duration-cue['duration'])<.001
  source=ROOT/cue['source_file']
  assert hashlib.sha256(source.read_bytes()).hexdigest()==cue['source_sha256']
  assert cue['text'] in (OUT/'sunset-launch-v3.srt').read_text()
  prev=cue['end']
 tail=30-edit['voice'][-1]['end'];assert tail>=.4
 result=subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
 (OUT/'decode.log').write_text(result.stderr)
 assert result.returncode==0 and not result.stderr.strip(),result.stderr
 black=subprocess.run(['ffmpeg','-hide_banner','-i',str(video),'-vf','blackdetect=d=.20:pix_th=.02:pic_th=.98','-an','-f','null','-'],capture_output=True,text=True,check=True)
 (OUT/'black-frames.log').write_text(black.stderr)
 assert 'black_start:' not in black.stderr
 levels=subprocess.run(['ffmpeg','-hide_banner','-i',str(video),'-af','loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 (OUT/'audio-levels.log').write_text(levels.stderr)
 raw=levels.stderr[levels.stderr.rfind('{'):]
 loud,_=json.JSONDecoder().raw_decode(raw)
 assert -18<=float(loud['input_i'])<=-14
 assert float(loud['input_tp'])<=-.8
 qa={'checked':True,'duration':probe['format']['duration'],'frames':int(vs['nb_frames']),'dimensions':[vs['width'],vs['height']],'fps':vs['r_frame_rate'],'decodeErrors':0,'faststartMoovBeforeMdat':True,'topLevelAtoms':atoms,'blackIntervals':0,'blackdetectThresholds':{'duration':.20,'pixel':.02,'picture':.98},'lastVoiceEnds':edit['voice'][-1]['end'],'finalVoiceTailSeconds':tail,'genuineCaptureHashes':actual_captures,'voiceCues':len(edit['voice']),'voiceSourceHashesVerified':True,'voiceOverlap':False,'captionTextExact':True,'integratedLufs':float(loud['input_i']),'truePeakDbtp':float(loud['input_tp']),'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'bytes':video.stat().st_size,'perceptualListeningVerified':False,'note':'Editorial animation and genuine UI excerpts; objective checks do not prove subjective visual/audio quality.'}
 (OUT/'media-qa.json').write_text(json.dumps(qa,indent=2)+'\n')
 (OUT/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
 print(json.dumps(qa,indent=2))
if __name__=='__main__':main()
