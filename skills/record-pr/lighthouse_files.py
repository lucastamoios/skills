"""Write and check the files that record-pr --lighthouse leaves for Lighthouse.

The contract is tasks/lighthouse/pr-explanation-update-20261020/screenshots-contract.md.

    lighthouse_files.py environment --pr N --head SHA --base-url URL --compose-dir DIR --login-email EMAIL
        Reads the password from $LIGHTHOUSE_TEST_PASSWORD and writes environment.json.
    lighthouse_files.py reuse --pr N --head SHA
        Prints the old manifest entries that still apply, as a JSON list.
    lighthouse_files.py manifest --pr N --head SHA --entries entries.json
        Checks the entries and writes manifest.json.
    lighthouse_files.py progress --pr N --head SHA --base-url URL --worktree DIR --scenes scenes.json --reused reused.json
        Writes progress.json with every planned scene, keeps the shots that an earlier run for the same
        head already took, writes manifest.json from it, and prints the scenes that are still to take.
    lighthouse_files.py shot --pr N --head SHA --file NAME --result done|failed [--reason TEXT]
        Records one scene's result in progress.json and writes manifest.json again at once.
    lighthouse_files.py resume --pr N --head SHA
        Prints the planned scenes of progress.json when it is for this head, else [].

Every command uses $LIGHTHOUSE_SCREENSHOTS_DIR as the folder. The reuse command reads
$LIGHTHOUSE_UPDATE_DIFF_FILE and prints [] when it is not set. Both writes go to a
temporary file in the same folder first and then replace the target, so that Lighthouse
never reads a partial file.
"""

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

SHA = re.compile(r"[0-9a-f]{40}")
PNG_NAME = re.compile(r"[a-z0-9-]+\.png")
TEST_EMAIL = re.compile(r"user\d+@example\.com")
MAX_SCREENSHOTS = 40
PROGRESS_FORMAT = "lighthouse.pr-progress/1"
SCENE_KEYS = ("file", "title", "path", "files")
KEPT_STATES = ("done", "reused")
# A scene's optional steps bring the page to the changed state before the shot; the manifest never carries them.
OPTIONAL_SCENE_KEYS = ("related_files", "steps")
STEP_ACTIONS = {"click", "fill", "select", "check", "press", "wait"}
VALUE_ACTIONS = {"fill", "select", "press"}
MAX_STEPS = 10


def write_atomic(path, document):
    descriptor, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    with os.fdopen(descriptor, "w") as handle:
        json.dump(document, handle, indent=2)
        handle.write("\n")
    os.replace(tmp, path)


def environment_document(pr, head, base_url, compose_dir, login_email, password, worktrees_dir):
    problems = []
    if not SHA.fullmatch(head):
        problems.append("head is not a 40 character hex sha")
    if not re.fullmatch(r"https://[a-z0-9.-]+:\d+", base_url):
        problems.append("base_url must be https://<host>:<port> with no path")
    compose = Path(compose_dir).resolve()
    if not compose.is_relative_to(Path(worktrees_dir).resolve()):
        problems.append("compose_dir is not inside LIGHTHOUSE_WORKTREES_DIR")
    if not TEST_EMAIL.fullmatch(login_email):
        problems.append("login_email is not a seeded user<N>@example.com test user")
    if not password:
        problems.append("LIGHTHOUSE_TEST_PASSWORD is empty")
    if problems:
        raise ValueError("; ".join(problems))
    return {
        "format": "lighthouse.pr-environment/1",
        "pr_number": pr,
        "head_sha": head,
        "base_url": base_url,
        "instance": f"lighthouse-pr{pr}",
        "compose_dir": str(compose),
        "login_email": login_email,
        "login_password": password,
    }


def reusable_entries(manifest, diff, pr, head, folder):
    """Return the old entries whose files the head-to-head diff does not touch."""
    if not manifest or not diff:
        return []
    if manifest.get("format") != "lighthouse.pr-screenshots/1" or manifest.get("pr_number") != pr:
        return []
    if diff.get("old_head_sha") != manifest.get("head_sha") or diff.get("head_sha") != head:
        return []
    # A truncated diff can omit changed files, so nothing is safe to keep.
    if diff.get("status") != "ahead" or diff.get("truncated"):
        return []
    changed = set()
    for item in diff.get("files") or []:
        changed.update(name for name in (item.get("filename"), item.get("previous_filename")) if name)
    return [
        entry
        for entry in manifest.get("screenshots") or []
        if not changed.intersection((entry.get("files") or []) + (entry.get("related_files") or []))
        and isinstance(entry.get("file"), str)
        and PNG_NAME.fullmatch(entry["file"])
        and (folder / entry["file"]).is_file()
        and not (folder / entry["file"]).is_symlink()
    ]


