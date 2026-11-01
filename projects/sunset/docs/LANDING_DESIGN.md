# Public landing and workspace visual refresh

Requested: a proper landing page and a substantially stronger interface. The previous root opened directly into a dense workspace. The new root is a static, editorial introduction; the application remains at `/app/`.

Direction: warm paper, deep green, terracotta, large expressive type and a custom sculptural book/sunset hero. Locally hosted Geist handles interface/body text; system Georgia provides editorial emphasis. Artwork is project-local WebP (approximately 107 KB); the font is approximately 29 KB with its OFL text retained. Resource covers are native SVG. No remote font, image service, UI dependency, analytics or wallet connection is needed to load the landing.

The page explains the product through a clear hero, actual sample scenarios, a three-step mechanism, creator guidance, stewardship, native FAQ disclosures and repeated useful entry points. No testimonials, adoption figures, live funding claims or registered-trademark symbols were invented. Prototype and sample-funding disclosures are at least 12px and use a contrast pair measured at 5.27:1. Essential step/body text and final CTA copy were darkened to pass normal-text contrast.

The workspace uses the same palette with a deep-green navigation rail, larger copy and metadata, 44–48px controls, roomier panels and responsive navigation/card layouts. CSS is scoped so its controls do not affect the public landing. Monetary/cryptographic/state transitions remain unchanged.

Homepage links use allowlisted `view` values and existing campaign IDs. Existing same-origin browser data keeps the `sunset-rehearsal-v1` key/schema. The export enables trailing slashes so the included Python static server resolves `/app/` as `out/app/index.html`. A small About SUNSET link returns from the workspace to the landing.

Validation: production export, TypeScript, existing application/compiled-Wasm checks, PostCSS parsing and static page/asset/deep-link checks. The checker was also shown to reject missing rendered headings, changed Creator studio links and missing font files in a temporary export copy. These checks do not substitute for a browser screenshot or interaction test. Browser/server startup remains blocked by OS socket restrictions; no visual browser QA, deployment or successful GitHub push is claimed.

[Hero asset and exact generation prompt](../public/images/README.md) · [Geist license](../public/fonts/OFL-Geist.txt) · [Current product](../README.md)
