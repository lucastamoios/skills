#!/usr/bin/env bash
# rebase-branch.sh <branch> <base>
# Checks out <branch>, fetches and rebases onto origin/<base>, then pushes.
#
# Output (stdout): JSON status message
#
# Exit codes:
#   0 - success (rebased + pushed)
#   1 - conflict (rebase left in progress, JSON with conflicted files)
#   2 - push failure (hard stop, JSON with error)
#   3 - diverged from origin (local and origin/<branch> have both advanced; force-push would drop remote commits)

set -uo pipefail

branch="$1"
base="$2"

if [ -z "$branch" ] || [ -z "$base" ]; then
    echo '{"error":"args","message":"Usage: rebase-branch.sh <branch> <base>"}' >&2
    exit 1
fi

# Checkout the branch
if ! git checkout "$branch" 2>/dev/null; then
    echo "{\"status\":\"error\",\"error\":\"checkout\",\"message\":\"Failed to checkout $branch\"}"
    exit 1
fi

# Fetch the base AND the branch itself. We need origin/<branch> to detect
# whether the local working copy is behind the remote before we rebase and
# force-push. The branch may legitimately not exist on origin yet (first
# push), which is why we swallow fetch errors.
git fetch origin "$base" 2>/dev/null || true
git fetch origin "$branch" 2>/dev/null || true

# Without this sync, a local branch that is behind origin would be silently
# overwritten by the force-push below, orphaning remote commits. This
# happens in practice when the same branch is shared across worktrees.
if git rev-parse --verify --quiet "origin/$branch" > /dev/null 2>&1; then
    pre_sync_head=$(git rev-parse HEAD)
    remote_branch_head=$(git rev-parse "origin/$branch")
    if [ "$pre_sync_head" != "$remote_branch_head" ]; then
        if git merge-base --is-ancestor "$pre_sync_head" "$remote_branch_head"; then
            # Strictly behind - fast-forward to origin/<branch>.
            if ! git merge --ff-only "origin/$branch" 2>/dev/null; then
                echo "{\"status\":\"error\",\"error\":\"sync\",\"branch\":\"$branch\",\"message\":\"Failed to fast-forward $branch to origin/$branch\"}"
                exit 1
            fi
        elif git merge-base --is-ancestor "$remote_branch_head" "$pre_sync_head"; then
            # Strictly ahead - legitimate unpushed local commits, continue.
            :
        else
            # Diverged - force-push would silently discard remote commits.
            echo "{\"status\":\"diverged\",\"branch\":\"$branch\",\"local\":\"$pre_sync_head\",\"remote\":\"$remote_branch_head\",\"message\":\"Local $branch and origin/$branch have diverged. Reconcile manually before rebasing.\"}"
            exit 3
        fi
    fi
fi

# Check if rebase is needed
local_head=$(git rev-parse HEAD)
merge_base=$(git merge-base HEAD "origin/$base")
remote_base_head=$(git rev-parse "origin/$base")

if [ "$merge_base" = "$remote_base_head" ]; then
    # Already up to date with base, just push
    :
else
    # Rebase onto origin/base
    if ! git rebase "origin/$base" 2>/dev/null; then
        # Conflict - collect conflicted files
        conflicted=$(git diff --name-only --diff-filter=U 2>/dev/null | jq -R -s 'split("\n") | map(select(length > 0))')
        echo "{\"status\":\"conflict\",\"branch\":\"$branch\",\"base\":\"$base\",\"files\":$conflicted}"
        exit 1
    fi
fi

# Check if we need to push
has_remote=$(git config "branch.$branch.remote" 2>/dev/null || true)

if [ -z "$has_remote" ]; then
    # First push
    if ! push_output=$(git push -u origin "$branch" 2>&1); then
        echo "{\"status\":\"push_failed\",\"branch\":\"$branch\",\"message\":$(echo "$push_output" | jq -R -s '.')}"
        exit 2
    fi
else
    # Force push with lease
    if ! push_output=$(git push --force-with-lease 2>&1); then
        echo "{\"status\":\"push_failed\",\"branch\":\"$branch\",\"message\":$(echo "$push_output" | jq -R -s '.')}"
        exit 2
    fi
fi

echo "{\"status\":\"ok\",\"branch\":\"$branch\",\"base\":\"$base\"}"
exit 0
