#!/usr/bin/env python3
"""Run task management against the configured private task directory."""
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"skills/skill-config/scripts"))
import skill_profile
path = skill_profile.get("paths.tasks")
if not path:
    raise SystemExit("Configure paths.tasks before managing private tasks.")
os.environ["BRAIN_TASKS_DIR"] = str(skill_profile.resolve_path(path))
import tasks_impl
if not tasks_impl.TEMPLATE.is_file():
    tasks_impl.TEMPLATE = Path(__file__).with_name("task-template.md")
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        tasks_impl.TASKS.mkdir(parents=True, exist_ok=True)
    arguments = tasks_impl.parser().parse_args()
    arguments.run(arguments)
