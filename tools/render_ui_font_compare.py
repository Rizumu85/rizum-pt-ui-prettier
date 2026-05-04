"""Render UI Font reference and PySide preview snapshots for visual comparison."""

from __future__ import annotations

import sys
import os
from pathlib import Path

os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "0")
os.environ.setdefault("QT_SCALE_FACTOR", "1")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


SCALE = 356 / 260
OUT_DIR = ROOT / "visual-diff"


def px(value):
    return round(value * SCALE)


def render_reference(QtCore, QtGui, QtWidgets):
    panel = QtWidgets.QFrame()
    panel.setObjectName("ReferencePanel")
    panel.setFixedSize(356, round(236 * SCALE))

    layout = QtWidgets.QVBoxLayout(panel)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    header = QtWidgets.QWidget()
    header.setObjectName("Transparent")
    header.setFixedHeight(px(40))
    header_layout = QtWidgets.QHBoxLayout(header)
    header_layout.setContentsMargins(px(16), 0, px(16), 0)
    title = QtWidgets.QLabel("UI Font")
    title.setObjectName("ReferenceTitle")
    header_layout.addWidget(title)
    header_layout.addStretch(1)
    layout.addWidget(header)
    layout.addWidget(separator(QtWidgets, px(12)))

    main = QtWidgets.QWidget()
    main.setObjectName("Transparent")
    main_layout = QtWidgets.QVBoxLayout(main)
    main_layout.setContentsMargins(px(16), px(16), px(16), px(16))
    main_layout.setSpacing(px(12))
    main_layout.addLayout(field_row(QtWidgets, "Size", mock_input(QtWidgets, "1.00", px(70))))
    main_layout.addLayout(field_row(QtWidgets, "Font", mock_input(QtWidgets, "System Default", None, chevron=True)))

    sub = QtWidgets.QHBoxLayout()
    sub.setContentsMargins(px(44), px(-6), px(4), px(2))
    sub.setSpacing(0)
    icon_group = QtWidgets.QHBoxLayout()
    icon_group.setSpacing(px(4))
    icon_group.addWidget(icon_button(QtCore, QtGui, QtWidgets, "folder.svg"))
    icon_group.addWidget(icon_button(QtCore, QtGui, QtWidgets, "refresh.svg"))
    sub.addLayout(icon_group)
    sub.addStretch(1)

    hint = QtWidgets.QWidget()
    hint.setObjectName("ReferenceInlineCheckbox")
    hint_layout = QtWidgets.QHBoxLayout(hint)
    hint_layout.setContentsMargins(px(8), px(4), px(8), px(4))
    hint_layout.setSpacing(px(10))
    hint_label = QtWidgets.QLabel("No hinting")
    hint_label.setObjectName("ReferenceHint")
    hint_layout.addWidget(hint_label)
    check = QtWidgets.QCheckBox()
    check.setChecked(True)
    check.setText("")
    hint_layout.addWidget(check)
    sub.addWidget(hint)
    main_layout.addLayout(sub)

    layout.addWidget(main)
    layout.addStretch(1)
    layout.addWidget(separator(QtWidgets, px(12)))

    footer = QtWidgets.QWidget()
    footer.setObjectName("Transparent")
    footer.setFixedHeight(px(48))
    footer_layout = QtWidgets.QHBoxLayout(footer)
    footer_layout.setContentsMargins(px(16), 0, px(16), 0)
    footer_layout.setSpacing(px(8))
    footer_layout.addStretch(1)
    reset = QtWidgets.QPushButton("Reset")
    reset.setObjectName("ReferenceReset")
    reset.setFixedHeight(px(26))
    apply = QtWidgets.QPushButton("Apply")
    apply.setObjectName("ReferenceApply")
    apply.setFixedHeight(px(26))
    footer_layout.addWidget(reset)
    footer_layout.addWidget(apply)
    layout.addWidget(footer)

    panel.setStyleSheet(reference_stylesheet())
    return panel


def separator(QtWidgets, inset):
    wrapper = QtWidgets.QWidget()
    wrapper.setObjectName("Transparent")
    layout = QtWidgets.QHBoxLayout(wrapper)
    layout.setContentsMargins(inset, 0, inset, 0)
    line = QtWidgets.QFrame()
    line.setObjectName("ReferenceSeparator")
    line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
    line.setFixedHeight(1)
    layout.addWidget(line)
    return wrapper


def field_row(QtWidgets, label_text, control):
    row = QtWidgets.QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(px(12))
    label = QtWidgets.QLabel(label_text)
    label.setObjectName("ReferenceLabel")
    label.setFixedWidth(px(32))
    row.addWidget(label)
    if control.maximumWidth() > 0:
        row.addWidget(control)
        row.addStretch(1)
    else:
        row.addWidget(control, 1)
    return row


