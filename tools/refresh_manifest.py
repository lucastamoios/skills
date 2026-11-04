#!/usr/bin/env python3
"""Refresh public file hashes after an intentional repository edit."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
DIRECTORIES={'skills','plugins','support','tests','tools','.github'}
FILES={'README.md','INSTALL.md','CATALOG.md','LICENSE','NOTICE.md','.gitignore','package.json','install.py','check_package.py','command-map.json','registrations.json','setup-questions.json'}
ignored={'__pycache__','.pytest_cache','.git'}
paths=[]
for p in ROOT.rglob('*'):
    relative=p.relative_to(ROOT)
    if any(part in ignored for part in relative.parts):continue
    if p.is_file() and (str(relative) in FILES or relative.parts[0] in DIRECTORIES):
        if p.is_symlink():raise SystemExit('Do not include symlinks in the public tree.')
        paths.append(p)
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'Refreshed {len(manifest)} public files.')
