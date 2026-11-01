# SUNSET technical feasibility

NEAR is useful here as shared settlement and authority infrastructure. Its contract can enforce a capped ledger, fixed beneficiaries and time-dependent release/refund transitions independently of the application database. Its restricted function-call keys can support a release-only convenience service. It cannot certify copyright, teaching quality, delivery to a school or permanent availability of offchain files.

Other programmable chains can implement related agreements. The reason to use NEAR is a coherent implementation with its account/key model and testnet tooling, not an exclusivity claim.

## What must be proved

| Claim | Necessary implementation evidence | Remaining trust or availability |
| --- | --- | --- |
| Funding never exceeds the agreed buyout | Atomic cap reservations, checked arithmetic and concurrent-order tests | Correct deployed contract code |
| Creator compensation requires release | One transition validates the committed key and credits the fixed creator | Reviewer checked that this key matches the promised pack |
| A teacher can release independently | Actual own-wallet/CLI disclosure with API and creator process stopped | At least one key holder retains their backup and RPC access |
| Failure permits refunds | Deadline-bound contribution claims exercised directly | Chain availability, gas and correct withdrawal handling |
| The released version remains usable | Verified artifact plus independent export, opened without network | Someone retains copies and a compatible device |
| Support spending stays bounded | Named approver and unique claims cannot exceed a separate grant | Approver's judgment about the real service |

These are separate promises. A release key without artifact bytes is insufficient. A copy without a license may be usable technically without the promised reuse rights. A funding event without disclosure is still awaiting fulfillment.

## Key custody tradeoffs

| Approach | Useful property | Why it is not the complete answer |
| --- | --- | --- |
| Creator-only key | Smallest operational footprint | Creator can disappear or withhold |
| Backend-held key | Straightforward hosted delivery | Operator availability and secret custody remain dependencies |
| Creator and licensed teacher backups | Different adults can complete the same disclosure | Authorized recipients can leak early or lose every copy |
| Threshold key holders | Can distribute custody across a group | Adds coordination and liveness assumptions; not implemented |
| Confidential execution | Can protect key handling in approved execution | Requires verified code, inputs, invocation authority and a funded available service |
| drand timelock | Can target disclosure at a future beacon round | A clock is not proof of revenue; eventual disclosure can happen without funding |

The chosen first build combines managed delivery with adult backups. Its economic promise is release or the contract-defined refund; it does not promise automatic disclosure in every failure scenario. It also does not promise secrecy from licensed recipients who need offline access.

