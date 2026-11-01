import{readFile}from'node:fs/promises';import{createHash}from'node:crypto';
const base=new URL('../contracts/sunset/',import.meta.url),e=JSON.parse(await readFile(new URL('build-evidence.json',base),'utf8'));
function digest(bytes){return createHash('sha256').update(bytes).digest('hex')}
const artifact=await readFile(new URL(e.artifact,base));if(artifact.length!==e.artifact_bytes||digest(artifact)!==e.artifact_sha256)throw Error('Contract artifact differs from recorded evidence');
for(const[path,hash]of Object.entries(e.source_sha256)){if(path.startsWith('/')||path.split('/').includes('..'))throw Error('Invalid source evidence path');if(digest(await readFile(new URL(path,base)))!==hash)throw Error(`Contract source changed since evidence: ${path}`);}
console.log(`Contract artifact and ${Object.keys(e.source_sha256).length} source digests verified (${artifact.length} bytes). No deployment or protocol execution claimed.`);
