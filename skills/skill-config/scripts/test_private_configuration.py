"""Verify configuration isolation and the consumers that used personal constants."""

from __future__ import annotations

import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import skill_profile


SKILLS = Path(__file__).resolve().parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


github = module("configured_github", SKILLS / "priorities/scripts/collect_github_prs.py")
inventory = module("configured_inventory", SKILLS / "priorities/scripts/build_review_inventory.py")
timesheet = module("configured_timesheet", SKILLS / "folha-ponto/scripts/build_timesheet.py")


class PrivateConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="private skills ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.profile = self.root / "profile.json"
        self.profile.write_text(json.dumps({
            "version": 1,
            "work": {"github_repository": "example/project", "github_login": "example-user",
                     "issue_prefix": "OPS", "requester_aliases": {"casey example": "Lead"}},
            "timesheet": {"profile": "timesheet.json"},
        }))
        self.env = patch.dict(os.environ, {"SKILLS_CONFIG": str(self.profile)})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_relative_resources_resolve_beside_profile_target_not_link(self):
        link_dir = self.root / "installation"
        link_dir.mkdir()
        link = link_dir / "config.json"
        link.symlink_to(self.profile)
        self.assertEqual(skill_profile.resolve_path("glossary.md", link), (self.root / "glossary.md").resolve())

    def test_missing_profile_has_no_personal_fallback_and_cli_queries_fail(self):
        with patch.dict(os.environ, {"SKILLS_CONFIG": str(self.root / "absent.json")}):
            self.assertIsNone(skill_profile.get("work.github_repository"))
            with self.assertRaisesRegex(ValueError, "missing"):
                skill_profile.load()

    def test_cli_initialization_is_private_and_does_not_overwrite_answers(self):
        target = self.root / "new installation/config.json"
        command = [sys.executable, str(Path(__file__).with_name("config.py")),
                   "init", "--output", str(target)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(target.stat().st_mode & 0o777, 0o600)
        self.assertEqual(json.loads(target.read_text())["user"]["display_name"], "")
        target.write_text('{"version":1,"user":{"display_name":"Existing answer"}}')
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.assertEqual(json.loads(target.read_text())["user"]["display_name"], "Existing answer")

    def test_invalid_profile_version_and_sections_fail_before_consumption(self):
        for value in ({"version": 2}, {"version": 1, "work": []}):
            self.profile.write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                skill_profile.load()

    def test_github_collector_uses_profile_and_explicit_override(self):
        for extra, expected in (([], "example/project"), (["--repo", "another/project"], "another/project")):
            with patch.object(sys, "argv", ["collector", *extra]), \
                    patch.object(github, "run_gh", return_value=[]) as read, \
                    patch.object(sys, "stdout", io.StringIO()) as output:
                github.main()
                read.assert_called_once_with(expected, 250)
                self.assertEqual(json.loads(output.getvalue())["user_login"], "example-user")

    def test_issue_and_requester_matching_uses_installer_answers(self):
        self.assertEqual(inventory.issue_identifier({"title": "Fix OPS-12"}), "OPS-12")
        self.assertIsNone(inventory.issue_identifier({"title": "Fix OTHER-12"}))
        self.assertEqual(inventory.requester_for([{"creator": {"name": "Casey Example"}}]), "Lead")
        self.assertIsNone(inventory.requester_for([{"creator": {"name": "Someone Else"}}]))

    def test_timesheet_direction_comes_from_private_equipment_mapping(self):
        profile = {"schedule": {"start": "08:00", "standard_end": "17:00",
                               "presence_minutes": 540, "tolerance_minutes": 60},
                   "controls": {"entry_prefix": "2001", "exit_prefix": "2002"}}
        path = self.root / "timesheet.json"
        path.write_text(json.dumps(profile))
        loaded = timesheet.load_profile(None)
        records = self.root / "records.json"
        records.write_text(json.dumps([{"name": "Example Person", "control_id": "200100/1",
                                        "timestamp": "03/11/2026 08:00:00"},
                                       {"name": "Example Person", "control_id": "200200/1",
                                        "timestamp": "03/11/2026 17:30:00"}]))
        events = timesheet.load_events(records, loaded["controls"])
        self.assertEqual([event.direction for event in events], ["entry", "exit"])
        results, _, _ = timesheet.calculate(events, loaded, 2026, 11)
        self.assertEqual(sum(row.overtime_minutes for row in results if not row.special), 30)
        profile["controls"]["exit_prefix"] = "200"
        path.write_text(json.dumps(profile))
        with self.assertRaisesRegex(ValueError, "overlap"):
            timesheet.load_profile(None)


if __name__ == "__main__":
    unittest.main()
