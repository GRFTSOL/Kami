"""Shared constants and helpers for kami build and stabilize scripts."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "assets" / "templates"
DIAGRAMS = ROOT / "assets" / "diagrams"
EXAMPLES = ROOT / "assets" / "examples"
TOKENS_FILE = ROOT / "references" / "tokens.json"
FONTCONFIG_CACHE = Path("/private/tmp/kami-fontconfig-cache")
HOMEBREW_LIB = Path("/opt/homebrew/lib")


def configure_weasyprint_runtime() -> None:
    """Make macOS Homebrew native libraries discoverable before importing WeasyPrint."""
    os.environ.setdefault("XDG_CACHE_HOME", str(FONTCONFIG_CACHE))

    if sys.platform != "darwin":
        return

    if not (HOMEBREW_LIB / "libgobject-2.0.dylib").exists():
        return

    existing = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    paths = [path for path in existing.split(":") if path]
    brew_lib = str(HOMEBREW_LIB)
    if brew_lib in paths:
        return

    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = ":".join([brew_lib, *paths])

# Cool / neutral gray hex values that violate the "warm undertone only" rule.
COOL_GRAY_BLOCKLIST = {
    "#888", "#888888", "#666", "#666666", "#999", "#999999",
    "#ccc", "#cccccc", "#ddd", "#dddddd", "#eee", "#eeeeee",
    "#111", "#111111", "#222", "#222222", "#333", "#333333",
    "#444", "#444444", "#555", "#555555", "#777", "#777777",
    "#aaa", "#aaaaaa", "#bbb", "#bbbbbb",
    # Tailwind cool grays
    "#6b7280", "#9ca3af", "#d1d5db", "#e5e7eb", "#f3f4f6",
    "#4b5563", "#374151", "#1f2937", "#111827",
    # Bootstrap-like neutrals
    "#f8f9fa", "#e9ecef", "#dee2e6", "#ced4da", "#adb5bd",
    "#6c757d", "#495057", "#343a40", "#212529",
}
