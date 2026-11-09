import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createOfflineHtml,validatePack} from '../src/lib/pack.mjs';

const pack=validatePack(JSON.parse(await readFile(new URL('../public/packs/workshop-kit.json',import.meta.url),'utf8')));
if(pack.kind!=='guide'||pack.id!=='workshop-kit')throw Error('Expected the community skill-swap workshop guide.');
const html=createOfflineHtml(pack);
await writeFile(new URL('../public/try-workshop-kit.html',import.meta.url),html);
console.log(JSON.stringify({path:'public/try-workshop-kit.html',bytes:Buffer.byteLength(html),sha256:createHash('sha256').update(html).digest('hex')}));
