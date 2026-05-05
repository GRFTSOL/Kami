#!/usr/bin/env python3
"""Lightweight tests for scripts/build.py and scripts/shared.py.

Run with: python3 scripts/tests/test_build.py
The harness uses plain assertions and a tiny runner so it has no third-party
dependency (matching the rest of the repo's lean tooling).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Make scripts/ importable when running this file directly.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from build import (  # noqa: E402
    DIAGRAM_TARGETS,
    HTML_TARGETS,
    PPTX_TARGETS,
    _parse_slide_sequence,
    scan_file,
)
from shared import (  # noqa: E402
    HTML_TEMPLATES,
    PARCHMENT_RGB,
    build_targets,
    stabilize_targets,
)


# --------------------------- helpers ---------------------------

_PASS = 0
_FAIL = 0


def check(name: str, predicate: bool, detail: str = "") -> None:
    global _PASS, _FAIL
    if predicate:
        _PASS += 1
        print(f"OK: {name}")
    else:
        _FAIL += 1
        print(f"ERROR: {name}{(' - ' + detail) if detail else ''}")


def write_temp_html(body: str, suffix: str = "-en.html") -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8")
    f.write(body)
    f.close()
    return Path(f.name)


# --------------------------- shared registry ---------------------------

def test_registry_consistency() -> None:
    check("HTML_TEMPLATES has 16 entries", len(HTML_TEMPLATES) == 16,
          f"got {len(HTML_TEMPLATES)}")
    check("build_targets matches HTML_TEMPLATES key set",
          set(build_targets()) == set(HTML_TEMPLATES))
    check("stabilize_targets is a subset of HTML_TEMPLATES",
          set(stabilize_targets()) <= set(HTML_TEMPLATES))
    check("HTML_TARGETS in build.py matches build_targets()",
          dict(HTML_TARGETS) == build_targets())
    check("DIAGRAM_TARGETS has 14 entries", len(DIAGRAM_TARGETS) == 14,
          f"got {len(DIAGRAM_TARGETS)}")
    check("PPTX_TARGETS has 2 entries", len(PPTX_TARGETS) == 2,
          f"got {len(PPTX_TARGETS)}")
    check("PARCHMENT_RGB is canonical", PARCHMENT_RGB == (0xF5, 0xF4, 0xED))


# --------------------------- scan_file ---------------------------

def test_scan_file_skip_bug() -> None:
    """Lines starting with '#' (CSS id selectors) must NOT be skipped."""
    fixture = """<!doctype html>
<html><head><style>
#card { background: rgba(0,0,0,0.5); }
</style></head><body></body></html>
"""
    p = write_temp_html(fixture)
    try:
        findings = scan_file(p)
        rules = {f.rule for f in findings}
        check("scan_file flags rgba on #id-prefixed CSS line",
              "rgba-background" in rules,
              f"rules found: {rules or '(none)'}")
    finally:
        p.unlink(missing_ok=True)


def test_scan_file_arrow_in_en() -> None:
    """`→` in -en.html body should trigger arrow-unicode-in-en."""
    fixture = """<!doctype html>
<html lang="en"><head><style>
.tag { color: #1B365D; }
</style></head><body>
<p>Step 1 → Step 2</p>
</body></html>
"""
    p = write_temp_html(fixture, suffix="-en.html")
    try:
        findings = scan_file(p)
        rules = {f.rule for f in findings}
        check("scan_file flags U+2192 arrow in -en.html",
              "arrow-unicode-in-en" in rules,
              f"rules found: {rules or '(none)'}")
    finally:
        p.unlink(missing_ok=True)


def test_scan_file_clean_template() -> None:
    """A clean template should produce zero findings."""
    fixture = """<!doctype html>
<html><head><style>
:root { --brand: #1B365D; }
.card { background: var(--ivory); }
.tag { background: #EEF2F7; color: var(--brand); }
</style></head><body></body></html>
"""
    p = write_temp_html(fixture)
    try:
        findings = scan_file(p)
        check("scan_file produces no findings on clean template",
              len(findings) == 0,
              f"got {len(findings)} finding(s): {[f.rule for f in findings]}")
    finally:
        p.unlink(missing_ok=True)


# --------------------------- slide sequence ---------------------------

def test_parse_slide_sequence_empty() -> None:
    fixture = """def main():
    pass
"""
    p = write_temp_html(fixture, suffix=".py")
    try:
        seq = _parse_slide_sequence(p)
        check("_parse_slide_sequence returns [] for empty main()",
              seq == [], f"got {seq}")
    finally:
        p.unlink(missing_ok=True)


def test_parse_slide_sequence_basic() -> None:
    fixture = """def main():
    cover_slide()
    content_slide()
    content_slide()
    chapter_slide()
    metrics_slide()

def helper():
    other_call()
"""
    p = write_temp_html(fixture, suffix=".py")
    try:
        seq = _parse_slide_sequence(p)
        expected = ["cover_slide", "content_slide", "content_slide", "chapter_slide", "metrics_slide"]
        check("_parse_slide_sequence parses ordered slide calls",
              seq == expected, f"got {seq}")
    finally:
        p.unlink(missing_ok=True)


# --------------------------- runner ---------------------------

def main() -> int:
    test_registry_consistency()
    test_scan_file_skip_bug()
    test_scan_file_arrow_in_en()
    test_scan_file_clean_template()
    test_parse_slide_sequence_empty()
    test_parse_slide_sequence_basic()
    print()
    print(f"Passed: {_PASS} | Failed: {_FAIL}")
    return 0 if _FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
