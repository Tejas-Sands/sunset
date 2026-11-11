/** Small deterministic calculations used by the public study labs. No model or network. */
function finite(value){if(typeof value!=='number'||!Number.isFinite(value)||Math.abs(value)>1e6)throw Error('Use a finite value between −1,000,000 and 1,000,000.');return value;}
function vector(value,width){if(!Array.isArray(value)||!value.length||value.length>64||(width!==undefined&&value.length!==width))throw Error('Incompatible vector dimensions.');value.forEach(finite);return value;}
/** @param {{causalIndex?: number}} [options] */
export function attentionStep(query,keys,values,{causalIndex}={}){
  vector(query);
  if(!Array.isArray(keys)||!keys.length||keys.length>64||!Array.isArray(values)||values.length!==keys.length)throw Error('Use matching key and value rows.');
  keys.forEach(row=>vector(row,query.length));vector(values[0]);values.forEach(row=>vector(row,values[0].length));
  if(causalIndex!==undefined&&(!Number.isInteger(causalIndex)||causalIndex<0||causalIndex>=keys.length))throw Error('Invalid causal position.');
  const scores=keys.map((row,i)=>causalIndex!==undefined&&i>causalIndex?-Infinity:row.reduce((sum,n,j)=>sum+n*query[j],0)/Math.sqrt(query.length));
  const largest=Math.max(...scores),exponentials=scores.map(score=>Math.exp(score-largest)),sum=exponentials.reduce((a,b)=>a+b,0);
  const weights=exponentials.map(value=>value/sum);
  return {scores,weights,output:values[0].map((_,j)=>values.reduce((sum,row,i)=>sum+weights[i]*row[j],0))};
}
export function binaryLogisticStep({x,w,b,y,learningRate}){
  [x,w,b,learningRate].forEach(finite);
  if(![0,1].includes(y)||learningRate<0||learningRate>1)throw Error('Use a binary target and a learning rate from 0 to 1.');
  const z=w*x+b,probability=z>=0?1/(1+Math.exp(-z)):Math.exp(z)/(1+Math.exp(z));
  const loss=Math.max(z,0)-y*z+Math.log1p(Math.exp(-Math.abs(z))),error=probability-y;
  const gradient={w:error*x,b:error};
  return {z,probability,loss,gradient,next:{w:w-learningRate*gradient.w,b:b-learningRate*gradient.b}};
}
export function lowRankStats({input,output,rank}){
  if(![input,output,rank].every(n=>Number.isInteger(n)&&n>=1&&n<=65536)||rank>Math.min(input,output))throw Error('Use positive integer dimensions and a rank no larger than either dimension.');
  const baseParameters=input*output,trainableParameters=rank*(input+output);
  return {baseParameters,trainableParameters,trainableFraction:trainableParameters/baseParameters,baseWeightBytes:baseParameters*2,adapterWeightBytes:trainableParameters*2};
}
