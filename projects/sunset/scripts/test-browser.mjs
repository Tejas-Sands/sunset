#!/usr/bin/env node
// Real Chromium smoke test. Requires agent-browser 0.37.1 + its installed browser.
// Build first; the default starts Python's static server. --url uses an existing project server.
import assert from 'node:assert/strict';
import {spawn, spawnSync} from 'node:child_process';
import {mkdtemp, mkdir, readFile, rm, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createOfflineHtml, introPack} from '../src/lib/pack.mjs';

const usage = 'Usage: node scripts/test-browser.mjs [--url http://127.0.0.1:3000]';
const args = process.argv.slice(2);
if (args.length === 1 && ['--help', '-h'].includes(args[0])) {
  console.log(`${usage}\nWithout --url, serves the existing out/ on 127.0.0.1:3000. No wallet or signed actions.`);
  process.exit(0);
}
assert(args.length === 0 || (args.length === 2 && args[0] === '--url'), usage);
const base = new URL(args[1] || 'http://127.0.0.1:3000');
assert(['http:', 'https:'].includes(base.protocol) && !base.username && !base.password
  && base.pathname === '/' && !base.search && !base.hash, 'Use the explicit project origin, without credentials, query or path.');
const project = fileURLToPath(new URL('../', import.meta.url));
const temp = await mkdtemp(join(tmpdir(), 'sunset-browser-'));
const session = `sunset-${process.pid.toString(36)}`;
const config = join(temp, 'agent-browser.json');
await writeFile(config, '{}');
await mkdir(join(temp, 'sockets'));
// Never inherit a human profile, attached browser, stored authentication or restore state.
const env = Object.fromEntries(Object.entries(process.env).filter(([key]) => !key.startsWith('AGENT_BROWSER_')));
if (process.env.AGENT_BROWSER_EXECUTABLE_PATH) env.AGENT_BROWSER_EXECUTABLE_PATH = process.env.AGENT_BROWSER_EXECUTABLE_PATH;
Object.assign(env, {AGENT_BROWSER_SOCKET_DIR: join(temp, 'sockets'), AGENT_BROWSER_DOWNLOAD_PATH: temp,
  AGENT_BROWSER_DEFAULT_TIMEOUT: '15000'});
let server, browserStarted = false, stage = 'static server startup', cleanupPromise;

function browser(...command) {
  const result = spawnSync('agent-browser', ['--config', config, '--session', session, '--namespace', session,
    '--allow-file-access', '--json', ...command], {env, encoding: 'utf8', timeout: 45000, maxBuffer: 4 * 1024 * 1024});
  const detail = `${result.stdout || ''}\n${result.stderr || ''}`.trim();
  assert(!result.error && result.status === 0,
    `agent-browser ${command[0]} failed: ${result.error?.message || detail || result.signal || result.status}`);
  let reply;
  try { reply = JSON.parse(result.stdout); } catch { throw Error(`Invalid agent-browser JSON: ${detail}`); }
  assert.equal(reply.success, true, `agent-browser ${command[0]}: ${JSON.stringify(reply.error || reply)}`);
  return reply.data;
}
function evaluate(code) { return browser('eval', '-b', Buffer.from(code).toString('base64')).result; }
function waitFor(code) { browser('wait', '--fn', code); }
function act(command, ...values) {
  browser('snapshot', '-i'); // Refresh the accessibility tree before every locator interaction.
  return browser(command, ...values);
}
function clickName(name) { act('find', 'role', 'button', 'click', '--name', String(name), '--exact'); }
function appReady() { waitFor('!!document.querySelector(".rehearsal-banner")'); }
function assertTheme(theme) {
  assert.equal(evaluate('document.documentElement.dataset.theme'), theme, 'Chosen theme must survive navigation/reload');
}
function assertFits() {
  assert.equal(evaluate('Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) <= innerWidth + 1'),
    true, 'Page must fit the viewport without horizontal overflow');
}
function assertNoPageErrors() {
  const {errors} = browser('errors');
  assert.deepEqual(errors, [], 'Browser runtime errors');
}
function passed(message) { console.log(`PASS ${message}`); }

