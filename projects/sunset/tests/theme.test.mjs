import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {themeBootstrap, toggleTheme} from '../src/lib/theme.mjs';

function page(values = new Map(), prefersDark = false, blocked = false) {
  const storage = {
    getItem(key) { if (blocked) throw Error('Storage blocked'); return values.get(key) ?? null; },
    setItem(key, value) { if (blocked) throw Error('Quota exceeded'); values.set(key, value); },
  };
  const window = {localStorage: storage, matchMedia: () => ({matches: prefersDark})};
  if (blocked === 'getter') Object.defineProperty(window, 'localStorage', {get() {throw Error('Storage access blocked');}});
  const context = vm.createContext({
    document: {documentElement: {dataset: {}}},
    window,
  });
  vm.runInContext(themeBootstrap, context);
  return {
    current: () => context.document.documentElement.dataset.theme,
    toggle: () => vm.runInContext(`(${toggleTheme.toString()})()`, context),
  };
}

test('first paint follows the device, with a valid saved choice taking precedence', () => {
  assert.equal(page(new Map(), false).current(), 'light');
  assert.equal(page(new Map(), true).current(), 'dark');
  assert.equal(page(new Map([['sunset-theme', 'light']]), true).current(), 'light');
  assert.equal(page(new Map([['sunset-theme', 'dark']]), false).current(), 'dark');
  assert.equal(page(new Map([['sunset-theme', 'unexpected']]), true).current(), 'dark');
});

test('switching survives a new page without modifying the rehearsal or other stored data', () => {
  const rehearsal = '{"schema":1,"ledger":{"existing":"keep me"}}';
  const values = new Map([['sunset-rehearsal-v1', rehearsal], ['unrelated', 'keep this too']]);
  const landing = page(values);
  landing.toggle();
  assert.equal(landing.current(), 'dark');
  const workspace = page(values);
  assert.equal(workspace.current(), 'dark');
  workspace.toggle();
  assert.equal(workspace.current(), 'light');
  assert.equal(page(values, true).current(), 'light');
  assert.equal(values.get('sunset-rehearsal-v1'), rehearsal);
  assert.equal(values.get('unrelated'), 'keep this too');
});

test('blocked storage still allows the device default and repeated in-tab switches', () => {
  for (const blocked of [true, 'getter']) {
    const current = page(new Map(), true, blocked);
    assert.equal(current.current(), 'dark');
    current.toggle();
    assert.equal(current.current(), 'light');
    current.toggle();
    assert.equal(current.current(), 'dark');
  }
});
