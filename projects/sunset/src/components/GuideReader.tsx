'use client';
import {useEffect,useRef,useState} from 'react';
import {GUIDE_CSS,filterGuideSections,loadGuideProgress,saveGuideProgress} from '../lib/guide.mjs';

export type GuideSection={id:string,title:string,body:string,checklist:{id:string,text:string}[]};
export type GuidePack={schema:2,kind:'guide',id:string,title:string,description:string,license:'CC0-1.0',sections:GuideSection[]};
type Progress={section:string,checked:string[],persistent:boolean};

export default function GuideReader({pack,titleId='guide-title'}:{pack:GuidePack,titleId?:string}){
  const [query,setQuery]=useState('');
  const [progress,setProgress]=useState<Progress>({section:pack.sections[0].id,checked:[],persistent:false});
  const [ready,setReady]=useState(false);
  const heading=useRef<HTMLHeadingElement>(null);
  useEffect(()=>{
    let storage;
    try{storage=window.localStorage}catch{}
    setProgress(loadGuideProgress(pack,storage));
    setQuery('');
    setReady(true);
  },[pack]);
  function update(next:Progress){
    let storage;
    try{storage=window.localStorage}catch{}
    setProgress({...next,persistent:saveGuideProgress(pack,next,storage)});
  }
  const matches:GuideSection[]=filterGuideSections(pack,query);
  const section=matches.find(s=>s.id===progress.section)||matches[0];
  const total=pack.sections.reduce((n,s)=>n+s.checklist.length,0);
  const position=section?pack.sections.indexOf(section):-1,previous=position>0?pack.sections[position-1]:undefined,next=position>=0?pack.sections[position+1]:undefined;
  function go(target:GuideSection){setQuery('');update({...progress,section:target.id});setTimeout(()=>{heading.current?.focus({preventScroll:true});heading.current?.scrollIntoView({block:'start'});},0);}
  return <section className="sunset-guide" id="guide-reader" aria-labelledby={titleId}>
    <style>{GUIDE_CSS}</style>
    <header><div className="guide-eyebrow">SUNSET · A copy you can keep</div><h1 className="guide-title" id={titleId}>{pack.title}</h1><p className="guide-description">{pack.description}</p></header>
    <div className="guide-layout">
      <aside className="guide-rail">
        <label className="guide-search-label" htmlFor="guide-search">Search this guide</label>
        <input id="guide-search" type="search" placeholder="Find a chapter" autoComplete="off" value={query} onChange={e=>{setQuery(e.target.value);const found:GuideSection[]=filterGuideSections(pack,e.target.value);if(found.length&&!found.some(s=>s.id===progress.section))setProgress({...progress,section:found[0].id})}}/>
        <p className="guide-search-status" role="status" aria-live="polite">{matches.length} of {pack.sections.length} chapters</p>
        <nav className="guide-nav" aria-label="Handbook chapters">{matches.map(s=><button type="button" key={s.id} data-section-id={s.id} aria-current={section===s?'page':undefined} onClick={()=>{update({...progress,section:s.id});setTimeout(()=>heading.current?.focus(),0)}}>
          <span className="guide-chapter-number">Chapter {pack.sections.indexOf(s)+1}</span><span>{s.title}</span>
        </button>)}</nav>
      </aside>
      <div>
        <article key={section?.id||"none"} className="guide-chapter" id="guide-chapter" aria-labelledby="guide-section-title">
          <h2 className="guide-section-title" id="guide-section-title" ref={heading} tabIndex={-1}>{section?.title||'No matching chapters'}</h2>
          {section&&<><p className="guide-body">{section.body}</p>{section.checklist.length>0&&<fieldset><legend>Procedure checklist</legend>{section.checklist.map(item=><label className="guide-check" key={item.id}>
            <input id={'check-'+item.id} data-check-id={item.id} type="checkbox" checked={progress.checked.includes(item.id)} onChange={e=>update({...progress,checked:e.target.checked?[...progress.checked.filter(id=>id!==item.id),item.id]:progress.checked.filter(id=>id!==item.id)})}/><span>{item.text}</span>
          </label>)}</fieldset>}</>}
        </article>
        {(previous||next)&&<nav className="guide-pager" aria-label="Chapter">{previous?<button type="button" onClick={()=>go(previous)}><small>Previous</small><span>{previous.title}</span></button>:<span/>}{next&&<button type="button" className="guide-pager-next" onClick={()=>go(next)}><small>Next chapter</small><span>{next.title}</span></button>}</nav>}
        <p className="guide-progress" id="guide-progress" role="status" aria-live="polite" aria-atomic="true"><span className="guide-progress-bar" aria-hidden="true"><i style={{width:(total?progress.checked.length/total*100:0)+'%'}}/></span>{progress.checked.length} of {total} checks complete. {ready?(progress.persistent?'Saved on this device.':'Browser storage is unavailable. Checks stay for this open tab only.'):'Checks stay on this device when browser storage is available.'}</p>
      </div>
    </div>
    <footer className="guide-footer">Content: CC0-1.0 · Runtime: MIT. No wallet or account is needed to read. Checklist progress stays on this device. Commands are plain text; this guide never runs them.</footer>
  </section>;
}
