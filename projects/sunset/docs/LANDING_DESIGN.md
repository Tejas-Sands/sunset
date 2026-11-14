# Public landing and workspace visual refresh

Requested: a proper landing page and a substantially stronger interface. The previous root opened directly into a dense workspace. The new root is a static, editorial introduction; the application remains at `/app/`.

Direction: warm paper, deep green, terracotta, large expressive type and a custom sculptural book/sunset hero. Locally hosted Geist handles interface/body text; system Georgia provides editorial emphasis. Artwork is project-local WebP (approximately 107 KB); the font is approximately 29 KB with its OFL text retained. Resource covers are native SVG. No remote font, image service, UI dependency, analytics or wallet connection is needed to load the landing.

The page explains the product through a clear hero, actual sample scenarios, a three-step mechanism, creator guidance, stewardship, native FAQ disclosures and repeated useful entry points. No testimonials, adoption figures, live funding claims or registered-trademark symbols were invented. Prototype and sample-funding disclosures are at least 12px and use a contrast pair measured at 5.27:1. Essential step/body text and final CTA copy were darkened to pass normal-text contrast.

The workspace uses the same palette with a deep-green navigation rail, larger copy and metadata, 44–48px controls, roomier panels and responsive navigation/card layouts. CSS is scoped so its controls do not affect the public landing. Monetary/cryptographic/state transitions remain unchanged.

Homepage links use allowlisted `view` values and existing campaign IDs. Existing same-origin browser data keeps the `sunset-rehearsal-v1` key/schema. The export enables trailing slashes so the included Python static server resolves `/app/` as `out/app/index.html`. A small About SUNSET link returns from the workspace to the landing.

Validation: production export, TypeScript, existing application/compiled-Wasm checks, PostCSS parsing and static page/asset/deep-link checks. The checker was also shown to reject missing rendered headings, changed Creator studio links and missing font files in a temporary export copy. These checks do not substitute for a browser screenshot or interaction test. Browser/server startup remains blocked by OS socket restrictions; no visual browser QA, deployment or successful GitHub push is claimed.

## Interface revision, 14 November 2026

The landing, app and reader were redesigned without changing contract, wallet, ledger or content logic. The palette tokens and the approved SUNSET mark are unchanged.

- Type: Bricolage Grotesque (locally hosted variable WOFF2, about 77 KB, OFL text retained) sets headings; Geist stays for interface and body text. Uppercase tracked labels and decorative arrow glyphs were removed; sentence-case labels and one icon set replace them.
- Landing: the hero is an interactive release path. Its four steps (commit, fund, release, deadline missed) move a sun toward a goal line using the figures of the completed Lantern Trail showcase; on release the scene forms the SUNSET mark. The mechanism section states the two possible endings. No adoption figures or testimonials were added.
- App: compact page titles, a sticky tab bar that scrolls on small screens, and a chain status with block height beside the refresh action. Campaign rows show raised amount against goal, a progress bar and the deadline or outcome; an opened campaign shows its review, funding and release stages, including which deadline was missed. Empty states name the next useful action. Sponsor, withdraw and transaction-tracking forms keep their validation and add inline guidance. The studio shows its three steps and why the next action is unavailable.
- Reader: shorter line length, chapter previous/next controls and a checklist progress bar in the hosted reader. The offline export and its bytes are unchanged.

- Motion: one scale defined in `protocol.css`. Distances are 4px (text swaps), 8px (panels, notices, view changes), 16px (landing sections) and 24px (hero figure). Durations are 150ms (hover and press), 200ms (disclosures), 320ms (view change), 480ms (entrances) and 700ms (the sun's travel), with a 60ms stagger and one ease-out curve. The hero enters once on load; landing sections reveal once when scrolled into view; meters fill, campaign stages and opened panels ease in, and the refresh icon turns while the chain is read. Blocks are hidden for a reveal only after the script has started, entrances leave no transform behind, and reduced motion disables all of it.

Validation on 14 November: 109 unit tests, TypeScript, production export, `npm run check`, `npm run test:pages` and `npm run test:browser` passed locally, including the controlled wallet stage. That stage failed on the unmodified tree because a click could land while actions were disabled during a chain refresh; the smoke test now waits for the refresh before clicking. Screenshots were reviewed at 1440 and 390 pixels in both themes. No real wallet transaction, deployment or independent accessibility audit is claimed.

[Hero asset and exact generation prompt](../public/images/README.md) · [Geist license](../public/fonts/OFL-Geist.txt) · [Current product](../README.md)
