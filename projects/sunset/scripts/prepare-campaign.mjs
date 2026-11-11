import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {parseArgs} from 'node:util';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {base64ToBytes} from '../src/lib/demo.mjs';
import {prepareOnchainCampaign} from '../src/lib/publishing.mjs';
export {prepareOnchainCampaign};
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){try{
 const {values:o}=parseArgs({options:{pack:{type:'string'},reviewer:{type:'string'},'manifest-uri':{type:'string'},target:{type:'string'},deadline:{type:'string'},'release-hours':{type:'string'},out:{type:'string'}}});
 for(const k of ['pack','reviewer','manifest-uri','target','deadline','out'])if(!o[k])throw Error('Missing --'+k);
 const pack=JSON.parse(await readFile(o.pack,'utf8')),p=await prepareOnchainCampaign(pack,{reviewer:o.reviewer,manifestUri:o['manifest-uri'],target:o.target,deadline:o.deadline,releaseHours:o['release-hours']});
 await mkdir(o.out,{recursive:false,mode:0o700});
 const files={'create-campaign.json':JSON.stringify(p.terms,null,2),'artifact.json':JSON.stringify(p.artifact,null,2),'manifest.json':p.artifact.manifestText,'ciphertext.sunset':base64ToBytes(p.artifact.envelope),'private-release-backup.json':JSON.stringify(p.backup,null,2),'release-args.json':JSON.stringify({id:p.terms.id,key_base64:p.backup.keyBase64})};
 for(const[name,text]of Object.entries(files))await writeFile(resolve(o.out,name),text,{flag:'wx',mode:0o600});
 console.log('Prepared committed artifact and unsigned campaign terms. No network requests or signatures.');console.log('Keep the output directory private. Publish the exact manifest.json and ciphertext.sunset together; retain artifact.json for offline recovery; never upload the backup or release arguments before release.');
}catch(e){console.error(e.message);process.exitCode=1;}}
