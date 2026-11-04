// Deterministic authored contact response. Real mesh affine deformation, not a soft-body solver.
export const DURATION=8,FPS=30,FLOOR_Y=0,SKIN=.004;
export const REST={
 'handbook-core':{kind:'roundedBox',core:[1.65,1,0],radius:.35},
 'handbook-cover':{kind:'roundedBox',core:[1.78,1.13,0],radius:.22},
 'sunset-seal':{kind:'roundedBox',core:[.37,.24,.03],radius:.28},
 'support-left':{kind:'roundedBox',core:[.25,.25,.25],radius:.25},
 'support-right':{kind:'roundedBox',core:[.25,.25,.25],radius:.25},
 'support-rear':{kind:'roundedBox',core:[.25,.25,.25],radius:.25}
};
export const clamp=x=>Math.max(0,Math.min(1,x));
export const smooth=x=>{x=clamp(x);return x*x*(3-2*x)};
export const move=(t,a,b)=>smooth((t-a)/(b-a));
export const mix=(a,b,q)=>a+(b-a)*q;
// A smooth, single compression then a small damped recovery overshoot. Exactly zero outside the event.
export function bump(t,a,b,c){return t<a||t>=c?0:t<b?smooth((t-a)/(b-a)):1-smooth((t-b)/(c-b))}
export function pressure(t,contact,amount){const u=t-contact;return amount*(bump(u,0,.14,.46)-.18*bump(u,.46,.62,.94))}
export function squash(axis,k){const scale=[1,1,1];scale[axis]=1-k;const bulge=1/Math.sqrt(1-k);for(let i=0;i<3;i++)if(i!==axis)scale[i]=bulge;return scale}
export function extent(rest,scale){return rest.core.map((v,i)=>(v+rest.radius)*scale[i])}
export function sampleState(time){
 const t=clamp(time/DURATION)*DURATION;
 const baseScale=[1,1,1],baseE=extent(REST['handbook-core'],baseScale);
 const coverScale=squash(2,pressure(t,.55,.16)),coverE=extent(REST['handbook-cover'],coverScale);
 const sealScale=squash(2,pressure(t,.55,.22)),sealE=extent(REST['sunset-seal'],sealScale);
 const leftScale=squash(0,pressure(t,2.9,.22)),leftE=extent(REST['support-left'],leftScale);
 const rightScale=squash(0,pressure(t,3.3,.22)),rightE=extent(REST['support-right'],rightScale);
 const rearScale=squash(2,pressure(t,3.7,.22)),rearE=extent(REST['support-rear'],rearScale);
 const coverZ=baseE[2]+coverE[2]+SKIN+1.65*move(t,6.1,6.5);
 const coverY=FLOOR_Y+coverE[1]+SKIN+3.0*move(t,6.5,7.3);
 const sealLift=2.9*move(t,5.3,5.9);
 // Seal approaches the actual current deformed cover support, then remains in contact until lifted.
 const sealZ=baseE[2]+2*coverE[2]+sealE[2]+2*SKIN+2.15*(1-move(t,0,.55));
 const sealY=FLOOR_Y+coverE[1]+SKIN+.15+sealLift;
 const bodies=[
  {id:'handbook-core',position:[0,FLOOR_Y+baseE[1]+SKIN,0],scale:baseScale},
  {id:'handbook-cover',position:[0,coverY,coverZ],scale:coverScale},
  {id:'sunset-seal',position:[.25,sealY,sealZ],scale:sealScale},
  {id:'support-left',position:[-(baseE[0]+leftE[0]+SKIN+4.8*(1-move(t,2.4,2.9))),FLOOR_Y+leftE[1]+SKIN,0],scale:leftScale},
  {id:'support-right',position:[baseE[0]+rightE[0]+SKIN+4.8*(1-move(t,2.8,3.3)),FLOOR_Y+rightE[1]+SKIN,0],scale:rightScale},
  {id:'support-rear',position:[0,FLOOR_Y+rearE[1]+SKIN,-(baseE[2]+rearE[2]+SKIN+4.8*(1-move(t,3.2,3.7)))],scale:rearScale}
 ].map(b=>({...b,rest:REST[b.id],rotation:[0,0,0]}));
 const macro=move(t,0,2.4),wide=move(t,2.4,5.3),handoff=move(t,6.2,8);
 const position=[mix(2.5,5.2,macro),mix(2.0,3.5,macro),mix(4.5,7.3,macro)];
 const side=move(t,2.4,3.65),back=move(t,3.65,5.3);
 for(let i=0;i<3;i++)position[i]=mix(position[i],[7.2,3.0,-1.4][i],side);
 for(let i=0;i<3;i++)position[i]=mix(position[i],[4.0,3.2,7.0][i],back);
 const final=[.15,1.65,5.5];for(let i=0;i<3;i++)position[i]=mix(position[i],final[i],handoff);
 const target=[mix(.25,0,macro),mix(1.5,1.3,macro),mix(.9,0,macro)];
 for(let i=0;i<3;i++)target[i]=mix(target[i],[0,1.35,.35][i],handoff);
 return {time:t,floorY:FLOOR_Y,bodies,camera:{position,target,near:.08,far:60,fov:mix(37,32,handoff),aspect:16/9},phrase:t>=2.6&&t<5.1?'Fund public knowledge.':null,phase:t<2.4?'shared-contact':t<5.3?'community-contacts':t<6.1?'seal-clears':'padded-cover-opens'};
}
// Each identity is an algebraic separation of certified supports. No group exemptions.
export const motionContract={duration:8,fps:30,contactSubstepHz:240,skin:SKIN,floorY:FLOOR_Y,
 deformation:'Affine volume-preserving squash; no shader displacement or inward dents. All solid meshes retain an inspectable CPU geometry.',
 curves:{smooth:'s(x)=3x^2-2x^3 on[0,1];clamped outside; |s_prime|<=1.5',pressure:{contact:[.55,2.9,3.3,3.7],maxCompression:.22,primary:[0,.14,.46],overshoot:{weight:-.18,window:[.46,.62,.94]},definition:'amount*(bump(u,0,.14,.46)-.18*bump(u,.46,.62,.94))'},volume:'scale_axis=1-k; other_two=(1-k)^(-1/2), determinant exactly1',bodyMotions:'sampleState source contains all anchors and curve parameters; no integration or hidden state'},
 bodyIds:Object.keys(REST),sameSolidComponents:[],
 floorAnchors:Object.keys(REST).map(id=>({id,formula:id==='sunset-seal'?'cy=floor+coverEy+skin+.15+sealLift; ey<=.588785 and coverEy>=1.330969; gap positive':id==='handbook-cover'?'cy=floor+ey+skin+3*move(6.5,7.3)':'cy=floor+ey+skin'})),
 pairCertificates:[
  {a:'handbook-core',b:'handbook-cover',axis:2,order:'b-a',skin:SKIN},
  {a:'handbook-core',b:'sunset-seal',axis:2,order:'b-a',skin:SKIN},
  {a:'handbook-cover',b:'sunset-seal',interval:[0,6.1],axis:2,order:'b-a',skin:SKIN},
  {a:'handbook-cover',b:'sunset-seal',interval:[6.1,6.5],axis:1,order:'b-a',skin:SKIN},
  {a:'handbook-cover',b:'sunset-seal',interval:[6.5,8],axis:2,order:'a-b',skin:SKIN},
  {a:'support-left',b:'handbook-core',axis:0,order:'b-a',skin:SKIN},
  {a:'support-right',b:'handbook-core',axis:0,order:'a-b',skin:SKIN},
  {a:'support-rear',b:'handbook-core',axis:2,order:'b-a',skin:SKIN},
  {a:'support-left',b:'handbook-cover',axis:0,order:'b-a',skin:SKIN},
  {a:'support-right',b:'handbook-cover',axis:0,order:'a-b',skin:SKIN},
  {a:'support-rear',b:'handbook-cover',axis:2,order:'b-a',skin:SKIN},
  {a:'support-left',b:'sunset-seal',axis:0,order:'b-a',skin:SKIN},
  {a:'support-right',b:'sunset-seal',axis:0,order:'a-b',skin:SKIN},
  {a:'support-rear',b:'sunset-seal',axis:2,order:'b-a',skin:SKIN},
  {a:'support-left',b:'support-right',axis:0,order:'b-a',skin:SKIN},
  {a:'support-left',b:'support-rear',axis:0,order:'b-a',skin:SKIN},
  {a:'support-right',b:'support-rear',axis:0,order:'a-b',skin:SKIN}
 ],
 speedBoundDerivation:'smooth translation <=1.5*distance/duration; |k_prime|<=1.5*.22/.14; |bulge_prime|<=.5*.78^(-1.5)*|k_prime|. Bounds below conservatively sum centre and maximum local-hull vertex speed.',
 worldSurfaceSpeedBounds:{'handbook-core':0,'handbook-cover':24,'sunset-seal':30,'support-left':22,'support-right':22,'support-rear':22},cameraSpeedBound:16,cameraTargetSpeedBound:4,
 contacts:[{time:.55,pair:['handbook-cover','sunset-seal'],cause:'Approach stops at shared normal support; both padded bodies compress and rebound.'},{time:2.9,pair:['handbook-core','support-left']},{time:3.3,pair:['handbook-core','support-right']},{time:3.7,pair:['handbook-core','support-rear']}]
};
