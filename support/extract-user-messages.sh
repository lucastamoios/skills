#!/bin/bash
# Extract the user's typed messages from Claude Code transcripts into per-project
# markdown files, for the gardener-transcripts miner.
#
# Usage: extract-user-messages.sh --out <dir> [--since <ISO-8601 timestamp>]
#
# Filters applied (each one earned its place in the July 2026 manual pass):
# - isSidechain != true: subagent "user" messages are machine-generated prompts
#   and would badly skew any analysis of what the user corrects (excluding generated prompts).
# - Harness noise excluded: local-command caveats, command stdout, system
#   reminders, skill expansions, interrupt markers.
# - Automated hook prompts excluded (the per-commit security-review boilerplate
#   that dominates most worktree project dirs).
# - Messages over 2000 chars are truncated: giant pastes (logs, PR bodies) are
#   context, not voice.

set -euo pipefail

SINCE=""
OUT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --since) SINCE="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done
if [ -z "$OUT" ]; then
  echo "usage: extract-user-messages.sh --out <dir> [--since <ISO timestamp>]" >&2
  exit 1
fi
mkdir -p "$OUT"

for dir in "$HOME"/.claude/projects/*/; do
  name=$(basename "$dir")
  outfile="$OUT/$name.md"
  : > "$outfile"
  for f in $(ls -t "$dir"*.jsonl 2>/dev/null); do
    sid=$(basename "$f" .jsonl)
    msgs=$(jq -r --arg since "$SINCE" '
      select(.type=="user")
      | select(.isSidechain != true)
      | select($since == "" or .timestamp > $since)
      | .timestamp as $ts
      | .message.content
      | if type=="string" then .
        elif type=="array" then ([.[] | select(.type=="text") | .text] | join("\n"))
        else empty end
      | select(length>0)
      | select(startswith("<local-command-caveat>")|not)
      | select(startswith("<command-name>")|not)
      | select(startswith("<local-command-stdout>")|not)
      | select(startswith("<system-reminder>")|not)
      | select(startswith("Base directory for this skill")|not)
      | select(startswith("Review this change for security vulnerabilities")|not)
      | select(test("^\\[Request interrupted") | not)
      | (if length > 2000 then .[0:2000] + " [...TRUNCATED]" else . end)
      | "### [\($ts)]\n" + .
    ' "$f" 2>/dev/null)
    if [ -n "$msgs" ]; then
      printf '\n\n## SESSION %s\n%s\n' "$sid" "$msgs" >> "$outfile"
    fi
  done
  # Drop files with no real content so miners do not waste a read on them.
  if [ ! -s "$outfile" ] || [ "$(wc -c < "$outfile")" -lt 500 ]; then
    rm -f "$outfile"
  fi
done

wc -c "$OUT"/*.md 2>/dev/null | sort -rn
