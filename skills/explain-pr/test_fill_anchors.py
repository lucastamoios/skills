from fill_anchors import fill

FILES = {"a.py": "def f():\n    return 1\n\ndef g():\n    return 1\n"}


def fetch(repository, sha, path):
    return FILES.get(path)


def document(anchors):
    return {"repository": "o/r", "head_sha": "0" * 40, "anchors": anchors}


def test_fills_text_from_head():
    doc = document({"f": {"path": "a.py", "line": 4, "span": 1}})
    assert fill(doc, fetch) == ([], [])
    assert doc["anchors"]["f"] == {"path": "a.py", "line": 4, "text": "def g():"}


def test_reports_text_at_wrong_line():
    doc = document({"f": {"path": "a.py", "line": 1, "text": "def g():\n"}})
    problems, _ = fill(doc, fetch)
    assert problems == ["anchors.f: text not at line 1 of a.py (found at [4])"]


def test_warns_on_ambiguous_text_and_rejects_missing_file():
    doc = document(
        {
            "r": {"path": "a.py", "line": 2, "text": "    return 1"},
            "gone": {"path": "b.py"},
            "removed": {"path": "b.py", "absent": True},
        }
    )
    problems, warnings = fill(doc, fetch)
    assert problems == ["anchors.gone: b.py is not a file at head"]
    assert warnings == ["anchors.r: text also occurs at [2, 5]; widen span"]


def test_rejects_inline_link_to_unknown_anchor():
    doc = document({"f": {"path": "a.py"}})
    doc["items"] = [{"id": "i1", "text": "See [[f]] and [[i1|the item]]."}]
    problems, _ = fill(doc, fetch)
    assert problems == ["items.i1: [[i1]] is not an anchor id"]


def test_relocate_moves_text_found_once():
    doc = document({"f": {"path": "a.py", "line": 1, "text": "def g():"}})
    assert fill(doc, fetch, relocate=True) == ([], ["anchors.f: moved from line 1 to line 4 of a.py"])
    assert doc["anchors"]["f"]["line"] == 4


def test_relocate_keeps_missing_and_ambiguous_text_as_problems():
    doc = document(
        {
            "missing": {"path": "a.py", "line": 1, "text": "def h():"},
            "ambiguous": {"path": "a.py", "line": 1, "text": "    return 1"},
        }
    )
    problems, _ = fill(doc, fetch, relocate=True)
    assert problems == [
        "anchors.missing: text not at line 1 of a.py (not found)",
        "anchors.ambiguous: text not at line 1 of a.py (found at [2, 5])",
    ]
    assert doc["anchors"]["ambiguous"]["line"] == 1


def test_without_relocate_moved_text_stays_a_problem():
    doc = document({"f": {"path": "a.py", "line": 1, "text": "def g():"}})
    problems, _ = fill(doc, fetch)
    assert problems == ["anchors.f: text not at line 1 of a.py (found at [4])"]
    assert doc["anchors"]["f"]["line"] == 1
