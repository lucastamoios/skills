#!/usr/bin/env python3
"""Collect normalized access records from BRCondos."""

from __future__ import annotations

import argparse
import calendar
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Protocol


SOURCE = "BRCondos /Persons/AccessHistory"


class CollectionClient(Protocol):
    def collect(
        self,
        *,
        login: str,
        password: str,
        date_start: str,
        date_end: str,
        person: str,
        headed: bool,
        max_pages: int,
    ) -> list[dict[str, str]]: ...


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect one person's monthly BRCondos access records."
    )
    parser.add_argument("--month", required=True, help="Reference month as YYYY-MM")
    parser.add_argument("--person", required=True, help="Exact person name in BRCondos")
    parser.add_argument("--output", required=True, type=Path, help="Destination JSON file")
    parser.add_argument("--headed", action="store_true", help="Show the browser window")
    parser.add_argument("--max-pages", type=int, default=50)
    return parser


def month_bounds(value: str) -> tuple[str, str]:
    try:
        year_text, month_text = value.split("-", 1)
        year, month = int(year_text), int(month_text)
        last_day = calendar.monthrange(year, month)[1]
    except (TypeError, ValueError) as exc:
        raise ValueError("Month must use the YYYY-MM format") from exc
    return (
        f"01/{month:02d}/{year:04d} 00:00:00",
        f"{last_day:02d}/{month:02d}/{year:04d} 23:59:59",
    )


def required_credential(env: Mapping[str, str], name: str) -> str:
    value = env.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Set {name} before running the collector")
    return value


def run(
    argv: Sequence[str],
    *,
    env: Mapping[str, str],
    client: CollectionClient,
) -> int:
    args = build_parser().parse_args(argv)
    date_start, date_end = month_bounds(args.month)
    records = client.collect(
        login=required_credential(env, "BRCONDOS_LOGIN"),
        password=required_credential(env, "BRCONDOS_PASSWORD"),
        date_start=date_start,
        date_end=date_end,
        person=args.person,
        headed=args.headed,
        max_pages=args.max_pages,
    )
    payload = {"source": SOURCE, "records": records}
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


def main() -> int:
    raise RuntimeError("The Playwright BRCondos client is not implemented yet")


if __name__ == "__main__":
    raise SystemExit(main())
