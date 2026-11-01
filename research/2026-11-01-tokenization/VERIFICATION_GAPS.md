# SUNSET local verification gaps — 1 November 2026

Checked at `2026-11-01T06:06:06Z`, against working-tree source based on Git revision `7940cd97779d2e0931bb92ae2e992c23c1616bcf`. This is an environment and verification assessment, not proof of deployment, browser execution, NEAR protocol execution, educational outcomes or sponsor demand.

The selected product and implemented scope are [SUNSET](../../projects/sunset/README.md) and its [build ledger](../../projects/sunset/docs/BUILD_LEDGER.md). Existing evidence remains in [verification.json](../../projects/sunset/evidence/verification.json), the [frontend review](../2026-11-01-council/frontend-review.md) and [contract review](../2026-11-01-council/contract-review.md).

## Results reproduced in this workspace

| Check | Observed result | What it establishes |
| --- | --- | --- |
| `npm test` in `projects/sunset` | **24 passed**, zero failures or skipped tests | Current Node crypto/schema/accounting/deadline/grant/policy/receipt/recovery/preparation/RPC test suite passes. |
| `npm run test:contract` | **3 passed**, zero failures or skipped tests | The checked-in compiled Wasm executes against transactional host doubles. This is **not NEAR Sandbox**. |
| Checked-in contract identity | 190,561 bytes; SHA-256 `79a647abecd7f04e36d44dcd4b79f8310395e636f6165755e1a74d97887f4837` | Identifies the precise artifact exercised by the compiled-Wasm tests. |
| Python `socket.socket(AF_INET, SOCK_STREAM)` | `PermissionError: [Errno 1] Operation not permitted` | The current execution context cannot create a local TCP socket; failure occurs before bind. |
| Python `socket.socket(AF_UNIX, SOCK_STREAM)` | `PermissionError: [Errno 1] Operation not permitted` | A writable `/tmp` location does not remove the Unix socket restriction. |
| `npm start` | Exits 1 at Python `socket.socket`, before binding `127.0.0.1:3000` | The static app server cannot start in this execution context. This is not an HTTP/application response failure. |
| Named `agent-browser` file navigation with writable runtime/profile | Exits 1: `Daemon process exited during startup with no error output` | No rendered page, DOM snapshot, screenshot, mobile check or offline play result was obtained. |
| `agent-browser doctor --offline --quick --json` | Exits 0, nine local checks pass; no active daemons | Installation and local paths are present. The quick doctor does **not** establish successful browser launch. |
| Actual NEAR runtime availability | No `near-sandbox` or `neard` command found; no matching runtime executable or `near-workspaces` package found in the searched workspace/local caches | A real protocol test was not runnable with the available local tools. This is not a failed protocol execution. |

Node is `v24.17.0`, Python is `3.14.6`, and agent-browser is `0.37.1`. Cached Chromium exists, including `/home/citrux/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome`. The doctor also detects its managed Chrome installation. Installing another browser would not resolve the independently reproduced socket restriction.

Runtime searches covered `PATH`, repository `node_modules`, `/home/citrux/Sides`, `/home/citrux/.cache`, `/home/citrux/.local/share`, `/home/citrux/.npm`, `/home/citrux/.cargo` and `/tmp`. `/home/citrux/.near-sandbox` and `/home/citrux/.near` are absent. This is a bounded local inventory, not a claim that no runtime exists anywhere on the machine.

## Minimal reproductions

Run from the repository root. The socket probe uses only a transient `/tmp` path and closes/unlinks successful sockets:

```sh
python3 - <<'PY'
import socket
from pathlib import Path

for label, family, address in [
    ('tcp_loopback', socket.AF_INET, ('127.0.0.1', 0)),
    ('unix_tmp', socket.AF_UNIX, '/tmp/sunset-verification-socket-probe.sock'),
]:
    try:
        with socket.socket(family, socket.SOCK_STREAM) as connection:
            connection.bind(address)
            print(label, 'PASS', connection.getsockname())
        if family == socket.AF_UNIX:
            Path(address).unlink()
    except OSError as error:
        print(label, 'BLOCKED', type(error).__name__, error.errno, str(error))
PY
```

Both families returned errno 1. Starting the already-built app with `cd projects/sunset && npm start` independently reproduced the same failure at socket creation.

The browser check used an empty explicit configuration, a session derived by `agent-browser session id --scope worktree --prefix sunset-verification`, the cached Chromium, and writable runtime/profile locations. A first attempt exposed a Unix socket path-length limit; shortening the runtime directory removed that specific error. The following attempt reached daemon startup and failed:

```sh
mkdir -p /tmp/sv1101 /tmp/sunset-verification-20261101/profile
printf '{}\n' > /tmp/sunset-verification-20261101/agent-browser.json
XDG_RUNTIME_DIR=/tmp/sv1101 \
AGENT_BROWSER_SOCKET_DIR=/tmp/sv1101 \
agent-browser \
  --config /tmp/sunset-verification-20261101/agent-browser.json \
  --session sunset-verification-578c96ae66ed \
  --profile /tmp/sunset-verification-20261101/profile \
  --executable-path /home/citrux/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome \
  --debug open \
  file:///home/citrux/Sides/chained_blocks/near/hacka/projects/sunset/public/try-lantern-trail.html
```

