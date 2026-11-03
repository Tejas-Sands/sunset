"""Prepare only the explicitly passed v10 native browser-owner screenshot take.
No recapture, glob discovery, UI reconstruction, time compression or chain actions.
"""
from pathlib import Path
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[4];SRC=Path(__file__).resolve().parent;OUT=ROOT/'.publication/sunset-launch-v10';FOOT=OUT/'footage'
CAPTURE=FOOT/'capture-provenance.json';EXPECTED='ea94abea8db8e1cec01335d9da42399a99e34a7b1ef24c37965226c5109350f0'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 assert sha(CAPTURE)==EXPECTED,'Only the root-passed native owner capture is authorized'
 data=json.loads(CAPTURE.read_text());assert data['status']=='actual_download_offline_procedure_and_retained_check_passed';assert data['dimensions']==[4320,2700] and data['dpr']==3
 assert data['guide_onchain_release_claimed'] is False and data['underlying_git_steps_executed'] is False and data['chain_mutations']==0
 for key in ('blank_offline_before_file','offline_before','checked_result','offline_after'):
  state=data[key];assert state['onLine'] is False and state['resources']==0
 for identity in (data['download'],data['source_pack'],data['retained_after_reload']):assert sha(ROOT/identity['path'])==identity['sha256']
 recordings={r['name']:r for r in data['recordings']};assert set(recordings)=={'actual-download','actual-offline-procedure'}
 available=[]
 for name,recording in recordings.items():
  for sample in recording['samples']:
   path=FOOT/name/sample['file'];assert sha(path)==sample['sha256'];im=Image.open(path);assert im.size==(4320,2700);im.verify();available.append({'path':str(path.relative_to(ROOT)),'sha256':sample['sha256'],'capture_time':sample['at']})
 download=recordings['actual-download'];offline=recordings['actual-offline-procedure'];assert len(download['samples'])==3 and len(offline['samples'])==8
 dstart=28-download['samples'][0]['at'];ostart=29.5-offline['samples'][0]['at']
 dcrop=[990,865,1840,1095]
 crops=[[270,80,4050,1180],[1170,980,3966,1180],[1230,1580,2300,1790],[1230,1580,2300,1790],[1230,1595,2790,1760],[1230,1595,2790,1760],[1125,2175,2130,2355],[1120,1595,2790,2335]]
 def frames(recording,offset,crops):
  return [{'path':str((FOOT/recording['name']/sample['file']).relative_to(ROOT)),'file':sample['file'],'time':sample['at'],'film_time':offset+sample['at'],'sha256':sample['sha256'],'crop':crop} for sample,crop in zip(recording['samples'],crops)]
 dfs=frames(download,dstart,[dcrop]*3);ofs=frames(offline,ostart,crops)
 segments=[{'id':'actual-app-download','start':28.,'end':29.5,'context':'app_download','network_offline_verified':False,'source_dimensions':[4320,2700],'crop':dcrop,'playbackstart':dstart,'sourceframes':[f for f in dfs if f['film_time']<29.5],'max_editorial_scale':2.2}, {'id':'actual-offline-procedure','start':29.5,'end':36.,'context':'guide_file','network_offline_verified':True,'source_dimensions':[4320,2700],'crop':crops[0],'playbackstart':ostart,'sourceframes':ofs,'max_editorial_scale':2.2}]
 events=[]
 for event in data['events']:
  if 'seconds' not in event or event.get('recording') not in recordings:continue
  offset=dstart if event['recording']=='actual-download' else ostart;events.append({**event,'film_time':offset+event['seconds']})
 manifest={'schema':2,'film_start':28.,'film_end':36.,'delivery_frames':240,'fps':30,'source_dimensions':[4320,2700],'source_capture_provenance':str(CAPTURE.relative_to(ROOT)),'source_capture_provenance_sha256':sha(CAPTURE),'source_sampling':data['capture_method'],'timestamp_meaning':'Raw elapsed capture-completion clocks retained without acceleration. Fixed offsets map the passed take into film time. Native browser screenshots were interleaved with inputs, not continuous full-rate capture.','selection_rule':'Select segment start<=t<end then last sourceframe.film_time<=t; hold endpoints. Each sample crop is an editorial crop of genuine pixels. No invented UI/cursor/interpolation.','segments':segments,'events':events,'available_passed_samples':available,'unused_passed_samples':[f for f in dfs if f['film_time']>=29.5],'failed_takes_used':False,'download_identity':data['download'],'source_pack':data['source_pack'],'offline_before':data['offline_before'],'offline_after':data['offline_after'],'retained_after_reload':data['retained_after_reload'],'editorial_magnification':{'allowed':True,'max_scale':2.2,'resampling':'LANCZOS','native_detail_added':False},'retained_endpoint':{'original_film_playback_time':35.9666666667,'output_window':[36,40],'meaning':'Final genuine post-reload state held; actual sample time remains distinct from output time.'}}
 path=FOOT/'compositor.json';path.write_text(json.dumps(manifest,indent=2)+'\n')
 timeline_path=SRC/'timeline.json';timeline=json.loads(timeline_path.read_text());timeline['actual_manifest_sha256']=sha(path);timeline['capture_provenance_sha256']=sha(CAPTURE);timeline['actual_sampling']=data['capture_method'];timeline['actual_download_sha256']=data['download']['sha256'];timeline_path.write_text(json.dumps(timeline,indent=2)+'\n')
 print(json.dumps({'manifest':str(path),'sha256':sha(path),'passed_pngs':len(available),'mapped_source_frames':sum(len(s['sourceframes']) for s in segments),'unused_passed_download_samples':1,'download_event_window':[dstart+10.238886277,dstart+10.29711729],'offline_first_sample':ofs[0]['film_time'],'offline_last_sample':ofs[-1]['film_time']},indent=2))
if __name__=='__main__':main()
