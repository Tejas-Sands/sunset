import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {resources,resourceById} from '../src/lib/library.mjs';
import {attentionStep,binaryLogisticStep,lowRankStats} from '../src/lib/learning.mjs';
import {validatePack,createOfflineHtml} from '../src/lib/pack.mjs';

const near=(actual,expected)=>assert.ok(Math.abs(actual-expected)<1e-9,`${actual} differs from ${expected}`);
test('all featured technical resources have complete strict packs, unique routes and self-contained exact downloads',async()=>{
 assert.equal(resources.length,3);assert.equal(new Set(resources.map(r=>r.href)).size,3);
 for(const resource of resources){
  const pack=validatePack(resource.pack);assert.equal(pack.id,resource.id);assert.equal(pack.kind,'guide');
  assert.ok(pack.sections.length>=4);assert.ok(pack.sections.every(s=>s.body.length>300&&s.checklist.length>=2));
  const html=await readFile(new URL('../public'+resource.download,import.meta.url),'utf8');
  assert.equal(html,createOfflineHtml(pack));assert.match(html,/connect-src 'none'/);
  assert.equal(JSON.parse(html.match(/id="pack-data">([\s\S]*?)<\/script>/)[1]).id,resource.id);
  assert.ok(resource.sources.every(source=>new URL(source.href).protocol==='https:'));
  assert.equal(resourceById(resource.id),resource);
 }
 for(const id of ['constructor','__proto__','unknown','../backpropagation'])assert.equal(resourceById(id),undefined);
});
test('attention lab computes scaled logits, stable softmax and the complete weighted value vector',()=>{
 const result=attentionStep([Math.SQRT2,0],[[1,0],[0,1],[1,1]],[[1,0],[0,2],[3,1]]);
 result.weights.forEach((w,i)=>near(w,[0.4223187982515182,0.15536240349696362,0.4223187982515182][i]));
 near(result.output[0],1.6892751930060728);near(result.output[1],0.7330436052454454);
 const large=attentionStep([10000],[[10000],[9999]],[[1],[3]]);
 assert.equal(large.output[0],1);assert.ok(large.weights.every(Number.isFinite));
});
test('causal attention excludes future keys and invalid matrix shapes cannot produce plausible output',()=>{
 const result=attentionStep([Math.SQRT2,0],[[1,0],[0,1],[1,1]],[[1,0],[0,2],[3,1]],{causalIndex:1});
 near(result.weights[0],0.7310585786300049);near(result.weights[1],0.2689414213699951);assert.equal(result.weights[2],0);
 near(result.output[0],0.7310585786300049);near(result.output[1],0.5378828427399902);
 for(const inputs of [[[1,2],[[1]],[[1]]],[[NaN],[[1]],[[1]]],[[1],[],[]]])assert.throws(()=>attentionStep(...inputs));
 assert.throws(()=>attentionStep([1],[[1]],[[1]],{causalIndex:-1}));
});
test('binary cross-entropy gradient matches an independently derived step and central finite differences',()=>{
 const input={x:2,w:0.5,b:-1,y:1,learningRate:0.1},result=binaryLogisticStep(input);
 near(result.probability,0.5);near(result.loss,0.6931471805599453);near(result.gradient.w,-1);near(result.gradient.b,-0.5);
 near(result.next.w,0.6);near(result.next.b,-0.95);
 const epsilon=1e-5;
 const numerical=(binaryLogisticStep({...input,w:input.w+epsilon}).loss-binaryLogisticStep({...input,w:input.w-epsilon}).loss)/(2*epsilon);
 near(numerical,result.gradient.w);
 assert.ok(binaryLogisticStep({...input,...result.next}).loss<result.loss);
 assert.equal(binaryLogisticStep({...input,x:10000,w:10000,y:1}).loss,0);
 assert.throws(()=>binaryLogisticStep({...input,y:2}));
});
test('adapter notebook reports actual trained-parameter and two-byte weight counts without implying total GPU memory',()=>{
 const result=lowRankStats({input:4096,output:4096,rank:8});
 assert.equal(result.baseParameters,16777216);assert.equal(result.trainableParameters,65536);
 assert.equal(result.trainableFraction,0.00390625);assert.equal(result.baseWeightBytes,33554432);assert.equal(result.adapterWeightBytes,131072);
 for(const value of [{input:4096,output:4096,rank:0},{input:2,output:2,rank:3},{input:2.5,output:2,rank:1},{input:Infinity,output:2,rank:1}])assert.throws(()=>lowRankStats(value));
});
