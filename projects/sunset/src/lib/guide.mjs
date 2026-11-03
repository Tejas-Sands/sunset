/** Native data-only guide UI shared by the app and standalone export. */
export function filterGuideSections(pack, query) {
  const needle=query.trim().toLocaleLowerCase();
  return pack.sections.filter(s=>[s.title,s.body,...s.checklist.map(i=>i.text)].join('\n').toLocaleLowerCase().includes(needle));
}
export function loadGuideProgress(pack, storage) {
  const fresh={section:pack.sections[0].id,checked:[],persistent:false};
  try {
    const saved=JSON.parse(storage.getItem('sunset-guide-progress:'+pack.id));
    fresh.persistent=true;
    if (!saved || saved.version!==JSON.stringify(pack) || !Array.isArray(saved.checked) || saved.checked.length>2048) return fresh;
    const valid=new Set(pack.sections.flatMap(s=>s.checklist.map(i=>i.id)));
    return {section:pack.sections.some(s=>s.id===saved.section)?saved.section:fresh.section,
      checked:[...new Set(saved.checked.filter(id=>typeof id==='string'&&valid.has(id)))],persistent:true};
  } catch { return fresh; }
}
export function saveGuideProgress(pack, state, storage) {
  try {
    storage.setItem('sunset-guide-progress:'+pack.id,JSON.stringify({version:JSON.stringify(pack),section:state.section,checked:state.checked}));
    return true;
  } catch { return false; }
}

export const GUIDE_CSS = ".modal-backdrop .modal.guide-modal{width:1240px}.guide-modal .guide-toolbar{padding:24px 80px 0 28px}.sunset-guide{--guide-ink:#233a32;--guide-paper:#fffdf7;--guide-muted:#526458;--guide-line:#d9ded1;color:var(--guide-ink);font-family:system-ui,-apple-system,BlinkMacSystemFont,\"Segoe UI\",sans-serif;line-height:1.65;max-width:1260px;margin:0 auto;padding:32px 28px;box-sizing:border-box;container-type:inline-size}\n.sunset-guide *{box-sizing:border-box}.sunset-guide .guide-eyebrow{font-size:12px;letter-spacing:.13em;text-transform:uppercase;color:var(--guide-muted);font-weight:650}\n.sunset-guide .guide-title{font-size:clamp(30px,4.1vw,52px);line-height:1.12;letter-spacing:-.035em;margin:12px 0 16px;max-width:25ch;color:var(--guide-ink);font-family:inherit}\n.sunset-guide .guide-description{max-width:78ch;margin:0 0 28px;font-size:17px;line-height:1.65}\n.sunset-guide .guide-layout{display:grid;grid-template-columns:240px minmax(0,1fr);gap:32px;align-items:start}\n.sunset-guide .guide-rail{position:sticky;top:20px;min-width:0}.sunset-guide .guide-search-label{display:block;font-size:14px;font-weight:650;margin-bottom:7px}\n.sunset-guide input[type=search]{width:100%;min-height:46px;border:1px solid #99a993;border-radius:8px;background:var(--guide-paper);padding:10px 12px;font:inherit;color:inherit;margin:0}\n.sunset-guide .guide-search-status{font-size:13px;color:var(--guide-muted);margin:9px 0 14px;min-height:22px}.sunset-guide .guide-nav{display:flex;flex-direction:column;gap:6px}\n.sunset-guide .guide-nav button{width:100%;min-height:48px;border:1px solid transparent;border-radius:8px;background:transparent;padding:12px;text-align:left;font:inherit;font-size:14px;line-height:1.45;color:inherit;cursor:pointer;white-space:normal}\n.sunset-guide .guide-nav button:hover{background:#e7eddf}.sunset-guide .guide-nav button[aria-current=page]{background:#e1eadc;border-color:#99a993;font-weight:650}\n.sunset-guide .guide-chapter-number{display:block;font-size:11px;color:var(--guide-muted);letter-spacing:.1em;margin-bottom:4px}\n.sunset-guide .guide-chapter{min-width:0;background:var(--guide-paper);border:1px solid var(--guide-line);border-radius:12px;padding:30px 34px}\n.sunset-guide .guide-chapter .guide-section-title{font:700 clamp(25px,3vw,34px)/1.2 system-ui,sans-serif;letter-spacing:-.025em;margin:0 0 24px;color:var(--guide-ink)}\n.sunset-guide .guide-body{white-space:pre-wrap;overflow-wrap:anywhere;font-size:17px;line-height:1.75;max-width:72ch;margin:0 0 30px}\n.sunset-guide fieldset{padding:18px 0 0;border:0;border-top:1px solid var(--guide-line);margin:0;min-width:0}.sunset-guide legend{font-size:14px;font-weight:700;padding:0 12px 0 0}\n.sunset-guide .guide-check{display:flex;gap:12px;align-items:flex-start;padding:12px 0;min-height:48px;font-size:16px;font-weight:400;line-height:1.6;cursor:pointer;margin:0;overflow-wrap:anywhere}\n.sunset-guide input[type=checkbox]{accent-color:#2b6149;width:21px;height:21px;min-width:21px;margin:3px 0 0;cursor:pointer}\n.sunset-guide .guide-progress{font-size:14px;line-height:1.6;margin:22px 0 0;color:var(--guide-muted);border-top:1px solid var(--guide-line);padding-top:17px}\n.sunset-guide .guide-footer{margin-top:28px;font-size:13px;color:var(--guide-muted);max-width:90ch}\n.sunset-guide :is(button,input):focus-visible{outline:3px solid #bc4829;outline-offset:3px}.sunset-guide .guide-section-title:focus{outline:none}\n@media(max-width:760px){.sunset-guide{padding:24px 18px}.sunset-guide .guide-layout{grid-template-columns:1fr;gap:22px}.sunset-guide .guide-rail{position:static}.sunset-guide .guide-nav{display:grid;grid-template-columns:1fr 1fr}.sunset-guide .guide-chapter{padding:24px 20px}.sunset-guide .guide-description{font-size:16px}.sunset-guide .guide-body{font-size:17px}.sunset-guide .guide-nav button{padding:10px;font-size:13px}}\n@container(max-width:760px){.sunset-guide .guide-layout{grid-template-columns:1fr;gap:22px}.sunset-guide .guide-rail{position:static}.sunset-guide .guide-nav{display:grid;grid-template-columns:1fr 1fr}}\n@media print{.sunset-guide .guide-rail{display:none}.sunset-guide .guide-layout{display:block}.sunset-guide .guide-chapter{border:0;padding:0}.sunset-guide .guide-footer{display:none}}";

