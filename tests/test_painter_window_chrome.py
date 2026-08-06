from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtWidgets

from preview import build_bridge_preview, build_settings_preview
from rizum_ui import (
    PAINTER_SETTINGS_LAYOUT,
    PAINTER_WINDOW_CONTENT_RADIUS,
    PainterSettingsDialog,
    make_painter_title_bar,
)
from view_roll_preview import ViewRollConceptPanel


class PainterWindowChromeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        cls.app.setProperty("rizumUiFontScale", 1.0)

    def test_title_bar_stays_at_native_metrics_when_content_scale_changes(self):
        title_bar = make_painter_title_bar("Export")
        self.addCleanup(title_bar.deleteLater)

        self.assertEqual(title_bar.height(), 32)
        title_bar.setCompactHeight(40)
        self.assertEqual(title_bar.height(), 32)
        icon = title_bar.findChild(QtWidgets.QLabel, "RizumPainterTitleBarIcon")
        title = title_bar.findChild(QtWidgets.QLabel, "RizumPainterTitleBarText")
        self.assertEqual((icon.width(), icon.height()), (14, 14))
        self.assertEqual(title.font().pixelSize(), 12)
        self.assertTrue(
            title_bar.testAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)
        )

    def test_reference_panels_omit_platform_owned_title_bars(self):
        panels = [
            build_bridge_preview(QtWidgets),
            build_settings_preview(QtWidgets),
            ViewRollConceptPanel(),
        ]
        for panel in panels:
            self.addCleanup(panel.deleteLater)
            self.assertEqual(
                len(
                    panel.findChildren(
                        QtWidgets.QWidget,
                        "RizumPainterTitleBar",
                    )
                ),
                0,
            )
            self.assertEqual(
                len(
                    panel.findChildren(
                        QtWidgets.QFrame,
                        "RizumPainterWindowContent",
                    )
                ),
                1,
            )

    def test_preview_panels_do_not_duplicate_native_window_titles(self):
        panels = [
            (build_bridge_preview(QtWidgets), "RizumExportTitle"),
            (build_settings_preview(QtWidgets), "RizumSettingsTitle"),
            (ViewRollConceptPanel(), "RizumViewRollTitle"),
        ]
        for panel, old_title_name in panels:
            self.addCleanup(panel.deleteLater)
            self.assertIsNone(panel.findChild(QtWidgets.QLabel, old_title_name))

    def test_view_roll_preview_has_no_platform_frame_decoration(self):
        panel = ViewRollConceptPanel()
        self.addCleanup(panel.deleteLater)

        content = panel.findChild(QtWidgets.QFrame, "RizumPainterWindowContent")
        self.assertIsNotNone(content)
        self.assertIn(
            "border-top-left-radius: 0px",
            content.styleSheet(),
        )
        self.assertIn(
            f"border-bottom-left-radius: {PAINTER_WINDOW_CONTENT_RADIUS}px",
            content.styleSheet(),
        )
        self.assertIn(
            "background: #1b1b1b",
            panel.dialog.settingsSurface().styleSheet(),
        )

    def test_bridge_preview_uses_canonical_export_layout(self):
        bridge = build_bridge_preview(QtWidgets)
        self.addCleanup(bridge.deleteLater)

        self.assertIsInstance(bridge, PainterSettingsDialog)
        top_controls = bridge._rizum_top_controls
        top_margins = top_controls.layout().contentsMargins()
        self.assertEqual(
            top_controls.height(), PAINTER_SETTINGS_LAYOUT.row_height.design
        )
        self.assertEqual(
            top_margins.left(), PAINTER_SETTINGS_LAYOUT.body_margin_x.design
        )
        self.assertEqual(
            top_margins.right(), PAINTER_SETTINGS_LAYOUT.body_margin_x.design
        )

        footer = bridge.findChild(QtWidgets.QWidget, "RizumExportFooter")
        footer_row = bridge.findChild(QtWidgets.QWidget, "RizumExportFooterRow")
        footer_margins = footer_row.layout().contentsMargins()
        self.assertEqual(
            footer_margins.left(), PAINTER_SETTINGS_LAYOUT.footer_margin_x.design
        )
        self.assertEqual(
            footer_margins.right(), PAINTER_SETTINGS_LAYOUT.footer_margin_x.design
        )
        self.assertEqual(
            footer.height(),
            PAINTER_SETTINGS_LAYOUT.footer_top.design
            + PAINTER_SETTINGS_LAYOUT.footer_gap.design
            + PAINTER_SETTINGS_LAYOUT.footer_row_height.design
            + PAINTER_SETTINGS_LAYOUT.footer_bottom.design,
        )
        self.assertIs(
            footer_row.layout().itemAt(0).widget(), bridge._rizum_cancel_button
        )
        self.assertIs(
            footer_row.layout().itemAt(2).widget(), bridge._rizum_export_button
        )
        self.assertIn("background: #202020", bridge.settingsSurface().styleSheet())

    def test_bridge_preview_scales_fixed_component_internals(self):
        bridge = build_bridge_preview(QtWidgets)
        self.addCleanup(bridge.deleteLater)

        bridge.setSettingsUiScale(1.1)
        top_controls = bridge._rizum_top_controls
        combo = top_controls._rizum_left_controls[0]
        group = bridge._rizum_groups[0]
        chevron = group["widget"].findChild(
            QtWidgets.QWidget, "RizumCollapsibleChevron"
        )

        self.assertEqual(
            top_controls.height(),
            PAINTER_SETTINGS_LAYOUT.row_height.resolve(bridge),
        )
        self.assertEqual(
            combo.height(), PAINTER_SETTINGS_LAYOUT.control_height.resolve(bridge)
        )
        self.assertEqual(
            group["widget"]._rizum_header.height(), bridge.settingsMetric(36, 27)
        )
        expected_chevron = max(
            11,
            round(14 * group["widget"]._rizum_header.height() / 36),
        )
        self.assertEqual(chevron.width(), expected_chevron)
        self.assertEqual(
            group["parent"].checkboxSize(), bridge.settingsMetric(14, 11)
        )
        self.assertEqual(
            group["rows"][0]._rizum_right_inset,
            bridge.settingsMetric(4, 3),
        )

    def test_export_children_inset_hover_edge_without_moving_checkboxes(self):
        bridge = build_bridge_preview(QtWidgets)
        self.addCleanup(bridge.deleteLater)
        bridge.show()
        self.app.processEvents()

        group = bridge._rizum_groups[0]
        group_widget = group["widget"]
        parent_label = group_widget.findChild(
            QtWidgets.QLabel, "RizumCollapsibleTitle"
        )
        child_host = group["rows"][0]
        child_row = child_host._rizum_row

        child_row_x = child_row.mapTo(group_widget, QtCore.QPoint()).x()
        child_row_right = child_row_x + child_row.width()
        self.assertGreater(child_row_x, 0)
        self.assertEqual(group_widget.width() - child_row_right, 4)
        self.assertLessEqual(
            abs(
                child_host._rizum_label.mapTo(
                    group_widget, QtCore.QPoint()
                ).x()
                - parent_label.mapTo(group_widget, QtCore.QPoint()).x()
            ),
            1,
        )

        parent_center_x = group["parent"].mapTo(
            group_widget, group["parent"].rect().center()
        ).x()
        for checkbox in group["children"]:
            child_center_x = checkbox.mapTo(
                group_widget, checkbox.rect().center()
            ).x()
            self.assertLessEqual(abs(child_center_x - parent_center_x), 1)

    def test_settings_preview_uses_canonical_codex_layout(self):
        settings = build_settings_preview(QtWidgets)
        self.addCleanup(settings.deleteLater)

        self.assertIsInstance(settings, PainterSettingsDialog)
        body = settings._rizum_body_layout
        margins = body.contentsMargins()
        self.assertEqual(margins.left(), PAINTER_SETTINGS_LAYOUT.body_margin_x.design)
        self.assertEqual(margins.top(), PAINTER_SETTINGS_LAYOUT.body_margin_top.design)
        self.assertEqual(
            margins.bottom(), PAINTER_SETTINGS_LAYOUT.body_margin_bottom.design
        )
        self.assertEqual(body.spacing(), PAINTER_SETTINGS_LAYOUT.body_spacing.design)

        footer_row = settings._rizum_footer_row
        footer_margins = footer_row.layout().contentsMargins()
        self.assertEqual(
            footer_margins.left(), PAINTER_SETTINGS_LAYOUT.footer_margin_x.design
        )
        self.assertEqual(
            footer_margins.right(), PAINTER_SETTINGS_LAYOUT.footer_margin_x.design
        )
        self.assertEqual(
            settings._rizum_footer.height(),
            PAINTER_SETTINGS_LAYOUT.footer_top.design
            + PAINTER_SETTINGS_LAYOUT.footer_gap.design
            + PAINTER_SETTINGS_LAYOUT.footer_row_height.design
            + PAINTER_SETTINGS_LAYOUT.footer_bottom.design,
        )


if __name__ == "__main__":
    unittest.main()
