# SUNSET submission guide

Rules rechecked on **9 November 2026** against the [live organizer instructions](https://nearhackathon.com/HACKATHON.md). The [submission checklist](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/SUBMITTING.md) is a secondary overview; the live guide governs any difference. Recheck the live instructions before sending.

Submit by **14 November 2026, 23:59 UTC — 15 November, 05:29 IST**. There is no advance registration. Testnet projects are eligible; a paid domain is unnecessary for the existing hosted demo.

## Official submission steps

1. Publish the reviewed code, license and reproducible README in the [public repository](https://github.com/Tejas-Sands/sunset). Keep it public through judging. Check the repository history for secrets before publication.
2. The human publishes a public X demo with attached video or screenshots, the build-at-NEAR-HACKATHON statement, `@NEARProtocol` and `#NEARHackathon`. Include an actual action and visible result, NEAR's concrete role, and links to the [hosted demo](https://sunset-lemon.vercel.app) and repository.
3. Confirm the human fields below, select defensible tracks, then use the [final submission form](https://nearhackathon.com/#apply). An agent may instead use the [official API contract](https://nearhackathon.com/HACKATHON.md), after showing the complete payload and receiving explicit approval. One submission per project. Saved submissions cannot be edited directly; the human can [request organizer-reviewed corrections](https://nearhackathon.com/request-changes). Never resubmit the same project.

Keep the hosted demo up through 18 November, ideally 25 November, following the organizer's availability guidance.

## One anchor post, optional replies

A thread is optional. Recommended delivery: one public post with the launch video uploaded natively, the required event wording/tags, and demo/repository links. Use that post's URL as `demoUrl`. Optional replies can explain the testnet proof and stewardship token without turning the launch into a full setup tutorial. The website URL is not the submission's `demoUrl`.

Show native NEAR escrow, release/payout and a token that transfers mirror-maintenance authority. Learners keep the public resource without holding a token. Do not imply copyright ownership, revenue rights, mainnet settlement or independent adoption.

## Human fields and final send

[SUBMISSION_DRAFT.json](SUBMISSION_DRAFT.json) is preparation, not a sendable payload. Missing decisions are the lead's name, contact email, exact team-size option, final track selection, public X-post URL, mainnet prize account and consent. The existing `shiftultra.testnet` account is for the demonstration; it is not a mainnet prize-payout account. Supply account IDs only, never keys or recovery phrases.

Team-size options are exactly `1`, `2 - 4`, `4 - 6`, `6 - 8` or `8+`.

The API accepts exactly: `requestId`, `projectName`, `leadName`, `email`, `size`, `tracks`, `nearAddress`, `projectUrl`, `demoUrl`, `idea`, `consent`. Generate one request ID during final preparation and retain it for legitimate retries. Validate against the live contract; do not add a `website` field or commit the personal-data payload.

Read this contact notice verbatim before recording consent:

> I agree that the organizers may use these details to review our submission and contact us about this hackathon.

A 201 response confirms submission. If a saved submission needs correction, use the human [request-changes page](https://nearhackathon.com/request-changes), not another submission. For 400, correct the listed fields with the same request ID; for 503 or a network error, retain that ID. Stop on 403 or 409 and inspect the response rather than creating a duplicate submission.

## Track selection and evidence limits

Current candidates are **`open`, `social`, `nfts`**: public-resource funding, shared sponsorship, and transferable maintenance authority. `realworld` remains conditional on a defensible real-business use case and evidence; testnet transactions alone do not prove demand. Confirm the final choices against the [current track definitions](https://nearhackathon.com/HACKATHON.md).

The [main showcase](../evidence/testnet-showcase.json) records actual funding, release, creator payout and stewardship transfer. [Browser evidence](../evidence/browser-showcase.json) records committed-resource recovery and completion of the downloaded game with browser networking disabled before load. All roles share one operator; both mirrors share one host.

Both deadline-expiry refund paths and their native withdrawals are recorded separately in [live refund evidence](../evidence/testnet-refunds.json).

Protocol failure/max-state checks, broader accessibility/device QA and independent educator/sponsor validation are remaining engineering goals, **not additional organizer submission requirements**. Disclose their current status; do not present local rehearsal as live settlement. The assistant has not posted on X or submitted the project.
