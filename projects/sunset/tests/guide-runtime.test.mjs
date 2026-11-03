import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {createOfflineHtml} from '../src/lib/pack.mjs';

const pack={schema:2,kind:'guide',id:'runtime-example',title:'Maintainer handbook',description:'An original example.',license:'CC0-1.0',sections:[
  {id:'release',title:'Prepare a release',body:'Record the reviewed commit.',checklist:[]},
  {id:'recover',title:'Recover a lost commit',body:'Inspect the reflog and candidate changes before restoring.',checklist:[{id:'inspect',text:'Inspect the candidate commit summary and actual changes.'}]},
]};
function openHtml(html,storage){
  const ids=new Map();
  class Element{
    constructor(tag){this.tagName=tag;this.children=[];this.dataset={};this.events={};this.attributes={};this.value='';this.textContent='';this.checked=false;}
    set id(value){this._id=value;ids.set(value,this)}get id(){return this._id}
    append(...nodes){this.children.push(...nodes)}
    replaceChildren(){this.children=[]}
    setAttribute(k,v){this.attributes[k]=v}
    addEventListener(k,fn){this.events[k]=fn}
    focus(){}
  }
  for(const id of ['guide-title','guide-description','guide-search','guide-search-status','guide-chapters','guide-chapter','guide-progress','pack-data']){const el=new Element('div');el.id=id;}
  ids.get('pack-data').textContent=html.match(/<script type="application\/json" id="pack-data">([\s\S]*?)<\/script>/)[1];
  const document={getElementById:id=>ids.get(id),createElement:tag=>new Element(tag)};
  const script=html.match(/<script>\n([\s\S]*?)<\/script>/)[1];
  vm.runInNewContext(script,{document,localStorage:storage});
  return ids;
}
test('the exported runtime remembers the searched chapter and checked step after reopening',()=>{
  const values=new Map(),storage={getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,v)};
  const html=createOfflineHtml(pack),page=openHtml(html,storage);
  page.get('guide-search').value='REFLOG';page.get('guide-search').events.input();
  assert.equal(page.get('guide-section-title').textContent,'Recover a lost commit');
  const checkbox=page.get('check-inspect');checkbox.checked=true;checkbox.events.change();
  assert.match(page.get('guide-progress').textContent,/1 of 1 checks complete/);
  const reopened=openHtml(html,storage);
  assert.equal(reopened.get('guide-section-title').textContent,'Recover a lost commit');
  assert.equal(reopened.get('check-inspect').checked,true);
});
test('the exported runtime remains usable when browser storage throws',()=>{
  const page=openHtml(createOfflineHtml(pack),{getItem(){throw Error('Blocked')},setItem(){throw Error('Quota')}});
  page.get('guide-search').value='reflog';page.get('guide-search').events.input();
  const checkbox=page.get('check-inspect');checkbox.checked=true;checkbox.events.change();
  assert.equal(checkbox.checked,true);
  assert.match(page.get('guide-progress').textContent,/1 of 1 checks complete/);
  assert.match(page.get('guide-progress').textContent,/open tab only/);
});
