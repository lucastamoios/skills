#!/usr/bin/env python3
"""List recent root Codex and Claude sessions for meeting evidence."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SESSION_ROOTS = (
    ("codex", Path.home() / ".codex" / "sessions"),
    ("codex", Path.home() / ".codex" / "archived_sessions"),
    ("claude", Path.home() / ".claude" / "projects"),
)


def parse_timestamp(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.astimezone()
    return parsed


def normalize_for_comparison(value: datetime) -> datetime:
    return value.astimezone()


def iter_session_files() -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    for provider, root in SESSION_ROOTS:
        if not root.exists():
            continue
        files.extend((provider, path) for path in root.rglob("*.jsonl"))
    return files


def path_is_in_scope(cwd: str | None, scope: Path | None) -> bool:
    if scope is None:
        return True
    if not cwd:
        return False
    try:
        Path(cwd).expanduser().resolve().relative_to(scope)
        return True
    except (OSError, ValueError):
        return False


def inspect_session(
    provider: str,
    path: Path,
    since: datetime,
    until: datetime,
    scope: Path | None,
    include_children: bool,
) -> dict[str, Any] | None:
    cwd: str | None = None
    session_id: str | None = None
    is_child = False
    first_activity: datetime | None = None
    last_activity: datetime | None = None
    matching_records = 0

    try:
        with path.open(encoding="utf-8") as handle:
            for raw_line in handle:
                try:
                    record = json.loads(raw_line)
                except (json.JSONDecodeError, TypeError):
                    continue

                if provider == "codex" and record.get("type") == "session_meta":
                    payload = record.get("payload") or {}
                    cwd = payload.get("cwd") or cwd
                    session_id = (
                        payload.get("id")
                        or payload.get("session_id")
                        or session_id
                    )
                    source = payload.get("source") or {}
                    source_is_subagent = (
                        bool(source.get("subagent"))
                        if isinstance(source, dict)
                        else False
                    )
                    is_child = bool(
                        payload.get("parent_thread_id")
                        or source_is_subagent
                    )
                elif provider == "claude":
                    cwd = record.get("cwd") or cwd
                    session_id = record.get("sessionId") or session_id
                    is_child = is_child or bool(record.get("isSidechain"))

                raw_timestamp = record.get("timestamp")
                if not isinstance(raw_timestamp, str):
                    continue
                try:
                    timestamp = normalize_for_comparison(
                        parse_timestamp(raw_timestamp)
                    )
                except ValueError:
                    continue
                if since <= timestamp <= until:
                    matching_records += 1
                    first_activity = min(first_activity, timestamp) if first_activity else timestamp
                    last_activity = max(last_activity, timestamp) if last_activity else timestamp
    except OSError as error:
        print(f"Could not read {path}: {error}", file=sys.stderr)
        return None

    if not matching_records or not path_is_in_scope(cwd, scope):
        return None
    if is_child and not include_children:
        return None

    return {
        "provider": provider,
        "session_id": session_id or path.stem,
        "first_activity": first_activity.isoformat() if first_activity else None,
        "last_activity": last_activity.isoformat() if last_activity else None,
        "cwd": cwd,
        "kind": "child" if is_child else "root",
        "matching_records": matching_records,
        "archived": "archived_sessions" in path.parts,
        "path": str(path),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="List Codex and Claude sessions active in a time window."
    )
    parser.add_argument("--since", required=True, help="Inclusive ISO timestamp.")
    parser.add_argument("--until", required=True, help="Inclusive ISO timestamp.")
    parser.add_argument(
        "--scope",
        help="Only include sessions whose working directory is inside this path.",
    )
    parser.add_argument(
        "--include-children",
        action="store_true",
        help="Include Codex child-agent and Claude sidechain sessions.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of sessions to return. Defaults to 100.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        since = normalize_for_comparison(parse_timestamp(args.since))
        until = normalize_for_comparison(parse_timestamp(args.until))
    except ValueError as error:
        print(f"Invalid timestamp: {error}", file=sys.stderr)
        return 2

    if since > until:
        print("--since must not be later than --until.", file=sys.stderr)
        return 2
    if args.limit < 1:
        print("--limit must be at least 1.", file=sys.stderr)
        return 2

    scope = Path(args.scope).expanduser().resolve() if args.scope else None
    sessions = []
    for provider, path in iter_session_files():
        try:
            if path.stat().st_mtime < since.timestamp():
                continue
        except OSError as error:
            print(f"Could not inspect {path}: {error}", file=sys.stderr)
            continue
        session = inspect_session(
            provider,
            path,
            since,
            until,
            scope,
            args.include_children,
        )
        if session:
            sessions.append(session)

    sessions.sort(key=lambda item: item["last_activity"] or "", reverse=True)
    print(json.dumps(sessions[: args.limit], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
