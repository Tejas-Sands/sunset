import {validateMirrorUri} from './stewardship.mjs';
import {base64ToBytes} from './demo.mjs';
import {decryptPack,hashBytes,keyCommitment,validatePack} from './pack.mjs';
async function bounded(response,maxBytes){if(!response?.ok)throw Error('Mirror download failed');if(response.redirected)throw Error('Mirror redirects are not accepted');const declared=response.headers?.get('content-length');if(declared&&(!/^\d+$/.test(declared)||BigInt(declared)>BigInt(maxBytes)))throw Error('Mirror response exceeds the size limit');if(!response.body?.getReader)throw Error('Mirror response must support bounded streaming');const reader=response.body.getReader(),chunks=[];let size=0;try{for(;;){const{done,value}=await reader.read();if(done)break;size+=value.byteLength;if(size>maxBytes)throw Error('Mirror response exceeds the size limit');chunks.push(value);}}catch(e){await reader.cancel().catch(()=>{});throw e;}finally{reader.releaseLock();}const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}return bytes;}
/** Explicit user-triggered browser fetch. No server fetch, credentials, redirects or code execution. */
export async function fetchVerifiedMirror(uri,expected,{fetcher=fetch}={}){
 if(typeof expected?.publicKey!=='string'||!expected.publicKey)throw Error('A public released key is required');
 for(const h of [expected.manifestHash,expected.plaintextHash,expected.ciphertextHash,expected.keyCommitment])if(!/^[a-f0-9]{64}$/.test(h))throw Error('Independent SHA-256 commitments are required');
 const url=validateMirrorUri(uri),options={method:'GET',credentials:'omit',redirect:'error',referrerPolicy:'no-referrer',cache:'no-store',signal:AbortSignal.timeout(10000)};
 const rawManifest=await bounded(await fetcher(url,options),65536);
 if(await hashBytes(rawManifest)!==expected.manifestHash)throw Error('Mirror manifest does not match the original commitment');
 const manifest=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(rawManifest));
 if(manifest.schema!==2||manifest.ciphertext_path!=='ciphertext.sunset')throw Error('This manifest needs its retained artifact file; network recovery requires schema 2');
 if(manifest.plaintextHash!==expected.plaintextHash||manifest.ciphertextHash!==expected.ciphertextHash||manifest.keyCommitment!==expected.keyCommitment||manifest.license!=='CC0-1.0')throw Error('Manifest identity conflicts with the original agreement');
 const ciphertextUrl=new URL(manifest.ciphertext_path,url).href;
 const envelope=await bounded(await fetcher(ciphertextUrl,{...options,signal:AbortSignal.timeout(10000)}),5*1024*1024+36);
 if(await hashBytes(envelope)!==expected.ciphertextHash)throw Error('Mirror ciphertext is corrupt or substituted');
 const key=base64ToBytes(expected.publicKey);if(await keyCommitment(key)!==expected.keyCommitment)throw Error('Public release key does not match');
 const plain=await decryptPack(envelope,key);if(await hashBytes(plain)!==expected.plaintextHash)throw Error('Mirror plaintext does not match');
 const pack=validatePack(JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(plain)));if(pack.id!==manifest.packId||(expected.packId&&pack.id!==expected.packId))throw Error('Recovered resource identity differs');return pack;
}
