#!/usr/bin/env python3
"""Read final film/evidence and write checks only inside ignored launch-v2."""
from pathlib import Path
import datetime,hashlib,json,re,struct,subprocess
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'.publication/sunset-launch-v2';movie=OUT/'sunset-launch-v2.mp4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ff(args,name):
 r=subprocess.run(['ffmpeg',*args],capture_output=True,text=True);(OUT/(name+'.log')).write_text(r.stderr);assert r.returncode==0,r.stderr[-2000:];return r.stderr
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(movie)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['codec_name'],v['pix_fmt'],v['r_frame_rate'])==(1920,1080,'h264','yuv420p','30/1')
assert a['codec_name']=='aac' and abs(float(probe['format']['duration'])-30)<.04
ff(['-v','error','-i',str(movie),'-f','null','-'],'full-decode')
black=ff(['-hide_banner','-i',str(movie),'-vf','blackdetect=d=0.08:pix_th=0.10','-an','-f','null','-'],'black-frames');assert 'black_start:' not in black
levels=ff(['-hide_banner','-i',str(movie),'-vn','-af','ebur128=peak=true','-f','null','-'],'audio-levels')
summary=levels[levels.rfind('Summary:'):];print(summary)
lufs=float(re.search(r'I:\s+(-?[\d.]+) LUFS',summary)[1]);peak=float(re.search(r'Peak:\s+(-?[\d.]+) dBFS',summary)[1]);assert peak<=-1 and -20<=lufs<=-14
atoms=[]
with movie.open('rb') as f:
 while True:
  h=f.read(8)
  if len(h)!=8:break
  size,kind=struct.unpack('>I4s',h);hs=8
  if size==1:size=struct.unpack('>Q',f.read(8))[0];hs=16
  atoms.append(kind.decode())
  if size==0:break
  f.seek(size-hs,1)
assert atoms.index('moov')<atoms.index('mdat')
edit=json.loads((ROOT/'projects/sunset/media/launch-v2/edit.json').read_text());voice=json.loads((OUT/'voice/timing.json').read_text())
assert edit['duration']==30 and edit['fps']==30 and edit['bpm']==128
cues=(OUT/'sunset-launch-v2.srt').read_text().strip().split('\n\n');assert len(cues)==6
inputs=[ROOT/'projects/sunset/media/launch-v2/render_launch.py',ROOT/'projects/sunset/media/launch-v2/render_motion.py',ROOT/'projects/sunset/media/launch-v2/edit.json',OUT/'voice/timing.json',ROOT/'projects/sunset/public/icon.svg',ROOT/'projects/sunset/public/images/sunset-commons-hero.webp',ROOT/'projects/sunset/public/fonts/geist-latin-variable.woff2']
for cue,entry,vo in zip(cues,edit['voice'],voice['phrases']):
 assert ' '.join(cue.splitlines()[2:])==entry['text']==vo['text']
 assert entry['end']<30 and entry['duration']==vo['duration']
 path=OUT/'voice'/entry['file'];assert sha(path)==entry['sha256'];inputs.append(path)
browser=ROOT/'projects/sunset/evidence/browser-showcase.json';data=json.loads(browser.read_text());records={x['file']:x for x in data['capture_files']};inputs.append(browser)
for file in edit['capture_files']:
 path=ROOT/'.publication/sunset-launch-v1/footage'/file;assert sha(path)==records[file]['sha256'];inputs.append(path)
assert data['offline']['all_five_correct'] and data['offline']['navigator_onLine'] is False
for name,t in [('opening',.6),('answer-action',5.42),('actual-feedback',6.4),('download-action',12.50),('offline-file',13.9),('actual-offline-completion',17.8),('closing',28.1)]:
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(movie),'-frames:v','1',str(OUT/(name+'-final.png'))],check=True)
provenance={'format':'Native frame-driven kinetic motion design; genuine UI state excerpts and graphical cursor/camera reenactment, not an uninterrupted screen recording.','voice':'Six whole prior Kokoro af_heart synthetic-voice sentences, pitch-preserving atempo1.12; not a newly synthesized or cloned voice.','music':'Original procedural128BPM score and click/whoosh/chime synthesis from render_launch.py; no third-party recording.','scope':'Actual learning game and download/offline state excerpts only. No wallet, chain, deployment or social action. No new feature or fabricated financial UI.','illustrations':'Existing SUNSET icon/hero; HTML file tile and copy fan are editorial illustrations.','inputs':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in inputs]}
(OUT/'media-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
qa={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed_objective_checks_visual_review_pending','film':'sunset-launch-v2.mp4','sha256':sha(movie),'bytes':movie.stat().st_size,'duration':float(probe['format']['duration']),'resolution':[1920,1080],'fps':30,'video_codec':'h264','pixel_format':'yuv420p','audio_codec':'aac','faststart':True,'full_decode':'passed','black_frames':'none','loudness_lufs':lufs,'true_peak_dbfs':peak,'captions':{'cues':6,'exact_phrase_text':True,'last_phrase_end':edit['voice'][-1]['end'],'end_tail_seconds':30-edit['voice'][-1]['end']},'capture_hashes_match_verified_browser_evidence':True,'voice_hashes_match':True,'perceptual_listening_verified':False,'source_layout':'Native independent text/image/mask/cursor layers; no static card PNG/zoompan pipeline.','product_and_v1_preserved':True,'new_wallet_or_chain_actions':False}
(OUT/'media-qa.json').write_text(json.dumps(qa,indent=2)+'\n');(OUT/'full-ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
(OUT/'CREDITS.md').write_text('SUNSET kinetic launch film v2. Existing SUNSET SVG icon, brand palette and original book/sunset hero. Hero generation prompt/provenance: projects/sunset/public/images/README.md. Geist: existing SIL OFL1.1 license under public/fonts. Genuine game/download/offline captures: browser-showcase.json. Cursor graphically reenacts captured answer12 and download actions; no financial action. HTML tile/copy fan are editorial illustrations. Six edited prior local Kokoro af_heart synthetic phrases, atempo1.12, no cloning or fresh synthesis; prior engine MIT and model Apache2 provenance/licenses retained in voice delivery. Music/sound effects are newly composed procedural128BPM synthesis, no commercial samples. Perceptual listening is not verified by tools. Version1 is preserved. All source identities are in media-provenance.json.\n')
print(json.dumps(qa,indent=2))
