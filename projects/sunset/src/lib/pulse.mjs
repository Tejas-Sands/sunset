// Read-only view of the newest finalized NEAR testnet block for the landing page's live strip.
import {RPC} from './chain.mjs';

const HASH=/^[1-9A-HJ-NP-Za-km-z]{43,44}$/;
export function parseBlock(result){
  const header=result?.header,height=header?.height,timestamp=Number(BigInt(header?.timestamp_nanosec||0)/1000000n);
  if(!Number.isSafeInteger(height)||height<=0||typeof header.hash!=='string'||!HASH.test(header.hash)||!(timestamp>0))throw Error('Unexpected block response');
  return {height,hash:header.hash,timestamp};
}
export async function fetchLatestBlock(fetcher=fetch){
  const response=await fetcher(RPC,{method:'POST',credentials:'omit',redirect:'error',headers:{'content-type':'application/json'},
    body:JSON.stringify({jsonrpc:'2.0',id:'sunset-pulse',method:'block',params:{finality:'final'}}),signal:AbortSignal.timeout(8000)});
  if(!response.ok)throw Error('Testnet RPC unavailable');
  const body=await response.json();
  if(body?.error||!body?.result)throw Error('Testnet RPC unavailable');
  return parseBlock(body.result);
}
// Keeps the newest blocks in ascending order without duplicates or stale heights.
export function appendBlock(blocks,block,limit=6){
  if(blocks.length&&block.height<=blocks[blocks.length-1].height)return blocks;
  return [...blocks,block].slice(-limit);
}
