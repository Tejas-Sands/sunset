// Throwaway visual concept: unchanged V11 meshes, lighting and choreography; new UV print only.
import * as T from '/three.module.js';
import '/v11-scene.mjs';
const base=window.sunsetV11,renderOriginal=window.renderFrame,W=1920,H=1080;
const C={cream:'#f8ecd5',coral:'#e46542',mint:'#b7d7c2',ink:'#203b36'};
const printed=[];
function texture(draw){const canvas=document.createElement('canvas');canvas.width=2048;canvas.height=1536;draw(canvas.getContext('2d'));const map=new T.CanvasTexture(canvas);map.colorSpace=T.SRGBColorSpace;map.anisotropy=Math.min(8,base.renderer.capabilities.getMaxAnisotropy());return map}
function line(c,text,x,y,font){c.font=font;c.fillText(text,x,y);printed.push(text)}
function tabs(c){for(const [i,label] of ['PLAN','PREPARE','WELCOME'].entries()){c.fillStyle=[C.mint,'#e8b485','#e8d59c'][i];c.fillRect(135+i*600,1080,560,145);c.fillStyle=C.ink;line(c,label,180+i*600,1173,'650 67px Space')}}
const cover=texture(c=>{c.fillStyle=C.cream;c.fillRect(0,0,2048,1536);c.fillStyle=C.ink;line(c,'A PRACTICAL GUIDE',135,245,'650 66px Space');line(c,'First Community',125,555,'750 171px Bricolage');line(c,'Workshop Kit',125,815,'750 218px Bricolage');tabs(c);c.fillStyle=C.ink;line(c,'A useful copy to keep.',135,1390,'500 62px Space');for(let y=120;y<1430;y+=32){c.fillStyle='#d8d0ba';c.fillRect(1942,y,38,3)}});
const page=texture(c=>{c.fillStyle='#f9f7ee';c.fillRect(0,0,2048,1536);c.fillStyle=C.coral;line(c,'02 / PREPARE',135,220,'650 65px Space');c.fillStyle=C.ink;line(c,'Prepare the materials',125,470,'750 132px Bricolage');for(const [i,text] of ['Set out pens and paper','Leave time for questions'].entries()){const y=720+i*240;c.strokeStyle=C.ink;c.lineWidth=7;c.strokeRect(140,y-70,78,78);line(c,text,275,y,'550 78px Space')}c.fillStyle=C.ink;line(c,'Illustrative workshop checklist',135,1325,'500 53px Space');for(let y=110;y<1430;y+=32){c.fillStyle='#d8d0ba';c.fillRect(1942,y,38,3)}});
const sponsor=texture(c=>{c.fillStyle=C.mint;c.fillRect(0,0,2048,1536);c.fillStyle=C.ink;c.textAlign='center';line(c,'SPONSOR',1024,850,'750 168px Bricolage')});
const edges=texture(c=>{c.fillStyle='#e7dfc9';c.fillRect(0,0,2048,1536);for(let y=24;y<1536;y+=35){c.fillStyle='#c8c1ad';c.fillRect(0,y,2048,4)}for(const [i,color] of [C.mint,'#e8b485','#e8d59c'].entries()){c.fillStyle=color;c.fillRect(1540,170+i*400,508,250)}});
const back=texture(c=>{c.fillStyle=C.cream;c.fillRect(0,0,2048,1536);c.fillStyle=C.ink;line(c,'First Community',135,380,'750 160px Bricolage');line(c,'Workshop Kit',135,610,'750 190px Bricolage');tabs(c)});
for(const body of base.bodies){const materials=body.mesh.material;if(body.id==='handbook-core'||body.id==='handbook-cover'){materials[4].map=body.id==='handbook-core'?page:cover;for(const side of [0,1,2,3]){materials[side]=materials[side].clone();materials[side].color.set('#ffffff');materials[side].map=edges}materials[5]=materials[5].clone();materials[5].color.set('#ffffff');materials[5].map=back}else if(body.id.startsWith('support-'))materials[4].map=sponsor;for(const material of materials)material.needsUpdate=true}
const canvas=document.createElement('canvas');canvas.width=W;canvas.height=H;const ctx=canvas.getContext('2d');
const phrase='Free to use. Creators paid.',label='Concept preview';printed.push(phrase,label);
function ink(id,text,x,y,font){ctx.font=font;const m=ctx.measureText(text);return {id,kind:'screen-text',coordinate_space:'screen',essential:true,visible:true,text,screen_bbox:[x-m.actualBoundingBoxLeft,y-m.actualBoundingBoxAscent,x+m.actualBoundingBoxRight,y+m.actualBoundingBoxDescent],safe_bbox:[96,54,1824,1026],foreground:C.ink,background:'#fcf0db',contrast_ratio:10.7}}
const textElements=[ink('style-phrase',phrase,130,991,'750 76px Bricolage'),ink('concept-label',label,1510,105,'600 34px Space')];
let frame=0,physicalTime=0;
window.renderFrame=t=>{frame=Math.round(t*30);physicalTime=t*8/5.5;const meta=renderOriginal(physicalTime);ctx.clearRect(0,0,W,H);ctx.drawImage(base.renderer.domElement,0,0);ctx.fillStyle='#fcf0db';ctx.fillRect(110,907,1160,117);ctx.fillRect(1490,56,326,72);ctx.fillStyle=C.ink;ctx.font='750 76px Bricolage';ctx.fillText(phrase,130,991);ctx.font='600 34px Space';ctx.fillText(label,1510,105);return {...meta,time:t,physicalTime,essential_text:textElements}};
window.captureFrame=()=>canvas.toDataURL('image/png');
window.sunsetStyle={printed,exportLive(){const live=base.exportLive();live.frames[0]={...live.frames[0],frame,time:frame/30,physicalTime,render_elements:[...live.frames[0].render_elements.filter(e=>e.kind!=='screen-text'),...textElements]};return live}};
window.renderFrame(0);window.sunsetStyleReady=true;
