# Stewardship and completion implementation plan

> **For agentic workers:** Use subagent-driven-development for the isolated contract and verification/document tasks; parent implements client integration. Execute authorized work continuously.

**Goal:** Add meaningful transferable maintenance rights and finish reproducible non-deployment product verification/handoff.
**Architecture:** Existing Rust contract gains a bounded NEP-171 steward token per released campaign; existing Next.js app gains verified mirror recovery and NFT rehearsal/plans. No new money product, dependencies or external resource provisioning.
**Tech Stack:** Rust direct NEAR host ABI/Borsh/Serde, native Node tests/Web Crypto, Next.js/TypeScript.
**Spec:** docs/superpowers/specs/2026-11-01-stewardship-design.md.

## Global constraints

Public access and committed funding/release/refund terms never depend on token ownership. NFT transfer uses exactly one yocto and native predecessor authority. No deployment/signing/provisioning. Keep local/live evidence separate. No new dependencies without a proven need. Keep all user data/backups safe and preserve old demo state.

## Review focus

Provisional receivers mutate rights then reject; former owner keeps mirror authority; malicious mirror redirects/oversize/corruption; mutable strings require unfunded storage; stale async UI operations act on different packs; client receipts confirm a different caller/action; payout/refund or public access changes on token transfer.

## Tasks

- [ ] Primary-source research and independent product/engineering challenge; save source limits.
- [ ] Contract failing tests → bounded token/metadata/events/transfer-call implementation → native and actual-Wasm host checks; independent review; commit.
- [ ] Client mirror/rights tests → strict mirror recovery and rehearsal NFT operations with legacy-state migration; unsigned plans for actual ABI; commit.
- [ ] Interface stewardship and transfer/recovery actions; integrate exact-pack verification; typecheck/build and review; commit.
- [ ] Reproducible end-to-end scenarios, browser/Sandbox availability evidence, threat model, demonstration/submission preparation and evidence/track matrix updates; commit.
- [ ] Run final required checks, verify source/Wasm identity and clean Git tree, refresh portable publication history; push only if existing GitHub access actually works.