function startGuideReader() {
  const pack=JSON.parse(document.getElementById('pack-data').textContent),byId=id=>document.getElementById(id);
  let storage;
  try { storage=localStorage; } catch {}
  let state=loadGuideProgress(pack,storage);
  const total=pack.sections.reduce((n,s)=>n+s.checklist.length,0);
  byId('guide-title').textContent=pack.title;
  byId('guide-description').textContent=pack.description;
  document.title=pack.title+' · Offline';
  function status() {
    byId('guide-progress').textContent=state.checked.length+' of '+total+' checks complete. '+(state.persistent?'Saved on this device.':'Browser storage is unavailable. Checks stay for this open tab only.');
  }
  function save() { state.persistent=saveGuideProgress(pack,state,storage);status(); }
  function render() {
    const matches=filterGuideSections(pack,byId('guide-search').value),section=matches.find(s=>s.id===state.section)||matches[0];
    if (section) state.section=section.id;
    byId('guide-search-status').textContent=matches.length+' of '+pack.sections.length+' chapters';
    const nav=byId('guide-chapters');nav.replaceChildren();
    for (const s of matches) {
      const b=document.createElement('button');b.type='button';b.dataset.sectionId=s.id;
      if (s===section) b.setAttribute('aria-current','page');
      const n=document.createElement('span');n.className='guide-chapter-number';n.textContent='CHAPTER '+String(pack.sections.indexOf(s)+1).padStart(2,'0');
      const label=document.createElement('span');label.textContent=s.title;b.append(n,label);
      b.addEventListener('click',()=>{state.section=s.id;save();render();byId('guide-section-title').focus()});nav.append(b);
    }
    const article=byId('guide-chapter');article.replaceChildren();
    const heading=document.createElement('h2');heading.id='guide-section-title';heading.className='guide-section-title';heading.tabIndex=-1;
    heading.textContent=section?section.title:'No matching chapters';article.append(heading);
    if (section) {
      const body=document.createElement('p');body.className='guide-body';body.textContent=section.body;article.append(body);
      if (section.checklist.length) {
        const list=document.createElement('fieldset'),legend=document.createElement('legend');legend.textContent='Procedure checklist';list.append(legend);
        for (const item of section.checklist) {
          const label=document.createElement('label');label.className='guide-check';
          const input=document.createElement('input');input.type='checkbox';input.id='check-'+item.id;input.dataset.checkId=item.id;input.checked=state.checked.includes(item.id);
          const text=document.createElement('span');text.textContent=item.text;label.append(input,text);
          input.addEventListener('change',()=>{state.checked=input.checked?[...state.checked.filter(id=>id!==item.id),item.id]:state.checked.filter(id=>id!==item.id);save()});list.append(label);
        }
        article.append(list);
      }
    }
    status();
  }
  byId('guide-search').addEventListener('input',render);
  render();
}
export function createGuideHtml(pack) {
  const embedded=JSON.stringify(pack).replaceAll('<','\\u003c').replaceAll('\u2028','\\u2028').replaceAll('\u2029','\\u2029');
  return '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+
    '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; connect-src \'none\'; script-src \'unsafe-inline\'; style-src \'unsafe-inline\'; img-src \'none\'; object-src \'none\'; base-uri \'none\'; form-action \'none\'">'+
    '<title>SUNSET offline handbook</title><style>body{margin:0;background:#f5f0e6}'+GUIDE_CSS+'</style></head><body>'+
    '<main class="sunset-guide" id="guide-reader"><header><div class="guide-eyebrow">SUNSET · Your offline copy</div><h1 class="guide-title" id="guide-title"></h1><p class="guide-description" id="guide-description"></p></header>'+
    '<div class="guide-layout"><aside class="guide-rail"><label class="guide-search-label" for="guide-search">Search handbook</label><input id="guide-search" type="search" placeholder="Find a procedure" autocomplete="off"><p class="guide-search-status" id="guide-search-status" role="status" aria-live="polite"></p><nav class="guide-nav" id="guide-chapters" aria-label="Handbook chapters"></nav></aside>'+
    '<div><article class="guide-chapter" id="guide-chapter" aria-labelledby="guide-section-title"></article><p class="guide-progress" id="guide-progress" role="status" aria-live="polite" aria-atomic="true"></p></div></div>'+
    '<footer class="guide-footer">Content: CC0-1.0 · Runtime: MIT. This self-contained guide needs no SUNSET server, wallet, account or network connection. Checklist progress stays on this device when browser storage is available. Commands are plain text; this guide never runs them.</footer></main>'+
    '<script type="application/json" id="pack-data">'+embedded+'</script><script>\n'+filterGuideSections.toString()+'\n'+loadGuideProgress.toString()+'\n'+saveGuideProgress.toString()+'\n('+startGuideReader.toString()+')();\n</script></body></html>';
}
