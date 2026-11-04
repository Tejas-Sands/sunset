# Tactile 3D launch implementation plan

Goal: deliver the operator-requested spongy, dynamic 3D launch treatment with real contacts and no interpenetration.

Architecture: cached Three.js plus newly authored convex/puffy geometry, deterministic contact/deformation choreography and native frame capture. Independent geometry checks and a short visual feel test precede the full film. Existing handbook footage and licensed sound remain reusable.

Spec: [selected direction](DIRECTION.md).

- [x] Author new rounded matte/satin bodies, lighting and physical contact sequence; preserve handbook/brand identity.
- [x] Export live solid geometry/camera/pose state. Independently check post-deform floor/pair separation and dense motion with between-step bounds; investigate any contact or clipping failure.
- [x] Review native contact/material poses and12-frame throughput, then render8s native1080p/30fps. Inspect actual contact strips, changing compositions, camera clearance and legibility.
- [x] Extend the accepted motion treatment into a34s launch film with a short genuine handbook action/result, concrete NEAR mechanism and retained-copy payoff.
- [x] Mix licensed background/effects with no voice; native final encode with correct colour/codec tags, separate stems and clean brand landing.
- [x] Verify actual full decode, all-frame text/geometry/source identities/audio and old-film preservation. Independently review decoded movement, not merely metrics.
- [x] Update accurate delivery evidence/guide/ledger; make a verified local batch and provide the operator push command. No social post, submission or deployment.
