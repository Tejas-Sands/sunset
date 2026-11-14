'use client';
import {useEffect,useState} from 'react';
import {appendBlock,fetchLatestBlock} from '../lib/pulse.mjs';
import {loadLiveSnapshot} from '../lib/live.mjs';
import {PROOF,shorten} from '../lib/proof.mjs';
import {NodeField} from './Onchain';

type Block={height:number,hash:string,timestamp:number};
const SLOTS=6,INTERVAL=2500;

export default function ChainPulse(){
  const [blocks,setBlocks]=useState<Block[]>([]),[state,setState]=useState<'connecting'|'live'|'down'>('connecting');
  const [contract,setContract]=useState<{campaigns:number,released:number}|null>(null);
  useEffect(()=>{
    let alive=true,timer:ReturnType<typeof setTimeout>|undefined,failures=0;
    async function tick(){
      if(!alive)return;
      if(document.visibilityState==='visible'){
        try{const block=await fetchLatestBlock();if(!alive)return;failures=0;setState('live');setBlocks(previous=>appendBlock(previous,block,SLOTS));}
        catch{if(!alive)return;if(++failures>=2)setState('down');}
      }
      timer=setTimeout(tick,failures?INTERVAL*4:INTERVAL);
    }
    void tick();
    loadLiveSnapshot().then(snapshot=>{if(alive)setContract({campaigns:snapshot.campaigns.length,released:snapshot.campaigns.filter((c:any)=>c.state==='Released').length});}).catch(()=>{});
    return()=>{alive=false;clearTimeout(timer);};
  },[]);
  const latest=blocks[blocks.length-1];
  const slots:(Block|null)[]=[...Array(Math.max(0,SLOTS-blocks.length)).fill(null),...blocks];
  return <section className={'p-pulse p-pulse-'+state} aria-label="Live NEAR testnet status"><NodeField/><div className="p-container p-pulse-row">
    <p className="p-pulse-status"><span className="p-pulse-dot" aria-hidden="true"/>{state==='live'?'Live':state==='down'?'Offline':'Connecting'}<span>NEAR testnet</span></p>
    <ol className="p-pulse-chain" aria-hidden="true">{slots.map((block,i)=><li key={block?block.height:'empty-'+i} className={block?(i===SLOTS-1?'p-pulse-new':''):'p-pulse-empty'}>{block?String(block.height).slice(-3):''}</li>)}</ol>
    <dl className="p-pulse-data">
      <div><dt>block</dt><dd>{latest?latest.height.toLocaleString('en-US'):'—'}</dd></div>
      <div><dt>hash</dt><dd>{latest?shorten(latest.hash,6,6):'—'}</dd></div>
      <div><dt>contract</dt><dd>{PROOF.contract}</dd></div>
      <div><dt>state</dt><dd>{contract?`${contract.campaigns} campaigns, ${contract.released} released, code verified`:state==='down'?'unreachable, records below still verifiable':'reading…'}</dd></div>
    </dl>
  </div></section>;
}
