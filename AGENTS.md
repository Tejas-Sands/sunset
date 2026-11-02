# Project collaboration

SUNSET is the selected NEAR hackathon product. Read projects/sunset/README.md and its build ledger for the implemented scope; the October architecture is historical planning.

## GitHub workflow authorized by the user

The user requested on 1 November 2026: use the Tejas-Sands GitHub account, publish README first, then keep committing and pushing subsequent changes. Continue with small meaningful verified commits and push each completed batch; no repeated confirmation is needed for routine commits/pushes within this repository. Do not force-push or overwrite unrelated remote history. The intended new repository is Tejas-Sands/sunset; verify its ownership and contents before publishing.

The user revised this workflow on 2 November: the assistant should keep making verified local commits, and the user will push them from the laptop's normal terminal. After a completed batch, provide `git --git-dir=.sunset-git --work-tree=. push origin main` from this root. Do not restart shared Codex GitHub-plugin connection changes; the account is shared and GitHub authentication should remain local to the laptop.

Commit author is Tejas-Sands with a GitHub noreply address, configured only for this repository. Do not silently add AI co-author trailers or LLM disclosures in commit metadata/messages or PR descriptions; announce any such wording before publication. Existing council documentation retains its accurate methodology.

This restricted workspace exposes an empty read-only .git mount. Local repository metadata is instead in .sunset-git, ignored from publication. Use `git --git-dir=.sunset-git --work-tree=.` from this root. A normal clone from GitHub will have a standard .git directory.

Never commit node_modules, framework/build caches, Rust targets, environment secrets, private release backups, wallet keys, or secret release arguments. Keep checked-in public WASM and original sample content. Run checks appropriate to the changed code before pushing. Document failed pushes accurately; local commits are not proof of remote publication.

## Current testnet operator preparation

The operator supplied `shiftultra.testnet` and reported frontend `https://sunset-lemon.vercel.app`. Read `projects/sunset/docs/TESTNET_SHOWCASE.md` and `projects/sunset/evidence/testnet-preparation.json` before live steps. Proposed contract/reviewer/sponsor subaccounts are not evidence that those accounts exist. The matching prepared release backup and arguments are in ignored `projects/sunset/private/shiftultra-testnet-v1/`; retain them privately. No signed deployment or actual protocol execution is established by preparation alone.

The operator explicitly requested avoiding MyNearWallet after the CLI's default browser import failed. Use the installed CLI's direct private-key/recovery-phrase import in the operator's own terminal, with account-key checking and local keychain storage. Never request those secrets or secret-bearing import transcripts in chat, and do not return to the default browser-wallet flow.
