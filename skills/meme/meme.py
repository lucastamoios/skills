#!/usr/bin/env python3
"""Generate a meme image from a template, using the memegen.link API.

No account, no API key, no dependencies. The API escapes the caption text
server side, so any characters can be passed through verbatim.

    meme.py search drake
    meme.py make drake "before" "after" -o /tmp/meme.png
    meme.py make custom "top" "bottom" --background https://example.com/pic.png
    meme.py --selftest

memegenerator.net is dead (it refuses connections, homepage included) and
imgflip needs an account, which is why this targets memegen.link instead.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request

API = "https://api.memegen.link"
TIMEOUT = 30
# Cloudflare in front of memegen.link answers 403 (error 1010) to urllib's default
# "Python-urllib/x.y" agent. Any ordinary browser agent gets through.
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def _open(url, data=None, content_type=None):
    headers = {"User-Agent": UA}
    if content_type:
        headers["Content-Type"] = content_type
    return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=TIMEOUT)


def _get(path):
    with _open(f"{API}{path}") as response:
        return json.load(response)


def search(query):
    query = query.lower()
    matches = [
        template
        for template in _get("/templates")
        if query in template["name"].lower()
        or query in template["id"].lower()
        or any(query in keyword.lower() for keyword in template.get("keywords") or [])
    ]
    # The API lists a few templates twice under different aliases.
    seen = set()
    for template in matches:
        if template["id"] in seen:
            continue
        seen.add(template["id"])
        print(f"{template['id']:20} lines={template['lines']}  {template['name']}")
    if not matches:
        print(f"No template matches {query!r}. Try a broader word.", file=sys.stderr)
        return 1
    return 0


def make(template, lines, out_path, background=None):
    payload = {"template_id": template, "text": lines, "extension": "png"}
    if background:
        payload["background"] = background

    try:
        with _open(f"{API}/images", json.dumps(payload).encode(), "application/json") as response:
            url = json.load(response)["url"]
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")[:200]
        print(f"memegen.link rejected the request ({error.code}): {detail}", file=sys.stderr)
        return 1

    with _open(url) as response:
        image = response.read()
    with open(out_path, "wb") as handle:
        handle.write(image)

    print(url)
    print(f"{out_path} ({len(image) // 1024} KB)")
    return 0


def selftest():
    """One real round trip. Fails if the API, the payload shape, or the download breaks."""
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        assert make("drake", ["no subject", "a subject"], tmp.name) == 0
        data = open(tmp.name, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "response was not a PNG"
    assert len(data) > 10_000, f"PNG suspiciously small: {len(data)} bytes"
    print("selftest ok")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--selftest", action="store_true", help="round trip against the live API")
    sub = parser.add_subparsers(dest="command")

    search_parser = sub.add_parser("search", help="find a template by name or keyword")
    search_parser.add_argument("query")

    make_parser = sub.add_parser("make", help="render a meme to a file")
    make_parser.add_argument("template", help="template id, or 'custom' with --background")
    make_parser.add_argument("lines", nargs="+", help="caption lines, top to bottom")
    make_parser.add_argument("-o", "--out", default="meme.png")
    make_parser.add_argument("--background", help="public image URL, requires template 'custom'")

    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.command == "search":
        return search(args.query)
    if args.command == "make":
        return make(args.template, args.lines, args.out, args.background)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
