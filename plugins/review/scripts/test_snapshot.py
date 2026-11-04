import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from snapshot import capture, check


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        (self.repo / "app.py").write_text("value = 1\n")
        (self.repo / ".gitignore").write_text("cache/\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "fixture")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], stderr=subprocess.PIPE)

    def snapshot(self):
        return capture(self.repo, "HEAD")

    def test_same_head_does_not_hide_local_edits(self):
        original = self.snapshot()
        (self.repo / "app.py").write_text("value = 2\n")
        changed = self.snapshot()
        self.assertEqual(original["head"], changed["head"])
        self.assertNotEqual(original["snapshot_id"], changed["snapshot_id"])

    def test_untracked_deleted_mode_and_link_changes_are_identified(self):
        previous = self.snapshot()["snapshot_id"]
        mutations = [
            lambda: (self.repo / "new.py").write_text("new\n"),
            lambda: (self.repo / "app.py").chmod(0o755),
            lambda: (self.repo / "alias").symlink_to("app.py"),
            lambda: (self.repo / "app.py").unlink(),
            lambda: (self.repo / "new.py").unlink(),
        ]
        for mutate in mutations:
            mutate()
            current = self.snapshot()["snapshot_id"]
            self.assertNotEqual(previous, current)
            previous = current

    def test_ignored_runtime_files_do_not_invalidate_source(self):
        original = self.snapshot()["snapshot_id"]
        (self.repo / "cache").mkdir()
        (self.repo / "cache" / "log").write_text("runtime output")
        self.assertEqual(original, self.snapshot()["snapshot_id"])

    def test_copy_has_same_content_identity(self):
        other = self.root / "other"
        shutil.copytree(self.repo, other, symlinks=True)
        self.assertEqual(self.snapshot()["snapshot_id"], capture(other, "HEAD")["snapshot_id"])

    def test_check_rejects_stale_or_tampered_manifest(self):
        data = self.snapshot()
        manifest = self.root / "snapshot.json"
        manifest.write_text(json.dumps(data))
        self.assertEqual(check(manifest), data["snapshot_id"])
        (self.repo / "app.py").write_text("changed")
        with self.assertRaisesRegex(ValueError, "stale"):
            check(manifest)
        data["files"] = {}
        manifest.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "modified"):
            check(manifest)

    def test_submodules_are_not_silently_omitted(self):
        head = self.git("rev-parse", "HEAD").decode().strip()
        self.git("update-index", "--add", "--cacheinfo", f"160000,{head},vendor")
        with self.assertRaisesRegex(ValueError, "Submodules"):
            self.snapshot()


if __name__ == "__main__":
    unittest.main()
