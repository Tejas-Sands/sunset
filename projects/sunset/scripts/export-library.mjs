import {mkdir,writeFile} from 'node:fs/promises';
import {resources} from '../src/lib/library.mjs';
import {createOfflineHtml} from '../src/lib/pack.mjs';
await mkdir(new URL('../public/library/',import.meta.url),{recursive:true});
for(const resource of resources)await writeFile(new URL('../public'+resource.download,import.meta.url),createOfflineHtml(resource.pack));
console.log(`Exported ${resources.length} complete technical guides.`);