def entry_problems(index, entry, folder):
    where = f"screenshots[{index}]"
    keys = {"file", "title", "path", "files", "head_sha"}
    if not isinstance(entry, dict) or not keys <= set(entry) <= keys | {"related_files"}:
        return [f"{where} must have exactly file, title, path, files, head_sha, and optionally related_files"]
    problems = []
    name = entry["file"]
    if not isinstance(name, str) or len(name) > 64 or not PNG_NAME.fullmatch(name):
        problems.append(f"{where}.file must match [a-z0-9-]+.png and be at most 64 characters")
    elif not (folder / name).is_file() or (folder / name).is_symlink():
        problems.append(f"{where}.file {name} is not a regular file in the folder")
    if not isinstance(entry["title"], str) or not 0 < len(entry["title"]) <= 120:
        problems.append(f"{where}.title must have 1 to 120 characters")
    path = entry["path"]
    if not isinstance(path, str) or not path.startswith("/") or len(path) > 500:
        problems.append(f"{where}.path must start with / and have at most 500 characters")
    for key in ("files", "related_files"):
        files = entry.get(key, [])
        if not isinstance(files, list) or len(files) > 50 or not all(isinstance(f, str) and f for f in files):
            problems.append(f"{where}.{key} must be a list of at most 50 repository paths")
    if not isinstance(entry["head_sha"], str) or not SHA.fullmatch(entry["head_sha"]):
        problems.append(f"{where}.head_sha is not a 40 character hex sha")
    return problems


def manifest_document(pr, head, entries, folder):
    problems = [] if SHA.fullmatch(head) else ["head is not a 40 character hex sha"]
    if not isinstance(entries, list):
        raise ValueError("entries must be a JSON list")
    if len(entries) > MAX_SCREENSHOTS:
        problems.append(f"at most {MAX_SCREENSHOTS} screenshots")
    for index, entry in enumerate(entries):
        problems.extend(entry_problems(index, entry, folder))
    names = [entry.get("file") for entry in entries if isinstance(entry, dict)]
    if len(names) != len(set(names)):
        problems.append("file names must be unique")
    if problems:
        raise ValueError("; ".join(problems))
    return {"format": "lighthouse.pr-screenshots/1", "pr_number": pr, "head_sha": head, "screenshots": entries}


def current_progress(folder, pr, head):
    """The folder's progress when an earlier run for the same pull request and head wrote it, else None."""
    progress = read_json(folder / "progress.json")
    if not isinstance(progress, dict) or progress.get("format") != PROGRESS_FORMAT:
        return None
    if progress.get("pr_number") != pr or progress.get("head_sha") != head:
        return None
    return progress if isinstance(progress.get("scenes"), list) else None


def step_problems(where, steps):
    if not isinstance(steps, list) or len(steps) > MAX_STEPS:
        return [f"{where}.steps must be a list of at most {MAX_STEPS} steps"]
    problems = []
    for index, step in enumerate(steps):
        at = f"{where}.steps[{index}]"
        if not isinstance(step, dict) or step.get("action") not in STEP_ACTIONS:
            problems.append(f"{at}.action must be one of {', '.join(sorted(STEP_ACTIONS))}")
            continue
        if not isinstance(step.get("selector"), str) or not step["selector"]:
            problems.append(f"{at}.selector must be a Playwright selector")
        if step["action"] in VALUE_ACTIONS and not isinstance(step.get("value"), str):
            problems.append(f"{at}.value must be text for {step['action']}")
    return problems


def progress_document(pr, head, base_url, worktree, scenes, reused, earlier, folder):
    """Plan every scene; a reused entry or a shot that an earlier run for this head took is kept."""
    if not SHA.fullmatch(head):
        raise ValueError("head is not a 40 character hex sha")
    if not isinstance(scenes, list) or not all(isinstance(scene, dict) for scene in scenes):
        raise ValueError("scenes must be a JSON list of objects")
    if len(scenes) > MAX_SCREENSHOTS:
        raise ValueError(f"at most {MAX_SCREENSHOTS} scenes")
    problems = [
        p for i, scene in enumerate(scenes) if "steps" in scene for p in step_problems(f"scenes[{i}]", scene["steps"])
    ]
    if problems:
        raise ValueError("; ".join(problems))
    reused_by_file = {item.get("file"): item for item in reused or [] if isinstance(item, dict)}
    taken = {item.get("file") for item in (earlier or {}).get("scenes", []) if item.get("state") == "done"}
    planned = []
    for scene in scenes:
        item = {key: scene.get(key) for key in SCENE_KEYS}
        item.update({key: scene[key] for key in OPTIONAL_SCENE_KEYS if key in scene})
        image = folder / str(item["file"])
        if item["file"] in reused_by_file:
            item.update(state="reused", head_sha=reused_by_file[item["file"]].get("head_sha"))
        elif item["file"] in taken and image.is_file() and not image.is_symlink():
            item.update(state="done", head_sha=head)
        else:
            item["state"] = "planned"
        planned.append(item)
    return {
        "format": PROGRESS_FORMAT,
        "pr_number": pr,
        "head_sha": head,
        "instance": f"lighthouse-pr{pr}",
        "base_url": base_url,
        "worktree": worktree,
        "scenes": planned,
    }


