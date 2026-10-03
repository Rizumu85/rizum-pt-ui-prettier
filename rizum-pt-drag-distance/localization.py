"""Painter-language localization for Drag Distance."""

from __future__ import annotations

import json
from pathlib import Path


DEFAULT_LANGUAGE = "en"
I18N_DIR = Path(__file__).resolve().parent / "i18n"
PAINTER_SETTINGS = ("Adobe", "Adobe Substance 3D Painter")
LANGUAGE_SETTING = "General/UI_LANGUAGE"
FALLBACK_TEXT = {
    "menu_title": "Drag Distance",
    "current": "Current: {distance} pixels",
    "menu_settings": "Drag Distance Settings...",
    "dialog_title": "Drag Distance Settings",
    "drag_distance": "Drag distance",
    "pixels": "pixels",
    "cancel": "Cancel",
    "ok": "OK",
}


def normalize_language(language) -> str:
    return str(language or "").strip().lower().replace("-", "_")


def _load_catalogs(directory: Path = I18N_DIR) -> dict[str, dict[str, str]]:
    catalogs = {DEFAULT_LANGUAGE: dict(FALLBACK_TEXT)}
    if not directory.exists():
        return catalogs

    for path in sorted(directory.glob("*.json")):
        language = normalize_language(path.stem)
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        catalogs[language] = {
            str(key): str(value)
            for key, value in data.items()
        }
        root = language.split("_", 1)[0]
        catalogs.setdefault(root, catalogs[language])
    return catalogs


CATALOGS = _load_catalogs()


def resolve_language(*candidates) -> str:
    for candidate in candidates:
        language = normalize_language(candidate)
        if not language:
            continue
        if language in CATALOGS:
            return language
        root = language.split("_", 1)[0]
        if root in CATALOGS:
            return root
    return DEFAULT_LANGUAGE


def read_painter_language() -> str:
    """The language chosen in Painter's Language preference.

    Painter's log names a locale too, but only after the plugins have
    started, so reading the log left every plugin in English on a freshly
    started non-English Painter.
    """
    from PySide6 import QtCore

    return str(QtCore.QSettings(*PAINTER_SETTINGS).value(LANGUAGE_SETTING, "") or "")


def read_system_language() -> str:
    from PySide6 import QtCore

    return QtCore.QLocale.system().name()


# Painter's Language preference starts as "Default (System Language)", which
# names no language and makes Painter follow the system locale. A fresh
# install is in that state, so the system locale is the second candidate.
CURRENT_LANGUAGE = resolve_language(read_painter_language(), read_system_language())


def text(key: str, *, language: str | None = None, **values) -> str:
    language = resolve_language(language) if language else CURRENT_LANGUAGE
    catalog = CATALOGS.get(language, CATALOGS[DEFAULT_LANGUAGE])
    template = catalog.get(key, CATALOGS[DEFAULT_LANGUAGE].get(key, key))
    try:
        return template.format(**values)
    except (KeyError, ValueError):
        return template


def supported_languages() -> tuple[str, ...]:
    return tuple(
        sorted(
            language
            for language in CATALOGS
            if "_" not in language
        )
    )
