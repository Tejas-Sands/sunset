import assert from 'node:assert/strict';
import { mkdir, mkdtemp, open, readFile, readdir, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

// Catches a broken cross-module journey or a verifier that assumes a running website/cwd.
test('local workflow verifies retained-file recovery and settlement outside the website directory', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'sunset-workflow-test-'));
  try {
    const caller = join(directory, 'caller');
    await mkdir(caller);
    const outputFile = join(directory, 'output.txt');
    const output = await open(outputFile, 'w');
    let result;
    try {
      result = spawnSync(process.execPath, [fileURLToPath(new URL('../scripts/verify-local.mjs', import.meta.url))], {
        cwd: caller,
        // Regular files avoid IPC socket creation in restricted local environments.
        stdio: ['ignore', output.fd, output.fd],
        timeout: 30_000,
      });
    } finally {
      await output.close();
    }
    assert.ifError(result.error);
    const text = await readFile(outputFile, 'utf8');
    assert.equal(result.status, 0, text);
    assert.match(text, /local rehearsal/i);
    assert.match(text, /browser.*NEAR protocol.*unverified/i);
    assert.deepEqual(await readdir(caller), [], 'the workflow must leave no private backup in the caller directory');
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