def mock_input(QtWidgets, text, width, chevron=False):
    widget = QtWidgets.QFrame()
    widget.setObjectName("ReferenceInput")
    if width is not None:
        widget.setFixedWidth(width)
    layout = QtWidgets.QHBoxLayout(widget)
    layout.setContentsMargins(px(8), px(6), px(8), px(6))
    label = QtWidgets.QLabel(text)
    label.setObjectName("ReferenceInputText")
    layout.addWidget(label)
    layout.addStretch(1)
    if chevron:
        arrow = QtWidgets.QLabel("⌄")
        arrow.setObjectName("ReferenceArrow")
        layout.addWidget(arrow)
    else:
        arrows = QtWidgets.QLabel("⌃\n⌄")
        arrows.setObjectName("ReferenceSpin")
        layout.addWidget(arrows)
    return widget


def icon_button(QtCore, QtGui, QtWidgets, icon_name):
    button = QtWidgets.QPushButton()
    button.setObjectName("ReferenceIconButton")
    button.setIcon(QtGui.QIcon(str(ROOT / "icons" / icon_name)))
    button.setIconSize(QtCore.QSize(px(14), px(14)))
    return button


def reference_stylesheet():
    return f"""
QFrame#ReferencePanel {{
    background: #1b1b1b;
    border: 1px solid #414141;
    border-radius: {px(10)}px;
}}
QWidget#Transparent {{
    background: transparent;
}}
QFrame#ReferenceSeparator {{
    background: #414141;
    border: 0;
}}
QLabel#ReferenceTitle {{
    color: #e0e0e0;
    font-size: {px(13)}px;
    font-weight: 600;
}}
QLabel#ReferenceLabel {{
    color: #9e9e9e;
    font-size: {px(13)}px;
    font-weight: 500;
}}
QFrame#ReferenceInput {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: {px(6)}px;
}}
QLabel#ReferenceInputText {{
    color: #e0e0e0;
    font-size: {px(13)}px;
}}
QLabel#ReferenceArrow, QLabel#ReferenceSpin {{
    color: #9e9e9e;
    font-size: {px(10)}px;
}}
QPushButton#ReferenceIconButton {{
    width: {px(26)}px;
    height: {px(26)}px;
    background: transparent;
    border: 0;
    border-radius: {px(4)}px;
}}
QWidget#ReferenceInlineCheckbox {{
    background: transparent;
    border-radius: {px(6)}px;
}}
QLabel#ReferenceHint {{
    color: #9e9e9e;
    font-size: {px(11)}px;
    font-weight: 500;
}}
QCheckBox::indicator {{
    width: {px(14)}px;
    height: {px(14)}px;
    border: 1px solid #ffffff;
    border-radius: {px(3)}px;
    background: transparent;
}}
QCheckBox::indicator:checked {{
    background: #ffffff;
}}
QPushButton#ReferenceReset, QPushButton#ReferenceApply {{
    min-height: {px(26)}px;
    padding: 0 {px(18)}px;
    border: 0;
    border-radius: {px(13)}px;
    font-size: {px(12)}px;
}}
QPushButton#ReferenceReset {{
    background: #343434;
    color: #ffffff;
    font-weight: 500;
}}
QPushButton#ReferenceApply {{
    background: #ffffff;
    color: #1b1b1b;
    font-weight: 600;
}}
"""


def render_preview(QtWidgets):
    import preview
    from rizum_ui import (
        apply_painter_like_base,
        build_painter_host_preview_stylesheet,
        build_stylesheet,
    )

    app = QtWidgets.QApplication.instance()
    apply_painter_like_base(app)
    app.setStyleSheet(build_painter_host_preview_stylesheet() + build_stylesheet())

    return preview.build_font_preview(QtWidgets)


def save_widget(widget, path):
    from PySide6 import QtCore

    widget.show()
    widget.ensurePolished()
    pixmap = widget.grab()
    image = pixmap.toImage()
    if pixmap.devicePixelRatio() != 1:
        image = image.scaled(
            widget.width(),
            widget.height(),
            QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
    image.save(str(path))


def main():
    from PySide6 import QtCore, QtGui, QtWidgets

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    OUT_DIR.mkdir(exist_ok=True)
    reference = render_reference(QtCore, QtGui, QtWidgets)
    preview_widget = render_preview(QtWidgets)
    save_widget(reference, OUT_DIR / "ui-font-reference.png")
    save_widget(preview_widget, OUT_DIR / "ui-font-preview.png")
    print(OUT_DIR / "ui-font-reference.png")
    print(OUT_DIR / "ui-font-preview.png")
    app.quit()


if __name__ == "__main__":
    main()
