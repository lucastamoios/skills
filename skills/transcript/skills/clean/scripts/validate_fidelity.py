#!/usr/bin/env python3
"""Detect transcript cleanup outputs that may have become summaries."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


WORD_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)?|\d+", re.UNICODE)
TIMESTAMP_RE = re.compile(
    r"^\*\*.*?\((\d{1,2}:\d{2}(?::\d{2})?)\)", re.MULTILINE
)
BOLD_SPEAKER_RE = re.compile(r"^\*\*[^*\n]{1,120}:\*\*", re.MULTILINE)
PLAIN_TURN_RE = re.compile(
    r"^(?:Speaker(?: \d+)?|[A-ZÀ-Ý][A-Za-zÀ-ÿ .'-]{0,60}):(?:\s*$|\s*[\"″])",
    re.MULTILINE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare a cleaned transcript with one or more raw sources."
    )
    parser.add_argument(
        "--raw",
        action="append",
        required=True,
        type=Path,
        help="Raw source path. Repeat this option for a consolidated transcript.",
    )
    parser.add_argument("--cleaned", required=True, type=Path)
    parser.add_argument("--review-ratio", type=float, default=0.65)
    parser.add_argument("--critical-ratio", type=float, default=0.35)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    return text[end + 5 :] if end >= 0 else text


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def turn_count(text: str) -> int:
    timestamped_turns = len(TIMESTAMP_RE.findall(text))
    if timestamped_turns:
        return timestamped_turns
    bold_turns = len(BOLD_SPEAKER_RE.findall(text))
    if bold_turns:
        return bold_turns
    return len(PLAIN_TURN_RE.findall(text))


def timestamp_seconds(value: str) -> int:
    parts = [int(part) for part in value.split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def backward_timestamp_count(text: str) -> int:
    timestamps = [timestamp_seconds(value) for value in TIMESTAMP_RE.findall(text)]
    return sum(current < previous for previous, current in zip(timestamps, timestamps[1:]))


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def classify(
    word_ratio: float | None,
    turn_ratio: float | None,
    backward_timestamps: int,
    raw_source_count: int,
    review_ratio: float,
    critical_ratio: float,
) -> tuple[str, list[str]]:
    reasons: list[str] = []

    for label, value in (("word", word_ratio), ("turn", turn_ratio)):
        if value is not None and value < critical_ratio:
            reasons.append(f"{label} retention is below {critical_ratio:.0%}")

    if backward_timestamps and raw_source_count == 1:
        reasons.append("cleaned timestamps move backward within one source")

    if reasons:
        return "critical", reasons

    for label, value in (("word", word_ratio), ("turn", turn_ratio)):
        if value is not None and value < review_ratio:
            reasons.append(f"{label} retention is below {review_ratio:.0%}")

    if reasons:
        return "review", reasons
    return "pass", reasons


def main() -> int:
    args = parse_args()
    raw_texts = [path.read_text(encoding="utf-8") for path in args.raw]
    cleaned_text = strip_frontmatter(args.cleaned.read_text(encoding="utf-8"))
    combined_raw = "\n".join(raw_texts)

    raw_words = word_count(combined_raw)
    cleaned_words = word_count(cleaned_text)
    raw_turns = sum(turn_count(text) for text in raw_texts)
    cleaned_turns = turn_count(cleaned_text)
    retained_words = ratio(cleaned_words, raw_words)
    retained_turns = ratio(cleaned_turns, raw_turns)
    backward_timestamps = backward_timestamp_count(cleaned_text)
    status, reasons = classify(
        retained_words,
        retained_turns,
        backward_timestamps,
        len(raw_texts),
        args.review_ratio,
        args.critical_ratio,
    )

    result = {
        "status": status,
        "raw_sources": [str(path) for path in args.raw],
        "cleaned": str(args.cleaned),
        "raw_words": raw_words,
        "cleaned_words": cleaned_words,
        "word_retention": retained_words,
        "raw_turns": raw_turns,
        "cleaned_turns": cleaned_turns,
        "turn_retention": retained_turns,
        "backward_timestamps": backward_timestamps,
        "reasons": reasons,
    }

    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"status: {status}")
        print(f"word retention: {retained_words:.1%}" if retained_words is not None else "word retention: n/a")
        print(f"turn retention: {retained_turns:.1%}" if retained_turns is not None else "turn retention: n/a")
        print(f"backward timestamps: {backward_timestamps}")
        for reason in reasons:
            print(f"reason: {reason}")

    return {"pass": 0, "review": 1, "critical": 2}[status]


if __name__ == "__main__":
    raise SystemExit(main())
