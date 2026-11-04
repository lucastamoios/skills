#!/usr/bin/env python3
"""Read private skill configuration without resolving credentials."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


def profile_path(path: str | Path | None = None) -> Path:
    return Path(path or os.environ.get("SKILLS_CONFIG") or
                "~/.config/agent-skills/config.json").expanduser().absolute()


def load(path: str | Path | None = None, *, required: bool = True) -> dict:
    source = profile_path(path)
    if not source.is_file():
        if required:
            raise ValueError("Private skill configuration is missing. Configure SKILLS_CONFIG or run skill-config setup.")
        return {}
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raise ValueError("Private skill configuration is not valid JSON.") from None
    if not isinstance(value, dict) or value.get("version") != 1:
        raise ValueError("Private skill configuration must be an object with version 1.")
    for key in ("user", "paths", "work", "contexts", "integrations", "timesheet", "marketing", "execution"):
        if key in value and not isinstance(value[key], dict):
            raise ValueError(f"Configuration section {key} must be an object.")
    return value


def get(key: str, path: str | Path | None = None, *, default: Any = None) -> Any:
    value: Any = load(path, required=False)
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value


def resolve_path(value: str, path: str | Path | None = None) -> Path:
    result = Path(value).expanduser()
    if not result.is_absolute():
        result = profile_path(path).resolve().parent / result
    return result.resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check")
    query = commands.add_parser("get")
    query.add_argument("key")
    query.add_argument("--json", action="store_true")
    query.add_argument("--path", action="store_true", help="Resolve a configured file or directory path")
    init = commands.add_parser("init")
    init.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "init":
            example = Path(__file__).resolve().parents[1] / "references/profile.example.json"
            target = args.output.expanduser()
            target.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w") as stream:
                stream.write(example.read_text(encoding="utf-8"))
            print("Created private profile. Complete the selected modules before use.")
        elif args.command == "check":
            load(args.config)
            print("Private skill configuration is valid (version 1).")
        else:
            load(args.config)
            value = get(args.key, args.config)
            if value is None or value == "":
                raise ValueError(f"Configure {args.key} before using this integration.")
            if args.path:
                if not isinstance(value, str):
                    raise ValueError("A configured path must be a string.")
                value = str(resolve_path(value, args.config))
            print(json.dumps(value, ensure_ascii=False) if args.json or isinstance(value, (dict, list)) else value)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.exit(2, f"Configuration error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
