#!/usr/bin/env python3
"""Validate a marketing/v1 JSON file: validate.py <schema-name> <file.json>, e.g. script.output."""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMAS = Path(__file__).resolve().parent.parent / "protocol" / "schemas"


def main() -> int:
    name, path = sys.argv[1], Path(sys.argv[2])
    registry = Registry().with_resources(
        (p.name, Resource.from_contents(json.loads(p.read_text()))) for p in SCHEMAS.glob("*.json")
    )
    schema = json.loads((SCHEMAS / f"{name}.schema.json").read_text())
    errors = sorted(Draft202012Validator(schema, registry=registry).iter_errors(json.loads(path.read_text())), key=str)
    for error in errors:
        print(f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}")
    print("valid" if not errors else f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