async function startServer() {
  await readFile(join(project, 'out', 'index.html')); // Do not serve source or fall back to a dev server.
  let output = '';
  server = spawn('python3', ['-u', '-m', 'http.server', '3000', '--bind', '127.0.0.1', '--directory', join(project, 'out')],
    {stdio: ['ignore', 'pipe', 'pipe']});
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(Error(`Static server startup timed out: ${output}`)), 10000);
    const finish = fn => value => { clearTimeout(timer); fn(value); };
    const consume = chunk => {
      output = (output + chunk).slice(-6000);
      if (output.includes('Serving HTTP on')) finish(resolve)();
    };
    server.stdout.on('data', consume);
    server.stderr.on('data', consume);
    server.once('error', finish(reject));
    server.once('exit', code => finish(reject)(Error(`Static server exited (${code}): ${output.trim()}`)));
  });
  const response = await fetch(base, {signal: AbortSignal.timeout(5000), redirect: 'error'});
  assert.equal(response.status, 200, 'Static project server must answer successfully');
  await response.arrayBuffer();
}
async function cleanup() {
  if (cleanupPromise) return cleanupPromise;
  cleanupPromise = (async () => {
    if (browserStarted) {
      try { browser('close'); } catch (error) { console.error(`Browser cleanup failed: ${error.message}`); process.exitCode = 1; }
      browserStarted = false;
    }
    if (server && server.exitCode === null) {
      server.kill('SIGTERM');
      await new Promise(resolve => {
        const timer = setTimeout(() => { server.kill('SIGKILL'); resolve(); }, 3000);
        server.once('exit', () => { clearTimeout(timer); resolve(); });
      });
    }
    await rm(temp, {recursive: true, force: true});
  })();
  return cleanupPromise;
}
for (const [signal, code] of [['SIGINT', 130], ['SIGTERM', 143]]) {
  process.once(signal, () => { cleanup().finally(() => process.exit(code)); });
}

