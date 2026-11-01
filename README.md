# NEAR hackathon — SUNSET

The selected product is now implemented locally. [Run SUNSET](projects/sunset/README.md), [read the council decision](research/2026-11-01-council/README.md), or [inspect verification evidence](projects/sunset/evidence/verification.json).

```sh
cd projects/sunset
npm run dev
```

Open http://127.0.0.1:3000. Dependencies are installed in this workspace; use `npm ci` on a fresh checkout. No model key or database is needed for the local rehearsal. A [standalone learning sample](projects/sunset/public/try-lantern-trail.html) is also included.

SUNSET pools adult sponsorship until a resource's creator is paid for public release, or contributors qualify for refunds. Learners keep a self-contained game without a wallet. The app clearly separates browser rehearsal from real NEAR settlement. The compiled Rust contract still needs protocol Sandbox and live testnet evidence; no hosted service or submission has been published.

Current targets: Open Innovation and Social Money. Real-World Money and agent tracks require additional real settlement evidence. [All thirteen tracks](research/2026-11-01-council/track-verification.md).

[Research archive](research/README.md) · [Candidates and selection](projects/README.md)
