#!/usr/bin/env python3
"""Fill and check the symbol anchors of a Lighthouse PR explanation draft.

Usage: fill_anchors.py [--relocate] DRAFT.json OUT.json

An anchor with `path` and `line` but no `text` gets `text` copied from the file
at the document's `head_sha`: `span` lines (default 2) starting at `line`, and
`span` is removed. An anchor that already has `text` is checked against the head.
File anchors must name a file that exists at the head. With --relocate, an anchor
whose text is not at its line but occurs exactly once in the file gets that line,
and the move is printed as a note. The output is written only when every anchor
is valid; problems are printed and the exit status is 1.
"""

import json
import re
import subprocess
import sys
import urllib.parse

MAX_LINES = 40
MAX_BYTES = 4096


def split_lines(text):
    return re.split(r"\r\n|\r|\n", text)


def normalized(text):
    if text.endswith("\r\n"):
        text = text[:-2]
    elif text.endswith(("\n", "\r")):
        text = text[:-1]
    return [line.rstrip() for line in split_lines(text)]


def gh_fetch(repository, sha, path):
    """Return the file text at `sha`, or None when the path is not a file there."""
    url = f"repos/{repository}/contents/{urllib.parse.quote(path)}?ref={sha}"
    result = subprocess.run(
        ["gh", "api", "-H", "Accept: application/vnd.github.raw", url],
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8")


def fill(document, fetch, relocate=False):
    """Fill missing anchor text in place and return a list of problems."""
    cache = {}

    def source(path):
        if path not in cache:
            cache[path] = fetch(document["repository"], document["head_sha"], path)
        return cache[path]

    problems = []
    warnings = []
    for anchor_id, anchor in document.get("anchors", {}).items():
        path = anchor.get("path")
        if not path or anchor.get("absent"):
            continue
        text = source(path)
        if text is None:
            problems.append(f"anchors.{anchor_id}: {path} is not a file at head")
            continue
        if "line" not in anchor:
            continue
        line = anchor["line"]
        file_lines = split_lines(text)
        if "text" not in anchor:
            span = anchor.pop("span", 2)
            if not isinstance(line, int) or line < 1 or line > len(file_lines):
                problems.append(f"anchors.{anchor_id}: line {line} outside {path}")
                continue
            anchor["text"] = "\n".join(file_lines[line - 1 : line - 1 + span])
        expected = normalized(anchor["text"])
        if len(expected) > MAX_LINES or len(anchor["text"].encode()) > MAX_BYTES:
            problems.append(f"anchors.{anchor_id}: text over 40 lines or 4 KiB")
        if not any(expected):
            problems.append(f"anchors.{anchor_id}: text has no non-blank line")
            continue
        actual = [item.rstrip() for item in file_lines]
        found = [
            start + 1
            for start in range(len(actual) - len(expected) + 1)
            if actual[start : start + len(expected)] == expected
        ]
        if line not in found and relocate and len(found) == 1:
            anchor["line"] = found[0]
            warnings.append(f"anchors.{anchor_id}: moved from line {line} to line {found[0]} of {path}")
        elif line not in found:
            where = f"found at {found}" if found else "not found"
            problems.append(f"anchors.{anchor_id}: text not at line {line} of {path} ({where})")
        elif len(found) > 1:
            warnings.append(f"anchors.{anchor_id}: text also occurs at {found}; widen span")
    problems.extend(unknown_inline_anchors(document))
    return problems, warnings


def unknown_inline_anchors(document):
    """Lighthouse accepts an unknown [[id]] but shows it as unresolved, so catch it here."""
    anchors = document.get("anchors", {})
    texts = [(f"overview.{key}", value) for key, value in document.get("overview", {}).items()]
    texts += [(f"items.{item.get('id')}", item.get("text", "")) for item in document.get("items", [])]
    texts += [(f"files[{path!r}]", value) for path, value in document.get("files", {}).items()]
    problems = []
    for where, text in texts:
        if not isinstance(text, str):
            continue
        for anchor_id in re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", text):
            if anchor_id not in anchors:
                problems.append(f"{where}: [[{anchor_id}]] is not an anchor id")
    return problems


def main():
    args = sys.argv[1:]
    relocate = "--relocate" in args
    draft_path, out_path = [arg for arg in args if arg != "--relocate"]
    with open(draft_path, encoding="utf-8") as handle:
        document = json.load(handle)
    problems, warnings = fill(document, gh_fetch, relocate)
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        sys.exit(1)
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(document, handle, ensure_ascii=False, indent=1)
    print(f"wrote {out_path}: {len(document.get('anchors', {}))} anchors checked")


if __name__ == "__main__":
    main()
