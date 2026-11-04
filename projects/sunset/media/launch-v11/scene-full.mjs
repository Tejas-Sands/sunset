// New continuation wrapper; the approved proof scene, motion and capture sources stay intact.
import './scene.mjs';
import {sampleState,motionContract,REST} from './motion-full.mjs';
const api=window.sunsetV11,{scene,renderer,camera,bodies,outputCanvas,overlayCanvas}=api;
const template=bodies.find(b=>b.id==='handbook-core');
for(const id of ['copy-left','copy-right']){
 const mesh=template.mesh.clone();mesh.geometry=template.mesh.geometry.clone();mesh.name=id;
 mesh.userData={renderKind:'solid'};mesh.castShadow=true;mesh.receiveShadow=true;scene.add(mesh);
 bodies.push({id,geometryId:id+'-geometry',mesh,rest:REST[id],restGeometry:mesh.geometry,boundsShape:REST[id]});
}
const composite=outputCanvas.getContext('2d'),W=1920,H=1080;
api.sampleState=sampleState;api.motionContract=motionContract;
window.renderFrame=t=>{
 const state=sampleState(t);api.applyState(state);renderer.render(scene,camera);
 const gl=renderer.getContext();gl.finish();composite.clearRect(0,0,W,H);composite.drawImage(renderer.domElement,0,0);composite.drawImage(overlayCanvas,0,0);
 const d=gl.getExtension('WEBGL_debug_renderer_info');
 return {time:t,width:W,height:H,pixelRatio:renderer.getPixelRatio(),drawingBufferWidth:gl.drawingBufferWidth,drawingBufferHeight:gl.drawingBufferHeight,actual_context_antialias:gl.getContextAttributes().antialias,actual_samples:gl.getParameter(gl.SAMPLES),triangles:renderer.info.render.triangles,calls:renderer.info.render.calls,phase:state.phase,webgl_renderer:d?gl.getParameter(d.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),webgl_version:gl.getParameter(gl.VERSION),state,essential_text:api.getRenderElements().filter(e=>e.essential)};
};
window.renderFrame(8);window.sunsetFullSceneReady=true;
