# GitHub publication

User-authorized destination: **Tejas-Sands/sunset**. Publish the standalone README first, then push each meaningful verified implementation batch. No routine reconfirmation is needed. Preserve existing unrelated remote history and never force-push.

## Current state

A README-only root commit and subsequent source/research/contract commits exist locally on `main`. No GitHub repository creation or successful remote push has been verified. The GitHub plugin is installed, but its calls return `Unknown tool`; the CLI cannot obtain the Tejas-Sands credential, and API requests cannot connect in this session. Resolve account/network access before claiming publication.

The usual `.git` mount is read-only and empty in this restricted workspace. Local metadata is in ignored `.sunset-git`. From this root:

```sh
sunset_git() { git --git-dir=.sunset-git --work-tree=. "$@"; }
sunset_git status
sunset_git log --reverse --oneline
```

Outside this restricted workspace, a normal clone uses ordinary Git commands. The ignored `.publication/sunset.bundle` is a portable copy of the local `main` history; it contains source/history, not GitHub credentials.

## Once GitHub access is restored

Authenticate the actual Tejas-Sands account through the supported GitHub CLI/browser flow and verify `gh api user --jq .login`. Do not use another account's credential or paste tokens into source, command arguments or chat. Inspect whether the intended repository exists and has existing history before writing.

If it does not exist, the user has authorized creating it for this public hackathon project:

```sh
gh repo create Tejas-Sands/sunset --public --description 'SUNSET: public-resource sponsorship, release/refund and independent offline learning on NEAR testnet.'
```

For a **new empty repository only**, publish each commit in order so the README is the first remote content:

```sh
for revision in $(sunset_git rev-list --reverse main); do
  sunset_git push origin "$revision:refs/heads/main" || break
done
sunset_git push --set-upstream origin main
```

Inspect remote `main` before retrying a partial run. If the destination already contains unrelated work, fetch and reconcile it rather than overwriting it. Verify the remote head matches the intended local head. Only then update `projects/sunset/evidence/verification.json` to record actual repository publication, commit that evidence change and push it.

Subsequent work: run relevant checks, inspect the staged diff and exclusions, commit one coherent batch and push it. Do not publish generated dependencies/caches, environment files, wallet private keys, private release backups or secret release arguments. Commit author is configured locally as Tejas-Sands with a GitHub noreply email. No AI co-author attribution is included; announce any future changes to that policy in advance.