drand documents both threshold-compromise and continued-network assumptions. A timelock fallback would change the product: the creator may eventually lose exclusivity even after an unsuccessful funding campaign. That needs explicit agreement and key-binding verification. It is not a free upgrade to the existing terms. [drand documentation](https://docs.drand.love/docs/timelock-encryption/).

OutLayer documents secrets bound to project identity or exact WASM hashes, and an attestation architecture checking worker measurements. These are useful capabilities to investigate if confidential execution becomes necessary. They do not independently prove that a SUNSET module receives authentic finalized funding inputs, remains invocable after a creator disappears, or has future execution paid for. No confidential integration or zero-cost entitlement is established here. [Secrets](https://app.outlayer.ai/docs/secrets), [verification model](https://app.outlayer.ai/docs/trust-verification).

## NEAR key permissions need method-level decisions

Function-call keys can target a specified contract and method list with a gas allowance, and cannot attach NEAR. The managed signer should allow only `publish_release`, with zero deposit and a bounded allowance. Omitting the method list permits a broader surface and is unsuitable here. [Access keys](https://docs.near.org/protocol/accounts-contracts/access-keys).

There is a separate account-authorization issue: a function-call key acts under the user's account name. A predecessor-account check does not prove a fresh wallet decision. NEAR documents requiring exactly one yoctoNEAR for sensitive methods as a way to require deposit-capable authorization while keeping the ownership check. Apply an explicit policy to withdrawal and to methods such as accepting an order or approving service spend; preserve the zero-deposit permissionless release path. [Sensitive-method guidance](https://docs.near.org/smart-contracts/security/one_yocto).

The small authorization deposit must have a defined accounting category. Do not silently count it toward buyout or service revenue. If using a protocol dust/surplus category, include it in reconciliation explicitly. Deposit-bearing create methods already have another deposit model; review those separately rather than attaching one yocto indiscriminately to every call. A signature proves account authority, not an educator's qualifications.

## Storage and withdrawals

NEAR locks balance to cover contract state. Record creation must fund actual state growth; unbounded free writes can consume contract collateral. Preallocate release, refund and callback state where necessary, keep IDs/collections bounded and paginate reads. Read live storage configuration instead of embedding a marketing estimate of transaction cost. [Storage staking](https://docs.near.org/protocol/storage/storage-staking).

A native transfer and its callback are distinct receipt executions. If cleanup fails, earlier committed state does not roll back automatically, and the callback is not automatically retried. Keep pending withdrawals explicit; recredit only a confirmed failure, once. An uncertain callback cannot justify a second payout. The specification's diagnostic-but-pending outcome is honest, but it also means absolute recovery under every implementation failure is not yet proved. [Asynchronous calls](https://docs.near.org/smart-contracts/anatomy/crosscontract), [callback failures](https://docs.near.org/smart-contracts/security/cross-contract-calls/callback-failures).

## Verification and preservation are different

The manifest, ciphertext, plaintext, license and key commitment identify exact bytes. They should be checked independently at each transition. The contract validates the key commitment; the adult review establishes that the key opens the agreed pack. A dishonest or mistaken reviewer is still a failure mode.

Do not publish a real key in a deliberately failing early transaction. Transaction arguments are not made private by rejection. Run wrong-key and timing tests with disposable fixtures, then use the real key only on the intended disclosure path.

After release, readers need the encrypted artifact, public key, format specification, compatible runtime and granted rights. Keep these together in exported bundles with hashes and provenance. Public chain state does not preserve a Supabase object; content addressing does not ensure someone stores it. A free-tier pause or deleted object must be tested with copies already held outside the provider.

The same distinction applies to immutability. A fixed agreement in today's code can still be replaced if an external full-access deployment key or upgrade/key-restoration method remains. Label development deployments accurately. The stronger final deployment needs source/build identity and a verified absence of replacement authority, followed by an explicit human signing decision.

## Size boundaries require clarification

The proposed v1 encryption envelope adds 36 bytes: an eight-byte header, twelve-byte nonce and sixteen-byte authentication tag. Therefore a 5-MiB plaintext requires more than 5 MiB of ciphertext. If Storage limits the whole object to 5 MiB, a maximum-sized valid plaintext would fail upload.

Before implementation, define 5 MiB as the maximum plaintext pack size and permit the fixed envelope overhead in the ciphertext bucket, or reduce the allowable plaintext accordingly. The self-contained export can be larger again: base64 data expands binary size, and the reviewed runtime adds bytes. Give export size its own limit and do not promise that every 5-MiB pack produces a 5-MiB HTML file.

This is a design consistency finding, not a performance measurement or an implemented fix.

## Changes to make before implementation

1. Add a deposit-policy column to the contract method table: actual economic/storage deposit for create methods; deposit-capable authorization for sensitive adult decisions; zero deposit for independent release; private callbacks with no external authorization path. Specify accounting for authorization dust.
2. Define plaintext, ciphertext and export size limits separately, including the v1 envelope overhead and a bounded runtime.
3. Include the exact public license text/reference, attribution, runtime license, format version and provenance in the reviewed manifest and independent export.
4. Add tests that attempt sensitive actions through an overly broad function-call key, and prove the managed release key cannot perform them.
5. Add a copied-to-another-device offline test, alongside the same-browser network-disabled test. Keep a prospective Kolibri ZIP import as a separate later check.

These are research recommendations. They do not silently change existing economic terms or claim that the proposed contract or browser code has been implemented.

## Extensions with a concrete reason

Original accessibility resources, local-language teacher materials and reusable game assets are plausible later release candidates if a rights holder and buyer exist. General game/cloud hosting remains a recurring service rather than a one-time liberated asset. That would fit a finite access grant with an actual provider, operating budget and uptime arrangement. Vercel remains the control application, not a persistent multiplayer/GPU fleet.

Track fit follows demonstrated behavior. Open Innovation is the clearest baseline. A learning game alone does not establish the Games With Real Economies requirements, and a deterministic release job alone does not establish AI Swarms or Autonomous Business. Keep additional tracks conditional on meaningful implemented behavior described by the organizers. [Official tracks](https://nearhackathon.com/HACKATHON.md).
