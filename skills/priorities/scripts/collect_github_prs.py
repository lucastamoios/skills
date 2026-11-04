#!/usr/bin/env python3
"""Collect every open PR and classify review signals locally."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
# The profile reader is a required resource of the shared skill distribution.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skill-config" / "scripts"))
import skill_profile




FIELDS = (
    "number,title,url,author,isDraft,reviewRequests,reviews,comments,commits,"
    "statusCheckRollup,mergeable,updatedAt,createdAt,headRefName,baseRefName,body"
)
DEFAULT_BOT_MARKERS = ()


def run_gh(repo: str, limit: int) -> list[dict]:
    command = [
        "gh",
        "pr",
        "list",
        "--repo",
        repo,
        "--state",
        "open",
        "--limit",
        str(limit),
        "--json",
        FIELDS,
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode:
        message = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"gh pr list failed: {message}")
    payload = json.loads(completed.stdout)
    if not isinstance(payload, list):
        raise ValueError("gh pr list returned a non-list payload")
    return payload


def login(value: object) -> str:
    if not isinstance(value, dict):
        return ""
    raw = value.get("login")
    return raw if isinstance(raw, str) else ""


def activity_time(value: dict, *fields: str) -> str:
    for field in fields:
        raw = value.get(field)
        if isinstance(raw, str) and raw:
            return raw
    return ""


def summarize_activity(value: dict, *, timestamp_fields: tuple[str, ...]) -> dict:
    body = value.get("body")
    return {
        "author_login": login(value.get("author")),
        "at": activity_time(value, *timestamp_fields),
        "body": body[:1000] if isinstance(body, str) else "",
        "state": value.get("state"),
        "url": value.get("url"),
    }


def classify(pr: dict, *, user_login: str, bot_markers: tuple[str, ...]) -> dict:
    rendered_pr = {
        key: value for key, value in pr.items() if key not in {"comments", "commits"}
    }
    author_login = login(pr.get("author"))
    author_lower = author_login.lower()
    requested = sorted(
        {
            candidate
            for item in pr.get("reviewRequests") or []
            if (candidate := login(item))
        }
    )
    reviews = pr.get("reviews") or []
    comments = pr.get("comments") or []
    commits = pr.get("commits") or []
    user_reviews = [
        review
        for review in reviews
        if login(review.get("author")).lower() == user_login.lower()
    ]
    user_comments = [
        comment
        for comment in comments
        if login(comment.get("author")).lower() == user_login.lower()
    ]
    latest_commit = commits[-1] if commits else {}
    baseline_times = [
        activity_time(review, "submittedAt") for review in user_reviews
    ] + [
        activity_time(comment, "createdAt", "updatedAt") for comment in user_comments
    ]
    if author_lower == user_login.lower():
        baseline_times.append(activity_time(latest_commit, "committedDate", "authoredDate"))
    baseline_times = [value for value in baseline_times if value]
    last_user_activity_at = max(baseline_times, default="")
    in_user_scope = (
        author_lower == user_login.lower()
        or user_login.lower() in {item.lower() for item in requested}
        or any(marker in author_lower for marker in bot_markers)
        or bool(user_reviews)
        or bool(user_comments)
    )
    external_comments = [
        comment
        for comment in comments
        if login(comment.get("author")).lower() != user_login.lower()
        and activity_time(comment, "createdAt", "updatedAt") > last_user_activity_at
    ] if in_user_scope else []
    external_reviews = [
        review
        for review in reviews
        if login(review.get("author")).lower() != user_login.lower()
        and activity_time(review, "submittedAt") > last_user_activity_at
    ] if in_user_scope else []
    latest_user_review_at = max(
        (activity_time(review, "submittedAt") for review in user_reviews),
        default="",
    )
    latest_commit_at = activity_time(latest_commit, "committedDate", "authoredDate")
    pending_action_signals = []
    if user_login.lower() in {item.lower() for item in requested}:
        pending_action_signals.append("review_requested")
    if external_comments:
        pending_action_signals.append("new_issue_comment_after_user")
    if external_reviews:
        pending_action_signals.append("new_review_after_user")
    if latest_user_review_at and latest_commit_at > latest_user_review_at:
        pending_action_signals.append("new_commit_after_user_review")
    return {
        **rendered_pr,
        "author_login": author_login,
        "is_bot_authored": any(marker in author_lower for marker in bot_markers),
        "is_user_authored": author_lower == user_login.lower(),
        "requested_reviewer_logins": requested,
        "explicitly_requests_user": user_login.lower() in {item.lower() for item in requested},
        "user_review_states": [review.get("state") for review in user_reviews],
        "last_user_activity_at": last_user_activity_at or None,
        "latest_commit": {
            "oid": latest_commit.get("oid"),
            "at": latest_commit_at or None,
            "headline": latest_commit.get("messageHeadline"),
        } if latest_commit else None,
        "new_comments_after_user": [
            summarize_activity(comment, timestamp_fields=("createdAt", "updatedAt"))
            for comment in external_comments[-5:]
        ],
        "new_reviews_after_user": [
            summarize_activity(review, timestamp_fields=("submittedAt",))
            for review in external_reviews[-5:]
        ],
        "pending_action_signals": pending_action_signals,
    }


def write_json(payload: object, output: Path | None) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output:
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=skill_profile.get("work.github_repository"))
    parser.add_argument("--user-login", default=skill_profile.get("work.github_login") or skill_profile.get("user.github_login"))
    parser.add_argument("--bot-marker", action="append", dest="bot_markers")
    parser.add_argument("--limit", type=int, default=250)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.repo or not args.user_login:
        parser.error("Configure work.github_repository and work.github_login, or pass --repo and --user-login.")
    markers = tuple(marker.lower() for marker in (args.bot_markers or skill_profile.get("work.bot_markers", default=[]) or DEFAULT_BOT_MARKERS))
    pull_requests = [
        classify(pr, user_login=args.user_login, bot_markers=markers)
        for pr in run_gh(args.repo, args.limit)
    ]
    write_json(
        {
            "repository": args.repo,
            "user_login": args.user_login,
            "bot_markers": markers,
            "pull_requests": pull_requests,
        },
        args.output,
    )


if __name__ == "__main__":
    main()
