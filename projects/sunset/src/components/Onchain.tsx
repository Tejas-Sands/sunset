'use client';
import {useEffect,useRef,useState} from 'react';
import {Icon} from './Protocol';
import {accountUrl,fingerprintCells,shorten} from '../lib/proof.mjs';

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
export function Address({id}:{id:string}){return <CopyChip value={id} label="account" href={accountUrl(id)} head={22} tail={8}/>;}
