#!/usr/bin/env python3
"""Install shared skills and configure a private profile without network access."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ROOT = Path(__file__).resolve().parent


def inside(path, directory):
    return path == directory or directory in path.parents


def save_private(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.profile-', dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def assign(profile, key, value):
    parts = key.split('.')
    node = profile
    for part in parts[:-1]:
        if not isinstance(node.get(part), dict):
            node[part] = {}
        node = node[part]
    node[parts[-1]] = value


def lookup(profile, key):
    node = profile
    for part in key.split('.'):
        if not isinstance(node, dict):
            return None
        node = node.get(part)
    return node


def prompt(question, existing='', *, required=False, kind='string'):
    while True:
        default = json.dumps(existing, ensure_ascii=False) if isinstance(existing, (dict, list)) else existing
        suffix = f' [{default}]' if default else ' [Enter to skip]' if not required else ''
        answer = input(question + suffix + ': ').strip()
        value = existing if not answer else answer
        if required and not value:
            print('Please provide a value.')
            continue
        if kind in ('list', 'object'):
            try:
                value = json.loads(answer) if answer else existing or ([] if kind == 'list' else {})
                if not isinstance(value, list if kind == 'list' else dict):
                    raise ValueError()
            except ValueError:
                print('Use a JSON array.' if kind == 'list' else 'Use a JSON object.')
                continue
        return value


def valid_answers(answers, profile, question_groups):
    allowed = {q['key']: q for group in question_groups for q in group['questions']}
    for key, value in answers.items():
        if key not in allowed:
            raise ValueError(f'Unknown setup answer: {key}')
        question = allowed[key]
        expected = {'list': list, 'object': dict}.get(question.get('type'), str)
        if not isinstance(value, expected):
            raise ValueError(f'Invalid answer type for {key}')
        # Setup accepts paths and references, never arbitrary credential fields.
        if key == 'integrations':
            raise ValueError('Configure integration references separately; do not supply secret values to setup.')
        assign(profile, key, value)


def configure(args, package, original):
    template = json.loads((ROOT / 'skills/skill-config/references/profile.example.json').read_text())
    profile = copy.deepcopy(original if original is not None else template)
    questions = json.loads((ROOT / 'setup-questions.json').read_text())['groups']
    if args.answers:
        answers = json.loads(args.answers.read_text())
        if not isinstance(answers, dict):
            raise ValueError('Answers must be an object of dotted profile fields.')
        valid_answers(answers, profile, questions)
        selected = [v.strip() for v in args.modules.split(',') if v.strip()] if args.modules else profile.get('installation', {}).get('modules', [])
    else:
        print('Private configuration. Optional modules can be skipped. Never enter passwords or tokens.')
        modules = prompt('Optional modules (comma separated: work, transcripts, marketing, timesheets, integrations)',
                         args.modules or ','.join(profile.get('installation', {}).get('modules', [])))
        selected = [v.strip() for v in modules.split(',') if v.strip()]
        for group in questions:
            if group['module'] != 'basic' and group['module'] not in selected:
                continue
            for question in group['questions']:
                value = prompt(question['question'], lookup(profile, question['key']) or '',
                               required=question.get('required', False), kind=question.get('type', 'string'))
                assign(profile, question['key'], value)
    known = {group['module'] for group in questions} - {'basic'}
    if any(name not in known for name in selected):
        raise ValueError('Unknown optional module. Choose work, transcripts, marketing, timesheets or integrations.')
    for key in ('user.display_name', 'user.language', 'user.timezone', 'paths.brain'):
        if not isinstance(lookup(profile, key), str) or not lookup(profile, key).strip():
            raise ValueError(f'Missing required answer: {key}')
    try:
        ZoneInfo(profile['user']['timezone'])
    except (ValueError, ZoneInfoNotFoundError):
        raise ValueError('Use an IANA timezone such as Etc/UTC.') from None
    context = Path(profile['paths']['brain']).expanduser()
    if not context.is_absolute():
        raise ValueError('Use an absolute private context directory.')
    if inside(context.resolve(), ROOT) or inside(context.resolve(), package):
        raise ValueError('The private context must be outside the public package.')
    profile['paths']['brain'] = str(context)
    defaults = {'vault': context/'vault', 'tasks': context/'vault/tasks', 'artifacts': context/'tasks',
                'docs': context/'docs', 'logs': context/'logs', 'worktrees': context/'worktrees', 'code': context/'code'}
    for key, value in defaults.items():
        configured = profile['paths'].get(key)
        resolved = Path(configured).expanduser() if configured else value
        if not resolved.is_absolute():
            resolved = args.config.expanduser().resolve().parent / resolved
        profile['paths'][key] = str(resolved.resolve())
    # These paths belong to this installed release, not the author's workspace.
    profile['paths'].update(skills=str(package/'skills'), plugins=str(package/'plugins'), scripts=str(package/'support'))
    profile['installation'] = {'package_id': json.loads((ROOT/'package.json').read_text())['id'],
                               'modules': selected,
                               'commands': json.loads((ROOT/'command-map.json').read_text())}
    return profile


def verify_package(directory=ROOT):
    manifest = json.loads((directory/'manifest.json').read_text())
    actual = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and not any(part in {'__pycache__', '.pytest_cache', '.git'} for part in p.relative_to(directory).parts)}
    if actual != set(manifest) | {'manifest.json'}:
        raise ValueError('Package contains unexpected or missing files. Keep private answers outside it.')
    for name, expected in manifest.items():
        path = directory/name
        if path.is_symlink() or not path.is_file() or not inside(path.resolve(), directory):
            raise ValueError('Invalid package member: ' + name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Package checksum mismatch: ' + name)
    return hashlib.sha256((directory/'manifest.json').read_bytes()).hexdigest()[:16]


def install(args):
    release = verify_package()
    state = args.state_dir.expanduser().resolve()
    package = state/'packages'/release
    config = args.config.expanduser().absolute()
    if inside(state, ROOT) or inside(config.resolve(), ROOT) or inside(config.resolve(), package):
        raise ValueError('Installation state and private configuration must be outside the public package.')
    if config.resolve() == (state/'install-state.json').resolve():
        raise ValueError('Private profile must not replace the installation state file.')
    if package.exists():
        try:
            verify_package(package)
        except (OSError, ValueError) as error:
            raise ValueError('Installed release is damaged or changed. Preserve it and choose a new state directory or restore its files.') from error
    original = None
    if config.exists():
        original = json.loads(config.read_text())
        if not isinstance(original, dict) or original.get('version') != 1:
            raise ValueError('Existing profile must have version 1.')
    if original is not None:
        for key in ('user', 'paths', 'work', 'contexts', 'integrations', 'timesheet', 'marketing', 'execution'):
            if key in original and not isinstance(original[key], dict):
                raise ValueError('Invalid existing profile section: ' + key)
    profile = configure(args, package, original)
    destinations = []
    if args.client in ('codex', 'both'):
        destinations.append(args.codex_dir.expanduser().absolute())
    if args.client in ('claude', 'both'):
        destinations.append(args.claude_dir.expanduser().absolute())
    # Check lexical locations before nonexistent directories become skill symlinks.
    protected = [ROOT, state/'packages', *[p.resolve() for p in destinations]]
    private_paths = [config, config.resolve(), Path(profile['paths']['brain']),
                     *[Path(profile['paths'][key]) for key in ('vault','tasks','artifacts','docs','logs','worktrees','code')]]
    if any(inside(p.absolute(), directory) for p in private_paths for directory in protected):
        raise ValueError('Private configuration and context must be outside client skill directories and release packages.')
    if any(inside(state, directory.resolve()) or inside(directory.resolve(), state/'packages')
           or inside(directory.resolve(), ROOT) for directory in destinations):
        raise ValueError('Client directories must be separate from package storage and source files.')
    registrations = json.loads((ROOT/'registrations.json').read_text())
    links = [(directory/name, package/relative) for directory in destinations for name, relative in registrations.items()]
    previous = state/'install-state.json'
    owned = json.loads(previous.read_text()).get('links', {}) if previous.exists() else {}
    # Detect every conflict before writing skills or answers.
    for link, target in links:
        if link.exists() or link.is_symlink():
            if not link.is_symlink() or str(link.readlink()) not in {str(target), owned.get(str(link))}:
                raise ValueError(f'Existing skill was preserved: {link.name}. Choose another skills directory.')
    if not package.exists():
        package.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(ROOT, package, ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache', '.git'))
    made = []
    try:
        for link, target in links:
            link.parent.mkdir(parents=True, exist_ok=True)
            if link.is_symlink() and link.readlink() == target:
                continue
            prior = str(link.readlink()) if link.is_symlink() else None
            if prior:
                link.unlink()
            link.symlink_to(target, target_is_directory=True)
            made.append((link, prior))
        if any(inside(p.resolve(), directory) for p in private_paths for directory in protected):
            raise ValueError('A private path resolves into a skill directory or release package.')
        # Initialize a minimal private context without replacing existing notes.
        scaffold = ROOT/'support/scaffold'
        initial = [(Path(profile['paths']['vault'])/'index.md', scaffold/'index.md'),
                   (Path(profile['paths']['vault'])/'AGENTS.md', scaffold/'conventions.md'),
                   (Path(profile['paths']['tasks'])/'index.md', scaffold/'tasks-index.md')]
        for destination, source in initial:
            if not destination.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open('x', encoding='utf-8') as stream:
                    stream.write(source.read_text())
        # Write through an existing profile symlink, preserving the user's locator.
        save_private(config.resolve() if config.is_symlink() else config, profile)
        save_private(previous, {'links': {**owned, **{str(link): str(target) for link, target in links}}})
    except Exception:
        for link, prior in reversed(made):
            link.unlink(missing_ok=True)
            if prior:
                link.symlink_to(prior, target_is_directory=True)
        raise
    print(f'Installed {len(registrations)} skills for {args.client}. Private answers were saved outside the package.')
    print('Restart the client or start a new session to discover the skills.')
    print('If using a custom profile path, set SKILLS_CONFIG to ' + str(config))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', choices=['codex', 'claude', 'both'], default='codex')
    parser.add_argument('--codex-dir', type=Path, default=Path.home()/'.codex/skills')
    parser.add_argument('--claude-dir', type=Path, default=Path.home()/'.claude/skills')
    parser.add_argument('--state-dir', type=Path, default=Path.home()/'.local/share/agent-skills')
    parser.add_argument('--config', type=Path, default=Path.home()/'.config/agent-skills/config.json')
    parser.add_argument('--answers', type=Path, help='JSON answers keyed by dotted profile fields (for unattended installation)')
    parser.add_argument('--modules', default='', help='Comma-separated optional modules')
    args = parser.parse_args()
    try:
        install(args)
    except (OSError, ValueError, EOFError) as error:
        parser.exit(2, 'Installation stopped: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
