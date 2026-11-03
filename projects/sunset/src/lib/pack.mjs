import {createGuideHtml} from './guide.mjs';
const encoder = new TextEncoder();
const decoder = new TextDecoder('utf-8', { fatal: true });
const header = encoder.encode('SUNSET01');
const maxPlaintextBytes = 5 * 1024 * 1024;
const envelopeOverhead = 36;

function requireBytes(value, label, length) {
  if (!(value instanceof Uint8Array) || (length !== undefined && value.length !== length)) {
    throw new TypeError(`${label} must be ${length === undefined ? '' : `${length} `}bytes.`);
  }
  return value;
}

function exactFields(value, fields, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)
      || ![Object.prototype, null].includes(Object.getPrototypeOf(value))
      || Reflect.ownKeys(value).length !== fields.length
      || fields.some((field) => !Object.hasOwn(value, field))) {
    throw new TypeError(`${label} must contain exactly: ${fields.join(', ')}.`);
  }
}

function plainText(value, label, limit) {
  if (typeof value !== 'string' || !value.trim() || value.length > limit
      || /[<>\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(value)
      || /(?:https?|ftp|file|data|javascript|vbscript|blob):|\/\/|www\./i.test(value)) {
    throw new TypeError(`${label} must be bounded plain text without markup or resource URLs.`);
  }
}

function identifier(value, label) {
  if (typeof value !== 'string' || !/^[a-z0-9][a-z0-9-]{0,63}$/.test(value)) {
    throw new TypeError(`${label} must be a short lowercase identifier.`);
  }
}


function validateGuide(pack) {
  exactFields(pack,['schema','kind','id','title','description','license','sections'],'Guide');
  if (pack.schema!==2 || pack.kind!=='guide') throw new TypeError('Unsupported guide schema.');
  identifier(pack.id,'Pack ID');plainText(pack.title,'Title',120);plainText(pack.description,'Description',4096);
  if (pack.license!=='CC0-1.0') throw new TypeError('This pack format supports CC0-1.0 only.');
  if (!Array.isArray(pack.sections) || pack.sections.length<1 || pack.sections.length>64) throw new TypeError('A guide needs 1 to 64 sections.');
  const sectionIds=new Set(),itemIds=new Set();
  for (const section of pack.sections) {
    exactFields(section,['id','title','body','checklist'],'Guide section');identifier(section.id,'Section ID');
    if (sectionIds.has(section.id)) throw new TypeError('Section IDs must be unique.');
    sectionIds.add(section.id);plainText(section.title,'Section title',160);plainText(section.body,'Section body',32768);
    if (!Array.isArray(section.checklist) || section.checklist.length>32) throw new TypeError('A section supports up to 32 checklist items.');
    for (const item of section.checklist) {
      exactFields(item,['id','text'],'Checklist item');identifier(item.id,'Checklist ID');
      if (itemIds.has(item.id)) throw new TypeError('Checklist IDs must be unique across the guide.');
      itemIds.add(item.id);plainText(item.text,'Checklist text',1024);
    }
  }
  if (encoder.encode(JSON.stringify(pack)).length>maxPlaintextBytes) throw new RangeError('The plaintext pack exceeds 5 MiB.');
  return pack;
}

/** Validate data only: no uploaded runtime, markup, remote assets or learner identity. */
export function validatePack(pack) {
  if (pack?.schema===2 || pack?.kind==='guide') return validateGuide(pack);
  exactFields(pack, ['id', 'title', 'description', 'license', 'questions'], 'Pack');
  identifier(pack.id, 'Pack ID');
  plainText(pack.title, 'Title', 120);
  plainText(pack.description, 'Description', 4096);
  if (pack.license !== 'CC0-1.0') throw new TypeError('This pack format supports CC0-1.0 only.');
  if (!Array.isArray(pack.questions) || pack.questions.length < 1 || pack.questions.length > 1000) {
    throw new TypeError('A pack needs between 1 and 1000 questions.');
  }
  const ids = new Set();
  for (const question of pack.questions) {
    exactFields(question, ['id', 'prompt', 'choices', 'answer', 'explanation'], 'Question');
    identifier(question.id, 'Question ID');
    if (ids.has(question.id)) throw new TypeError('Question IDs must be unique.');
    ids.add(question.id);
    plainText(question.prompt, 'Prompt', 2048);
    plainText(question.explanation, 'Explanation', 4096);
    if (!Array.isArray(question.choices) || question.choices.length < 2 || question.choices.length > 6
        || question.choices.some((choice) => !Number.isSafeInteger(choice))
        || new Set(question.choices).size !== question.choices.length
        || !Number.isSafeInteger(question.answer) || !question.choices.includes(question.answer)) {
      throw new TypeError('Questions need 2 to 6 distinct safe integers including their integer answer.');
    }
  }
  if (encoder.encode(JSON.stringify(pack)).length > maxPlaintextBytes) {
    throw new RangeError('The plaintext pack exceeds 5 MiB.');
  }
  return pack;
}

function validatePlaintext(plaintext) {
  requireBytes(plaintext, 'Plaintext');
  if (!plaintext.length || plaintext.length > maxPlaintextBytes) {
    throw new RangeError('The plaintext pack must be between 1 byte and 5 MiB.');
  }
  validatePack(JSON.parse(decoder.decode(plaintext)));
}

export async function hashBytes(bytes) {
  requireBytes(bytes, 'Hash input');
  const digest = new Uint8Array(await crypto.subtle.digest('SHA-256', bytes));
  return Array.from(digest, (byte) => byte.toString(16).padStart(2, '0')).join('');
}

export async function keyCommitment(key) {
  requireBytes(key, 'Content key', 32);
  const prefix = encoder.encode('SUNSET:KEY:1:');
  const committed = new Uint8Array(prefix.length + key.length);
  committed.set(prefix);
  committed.set(key, prefix.length);
  return hashBytes(committed);
}

/** Encrypt exact UTF-8 JSON bytes. The 5-MiB plaintext limit excludes 36 envelope bytes. */
export async function encryptPack(plaintext, key) {
  validatePlaintext(plaintext);
  requireBytes(key, 'Content key', 32);
  const nonce = crypto.getRandomValues(new Uint8Array(12));
  const cryptoKey = await crypto.subtle.importKey('raw', key, 'AES-GCM', false, ['encrypt']);
  const ciphertext = new Uint8Array(await crypto.subtle.encrypt({ name: 'AES-GCM', iv: nonce }, cryptoKey, plaintext));
  const envelope = new Uint8Array(20 + ciphertext.length);
  envelope.set(header);
  envelope.set(nonce, 8);
  envelope.set(ciphertext, 20);
  return envelope;
}

/** Authenticate and validate before returning exact plaintext bytes. */
export async function decryptPack(envelope, key) {
  requireBytes(envelope, 'Ciphertext');
  requireBytes(key, 'Content key', 32);
  if (envelope.length <= envelopeOverhead || envelope.length > maxPlaintextBytes + envelopeOverhead
      || !header.every((byte, index) => envelope[index] === byte)) {
    throw new TypeError('Invalid SUNSET01 envelope or ciphertext size.');
  }
  const cryptoKey = await crypto.subtle.importKey('raw', key, 'AES-GCM', false, ['decrypt']);
  const plaintext = new Uint8Array(await crypto.subtle.decrypt({ name: 'AES-GCM', iv: envelope.slice(8, 20) }, cryptoKey, envelope.slice(20)));
  validatePlaintext(plaintext);
  return plaintext;
}

export const introPack = {
  id: 'lantern-trail',
  title: 'The Lantern Trail',
  description: 'The lighthouse has gone dark. Follow the forest trail, solve five number puzzles and carry a little light back to the coast. An original technical sample; educational effectiveness has not been evaluated.',
  license: 'CC0-1.0',
  questions: [
    {
      id: 'forest-gate',
      prompt: 'At the forest gate, 7 fireflies join 5 waiting fireflies. How many lights guide your first steps?',
      choices: [10, 12, 14],
      answer: 12,
      explanation: '7 + 5 = 12. Your first lantern glows. The gate opens onto a quiet trail.',
    },
    {
      id: 'wooden-bridge',
      prompt: 'A bridge has 16 wooden planks. You cross 7 of them. How many planks are still ahead?',
      choices: [8, 9, 10],
      answer: 9,
      explanation: '16 - 7 = 9. Your second lantern lights the rest of the bridge.',
    },
    {
      id: 'orchard-path',
      prompt: 'In the orchard, there are 4 baskets with 3 golden apples in each. How many apples are there altogether?',
      choices: [7, 12, 16],
      answer: 12,
      explanation: '4 groups of 3 make 12. Your third lantern shines between the apple trees.',
    },
    {
      id: 'river-stones',
      prompt: 'You share 24 smooth stones equally among 6 stepping places. How many stones go in each place?',
      choices: [3, 4, 6],
      answer: 4,
      explanation: '24 divided by 6 is 4. Your fourth lantern shows a safe path over the river.',
    },
    {
      id: 'coastal-beacon',
      prompt: 'The beacon gathers 8 sparks from each of 3 lanterns. Then 5 sparks drift away. How many sparks remain?',
      choices: [16, 19, 24],
      answer: 19,
      explanation: '3 times 8 is 24, and 24 - 5 = 19. The last lantern glows. The lighthouse welcomes you home.',
    },
  ],
};

/** A standalone data-and-runtime artifact. It makes no network requests. */
export function createOfflineHtml(input) {
  const pack = validatePack(input);
  if (pack.kind==='guide') return createGuideHtml(pack);
  const embedded = JSON.stringify(pack).replaceAll('<', '\\u003c').replaceAll('\u2028', '\\u2028').replaceAll('\u2029', '\\u2029');
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; connect-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<title>SUNSET offline learning pack</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f5f0e6;color:#233a32;font-family:system-ui,sans-serif;line-height:1.65}main{max-width:760px;margin:auto;padding:48px 24px}header{margin-bottom:30px}.eyebrow{font-size:.78rem;text-transform:uppercase;letter-spacing:.14em;color:#526b5d}h1{font-size:clamp(2.2rem,7vw,3.8rem);line-height:1.1;margin:.4em 0}h2{font-size:1.45rem;line-height:1.5}p{max-width:64ch}.card{background:#fffdf7;border:1px solid #dcd7c8;border-radius:22px;padding:clamp(22px,5vw,40px);box-shadow:0 12px 40px #233a320a}progress{width:100%;height:12px;accent-color:#39795b}.choices{display:flex;gap:12px;flex-wrap:wrap;margin:26px 0}button{font:inherit;cursor:pointer;border:1px solid #bdc9bc;border-radius:12px;padding:12px 22px;background:#edf3e7;color:#233a32;min-width:64px;min-height:48px}button:hover:enabled{background:#d9e8ce}button:focus-visible{outline:3px solid #b45d21;outline-offset:4px}button:disabled{cursor:default;opacity:.6}.primary{background:#244d3a;color:#fff;border-color:#244d3a}.primary:hover:enabled{background:#34664b}#feedback{min-height:3.5em}footer{margin-top:30px;font-size:.84rem;color:#526b5d}small{display:block}#restart{margin-top:18px;background:transparent}[hidden]{display:none!important}@media(prefers-reduced-motion:no-preference){.card{animation:arrive .25s ease-out}@keyframes arrive{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}}
</style>
</head>
<body><main>
<header><div class="eyebrow">SUNSET · Your offline copy</div><h1 id="title"></h1><p id="description"></p></header>
<section class="card" aria-label="Maths adventure">
<p id="status"></p><progress id="progress" value="0" max="5" aria-label="Lanterns lit"></progress>
<h2 id="question" tabindex="-1"></h2><div id="choices" class="choices" role="group" aria-labelledby="question"></div>
<p id="feedback" aria-live="polite" aria-atomic="true"></p>
<button id="next" class="primary" type="button" disabled>Continue along the trail</button>
</section>
<button id="restart" type="button">Start the trail again</button>
<footer><p>This copy works without SUNSET, a wallet or an internet connection. Progress stays in this browser when local storage is available. Clearing browser data can erase progress.</p><small>Original technical sample · Content: CC0-1.0 · Runtime: MIT. No claim of teacher review or measured learning outcomes.</small><small>CC0-1.0 dedicates the content to the public domain to the extent permitted by law. Full terms: Creative Commons CC0 1.0 Universal.</small></footer>
</main>
<script type="application/json" id="pack-data">${embedded}</script>
<script>
(() => {
  'use strict';
  const pack = JSON.parse(document.getElementById('pack-data').textContent);
  const byId = (id) => document.getElementById(id);
  const storageKey = 'sunset-progress:' + pack.id;
  let index = 0;
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey));
    if (saved && Number.isInteger(saved.index) && saved.index >= 0 && saved.index <= pack.questions.length && saved.version === JSON.stringify(pack)) index = saved.index;
  } catch {}
  byId('title').textContent = pack.title;
  byId('description').textContent = pack.description;
  document.title = pack.title + ' · Offline';
  byId('progress').max = pack.questions.length;
  function save(completed) {
    try { localStorage.setItem(storageKey, JSON.stringify({ index: completed, version: JSON.stringify(pack) })); } catch {}
  }
  function render() {
    byId('choices').replaceChildren();
    byId('feedback').textContent = '';
    byId('progress').value = index;
    byId('next').disabled = true;
    const finished = index === pack.questions.length;
    byId('next').hidden = finished;
    if (finished) {
      byId('status').textContent = 'Trail complete';
      byId('question').textContent = 'All ' + pack.questions.length + ' lanterns are lit.';
      byId('feedback').textContent = 'You brought the light home. Keep this copy, share it, or start the adventure again.';
      return;
    }
    const question = pack.questions[index];
    byId('status').textContent = 'Lantern ' + (index + 1) + ' of ' + pack.questions.length;
    byId('question').textContent = question.prompt;
    for (const choice of question.choices) {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = String(choice);
      button.addEventListener('click', () => {
        if (choice !== question.answer) {
          byId('feedback').textContent = 'That lantern needs another spark. Try again; there is no hurry.';
          return;
        }
        byId('feedback').textContent = question.explanation;
        byId('progress').value = index + 1;
        for (const answer of byId('choices').children) answer.disabled = true;
        byId('next').disabled = false;
        save(index + 1);
        byId('next').focus();
      });
      byId('choices').append(button);
    }
  }
  byId('next').addEventListener('click', () => {
    if (byId('next').disabled) return;
    index += 1;
    render();
    byId('question').focus();
  });
  byId('restart').addEventListener('click', () => {
    index = 0;
    save(0);
    render();
    byId('question').focus();
  });
  render();
})();
</script>
</body></html>`;
}
