#!/usr/bin/env python3
"""Collect open Linear issues with parent and source-link metadata."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


QUERY = """
query OpenIssues($first: Int!, $after: String) {
  issues(
    first: $first
    after: $after
    filter: { state: { type: { nin: ["completed", "canceled"] } } }
  ) {
    pageInfo { hasNextPage endCursor }
    nodes {
      id identifier title url priority createdAt updatedAt
      state { name type }
      creator { id name email }
      assignee { id name email }
      delegate { id name }
      parent {
        id identifier title url
        creator { id name email }
        attachments { nodes { title subtitle url } }
        parent {
          id identifier title url
          creator { id name email }
          attachments { nodes { title subtitle url } }
        }
      }
      attachments { nodes { title subtitle url } }
      labels { nodes { name } }
    }
  }
}
"""

def resolve_api_key() -> str:
    """Use the Linear credential already loaded by the shared agent environment."""
    api_key = os.environ.get("LINEAR_API_KEY", "").strip()
    if not api_key or api_key.startswith("op://"):
        raise RuntimeError(
            "LINEAR_API_KEY is missing or unresolved. "
            "Inject the configured environment before running this collector. "
            "Do not request or print the key in chat."
        )
    return api_key


def graphql(api_key: str, variables: dict) -> dict:
    request = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": api_key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        raise RuntimeError(f"Linear returned HTTP {error.code}: {body}") from None
    if payload.get("errors"):
        messages = "; ".join(error.get("message", "unknown error") for error in payload["errors"])
        raise RuntimeError(f"Linear GraphQL failed: {messages}")
    return payload["data"]["issues"]


def collect(api_key: str) -> list[dict]:
    issues: list[dict] = []
    cursor: str | None = None
    while True:
        connection = graphql(api_key, {"first": 250, "after": cursor})
        issues.extend(connection["nodes"])
        page_info = connection["pageInfo"]
        if not page_info["hasNextPage"]:
            return issues
        cursor = page_info["endCursor"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        api_key = resolve_api_key()
    except RuntimeError as error:
        raise SystemExit(str(error)) from None
    payload = {"issues": collect(api_key)}
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


if __name__ == "__main__":
    main()