try {
  if (!args.length) await startServer();
  stage = 'standalone public URLs';
  for (const filename of ['try-lantern-trail.html', 'try-maintainer-handbook.html', 'try-workshop-kit.html']) {
    const response = await fetch(new URL(`/${filename}`, base), {signal: AbortSignal.timeout(10000)});
    assert.equal(response.status, 200, `Standalone URL must work, including hosting redirects: ${filename}`);
    assert.deepEqual(Buffer.from(await response.arrayBuffer()), await readFile(join(project, 'public', filename)),
      `Standalone public URL changed the original bytes: ${filename}`);
  }
  passed('all three public standalone URLs return their exact original bytes');
  stage = 'Chromium startup';
  browser('set', 'viewport', '1440', '1000'); // One startup attempt. Missing/blocked browsers fail, never skip.
  browserStarted = true;
  browser('open', base.href);
  browser('wait', '--load', 'networkidle');
  stage = 'damaged saved-data recovery';
  browser('open', new URL('/app/', base).href);
  appReady();
  const damaged = evaluate(`(() => {
    const value = JSON.parse(localStorage.getItem('sunset-rehearsal-v1'));
    delete value.ledger.campaigns[0].raised;
    const raw = JSON.stringify(value);
    localStorage.setItem('sunset-rehearsal-v1', raw);
    return raw;
  })()`);
  browser('reload');
  appReady();
  waitFor('document.querySelector(".notice[role=status]")?.textContent.includes("Saved rehearsal data needs recovery")');
  assert.equal(evaluate('localStorage.getItem("sunset-rehearsal-v1")'), damaged, 'Damaged original data must remain intact');
  assertFits();
  assertNoPageErrors();
  // Test fixture cleanup only: this isolated browser has no human profile or wallet.
  evaluate('localStorage.removeItem("sunset-rehearsal-v1")');
  browser('open', base.href);
  passed('damaged saved data renders a recovery path without overwriting the original');

  stage = 'landing, navigation and theme';
  waitFor('!!document.querySelector("header .theme-toggle")');
  assertFits();
  const initialTheme = evaluate('document.documentElement.dataset.theme');
  assert(['light', 'dark'].includes(initialTheme), 'Theme bootstrap must run');
  const theme = initialTheme === 'dark' ? 'light' : 'dark';
  act('click', 'header .theme-toggle');
  waitFor(`document.documentElement.dataset.theme === ${JSON.stringify(theme)}`);
  assert.equal(evaluate('localStorage.getItem("sunset-theme")'), theme);
  browser('reload');
  browser('wait', '--load', 'networkidle');
  assertTheme(theme);
  act('click', 'header .lp-nav-cta');
  appReady();
  assertTheme(theme);
  assertFits();
  act('click', '.sidebar a[aria-label="SUNSET home"]');
  waitFor('!!document.querySelector("#hero-title")');
  assert.equal(new URL(evaluate('location.href')).pathname, '/');
  assertTheme(theme);
  browser('set', 'viewport', '390', '844');
  waitFor('innerWidth === 390');
  assertFits();
  act('click', 'header .lp-nav-cta');
  appReady();
  assertFits();
  act('click', '.mobile-brand[aria-label="SUNSET home"]');
  waitFor('!!document.querySelector("#hero-title")');
  assert.equal(new URL(evaluate('location.href')).pathname, '/');
  assertTheme(theme);
  passed('landing/header, desktop/mobile home links, theme persistence and viewport fit');

  stage = 'handbook search, checks and download';
  act('click', '.lp-play-link[href="/app/?view=Handbook"]');
  appReady();
  waitFor('!!document.querySelector("#guide-search")');
  assertTheme(theme);
  assertFits();
  act('fill', '#guide-search', 'sunset-no-such-procedure-7x9');
  waitFor('document.querySelector("#guide-section-title")?.textContent === "No matching chapters"');
  assert.equal(evaluate('document.querySelector(".guide-search-status").textContent'), '0 of 4 chapters');
  act('fill', '#guide-search', 'Recover a lost commit');
  waitFor('document.querySelector(".guide-search-status")?.textContent === "1 of 4 chapters"');
  act('click', '[data-section-id="recover-commit"]');
  act('check', '[data-check-id="recovery-copy"]');
  waitFor('document.querySelector("#guide-progress")?.textContent.startsWith("1 of 16 checks complete.")');
  browser('reload');
  appReady();
  waitFor('document.querySelector("[data-check-id=recovery-copy]")?.checked === true');
  assert.equal(evaluate('document.querySelector("#guide-section-title").textContent'), 'Recover a lost commit');
  assertTheme(theme);
  assertFits();
  const handbookFile = join(temp, 'maintainer-handbook-offline.html');
  act('download', '#download-maintainer-handbook', handbookFile);
  assert.deepEqual(await readFile(handbookFile), await readFile(join(project, 'public', 'try-maintainer-handbook.html')),
    'Actual downloaded handbook must preserve the standalone original bytes');
  passed('handbook empty/search states, saved chapter/check, and actual original-byte download');

  stage = 'released rehearsal sample play and download';
  browser('open', new URL('/app/?view=Discover&campaign=pebble-market', base).href);
  appReady();
  waitFor('document.querySelector("#campaign-heading")?.textContent === "The Pebble Market"');
  assertFits();
  const gameFile = join(temp, 'pebble-market-offline.html');
  act('download', '[role="dialog"] .button-row .secondary', gameFile);
  const sample = {...introPack, id: 'pebble-market', title: 'The Pebble Market'};
  assert.equal(await readFile(gameFile, 'utf8'), createOfflineHtml(sample), 'Actual downloaded game must contain the exact pack/runtime');
  clickName('Open resource');
  waitFor('document.querySelector("#game-heading")?.textContent === "The Pebble Market"');
  for (const [index, question] of sample.questions.entries()) {
    waitFor(`document.querySelector(".question")?.textContent === ${JSON.stringify(question.prompt)}`);
    clickName(question.answer);
    waitFor('document.querySelector(".answer-feedback strong")?.textContent === "A little brighter!"');
    clickName(index === sample.questions.length - 1 ? 'Finish the trail' : 'Next lantern');
  }
  waitFor('!!document.querySelector(".completion")');
  assert.match(evaluate('document.querySelector(".completion").textContent'), /You lit 5 of 5 lanterns/);
  assertFits();
  assertNoPageErrors();
  passed('already-released local resource, all five hosted questions and exact on-disk game download');

  stage = 'cold standalone file loads with browser offline before navigation';
  browser('set', 'offline', 'on');
  browser('tab', 'new', pathToFileURL(gameFile).href);
  waitFor('document.querySelector("#title")?.textContent === "The Pebble Market"');
  assert.equal(evaluate('location.protocol'), 'file:');
  assertFits();
  const wrong = sample.questions[0].choices.find(value => value !== sample.questions[0].answer);
  clickName(wrong);
  waitFor('document.querySelector("#feedback")?.textContent.includes("Try again")');
  assert.equal(evaluate('document.querySelector("#next").disabled'), true, 'Wrong answers must not advance the offline game');
  for (const question of sample.questions) {
    waitFor(`document.querySelector("#question")?.textContent === ${JSON.stringify(question.prompt)}`);
    clickName(question.answer);
    waitFor('document.querySelector("#next")?.disabled === false');
    act('click', '#next');
  }
  waitFor('document.querySelector("#status")?.textContent === "Trail complete"');
  assert.equal(evaluate('document.querySelector("#question").textContent'), 'All 5 lanterns are lit.');
  assert.equal(evaluate('performance.getEntriesByType("resource").some(r => /^https?:/.test(r.name))'), false);
  assertFits();
  assertNoPageErrors();
  browser('tab', 'new', pathToFileURL(handbookFile).href);
  waitFor('!!document.querySelector("#guide-search")');
  act('fill', '#guide-search', 'Recover a lost commit');
  waitFor('document.querySelector("#guide-search-status")?.textContent === "1 of 4 chapters"');
  act('check', '[data-check-id="recovery-copy"]');
  waitFor('document.querySelector("#guide-progress")?.textContent.startsWith("1 of 16 checks complete.")');
  assert.equal(evaluate('location.protocol'), 'file:');
  assertFits();
  assertNoPageErrors();
  passed('cold offline file:// game completion, wrong-answer recovery, handbook search/checks and mobile fit');
  console.log('Browser smoke passed. Browser offline emulation was used; no OS network toggle, wallet or protocol transaction was tested.');
} catch (error) {
  console.error(`FAIL ${stage}: ${error.message}`);
  console.error('Browser smoke did not pass. Resolve the reported server/browser/UI failure and rerun; no success or skipped coverage is inferred.');
  process.exitCode = 1;
} finally {
  await cleanup();
}
