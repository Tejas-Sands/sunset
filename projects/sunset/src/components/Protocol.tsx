import {useId} from 'react';
import SunsetMark from './SunsetMark';
import ThemeToggle from './ThemeToggle';

const paths:Record<string,string>={
  external:'M7 17 17 7M8 7h9v9',
  forward:'M5 12h14m-6-6 6 6-6 6',
  back:'M19 12H5m6 6-6-6 6-6',
  download:'M12 4v11m-5-5 5 5 5-5M5 20h14',
  check:'m5 12.5 4.5 4.5L19 7.5',
  close:'M6 6l12 12M18 6 6 18',
  chevron:'m6 9 6 6 6-6',
  refresh:'M20 11a8 8 0 0 0-14.3-4.3L4 8.5M4 4v4.5h4.5M4 13a8 8 0 0 0 14.3 4.3L20 15.5m0 4.5v-4.5h-4.5',
  alert:'M12 8v5m0 3.5v.5M10.3 3.9 2.6 17.3A2 2 0 0 0 4.3 20h15.4a2 2 0 0 0 1.7-2.7L13.7 3.9a2 2 0 0 0-3.4 0Z',
  info:'M12 11v6m0-9.5V8m9 4a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
  clock:'M12 7v5l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
  lock:'M7 11V8a5 5 0 0 1 10 0v3M6 11h12v9H6z',
  wallet:'M4 7h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h10M16 13.5h.5',
  file:'M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8zm0 0v5h5M9 13h6m-6 4h4'
};
export function Icon({name,size=18}:{name:string,size?:number}){
  return <svg className="p-icon" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false"><path d={paths[name]}/></svg>;
}
export function Arrow({down=false}:{down?:boolean}){return <Icon name={down?'download':'forward'}/>;}

const siteLinks=[['#commons','Library'],['#how-it-works','How it works'],['#stewardship','Stewardship'],['#questions','Questions']];
export function SiteHeader({wallet,compact=false,children}:{wallet?:React.ReactNode,compact?:boolean,children?:React.ReactNode}){
  return <header className={'p-header'+(compact?' p-header-compact':'')}><div className="p-header-row p-container">
    <a className="p-brand" href="/" aria-label="SUNSET home"><SunsetMark/><span>SUNSET</span></a>
    {compact?children||<a className="p-back-home" href="/#commons"><Icon name="back" size={16}/>All guides</a>:<nav className="p-site-nav" aria-label="Website navigation">{siteLinks.map(([href,label])=><a key={href} href={href}>{label}</a>)}</nav>}
    <div className="p-header-actions"><ThemeToggle/>{wallet||<a className="p-button p-button-accent p-launch" href="/app/">Open app</a>}</div>
  </div></header>;
}
export function SiteFooter({network}:{network?:React.ReactNode}){
  return <footer className="p-footer"><div className="p-container p-footer-row">
    <div><a className="p-brand" href="/" aria-label="SUNSET home"><SunsetMark/><span>SUNSET</span></a><p>Support once. Share forever.</p></div>
    <nav aria-label="Footer"><a href="/#commons">Library</a><a href="/#how-it-works">How it works</a><a href="/app/?view=Funding">Campaigns</a><a href="https://github.com/Tejas-Sands/sunset" target="_blank" rel="noreferrer">Source code<Icon name="external" size={14}/></a></nav>
    <p className="p-footer-network">{network||'Runs on NEAR testnet. Guides are CC0; software is MIT.'}</p>
  </div></footer>;
}
export function ResourceArt({index=0}:{index?:number}){
  const id=useId();
  return <svg className="p-resource-diagram" viewBox="0 0 400 200" fill="none" aria-hidden="true"><defs><radialGradient id={id}><stop stopColor="#e9825f" stopOpacity=".28"/><stop offset="1" stopColor="#e9825f" stopOpacity="0"/></radialGradient></defs><ellipse cx="220" cy="105" rx="200" ry="115" fill={`url(#${id})`}/>
    <g stroke="#9bb9a4" strokeOpacity=".13">{[20,60,100,140,180].map(y=><path key={'r'+y} d={`M0 ${y}H400`}/>)}{[40,80,120,160,200,240,280,320,360].map(x=><path key={'c'+x} d={`M${x} 0V200`}/>)}</g>
    {index===0?<g transform="translate(78 14)"><g stroke="#a2baaa" strokeOpacity=".55"><path d="M0 86H45m155 0h45M45 4v164m155-164v164"/></g>{Array.from({length:9},(_,i)=><rect key={i} x={63+(i%3)*43} y={23+Math.floor(i/3)*43} width="35" height="35" rx="4" fill="#f3926f" fillOpacity={[.82,.25,.7,.2,.9,.45,.65,.4,.95][i]}/>)}<g fill="#d9e3d5" fontSize="13" fontFamily="ui-monospace,monospace"><text x="6" y="76">Q</text><text x="222" y="76">V</text></g></g>
    :index===1?<g transform="translate(0 -22)"><path d="M58 150 138 68l95 82 105-78M58 150l80 32 95-32 105 31" stroke="#9bbb9f" strokeOpacity=".65" strokeWidth="1.5"/><path d="m338 72-105 78-95-82-80 82" stroke="#f3926f" strokeWidth="2" strokeDasharray="5 7"/>{[[58,150],[138,68],[233,150],[338,72],[138,182],[338,181]].map(([x,y],i)=><g key={i}><circle cx={x} cy={y} r="18" fill="#16392c" stroke={i===2?'#f3926f':'#a6bea7'}/><circle cx={x} cy={y} r="5" fill={i===2?'#f3926f':'#a6bea7'}/></g>)}</g>
    :<g transform="translate(54 36)"><g fill="#9bbda7" fillOpacity=".45">{Array.from({length:12},(_,i)=><rect key={i} x={(i%2)*17} y={Math.floor(i/2)*18} width="12" height="13" rx="1.5"/>)}{Array.from({length:12},(_,i)=><rect key={i} x={73+(i%6)*17} y={Math.floor(i/6)*18} width="12" height="13" rx="1.5"/>)}</g><path d="M187 54h25m-7-7 7 7-7 7" stroke="#dce6d9" strokeWidth="1.5"/>{Array.from({length:36},(_,i)=><rect key={i} x={232+(i%6)*12} y={9+Math.floor(i/6)*15} width="8" height="10" rx="1.5" fill="#f3926f" fillOpacity={(i%6+1)/8+.18}/>)}<g fill="#d9e3d5" fontSize="13" fontFamily="ui-monospace,monospace"><text x="8" y="128">B</text><text x="119" y="56">A</text><text x="254" y="121">ΔW</text></g></g>}
  </svg>;
}
const sentence=(value:string)=>value.charAt(0)+value.slice(1).toLowerCase();
export function ResourceCard({resource:r,heading='h3'}:{resource:any,heading?:'h2'|'h3'}){
  const Heading=heading;
  return <a className="p-resource-card" href={r.href}><div className={'p-resource-art p-resource-art-'+r.index}><ResourceArt index={r.index}/><code>{r.formula}</code></div>
    <div className="p-resource-body"><p className="p-resource-meta"><span>{sentence(r.topic)}</span><span>{r.duration} read</span></p><Heading>{r.title}</Heading><p>{r.description}</p><span className="p-card-action">Read the guide<Icon name="forward"/></span></div></a>;
}
