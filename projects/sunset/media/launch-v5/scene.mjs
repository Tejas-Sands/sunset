import * as T from '/three.module.js';

// Original scene geometry. Reference videos are never loaded as textures or footage.
const cfg=window.SUNSET_RENDER||{}, W=cfg.width||1920,H=cfg.height||1080;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});
renderer.setPixelRatio(1);renderer.setSize(W,H);renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.1;
renderer.shadowMap.enabled=false;document.body.append(renderer.domElement);
const scene=new T.Scene(),camera=new T.PerspectiveCamera(38,W/H,.05,100);
const colors={ink:'#111417',cream:'#f2efe8',coral:'#a14c31',amber:'#a78262',green:'#323d39'};
const clamp=v=>Math.max(0,Math.min(1,v)), ease=v=>1-(1-clamp(v))**3, smooth=v=>{v=clamp(v);return v*v*(3-2*v)}, lerp=(a,b,t)=>a+(b-a)*t;
const vec=(a,b,t)=>a.map((v,i)=>lerp(v,b[i],t));
const physical=(color,metalness=.8,roughness=.17)=>new T.MeshStandardMaterial({color,metalness,roughness});
const copper=physical(colors.coral,.48,.27),gold=physical(colors.amber,.75,.21),silver=physical('#a9acae',.88,.21),jade=physical('#28322f',.55,.24);
const porcelain=physical('#f2efe8',.12,.24),dark=physical('#394148',.24,.28);
const glass=new T.MeshPhysicalMaterial({color:'#afb9bc',metalness:.2,roughness:.07,transparent:true,opacity:.25,clearcoat:.8,side:T.FrontSide,depthWrite:false});
const environment=new T.Scene();environment.background=new T.Color('#51555a');
function panel(x,y,z,w,h,power,color='#ffffff'){const m=new T.MeshBasicMaterial({color:new T.Color(color).multiplyScalar(power),side:T.DoubleSide});const p=new T.Mesh(new T.PlaneGeometry(w,h),m);p.position.set(x,y,z);p.lookAt(0,0,0);environment.add(p)}
panel(-4,4,2,3,7,4);panel(4,2,-2,1,7,5);panel(0,6,0,6,4,2.8);panel(0,1,-5,6,1,2);panel(-2,-3,3,3,4,.2,'#b2917c');
const pmrem=new T.PMREMGenerator(renderer);scene.environment=pmrem.fromScene(environment,.025,.1,40).texture;pmrem.dispose();
const ambient=new T.AmbientLight('#d7d8d6',.55);scene.add(ambient);
const key=new T.DirectionalLight('#f6f4ef',3.2);key.position.set(-3,6,5);key.castShadow=true;key.shadow.mapSize.set(1024,1024);key.shadow.camera.left=-8;key.shadow.camera.right=8;key.shadow.camera.top=8;key.shadow.camera.bottom=-8;key.shadow.normalBias=.03;key.shadow.bias=-.0003;scene.add(key);
const rim=new T.DirectionalLight('#c2a48f',.85);rim.position.set(4,2,-4);scene.add(rim);
const frontFill=new T.DirectionalLight('#f4f3ef',2.2);frontFill.position.set(4,1.5,7);scene.add(frontFill);
const floor=new T.Mesh(new T.PlaneGeometry(200,200),new T.MeshLambertMaterial({color:colors.ink}));floor.rotation.x=-Math.PI/2;floor.position.y=-2.3;floor.receiveShadow=true;scene.add(floor);
const shadowCanvas=document.createElement('canvas');shadowCanvas.width=256;shadowCanvas.height=256;const sc=shadowCanvas.getContext('2d'),sg=sc.createRadialGradient(128,128,10,128,128,123);sg.addColorStop(0,'rgba(0,0,0,.45)');sg.addColorStop(1,'rgba(0,0,0,0)');sc.fillStyle=sg;sc.fillRect(0,0,256,256);const contactShadow=new T.Mesh(new T.PlaneGeometry(6.8,4.4),new T.MeshBasicMaterial({map:new T.CanvasTexture(shadowCanvas),transparent:true,depthWrite:false}));contactShadow.rotation.x=-Math.PI/2;contactShadow.position.y=-2.29;scene.add(contactShadow);
const textureLoader=new T.TextureLoader();
// The original product landscape is vector rasterized directly at 2048px;
// no screenshot is enlarged inside a texture.
const landscapeSvg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 300"><rect width="600" height="300" fill="#f4d6a7"/><circle cx="385" cy="125" r="73" fill="#f27344"/><path d="M0 220 90 155 160 210 270 137 390 226 500 176 600 216V300H0Z" fill="#7e8d6f"/><path d="M0 278 130 214 240 264 380 201 600 277v23H0Z" fill="#405c4e"/><path d="M280 300q-20-34 28-43t34-35q-2-15 24-22" fill="none" stroke="#ead7af" stroke-width="15"/><path d="M72 300v-81m-14 28 14-15 14 15m-26-6 12-16 12 16 M515 300v-76m-13 22 13-15 13 15" fill="none" stroke="#294a3f" stroke-width="5"/><g fill="#ffcb7a"><circle cx="307" cy="266" r="4"/><circle cx="328" cy="242" r="3"/><circle cx="346" cy="218" r="2"/></g><path d="M55 76h55m-38-8h31 M477 61h65m-51 9h40" stroke="#fff6e8" stroke-width="4" stroke-linecap="round"/></svg>';
const cover=await textureLoader.loadAsync('data:image/svg+xml;charset=utf-8,'+encodeURIComponent(landscapeSvg));
const font=new FontFace('SunsetGeist','url(/Geist.ttf)');await font.load();document.fonts.add(font);
function canvasTexture(draw){const c=document.createElement('canvas');c.width=2048;c.height=1536;draw(c.getContext('2d'),c);const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;t.anisotropy=renderer.capabilities.getMaxAnisotropy();return t}
const packTexture=canvasTexture(c=>{
 c.fillStyle=colors.cream;c.fillRect(0,0,2048,1536);
 c.fillStyle=colors.ink;c.font='550 48px SunsetGeist';c.fillText('SUNSET  /  PUBLIC RESOURCE',100,126);
 c.drawImage(cover.image,100,194,1848,924);
 c.fillStyle=colors.ink;c.font='650 112px SunsetGeist';c.fillText('The Lantern Trail',100,1280);
 c.fillStyle='#5a5d59';c.font='450 42px SunsetGeist';c.fillText('CC0  /  DOWNLOAD. KEEP. SHARE.',104,1420);
});
const credentialTexture=canvasTexture(c=>{
 c.fillStyle=colors.ink;c.fillRect(0,0,2048,1536);
 c.fillStyle=colors.cream;c.font='600 128px SunsetGeist';c.fillText('PUBLIC',132,520);c.fillText('BY DESIGN.',132,700);
 c.fillStyle='#bda088';c.font='450 56px SunsetGeist';c.fillText('ONE RELEASE. UNLIMITED COPIES.',136,1220);
});
function roundedShape(w,h,r){const s=new T.Shape(),x=-w/2,y=-h/2;s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);s.lineTo(x+w,y+h-r);s.quadraticCurveTo(x+w,y+h,x+w-r,y+h);s.lineTo(x+r,y+h);s.quadraticCurveTo(x,y+h,x,y+h-r);s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);return s}
function roundedGeometry(w,h,depth,r=.18){const g=new T.ExtrudeGeometry(roundedShape(w,h,r),{depth,steps:1,bevelEnabled:true,bevelSegments:4,bevelSize:.055,bevelThickness:.055,curveSegments:14});g.translate(0,0,-depth/2);return g}
function card(texture,w=3,h=2.24,depth=.14,material=silver){const g=new T.Group(),body=new T.Mesh(roundedGeometry(w,h,depth),material);body.castShadow=true;body.receiveShadow=true;g.add(body);const face=new T.Mesh(new T.PlaneGeometry(w-.16,h-.16),new T.MeshBasicMaterial({map:texture,toneMapped:false}));face.position.z=depth/2+.06;g.add(face);return g}
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
// Credit and refund are distinct object handoffs, not fabricated wallet UI.
const payoutStage=group();
const payoutTray=new T.Mesh(roundedGeometry(2.3,.18,.95,.09),dark);
payoutTray.rotation.x=Math.PI/2;payoutTray.position.set(1,-.95,0);payoutStage.add(payoutTray);
const payoutResource=card(packTexture,1.55,1.16,.1,porcelain);
payoutResource.position.set(-1.25,.15,-.25);payoutResource.rotation.set(.08,.2,-.05);payoutStage.add(payoutResource);
const payoutPuck=new T.Mesh(new T.CylinderGeometry(.36,.36,.12,64),copper);
payoutPuck.rotation.x=Math.PI/2;payoutStage.add(payoutPuck);
const payoutRail=new T.Mesh(new T.TorusGeometry(.76,.035,16,96,Math.PI*1.6),silver);
payoutRail.position.set(1,-.05,-.35);payoutRail.rotation.z=-.7;payoutStage.add(payoutRail);
const refundStage=group();
const refundClock=new T.Mesh(new T.TorusGeometry(1.26,.08,20,128),silver);refundClock.position.set(.55,.2,-.3);refundStage.add(refundClock);
const clockHand=new T.Mesh(new T.BoxGeometry(.055,.83,.06),copper);clockHand.position.y=.41;
const clockPivot=new T.Group();clockPivot.position.set(.55,.2,-.15);clockPivot.add(clockHand);refundStage.add(clockPivot);
const sponsorTray=new T.Mesh(roundedGeometry(1.6,.18,.85,.09),dark);sponsorTray.rotation.x=Math.PI/2;sponsorTray.position.set(-.7,-.9,.3);refundStage.add(sponsorTray);
const refundPuck=new T.Mesh(new T.CylinderGeometry(.33,.33,.12,64),copper);refundPuck.rotation.x=Math.PI/2;refundStage.add(refundPuck);
function visible(g){g.visible=true;return g}
function pose(g,p=[0,0,0],r=[0,0,0],s=1){g.position.set(...p);g.rotation.set(...r);g.scale.setScalar(s)}
function cam(from,to,target,fov,t){camera.position.set(...vec(from,to,ease(t)));camera.fov=fov;camera.lookAt(...target);camera.updateProjectionMatrix()}
function reset(light=false){for(const g of all){g.visible=false;pose(g)}const bg=light?colors.cream:colors.ink;scene.background=new T.Color(bg);scene.fog=new T.FogExp2(bg,light?.018:.018);floor.material.color.set(bg);floor.visible=true;key.intensity=light?2.5:3.5;renderer.toneMappingExposure=light?.95:1.1}
// 24s actual narration clock. Protected headline slab is x128..628 logical;
// key object faces settle on the right before each essential read.
window.renderFrame=function(t){
 t=Math.max(0,Math.min(23.999999,t));reset(false);
 packBand.visible=false;sunHalo.visible=false;
 if(t<3.2){
  const u=clamp(t/3.2),settle=ease(t/.48);visible(copiesStage);
  pose(copiesStage,[2.32,.17,0],[.06,-.22+.23*u,-.025],lerp(1.52,.94,settle));
  for(let i=0;i<copies.length;i++){
   copies[i].visible=i<4;
   const fan=smooth((t-.6)/1.6),k=i?i:0;
   pose(copies[i],[k*.22*fan,-k*.16*fan,-k*.31],[.02*k,-.07*k*fan,-.035*k*fan],1);
  }
  cam([.2,.45,7.8],[-.15,.25,8.2],[0,.08,0],37,u);floor.visible=false;
 }else if(t<7.8){
  const u=(t-3.2)/4.6;visible(escrowStage);pose(escrowStage,[2.35,.2,0],[.08,-.23+u*.4,0],lerp(1.16,.9,ease((t-3.2)/.38)));
  escrowSun.rotation.y=-.12+u*.55;halo.rotation.z=.22+u*.7;
  for(let i=0;i<coins.length;i++){
   const k=ease((u-i*.022)/.65),a=i*Math.PI*2/coins.length+u*.2,r=lerp(2.25,.82,k);
   coins[i].position.set(Math.cos(a)*r,Math.sin(a)*r*.75,Math.sin(i*1.8)*.8*(1-k));
   coins[i].rotation.set(Math.PI/2,.1,i+u*1.1);
  }
  cam([-.15,.5,8.4],[.25,.2,7.6],[0,.08,0],38,u);
 }else if(t<10.35){
  const u=(t-7.8)/2.55;visible(packStage);pose(packStage,[2.42,.15,0],[.1,-.25+.28*u,-.04],lerp(1.13,.88,ease((t-7.8)/.35)));
  const open=ease((u-.07)/.60);
  shellBack.position.set(-.16*open,-.12*open,-.25-open*.4);shellBack.rotation.y=-open*.12;
  shellFront.position.set(open*1.38,open*1.28,.26+open*.35);shellFront.rotation.set(open*.3,open*.85,-open*.12);
  shellFront.scale.setScalar(1-open*.17);shellFront.visible=u<.87;
  pack.position.set(-.08*open,.07*open,.34*open);pack.rotation.y=-.06+.07*u;
  packBand.visible=true;packBand.rotation.set(.35,.2+u*.1,.45+u*.65);
  cam([.1,.35,8.5],[-.1,.25,7.9],[0,.08,0],37,u);
  if(t<8.16){
   const handoff=smooth((t-7.8)/.36),settled=camera.position.clone();
   camera.position.set(...vec([2.85,.5,1.55],settled.toArray(),handoff));
   camera.fov=lerp(44,37,handoff);camera.lookAt(...vec([2.42,.15,.1],[0,.08,0],handoff));camera.updateProjectionMatrix();
  }
 }else if(t<13.0){
  const u=(t-10.35)/2.65;visible(payoutStage);pose(payoutStage,[2.42,.15,0],[.08,-.15+u*.25,0],lerp(1.17,.92,ease((t-10.35)/.28)));
  const travel=smooth((u-.08)/.68);
  payoutPuck.position.set(lerp(-1.25,1,travel),lerp(.6,-.52,travel)+Math.sin(travel*Math.PI)*.5,lerp(.55,.15,travel));
  payoutPuck.rotation.z=-.25+u*.5;payoutRail.rotation.z=-.7+u*.3;
  cam([-.2,.65,8.3],[.1,.3,7.8],[0,.08,0],37,u);
 }else if(t<16.2){
  const u=(t-13)/3.2;visible(refundStage);pose(refundStage,[2.45,.13,0],[.08,-.1+u*.15,0],lerp(1.24,.95,ease((t-13)/.28)));
  const expire=smooth((u-.02)/.4),back=smooth((u-.36)/.52);
  clockPivot.rotation.z=-expire*Math.PI*1.83;
  refundPuck.position.set(lerp(.55,-.7,back),lerp(-.27,-.5,back)+Math.sin(back*Math.PI)*.42,.47);
  refundPuck.rotation.z=.15+u*.45;
  cam([-.1,.55,8.5],[.18,.28,7.85],[0,.08,0],37,u);
  if(t<13.27){
   const handoff=smooth((t-13)/.27),settled=camera.position.clone();
   camera.position.set(...vec([3.7,1.3,1.85],settled.toArray(),handoff));
   camera.fov=lerp(47,37,handoff);camera.lookAt(...vec([2.96,.45,-.1],[0,.08,0],handoff));camera.updateProjectionMatrix();
  }
 }else if(t>=19.6&&t<21){
  const u=(t-19.6)/1.4;visible(sunStage);pose(sunStage,[3.25,.22,-.35],[.14,-.6+u*.48,.05],2.25);
  sunHalo.visible=true;sunHalo.rotation.set(.25,.3,.25+u*.25);
  cam([.2,.3,8.2],[-.15,.2,7.55],[0,.1,0],40,u);floor.visible=false;
 }else{floor.visible=false;}
 contactShadow.visible=floor.visible;contactShadow.position.x=2.35;
 renderer.render(scene,camera);const gl=renderer.getContext();gl.finish();const debug=gl.getExtension('WEBGL_debug_renderer_info');
 return {time:t,width:W,height:H,triangles:renderer.info.render.triangles,calls:renderer.info.render.calls,actual_context_antialias:gl.getContextAttributes().antialias,actual_samples:gl.getParameter(gl.SAMPLES),texture_dimensions:[2048,1536],webgl_renderer:debug?gl.getParameter(debug.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),webgl_version:gl.getParameter(gl.VERSION),viewport:gl.getParameter(gl.VIEWPORT)};
};
window.sunsetSceneReady=true;window.renderFrame(0);
