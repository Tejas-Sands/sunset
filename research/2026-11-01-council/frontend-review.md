# Frontend and product review — 1 November 2026

The application is coherent as a browser-local rehearsal with a separately configured, read-only testnet viewer. Its visible distinction between simulated balances and actual chain state is appropriate. This review does not establish a live deployment, successful blockchain settlement or browser-tested offline play.

Reviewed `projects/sunset/src/app/page.tsx`, the ledger, chain, agents and demo modules, pack/export interoperability, CSV export and recovery tests. Production source was not edited by this review.

## Findings and dispositions

| Finding | Evidence and correction | Final inspection |
| --- | --- | --- |
| Spreadsheet formula injection in CSV exports | Campaign titles could begin with `=`, and CSV quoting alone preserved executable spreadsheet formulas. Export now uses `receiptsCsv`, which prefixes formula-like cells before CSV quoting. | Corrected; native regression test passes. |
| Stale verified testnet result after configuration edits | Changing contract/hash previously left the old result visible. Inputs now clear the result and rendering requires matching contract and code hash. | Corrected in inspected source. |
| Code verification and campaign view could refer to different blocks | Separate `final` reads could cross an upgrade. The campaign view now pins `block_id` to the verified code block and checks returned block identity. | Corrected; native regression test passes. |
| Public preservation overclaim and misleading grant status | Released campaigns said “Public forever”; refunded grants reused that label. Labels now say “Public release” and “Unused budget returned.” | Corrected. Exported copies are the demonstrated preservation mechanism. |
| Reviewer could not inspect a custom uploaded pack | Verification decrypted the pack but discarded its content; the only playable preview was the generic sample. The review flow now displays the exact decrypted questions, choices, answers and explanations. | Corrected in inspected source. |
| Uploaded pack identity could differ from its campaign | A custom pack could retain another ID/title. Upload now derives the draft identity, and creation rejects mismatches. | Corrected in inspected source. |
| Custom provider credit could not be selected for withdrawal | Activity used five hardcoded accounts although grants allowed configurable providers. Account choices now include campaign/grant participants and credit owners. | Corrected in inspected source. |
| Late reviewer verification could mark a different selected campaign reviewed | A shared boolean could be set by a verification for A after B was opened. Verification now stores `c.digest`; both content rendering and approval require that digest to match the selected campaign. | Corrected in final inspected source. |

The creator form now also requires an explicit CC0 rights acknowledgment, and review approval requires a local backup acknowledgment. These are disclosed adult assertions; they do not authenticate ownership or establish educational quality. State mutations clone the latest `dataRef.current` and update that reference when saving, avoiding replacement of newer rehearsal state by an older asynchronous closure. No unresolved finding from this review remains in the inspected source.

## Verification evidence

- Final fresh `npm test`: 24 tests passed, zero failures. Coverage includes exact monetary parsing, cap/change accounting, exclusive release/refund boundaries, grant spending limits, agent mandates, code-block-pinned live reads, pack validation/encryption, deployment preparation, CSV escaping and independent retained-file recovery.
- Fresh `npm run typecheck`: exit 0.
- Seed interoperability was exercised directly: campaign states are active, refundable and released; balances conserve; ciphertext, plaintext, key and manifest commitments agree; decrypted packs validate; pack IDs/titles match campaigns.
- Pack validation rejects unknown fields, markup, script/remote-resource references, invalid integer choices and oversized content. AES-GCM tests reject modified ciphertext, wrong keys and malformed envelopes. Encryption and decryption both validate the plaintext schema.
- Recovery tests produce standalone HTML from retained encrypted artifact and backup files and reject altered ciphertext/manifest data. This proves the recovery/export computation; it does not prove browser runtime behavior.

The local ledger and deterministic agents are rehearsal tools, not authorization boundaries. The interface identifies role-play accounts, simulated NEAR, unsigned transaction plans and the absence of autonomous wallet access. All sample content keys are locally available for demonstrations; this is not a confidential content-delivery service. No child identity or individual answers are sent by the inspected game flow.

## Browser verification limitation

The preferred agent-browser check could not start. Its default socket directory was read-only; a `/tmp` runtime/profile fallback then exited during daemon startup.

The requested direct fallback used the already-installed Chromium at `/home/citrux/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome`, headless mode, `--no-sandbox`, a `/tmp` user-data directory, disabled background networking, blocked host resolution and `--dump-dom` on `file:///tmp/sunset-lantern-trail.html`. Chromium exited with signal result `-5` and emitted zero DOM bytes. Its error was:

```text
third_party/crashpad/crashpad/util/linux/socket.cc:45
setsockopt: Operation not permitted (1)
```

No browser installation, permission escalation or successful runtime claim followed. Actual offline completion, focus behavior and responsive rendering still need a browser-capable environment. Semantic buttons, form labels, dialog names, Escape handling, focus outlines and a basic Tab loop are present in source; they are not an accessibility certification.

The appropriate completion statement is a tested, truthful local prototype with real encryption/export and a fail-closed testnet reader. Live financial receipts, provider-backed operation and actual offline browser use remain separate evidence requirements.
