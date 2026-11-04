#!/usr/bin/env python3
"""Join GitHub PRs to Linear issues and expose unaccounted bot PRs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path



# The profile reader is a required resource of the shared skill distribution.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skill-config" / "scripts"))
import skill_profile

def issue_pattern() -> re.Pattern:
    prefix = skill_profile.get("work.issue_prefix")
    if not isinstance(prefix, str) or not prefix.strip():
        raise ValueError("Configure work.issue_prefix before matching issues.")
    return re.compile(r"\b" + re.escape(prefix) + r"-\d+\b", re.IGNORECASE)


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected an object in {path}")
    return payload


def issue_identifier(pr: dict) -> str | None:
    text = "\n".join(str(pr.get(field) or "") for field in ("title", "body", "headRefName"))
    match = issue_pattern().search(text)
    return match.group(0).upper() if match else None


def ancestry(issue: dict | None) -> list[dict]:
    result: list[dict] = []
    current = issue
    while isinstance(current, dict):
        result.append(current)
        current = current.get("parent")
    return result


def requester_for(nodes: list[dict]) -> str | None:
    requesters = skill_profile.get("work.requester_aliases", default={})
    for node in nodes:
        creator = node.get("creator") or {}
        name = str(creator.get("name") or "").strip().lower()
        if name in requesters:
            return requesters[name]
    return None


def slack_links(nodes: list[dict]) -> list[str]:
    links: set[str] = set()
    for node in nodes:
        for attachment in (node.get("attachments") or {}).get("nodes") or []:
            url = str(attachment.get("url") or "")
            if "slack.com/" in url:
                links.add(url)
    return sorted(links)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--github", type=Path, required=True)
    parser.add_argument("--linear", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    github = load(args.github)
    linear = load(args.linear)
    issues = {
        str(issue.get("identifier") or "").upper(): issue
        for issue in linear.get("issues") or []
    }
    rows = []
    for pr in github.get("pull_requests") or []:
        if not pr.get("is_bot_authored"):
            continue
        identifier = issue_identifier(pr)
        issue = issues.get(identifier or "")
        nodes = ancestry(issue)
        requester = requester_for(nodes)
        links = slack_links(nodes)
        rows.append(
            {
                "pr_number": pr.get("number"),
                "pr_title": pr.get("title"),
                "pr_url": pr.get("url"),
                "linear_issue": identifier,
                "linear_ancestry": [node.get("identifier") for node in nodes],
                "origin_requester": requester,
                "origin_status": "resolved" if requester else "unresolved",
                "slack_links_to_inspect": links,
                "explicitly_requests_user": pr.get("explicitly_requests_user", False),
                "user_review_states": pr.get("user_review_states") or [],
                "last_user_activity_at": pr.get("last_user_activity_at"),
                "latest_commit": pr.get("latest_commit"),
                "pending_action_signals": pr.get("pending_action_signals") or [],
                "new_comments_after_user": pr.get("new_comments_after_user") or [],
                "new_reviews_after_user": pr.get("new_reviews_after_user") or [],
                "draft": pr.get("isDraft", False),
                "mergeable": pr.get("mergeable"),
                "updated_at": pr.get("updatedAt"),
            }
        )

    resolved = sum(row["origin_status"] == "resolved" for row in rows)
    payload = {
        "summary": {
            "open_bot_prs": len(rows),
            "origin_resolved": resolved,
            "origin_unresolved": len(rows) - resolved,
        },
        "bot_pull_requests": rows,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


if __name__ == "__main__":
    main()
