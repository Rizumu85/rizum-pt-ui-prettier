"""The vendoring tool: which plugins it syncs and what counts as a change."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOL_PATH = Path(__file__).resolve().parents[1] / "tools" / "sync_vendor.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("rizum_sync_vendor_test", TOOL_PATH)
    module = importlib.util.module_from_spec(spec)
    # dataclasses looks the module up while the tool defines VendorFile.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SyncVendorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool = load_tool()

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.plugins = Path(temp.name)
        self.source = self.plugins / "kit"
        (self.source / "rizum_ui").mkdir(parents=True)
        self.source_file = self.source / "rizum_ui" / "theme.py"
        self.source_file.write_bytes(b"A = 1\r\nB = 2\r\n")
        self.files = [
            self.tool.VendorFile(
                source=self.source_file,
                relative=Path("rizum_ui/theme.py"),
            )
        ]

    def plugin(self, name, manifest=None, vendored=None):
        folder = self.plugins / name
        (folder / "rizum_ui").mkdir(parents=True)
        if manifest is not None:
            (folder / self.tool.MANIFEST_NAME).write_text(
                json.dumps(manifest),
                encoding="utf-8",
            )
        if vendored is not None:
            (folder / "rizum_ui" / "theme.py").write_bytes(vendored)
        return folder

    def manifest(self, folder):
        return json.loads(
            (folder / self.tool.MANIFEST_NAME).read_text(encoding="utf-8")
        )

    def test_default_targets_are_the_plugins_that_already_vendor_the_kit(self):
        first = self.plugin("rizum-pt-first", manifest={"files": []})
        second = self.plugin("rizum-pt-second", manifest={"files": []})
        self.plugin("rizum-pt-without-kit")
        self.plugin("other-plugin", manifest={"files": []})

        targets, pinned = self.tool.default_targets(self.plugins)

        self.assertEqual(targets, [first, second])
        self.assertEqual(pinned, [])

    def test_a_pinned_plugin_is_left_out_with_its_reason(self):
        synced = self.plugin("rizum-pt-synced", manifest={"files": []})
        held = self.plugin(
            "rizum-pt-held",
            manifest={"files": [], "pinned": "own edits"},
        )

        targets, pinned = self.tool.default_targets(self.plugins)

        self.assertEqual(targets, [synced])
        self.assertEqual(pinned, [(held, "own edits")])

    def test_syncing_a_pinned_plugin_by_name_keeps_the_pin(self):
        held = self.plugin(
            "rizum-pt-held",
            manifest={"files": [], "pinned": "own edits"},
            vendored=b"A = 0\n",
        )

        self.tool.sync_target(held, self.files, apply=True, delete_stale=False)

        self.assertEqual(self.manifest(held)["pinned"], "own edits")
        self.assertEqual(self.manifest(held)["files"], ["rizum_ui/theme.py"])
        self.assertEqual(
            (held / "rizum_ui" / "theme.py").read_bytes(),
            self.source_file.read_bytes(),
        )

    def test_a_sync_does_not_pin_a_plugin(self):
        free = self.plugin("rizum-pt-free", manifest={"files": []})

        self.tool.sync_target(free, self.files, apply=True, delete_stale=False)

        self.assertNotIn("pinned", self.manifest(free))

    def test_a_copy_that_differs_only_in_line_endings_is_left_alone(self):
        target = self.plugin(
            "rizum-pt-lf",
            manifest={"files": []},
            vendored=b"A = 1\nB = 2\n",
        )

        self.tool.sync_target(target, self.files, apply=True, delete_stale=False)

        self.assertEqual(
            (target / "rizum_ui" / "theme.py").read_bytes(),
            b"A = 1\nB = 2\n",
        )

    def test_a_changed_file_is_copied_with_the_source_bytes(self):
        target = self.plugin(
            "rizum-pt-old",
            manifest={"files": []},
            vendored=b"A = 0\nB = 2\n",
        )

        self.tool.sync_target(target, self.files, apply=True, delete_stale=False)

        self.assertEqual(
            (target / "rizum_ui" / "theme.py").read_bytes(),
            self.source_file.read_bytes(),
        )

    def test_a_dry_run_writes_nothing(self):
        target = self.plugin(
            "rizum-pt-old",
            manifest={"files": []},
            vendored=b"A = 0\n",
        )

        self.tool.sync_target(target, self.files, apply=False, delete_stale=False)

        self.assertEqual((target / "rizum_ui" / "theme.py").read_bytes(), b"A = 0\n")
        self.assertEqual(self.manifest(target), {"files": []})


if __name__ == "__main__":
    unittest.main()
