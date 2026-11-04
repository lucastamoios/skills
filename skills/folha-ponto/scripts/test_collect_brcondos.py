#!/usr/bin/env python3
"""Tests for the BRCondos collection command."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from collect_brcondos import run


class FakeClient:
    def __init__(self) -> None:
        self.call: dict[str, str | int | bool] = {}

    def collect(self, **kwargs: str | int | bool) -> list[dict[str, str]]:
        self.call = kwargs
        return [
            {
                "name": "FUNCIONARIA TESTE",
                "control_id": "1000001000000000/1",
                "timestamp": "01/08/2026 07:20:00",
            }
        ]


class CollectBrcondosCommandTests(unittest.TestCase):
    """The command writes normalized records without authentication data."""

    def test_collects_requested_month_into_normalized_json(self) -> None:
        fake_client = FakeClient()
        credentials = {
            "BRCONDOS_LOGIN": "person@example.test",
            "BRCONDOS_PASSWORD": "secret-value",
        }

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "records.json"
            exit_code = run(
                [
                    "--month",
                    "2026-08",
                    "--person",
                    "FUNCIONARIA TESTE",
                    "--output",
                    str(output),
                ],
                env=credentials,
                client=fake_client,
            )

            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            fake_client.call,
            {
                "login": "person@example.test",
                "password": "secret-value",
                "date_start": "01/08/2026 00:00:00",
                "date_end": "31/08/2026 23:59:59",
                "person": "FUNCIONARIA TESTE",
                "headed": False,
                "max_pages": 50,
            },
        )
        self.assertEqual(
            payload,
            {
                "source": "BRCondos /Persons/AccessHistory",
                "records": [
                    {
                        "name": "FUNCIONARIA TESTE",
                        "control_id": "1000001000000000/1",
                        "timestamp": "01/08/2026 07:20:00",
                    }
                ],
            },
        )
        self.assertNotIn("secret-value", json.dumps(payload))


if __name__ == "__main__":
    unittest.main()
