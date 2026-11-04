---
name: sync
description: Synchronize the configured context repository with its upstream and run its optional setup integration. Use for an explicit request to sync the private knowledge repository.
---

# Sync

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Run this workflow in `profile.paths.brain`. Invoking this skill authorizes its setup, commit, and push steps.

## SSH execution and preflight

On this Mac, run Git remote operations and SSH-signed commits in an interactive
terminal with access to the 1Password agent. For Codex `exec_command`, use
`tty: true` and `sandbox_permissions: "require_escalated"`, subject to normal
approval review. Use this mode for the preflight, pull, signed commit, push,
and remote verification. Keep local read-only inspection in the sandbox.

After inspecting the repository and before creating a stash, resolve the current
branch's configured upstream remote and branch. Run `git ls-remote --exit-code
--heads <remote> <branch>` and require success. Do not hardcode `origin/main`.
If it fails, preserve the working tree and diagnose the connection before
stashing. Agent socket access and authorization to sign are separate checks.

For `Operation not permitted` or `communication with agent failed`, verify the
execution mode and effective `IdentityAgent`; do not conclude that 1Password is
locked or the key is missing. If the failed attempt was noninteractive or
sandboxed, retry once in the required mode. If it already used that mode, report
the actual blocker instead of repeating the same command. Apply this check
before falling back to an unsigned commit. Do not change global sandbox policy,
export private keys, or relax 1Password authorization settings.

When resuming a failed run, inspect its recorded stash IDs and operation state
first. Reuse the existing stash; preserve any newer changes separately. Never
create another stash merely because authentication is being retried.

## Synchronization

1. Inspect `git status --short --branch`. If another merge or rebase is already in progress, stop and report it. Stay on the current branch and use its configured upstream.
2. If local changes exist, run `git stash push -u -m "sync"` and record the new stash ID. Leave existing stashes alone.
3. Run `git pull --prune --rebase` (`git pull -pr`). Resolve conflicts by preserving the intent of both sides, then run `git add <resolved-files>` and `GIT_EDITOR=true git rebase --continue` until the rebase finishes. Ask only when conflicting intent cannot be inferred. If the pull fails for another reason, stop and preserve the stash.
4. If you created a stash, restore it with `git stash apply <recorded-stash-id>`. Resolve any conflicts and stage the resolved files. Drop only that stash, by its current stash reference, after its contents are safely restored and committed.
5. After restoring local changes, run the configured `profile.integrations.sync.setup_command` when present. Without that optional setup integration, skip machine configuration and continue repository synchronization. This installs new shared skills and refreshes managed configuration links. If incoming configuration needs setup beyond links, read its updated installation instructions and perform the relevant setup. Preserve machine-specific settings and report any setup that cannot finish. Do not run full machine provisioning unless the incoming changes require it.
6. Review `git diff` and `git diff --cached`. Stage the local Brain changes with `git add -A`, then run `git diff --cached --check`. If staged changes exist, run `git commit -S -m "chore: sync brain"` with the 30 second signing timeout from AGENTS.md. If SSH signing fails or times out, retry unsigned and report it. Do not add a co-author.
7. Run `git push`. Never force-push. If the remote advanced, repeat the pull, conflict-resolution, and setup steps, commit any resulting local changes, then retry the push once.
8. Verify that the remote branch SHA matches `git rev-parse HEAD`, and check `git status --short --branch`. Report the sync result, installed skills or configuration, and any remaining changes or required reloads.

Keep repository syncing limited to Brain, and setup limited to its managed skills and configuration. Do not sync nested repositories or discard changes to resolve conflicts.
