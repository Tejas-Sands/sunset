import * as T from '/three.module.js';

// Original scene geometry. Reference videos are never loaded as textures or footage.
const cfg=window.SUNSET_RENDER||{}, W=cfg.width||1920,H=cfg.height||1080;
const renderer=new T.WebGLRenderer({antialias:false,preserveDrawingBuffer:true,powerPreference:'high-performance'});
renderer.setPixelRatio(1);renderer.setSize(W,H);renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.1;
renderer.shadowMap.enabled=false;document.body.append(renderer.domElement);
const scene=new T.Scene(),camera=new T.PerspectiveCamera(38,W/H,.05,100);
const colors={ink:'#090d0c',cream:'#f4f0e8',coral:'#dc643d',amber:'#efaf58',green:'#173f31'};
const clamp=v=>Math.max(0,Math.min(1,v)), ease=v=>1-(1-clamp(v))**3, smooth=v=>{v=clamp(v);return v*v*(3-2*v)}, lerp=(a,b,t)=>a+(b-a)*t;
const vec=(a,b,t)=>a.map((v,i)=>lerp(v,b[i],t));
const physical=(color,metalness=.8,roughness=.17)=>new T.MeshStandardMaterial({color,metalness,roughness});
const copper=physical(colors.coral,.8,.18),gold=physical(colors.amber,.9,.13),silver=physical('#e0e2df',1,.13),jade=physical('#1d4536',.55,.17);
const porcelain=physical('#f4eddf',.15,.22),dark=physical('#13271f',.4,.22);
const glass=new T.MeshPhysicalMaterial({color:'#c9dfcf',metalness:.2,roughness:.07,transparent:true,opacity:.25,clearcoat:.8,side:T.FrontSide,depthWrite:false});
const environment=new T.Scene();environment.background=new T.Color('#535e57');
function panel(x,y,z,w,h,power,color='#ffffff'){const m=new T.MeshBasicMaterial({color:new T.Color(color).multiplyScalar(power),side:T.DoubleSide});const p=new T.Mesh(new T.PlaneGeometry(w,h),m);p.position.set(x,y,z);p.lookAt(0,0,0);environment.add(p)}
panel(-4,4,2,3,7,4);panel(4,2,-2,1,7,5);panel(0,6,0,6,4,2.8);panel(0,1,-5,6,1,2);panel(-2,-3,3,3,4,.4,'#ffb180');
const pmrem=new T.PMREMGenerator(renderer);scene.environment=pmrem.fromScene(environment,.025,.1,40).texture;pmrem.dispose();
const ambient=new T.AmbientLight('#c6d5d0',.15);scene.add(ambient);
const key=new T.DirectionalLight('#fff5e2',3.5);key.position.set(-3,6,5);key.castShadow=true;key.shadow.mapSize.set(1024,1024);key.shadow.camera.left=-8;key.shadow.camera.right=8;key.shadow.camera.top=8;key.shadow.camera.bottom=-8;key.shadow.normalBias=.03;key.shadow.bias=-.0003;scene.add(key);
const rim=new T.DirectionalLight('#e8ac70',1.3);rim.position.set(4,2,-4);scene.add(rim);
const floor=new T.Mesh(new T.PlaneGeometry(200,200),new T.MeshLambertMaterial({color:colors.ink}));floor.rotation.x=-Math.PI/2;floor.position.y=-2.3;floor.receiveShadow=true;scene.add(floor);
const shadowCanvas=document.createElement('canvas');shadowCanvas.width=256;shadowCanvas.height=256;const sc=shadowCanvas.getContext('2d'),sg=sc.createRadialGradient(128,128,10,128,128,123);sg.addColorStop(0,'rgba(0,0,0,.45)');sg.addColorStop(1,'rgba(0,0,0,0)');sc.fillStyle=sg;sc.fillRect(0,0,256,256);const contactShadow=new T.Mesh(new T.PlaneGeometry(6.8,4.4),new T.MeshBasicMaterial({map:new T.CanvasTexture(shadowCanvas),transparent:true,depthWrite:false}));contactShadow.rotation.x=-Math.PI/2;contactShadow.position.y=-2.29;scene.add(contactShadow);
const textureLoader=new T.TextureLoader();
const cover=await textureLoader.loadAsync('/game.png');
const font=new FontFace('SunsetGeist','url(/Geist.ttf)');await font.load();document.fonts.add(font);
function canvasTexture(draw){const c=document.createElement('canvas');c.width=1024;c.height=768;draw(c.getContext('2d'),c);const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;return t}
const packTexture=canvasTexture((c)=>{c.fillStyle='#f4f0e8';c.fillRect(0,0,1024,768);c.drawImage(cover.image,765,203,390,196,38,38,948,476);c.fillStyle='#173f31';c.font='650 64px SunsetGeist';c.fillText('The Lantern Trail',52,606);c.fillStyle='#9f542f';c.font='450 24px SunsetGeist';c.fillText('A PUBLIC LEARNING PACK',54,671);c.fillStyle='#173f31';c.font='450 20px SunsetGeist';c.fillText('KEEP A COPY. PLAY OFFLINE.',54,712)});
const credentialTexture=canvasTexture((c)=>{c.fillStyle='#10241c';c.fillRect(0,0,1024,768);c.fillStyle='#d9633a';c.beginPath();c.arc(142,135,65,Math.PI,0);c.fill();[0,1,2].forEach(i=>c.fillRect(82+i*13,148+i*21,120-i*26,8));c.fillStyle='#f2eadb';c.font='650 73px SunsetGeist';c.fillText('STEWARDSHIP',74,346);c.font='480 34px SunsetGeist';c.fillText('THE LANTERN TRAIL',78,423);c.fillStyle='#d8ab71';c.font='430 26px SunsetGeist';c.fillText('MIRROR MAINTENANCE',78,611);c.fillText('01 / SUNSET',78,682);c.fillStyle='#47614c';c.fillRect(78,514,866,2)});
function roundedShape(w,h,r){const s=new T.Shape(),x=-w/2,y=-h/2;s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);s.lineTo(x+w,y+h-r);s.quadraticCurveTo(x+w,y+h,x+w-r,y+h);s.lineTo(x+r,y+h);s.quadraticCurveTo(x,y+h,x,y+h-r);s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);return s}
function roundedGeometry(w,h,depth,r=.18){const g=new T.ExtrudeGeometry(roundedShape(w,h,r),{depth,steps:1,bevelEnabled:true,bevelSegments:4,bevelSize:.055,bevelThickness:.055,curveSegments:14});g.translate(0,0,-depth/2);return g}
function card(texture,w=3,h=2.24,depth=.14,material=silver){const g=new T.Group(),body=new T.Mesh(roundedGeometry(w,h,depth),material);body.castShadow=true;body.receiveShadow=true;g.add(body);const face=new T.Mesh(new T.PlaneGeometry(w-.16,h-.16),new T.MeshBasicMaterial({map:texture}));face.position.z=depth/2+.06;g.add(face);return g}
function sun(material=copper){const g=new T.Group(),s=new T.Shape();s.moveTo(-1,0);s.absarc(0,0,1,Math.PI,0,true);s.lineTo(-1,0);const geo=new T.ExtrudeGeometry(s,{depth:.18,steps:1,bevelEnabled:true,bevelSegments:5,bevelSize:.035,bevelThickness:.04,curveSegments:40});geo.translate(0,0,-.09);const dome=new T.Mesh(geo,material);dome.castShadow=true;g.add(dome);[1.9,1.42,.78].forEach((w,i)=>{const b=new T.Mesh(roundedGeometry(w,.11,.18,.055),material);b.position.y=-.26-i*.27;b.castShadow=true;g.add(b)});return g}
const all=[];function group(){const g=new T.Group();scene.add(g);all.push(g);return g}
const sunStage=group(),sunMark=sun();sunStage.add(sunMark);
const sunHalo=new T.Mesh(new T.TorusGeometry(1.6,.065,16,128,Math.PI*1.88),silver);sunHalo.rotation.x=.32;sunStage.add(sunHalo);
const escrowStage=group(),escrowOrb=new T.Mesh(new T.SphereGeometry(1.3,64,40),glass);escrowStage.add(escrowOrb);
const escrowSun=sun(gold);escrowSun.scale.setScalar(.58);escrowSun.position.set(0,.1,0);escrowStage.add(escrowSun);
const halo=new T.Mesh(new T.TorusGeometry(1.7,.12,24,160,Math.PI*1.93),gold);halo.rotation.set(.6,.1,.1);escrowStage.add(halo);
const coins=[];for(let i=0;i<12;i++){const m=new T.Mesh(new T.CylinderGeometry(.17,.17,.075,32),i%3?copper:silver);m.rotation.x=Math.PI/2;escrowStage.add(m);coins.push(m)}
const packStage=group(),pack=card(packTexture,3,2.24,.13,porcelain);packStage.add(pack);
const shellBack=new T.Mesh(roundedGeometry(3.42,2.66,.25,.28),jade);shellBack.position.z=-.25;packStage.add(shellBack);
const shellFront=new T.Mesh(roundedGeometry(3.42,2.66,.20,.28),silver);shellFront.position.z=.26;packStage.add(shellFront);
const shellMark=sun(copper);shellMark.scale.setScalar(.45);shellMark.position.set(0,.1,.37);shellFront.add(shellMark);
const packBand=new T.Mesh(new T.TorusGeometry(2.15,.09,16,128,Math.PI*1.6),gold);packBand.rotation.set(.35,.2,.2);packStage.add(packBand);
const copiesStage=group(),copies=[];for(let i=0;i<9;i++){const c=card(packTexture,2.55,1.9,.11,i%2?porcelain:silver);copiesStage.add(c);copies.push(c)}
const credentialStage=group(),credential=card(credentialTexture,3.7,2.77,.28,silver);credentialStage.add(credential);
const credentialBackSun=sun(copper);credentialBackSun.scale.setScalar(.58);credentialBackSun.position.set(0,.05,-.205);credentialBackSun.rotation.y=Math.PI;credential.add(credentialBackSun);
const authorityRing=new T.Mesh(new T.TorusGeometry(.54,.065,24,96,Math.PI*1.8),gold);credentialStage.add(authorityRing);
const routeA=new T.Mesh(new T.SphereGeometry(.15,24,16),gold),routeB=new T.Mesh(new T.SphereGeometry(.15,24,16),silver);credentialStage.add(routeA,routeB);
const quietStage=group();for(let i=0;i<3;i++){const r=new T.Mesh(new T.TorusGeometry(1.7+i*.6,.035,12,128,Math.PI*1.85),i%2?silver:gold);r.position.set((i-1)*6,0,-4-i);r.rotation.set(.6*i,1.2,.2);quietStage.add(r)}
function visible(g){g.visible=true;return g}
function pose(g,p=[0,0,0],r=[0,0,0],s=1){g.position.set(...p);g.rotation.set(...r);g.scale.setScalar(s)}
function cam(from,to,target,fov,t){camera.position.set(...vec(from,to,ease(t)));camera.fov=fov;camera.lookAt(...target);camera.updateProjectionMatrix()}
function reset(light=false){for(const g of all){g.visible=false;pose(g)}const bg=light?colors.cream:colors.ink;scene.background=new T.Color(bg);scene.fog=new T.FogExp2(bg,light?.025:.065);floor.material.color.set(bg);floor.visible=true;key.intensity=light?2.5:3.5;renderer.toneMappingExposure=light?.95:1.1}
window.renderFrame=function(t){
 t=Math.max(0,Math.min(23.999999,t));reset(t<1.6||t>=21.6);
 if(t<1.6){
  const u=t/1.6;visible(sunStage);pose(sunStage,[0,.12,0],[.1,-.35+u*.5,-.04+u*.1],.20+3.6*ease((u-.15)/.85));sunHalo.rotation.z=t*1.1;sunHalo.visible=u>.32;cam([0,0.5,8],[1.6,.7,7],[0,.1,0],35,u);floor.visible=false;
 }else if(t<4.8){
  const u=(t-1.6)/3.2;visible(escrowStage);pose(escrowStage,[0,.15,0],[.08,-.25+u*.7,0]);escrowSun.rotation.y=t*.38;halo.rotation.z=t*.45;for(let i=0;i<coins.length;i++){const k=clamp((u-i*.035)/.7),a=i*Math.PI*2/coins.length+t*.4,r=lerp(3.2,1.05,ease(k));coins[i].position.set(Math.cos(a)*r,Math.sin(a)*r*.65,Math.sin(i*1.8)*1.3*(1-k));coins[i].rotation.z=t*1.7+i}cam([-3,1.7,8.2],[3,.4,5.4],[0,.05,0],37,u)
 }else if(t<8.8){
  const u=(t-4.8)/4;visible(packStage);pose(packStage,[0,.15,0],[.16+Math.sin(u*Math.PI)*.1,-.48+u*.7,-.12+u*.16]);const o=ease((u-.12)/.55);shellBack.position.set(-.28*o,-.18*o,-.25-o*.55);shellBack.rotation.y=-o*.2;shellFront.position.set(o*1.8,o*1.3,.26+o*1.4);shellFront.rotation.set(o*.45,o*.95,-o*.18);shellFront.scale.setScalar(1-o*.15);shellFront.visible=u<.83;pack.position.set(-.1*o,.12*o,.45*o);pack.rotation.y=-.12+u*.2;packBand.rotation.z=t*.6;packBand.rotation.y=.2+u*.3;cam([1.4,1.1,8.9],[-1.15,.2,5.7],[0,.15,0],36,u)
 }else if(t<9.6){
  const u=(t-8.8)/.8;visible(packStage);pose(packStage,[0,.05,0],[.1,.25+u*.5,.04],1+u*.35);shellFront.visible=false;shellBack.position.set(-.28,-.18,-.8);pack.position.set(0,.1,.45);pack.rotation.y=.1;packBand.visible=true;packBand.rotation.set(.35,u*.6,t);cam([-.8,.2,5.5],[1.8,.7,2.3],[0,.1,0],39,u)
 }else if(t<12.6){
  const u=(t-9.6)/3;visible(quietStage);pose(quietStage,[0,0,-2],[0,u*.15,0]);for(let i=0;i<quietStage.children.length;i++)quietStage.children[i].rotation.z=t*.3+i;cam([0,.5,8],[.5,.3,8.7],[0,0,0],38,u);floor.visible=false
 }else if(t<15.8){
  const u=(t-12.6)/3.2;visible(copiesStage);for(let i=0;i<copies.length;i++){const a=i*2.39996+u*.45,spread=ease((u-i*.025)/.8),radius=(i?1.25+Math.sqrt(i)*1.5:0)*spread;pose(copies[i],[Math.cos(a)*radius,Math.sin(a)*radius*.62+(i%3-1)*.15,Math.sin(i*2)*.6-i*.28*spread],[-.12+Math.sin(t+i)*.08,Math.cos(a)*.45+u*.35,(i%2?1:-1)*(.08+i*.025)*spread],1);copies[i].visible=true}cam([1.6,1.5,8.2],[-2.6,.7,9.4],[0,0,-.5],40,u)
 }else if(t<19.6){
  const u=(t-15.8)/3.8;visible(credentialStage);const hand=smooth((u-.3)/.48);pose(credentialStage,[lerp(-1.2,1.15,hand),.18+Math.sin(u*Math.PI)*.22,0],[.12,lerp(-.5,.4,hand)+Math.sin(u*Math.PI)*.2,-.12+u*.2]);credential.rotation.y=(u<.3?Math.sin(u/.3*Math.PI)*.45:0);authorityRing.position.set(lerp(-2.4,2.4,hand),lerp(-.1,.35,hand),.7);authorityRing.rotation.set(.2,t*.2,-.3+t*.8);routeA.position.set(-2.7,-1.35,.1);routeB.position.set(2.7,-1.35,.1);routeA.material=u>.65?silver:gold;routeB.material=u>.65?gold:silver;cam([2.7,1.3,8.7],[-1.3,.6,7],[0,.1,0],36,u)
 }else if(t<21.6){
  const u=(t-19.6)/2;visible(sunStage);pose(sunStage,[0,.1,0],[.18,lerp(-1,.5,ease(u)),.1],2.4);sunHalo.visible=true;sunHalo.rotation.set(.2,.5,t*.65);cam([1.9,.7,5.7],[-1.7,.1,3.6],[0,.1,0],43,u);floor.visible=false
 }else{
  const u=(t-21.6)/2.4;visible(sunStage);pose(sunStage,[0,1.3,0],[0,-.2+.16*ease(u),0],.48);sunHalo.visible=false;cam([0,.65,8],[0,.65,8],[0,.35,0],35,0);floor.visible=false
 }
 packBand.visible=t>=4.8&&t<9.6;
 contactShadow.visible=floor.visible;contactShadow.position.x=t>=15.8&&t<19.6?credentialStage.position.x:0;
 renderer.render(scene,camera);renderer.getContext().finish();
 return {time:t,width:W,height:H,triangles:renderer.info.render.triangles,calls:renderer.info.render.calls};
};
window.sunsetSceneReady=true;window.renderFrame(0);
