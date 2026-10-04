"""Tests for the shared Painter-language mechanism."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "rizum_ui" / "localization.py"
FALLBACK = {"title": "Title", "count": "Items: {count}", "only_en": "English only"}


def load_module(name="rizum_ui_localization_test"):
    spec = importlib.util.spec_from_file_location(name, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_catalogs(directory, catalogs):
    for stem, data in catalogs.items():
        (Path(directory) / f"{stem}.json").write_text(
            json.dumps(data, ensure_ascii=False),
            encoding="utf-8",
        )


class LocalizationMechanismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loc = load_module()

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)
        write_catalogs(
            self.directory,
            {
                "en": {"title": "Title", "count": "Items: {count}"},
                "zh-CN": {"title": "标题", "count": "项目：{count}"},
                "ja": {"title": "タイトル", "count": "項目: {count}"},
                "pt": {"title": "Título", "count": "Itens: {count}"},
            },
        )
        (self.directory / "broken.json").write_text("{", encoding="utf-8")
        (self.directory / "list.json").write_text("[]", encoding="utf-8")
        self.catalogs = self.loc.load_catalogs(self.directory, FALLBACK)

    def test_catalog_codes_register_their_root(self):
        self.assertIs(self.catalogs["zh"], self.catalogs["zh_cn"])
        self.assertEqual(self.catalogs["zh"]["title"], "标题")

    def test_english_comes_from_the_catalog_file_over_the_fallback(self):
        self.assertEqual(self.catalogs["en"], {"title": "Title", "count": "Items: {count}"})

    def test_unreadable_and_non_object_catalogs_are_skipped(self):
        self.assertNotIn("broken", self.catalogs)
        self.assertNotIn("list", self.catalogs)

    def test_missing_directory_leaves_only_the_fallback(self):
        catalogs = self.loc.load_catalogs(self.directory / "absent", FALLBACK)
        self.assertEqual(catalogs, {"en": FALLBACK})
        self.assertIsNot(catalogs["en"], FALLBACK)

    def test_resolution_tries_exact_code_then_root_then_english(self):
        resolve = self.loc.resolve_language
        self.assertEqual(resolve(self.catalogs, "zh-CN"), "zh_cn")
        self.assertEqual(resolve(self.catalogs, "zh_TW"), "zh")
        self.assertEqual(resolve(self.catalogs, "ja_JP"), "ja")
        self.assertEqual(resolve(self.catalogs, "pt-BR"), "pt")
        self.assertEqual(resolve(self.catalogs, "nl_NL"), "en")
        self.assertEqual(resolve(self.catalogs), "en")

    def test_unmatched_and_empty_candidates_are_skipped(self):
        resolve = self.loc.resolve_language
        self.assertEqual(resolve(self.catalogs, "", "ja_JP"), "ja")
        self.assertEqual(resolve(self.catalogs, None, "custom", "pt_PT"), "pt")
        self.assertEqual(resolve(self.catalogs, "ja", "zh"), "ja")

    def test_format_text_falls_back_to_english_then_the_key(self):
        text = self.loc.format_text
        catalogs = self.catalogs
        catalogs["en"]["only_en"] = "English only"
        self.assertEqual(text(catalogs, "zh", "count", {"count": 3}), "项目：3")
        self.assertEqual(text(catalogs, "zh", "only_en", {}), "English only")
        self.assertEqual(text(catalogs, "zh", "absent", {}), "absent")
        self.assertEqual(text(catalogs, "xx", "title", {}), "Title")

    def test_format_text_returns_the_template_when_values_do_not_fit(self):
        text = self.loc.format_text
        self.catalogs["en"]["brace"] = "Progress {"
        self.assertEqual(text(self.catalogs, "ja", "count", {}), "項目: {count}")
        self.assertEqual(text(self.catalogs, "en", "count", {"count": 2}), "Items: 2")
        self.assertEqual(text(self.catalogs, "en", "brace", {"count": 2}), "Progress {")

    def test_supported_languages_lists_root_codes_only(self):
        self.assertEqual(
            self.loc.supported_languages(self.catalogs),
            ("en", "ja", "pt", "zh"),
        )


class LanguageCandidateTests(unittest.TestCase):
    def test_module_imports_and_reads_without_pyside6(self):
        with mock.patch.dict(sys.modules, {"PySide6": None, "PySide6.QtCore": None}):
            loc = load_module("rizum_ui_localization_without_qt")
            self.assertEqual(loc.read_painter_language(), "")
            self.assertEqual(loc.read_system_language(), "")

    def test_candidates_come_from_painters_preference_and_the_system_locale(self):
        requested = []

        class Settings:
            def __init__(self, *scope):
                requested.append(scope)

            def value(self, key, default=""):
                requested.append(key)
                return "ja"

        class Locale:
            @staticmethod
            def system():
                return types.SimpleNamespace(name=lambda: "de_DE")

        qt_core = types.ModuleType("PySide6.QtCore")
        qt_core.QSettings = Settings
        qt_core.QLocale = Locale
        package = types.ModuleType("PySide6")
        package.QtCore = qt_core
        with mock.patch.dict(sys.modules, {"PySide6": package, "PySide6.QtCore": qt_core}):
            loc = load_module("rizum_ui_localization_stubbed_qt")
            self.assertEqual(loc.read_painter_language(), "ja")
            self.assertEqual(loc.read_system_language(), "de_DE")
        self.assertEqual(
            requested,
            [("Adobe", "Adobe Substance 3D Painter"), "General/UI_LANGUAGE"],
        )


if __name__ == "__main__":
    unittest.main()