def write_progress(folder, progress):
    """Write the manifest from the kept scenes first, so a listed image always exists, then the progress."""
    entries = [
        {key: scene[key] for key in (*SCENE_KEYS, "related_files", "head_sha") if key in scene}
        for scene in progress["scenes"]
        if scene["state"] in KEPT_STATES
    ]
    write_atomic(
        folder / "manifest.json", manifest_document(progress["pr_number"], progress["head_sha"], entries, folder)
    )
    write_atomic(folder / "progress.json", progress)
    return entries


def record_shot(folder, pr, head, name, result, reason):
    progress = current_progress(folder, pr, head)
    if progress is None:
        raise ValueError("progress.json is missing or names another pull request or head")
    scene = next((item for item in progress["scenes"] if item.get("file") == name), None)
    if scene is None:
        raise ValueError(f"{name} is not a planned scene")
    if result == "done":
        scene.update(state="done", head_sha=head)
        scene.pop("reason", None)
    else:
        scene.update(state="failed", reason=(reason or "The screenshot failed.")[:300])
        scene.pop("head_sha", None)
    return write_progress(folder, progress)


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return None


def main(argv=None):
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("environment", "reuse", "manifest", "progress", "shot", "resume"):
        command = commands.add_parser(name)
        command.add_argument("--pr", type=int, required=True)
        command.add_argument("--head", required=True)
    commands.choices["environment"].add_argument("--base-url", required=True)
    commands.choices["environment"].add_argument("--compose-dir", required=True)
    commands.choices["environment"].add_argument("--login-email", required=True)
    commands.choices["manifest"].add_argument("--entries", required=True)
    for option in ("--base-url", "--worktree", "--scenes", "--reused"):
        commands.choices["progress"].add_argument(option, required=True)
    commands.choices["shot"].add_argument("--file", required=True)
    commands.choices["shot"].add_argument("--result", choices=("done", "failed"), required=True)
    commands.choices["shot"].add_argument("--reason")
    args = parser.parse_args(argv)

    folder = Path(os.environ["LIGHTHOUSE_SCREENSHOTS_DIR"])
    try:
        if args.command == "environment":
            document = environment_document(
                args.pr,
                args.head,
                args.base_url,
                args.compose_dir,
                args.login_email,
                os.environ.get("LIGHTHOUSE_TEST_PASSWORD", ""),
                os.environ["LIGHTHOUSE_WORKTREES_DIR"],
            )
            write_atomic(folder / "environment.json", document)
            print("wrote environment.json")
        elif args.command == "reuse":
            diff_file = os.environ.get("LIGHTHOUSE_UPDATE_DIFF_FILE")
            diff = read_json(diff_file) if diff_file else None
            kept = reusable_entries(read_json(folder / "manifest.json"), diff, args.pr, args.head, folder)
            print(json.dumps(kept, indent=2))
        elif args.command == "progress":
            earlier = current_progress(folder, args.pr, args.head)
            progress = progress_document(
                args.pr,
                args.head,
                args.base_url,
                args.worktree,
                read_json(args.scenes),
                read_json(args.reused),
                earlier,
                folder,
            )
            write_progress(folder, progress)
            keys = (*SCENE_KEYS, *OPTIONAL_SCENE_KEYS)
            todo = [{key: s[key] for key in keys if key in s} for s in progress["scenes"] if s["state"] == "planned"]
            print(json.dumps(todo, indent=2))
        elif args.command == "shot":
            entries = record_shot(folder, args.pr, args.head, args.file, args.result, args.reason)
            print(f"recorded {args.file} as {args.result}; manifest.json has {len(entries)} screenshots")
        elif args.command == "resume":
            progress = current_progress(folder, args.pr, args.head)
            scenes = [
                {key: s[key] for key in (*SCENE_KEYS, *OPTIONAL_SCENE_KEYS) if key in s}
                for s in (progress or {}).get("scenes", [])
            ]
            print(json.dumps(scenes, indent=2))
        else:
            document = manifest_document(args.pr, args.head, read_json(args.entries), folder)
            write_atomic(folder / "manifest.json", document)
            print(f"wrote manifest.json with {len(document['screenshots'])} screenshots")
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
