import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, copyFileSync, rmSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { delimiter, join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const source = fileURLToPath(new URL('../scripts/publish-github.sh', import.meta.url));
const token = 'offline-test-token-never-print';
const realGit = process.env.PATH.split(delimiter).map(p => join(p, 'git')).find(p => existsSync(p));
const run = (cmd, args, options = {}) => spawnSync(cmd, args, { encoding: 'utf8', ...options });

function fixture(t, options = {}) {
  const dir = mkdtempSync(join(tmpdir(), 'sunset-publish-'));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  const root = join(dir, 'repo'), remote = join(dir, 'remote.git'), bin = join(dir, 'bin');
  mkdirSync(join(root, 'projects/sunset/scripts'), { recursive: true });
  mkdirSync(bin);
  const git = (...args) => {
    const result = run(realGit, ['-C', root, ...args]);
    assert.equal(result.status, 0, result.stderr);
    return result.stdout.trim();
  };
  git('init', '-b', 'main', ...(options.alternate ? ['--separate-git-dir', join(root, '.sunset-git')] : []));
  git('config', 'user.name', 'Tejas-Sands');
  git('config', 'user.email', '123+Tejas-Sands@users.noreply.github.com');
  writeFileSync(join(root, '.gitignore'), '.sunset-git/\nprivate/\n');
  writeFileSync(join(root, 'README.md'), '# SUNSET\n');
  git('add', '.'); git('commit', '-m', 'Publish README first');
  const first = git('rev-parse', 'HEAD');
  copyFileSync(source, join(root, 'projects/sunset/scripts/publish-github.sh'));
  git('add', '.'); git('commit', '-m', 'Add publishing helper');
  mkdirSync(join(root, 'private'));
  writeFileSync(join(root, 'private/ignored-secret'), 'ignored local content');
  assert.equal(run(realGit, ['init', '--bare', '-b', 'main', remote]).status, 0);
  if (options.unrelated || options.nonMain) {
    const other = join(dir, 'other'); mkdirSync(other);
    const otherGit = (...args) => run(realGit, ['-C', other, ...args]);
    otherGit('init', '-b', options.nonMain ? 'master' : 'main');
    otherGit('-c', 'user.name=Other', '-c', 'user.email=other@example.com', 'commit', '--allow-empty', '-m', 'Unrelated history');
    otherGit('push', remote, options.nonMain ? 'master' : 'main');
    if (options.nonMain) run(realGit, ['--git-dir', remote, 'symbolic-ref', 'HEAD', 'refs/heads/master']);
  }
  if (options.origin) git('remote', 'add', 'origin', options.origin);
  const state = join(dir, 'state.json'), log = join(dir, 'calls.jsonl');
  writeFileSync(state, JSON.stringify({ exists: !options.missing, ...options }));
  const prelude = `#!/usr/bin/env node\nconst fs=require('node:fs'), cp=require('node:child_process');
const a=process.argv.slice(2), s=JSON.parse(fs.readFileSync(process.env.MOCK_STATE,'utf8'));
fs.appendFileSync(process.env.MOCK_LOG,JSON.stringify({tool:TOOL,args:a,tokenPresent:!!process.env.GH_TOKEN})+'\\n');\n`;
  writeFileSync(join(bin, 'gh'), prelude.replace('TOOL', '"gh"') + `
if(a[0]!=='api') process.exit(90);
if(a.includes('user')) {
  if(s.authFail) { console.error(process.env.GH_TOKEN); process.exit(1); }
  console.log(s.wrongIdentity?'someone-else':'Tejas-Sands'); process.exit(0);
}
if(a.includes('user/repos')) {
  if(!a.includes('POST')||!a.includes('name=sunset')||!a.includes('private=false')||!a.includes('auto_init=false')) process.exit(91);
  s.exists=true;fs.writeFileSync(process.env.MOCK_STATE,JSON.stringify(s));process.exit(0);
}
if(a.includes('repos/Tejas-Sands/sunset')) {
  if(s.apiFail) {console.log('HTTP/2.0 403 Forbidden\\n\\n');console.error(process.env.GH_TOKEN);process.exit(1);}
  if(!s.exists) {console.log('HTTP/2.0 404 Not Found\\n\\n');process.exit(1);}
  console.log('HTTP/2.0 200 OK\\n\\n'+(s.wrongRepository?'Elsewhere/sunset\\tElsewhere':'Tejas-Sands/sunset\\tTejas-Sands')+'\\t'+(!s.noPush)+'\\t'+(s.nonMain?'master':'main'));process.exit(0);
}
process.exit(92);
`, { mode: 0o755 });
  writeFileSync(join(bin, 'git'), prelude.replace('TOOL', '"git"') + `
const network=a.some(x=>['ls-remote','fetch','push'].includes(x));
if(network && (!a.includes('credential.helper=')||!a.includes('credential.helper=!gh auth git-credential'))) process.exit(93);
if(s.verifyMismatch&&a.includes('ls-remote')&&!a.includes('--symref')) {console.log('0'.repeat(40)+'\\trefs/heads/main');process.exit(0);}
const mapped=network?a.map(x=>x==='https://github.com/Tejas-Sands/sunset.git'?process.env.MOCK_REMOTE:x):a;
const r=cp.spawnSync(process.env.REAL_GIT,mapped,{stdio:'inherit'});process.exit(r.status??1);
`, { mode: 0o755 });
  const invoke = () => {
    const result = run('bash', ['-x', join(root, 'projects/sunset/scripts/publish-github.sh')], {
      cwd: tmpdir(),
      env: { ...process.env, PATH: bin + delimiter + process.env.PATH, GH_TOKEN: token, GH_DEBUG: 'api', GIT_TRACE: '1', GIT_TRACE_CURL: '1',
        MOCK_STATE: state, MOCK_LOG: log, MOCK_REMOTE: remote, REAL_GIT: realGit },
    });
    assert.ok(!`${result.stdout}${result.stderr}${readFileSync(log, 'utf8')}`.includes(token), 'token leaked into output or argv');
    return { ...result, calls: readFileSync(log, 'utf8').trim().split('\n').map(JSON.parse) };
  };
  return { root, remote, git, invoke, first };
}

const mutations = calls => calls.filter(c => c.args.some(a => ['POST', 'fetch', 'push', 'add'].includes(a)));

test('wrong GitHub identity cannot mutate the repository or remote', t => {
  const f = fixture(t, { wrongIdentity: true, missing: true });
  const r = f.invoke(); assert.notEqual(r.status, 0); assert.deepEqual(mutations(r.calls), []);
  assert.equal(f.git('remote'), '');
});

test('authentication and non-404 API failures never create or push a repository', t => {
  for (const options of [{ authFail: true }, { apiFail: true }]) {
    const f = fixture(t, options), r = f.invoke();
    assert.notEqual(r.status, 0); assert.deepEqual(mutations(r.calls), []);
  }
});

test('an explicit 404 creates an empty public repo and preserves README-first history', t => {
  const f = fixture(t, { missing: true, alternate: true }), before = f.git('log', '--format=raw');
  const r = f.invoke(); assert.equal(r.status, 0, r.stderr);
  assert.equal(f.git('log', '--format=raw'), before);
  assert.equal(f.git('remote', 'get-url', 'origin'), 'https://github.com/Tejas-Sands/sunset.git');
  const remoteHead = run(realGit, ['--git-dir', f.remote, 'rev-parse', 'refs/heads/main']).stdout.trim();
  assert.equal(remoteHead, f.git('rev-parse', 'HEAD'));
  assert.equal(run(realGit, ['--git-dir', f.remote, 'rev-list', '--max-parents=0', 'main']).stdout.trim(), f.first);
  assert.equal(r.calls.filter(c => c.args.includes('POST')).length, 1);
});

test('unrelated remote history and an initialized non-main branch are never pushed', t => {
  for (const options of [{ unrelated: true }, { nonMain: true }]) {
    const f = fixture(t, options), before = run(realGit, ['--git-dir', f.remote, 'show-ref']).stdout;
    const r = f.invoke(); assert.notEqual(r.status, 0);
    assert.ok(!r.calls.some(c => c.args.includes('push')));
    assert.equal(run(realGit, ['--git-dir', f.remote, 'show-ref']).stdout, before);
  }
});

test('an existing ancestor is updated without changing an accepted SSH origin', t => {
  const origin = 'git@github.com:Tejas-Sands/sunset.git', f = fixture(t, { origin });
  f.git('push', f.remote, `${f.first}:refs/heads/main`);
  const r = f.invoke(); assert.equal(r.status, 0, r.stderr);
  assert.equal(f.git('remote', 'get-url', 'origin'), origin);
  assert.equal(run(realGit, ['--git-dir', f.remote, 'rev-parse', 'main']).stdout.trim(), f.git('rev-parse', 'HEAD'));
});

test('a push is not reported successful when remote main verification disagrees', t => {
  const f = fixture(t, { verifyMismatch: true }), r = f.invoke();
  assert.notEqual(r.status, 0); assert.ok(!r.stdout.includes('Published'));
});

test('an unrelated origin, wrong repository, or missing push permission stops publication', t => {
  for (const options of [{ origin: 'https://github.com/another/project.git' }, { wrongRepository: true }, { noPush: true }]) {
    const f = fixture(t, options), r = f.invoke();
    assert.notEqual(r.status, 0); assert.deepEqual(mutations(r.calls), []);
  }
});

test('a dirty tracked file or untracked file stops before authentication', t => {
  for (const name of ['README.md', 'untracked.txt']) {
    const f = fixture(t); writeFileSync(join(f.root, name), 'not committed');
    const r = f.invoke(); assert.notEqual(r.status, 0);
    assert.ok(!r.calls.some(c => c.tool === 'gh'));
  }
});
