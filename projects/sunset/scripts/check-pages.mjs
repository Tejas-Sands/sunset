import assert from 'node:assert/strict';
import {readFile, stat} from 'node:fs/promises';
import {resolve, relative, sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validatePack,createOfflineHtml} from '../src/lib/pack.mjs';

const output = fileURLToPath(new URL('../out/', import.meta.url));
const origin = 'https://sunset.invalid';
const decode = value => value.replace(/&amp;/g, '&').replace(/&#(?:x([\da-f]+)|(\d+));/gi,
  (_, hex, decimal) => String.fromCodePoint(parseInt(hex || decimal, hex ? 16 : 10)));
const visible = html => decode(html.replace(/<(script|style)\b[^>]*>[\s\S]*?<\/\1>/gi, '')
  .replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();
const landing = await readFile(resolve(output, 'index.html'), 'utf8');
const body = landing.match(/<body\b[^>]*>([\s\S]*?)<\/body>/i)?.[1];
assert.ok(body, 'Landing must contain a rendered body');
const headings = [...body.matchAll(/<h1\b[^>]*>([\s\S]*?)<\/h1>/gi)];
assert.equal(headings.length, 1, 'Landing must render one h1 before JavaScript runs');
assert.match(visible(headings[0][1]), /Good things\s+belong to\s+everyone\./i);
const text = visible(body);
for (const content of ['Interactive prototype', 'Simulated NEAR', 'not live funding',
  'The Lantern Trail', 'River Routes', 'The Pebble Market', 'Do I need a wallet?']) {
  assert.ok(text.includes(content), `Missing rendered content: ${content}`);
}
assert.doesNotMatch(text, /\b(?:trusted by|\d[\d,.+]*\s+(?:active learners|happy teachers|schools served|community sponsors))\b/i,
  'The prototype must not present adoption metrics as established use');

const links = [...body.matchAll(/<a\b[^>]*\bhref="([^"]+)"/gi)]
  .map(match => new URL(decode(match[1]), origin));
const appLinks = links.filter(url => url.origin === origin && url.pathname === '/app/');
for (const view of ['Discover', 'Handbook', 'Creator studio', 'Stewardship', 'How it works']) {
  assert.ok(appLinks.some(url => url.searchParams.get('view') === view), `Missing app link: ${view}`);
}
for (const id of ['lantern-trail', 'river-routes', 'pebble-market']) {
  assert.ok(appLinks.some(url => url.searchParams.get('campaign') === id), `Missing campaign link: ${id}`);
}
assert.ok(links.some(url => url.origin === origin && url.pathname === '/try-lantern-trail.html'),
  'Landing must link to the standalone sample');
assert.ok(links.some(url => url.origin === origin && url.pathname === '/try-maintainer-handbook.html'), 'Landing must expose the original handbook sample');
const app = await readFile(resolve(output, 'app/index.html'), 'utf8');
const hosting = JSON.parse(await readFile(fileURLToPath(new URL('../vercel.json', import.meta.url)), 'utf8'));
for (const filename of ['try-lantern-trail.html', 'try-maintainer-handbook.html', 'try-workshop-kit.html']) {
  assert.ok((await stat(resolve(output, filename))).isFile(), `Missing standalone export: ${filename}`);
  assert.ok(hosting.redirects.some(rule => rule.source === `/${filename}`
    && rule.destination === `/${filename.replace(/\.html$/, '/')}` && rule.permanent === true),
    `Vercel must preserve the literal HTML link: ${filename}`);
}
for (const [name, html] of [['landing', landing], ['workspace', app]]) {
  assert.match(html, /<script\b[^>]*id="sunset-theme"/, `${name} needs the before-paint theme bootstrap`);
  assert.ok(html.indexOf('id="sunset-theme"') < html.indexOf('<body'), `${name} must restore its theme before the body`);
  assert.match(html, /class="theme-toggle"/, `${name} needs an accessible theme switch`);
  assert.match(html, /Switch to dark mode/);
  assert.match(html, /Switch to light mode/);
  assert.match(html, /<a\b[^>]*href="\/"[^>]*aria-label="SUNSET home"/, `${name} logo must link to the landing page`);
}
const sample = await readFile(resolve(output, 'try-lantern-trail.html'), 'utf8');
const packData = sample.match(/<script\b[^>]*\bid="pack-data"[^>]*>([\s\S]*?)<\/script>/i)?.[1];
assert.ok(packData, 'Standalone sample must contain its own pack data');
assert.equal(validatePack(JSON.parse(packData)).id, 'lantern-trail');

const handbook = await readFile(resolve(output, 'try-maintainer-handbook.html'), 'utf8');
const guide = validatePack(JSON.parse(handbook.match(/<script type="application\/json" id="pack-data">([\s\S]*?)<\/script>/)[1]));
assert.equal(guide.kind, 'guide');
assert.equal(guide.id, 'maintainer-handbook');
assert.equal(handbook, createOfflineHtml(guide), 'Public download must be the exact offline export');

// Inspect exported HTML and its CSS dependencies without starting a socket.
const pages = new Map([['/', landing], ['/app/', app], ['/try-lantern-trail.html', sample], ['/try-maintainer-handbook.html', handbook]]);
const queue = [...pages].map(([path, content]) => ({url: new URL(path, origin), content, html: true}));
const checked = new Set();
let fonts = 0;
for (const {url: base, content, html} of queue) {
  const references = html
    ? [...content.matchAll(/\b(?:href|src)="([^"]+)"/gi)].map(match => decode(match[1]))
    : [...content.matchAll(/url\(\s*['"]?([^'"\s)]+)['"]?\s*\)/gi)].map(match => match[1]);
  for (const value of references) {
    const url = new URL(value, base);
    if (url.origin !== origin) continue;
    const path = decodeURIComponent(url.pathname);
    const filename = resolve(output, `.${path}`, path.endsWith('/') ? 'index.html' : '');
    const local = relative(output, filename);
    assert.ok(local !== '..' && !local.startsWith(`..${sep}`), `Asset escapes export: ${value}`);
    assert.ok((await stat(filename)).isFile(), `Missing exported target: ${value}`);
    if (url.hash && pages.has(url.pathname)) {
      const ids = [...pages.get(url.pathname).matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);
      assert.ok(ids.includes(decodeURIComponent(url.hash.slice(1))), `Missing anchor: ${url.href}`);
    }
    if (checked.has(filename)) continue;
    checked.add(filename);
    if (/\.woff2?$/.test(path)) fonts++;
    if (path.endsWith('.css')) queue.push({url, content: await readFile(filename, 'utf8'), html: false});
  }
}
assert.ok(fonts, 'Export must include its locally hosted font');
console.log(`Static pages verified: rendered landing, app export, sample, deep links and ${checked.size} local targets (${fonts} font). Browser execution remains unverified.`);
