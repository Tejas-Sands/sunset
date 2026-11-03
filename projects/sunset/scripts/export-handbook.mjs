import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createOfflineHtml,validatePack} from '../src/lib/pack.mjs';
const pack=validatePack(JSON.parse(await readFile(new URL('../public/packs/maintainer-handbook.json',import.meta.url),'utf8')));
if(pack.kind!=='guide'||pack.id!=='maintainer-handbook')throw Error('Expected the original maintainer handbook guide.');
const html=createOfflineHtml(pack);
await writeFile(new URL('../public/try-maintainer-handbook.html',import.meta.url),html);
console.log(JSON.stringify({path:'public/try-maintainer-handbook.html',bytes:Buffer.byteLength(html),sha256:createHash('sha256').update(html).digest('hex')}));
