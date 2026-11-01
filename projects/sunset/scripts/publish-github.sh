#!/usr/bin/env bash
# Run from a normal network-enabled terminal. Credentials stay in process memory.
set +x
set -euo pipefail
unset GH_DEBUG GIT_TRACE GIT_TRACE_PACKET GIT_TRACE_CURL GIT_CURL_VERBOSE GIT_TRACE2 GIT_TRACE2_EVENT GIT_TRACE2_PERF
export GH_HOST=github.com GH_PROMPT_DISABLED=1 GIT_TERMINAL_PROMPT=0

fail() { printf '%s\n' "$1" >&2; exit 1; }
for tool in git gh; do command -v "$tool" >/dev/null || fail "Required command missing: $tool"; done
script_dir=.
[[ ${BASH_SOURCE[0]} != */* ]] || script_dir=${BASH_SOURCE[0]%/*}
root=$(CDPATH= cd -- "$script_dir/../../.." && pwd -P)
git_cmd=(git -C "$root")
[[ ! -d "$root/.sunset-git" ]] || git_cmd=(git --git-dir="$root/.sunset-git" --work-tree="$root")
g() { "${git_cmd[@]}" "$@"; }
remote_git() { g -c credential.helper= -c 'credential.helper=!gh auth git-credential' "$@"; }
repo=Tejas-Sands/sunset
url=https://github.com/Tejas-Sands/sunset.git

[[ $(g rev-parse --show-toplevel 2>/dev/null) == "$root" ]] || fail 'Cannot locate the SUNSET repository.'
[[ $(g symbolic-ref --quiet --short HEAD 2>/dev/null) == main ]] || fail 'Check out the committed main branch before publishing.'
local_sha=$(g rev-parse --verify HEAD 2>/dev/null) || fail 'There are no commits to publish.'
[[ -z $(g status --porcelain --untracked-files=normal) ]] || fail 'Commit or remove pending tracked/untracked changes before publishing; ignored files are allowed.'

# Inspect origin before making any changes; never replace another repository.
origin=$(g remote get-url --all origin 2>/dev/null || true)
if [[ -n $origin ]]; then
  for candidate in "$origin" "$(g remote get-url --push --all origin 2>/dev/null)"; do
    case "$candidate" in
      https://github.com/Tejas-Sands/sunset|https://github.com/Tejas-Sands/sunset.git|git@github.com:Tejas-Sands/sunset|git@github.com:Tejas-Sands/sunset.git|ssh://git@github.com/Tejas-Sands/sunset|ssh://git@github.com/Tejas-Sands/sunset.git) ;;
      *) fail 'Origin points somewhere other than Tejas-Sands/sunset; leaving it unchanged.' ;;
    esac
  done
fi

if [[ -z ${GH_TOKEN:-} ]]; then
  IFS= read -r -s -p 'Temporary GitHub token (hidden): ' GH_TOKEN </dev/tty || fail 'Supply GH_TOKEN in this terminal or run interactively.'
  printf '\n' >/dev/tty
fi
[[ -n $GH_TOKEN ]] || fail 'A temporary GitHub token is required.'
export GH_TOKEN
trap 'unset GH_TOKEN' EXIT
login=$(gh api user --jq .login 2>/dev/null) || fail 'GitHub authentication failed; no repository was changed.'
[[ $login == Tejas-Sands ]] || fail 'The token must belong to Tejas-Sands; no repository was changed.'

read_repo() {
  gh api --include "repos/$repo" --jq '[.full_name, .owner.login, .permissions.push, .default_branch] | @tsv' 2>/dev/null
}
if response=$(read_repo); then
  :
elif [[ $response =~ ^HTTP/[0-9.]+[[:space:]]404[[:space:]] ]]; then
  gh api --method POST user/repos -f name=sunset -F private=false -F auto_init=false >/dev/null 2>&1 || fail 'Could not create Tejas-Sands/sunset; nothing was pushed.'
  response=$(read_repo) || fail 'Could not verify the newly created repository; nothing was pushed.'
else
  fail 'Could not inspect Tejas-Sands/sunset (authentication, access, or network failure); nothing was created or pushed.'
fi
IFS=$'\t' read -r full_name owner can_push default_branch <<<"${response##*$'\n'}"
[[ $full_name == "$repo" && $owner == Tejas-Sands && $can_push == true ]] || fail 'Repository ownership or push permission did not match; nothing was pushed.'

# Use the fixed HTTPS URL even for an SSH origin, so the temporary token is used.
refs=$(remote_git ls-remote --symref "$url" 2>/dev/null) || fail 'Could not inspect remote Git history; nothing was pushed.'
if [[ -n $refs ]]; then
  [[ $default_branch == main ]] || fail 'The initialized remote uses a different default branch; nothing was pushed.'
  remote_sha=
  while IFS=$'\t' read -r sha ref; do
    [[ $ref != refs/heads/main ]] || remote_sha=$sha
  done <<<"$refs"
  [[ -n $remote_sha ]] || fail 'The initialized remote has no main branch; nothing was pushed.'
  remote_git fetch --no-tags "$url" refs/heads/main >/dev/null 2>&1 || fail 'Could not fetch remote main; nothing was pushed.'
  g merge-base --is-ancestor FETCH_HEAD "$local_sha" 2>/dev/null || fail 'Remote main contains history absent locally; nothing was pushed.'
fi
[[ -n $origin ]] || g remote add origin "$url"
[[ $(g rev-parse HEAD) == "$local_sha" ]] || fail 'Local HEAD changed during verification; nothing was pushed.'
remote_git push "$url" "$local_sha:refs/heads/main" >/dev/null 2>&1 || fail 'Push failed; remote publication has not been verified.'
published=$(remote_git ls-remote "$url" refs/heads/main 2>/dev/null) || fail 'Push finished, but remote verification failed.'
[[ ${published%%$'\t'*} == "$local_sha" ]] || fail 'Remote main does not match the local commit; publication has not been verified.'
printf 'Published https://github.com/%s at %s\n' "$repo" "$local_sha"
