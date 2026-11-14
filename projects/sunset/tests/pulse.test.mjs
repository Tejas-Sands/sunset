import test from 'node:test';
import assert from 'node:assert/strict';
import {appendBlock,fetchLatestBlock,parseBlock} from '../src/lib/pulse.mjs';

const hash='5fT8k6yscErahFJ7fB2zLmr71y6XKWzuHiVDGPLzYBcF';
const header={height:276002928,hash,timestamp_nanosec:'1793682269958472374'};

test('a finalized block response is validated before it is shown',async()=>{
  assert.deepEqual(parseBlock({header}),{height:276002928,hash,timestamp:1793682269958});
  for(const bad of [{},{header:{...header,height:'1'}},{header:{...header,hash:'<script>'}},{header:{...header,timestamp_nanosec:'0'}}])assert.throws(()=>parseBlock(bad));
  let request;
  const block=await fetchLatestBlock(async(url,options)=>{request={url,options};return {ok:true,json:async()=>({result:{header}})};});
  assert.equal(block.height,276002928);
  assert.equal(request.options.credentials,'omit');assert.deepEqual(JSON.parse(request.options.body).params,{finality:'final'});
  await assert.rejects(fetchLatestBlock(async()=>({ok:false})));
  await assert.rejects(fetchLatestBlock(async()=>({ok:true,json:async()=>({error:{message:'x'}})})));
});

test('the live chain keeps only newer blocks, in order, up to its limit',()=>{
  let blocks=[];
  for(const height of [10,11,11,9,12,13,14,15,16])blocks=appendBlock(blocks,{height});
  assert.deepEqual(blocks.map(b=>b.height),[11,12,13,14,15,16]);
});
