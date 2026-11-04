import json

import pytest

from lighthouse_files import main, reusable_entries

OLD, NEW = "a" * 40, "b" * 40


def entry(name, files, head=OLD):
    return {"file": name, "title": name, "path": "/x/", "files": files, "head_sha": head}


def test_environment_is_written_and_rejects_real_accounts(tmp_path, monkeypatch):
    worktree = tmp_path / "worktrees" / "pr-7" / "clients" / "web"
    worktree.mkdir(parents=True)
    monkeypatch.setenv("LIGHTHOUSE_SCREENSHOTS_DIR", str(tmp_path))
    monkeypatch.setenv("LIGHTHOUSE_WORKTREES_DIR", str(tmp_path / "worktrees"))
    monkeypatch.setenv("LIGHTHOUSE_TEST_PASSWORD", "secret")
    common = ["--pr", "7", "--head", NEW, "--base-url", "https://test.cr.test:1443", "--compose-dir", str(worktree)]

    assert main(["environment", *common, "--login-email", "employee@example.test"]) == 1
    assert not (tmp_path / "environment.json").exists()

    assert main(["environment", *common, "--login-email", "user1000@example.com"]) == 0
    written = json.loads((tmp_path / "environment.json").read_text())
    assert written["instance"] == "lighthouse-pr7"
    assert written["login_password"] == "secret"

    outside = ["--compose-dir", str(tmp_path), "--login-email", "user1000@example.com"]
    assert main(["environment", *common[:-2], *outside]) == 1


def test_reuse_keeps_only_untouched_screens(tmp_path):
    for name in ("kept.png", "changed.png", "renamed.png"):
        (tmp_path / name).write_bytes(b"png")
    manifest = {
        "format": "lighthouse.pr-screenshots/1",
        "pr_number": 7,
        "head_sha": OLD,
        "screenshots": [
            entry("kept.png", ["a.html"]),
            entry("changed.png", ["b.html"]),
            entry("renamed.png", ["old.html"]),
            entry("missing.png", ["a.html"]),
        ],
    }
    diff = {
        "old_head_sha": OLD,
        "head_sha": NEW,
        "status": "ahead",
        "truncated": False,
        "files": [{"filename": "b.html"}, {"filename": "new.html", "previous_filename": "old.html"}],
    }
    kept = reusable_entries(manifest, diff, 7, NEW, tmp_path)
    assert [e["file"] for e in kept] == ["kept.png"]

    assert reusable_entries(manifest, {**diff, "truncated": True}, 7, NEW, tmp_path) == []
    assert reusable_entries(manifest, {**diff, "status": "diverged"}, 7, NEW, tmp_path) == []
    assert reusable_entries(manifest, {**diff, "old_head_sha": "c" * 40}, 7, NEW, tmp_path) == []
    assert reusable_entries(manifest, None, 7, NEW, tmp_path) == []


@pytest.mark.parametrize(
    "bad",
    [
        entry("../x.png", []),
        entry("Upper.png", []),
        entry("absent.png", []),
        {**entry("shot.png", []), "path": "no-slash"},
        {**entry("shot.png", []), "title": "x" * 121},
        {**entry("shot.png", []), "head_sha": "short"},
        {**entry("shot.png", []), "extra": 1},
    ],
)
def test_manifest_rejects_bad_entries(tmp_path, monkeypatch, bad):
    (tmp_path / "shot.png").write_bytes(b"png")
    (tmp_path / "entries.json").write_text(json.dumps([bad]))
    monkeypatch.setenv("LIGHTHOUSE_SCREENSHOTS_DIR", str(tmp_path))
    assert main(["manifest", "--pr", "7", "--head", NEW, "--entries", str(tmp_path / "entries.json")]) == 1
    assert not (tmp_path / "manifest.json").exists()


