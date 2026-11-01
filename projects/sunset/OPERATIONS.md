# SUNSET free deployment and acceptance checks

> Historical full design, prepared 22 October. The 1 November council replaced pending-order sales with immediate sponsorship and reduced the initial integration scope. See [the current implementation README](README.md) and [build ledger](docs/BUILD_LEDGER.md) for what is implemented and verified; this document is not a completion claim.

The initial service budget is $0 in provider charges within available free tiers. All economic demonstrations use faucet-funded NEAR testnet tokens. No paid inference, custom domain, TEE execution, mainnet balance, GPU server or managed worker is necessary for the complete first lifecycle.

These are checked plan conditions on 22 October 2026, not a guarantee that a provider will maintain its terms or serve unlimited traffic. The prototype should stop expensive work when its limits are reached rather than silently upgrade or require payment.

## Initial provider choices

| Service | Relevant current condition | Design consequence |
| --- | --- | --- |
| Vercel Hobby | Free, subject to plan eligibility and usage limits | One personal non-commercial testnet prototype using its included domain |
| Vercel Functions | Hobby duration up to 300 seconds; request/response body cap 4.5 MB | Use short Node.js requests; send files directly to Storage |
| Vercel Hobby quota | Includes 4 active CPU hours, 100 GB fast transfer and one million Function invocations | Small data packs, shared read caching and bounded reconciliation |
| Vercel Hobby cron | Daily frequency and imprecise timing | Optional maintenance only; no financial deadline depends on it |
| Supabase Free | 500 MB database, 1 GB files, 5 GB egress plus 5 GB cached egress; two active projects | One small database and compact content; choose matching free resources carefully |
| Supabase inactivity | A free project can pause after one inactive week | Check health before demonstrations and judging; preserve exports and backups |
| NEAR testnet | Public free RPC options and a CLI faucet account-creation path are documented | Use actual testnet accounts, current public endpoints and local Sandbox for repeatable tests |