The command exited 1 with no browser output. An offline quick doctor using the same configuration confirms `/tmp/sv1101` as its socket directory and reports no active daemons. A session-specific close also failed during startup. No shared default browser session was used. The direct Python probes establish an OS-level socket limitation independently of agent-browser's silent exit; its exact internal failure was not logged.

No sandbox escalation, remote browser, paid resource, external sandbox, testnet account, deployment, signing action or wallet was requested or used during these checks.

## Browser work that remains executable elsewhere without deployment

Use a local environment that permits loopback and Unix sockets. No hosted site, wallet or external service is necessary for the rehearsal. Build locally, serve the generated `out/`, then use a fresh named browser session. Save the initial state and reset only that session's sample data between independent scenarios.

| Scenario | Exact outcome to verify | Evidence to retain |
| --- | --- | --- |
| Main rehearsal | As `grove.testnet`, contribute 1.6 simulated NEAR to The Lantern Trail; reach its 8-NEAR goal; change becomes claimable. Switch to `teacher.testnet`, verify the retained backup and publish once; the creator is credited once. | Browser steps and before/after balances; double publication attempt; console errors. |
| Independent offline use | Download the released standalone HTML. Close the app tab and stop the local server. Use a separate fresh browser session, set networking offline before opening the downloaded file, and complete all five questions. | Downloaded file hash, screenshot of completion, browser network log showing no requests needed by gameplay. A cached website tab is insufficient. |
| Deadline refund | Claim River Routes' expired contribution refund as `grove.testnet`, then repeat the claim and attempt withdrawal twice. Advance the rehearsal clock to test funded-but-unreleased expiry separately. | Credit and pending balance changes, repeated-action rejection, activity entries clearly marked rehearsal. |
| Review binding | Prepare an original/custom pack; export and restore its private backup; inspect all exact decrypted questions as the named reviewer. Alter an agreement/artifact or switch roles while verification is pending. | Successful exact-pack review; stale or changed agreement cannot gain approval. Keep secret backups out of public evidence. |
| Recovery without app | Stop the server. Run documented `recover-pack.mjs` with retained ciphertext and private backup, then open its output offline in the fresh browser. | Recovery output hash, completed game and rejected modified-artifact attempt. |
| Mobile and keyboard | Exercise discover, campaign, creator/reviewer, recovery and dialogs at a narrow mobile viewport; use Tab/Shift+Tab/Escape through dialogs; inspect full terms and error messages. | Screenshots without clipped controls, visible focus, dialog close/focus-return observations and console errors. |
| State resilience | Reopen the same browser session, then use a fresh one; verify rehearsal state persists only in its own browser. Test malformed import and blocked browser storage. | Clear failure messages and no accidental claim of shared financial settlement. |
| Fail-closed chain reader | With no valid deployment configuration, attempt a read; with controlled mocked responses, test wrong chain/code/block identities and failed receipts. | Visible error and no live-success claim. Mock responses are not onchain evidence. |

Automate this workflow only after a browser can actually start. Recording test code that has never launched would add an unverified artifact without closing the current gap.

## Real NEAR protocol work that remains local, but unavailable here

A socket-capable machine with an actual compatible NEAR Sandbox binary is sufficient; external testnet deployment is not required to test these paths. Record runtime version, protocol version, source revision and Wasm hash, and use only disposable local accounts and sample keys. The existing host harness cannot supply any of these protocol observations.

1. Initialize once as the contract account with an owner; reject external and repeated initialization. Create a campaign with the exact 0.05-NEAR allowance and approve its exact agreement digest from the named reviewer.
2. Contribute from independent accounts with the required first-registration allowance. Exercise funding-cap change, exact deposits, incorrect deposits, forbidden callers and all deadline equality boundaries. Inspect canonical state after both success and rejection.
3. Complete funding and publish the committed sample key once. Read actual campaign/account state and measure the real transaction/receipt gas. Reject a wrong sample key and repeated release without exposing any real secret.
4. Run both underfunded and funded-but-unreleased expiry refunds. Refund only each contributor, reject duplicates and prohibit a subsequent release.
5. Withdraw credited amounts through the actual transfer and private callback. Capture the complete receipt chain, actual native balances and gas; balance comparisons must account for transaction fees rather than treating them as conservation failures.
6. Force a confirmed failed native transfer using a disposable local account setup. Verify that its actual result callback restores credit once and rejects forged/stale callback operations. Do not substitute a manually passed JavaScript boolean for the failed receipt.
7. Force callback execution failure in the local test setup after initiating a transfer. Verify the canonical pending operation persists and an automatic second payout cannot occur. Record the actual failed receipt and transfer outcome; elapsed time is not a valid recredit signal.
8. Fill the documented five-campaign/100-account capacity, measure serialized storage and account storage collateral, and run withdrawal/callback at the maximum supported state with the documented gas budget. Verify adequate balance collateral for code, state and scheduled transfers.

Do not call these scenarios passed until actual protocol execution and receipt results are retained. An older or incompatible runtime rejecting the Wasm must be recorded as that specific compatibility failure. The [contract README](../../projects/sunset/contracts/sunset/README.md) contains the ABI, amounts, invariant and direct recovery procedure.

## Scope of the remaining gates

The browser and protocol-runtime gaps are local execution constraints. Educator review and sponsor feedback require independent people and remain unverified. Public hosting, signed testnet settlement, wallet integration, hackathon submission and any irreversible account configuration are separate actions. A passing host harness or a successful quick browser doctor does not close those gates.