def test_manifest_is_written(tmp_path, monkeypatch):
    (tmp_path / "shot.png").write_bytes(b"png")
    (tmp_path / "entries.json").write_text(json.dumps([entry("shot.png", ["a.html"], NEW)]))
    monkeypatch.setenv("LIGHTHOUSE_SCREENSHOTS_DIR", str(tmp_path))
    assert main(["manifest", "--pr", "7", "--head", NEW, "--entries", str(tmp_path / "entries.json")]) == 0
    written = json.loads((tmp_path / "manifest.json").read_text())
    assert written["format"] == "lighthouse.pr-screenshots/1"
    assert [e["file"] for e in written["screenshots"]] == ["shot.png"]
    assert not list(tmp_path.glob(".manifest.json.*"))


def scene(name):
    return {"file": name, "title": name.removesuffix(".png"), "path": f"/{name}/", "files": ["a.html"]}


def start_progress(tmp_path, monkeypatch, capsys, scenes, reused=(), head=NEW):
    monkeypatch.setenv("LIGHTHOUSE_SCREENSHOTS_DIR", str(tmp_path))
    (tmp_path / "scenes.json").write_text(json.dumps(scenes))
    (tmp_path / "reused.json").write_text(json.dumps(list(reused)))
    args = ["progress", "--pr", "7", "--head", head, "--base-url", "https://test.cr.test:1443"]
    args += [
        "--worktree",
        "/wt/pr-7",
        "--scenes",
        str(tmp_path / "scenes.json"),
        "--reused",
        str(tmp_path / "reused.json"),
    ]
    capsys.readouterr()
    assert main(args) == 0
    return json.loads(capsys.readouterr().out)


def shot(tmp_path, name, result="done", reason=None, head=NEW):
    if result == "done":
        (tmp_path / name).write_bytes(b"png")
    extra = ["--reason", reason] if reason else []
    return main(["shot", "--pr", "7", "--head", head, "--file", name, "--result", result, *extra])


def manifest_files(tmp_path):
    return [e["file"] for e in json.loads((tmp_path / "manifest.json").read_text())["screenshots"]]


def test_progress_lists_the_plan_keeps_reused_shots_and_names_the_scenes_to_take(tmp_path, monkeypatch, capsys):
    (tmp_path / "kept.png").write_bytes(b"png")
    todo = start_progress(
        tmp_path,
        monkeypatch,
        capsys,
        [scene("kept.png"), scene("one.png"), scene("two.png")],
        [entry("kept.png", ["a.html"])],
    )
    assert [s["file"] for s in todo] == ["one.png", "two.png"]
    progress = json.loads((tmp_path / "progress.json").read_text())
    assert progress["format"] == "lighthouse.pr-progress/1"
    assert (progress["head_sha"], progress["instance"], progress["base_url"]) == (
        NEW,
        "lighthouse-pr7",
        "https://test.cr.test:1443",
    )
    assert [s["state"] for s in progress["scenes"]] == ["reused", "planned", "planned"]
    assert manifest_files(tmp_path) == ["kept.png"]


def test_each_shot_updates_the_progress_and_the_manifest_at_once(tmp_path, monkeypatch, capsys):
    start_progress(tmp_path, monkeypatch, capsys, [scene("one.png"), scene("two.png"), scene("three.png")])
    assert shot(tmp_path, "one.png") == 0
    assert manifest_files(tmp_path) == ["one.png"]
    assert shot(tmp_path, "two.png", "failed", "The page answered 404.") == 0
    scenes = json.loads((tmp_path / "progress.json").read_text())["scenes"]
    assert [(s["state"], s.get("reason")) for s in scenes] == [
        ("done", None),
        ("failed", "The page answered 404."),
        ("planned", None),
    ]
    assert json.loads((tmp_path / "manifest.json").read_text())["screenshots"][0]["head_sha"] == NEW
    assert shot(tmp_path, "absent.png") == 1
    assert shot(tmp_path, "three.png", head=OLD) == 1


