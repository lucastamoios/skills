#!/usr/bin/env python3
"""Capture and check review source identity without changing the checkout."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys


def git(repo, *args):
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], stderr=subprocess.PIPE
    )


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def capture(repo, base):
    root = Path(os.fsdecode(git(repo, "rev-parse", "--show-toplevel")).strip()).resolve()
    head = git(root, "rev-parse", "HEAD^{commit}").decode().strip()
    base_sha = git(root, "rev-parse", f"{base}^{{commit}}").decode().strip()
    entries = git(root, "ls-files", "--stage", "-z").split(b"\0")
    if any(entry.startswith(b"160000 ") for entry in entries):
        raise ValueError("Submodules need separately pinned snapshots; capture is incomplete.")
    names = set(git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0"))
    files = {}
    for raw in sorted(names - {b""}):
        name = os.fsdecode(raw)
        path = root / name
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            files[name] = {"kind": "missing"}
            continue
        if stat.S_ISLNK(mode):
            files[name] = {"kind": "symlink", "target": os.readlink(path)}
        elif stat.S_ISREG(mode):
            checksum = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    checksum.update(chunk)
            files[name] = {"kind": "file", "sha256": checksum.hexdigest(), "executable": bool(mode & 0o111)}
        else:
            raise ValueError(f"Unsupported source entry needs an explicit snapshot: {name}")
    if git(root, "rev-parse", "HEAD^{commit}").decode().strip() != head:
        raise ValueError("HEAD changed during capture; retry in an isolated checkout.")
    content = {"contract": "review-snapshot/v1", "base": base_sha, "head": head, "files": files}
    return {"repository": str(root), "snapshot_id": digest(content), **content}


def check(manifest):
    data = json.loads(Path(manifest).read_text())
    content = {key: data[key] for key in ("contract", "base", "head", "files")}
    if data["contract"] != "review-snapshot/v1" or digest(content) != data["snapshot_id"]:
        raise ValueError("Snapshot manifest is invalid or was modified.")
    current = capture(data["repository"], data["base"])
    if current["snapshot_id"] != data["snapshot_id"]:
        raise ValueError("Snapshot is stale: source contents or HEAD changed.")
    return data["snapshot_id"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    make = commands.add_parser("capture")
    make.add_argument("--repo", required=True)
    make.add_argument("--base", required=True)
    make.add_argument("--output", required=True)
    verify = commands.add_parser("check")
    verify.add_argument("--manifest", required=True)
    args = parser.parse_args()
    try:
        if args.command == "check":
            print(check(args.manifest))
        else:
            data = capture(args.repo, args.base)
            output = Path(args.output).resolve()
            if output.is_relative_to(Path(data["repository"])):
                raise ValueError("Write the manifest outside the reviewed repository.")
            # A second observation catches changes during a long initial scan.
            if capture(args.repo, args.base)["snapshot_id"] != data["snapshot_id"]:
                raise ValueError("Source changed during capture; use an isolated checkout.")
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("x") as stream:
                json.dump(data, stream, indent=2, ensure_ascii=True)
                stream.write("\n")
            print(data["snapshot_id"])
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(f"Snapshot error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
