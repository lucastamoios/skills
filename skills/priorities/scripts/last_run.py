#!/usr/bin/env python3
"""Read and update the successful-run window for the priorities skill."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path


DEFAULT_STATE_PATH = Path.home() / "brain" / ".codex" / "state" / "priorities.json"
SLACK_LOOKBACK = timedelta(days=7)


def parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def load_state(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"State file must contain an object: {path}")
    return data


def window(path: Path) -> None:
    now = datetime.now(timezone.utc)
    state = load_state(path)
    stored = state.get("last_successful_run")
    first_run = stored is None
    slack_cutoff = now if first_run else parse_timestamp(stored)
    since = slack_cutoff - SLACK_LOOKBACK
    print(
        json.dumps(
            {
                "since": format_timestamp(since),
                "until": format_timestamp(now),
                "first_run": first_run,
                "state_path": str(path),
            }
        )
    )


def mark(path: Path, timestamp: str | None) -> None:
    value = parse_timestamp(timestamp) if timestamp else datetime.now(timezone.utc)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"last_successful_run": format_timestamp(value)}
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    os.replace(temporary, path)
    print(json.dumps({**payload, "state_path": str(path)}))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--state",
        type=Path,
        default=DEFAULT_STATE_PATH,
        help="Override the state file path.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("window")
    mark_parser = subparsers.add_parser("mark")
    mark_parser.add_argument(
        "--timestamp",
        help="ISO 8601 timestamp to store. Defaults to the current time.",
    )
    args = parser.parse_args()

    if args.command == "window":
        window(args.state)
    else:
        mark(args.state, args.timestamp)


if __name__ == "__main__":
    main()
