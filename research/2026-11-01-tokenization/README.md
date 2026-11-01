# SUNSET tokenization and completion record

**Implemented decision:** add one transferable stewardship NFT for each successfully released resource. Its holder maintains the preferred recovery mirror for the original committed manifest/ciphertext. Public access, CC0 rights, content hashes and financial beneficiaries remain independent of token ownership.

- [Primary-source research and alternatives](RESEARCH.md): copyright/revenue shares, prepaid vouchers, receipts, stewardship, NEP-171/177/181 and event fit.
- [Independent contract review](CONTRACT_REVIEW.md): real source and compiled-Wasm behavior, callback/reacquisition limits and final artifact identity.
- [Independent client review](CLIENT_REVIEW.md): context binding, private backup handling, signer evidence and resource-specific navigation.
- [Browser/protocol availability assessment](VERIFICATION_GAPS.md): exact OS/runtime blockers and runnable remaining checks.
- [Current product](../../projects/sunset/README.md), [demonstration](../../projects/sunset/docs/DEMO.md), [threat model](../../projects/sunset/docs/THREAT_MODEL.md), [verification evidence](../../projects/sunset/evidence/verification.json).

The research supports a specific maintenance handover, not a token economy or proof of demand. A simple reassigned maintainer account could provide the same basic capability; standard NFT ownership adds transfer and discovery interoperability. Creator/library feedback is still required to establish whether that is useful. Revenue/copyright fractions would change the product; a service voucher requires its own real fulfillment lifecycle. Those were not added as decorative track entries.

The Rust implementation includes core transfer/transfer-call/private resolution, metadata, enumeration and events. One-yocto security deposits have their own reserve and token recipients do not consume contributor slots. Owner and mirror storage is funded at campaign creation. Every ownership change resets the mirror to the immutable original; a different current owner's transfer is preserved by an earlier callback. Reference-standard caveat: an original receiver that reacquires the token before its old callback can still have it returned. No nonce-based stronger guarantee is claimed.

The client can recover a released resource from an explicitly selected mirror, checking raw manifest hash, fixed ciphertext path, encrypted bytes, public key, plaintext and supplied onchain license commitment before exposing playable data. It omits credentials/referrers and rejects redirects and oversized bodies. This is explicit browser retrieval, not a server proxy or DNS-rebinding defense. Retained files and prior schema-1 backups remain independently recoverable.

## Updated track assessment

These are evidence-based product candidates, not organizer acceptance or live-token claims. The [official event](https://nearhackathon.com/) and [NFT prompt](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/tracks/10-nfts.md) support evaluating ownership with actual behavior. Full details and the limits of the source review are in RESEARCH.md.

| Track | Current decision |
| --- | --- |
| Open Innovation | Primary: inspectable public-resource sponsorship, release/refund and independent reuse. |
| Social Money | Primary: shared funding for a public outcome with fixed terms and recovery. Actual independent participants still needed for a live story. |
| NFTs That Do Something | New substantive candidate: standard ownership transfers exclusive maintenance authority while the resource stays public. Actual protocol/transfer demonstration remains a gate. |
| Real-World Money | Conditional: needs real creator payout/refund/withdrawal evidence and a useful adult sponsor/creator case. |
| Agent Economy | Do not claim from local unsigned policy plans. |
| AI Swarms | Do not claim without consequential settlement by independently bounded participants. |
| AI Security & Defense | Do not claim from a local rejection button; real agent authority is not implemented. |
| Autonomous Business | Do not claim: no autonomous useful seller/service/revenue operation. |
| Privacy & Private AI | Do not claim: offline learner privacy and encryption do not establish private inference. |
| Games With Real Economies | Do not claim: arithmetic gameplay has no player economic system. |
| Unstoppable DeFi | Do not claim: escrow is not a trading/lending protocol. |
| Memecoins With Mechanics | Do not claim: no fungible currency is needed or implemented. |
| Investment Thesis | Do not claim: this is a resource-release product, not an investment research deliverable. |

## Work completed without deployment

Research, product decisions, independently reviewed contract and client code, resource-stewardship UI, safe unsigned transaction planning, public-resource recovery UI, exact file preparation/recovery, nine cross-module local scenarios, source/artifact checks, canonical path-remapped Wasm build, prepared CI configuration, demonstration guide, threat model, arithmetic review and an unsubmitted preparation draft.

Independent review fixed same-account creator/reviewer acceptance, mutable URI normalization and local-host suffix issues, stale receipt/backup context, signer binding, contract-call result interpretation and wrong-resource maintenance navigation. Builds/tests are recorded in maintained evidence rather than inferred from the presence of code.

No hosting, provider, account or contract deployment, signing, external social post or submission was performed. The OS refuses TCP/Unix sockets and no NEAR runtime binary is available. Accordingly real browser/offline execution, CORS delivery, protocol receipts/gas, independent educator review and real sponsor demand remain unverified. Git commits preserve the work; GitHub publication remains blocked by the existing account/connector access issue.