def test_a_rerun_for_the_same_head_takes_only_what_is_left_and_another_head_starts_over(tmp_path, monkeypatch, capsys):
    scenes = [scene("one.png"), scene("two.png")]
    start_progress(tmp_path, monkeypatch, capsys, scenes)
    shot(tmp_path, "one.png")
    capsys.readouterr()
    assert main(["resume", "--pr", "7", "--head", NEW]) == 0
    assert [s["file"] for s in json.loads(capsys.readouterr().out)] == ["one.png", "two.png"]
    assert main(["resume", "--pr", "7", "--head", OLD]) == 0
    assert json.loads(capsys.readouterr().out) == []

    assert [s["file"] for s in start_progress(tmp_path, monkeypatch, capsys, scenes)] == ["two.png"]
    assert manifest_files(tmp_path) == ["one.png"]
    assert [s["file"] for s in start_progress(tmp_path, monkeypatch, capsys, scenes, head=OLD)] == [
        "one.png",
        "two.png",
    ]
    assert manifest_files(tmp_path) == []


def test_related_files_are_optional_checked_and_carried_into_the_manifest(tmp_path, monkeypatch, capsys):
    with_backend = {**scene("one.png"), "related_files": ["clients/web/products/views.py"]}
    start_progress(tmp_path, monkeypatch, capsys, [with_backend, scene("two.png")])
    shot(tmp_path, "one.png")
    shot(tmp_path, "two.png")
    entries = json.loads((tmp_path / "manifest.json").read_text())["screenshots"]
    assert entries[0]["related_files"] == ["clients/web/products/views.py"]
    assert "related_files" not in entries[1]
    (tmp_path / "entries.json").write_text(json.dumps([{**entry("one.png", []), "related_files": "views.py"}]))
    assert main(["manifest", "--pr", "7", "--head", NEW, "--entries", str(tmp_path / "entries.json")]) == 1


def test_reuse_drops_a_screen_whose_backend_file_changed(tmp_path):
    (tmp_path / "kept.png").write_bytes(b"png")
    manifest = {
        "format": "lighthouse.pr-screenshots/1",
        "pr_number": 7,
        "head_sha": OLD,
        "screenshots": [{**entry("kept.png", ["a.html"]), "related_files": ["views.py"]}],
    }
    diff = {
        "old_head_sha": OLD,
        "head_sha": NEW,
        "status": "ahead",
        "truncated": False,
        "files": [{"filename": "views.py"}],
    }
    assert reusable_entries(manifest, diff, 7, NEW, tmp_path) == []


def test_steps_reach_the_shot_through_the_progress_but_never_the_manifest(tmp_path, monkeypatch, capsys):
    steps = [
        {"action": "click", "selector": "text=Add Minimum WPS Requirement"},
        {"action": "wait", "selector": "#modal-content"},
    ]
    todo = start_progress(tmp_path, monkeypatch, capsys, [{**scene("modal.png"), "steps": steps}])
    assert todo[0]["steps"] == steps
    shot(tmp_path, "modal.png")
    assert "steps" not in json.loads((tmp_path / "manifest.json").read_text())["screenshots"][0]
    capsys.readouterr()
    main(["resume", "--pr", "7", "--head", NEW])
    assert json.loads(capsys.readouterr().out)[0]["steps"] == steps


@pytest.mark.parametrize(
    "steps",
    [
        "click",
        [{"action": "hover", "selector": "#x"}],
        [{"action": "click"}],
        [{"action": "fill", "selector": "#x"}],
        [{"action": "click", "selector": "#x"}] * 11,
    ],
)
def test_bad_steps_are_rejected(tmp_path, monkeypatch, capsys, steps):
    monkeypatch.setenv("LIGHTHOUSE_SCREENSHOTS_DIR", str(tmp_path))
    (tmp_path / "scenes.json").write_text(json.dumps([{**scene("one.png"), "steps": steps}]))
    (tmp_path / "reused.json").write_text("[]")
    args = ["progress", "--pr", "7", "--head", NEW, "--base-url", "https://test.cr.test:1443", "--worktree", "/wt"]
    assert main([*args, "--scenes", str(tmp_path / "scenes.json"), "--reused", str(tmp_path / "reused.json")]) == 1
