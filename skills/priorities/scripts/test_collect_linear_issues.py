#!/usr/bin/env python3

from __future__ import annotations

import io
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

import collect_linear_issues


class SharedCredentialTests(unittest.TestCase):
    # Regression test: collecting priorities must not request another CLI approval.
    # Direct cause: the collector reread the Linear credential with op read.
    # Root cause: it bypassed the shared environment used by agent processes.
    def test_collects_with_injected_key_without_calling_one_password(self) -> None:
        completed = subprocess.CompletedProcess([], 0, "obsolete-key\n", "")
        with (
            patch.dict(os.environ, {"LINEAR_API_KEY": "injected-key"}, clear=True),
            patch.object(sys, "argv", ["collect_linear_issues.py"]),
            patch("subprocess.run", return_value=completed) as run,
            patch.object(collect_linear_issues, "collect", return_value=[]) as collect,
            patch.object(sys, "stdout", io.StringIO()) as output,
        ):
            collect_linear_issues.main()

        collect.assert_called_once_with("injected-key")
        run.assert_not_called()
        self.assertEqual(output.getvalue(), '{\n  "issues": []\n}\n')

    def test_missing_or_unresolved_key_fails_without_cli_or_network_calls(self) -> None:
        for key in (None, "", "  ", "op://example-vault/example-item/token"):
            with self.subTest(key=key):
                environment = {} if key is None else {"LINEAR_API_KEY": key}
                completed = subprocess.CompletedProcess([], 1, "", "not signed in")
                with (
                    patch.dict(os.environ, environment, clear=True),
                    patch.object(sys, "argv", ["collect_linear_issues.py"]),
                    patch("subprocess.run", return_value=completed) as run,
                    patch.object(collect_linear_issues, "collect") as collect,
                    self.assertRaisesRegex(SystemExit, "LINEAR_API_KEY"),
                ):
                    collect_linear_issues.main()

                run.assert_not_called()
                collect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
