# Prepared SUNSET testnet sample

Prepared on 2 November 2026 for the operator's `shiftultra.testnet` wallet and reported frontend `https://sunset-lemon.vercel.app`. These files are an original CC0 technical sample, not evidence of a deployed contract, reviewed educational content, funding or settlement.

The campaign ID is `lantern-trail-testnet-v1`. Its prepared target is **0.1 testNEAR**, funding deadline **10 November 2026, 00:00 UTC**, and release window **24 hours after reaching the target**. Proposed contract: `sunset.shiftultra.testnet`; proposed reviewer: `reviewer.shiftultra.testnet`. Those accounts must be created and verified before use.

| Retained bytes | SHA-256 |
| --- | --- |
| `lantern-trail-v1/manifest.json` | `f808d7472f2e5d31749d02b42f89771e1be26ea80c985422ff8e3ed3e7e9656d` |
| `lantern-trail-v1/ciphertext.sunset` | `465542a09861e53c92463407a59f41cedf773f4119937ba413a63701e7543c38` |

`lantern-trail-mirror-v1/` contains byte-identical copies. It demonstrates a change of discovery location on the same host; it does not demonstrate availability independent of that host. The manifest's fixed relative `ciphertext.sunset` path resolves in either directory.

Only the manifest and encrypted resource are published in those directories. The operator's matching release backup and signing arguments stay in the ignored `private/shiftultra-testnet-v1/` directory. Keep them independently and publish the key only through the intended release transaction. A fresh checkout does not contain those private files.

Follow the [testnet showcase guide](../../docs/TESTNET_SHOWCASE.md). The current web workbench exports unsigned plans; actual CLI/wallet signatures and canonical receipts are required before recording a live demonstration. Running the downloaded game in a real browser with networking disabled remains a separate check.
