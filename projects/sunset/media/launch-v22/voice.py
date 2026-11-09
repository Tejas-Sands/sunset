#!/usr/bin/env python3
"""Local synthetic narration, using the retained licensed Kokoro environment.

Run with .publication/sunset-launch-v5/tts-cache/venv/bin/python.
No network, account, paid provider, cloning or imitation of a named person.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
import onnxruntime as ort
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'.publication/sunset-launch-v22'
CACHE=ROOT/'.publication/sunset-launch-v5/tts-cache'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def engine():
    records=json.loads((CACHE/'assets.json').read_text())
    for item in records:
        assert sha(CACHE/item['name'])==item['sha256'], item['name']
    options=ort.SessionOptions();options.intra_op_num_threads=4;options.inter_op_num_threads=1
    options.log_severity_level=3;options.enable_profiling=False
    session=ort.InferenceSession(str(CACHE/'kokoro-v1.0.fp16.onnx'),sess_options=options,providers=['CPUExecutionProvider'])
    return Kokoro.from_session(session,str(CACHE/'voices-v1.0.bin'))


def generate(voice,text,path,speed=.97):
    assert not path.exists(),f'Refusing to overwrite {path}'
    path.parent.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    samples,rate=voice[0].create(text,voice=voice[1],speed=speed,lang='en-gb' if voice[1].startswith('b') else 'en-us',
                               sentence_pause=.22,clause_pause=.12)
    samples=np.asarray(samples,dtype=np.float32)
    assert rate==24000 and samples.size>2400 and np.isfinite(samples).all()
    samples*=10**(-2/20)/max(float(np.max(np.abs(samples))),1e-8)
    sf.write(path,samples,rate,subtype='PCM_24')
    result={'voice':voice[1],'synthetic':True,'text':text,'speed':speed,'sample_rate':rate,
            'duration':len(samples)/rate,'sha256':sha(path),'compute_seconds':time.monotonic()-started}
    print(json.dumps(result),flush=True)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['audition','narrate'])
    parser.add_argument('--voice',default='af_bella')
    args=parser.parse_args()
    model=engine()
    if args.command=='audition':
        phrase='Useful work can be free, without leaving its creator unpaid. This is Sunset.'
        results=[]
        for name in ['af_bella','bm_george']:
            assert name in model.get_voices()
            results.append(generate((model,name),phrase,OUT/'voice-audition'/f'{name}.wav'))
        (OUT/'voice-audition/manifest.json').write_text(json.dumps(results,indent=2)+'\n')
        return
    script=json.loads((Path(__file__).parent/'narration.json').read_text())
    assert args.voice in model.get_voices()
    records=[]
    for i,line in enumerate(script['lines']):
        record=generate((model,args.voice),line['spoken'],OUT/'voice'/f'{i:02}-{line["id"]}.wav',line.get('speed',.97))
        record.update({'id':line['id'],'index':i})
        records.append(record)
    (OUT/'voice/takes.json').write_text(json.dumps({'synthetic':True,'voice':args.voice,'takes':records,
        'model_assets':json.loads((CACHE/'assets.json').read_text()),'generator_sha256':sha(Path(__file__))},indent=2)+'\n')


if __name__=='__main__':
    if sys.flags.optimize:raise SystemExit('Run without Python optimization.')
    main()
