"""Build a local, dependency-free frame-study viewer; all media remains ignored."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / '.publication/sunset-reference-study-20261105'
SRC = Path(__file__).resolve().parent
clips = []
for alias, name in [('feel-good', 'FEEL_GOOD_STUDY.md'), ('intelligence', 'INTELLIGENCE_STUDY.md')]:
    index = json.loads((OUT / alias / 'index.json').read_text())
    ranges = []
    for line in (SRC / name).read_text().splitlines():
        if not line.startswith('|'):
            continue
        cells = line.split('|')
        match = re.search(r'f?(\d{3})[–-]f?(\d{3})', cells[1])
        if match:
            a, b = map(int, match.groups())
            ranges.append({'first': a, 'last': b, 'note': cells[2].strip().replace('**', '')})
    assert ranges[0]['first'] == 0 and ranges[-1]['last'] == index['decoded_frames'] - 1
    assert all(a['last'] + 1 == b['first'] for a, b in zip(ranges, ranges[1:]))
    audio = json.loads((OUT / alias / 'audio-events.json').read_text())
    items = [{'frame': r['frame'], 'pts': r['pts'], 'duration': r['duration'],
              'image': str((ROOT / r['path']).relative_to(OUT)),
              'delta': r['previous_frame_mae'] or 0,
              'rms': audio[min(round(r['pts'] * 100), len(audio)-1)]['rms']} for r in index['all_frames']]
    clips.append({'id': alias, 'name': Path(index['source_path']).name,
                  'original': Path(index['source_path']).as_uri(), 'count': index['decoded_frames'],
                  'rate': index['encoded_frame_rate'], 'duration': index['visual_duration_seconds'],
                  'dimensions': index['native_dimensions'], 'sha256': index['source_sha256'],
                  'frames': items, 'ranges': ranges})

html = r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SUNSET — every-frame reference study</title>
<style> *{box-sizing:border-box}body{margin:0;background:#111a19;color:#f8f0df;font:16px/1.5 system-ui,sans-serif}header{padding:24px 32px;border-bottom:1px solid #3c4a44}h1{font-size:26px;margin:0 0 8px}p{margin:6px 0;color:#c9cfc8}main{display:grid;grid-template-columns:minmax(0,3fr) minmax(280px,1fr);gap:24px;padding:24px 32px}img{width:100%;max-height:65vh;object-fit:contain;background:#030505}button,select{background:#f8f0df;color:#193d35;font:inherit;padding:9px 14px;border:0;border-radius:5px;cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #ee8d62;outline-offset:3px}.controls{display:flex;align-items:center;gap:12px;margin:12px 0;flex-wrap:wrap}input{width:100%;accent-color:#e6754e}aside{max-height:85vh;overflow:auto}aside button{display:block;width:100%;text-align:left;margin-bottom:10px;background:#23352e;color:#f8f0df}aside button.active{background:#78402c;border-left:4px solid #eeaa74}small{color:#bbc5b9}a{color:#a9ddc0}.counter{font-variant-numeric:tabular-nums;font-weight:700;color:#ffd8b7}svg{width:100%;height:90px;background:#1a2a24;cursor:crosshair}#note{padding:16px;background:#24362f;border-left:3px solid #e6754e;min-height:100px}details{margin-top:16px}code{font-size:12px;overflow-wrap:anywhere}@media(max-width:850px){main{display:block;padding:16px}header{padding:20px}aside{margin-top:20px;max-height:none}img{max-height:55vh}}</style>
<header><h1>Every-frame reference study</h1><p>595 native frames · 21 complete atlases · indexed visual observations</p><small>Reference analysis only. Original clips, frames and audio are local study inputs. Observations do not establish authoring software or original project frame rate.</small></header>
<main><section><div class="controls"><label for="clip">Reference</label><select id="clip"></select><a id="original" target="_blank">Open original with sound</a></div><img id="frame" alt="Native decoded reference frame"><div class="controls"><button id="prev">← One frame</button><button id="play">Play frames</button><button id="next">One frame →</button><span class="counter" id="counter"></span></div><input id="seek" type="range" min="0" value="0" aria-label="Reference frame"><p id="note"></p><p><small>Frame-change score (coral) / audio RMS energy (mint). These measurements do not prove cuts, beats or perceptual sync. Click to seek.</small></p><svg id="graph" viewBox="0 0 1000 90" aria-label="Measured frame change and audio energy"></svg><p id="meta"></p><details><summary>Source identity and study method</summary><p id="method"></p><code id="hash"></code></details></section><aside><h2>Indexed shot and transition notes</h2><div id="shots"></div><small>All ranges are inclusive frame indices. Use ←/→ to inspect each frame; Space toggles playback. Native images preserve supplied raster size. Playback is an inspection aid, not a new export.</small></aside></main>
<script>const clips=__DATA__;let which=0,n=0,playing=false,last=0,shot=-1;const $=s=>document.getElementById(s);clips.forEach((c,i)=>{const o=document.createElement('option');o.value=i;o.textContent=c.id==='feel-good'?'Feel Good — 400 frames':'Intelligence — 195 frames';$('clip').append(o)});function update(){const c=clips[which],f=c.frames[n];$('frame').src=f.image;$('frame').alt=c.name+' / frame '+n;$('seek').value=n;$('counter').textContent='f'+String(n).padStart(3,'0')+' / '+(c.count-1)+' · '+f.pts.toFixed(3)+'s';const k=c.ranges.findIndex(r=>r.first<=n&&n<=r.last);$('note').textContent=c.ranges[k].note;if(k!==shot){[...$('shots').children].forEach((b,i)=>b.classList.toggle('active',i===k));shot=k}}function select(){playing=false;$('play').textContent='Play frames';n=0;shot=-1;const c=clips[which];$('seek').max=c.count-1;$('original').href=c.original;$('meta').textContent=c.dimensions.join(' × ')+' · supplied '+c.rate+' fps · '+c.duration.toFixed(3)+'s picture';$('hash').textContent='SHA-256 '+c.sha256;$('method').textContent='Every decoded frame was extracted without temporal resampling. All frames were inspected in dense indexed atlases, with selected native enlargements. Human listening is not claimed; open the original to hear the source.';$('shots').replaceChildren();c.ranges.forEach(r=>{const b=document.createElement('button');b.textContent='f'+r.first+'–'+r.last+' · '+c.frames[r.first].pts.toFixed(3)+'s — '+r.note;b.onclick=()=>{n=r.first;update()};$('shots').append(b)});$('graph').replaceChildren();for(const [key,color]of[['delta','#f39771'],['rms','#a9ddc0']]){const max=Math.max(.0001,...c.frames.map(f=>f[key]));const p=document.createElementNS('http://www.w3.org/2000/svg','polyline');p.setAttribute('points',c.frames.map((f,i)=>[i/(c.count-1)*1000,85-f[key]/max*75].join(',')).join(' '));p.setAttribute('fill','none');p.setAttribute('stroke',color);p.setAttribute('stroke-width','2');$('graph').append(p)}update()}function step(d){n=Math.max(0,Math.min(clips[which].count-1,n+d));update()}$('clip').onchange=e=>{which=Number(e.target.value);select()};$('seek').oninput=e=>{n=Number(e.target.value);update()};$('prev').onclick=()=>step(-1);$('next').onclick=()=>step(1);$('play').onclick=()=>{playing=!playing;last=performance.now();$('play').textContent=playing?'Pause':'Play frames'};$('graph').onclick=e=>{const box=e.currentTarget.getBoundingClientRect();n=Math.round((e.clientX-box.left)/box.width*(clips[which].count-1));n=Math.max(0,Math.min(clips[which].count-1,n));update()};document.onkeydown=e=>{if(e.target.matches('select,input'))return;if(e.code==='ArrowRight'){e.preventDefault();step(1)}if(e.code==='ArrowLeft'){e.preventDefault();step(-1)}if(e.code==='Space'){e.preventDefault();$('play').click()}};function tick(t){if(playing&&t-last>=clips[which].frames[n].duration*1000){last=t;if(n===clips[which].count-1){playing=false;$('play').textContent='Play frames'}else step(1)}requestAnimationFrame(tick)}select();requestAnimationFrame(tick);</script></html>'''
(OUT / 'reference-study.html').write_text(html.replace('__DATA__', json.dumps(clips, ensure_ascii=False).replace('</', '<\\/')))
print(json.dumps({'viewer': str((OUT / 'reference-study.html').relative_to(ROOT)),
                  'frames': sum(c['count'] for c in clips), 'annotated_ranges': sum(len(c['ranges']) for c in clips)}))
