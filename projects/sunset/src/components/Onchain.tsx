'use client';
import {useEffect,useRef,useState} from 'react';
import {Icon} from './Protocol';
import {accountUrl,fingerprintCells,seedHex,shorten,transactionUrl} from '../lib/proof.mjs';

export function Fingerprint({hash,size=40}:{hash:string,size?:number}){
  const cells:{x:number,y:number,strong:boolean}[]=fingerprintCells(hash);
  return <svg className="p-fingerprint" width={size} height={size} viewBox="0 0 7 7" aria-hidden="true" focusable="false">{cells.map(cell=><rect key={cell.x+'-'+cell.y} x={cell.x+1} y={cell.y+1} width="1" height="1" opacity={cell.strong?1:.55}/>)}</svg>;
}
export function CopyChip({value,label,href,head=6,tail=4}:{value:string,label:string,href?:string,head?:number,tail?:number}){
  const [copied,setCopied]=useState(false),timer=useRef<ReturnType<typeof setTimeout>|undefined>(undefined);
  useEffect(()=>()=>clearTimeout(timer.current),[]);
  async function copy(){try{await navigator.clipboard.writeText(value);setCopied(true);clearTimeout(timer.current);timer.current=setTimeout(()=>setCopied(false),1600);}catch{}}
  const text=<code title={value}>{shorten(value,head,tail)}</code>;
  return <span className={'p-chip'+(copied?' p-chip-copied':'')}>{href?<a href={href} target="_blank" rel="noreferrer" aria-label={`${label} ${value}, open in explorer`}>{text}<Icon name="external" size={13}/></a>:text}
    <button type="button" onClick={()=>void copy()} aria-label={`Copy ${label}`}><Icon name={copied?'check':'copy'} size={14}/></button><span className="sr-only" role="status">{copied?'Copied':''}</span></span>;
}
export function Avatar({id,size=22}:{id:string,size?:number}){
  const seed=seedHex(id),cells:{x:number,y:number,strong:boolean}[]=fingerprintCells(seed),hue=parseInt(seed.slice(20,23),16)%360;
  return <svg className="p-avatar" width={size} height={size} viewBox="0 0 7 7" aria-hidden="true" focusable="false" style={{background:`hsl(${hue} 42% 24%)`,fill:`hsl(${(hue+150)%360} 78% 72%)`}}>{cells.map(cell=><rect key={cell.x+'-'+cell.y} x={cell.x+1} y={cell.y+1} width="1" height="1" opacity={cell.strong?1:.6}/>)}</svg>;
}
export function Address({id}:{id:string}){return <span className="p-address"><Avatar id={id}/><CopyChip value={id} label="account" href={accountUrl(id)} head={22} tail={8}/></span>;}

// Decorative network of nodes for the dark onchain bands. Fixed coordinates keep server and client markup equal.
const nodes=[[40,60],[150,24],[250,96],[90,150],[330,40],[420,120],[520,50],[610,140],[700,30],[790,110],[880,60],[960,150],[1050,36],[1140,100],[200,170],[470,180],[740,176],[1010,180]];
const edges=[[0,1],[1,2],[0,3],[2,4],[4,5],[5,6],[6,7],[7,8],[8,9],[9,10],[10,11],[11,12],[12,13],[3,14],[2,14],[5,15],[14,15],[7,16],[15,16],[9,16],[11,17],[16,17],[13,17]];
export function NodeField(){
  return <svg className="p-nodes" viewBox="0 0 1180 200" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false"><g className="p-nodes-edges">{edges.map(([a,b])=><path key={a+'-'+b} d={`M${nodes[a][0]} ${nodes[a][1]}L${nodes[b][0]} ${nodes[b][1]}`}/>)}</g><g className="p-nodes-dots">{nodes.map(([x,y],i)=><circle key={i} cx={x} cy={y} r={i%5===0?4:2.5}/>)}</g></svg>;
}
type Row={step:string,label:string,detail:string,signer:string,hash:string,block:string};
export function BlockChain({rows,title,tone=''}:{rows:readonly Row[],title:string,tone?:string}){
  return <div className={'p-blocks '+tone}><h3>{title}</h3><ol className="p-blocks-track" tabIndex={0} aria-label={title}>{rows.map((row,i)=><li key={row.hash} className="p-block">
    <div className="p-block-head"><span>#{String(i+1).padStart(2,'0')}</span><span title={row.block}>block {shorten(row.block,5,4)}</span></div>
    <strong>{row.label}</strong><p>{row.detail}</p>
    <dl><div><dt>signer</dt><dd><Avatar id={row.signer} size={18}/><span title={row.signer}>{shorten(row.signer,6,7)}</span></dd></div><div><dt>tx</dt><dd><a href={transactionUrl(row.hash)} target="_blank" rel="noreferrer" aria-label={`${row.label}: transaction ${row.hash}, open in explorer`}>{shorten(row.hash,6,4)}<Icon name="external" size={13}/></a></dd></div></dl>
  </li>)}</ol></div>;
}
