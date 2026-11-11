import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import Module from 'node:module';
import {readFileSync} from 'node:fs';
import {introPack} from '../src/lib/pack.mjs';
const require=createRequire(import.meta.url),ts=require('typescript'),React=require('react');
const {renderToStaticMarkup}=require('react-dom/server');

test('reviewer preview exposes every choice and changes visibly when only the declared answer key changes',()=>{
 const previous=Module._extensions['.tsx'];
 Module._extensions['.tsx']=(module,path)=>module._compile(ts.transpileModule(readFileSync(path,'utf8'),{compilerOptions:{jsx:ts.JsxEmit.ReactJSX,module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText,path);
 let PackContent;
 try{({PackContent}=require('../src/components/CampaignActions.tsx'));}
 finally{if(previous)Module._extensions['.tsx']=previous;else delete Module._extensions['.tsx'];}
 const changed=structuredClone(introPack),question=changed.questions[0];
 question.answer=question.choices.find(value=>value!==question.answer);
 const original=renderToStaticMarkup(React.createElement(PackContent,{pack:introPack}));
 const html=renderToStaticMarkup(React.createElement(PackContent,{pack:changed}));
 assert.notEqual(html,original,'An answer-key change must be inspectable before a reviewer approves');
 const visible=html.replace(/<[^>]*>/g,' ').replace(/\s+/g,' ');
 for(const q of changed.questions){for(const choice of q.choices)assert.ok(visible.includes(String(choice)));assert.ok(visible.includes('Correct answer: '+q.answer));}
});
