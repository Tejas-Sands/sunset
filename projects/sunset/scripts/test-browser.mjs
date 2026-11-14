#!/usr/bin/env node
// Build first. An owned Chromium session tests public pages; a separate controlled
// injected wallet tests frontend orchestration only. No real signing or protocol writes.
import assert from 'node:assert/strict';
import {spawn, spawnSync} from 'node:child_process';
import {mkdtemp, mkdir, readFile, rm, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {resources} from '../src/lib/library.mjs';
import {installWalletFixture} from '../tests/browser/wallet-fixture.mjs';
import {browserFixture} from '../tests/browser/fixture-data.mjs';

const usage = 'Usage: node scripts/test-browser.mjs [--url http://127.0.0.1:3000]';
const args = process.argv.slice(2);
if (args.length === 1 && ['--help', '-h'].includes(args[0])) {
  console.log(`${usage}\nWithout --url, serves the existing out/ on 127.0.0.1:3000. No real signatures or protocol writes.`);
  process.exit(0);
}
assert(args.length === 0 || (args.length === 2 && args[0] === '--url'), usage);
const base = new URL(args[1] || 'http://127.0.0.1:3000');
assert(['http:', 'https:'].includes(base.protocol) && !base.username && !base.password
  && base.pathname === '/' && !base.search && !base.hash, 'Use the project origin without credentials, query or path.');
const project = fileURLToPath(new URL('../', import.meta.url));
const temp = await mkdtemp(join(tmpdir(), 'sunset-browser-'));
const session = `sunset-${process.pid.toString(36)}`, config = join(temp, 'agent-browser.json');
await writeFile(config, '{"autoConnect":false,"headed":false}');
await mkdir(join(temp, 'sockets'));
const env = Object.fromEntries(Object.entries(process.env).filter(([key]) => !key.startsWith('AGENT_BROWSER_')));
if (process.env.AGENT_BROWSER_EXECUTABLE_PATH) env.AGENT_BROWSER_EXECUTABLE_PATH = process.env.AGENT_BROWSER_EXECUTABLE_PATH;
Object.assign(env, {AGENT_BROWSER_SOCKET_DIR: join(temp, 'sockets'), AGENT_BROWSER_DOWNLOAD_PATH: temp,
  AGENT_BROWSER_DEFAULT_TIMEOUT: '15000'});
let server, browserStarted = false, initScript, stage = 'static server startup', cleanupPromise;

function browser(...command) {
  const result = spawnSync('agent-browser', ['--config', config, '--session', session, '--namespace', session,
    '--auto-connect', 'false', '--allow-file-access', ...(initScript ? ['--init-script', initScript] : []), '--json', ...command],
  {env, encoding: 'utf8', timeout: 45000, maxBuffer: 4 * 1024 * 1024});
  const detail = `${result.stdout || ''}\n${result.stderr || ''}`.trim();
  assert(!result.error && result.status === 0,
    `agent-browser ${command[0]} failed: ${result.error?.message || detail || result.signal || result.status}`);
  let reply;
  try { reply = JSON.parse(result.stdout); } catch { throw Error(`Invalid agent-browser JSON: ${detail}`); }
  assert.equal(reply.success, true, `agent-browser ${command[0]}: ${JSON.stringify(reply.error || reply)}`);
  return reply.data;
}
const evaluate = code => browser('eval', '-b', Buffer.from(code).toString('base64')).result;
const waitFor = code => browser('wait', '--fn', code);
function act(command, ...values) { browser('snapshot', '-i'); return browser(command, ...values); }
// Actions are disabled while a chain refresh is in flight; a click during that window is silently dropped.
const clickName = name => { waitFor('!document.querySelector(".p-refresh")?.disabled'); return act('find', 'role', 'button', 'click', '--name', name, '--exact'); };
function open(path) { browser('open', new URL(path, base).href); }
function appReady() { waitFor('!!document.querySelector(".p-app-nav")'); }
function assertFits() {
  assert.equal(evaluate('Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) <= innerWidth + 1'),
    true, 'Page must fit the viewport without horizontal overflow');
}
function assertNoPageErrors() { assert.deepEqual(browser('errors').errors, [], 'Browser runtime errors'); }
function passed(message) { console.log(`PASS ${message}`); }
async function startServer() {
  await readFile(join(project, 'out/index.html'));
  let output = '';
  server = spawn('python3', ['-u', '-m', 'http.server', '3000', '--bind', '127.0.0.1', '--directory', join(project, 'out')],
    {stdio: ['ignore', 'pipe', 'pipe']});
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(Error(`Static server startup timed out: ${output}`)), 10000);
    const finish = fn => value => { clearTimeout(timer); fn(value); };
    const consume = chunk => { output = (output + chunk).slice(-6000); if (output.includes('Serving HTTP on')) finish(resolve)(); };
    server.stdout.on('data', consume); server.stderr.on('data', consume);
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
  stage = 'six exact public standalone URLs';
  const standalone = ['/try-lantern-trail.html', '/try-maintainer-handbook.html', '/try-workshop-kit.html', ...resources.map(r => r.download)];
  for (const path of standalone) {
    const response = await fetch(new URL(path, base), {signal: AbortSignal.timeout(10000)});
    assert.equal(response.status, 200, `Standalone URL must work, including hosting redirects: ${path}`);
    assert.deepEqual(Buffer.from(await response.arrayBuffer()), await readFile(join(project, 'public', path)),
      `Standalone public URL changed the original bytes: ${path}`);
  }
  passed('all six standalone public URLs return their exact original bytes');
  stage = 'Chromium startup';
  browserStarted = true;
  browser('set', 'viewport', '1440', '1000');
  open('/');
  waitFor('!!document.querySelector("header .theme-toggle")');
  stage = 'landing, navigation and both themes';
  assertFits();
  const initialTheme = evaluate('document.documentElement.dataset.theme');
  assert(['light', 'dark'].includes(initialTheme), 'Theme bootstrap must run');
  const theme = initialTheme === 'dark' ? 'light' : 'dark';
  act('click', 'header .theme-toggle');
  waitFor(`document.documentElement.dataset.theme === ${JSON.stringify(theme)}`);
  assert.equal(evaluate('localStorage.getItem("sunset-theme")'), theme);
  browser('reload');
  waitFor(`document.documentElement.dataset.theme === ${JSON.stringify(theme)}`);
  act('click', 'header a[href="/app/"]');
  appReady(); assertFits();
  assert.equal(evaluate('document.documentElement.dataset.theme'), theme);
  assert.equal(evaluate('localStorage.getItem("sunset-rehearsal-v1")'), null, 'Public app must not initialize simulated finance');
  act('click', 'header a[aria-label="SUNSET home"]');
  waitFor('!!document.querySelector("#hero-title")');
  assert.equal(new URL(evaluate('location.href')).pathname, '/');
  browser('set', 'viewport', '390', '844');
  waitFor('innerWidth === 390'); assertFits();
  act('click', 'header a[href="/app/"]');
  appReady(); assertFits();
  act('click', 'header a[aria-label="SUNSET home"]');
  waitFor('!!document.querySelector("#hero-title")'); assertFits();
  assert.equal(evaluate('document.documentElement.dataset.theme'), theme);
  assertNoPageErrors();
  passed('desktop/mobile logo home links, persisted theme and viewport fit');

  const downloads = [];
  for (const resource of resources) {
    stage = `${resource.id}: real navigation, guide and download`;
    open('/');
    act('click', `#commons a[href="${resource.href}"]`);
    waitFor('!!document.querySelector("#guide-search")');
    assert.equal(new URL(evaluate('location.href')).pathname, resource.href);
    assert.equal(evaluate('document.querySelector("h1").textContent'), resource.title);
    assertFits();
    act('fill', '#guide-search', 'sunset-no-such-chapter-7x9');
    waitFor('document.querySelector("#guide-section-title")?.textContent === "No matching chapters"');
    act('fill', '#guide-search', resource.pack.sections[2].title);
    waitFor('document.querySelector(".guide-search-status")?.textContent === "1 of 4 chapters"');
    act('click', `[data-section-id="${resource.pack.sections[2].id}"]`);
    const check = resource.pack.sections[2].checklist[0].id;
    act('check', `[data-check-id="${check}"]`);
    browser('reload');
    waitFor(`document.querySelector('[data-check-id="${check}"]')?.checked === true`);
    assert.equal(evaluate('document.querySelector("#guide-section-title").textContent'), resource.pack.sections[2].title);
    const filename = join(temp, resource.id + '-offline.html');
    act('download', '#resource-download', filename);
    assert.deepEqual(await readFile(filename), await readFile(join(project, 'public', resource.download)), 'Actual download must contain exact complete guide bytes');
    downloads.push({filename, resource});
    if (resource.id === 'transformer-attention') {
      assert.equal(evaluate('document.querySelector("#attention-output").textContent'), '[1.689275, 0.733044]');
      act('check', '.p-lab input[type=checkbox]');
      waitFor('document.querySelector("#attention-output").textContent === "[0.731059, 0.537883]"');
    } else if (resource.id === 'backpropagation') {
      assert.equal(evaluate('document.querySelector("#gradient-loss").textContent'), '0.693147');
      clickName('Apply one gradient step');
      waitFor('document.querySelector("#gradient-loss").textContent === "0.575939"');
    } else {
      act('fill', '.p-lab label:nth-child(3) input', '16');
      waitFor('document.querySelector("#adapter-fraction").textContent === "0.78125%"');
    }
    assertFits(); assertNoPageErrors();
  }
  passed('three real resource links, search/empty states, saved chapters/checks, exact downloads and working math labs');

  stage = 'genuine testnet chooser open/cancel and real catalog';
  browser('set', 'viewport', '1440', '1000');
  open('/app/?view=Funding'); appReady();
  waitFor('!!document.querySelector(".p-network-ready")');
  clickName('Connect wallet');
  waitFor('!!document.querySelector(".hot-connector-popup .connect-item")');
  assert.equal(evaluate('!!document.querySelector(".connect-item[data-type=mynearwallet], .connect-item[data-type=my-near-wallet]")'), false);
  act('press', 'Escape');
  waitFor('!document.querySelector(".hot-connector-popup")');
  waitFor('!document.querySelector(".wallet-connect").disabled');
  assert.equal(evaluate('!!document.querySelector(".wallet-account")'), false);
  assertFits(); assertNoPageErrors();
  passed('real catalog read and genuine supported-wallet chooser cancellation; no real connection/signature');

  stage = 'cold offline files';
  browser('set', 'viewport', '390', '844');
  browser('set', 'offline', 'on');
  for (const {filename, resource} of downloads) {
    browser('tab', 'new', pathToFileURL(filename).href);
    waitFor('!!document.querySelector("#guide-search")');
    assert.equal(evaluate('location.protocol'), 'file:');
    act('fill', '#guide-search', resource.pack.sections[1].title);
    waitFor('document.querySelector("#guide-search-status")?.textContent === "1 of 4 chapters"');
    act('check', `[data-check-id="${resource.pack.sections[1].checklist[0].id}"]`);
    assert.equal(evaluate('performance.getEntriesByType("resource").some(r => /^https?:/.test(r.name))'), false);
    assertFits(); assertNoPageErrors();
  }
  // Keep coverage for the original game runtime and handbook as well as their exact HTTP bytes.
  const originalGame = join(temp, 'original-game.html');
  await writeFile(originalGame, await readFile(join(project, 'public/try-lantern-trail.html')));
  browser('tab', 'new', pathToFileURL(originalGame).href);
  waitFor('!!document.querySelector("#question")');
  const pack = evaluate('JSON.parse(document.querySelector("#pack-data").textContent)');
  const wrong = pack.questions[0].choices.find(value => value !== pack.questions[0].answer);
  clickName(String(wrong));
  waitFor('document.querySelector("#feedback")?.textContent.includes("Try again")');
  assert.equal(evaluate('document.querySelector("#next").disabled'), true);
  for (const q of pack.questions) {
    waitFor(`document.querySelector("#question")?.textContent === ${JSON.stringify(q.prompt)}`);
    clickName(String(q.answer)); act('click', '#next');
  }
  waitFor('document.querySelector("#status")?.textContent === "Trail complete"');
  assertFits(); assertNoPageErrors();
  const originalHandbook = join(temp, 'original-handbook.html');
  await writeFile(originalHandbook, await readFile(join(project, 'public/try-maintainer-handbook.html')));
  browser('tab', 'new', pathToFileURL(originalHandbook).href);
  waitFor('!!document.querySelector("#guide-search")');
  act('fill', '#guide-search', 'Recover a lost commit');
  waitFor('document.querySelector("#guide-search-status")?.textContent === "1 of 4 chapters"');
  act('check', '[data-check-id="recovery-copy"]');
  assertFits(); assertNoPageErrors();
  passed('cold offline technical guides, original game wrong-answer/completion paths and original handbook checks');

  stage = 'controlled injected wallet frontend';
  browser('close'); browserStarted = false;
  const data = await browserFixture();
  initScript = join(temp, 'controlled-wallet.js');
  await writeFile(initScript, `(${installWalletFixture.toString()})(${JSON.stringify(data)},${JSON.stringify(base.origin)});`);
  browserStarted = true;
  browser('set', 'viewport', '1440', '1000');
  open('/app/?view=Funding'); appReady();
  waitFor('!!document.querySelector(".p-network-ready")');
  evaluate('__sunsetQA.delay = 100');
  act('fill', '.p-campaign label input[inputmode=decimal]', '0.23');
  clickName('Connect wallet');
  act('click', '.connect-item[data-type=sunset-qa-wallet]');
  waitFor('document.querySelector(".wallet-account")?.textContent.includes("sponsor.testnet") && !document.querySelector(".p-refresh").disabled');
  assert.equal(evaluate('document.querySelector(".p-campaign label input[inputmode=decimal]").value'), '0.23', 'Wallet connection must preserve entered sponsorship');
  assert.equal(evaluate('__sunsetQA.requests.length'), 0);
  clickName('Sponsor public release');
  waitFor('document.body.innerText.includes("Sponsorship confirmed onchain.")');
  assert.equal(evaluate('__sunsetQA.requests[0].actions[0].params.deposit'), '230000000000000000000000');
  assert.equal(evaluate('__sunsetQA.requests.length'), 1);
  evaluate('__sunsetQA.reject = true');
  clickName('Sponsor public release');
  waitFor('document.body.innerText.includes("Wallet request cancelled.")');
  assert.equal(evaluate('__sunsetQA.requests.length'), 1, 'Explicit rejection must not create another request');
  assert.equal(evaluate('!!document.querySelector("[role=status] a")'), false, 'Cancellation must not link to a previous successful receipt');
  assert.equal(evaluate('localStorage.getItem("sunset-pending-v1:sponsor.testnet")'), null);
  evaluate('__sunsetQA.reject = false');
  act('click', '.p-app-nav a[href="/app/?view=My%20activity"], .p-app-nav a[href="/app/?view=My activity"]');
  waitFor('!!document.querySelector(".p-account-stats")');
  clickName('Withdraw credit');
  waitFor('document.body.innerText.includes("Native payout confirmed.")');
  assert.equal(evaluate('__sunsetQA.requests[1].actions[0].params.methodName'), 'withdraw');
  assert.equal(evaluate('__sunsetQA.accounts["sponsor.testnet"].paid'), '400000000000000000000000');
  act('click', '.p-app-nav a[href="/app/?view=Funding"]');
  evaluate('__sunsetQA.switchOnAccountRead = __sunsetQA.accountReads + 2');
  clickName('Sponsor public release');
  waitFor('document.querySelector(".wallet-account")?.textContent.includes("other.testnet")');
  waitFor('!document.querySelector(".p-refresh").disabled');
  assert.equal(evaluate('__sunsetQA.requests.length'), 2, 'A mid-preflight account switch must not sign another request');
  act('click', '.p-app-nav a[href="/app/?view=My%20activity"], .p-app-nav a[href="/app/?view=My activity"]');
  waitFor('!!document.querySelector(".p-account-stats")');
  assert.equal(evaluate('document.querySelector(".p-account-label").textContent'), 'other.testnet');
  assert.equal(evaluate('document.querySelector(".p-account-stats").textContent.includes("0.4")'), false, 'Previous account credit must not remain displayed');
  act('click', '.p-app-nav a[href="/app/?view=Explore"]');
  evaluate('__sunsetQA.outage = true');
  clickName('Refresh state');
  waitFor('document.body.innerText.includes("Live network data is unavailable.")');
  assert.equal(evaluate('document.querySelectorAll(".p-resource-card").length'), 3, 'Reading library must remain available during an RPC outage');
  assert.deepEqual(evaluate('__sunsetQA.errors'), []);
  assertFits(); assertNoPageErrors();
  passed('CONTROLLED wallet: preserved amount, exact sponsorship, rejection, receipt-bound withdrawal, account-switch reconciliation and outage reading');
  console.log('Browser smoke passed. Real page/RPC/chooser and controlled wallet coverage are separate. Browser offline emulation only; no real wallet transaction or OS network toggle was tested.');
} catch (error) {
  console.error(`FAIL ${stage}: ${error.message}`);
  console.error('Browser smoke did not pass. Resolve the reported server/browser/UI failure and rerun; no success or skipped coverage is inferred.');
  process.exitCode = 1;
} finally { await cleanup(); }
