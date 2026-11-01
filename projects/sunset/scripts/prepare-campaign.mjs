import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {parseArgs} from 'node:util';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {prepareArtifact,base64ToBytes} from '../src/lib/demo.mjs';
import {validatePack,hashBytes} from '../src/lib/pack.mjs';
import {toYocto} from '../src/lib/ledger.mjs';
import {validateMirrorUri} from '../src/lib/stewardship.mjs';
import {validContract} from '../src/lib/chain.mjs';
export async function prepareOnchainCampaign(pack,options,now=Date.now()){
 validatePack(pack);if(!validContract(options.reviewer))throw Error('Use a real testnet reviewer account');
 const manifestUri=validateMirrorUri(options.manifestUri);
 const deadline=Date.parse(options.deadline);if(!Number.isSafeInteger(deadline)||deadline<=now)throw Error('Funding deadline must be a future ISO date');
 const hours=Number(options.releaseHours||24);if(!Number.isInteger(hours)||hours<1||hours>720)throw Error('Release window must be 1–720 hours');
 const target=toYocto(options.target);if(target==='0')throw Error('Target must be positive');
 if(new TextEncoder().encode(pack.title).length>120)throw Error('Contract title exceeds 120 UTF-8 bytes');
 const a=await prepareArtifact(pack),terms={id:pack.id,title:pack.title,reviewer:options.reviewer,manifest_uri:manifestUri,manifest_hash:a.manifestHash,plaintext_hash:a.plaintextHash,ciphertext_hash:a.ciphertextHash,key_commitment:a.keyCommitment,license_hash:await hashBytes(new TextEncoder().encode(pack.license)),target,funding_deadline_ns:(BigInt(deadline)*1000000n).toString(),release_window_ns:(BigInt(hours)*3600000000000n).toString()};
 const {key,...artifact}=a;return{terms,artifact,backup:{schema:1,campaignId:pack.id,keyBase64:key,manifestHash:a.manifestHash}};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){try{
 const {values:o}=parseArgs({options:{pack:{type:'string'},reviewer:{type:'string'},'manifest-uri':{type:'string'},target:{type:'string'},deadline:{type:'string'},'release-hours':{type:'string'},out:{type:'string'}}});
 for(const k of ['pack','reviewer','manifest-uri','target','deadline','out'])if(!o[k])throw Error('Missing --'+k);
 const pack=JSON.parse(await readFile(o.pack,'utf8')),p=await prepareOnchainCampaign(pack,{reviewer:o.reviewer,manifestUri:o['manifest-uri'],target:o.target,deadline:o.deadline,releaseHours:o['release-hours']});
 await mkdir(o.out,{recursive:false,mode:0o700});
 const files={'create-campaign.json':JSON.stringify(p.terms,null,2),'artifact.json':JSON.stringify(p.artifact,null,2),'manifest.json':p.artifact.manifestText,'ciphertext.sunset':base64ToBytes(p.artifact.envelope),'private-release-backup.json':JSON.stringify(p.backup,null,2),'release-args.json':JSON.stringify({id:p.terms.id,key_base64:p.backup.keyBase64})};
 for(const[name,text]of Object.entries(files))await writeFile(resolve(o.out,name),text,{flag:'wx',mode:0o600});
 console.log('Prepared committed artifact and unsigned campaign terms. No network requests or signatures.');console.log('Keep the output directory private. Publish the exact manifest.json and ciphertext.sunset together; retain artifact.json for offline recovery; never upload the backup or release arguments before release.');
}catch(e){console.error(e.message);process.exitCode=1;}}
