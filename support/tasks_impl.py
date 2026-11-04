#!/usr/bin/env python3
"""Manage Obsidian task notes in the brain vault."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path


BRAIN = Path(__file__).resolve().parents[1]
TASKS = Path(os.environ.get("BRAIN_TASKS_DIR", BRAIN / "vault" / "tasks"))
ARCHIVE = TASKS / "archive"
TEMPLATE = TASKS / "task-template.md"
LANES = (
    "To Do",
    "Today",
    "In Progress",
    "Review",
    "Done",
    "Delegated",
    "Scheduled",
    "Blocked",
    "Maybe",
)


def fail(message: str) -> None:
    raise SystemExit(f"tasks: {message}")


def split_note(text: str) -> tuple[list[str], str]:
    if not text.startswith("---\n"):
        fail("task note has no YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        fail("task note has unterminated YAML frontmatter")
    return text[4:end].splitlines(), text[end + 5 :]


def scalar(value: str) -> str | int | None:
    value = value.strip()
    if not value or value in {"null", "~"}:
        return None
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def parse_frontmatter(lines: list[str]) -> dict[str, object]:
    values: dict[str, object] = {}
    active_list: str | None = None
    for line in lines:
        item = re.match(r"^\s+-\s+(.*)$", line)
        if item and active_list:
            if not isinstance(values.get(active_list), list):
                values[active_list] = []
            cast = values[active_list]
            if isinstance(cast, list):
                cast.append(scalar(item.group(1)))
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:\s*(.*))?$", line)
        if not match:
            active_list = None
            continue
        key, raw = match.group(1), match.group(2) or ""
        if raw.strip() == "[]":
            values[key] = []
            active_list = None
        elif not raw.strip():
            values[key] = None
            active_list = key
        else:
            values[key] = scalar(raw)
            active_list = None
    return values


def yaml_scalar(value: object) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if re.fullmatch(r"[A-Za-z0-9_./:@+-]+", text) and text.lower() not in {
        "true", "false", "null", "yes", "no",
    }:
        return text
    return json.dumps(text, ensure_ascii=False)


def set_property(lines: list[str], key: str, value: object) -> list[str]:
    start = next((i for i, line in enumerate(lines) if re.match(rf"^{re.escape(key)}:", line)), None)
    replacement = f"{key}: {yaml_scalar(value)}".rstrip()
    if start is None:
        return lines + [replacement]
    end = start + 1
    while end < len(lines) and (lines[end].startswith("  ") or not lines[end].strip()):
        end += 1
    return lines[:start] + [replacement] + lines[end:]


def title_from_body(body: str) -> str:
    match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    return match.group(1).strip() if match else "Untitled task"


def task_title(body: str, props: dict[str, object]) -> str:
    return str(props.get("title") or title_from_body(body))


def task_files() -> list[Path]:
    return sorted(path for path in TASKS.glob("*.md") if path.name not in {"index.md", TEMPLATE.name})


def load(path: Path) -> tuple[list[str], str, dict[str, object]]:
    lines, body = split_note(path.read_text())
    return lines, body, parse_frontmatter(lines)


def resolve(identifier: str) -> Path:
    candidate = TASKS / f"{identifier.removesuffix('.md')}.md"
    if candidate.is_file() and candidate.name not in {"index.md", TEMPLATE.name}:
        return candidate
    matches = [path for path in task_files() if path.stem.casefold() == identifier.casefold()]
    if len(matches) == 1:
        return matches[0]
    fail(f"task '{identifier}' not found")


def save(path: Path, lines: list[str], body: str) -> None:
    path.write_text("---\n" + "\n".join(lines) + "\n---\n" + body)


def append_history(body: str, entry: str) -> str:
    marker = "## History"
    if marker not in body:
        return body.rstrip() + f"\n\n{marker}\n\n- {entry}\n"
    return body.rstrip() + f"\n- {entry}\n"


def append_note(body: str, note: str) -> str:
    entry = f"- {dt.date.today().isoformat()}: {note}"
    marker = "## Notes"
    history = "## History"
    if marker not in body:
        insertion = f"\n\n{marker}\n\n{entry}\n"
        if history in body:
            return body.replace(history, insertion + "\n" + history, 1)
        return body.rstrip() + insertion
    if history in body:
        before, after = body.split(history, 1)
        return before.rstrip() + f"\n{entry}\n\n{history}" + after
    return body.rstrip() + f"\n{entry}\n"


def command_list(args: argparse.Namespace) -> None:
    for path in task_files():
        _, body, props = load(path)
        status = str(props.get("status") or "To Do")
        if args.lane and status.casefold() != args.lane.casefold():
            continue
        if not args.all and status in {"Done", "Delegated"}:
            continue
        realm = str(props.get("realm") or "-").replace("[[", "").replace("]]", "")
        print(
            f"{path.stem}\t[{status}]\t{realm}\t"
            f"impact={props.get('impact') or '-'}\t"
            f"effort={props.get('effort_minutes') or '-'}m\t{task_title(body, props)}"
        )


def command_get(args: argparse.Namespace) -> None:
    path = resolve(args.id)
    _, body, props = load(path)
    print(json.dumps({"id": path.stem, **props, "title": task_title(body, props), "path": str(path)}, indent=2))


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-")
    return slug or f"task-{dt.datetime.now().strftime('%Y%m%d%H%M%S')}"


def wikilink(value: str | None) -> str | None:
    """Wrap a value in wikilink brackets, tolerating a caller that already did."""
    if not value:
        return None
    inner = value.strip().strip("[]").strip()
    return f"[[{inner}]]" if inner else None


def linear_ticket(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"\b([A-Za-z]+-\d+)\b", value)
    return match.group(1).upper() if match else None


def pull_request_number(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"github\.com/[^/]+/[^/]+/pull/(\d+)", value, re.IGNORECASE)
    return int(match.group(1)) if match else None


def command_add(args: argparse.Namespace) -> None:
    slug = slugify(args.title)
    path = TASKS / f"{slug}.md"
    counter = 2
    while path.exists():
        path = TASKS / f"{slug}-{counter}.md"
        counter += 1
    today = dt.date.today().isoformat()
    lines, body = split_note(TEMPLATE.read_text())
    updates = {
        "title": args.title,
        "status": args.lane,
        "task_type": args.type,
        "realm": wikilink(args.realm),
        "effort_minutes": args.effort,
        "impact": args.impact,
        "work_type": args.worktype,
        "linear_ticket": args.ticket or linear_ticket(args.linear) or linear_ticket(args.title),
        "pr_number": args.pr or pull_request_number(args.git),
        "git_url": args.git,
        "linear_url": args.linear,
        "created": today,
        "updated": today,
    }
    for key, value in updates.items():
        lines = set_property(lines, key, value)
    body = body.replace("# Task title", f"# {args.title}", 1)
    if args.description:
        body = body.replace(
            "Describe what will be true when this task is complete.", args.description, 1
        )
    body = body.replace("- Created on YYYY-MM-DD in To Do.", f"- Created on {today} in {args.lane}.")
    save(path, lines, body)
    print(f"created task {path.stem} in lane '{args.lane}'")


def command_move(args: argparse.Namespace) -> None:
    if args.lane not in LANES:
        fail(f"unknown lane '{args.lane}'")
    path = resolve(args.id)
    lines, body, props = load(path)
    old = str(props.get("status") or "To Do")
    today = dt.date.today().isoformat()
    lines = set_property(lines, "status", args.lane)
    lines = set_property(lines, "updated", today)
    lines = set_property(lines, "completed", today if args.lane == "Done" else None)
    body = append_history(body, f"Moved from {old} to {args.lane} on {today}.")
    save(path, lines, body)
    print(f"moved task {path.stem} from '{old}' to '{args.lane}'")


def command_note(args: argparse.Namespace) -> None:
    path = resolve(args.id)
    lines, body, _ = load(path)
    lines = set_property(lines, "updated", dt.date.today().isoformat())
    save(path, lines, append_note(body, args.text))
    print(f"noted task {path.stem}")


def command_update(args: argparse.Namespace) -> None:
    path = resolve(args.id)
    lines, body, _ = load(path)
    updates = {
        "task_type": args.type,
        "realm": wikilink(args.realm),
        "effort_minutes": args.effort,
        "impact": args.impact,
        "work_type": args.worktype,
        "linear_ticket": args.ticket or linear_ticket(args.linear),
        "pr_number": args.pr or pull_request_number(args.git),
        "git_url": args.git,
        "linear_url": args.linear,
    }
    for key, value in updates.items():
        if value is not None:
            lines = set_property(lines, key, value)
    if args.title:
        lines = set_property(lines, "title", args.title)
        body = re.sub(r"^#\s+.+$", f"# {args.title}", body, count=1, flags=re.MULTILINE)
    lines = set_property(lines, "updated", dt.date.today().isoformat())
    save(path, lines, body)
    print(f"updated task {path.stem}")


def command_archive(args: argparse.Namespace) -> None:
    paths = task_files() if args.all_done else [resolve(args.id)]
    eligible: list[tuple[Path, list[str], str, Path | None]] = []
    for path in paths:
        lines, body, props = load(path)
        task_status = str(props.get("status") or "To Do")
        if task_status != "Done":
            if args.all_done:
                continue
            fail(f"task '{path.stem}' must be Done before it can be archived")
        destination = ARCHIVE / path.name
        if destination.exists():
            fail(f"archived task '{path.stem}' already exists")
        companion = TASKS / path.stem
        if companion.exists():
            if not companion.is_dir() or companion.is_symlink():
                fail(f"task '{path.stem}' has a non-directory companion path")
            if (ARCHIVE / companion.name).exists():
                fail(f"archived files for task '{path.stem}' already exist")
        else:
            companion = None
        eligible.append((path, lines, body, companion))

    if not eligible:
        print("no Done tasks to archive")
        return

    today = dt.date.today().isoformat()
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    for path, lines, body, companion in eligible:
        lines = set_property(lines, "updated", today)
        lines = set_property(lines, "archived", today)
        body = append_history(body, f"Archived on {today}.")
        save(path, lines, body)
        path.replace(ARCHIVE / path.name)
        if companion is not None:
            companion.replace(ARCHIVE / companion.name)
        print(f"archived task {path.stem}")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("list")
    listing.add_argument("--lane")
    listing.add_argument("--all", action="store_true")
    listing.set_defaults(run=command_list)
    get = sub.add_parser("get")
    get.add_argument("--id", required=True)
    get.set_defaults(run=command_get)
    add = sub.add_parser("add")
    add.add_argument("--title", required=True)
    add.add_argument("--lane", choices=LANES, default="To Do")
    add.add_argument("--type", choices=("Review", "Implement", "Investigate", "Plan", "Write", "Fix"))
    add.add_argument("--realm")
    add.add_argument("--description")
    add.add_argument("--effort", type=int)
    add.add_argument("--impact", type=int, choices=(1, 2, 4, 8, 16))
    add.add_argument("--worktype", choices=("proactive", "reactive"), default="proactive")
    add.add_argument("--git")
    add.add_argument("--linear")
    add.add_argument("--ticket")
    add.add_argument("--pr", type=int)
    add.set_defaults(run=command_add)
    move = sub.add_parser("move")
    move.add_argument("--id", required=True)
    move.add_argument("--lane", required=True)
    move.set_defaults(run=command_move)
    note = sub.add_parser("note")
    note.add_argument("--id", required=True)
    note.add_argument("--text", required=True)
    note.set_defaults(run=command_note)
    update = sub.add_parser("update")
    update.add_argument("--id", required=True)
    update.add_argument("--title")
    update.add_argument("--type", choices=("Review", "Implement", "Investigate", "Plan", "Write", "Fix"))
    update.add_argument("--realm")
    update.add_argument("--effort", type=int)
    update.add_argument("--impact", type=int, choices=(1, 2, 4, 8, 16))
    update.add_argument("--worktype", choices=("proactive", "reactive"))
    update.add_argument("--git")
    update.add_argument("--linear")
    update.add_argument("--ticket")
    update.add_argument("--pr", type=int)
    update.set_defaults(run=command_update)
    archive = sub.add_parser("archive")
    archive_target = archive.add_mutually_exclusive_group(required=True)
    archive_target.add_argument("--id")
    archive_target.add_argument("--all-done", action="store_true")
    archive.set_defaults(run=command_archive)
    return root


if __name__ == "__main__":
    arguments = parser().parse_args()
    arguments.run(arguments)
