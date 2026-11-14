'use client';
import {useRef,useState} from 'react';

// Figures follow the completed testnet showcase: a 0.1 testNEAR goal met by 0.06 + 0.04.
const stages=[
  {id:'commit',tab:'Commit',level:0,title:'The creator commits the finished work.',
    body:'The exact content is hashed into an agreement with a goal, two deadlines and a named reviewer. It cannot be swapped later.',
    facts:[['Pooled','0 of 0.1'],['Resource','Encrypted'],['Creator credit','0']]},
  {id:'fund',tab:'Fund',level:.6,title:'Sponsors pool toward the goal.',
    body:'Anyone can add testNEAR from their own wallet. Contributions are held by the contract, not by the creator.',
    facts:[['Pooled','0.06 of 0.1'],['Resource','Encrypted'],['Creator credit','0']]},
  {id:'release',tab:'Release',level:1,title:'The key is published. The work opens.',
    body:'The creator publishes the matching key before the release deadline. The resource becomes public under CC0 and the creator is credited.',
    facts:[['Pooled','0.1 of 0.1'],['Resource','Public, CC0'],['Creator credit','0.1']]},
  {id:'missed',tab:'Deadline missed',level:.6,title:'Every sponsor can take their contribution back.',
    body:'If the goal is not reached, or the key is not published in time, the campaign becomes refundable. Sponsors claim and withdraw what they put in.',
    facts:[['Pooled','0.06 of 0.1'],['Resource','Stays encrypted'],['Refundable','100%']]}
];
const TOP=62,HORIZON=206;

export default function ReleasePath(){
  const [index,setIndex]=useState(1),tabs=useRef<(HTMLButtonElement|null)[]>([]);
  const stage=stages[index],y=TOP+(HORIZON-TOP)*stage.level;
  function keys(event:React.KeyboardEvent){
    const step=event.key==='ArrowRight'?1:event.key==='ArrowLeft'?-1:0;if(!step)return;
    event.preventDefault();const next=(index+step+stages.length)%stages.length;setIndex(next);tabs.current[next]?.focus();
  }
  return <div className={'p-path p-path-'+stage.id}>
    <svg className="p-path-scene" viewBox="0 0 520 280" role="img" aria-label={`Release path, step ${index+1} of ${stages.length}: ${stage.title}`}>
      <defs><clipPath id="p-path-sky"><rect x="0" y="0" width="520" height={HORIZON}/></clipPath></defs>
      <g clipPath="url(#p-path-sky)"><g className="p-path-sun" style={{transform:`translateY(${y}px)`}}><circle className="p-path-glow" cx="260" cy="0" r="92"/><circle className="p-path-disc" cx="260" cy="0" r="46"/></g></g>
      <rect className="p-path-ground" x="0" y={HORIZON} width="520" height={280-HORIZON}/>
      <g className="p-path-scale"><path d={`M96 ${TOP}V${HORIZON}`}/>{[0,.25,.5,.75].map(v=><path key={v} d={`M90 ${TOP+(HORIZON-TOP)*v}h12`}/>)}
        <text x="80" y={TOP+4} textAnchor="end">0</text><text x="80" y={HORIZON+4} textAnchor="end">Goal</text></g>
      <g className="p-path-horizon"><path d={`M120 ${HORIZON}H400`}/><path d={`M160 ${HORIZON+22}H360`}/><path d={`M205 ${HORIZON+44}H315`}/></g>
      <g className="p-path-tag" style={{transform:`translateY(${Math.min(y,HORIZON-30)}px)`}}><path d="M318 0h24"/><text x="350" y="5">{stage.id==='missed'?'Deadline passed':stage.facts[0][1]+' testNEAR'}</text></g>
    </svg>
    <div className="p-path-tabs" role="tablist" aria-label="Steps of a release" onKeyDown={keys}>{stages.map((s,i)=><button key={s.id} ref={node=>{tabs.current[i]=node;}} type="button" role="tab" id={'path-tab-'+s.id} aria-selected={i===index} aria-controls="path-panel" tabIndex={i===index?0:-1} onClick={()=>setIndex(i)}>{s.tab}</button>)}</div>
    <div className="p-path-panel" role="tabpanel" id="path-panel" aria-labelledby={'path-tab-'+stage.id}>
      <p className="p-path-title">{stage.title}</p><p>{stage.body}</p>
      <dl>{stage.facts.map(([label,value])=><div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
    </div>
    <p className="p-path-note">Figures from The Lantern Trail, funded and released on NEAR testnet.</p>
  </div>;
}
