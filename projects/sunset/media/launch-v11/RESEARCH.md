# Native 3D production notes

The operator explicitly chose soft, kinetic 3D objects with contact and no interpenetration. Existing local SaasWAVE references inform physical staging/camera travel; their footage is not an output asset. [Prior exact reference study](../launch-v4/RESEARCH.md).

Blender is absent from the available PATH/package/tool locations. The cached Three.js0.180 WebGL2 pipeline previously captured native1080 frames; its historical speed is a baseline, not a new performance measurement. Reuse transport/dependencies while replacing the old metal/glass staging and unconstrained trajectories.

Primary Three.js docs checked for this correction:

- [Box3](https://threejs.org/docs/pages/Box3.html): world-transformed object bounds and the precise option. Bounds must be computed after CPU deformation and world transforms; an undeformed/model-space box does not certify the rendered body.
- [MeshPhysicalMaterial](https://threejs.org/docs/pages/MeshPhysicalMaterial.html): non-metallic roughness, clearcoat and sheen options. Extra physical effects increase per-pixel cost, so the native throughput probe precedes full capture.
- [PerspectiveCamera](https://threejs.org/docs/pages/PerspectiveCamera.html): actual perspective and near-plane constraints.

Sponginess is authored analytic squash/stretch and damped recovery, with certified separation constraints. No full volumetric soft-body simulation or photographic path tracing is claimed. Independent inspection must distinguish proof of separation from subjective contact/weight/material quality.
