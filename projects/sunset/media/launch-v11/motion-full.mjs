// Separate continuation. The approved eight-second proof sources remain unchanged.
import {sampleState as proofState,REST as PROOF_REST,extent,squash,pressure,move,mix,bump,motionContract as proofContract} from './motion.mjs';
export {extent};
export const DURATION=34,FPS=30,FLOOR_Y=0,SKIN=.004;
export const REST={...PROOF_REST,'copy-left':PROOF_REST['handbook-core'],'copy-right':PROOF_REST['handbook-core']};
export const CAMERA_KEYS=[
 [8,[.15,1.65,5.5],[0,1.35,.35],32],
 [10.5,[4,3.9,8.2],[0,1.2,0],36],
 [11.5,[-1.8,3.2,6.5],[-1.8,1.8,.4],34],
 [13.2,[-3.8,1.75,5.2],[-3.5,.45,.5],34],
 [15.4,[-3.2,2.4,7],[-1.6,1.2,0],36],
 [19,[4.2,4.5,9.2],[0,1.3,-.5],38],
 [24,[.4,3.8,9.4],[0,1.35,0],36],
 [27.6,[.15,4,14.5],[0,1.35,0],40],
 [30,[.15,3.1,13.4],[0,1.35,0],40],
 [34,[.15,3.1,13.4],[0,1.35,0],40]
];
function cameraAt(t){
 let a=CAMERA_KEYS[0],b=a;
 for(let i=1;i<CAMERA_KEYS.length;i++){b=CAMERA_KEYS[i];if(t<=b[0])break;a=b}
 const q=a===b?0:move(t,a[0],b[0]);
 return {position:a[1].map((v,i)=>mix(v,b[1][i],q)),target:a[2].map((v,i)=>mix(v,b[2][i],q)),fov:mix(a[3],b[3],q),aspect:16/9,near:.08,far:60};
}
export function sampleState(time){
 const t=Math.max(0,Math.min(DURATION,time)),s=proofState(Math.min(t,8));
 s.time=t;s.phrase=null;
 const copies=[['copy-left',-1,24,26.7],['copy-right',1,24.3,27]].map(([id,sign,a,land])=>{
  const scale=squash(1,pressure(t,land,.18)),e=extent(REST[id],scale);
  return {id,rest:REST[id],position:[sign*mix(12,4.5,move(t,a,land)),e[1]+SKIN+1.1*bump(t,a,(a+land)/2,land),0],scale,rotation:[0,0,0]};
 });
 if(t>8){
  const byId=Object.fromEntries(s.bodies.map(b=>[b.id,b])),cover=byId['handbook-cover'],seal=byId['sunset-seal'];
  // The already-open cover parks above the stage. It never returns through the page.
  cover.position[1]=mix(cover.position[1],8,move(t,8,10.5));
  // Seal clears horizontally while high above the core, then lands in a separate payout lane.
  seal.scale=squash(1,pressure(t,13.2,.22));const se=extent(seal.rest,seal.scale);
  seal.position[0]=mix(.25,-4.4,move(t,10.3,11.5));
  seal.position[1]=se[1]+SKIN+(4.404-(.52+SKIN))*(1-move(t,11.5,13.2));
  for(const [id,sign] of [['support-left',-1],['support-right',1]]){
   const b=byId[id];b.scale=squash(1,pressure(t,18.3,.22));const e=extent(b.rest,b.scale);
   // First retreat behind the book in the existing side lane, then move outward.
   b.position=[sign*mix(2.504+.05*move(t,8,8.6),6,move(t,16.3,18.3)),e[1]+SKIN+1.3*bump(t,15.4,16.7,18.3),-2*move(t,15.4,16.3)];
  }
  const rear=byId['support-rear'];rear.scale=squash(1,pressure(t,18.7,.22));const re=extent(rear.rest,rear.scale);
  rear.position=[0,re[1]+SKIN+1.1*bump(t,15.8,17.1,18.7),-mix(.854+.05*move(t,8,8.6),4.5,move(t,15.8,18.7))];
  s.camera=cameraAt(t);
 }
 s.bodies.push(...copies);
 s.phase=t<8?s.phase:t<10.5?'escrow-wide':t<13?'key-and-release':t<15.4?'creator-payout':t<19?'conditional-prerelease-refund':t<24?'genuine-ui-handoff':t<30?'retained-copies':'brand-handoff';
 return s;
}
export const motionContract={duration:DURATION,fps:FPS,contactSubstepHz:240,floorY:FLOOR_Y,skin:SKIN,
 deformation:'Inspectable CPU rounded-box geometry with affine volume-preserving squash; no shader displacement.',
 proofSource:'motion.mjs',proofContract,bodyIds:Object.keys(REST),sameSolidComponents:[],cameraKeys:CAMERA_KEYS,
 inventory:{persistent:Object.keys(REST),copies:'Both padded copies preexist at x=+/-12 outside the action; they approach in separate lanes at24s. Offscreen is allowed, physical camera clearance remains mandatory.'},
 contacts:[...proofContract.contacts,{time:13.2,pair:['sunset-seal','floor'],cause:'Creator-lane landing; vertical22% squash.'},{time:18.3,pair:['support-left','floor'],cause:'Conditional refund return landing.'},{time:18.3,pair:['support-right','floor'],cause:'Conditional refund return landing.'},{time:18.7,pair:['support-rear','floor'],cause:'Rear conditional refund return landing.'},{time:26.7,pair:['copy-left','floor'],cause:'Retained padded copy lands; vertical18% squash.'},{time:27,pair:['copy-right','floor'],cause:'Second retained padded copy lands; vertical18% squash.'}],
 phases:[{start:8,end:10.5,meaning:'Same open handbook; camera reveals sponsorship context.'},{start:10.3,end:13.2,meaning:'Seal routes high and left before landing in distinct creator lane.'},{start:15.4,end:19,meaning:'Conditional prerelease refund illustration. Each mint reverses through a reserved lane.'},{start:24,end:30,meaning:'Two real padded copies arrive after support lanes clear; no overlapping spawn.'}],
 continuation:{cover:{axis:1,from:4.354,to:8,interval:[8,10.5]},seal:{x:{from:.25,to:-4.4,interval:[10.3,11.5]},floorLanding:[11.5,13.2],z:1.108,compression:{axis:1,time:13.2,amount:.22}},mints:{sideInitialX:2.504,backoff:.05,zRetreat:{to:-2,interval:[15.4,16.3]},xRetreat:{to:6,interval:[16.3,18.3]},rearZ:{from:-.854,to:-4.5,interval:[15.8,18.7]}},copies:{x:{from:12,to:4.5},left:[24,26.7],right:[24.3,27],compression:{axis:1,amount:.18}}},
 renderHandoffs:[{start:19,end:24,kind:'opaque-genuine-handbook-ui'},{start:30,end:34,kind:'opaque-original-brand-endcard'}]
};