[Vercel plans](https://vercel.com/pricing), [Hobby usage](https://vercel.com/docs/plans/hobby), [Function limits](https://vercel.com/docs/functions/limitations), [cron limits](https://vercel.com/docs/cron-jobs/usage-and-pricing), [Supabase pricing](https://supabase.com/pricing), [NEAR RPC providers](https://docs.near.org/api/rpc/providers), [NEAR CLI](https://docs.near.org/tools/cli).

Vercel's Hobby plan is for personal, non-commercial use. This design starts with a non-commercial demonstration and valueless testnet payments. A genuine commercial launch requires reassessing plan eligibility even if traffic remains small. Do not treat real donations or real paid service as automatically eligible merely because the application has a public-benefit purpose. [Vercel pricing and eligibility](https://vercel.com/pricing).

The initial Supabase selection is a design decision, not a provisioned account. No database, hosting project, paid integration or subscription has been created in this architecture task. Marketplace discovery was read-only and confirmed Supabase, Turso and Neon are available choices. Provisioning belongs to the implementation setup.

## Free-tier operating envelope

Start with at most five demonstration campaigns, 100 orders per campaign, 5 MiB per pack and 50 MiB of total published pack data. These are our voluntary starting limits, below provider capacities. API metadata bodies are limited to 64 KiB. The learning game uses text and small static images; no required video or audio stream is introduced.

Use free public RPC with short timeouts, bounded retries and a verified fallback. Prefer `https://test.rpc.fastnear.com` and configure `https://testnet-rpc.intea.rs` as the fallback. Both answered read-only status checks from this environment with `chain_id=testnet` and `syncing=false`. The official archival endpoint also answered, but its documented severe rate limits make it an occasional recovery option. A documented alternative, `https://near-testnet.drpc.org`, returned HTTP 403 here and is excluded. Recheck endpoint health before enabling transactions. Public endpoints have availability and rate limits; an RPC outage must not become a request to pay for access.

Stop polling when a tab is hidden. A pending operation gets bounded polling with backoff; catalog reads use shared caching. Uploads and downloads use Storage directly. Do not run an LLM, browser automation, continuous indexer or game-server daemon inside a Vercel Function.

Daily maintenance clears expired session and rate-limit records, processes a small number of eligible release jobs, and checks health. A manual administrator action can run the same bounded work. This is ordinary maintenance, not a substitute for contract timestamp checks or a guarantee of uninterrupted uptime.

Track actual provider usage in their dashboards. Use only Free resources, keep paid upgrades disabled, and do not enable automatic paid add-ons. If a quota is exhausted, pause uploads and automation and leave clear status information. Already exported learning material remains usable.

## Environment and secret boundaries

| Configuration | Location and rule |
| --- | --- |
| Application origin and public network | Explicit local/preview/production configuration; prototype network is always `testnet` |
| Contract account and expected code hash | Set only from the actual reviewed deployment; never guess an account name |
| RPC primary and fallback | Server configuration with network verification; client wallet has the same network |
| Supabase URL | Backend configuration; object URLs may be public |
| Supabase server credential | Vercel server environment only; no `NEXT_PUBLIC_` prefix and no client import |
| Content key-encryption key | Server environment only, versioned; retain a private recovery copy |
| Restricted release signer | Testnet-only private key, allowed contract and method, bounded gas allowance |
| Maintenance secret | Server environment; reject absent or incorrect authorization |
| Adult sessions | Random opaque cookie; only token hashes in Postgres |
| Creator and teacher release backups | Their own local private files before release; not in the public repository |

Do not put faucet account keys, recovery phrases, content keys or upload tokens in source control. Runtime errors and logs must redact these values. Preview deployments use separate session origins and test data; they do not share unrestricted production credentials or silently act on a different contract.

The backend release key is not a creator's full-access key. Its scope is enforced by both NEAR access-key permissions and contract code. If the managed signer or content-key service fails, independent key holders can still disclose, and eligible actors can still refund through direct contract calls.

## Deployment workflow during implementation

1. Create the application source under `projects/sunset` when the development window opens. Keep the public README and architecture in place. Use a personal prototype repository compatible with the chosen hosting plan.
2. Resolve compatible stable framework and SDK versions, pin lockfiles and read the installed version's docs. Use a supported Node.js LTS runtime on Vercel. The contract builds locally with Rust tooling; it is not built inside a request handler.
3. Check existing Vercel and Supabase resources and quotas before creating another. Connect one Free Supabase resource through the actual Marketplace or supported account flow. Pull environment variables into a private local file; do not print their contents.
4. Apply database schema, indexes, access controls and atomic helper functions. Create bounded Storage buckets and upload policies. Test them against real free resources, not a fake successful-storage adapter.
   Place the database and Vercel Function in the same available region where practical. Record the actual selected region rather than assume a new free resource has a particular location.
5. Run contract tests in NEAR Sandbox. Create or use actual adult testnet accounts through supported wallet/CLI flows; no invented identities are treated as existing accounts. Deploy the contract to testnet and record its actual account, code hash and build identity.
6. Configure the app, optional restricted release signer, artifact key encryption and a small original demonstration pack. Deploy the frontend and API together to one Vercel project. Use its included domain.
7. Run the complete browser and contract flow with actual testnet receipts and provider-backed storage. Export a working offline pack. Verify direct recovery before preparing an immutable demonstration deployment.
8. Before judging, verify project health, endpoint availability, public repository access and reproducible demo instructions. Restore a paused free database through the supported provider flow if necessary. Do not rely on hidden keepalive traffic as a preservation strategy.

Publishing the repository, the X demonstration and the final submission follow the official hackathon requirements and the user's explicit publication decisions. No publication or external deployment is performed by this architecture task.

## Acceptance scenarios

| Scenario | Required evidence |
| --- | --- |
| Initial free learning | A fresh browser plays the introductory puzzle with no wallet or payment |
| Authentic adult login | Valid wallet login works; replayed nonce, wrong origin, wrong network and unauthorized key fail |
| Direct upload | A permitted creator uploads a real artifact; oversize, overwrite and foreign-prefix attempts fail |
| Review binding | Approval for a different digest cannot activate this campaign |
| Cap race | Concurrent final orders never make settled plus reserved contributions exceed the target |
| Quote changes | A stale quote cannot exceed the buyer's signed maximum; excess becomes visible change |
| Delivery recovery | Refreshing a failed download does not open a second order |
| Acceptance | Only the buyer can settle their order, once, before its deadline |
| Order expiry | An unaccepted expired order returns both economic portions and frees its reservation |
| Successful buyout | Final acceptance funds the target; key publication creates exactly one creator credit |
| Invalid or late disclosure | Wrong keys and post-deadline disclosure cannot create creator credit |
| Independent release | With the Vercel API unavailable and creator process stopped, a reviewer uses their backup and own wallet to complete disclosure |
| Public reuse | A new visitor verifies the exact released pack without any purchase entitlement |
| Underfunded campaign | Settled buyout contributions are refundable after expiry, while accepted service fees remain earned |
| Missed release | A funded campaign that misses disclosure refunds its buyout contributions |
| Terminal outcome | A released contribution cannot be refunded; a refundable campaign cannot release creator credit |
| Access grant | Only the named approver can credit the fixed provider, within the separate cap |
| Duplicate claim | A repeated service claim has one economic effect |
| Grant expiry | Unused grant credit returns to the fixed sponsor; buyout funds remain untouched |
| Withdrawal failure | Failed transfer returns credit once; pending or callback-uncertain operations cannot be paid twice |
| Accounting | Economic deposits reconcile with pending balances, escrow, grants, credits and payouts; gas and storage are separate |
| Hosting failure | Direct contract refunds remain available when the database or app is down |
| Data tampering | A changed SQL total does not change contract funds or release eligibility |
| Offline export | Exported game runs after disabling all network access, with no wallet, fonts, model or backend request |
| Content safety | Uploaded scripts, unsafe embedded markup and malformed pack data do not execute |
| Child data | No learner identifier or individual progress is sent to the database or chain during the demonstration |
| AI unavailable | All core paths work without a model key or model connection |
| Immutable claim | The specific demonstration contract has no retained upgrade/key-restoration path before it is labeled immutable |
| Build identity | A recorded source revision, lockfile and compiler/toolchain reproduce the published contract artifact or its build differences are explicitly resolved before making a source-to-binary claim |

These checks are not recorded as passing yet. The implementation should have focused contract tests for monetary invariants and meaningful browser/API integration checks for the complete flow. Documentation verification cannot substitute for them.

## Educational and delivery acceptance

The initial game needs a clear objective, correct answer checking, readable feedback, keyboard support and a complete short play session. The reviewer should check the selected language and content. A technical demo can prove download, access and correct balances; educational impact requires a later local pilot and evaluation.

A real school deployment would also fund devices, electricity, teacher training, support and content updates where needed. The first prototype demonstrates a finite service grant with labeled evidence, not a claim that infrastructure or teaching has already been delivered. Existing offline programs explicitly include local hubs and facilitator support. [UNICEF's model](https://www.unicef.org/learningpassport/offline-learning).

## Later additions with an actual trigger

| Trigger | Addition |
| --- | --- |
| Real commercial operation | Eligible hosting plan, operating budget and production review |
| Content distribution exceeds the free envelope | Additional object storage/CDN capacity with an explicit budget |
| Actual provider workloads need timely background execution | Durable worker/queue after measured demand |
| An AI feature proves useful and has a funded inference budget | Optional model integration; learning and refunds remain independent |
| Communities want to replace operators | Integrate LIFEBOAT's handover and authority controls |
| A real game needs persistent multiplayer hosting | A separate quoted game-server provider under finite grants |
| Confidentiality from infrastructure operators is required | A separately reviewed confidential-execution design |

The initial build remains one learning application and its funding/release workflow. These later services are not prerequisites for the first useful and reviewable deployment.
