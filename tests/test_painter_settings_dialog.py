from __future__ import annotations

import os
import json
import subprocess
import sys
import textwrap
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtGui, QtWidgets

from rizum_ui import PainterSettingsDialog


class PainterSettingsDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(
            []
        )

    def test_default_frame_and_surface_follow_painter_geometry(self):
        dialog = PainterSettingsDialog()
        dialog_margins = dialog.layout().contentsMargins()
        margins = dialog.settingsSurfaceLayout().contentsMargins()

        self.assertEqual(
            (
                dialog_margins.left(),
                dialog_margins.top(),
                dialog_margins.right(),
                dialog_margins.bottom(),
            ),
            (0, 0, 0, 0),
        )
        self.assertEqual(
            (margins.left(), margins.top(), margins.right(), margins.bottom()),
            (2, 0, 2, 2),
        )
        self.assertEqual(dialog.settingsFrameWidth(), 2)
        self.assertEqual(dialog.settingsFrameBottomWidth(), 2)
        self.assertTrue(dialog.settingsBottomEdgeExtensionEnabled())
        self.assertEqual(dialog.settingsWindowRadius(), 10.0)
        self.assertEqual(dialog.settingsSurfaceTopRadius(), 10.0)
        self.assertEqual(dialog.settingsSurfaceRadius(), 8.0)
        self.assertTrue(
            dialog.testAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        )
        surface_stylesheet = dialog.settingsSurface().styleSheet()
        self.assertIn("background: #1b1b1b", surface_stylesheet)
        self.assertNotIn("border-bottom", surface_stylesheet)
        self.assertNotIn("border-radius", surface_stylesheet)
        self.assertNotIn("radius:", surface_stylesheet)
        self.assertEqual(
            dialog.settingsSurface().paintedSurfaceColor().name(),
            "#1b1b1b",
        )

    def test_surface_paint_color_tracks_consumer_qss_override(self):
        dialog = PainterSettingsDialog()
        surface = dialog.settingsSurface()

        surface.setStyleSheet(
            surface.styleSheet()
            + "QFrame#RizumPainterSettingsSurface { background: #f3f3f3; }"
        )

        self.assertEqual(surface.paintedSurfaceColor().name(), "#f3f3f3")

    def test_frame_width_recomputes_parallel_inner_curve(self):
        dialog = PainterSettingsDialog()

        dialog.setSettingsFrameWidth(3)

        margins = dialog.settingsSurfaceLayout().contentsMargins()
        self.assertEqual(
            (margins.left(), margins.top(), margins.right(), margins.bottom()),
            (3, 0, 3, 3),
        )
        self.assertEqual(dialog.settingsSurfaceRadius(), 7.0)
        self.assertEqual(dialog.settingsSurfaceTopRadius(), 10.0)

    def test_painted_frame_is_two_device_pixels_with_clean_corners(self):
        probe = textwrap.dedent(
            """
            import json
            import math
            from PySide6 import QtGui, QtWidgets
            from rizum_ui import PainterSettingsDialog

            app = QtWidgets.QApplication([])
            dialog = PainterSettingsDialog()
            dialog.resize(120, 80)
            dialog.show()
            app.processEvents()
            image = dialog.grab().toImage().convertToFormat(
                QtGui.QImage.Format.Format_RGB32
            )
            dpr = image.devicePixelRatio()
            width, height = image.width(), image.height()

            # Ideal panel geometry in device pixels, derived independently
            # from the design contract: a 2-device-pixel frame on the left,
            # right, and bottom; 10px/8px logical corner radii.
            frame = 2.0
            top_radius = 10.0 * dpr
            bottom_radius = 8.0 * dpr
            x0, x1, y1 = frame, width - frame, height - frame

            def red(x, y):
                return image.pixelColor(x, y).red()

            def inside_panel(px, py, inset=0.0):
                ax0, ax1 = x0 + inset, x1 - inset
                ay0, ay1 = 0.0 + inset, y1 - inset
                if px < ax0 or px >= ax1 or py < ay0 or py >= ay1:
                    return False
                tr = max(0.0, top_radius - inset)
                br = max(0.0, bottom_radius - inset)
                # Only the cut-out quadrant of each corner square leaves the
                # panel; the other quadrants are the flat edge runs.
                for cx, cy, r, qx, qy in (
                    (ax0 + tr, ay0 + tr, tr, -1.0, -1.0),
                    (ax1 - tr, ay0 + tr, tr, 1.0, -1.0),
                    (ax0 + br, ay1 - br, br, -1.0, 1.0),
                    (ax1 - br, ay1 - br, br, 1.0, 1.0),
                ):
                    dx = (px - cx) * qx
                    dy = (py - cy) * qy
                    if dx > 0 and dy > 0 and dx * dx + dy * dy > r * r:
                        return False
                return True

            violations = []

            # 1) The straight bottom band is exactly two device pixels tall.
            straight_left = int(math.ceil(x0 + bottom_radius)) + 1
            straight_right = int(math.floor(x1 - bottom_radius)) - 1
            for x in range(straight_left, straight_right + 1):
                run = 0
                for y in range(height - 1, -1, -1):
                    if red(x, y) < 230:
                        break
                    run += 1
                if run != 2:
                    violations.append(f"bottom run at x={x}: {run} (want 2)")
                # 1b) The row right above the frame must be fully dark:
                # no fractional-DPR bleed row is allowed.
                if red(x, height - 3) >= 60:
                    violations.append(
                        f"bleed row above bottom frame at x={x}: "
                        f"{red(x, height - 3)}"
                    )

            # 2) The straight side bands are exactly two device pixels wide.
            straight_top = int(math.ceil(top_radius)) + 1
            straight_bottom = int(math.floor(y1 - bottom_radius)) - 1
            for y in range(straight_top, straight_bottom + 1):
                left_run = 0
                for x in range(width):
                    if red(x, y) < 230:
                        break
                    left_run += 1
                if left_run != 2:
                    violations.append(f"left run at y={y}: {left_run} (want 2)")
                right_run = 0
                for x in range(width - 1, -1, -1):
                    if red(x, y) < 230:
                        break
                    right_run += 1
                if right_run != 2:
                    violations.append(
                        f"right run at y={y}: {right_run} (want 2)"
                    )
                if red(2, y) >= 60 or red(width - 3, y) >= 60:
                    violations.append(
                        f"bleed column inside side frame at y={y}: "
                        f"{red(2, y)}/{red(width - 3, y)}"
                    )

            # 3) Corner columns follow the arc: no staircase, no thickening.
            def predicted_run(x):
                px = x + 0.5
                if px < x0:
                    return float(height)
                if px >= x1:
                    return float(height)
                if px < x0 + bottom_radius:
                    cx = x0 + bottom_radius
                    dy = math.sqrt(
                        max(0.0, bottom_radius**2 - (px - cx) ** 2)
                    )
                    return height - (y1 - bottom_radius + dy)
                if px >= x1 - bottom_radius:
                    cx = x1 - bottom_radius
                    dy = math.sqrt(
                        max(0.0, bottom_radius**2 - (px - cx) ** 2)
                    )
                    return height - (y1 - bottom_radius + dy)
                return height - y1

            for x in range(width):
                run = 0
                for y in range(height - 1, -1, -1):
                    if red(x, y) < 230:
                        break
                    run += 1
                expected = predicted_run(x)
                # The >=230 run counts ~full-coverage pixels while
                # predicted_run samples the column center; at the steep arc
                # section the circle crosses a column diagonally, biasing
                # the count down by up to ~1.6 rows. 2.0 still catches any
                # staircase or local thickening, which jumps by whole rows.
                if abs(run - expected) > 2.0:
                    violations.append(
                        f"bottom arc at x={x}: run {run} "
                        f"vs predicted {expected:.2f}"
                    )

            # 4) No bright artifacts inside the panel (miter, specks).
            for y in range(height):
                for x in range(width):
                    if inside_panel(x + 0.5, y + 0.5, inset=1.0):
                        if red(x, y) >= 60:
                            violations.append(
                                f"bright pixel inside panel at ({x}, {y}): "
                                f"{red(x, y)}"
                            )

            # 4b) Arc interiors just inside each corner curve stay dark.
            corners = (
                (x0 + top_radius, top_radius, 180.0, 270.0, top_radius),
                (x1 - top_radius, top_radius, 270.0, 360.0, top_radius),
                (x0 + bottom_radius, y1 - bottom_radius, 90.0, 180.0,
                 bottom_radius),
                (x1 - bottom_radius, y1 - bottom_radius, 0.0, 90.0,
                 bottom_radius),
            )
            for cx, cy, start, end, radius in corners:
                sample = radius - 0.75
                angle = start + 10.0
                while angle <= end - 10.0:
                    px = cx + sample * math.cos(math.radians(angle))
                    py = cy + sample * math.sin(math.radians(angle))
                    value = red(int(px), int(py))
                    if value >= 128:
                        violations.append(
                            f"bright arc interior at ({px:.1f}, {py:.1f}) "
                            f"angle {angle:.0f}: {value}"
                        )
                    angle += 10.0

            # 5) No dark bleed outside the panel into the frame ring.
            for y in range(height):
                for x in range(width):
                    if not inside_panel(x + 0.5, y + 0.5, inset=-1.0):
                        if red(x, y) < 230:
                            violations.append(
                                f"dark pixel inside frame ring at ({x}, {y})"
                                f": {red(x, y)}"
                            )

            print(json.dumps({"dpr": dpr, "violations": violations[:40]}))
            """
        )
        for scale in ("1.0", "1.125", "1.25", "1.5"):
            with self.subTest(dpr=scale):
                env = dict(os.environ)
                env["QT_QPA_PLATFORM"] = "offscreen"
                env["QT_SCALE_FACTOR"] = scale
                result = subprocess.run(
                    [sys.executable, "-c", probe],
                    check=True,
                    capture_output=True,
                    text=True,
                    env=env,
                )
                rendered = json.loads(result.stdout.strip())
                self.assertEqual(rendered["dpr"], float(scale))
                self.assertEqual(rendered["violations"], [])

    def test_settings_typography_tracks_ui_font_scale(self):
        dialog = PainterSettingsDialog()

        dialog.setSettingsUiScale(1.1)

        stylesheet = dialog.settingsSurface().styleSheet()
        self.assertEqual(dialog.settingsUiScale(), 1.1)
        self.assertEqual(dialog.settingsMetric(13), 14)
        self.assertIn("font-size: 11px", stylesheet)
        self.assertIn("font-size: 14px", stylesheet)
        self.assertIn("font-size: 12px", stylesheet)
        self.assertIn("font-weight: 700", stylesheet)

    def test_section_heading_color_matches_pt_bridge_reference(self):
        dialog = PainterSettingsDialog()
        stylesheet = dialog.settingsSurface().styleSheet()

        self.assertIn(
            "QLabel#RizumSettingsSection {\n"
            "                color: #666666;",
            stylesheet,
        )

    def test_show_preserves_consumer_surface_rules_when_scale_is_unchanged(self):
        self.app.setProperty("rizumUiFontScale", 1.0)
        dialog = PainterSettingsDialog()
        self.addCleanup(dialog.deleteLater)
        surface = dialog.settingsSurface()
        consumer_rule = "QWidget#ConsumerPanel { background: transparent; }"
        surface.setStyleSheet(surface.styleSheet() + consumer_rule)

        dialog.show()
        self.app.processEvents()

        self.assertIn(consumer_rule, surface.styleSheet())

    def test_metadata_labels_do_not_paint_over_parent_hover_fill(self):
        dialog = PainterSettingsDialog()
        stylesheet = dialog.settingsSurface().styleSheet()

        self.assertIn(
            "QLabel#RizumSettingsItemMeta,\n"
            "            QLabel#RizumSettingsFooterHint {\n"
            "                background: transparent;",
            stylesheet,
        )

    def test_native_window_paints_a_filled_frame_for_the_os_to_clip(self):
        previous_stylesheet = self.app.styleSheet()
        self.addCleanup(self.app.setStyleSheet, previous_stylesheet)
        self.app.setStyleSheet(
            "QDialog { background: #aa0000; } "
            "QFrame { background: #aa0000; border-radius: 0; }"
        )
        dialog = PainterSettingsDialog()
        self.addCleanup(dialog.deleteLater)
        dialog.setObjectName("ConsumerSettingsDialog")
        dialog.setStyleSheet("QLabel { color: white; }")
        dialog.resize(120, 80)
        dialog.show()
        self.app.processEvents()

        image = dialog.grab().toImage().convertToFormat(
            QtGui.QImage.Format.Format_ARGB32
        )
        self.assertEqual(image.pixelColor(0, 0).name(), "#f3f3f3")
        self.assertIn(
            'QDialog[rizumPainterSettingsDialog="true"]',
            dialog.styleSheet(),
        )

    def test_embedded_preview_simulates_the_native_rounded_window(self):
        host = QtWidgets.QWidget()
        self.addCleanup(host.deleteLater)
        host.setStyleSheet("QWidget { background: #202123; }")
        layout = QtWidgets.QVBoxLayout(host)
        layout.setContentsMargins(8, 8, 8, 8)
        dialog = PainterSettingsDialog(host)
        dialog.setWindowFlags(QtCore.Qt.WindowType.Widget)
        dialog.setSettingsFrameBottomWidth(dialog.settingsFrameWidth())
        dialog.setSettingsBottomEdgeExtensionEnabled(False)
        dialog.resize(120, 80)
        layout.addWidget(dialog)
        host.show()
        self.app.processEvents()

        image = host.grab().toImage().convertToFormat(
            QtGui.QImage.Format.Format_ARGB32
        )
        origin = dialog.mapTo(host, QtCore.QPoint(0, 0))
        self.assertNotEqual(
            image.pixelColor(origin).name(),
            "#f3f3f3",
            "embedded previews must antialias rather than fill the outer corner",
        )


if __name__ == "__main__":
    unittest.main()
