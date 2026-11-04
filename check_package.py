#!/usr/bin/env python3
"""Check a prepared package for accidental private data and damaged files."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent
PATTERNS={
    'private-key':r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
    'provider-token':r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-|ant-)?[A-Za-z0-9_-]{30,}|AKIA[A-Z0-9]{16}|xox[baprs]-[A-Za-z0-9-]{20,}|lin_api_[A-Za-z0-9]{20,})',
    'jwt':r'eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}',
    'personal-home':r'/(?:Users|home)/[A-Za-z0-9_.-]+/',
    'credential-url':r'\b(?:https?|postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^\s/:]+:[^\s/@]+@',
}
IGNORED={'__pycache__','.pytest_cache','.git'}


def inspect():
    errors=[]
    manifest=json.loads((ROOT/'manifest.json').read_text())
    actual=[]
    for path in ROOT.rglob('*'):
        relative=path.relative_to(ROOT)
        if any(p in IGNORED for p in relative.parts):continue
        if path.is_symlink():
            errors.append({'path':str(relative),'reason':'symlink in package'})
            continue
        if not path.is_file():continue
        actual.append(str(relative))
        if path.name in {'.env','config.json','profile.json','install-state.json'} or any(p in {'.git','vault','logs','context'} for p in relative.parts):
            errors.append({'path':str(relative),'reason':'private or generated member'})
        if str(relative)!='manifest.json' and manifest.get(str(relative))!=hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append({'path':str(relative),'reason':'unexpected or changed file'})
        try:text=path.read_text()
        except UnicodeDecodeError:
            errors.append({'path':str(relative),'reason':'binary member needs explicit review'})
            continue
        for name,pattern in PATTERNS.items():
            if re.search(pattern,text):errors.append({'path':str(relative),'reason':name})
    for name in manifest:
        if name not in actual:errors.append({'path':name,'reason':'missing file'})
    return errors


if __name__=='__main__':
    errors=inspect()
    print(json.dumps({'status':'FAIL' if errors else 'PASS','findings':errors},indent=2))
    sys.exit(bool(errors))
