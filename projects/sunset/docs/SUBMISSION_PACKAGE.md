# SUNSET final submission package

Prepared **9 November 2026**. The operator accepted the launch film; the project has **not been submitted**. Submit by **14 November, 23:59 UTC / 15 November, 05:29 IST**. [Official rules](https://nearhackathon.com/HACKATHON.md) and the [submission guide](SUBMISSION.md) govern the final send.

## Ready to review

- Public repository: <https://github.com/Tejas-Sands/sunset>. Anonymous GitHub HTML confirmed the repository is public on 9 November, at commit `22fe1a4ba393e772ada8138f0fec0ed91153ef14`. The operator must push the final local commits and confirm that the published branch updates before sending.
- Website: <https://sunset-lemon.vercel.app>. Recheck the deployed version and live recovery from the operator’s browser; a fresh HTTP check returned 200 on 9 November, but interactive browser/RPC verification could not run here. The deployed JavaScript chunk identities differ from the current local build.
- Accepted MP4: `.publication/sunset-final/sunset-launch.mp4`, 44.667 seconds, 1080p30, 23,121,135 bytes. SHA-256 `57348b1f7fea925c31b61650808bcc65f47b70d74b1889831674e8bb2e48022f`. [Source, licenses and verification](../media/launch/README.md).
- [Anchor-post draft](../media/launch/x-post.txt): upload the movie natively. Add the [music-credit reply](../media/launch/x-reply-credits.txt). These are drafts for the human to publish.
- Genuine 3 November screenshots remain at `.publication/sunset-e2e-2026-11-03/browser/03-hosted-pinned-reader.png` and `06-cold-offline-completion.png`. They show the pinned testnet reader and completed downloaded game. Attach them to a proof reply and label them with that date; they are not new screen recordings.

For a stronger action-to-result demonstration, the human can record the read-only path below in a short proof reply. Keep the accepted launch film intact. No new funding, release, payout, refund or NFT transaction is needed.

## Three-minute judge path

1. Open `/app/`, choose **Testnet setup**, and verify `sunset.shiftultra.testnet` against code hash `9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx`. Inspect `lantern-trail-testnet-v1` as Released.
2. Under **Public resources**, recover the original or steward-selected mirror. The commitments must verify before play/export. Answer **12** to the first question and see **A little brighter!**
3. Download the standalone HTML, open that file in a fresh browser with browser networking disabled before load, and finish the five questions. See **All 5 lanterns are lit.** No learner wallet or account is needed.
4. Inspect the [release/payout/stewardship receipts](../evidence/testnet-showcase.json) and [both actual expiry refunds](../evidence/testnet-refunds.json). These completed testnet actions must not be rerun.

All demonstration roles share one operator and both mirror paths share a host. Browser financial controls are local rehearsal or unsigned plans. Protocol failure/max-state gas, Sandbox, independent users, broad physical-device/accessibility QA and mainnet readiness are unverified. The practical workshop kit in the film is a separate illustrative resource, not the content paid for in the Lantern Trail receipts.

## Proposed project description

SUNSET helps communities make useful lessons and practical guides free while compensating their creators. Adults pool capped sponsorship for a precisely committed public release. A Rust contract on NEAR testnet holds escrow: a matching key published on time credits the fixed creator, while missed funding or release deadlines allow contributor refunds. Payment and refund claims use separate withdrawals. Readers verify the resource and keep a self-contained file without an account or wallet. A transferable stewardship NFT hands over verified mirror-maintenance authority without gating content or changing creator compensation. The recorded testnet showcase completed release, native creator payout, stewardship handover and both expiry-refund paths; browser evidence records original/mirror recovery and offline completion. All roles share one operator. Demand, independent adoption, protocol failure/max-state behavior and mainnet readiness are not established.

Candidate tracks: **`open`, `social`, `nfts`**. The human confirms the final selection and description. `realworld` needs a defensible real-business use case and demand evidence beyond testnet settlement.

## Final human inputs and send

Provide the lead name, email, exact team-size option, final tracks, mainnet prize account ID and public X-post URL. Confirm the project name, repository and description. Personal details may be saved in ignored `projects/sunset/private/submission-contact.json`; do not commit them. Supply account IDs only, never keys or recovery phrases.

Read this notice before recording agreement:

> I agree that the organizers may use these details to review our submission and contact us about this hackathon.

[SUBMISSION_DRAFT.json](SUBMISSION_DRAFT.json) deliberately keeps missing fields null. It is not an API payload. Once complete, prepare the exact eleven-field payload privately, generate and retain one UUID, show the complete payload to the human and receive explicit approval before sending it. The official `demoUrl` is the public **X-post URL**. Do not add a `website` field. A 201 response is the evidence of submission; saved entries use the human [request-changes page](https://nearhackathon.com/request-changes), never a second submission.

From the repository root, the operator publishes the verified local commits with:

```sh
git --git-dir=.sunset-git --work-tree=. push origin main
```

Keep the repository public through judging and the hosted demo available through 18 November, ideally 25 November.
