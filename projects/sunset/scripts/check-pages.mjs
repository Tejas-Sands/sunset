import assert from 'node:assert/strict';
import {readFile,stat} from 'node:fs/promises';
import {resolve,relative,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {resources} from '../src/lib/library.mjs';
import {validatePack,createOfflineHtml} from '../src/lib/pack.mjs';

const output=fileURLToPath(new URL('../out/',import.meta.url)),origin='https://sunset.invalid';
const decode=value=>value.replace(/&amp;/g,'&').replace(/&#(?:x([\da-f]+)|(\d+));/gi,(_,hex,decimal)=>String.fromCodePoint(parseInt(hex||decimal,hex?16:10)));
const visible=html=>decode(html.replace(/<(script|style)\b[^>]*>[\s\S]*?<\/\1>/gi,'').replace(/<[^>]+>/g,' ')).replace(/\s+/g,' ').trim();
const landing=await readFile(resolve(output,'index.html'),'utf8'),app=await readFile(resolve(output,'app/index.html'),'utf8');
const body=landing.match(/<body\b[^>]*>([\s\S]*?)<\/body>/i)?.[1];assert.ok(body,'Landing must render a body');
assert.equal([...body.matchAll(/<h1\b[^>]*>/gi)].length,1,'Landing must render one primary heading');
for(const html of [landing,app]){
  assert.doesNotMatch(visible(html),/Simulated NEAR|Interactive prototype|Explore the rehearsal|Role-play adult|Unsigned transaction workbench|Verify contract/i,'Public pages must contain actual resources and live account entry points');
  assert.doesNotMatch(visible(html),/\b(?:trusted by|\d[\d,.+]*\s+(?:active learners|happy teachers|schools served|community sponsors))\b/i,'Do not invent adoption metrics');
}
assert.match(visible(app),/Connect wallet/,'The public app must expose its wallet action');
for(const view of ['Explore','Funding','My activity','Studio','Stewardship'])assert.ok(visible(app).includes(view),`Missing real app destination: ${view}`);
const links=[...body.matchAll(/<a\b[^>]*\bhref="([^"]+)"/gi)].map(match=>new URL(decode(match[1]),origin));
const pages=new Map([['/',landing],['/app/',app]]);
for(const r of resources){
  assert.ok(links.some(url=>url.origin===origin&&url.pathname===r.href),`Featured card must open ${r.href}`);
  assert.ok(visible(body).includes(r.title),`Featured resource needs its actual title: ${r.id}`);
  const html=await readFile(resolve(output,'.'+r.href,'index.html'),'utf8');
  assert.ok(visible(html).includes(r.title)&&visible(html).includes(r.pack.sections[0].body.slice(0,80)),`Resource route must render its actual content: ${r.id}`);
  assert.equal([...html.matchAll(/<h1\b[^>]*>/gi)].length,1,`One primary heading for ${r.id}`);
  for(const source of r.sources)assert.ok(decode(html).includes(source.href),`Primary reference missing: ${r.id}`);
  pages.set(r.href,html);
}
const hosting=JSON.parse(await readFile(fileURLToPath(new URL('../vercel.json',import.meta.url)),'utf8'));
const downloads=['/try-lantern-trail.html','/try-maintainer-handbook.html','/try-workshop-kit.html',...resources.map(r=>r.download)];
for(const path of downloads){
  const html=await readFile(resolve(output,'.'+path),'utf8');
  assert.equal(html,await readFile(fileURLToPath(new URL('../public'+path,import.meta.url)),'utf8'),`Export changes original download bytes: ${path}`);
  const embedded=html.match(/<script\b[^>]*\bid="pack-data"[^>]*>([\s\S]*?)<\/script>/i)?.[1];assert.ok(embedded,`Download needs complete embedded content: ${path}`);
  const pack=validatePack(JSON.parse(embedded));assert.equal(html,createOfflineHtml(pack),`Download is not the exact self-contained export: ${path}`);
  assert.ok(hosting.redirects.some(rule=>rule.source===path&&rule.destination===path.replace(/\.html$/,'/')&&rule.permanent===true),`Literal download link must survive hosting redirects: ${path}`);
  pages.set(path,html);
}
for(const [path,html] of pages){
  if(path.endsWith('.html'))continue;
  assert.match(html,/<script\b[^>]*id="sunset-theme"/,`${path} needs before-paint theme restoration`);
  assert.ok(html.indexOf('id="sunset-theme"')<html.indexOf('<body'),`${path} theme must restore before the body`);
  assert.match(html,/class="theme-toggle"/);assert.match(html,/Switch to dark mode/);assert.match(html,/Switch to light mode/);
  assert.match(html,/<a\b[^>]*href="\/"[^>]*aria-label="SUNSET home"/,`${path} logo must return home`);
}
const queue=[...pages].map(([path,content])=>({url:new URL(path,origin),content,html:true})),checked=new Set();let fonts=0;
for(const {url:base,content,html} of queue){
  const references=html?[...content.matchAll(/\b(?:href|src)="([^"]+)"/gi)].map(match=>decode(match[1])):[...content.matchAll(/url\(\s*['"]?([^'"\s)]+)['"]?\s*\)/gi)].map(match=>match[1]);
  for(const value of references){
    const url=new URL(value,base);if(url.origin!==origin)continue;
    const path=decodeURIComponent(url.pathname),filename=resolve(output,`.${path}`,path.endsWith('/')?'index.html':''),local=relative(output,filename);
    assert.ok(local!=='..'&&!local.startsWith(`..${sep}`),`Asset escapes export: ${value}`);
    assert.ok((await stat(filename)).isFile(),`Missing exported target: ${value}`);
    if(url.hash&&pages.has(url.pathname)){const ids=[...pages.get(url.pathname).matchAll(/\bid="([^"]+)"/g)].map(match=>match[1]);assert.ok(ids.includes(decodeURIComponent(url.hash.slice(1))),`Missing anchor: ${url.href}`);}
    if(checked.has(filename))continue;checked.add(filename);
    if(/\.woff2?$/.test(path))fonts++;
    if(path.endsWith('.css'))queue.push({url,content:await readFile(filename,'utf8'),html:false});
  }
}
assert.ok(fonts,'Public routes must include the locally hosted font');
console.log(`Static pages verified: live app, ${resources.length} actual resource routes, ${downloads.length} exact downloads and ${checked.size} local targets. Browser behavior is checked separately.`);
