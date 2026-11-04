#!/usr/bin/env python3
"""Validate an architecture map and render complete function diffs in a standalone HTML page."""
import argparse
import difflib
import json
import html
from pathlib import Path
import uuid

KINDS = {'modified', 'added', 'deleted', 'moved', 'renamed', 'block'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def side_lines(side, label):
    if side is None:
        return []
    require(isinstance(side, dict), f'{label}: side must be an object or null')
    require(nonempty(side.get('path')), f'{label}: missing path')
    require(type(side.get('start_line')) is int and side['start_line'] > 0,
            f'{label}: start_line must be a positive integer')
    require(isinstance(side.get('source'), str), f'{label}: missing complete source')
    return side['source'].splitlines()


def prepare(data):
    require(isinstance(data, dict), 'Map must be an object')
    require(nonempty(data.get('title')), 'Missing title')
    require(isinstance(data.get('source'), dict), 'Missing source provenance')
    for key in ('base', 'head', 'snapshot', 'scope'):
        require(nonempty(data['source'].get(key)), f'Missing source.{key}')
    ids = set()

    def register(item, label):
        require(isinstance(item, dict), f'{label}: must be an object')
        identifier = item.get('id')
        require(nonempty(identifier) and identifier not in ids, f'{label}: missing or duplicate ID {identifier!r}')
        ids.add(identifier)

    modules = data.get('modules')
    domains = data.get('domains')
    require(isinstance(modules, list) and modules, 'At least one changed module is required')
    require(isinstance(domains, list) and domains, 'At least one domain is required')
    for module in modules:
        register(module, 'module')
        require(nonempty(module.get('path')), 'Module requires a path')
        require(module.get('change_kind') in KINDS, 'Invalid module change_kind')
        require(isinstance(module.get('functions'), list) and module['functions'],
                f"{module['path']}: include changed functions or honest block entries")
        for function in module['functions']:
            register(function, 'function')
            label = function.get('name', function['id'])
            require(nonempty(function.get('name')), 'Function requires name')
            require(function.get('change_kind') in KINDS, f'{label}: invalid change_kind')
            require(nonempty(function.get('business_rule')), f'{label}: missing business explanation')
            before, after = function.get('before'), function.get('after')
            old, new = side_lines(before, label), side_lines(after, label)
            require(old or new, f'{label}: both sides unavailable')
            if function['change_kind'] == 'added':
                require(not old and new, f'{label}: added entry must only have after')
            if function['change_kind'] == 'deleted':
                require(not new and old, f'{label}: deleted entry must only have before')
            parts = function.get('parts', [])
            require(isinstance(parts, list), f'{label}: parts must be a list')
            for part in parts:
                register(part, 'part')
                require(nonempty(part.get('title')) and nonempty(part.get('explanation')),
                        f'{label}: part requires title and explanation')
                present = False
                for prefix, lines in (('old', old), ('new', new)):
                    start, end = part.get(prefix + '_start'), part.get(prefix + '_end')
                    require((start is None) == (end is None), f'{label}: incomplete {prefix} range')
                    if start is not None:
                        present = True
                        require(type(start) is int and type(end) is int and 1 <= start <= end <= len(lines),
                                f'{label}: invalid {prefix} part range')
                require(present, f'{label}: part has no source range')
            rows = []

            def append(kind, old_index=None, new_index=None):
                annotations = []
                for part in parts:
                    for prefix, index in (('old', old_index), ('new', new_index)):
                        start, end = part.get(prefix + '_start'), part.get(prefix + '_end')
                        if index is not None and start is not None and start <= index + 1 <= end:
                            annotations.append(part['id'])
                            break
                rows.append({'kind': kind,
                             'old_line': before['start_line'] + old_index if old_index is not None else None,
                             'new_line': after['start_line'] + new_index if new_index is not None else None,
                             'text': old[old_index] if old_index is not None else new[new_index],
                             'parts': annotations})

            old_tokens = before['source'].splitlines(keepends=True) if before else []
            new_tokens = after['source'].splitlines(keepends=True) if after else []
            for tag, a, b, c, d in difflib.SequenceMatcher(None, old_tokens, new_tokens, autojunk=False).get_opcodes():
                if tag == 'equal':
                    for offset in range(b - a):
                        append('context', a + offset, c + offset)
                else:
                    for index in range(a, b):
                        append('deleted', old_index=index)
                    for index in range(c, d):
                        append('added', new_index=index)
            changed = [row for row in rows if row['kind'] != 'context']
            require(all(row['parts'] for row in changed), f'{label}: every changed line requires a diff-part explanation')
            location_changed = before and after and (before['path'], before['start_line']) != (after['path'], after['start_line'])
            if not changed:
                require(function['change_kind'] in {'moved', 'renamed'} and location_changed,
                        f'{label}: entry has no source or location change')
                require(parts, f'{label}: unchanged moved entry requires a location explanation part')
            explained_rows = changed if changed else rows
            used = {identifier for row in explained_rows for identifier in row['parts']}
            require(all(part['id'] in used for part in parts), f'{label}: part does not cover a changed line or moved context')
            function['diff_rows'] = rows
            function['trailing_newline'] = {'before': before['source'].endswith('\n') if old else None,
                                             'after': after['source'].endswith('\n') if new else None}
    module_ids = {module['id'] for module in modules}
    owned = set()
    positions = set()
    for domain in domains:
        register(domain, 'domain')
        require(nonempty(domain.get('label')), 'Domain requires label')
        for key in ('row', 'column'):
            require(type(domain.get(key)) is int and domain[key] >= 0, f'Domain {key} must be a nonnegative integer')
        position = (domain['row'], domain['column'])
        require(position not in positions, 'Domains must occupy distinct grid positions')
        positions.add(position)
        references = domain.get('module_ids')
        require(isinstance(references, list), 'Domain module_ids must be a list')
        require(all(isinstance(ref, str) for ref in references), 'Module references must be strings')
        require(len(references) == len(set(references)) and set(references) <= module_ids, 'Invalid module reference')
        owned.update(references)
    require(owned == module_ids, 'Every changed module must appear in a domain')
    domain_ids = {domain['id'] for domain in domains}
    edges = data.get('edges', [])
    require(isinstance(edges, list), 'Edges must be a list')
    for edge in edges:
        require(isinstance(edge, dict) and edge.get('from') in domain_ids and edge.get('to') in domain_ids,
                'Invalid edge domain reference')
        require(edge['from'] != edge['to'], 'Self edges are not supported')
        require(nonempty(edge.get('label')), 'Edge requires a relationship label')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--template', type=Path, default=Path(__file__).resolve().parents[1] / 'assets' / 'architecture-map.html')
    parser.add_argument('--fragment', action='store_true', help='Emit the legacy inline fragment instead of a standalone page')
    args = parser.parse_args()
    try:
        data = prepare(json.loads(args.input.read_text()))
        payload = json.dumps(data, ensure_ascii=True, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
        fragment = args.template.read_text().replace('__MAP_ROOT__', 'architecture-map-' + uuid.uuid4().hex).replace('__MAP_DATA__', payload)
        if args.fragment:
            document = fragment
            require(len(document.encode()) < 1_000_000, 'Fragment exceeds 1 MB; narrow the scope without truncating functions')
        else:
            css = (Path(__file__).resolve().parents[1] / 'assets' / 'standalone.css').read_text()
            title = html.escape(data['title'])
            document = f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title><style>{css}</style></head><body><main>{fragment}</main></body></html>\n'
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(document, encoding='utf-8')
    except (ValueError, KeyError, TypeError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
