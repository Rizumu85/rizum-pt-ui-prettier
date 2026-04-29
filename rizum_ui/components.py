"""Reusable PySide6 widgets for Rizum Painter plugins."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

COMPACT_DOCK_MIN_WIDTH = 250
COMPACT_DOCK_DEFAULT_WIDTH = COMPACT_DOCK_MIN_WIDTH
COMPACT_DOCK_DEFAULT_HEIGHT = 184
COMPACT_DOCK_OUTER_MARGINS = (4, 0, 4, 2)
COMPACT_DOCK_PANEL_BG = "#2b2b2b"
COMPACT_DOCK_CARD_BG = "#1b1b1b"
COMPACT_DOCK_CARD_RADIUS = 10
FOOTER_BUTTON_HEIGHT = 26
FOOTER_BUTTON_PADDING_X = 8


class Card:
    """Factory for a compact framed surface."""

    @staticmethod
    def create(parent=None):
        from PySide6 import QtWidgets

        frame = QtWidgets.QFrame(parent)
        frame.setObjectName("RizumCard")
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        return frame


class FieldLabel:
    """Factory for compact form labels."""

    @staticmethod
    def create(text, parent=None):
        from PySide6 import QtWidgets

        label = QtWidgets.QLabel(text, parent)
        label.setObjectName("RizumFieldLabel")
        return label


class SectionHeader:
    """A title/subtitle pair for dense plugin panels."""

    def __new__(cls, title, subtitle="", parent=None):
        from PySide6 import QtWidgets

        widget = QtWidgets.QWidget(parent)
        widget.setObjectName("RizumSectionHeader")
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("RizumSectionTitle")
        layout.addWidget(title_label)

        if subtitle:
            subtitle_label = QtWidgets.QLabel(subtitle)
            subtitle_label.setProperty("muted", True)
            subtitle_label.setWordWrap(True)
            layout.addWidget(subtitle_label)

        return widget


class ActionButton:
    """Primary or secondary button factory."""

    @staticmethod
    def create(text, variant="secondary", parent=None):
        from PySide6 import QtWidgets

        button = QtWidgets.QPushButton(text, parent)
        if variant != "secondary":
            button.setProperty("variant", variant)
        button.setMinimumHeight(32)
        return button


class PillButton:
    """Compact rounded button for secondary toolbar actions."""

    @staticmethod
    def create(text, parent=None):
        from PySide6 import QtWidgets

        button = QtWidgets.QPushButton(text, parent)
        button.setProperty("variant", "ghost")
        button.setMinimumSize(32, 32)
        return button


class StatusPill:
    """Small colored status label."""

    def __new__(cls, text, tone="neutral", parent=None):
        from PySide6 import QtWidgets

        label = QtWidgets.QLabel(text, parent)
        label.setObjectName("RizumStatusPill")
        colors = {
            "good": ("#0d3326", "#37c98b"),
            "info": ("#102b52", "#6aa8ff"),
            "warn": ("#3a2912", "#d69a38"),
            "bad": ("#3b171b", "#ff6f7d"),
            "neutral": ("#2a2a2a", "#9e9e9e"),
        }
        bg, fg = colors.get(tone, colors["neutral"])
        label.setStyleSheet(
            f"background: {bg}; color: {fg}; border-radius: 8px; padding: 5px 10px;"
        )
        return label


def make_action_row(*buttons, parent=None):
    """Create a right-aligned action row."""
    from PySide6 import QtWidgets

    widget = QtWidgets.QWidget(parent)
    widget.setObjectName("RizumActionRow")
    layout = QtWidgets.QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    layout.addStretch(1)
    for button in buttons:
        layout.addWidget(button)
    return widget


def build_compact_dock_stylesheet():
    """Return styles learned from live Painter dock panels."""
    return f"""
QWidget#RizumCompactDockSurface {{
    background: {COMPACT_DOCK_PANEL_BG};
}}
QFrame#RizumCompactDockCard,
QFrame#RizumCompactDockCard QWidget#RizumTransparent {{
    background: {COMPACT_DOCK_CARD_BG};
    border: 0;
    border-radius: {COMPACT_DOCK_CARD_RADIUS}px;
}}
QFrame#RizumCompactDockCard QPushButton[compactFooter="true"] {{
    min-width: 0;
    padding-left: {FOOTER_BUTTON_PADDING_X}px;
    padding-right: {FOOTER_BUTTON_PADDING_X}px;
}}
"""


def apply_compact_dock_surface(widget):
    """Apply Painter-like dock surface palette and local styles."""
    from PySide6 import QtGui

    widget.setObjectName("RizumCompactDockSurface")
    widget.setStyleSheet(widget.styleSheet() + build_compact_dock_stylesheet())
    palette = widget.palette()
    panel_color = QtGui.QColor(COMPACT_DOCK_PANEL_BG)
    palette.setColor(QtGui.QPalette.ColorRole.Window, panel_color)
    palette.setColor(QtGui.QPalette.ColorRole.Base, panel_color)
    widget.setPalette(palette)
    widget.setAutoFillBackground(True)


def make_compact_dock_layout(widget):
    """Create the outer layout for compact Painter dock content."""
    from PySide6 import QtWidgets

    layout = QtWidgets.QVBoxLayout(widget)
    layout.setContentsMargins(*COMPACT_DOCK_OUTER_MARGINS)
    layout.setSpacing(0)
    return layout


def make_compact_dock_card(parent=None):
    """Create the dark rounded card used inside compact dock panels."""
    from PySide6 import QtWidgets

    card = QtWidgets.QFrame(parent)
    card.setObjectName("RizumCompactDockCard")
    card.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Expanding,
    )
    layout = QtWidgets.QVBoxLayout(card)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    return card


def set_compact_footer_button_width(button, width, height=FOOTER_BUTTON_HEIGHT):
    """Set a footer button's final visual width despite Qt padding math."""
    content_width = max(0, width - (FOOTER_BUTTON_PADDING_X * 2 + 2))
    button.setProperty("compactFooter", True)
    button.setFixedSize(width, height)
    button.setMinimumSize(width, height)
    button.setMaximumSize(width, height)
    button.setStyleSheet(
        f"min-width: {content_width}px; max-width: {content_width}px; "
        f"padding-left: {FOOTER_BUTTON_PADDING_X}px; "
        f"padding-right: {FOOTER_BUTTON_PADDING_X}px;"
    )
    try:
        button.style().unpolish(button)
        button.style().polish(button)
    except Exception:
        pass


def make_inset_separator(inset, thickness=2):
    """Create an inset separator with left/right breathing room."""
    from PySide6 import QtWidgets

    wrapper = QtWidgets.QWidget()
    wrapper.setObjectName("RizumTransparent")
    wrapper.setFixedHeight(thickness)
    wrapper_layout = QtWidgets.QHBoxLayout(wrapper)
    wrapper_layout.setContentsMargins(inset, 0, inset, 0)
    wrapper_layout.setSpacing(0)
    line = QtWidgets.QFrame()
    line.setObjectName("RizumInsetSeparator")
    line.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
    line.setFixedHeight(thickness)
    line.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Fixed,
    )
    wrapper_layout.addWidget(line)
    return wrapper


def make_icon_button(icon_name, tooltip="", size=14, compact=True):
    """Create a themed icon button from the shared icons folder."""
    from PySide6 import QtCore, QtGui

    button = ActionButton.create("", "icon")
    if compact:
        button.setProperty("compact", True)
    icon_path = ROOT / "icons" / icon_name
    button.setIcon(QtGui.QIcon(str(icon_path)))
    button.setIconSize(QtCore.QSize(size, size))
    if tooltip:
        button.setToolTip(tooltip)
    return button


def make_svg_label(icon_name, size):
    """Create a passive SVG label that does not take its own hover state."""
    from PySide6 import QtCore, QtGui, QtWidgets

    label = QtWidgets.QLabel()
    label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    label.setPixmap(QtGui.QIcon(str(ROOT / "icons" / icon_name)).pixmap(QtCore.QSize(size, size)))
    label.setFixedSize(size, size)
    return label


def make_spin_input(value=1.0, minimum=0.75, maximum=2.0, step=0.05, decimals=2):
    """Create a functional compact spin input with Painter-style arrows."""
    from PySide6 import QtCore, QtWidgets

    class _SpinInput(QtWidgets.QFrame):
        valueChanged = QtCore.Signal(float)

        def __init__(self):
            super().__init__()
            self.setObjectName("RizumMockInput")
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
            self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            self.setFixedHeight(32)
            self._minimum = minimum
            self._maximum = maximum
            self._step = step
            self._decimals = decimals
            self._value = minimum

            layout = QtWidgets.QHBoxLayout(self)
            layout.setContentsMargins(8, 6, 8, 6)
            layout.setSpacing(4)
            self._label = QtWidgets.QLabel()
            self._label.setObjectName("RizumMockText")
            self._label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self._label.setMinimumWidth(0)
            self._label.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Preferred,
            )
            layout.addWidget(self._label, 1)
            layout.addWidget(CompactSpinArrows(self._step_by))

            self.setValue(value)
            self.setMinimumWidth(self.sizeHint().width())

        def value(self):
            return self._value

        def setValue(self, value):
            next_value = max(self._minimum, min(self._maximum, float(value)))
            if round(next_value, self._decimals) == round(self._value, self._decimals):
                self._value = next_value
                self._label.setText(f"{self._value:.{self._decimals}f}")
                return
            self._value = next_value
            self._label.setText(f"{self._value:.{self._decimals}f}")
            self.valueChanged.emit(self._value)

        def setRange(self, minimum, maximum):
            self._minimum = float(minimum)
            self._maximum = float(maximum)
            self.setValue(self._value)

        def setSingleStep(self, step):
            self._step = float(step)

        def setDecimals(self, decimals):
            self._decimals = int(decimals)
            self._label.setText(f"{self._value:.{self._decimals}f}")

        def wheelEvent(self, event):
            direction = 1 if event.angleDelta().y() > 0 else -1
            self._step_by(self._step * direction)

        def _step_by(self, delta):
            self.setValue(self._value + delta)

    return _SpinInput()


def make_combo_input(options=None):
    """Create a functional compact combo input backed by a lightweight menu."""
    from PySide6 import QtCore, QtWidgets

    class _ComboInput(QtWidgets.QFrame):
        currentIndexChanged = QtCore.Signal(int)

        def __init__(self):
            super().__init__()
            self.setObjectName("RizumMockInput")
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
            self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            self.setFixedHeight(32)
            self._items = []
            self._current_index = -1

            layout = QtWidgets.QHBoxLayout(self)
            layout.setContentsMargins(8, 6, 8, 6)
            layout.setSpacing(4)
            self._label = QtWidgets.QLabel()
            self._label.setObjectName("RizumMockText")
            self._label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self._label.setMinimumWidth(0)
            self._label.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Preferred,
            )
            layout.addWidget(self._label, 1)
            layout.addWidget(CompactChevronDown())

            for item in options or []:
                if isinstance(item, tuple):
                    self.addItem(item[0], item[1])
                else:
                    self.addItem(item, item)
            self.setMinimumWidth(self.sizeHint().width())

        def clear(self):
            self._items = []
            self._current_index = -1
            self._label.setText("")

        def addItem(self, text, userData=None):
            self._items.append((text, userData))
            if self._current_index < 0:
                self.setCurrentIndex(0)

        def findData(self, data):
            for index, item in enumerate(self._items):
                if item[1] == data:
                    return index
            return -1

        def setCurrentIndex(self, index):
            if index < 0 or index >= len(self._items):
                return
            changed = index != self._current_index
            self._current_index = index
            self._label.setText(self._items[index][0])
            if changed:
                self.currentIndexChanged.emit(index)

        def currentIndex(self):
            return self._current_index

        def currentText(self):
            if self._current_index < 0:
                return ""
            return self._items[self._current_index][0]

        def currentData(self):
            if self._current_index < 0:
                return None
            return self._items[self._current_index][1]

        def mousePressEvent(self, event):
            if event.button() != QtCore.Qt.MouseButton.LeftButton:
                return
            if not self._items:
                return
            menu = QtWidgets.QMenu(self)
            menu.setObjectName("RizumPopupMenu")
            for index, item in enumerate(self._items):
                action = menu.addAction(item[0])
                action.triggered.connect(lambda checked=False, i=index: self.setCurrentIndex(i))
            menu.exec(self.mapToGlobal(QtCore.QPoint(0, self.height() + 4)))

    return _ComboInput()


def make_mock_input(text, mode):
    """Create a Painter-style mock spin/combo input used by compact panels."""
    if mode == "spin":
        return make_spin_input(float(text))
    if mode == "combo":
        options = ["System Default", "MiSans", "Inter", "Segoe UI", "Arial"]
        return make_combo_input(options)
    raise ValueError(f"Unsupported mock input mode: {mode}")


class CompactSpinArrows:
    """Small painted up/down chevrons that never overflow their bounds."""

    def __new__(cls, on_step=None):
        from PySide6 import QtCore, QtGui, QtWidgets

        class _SpinArrows(QtWidgets.QWidget):
            def __init__(self):
                super().__init__()
                self.setObjectName("RizumSpinArrows")
                self.setFixedSize(10, 14)
                self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                self._active = None
                self._hover = None
                self.setMouseTracking(True)

            def paintEvent(self, event):
                painter = QtGui.QPainter(self)
                painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
                self._draw_chevron(painter, "up")
                self._draw_chevron(painter, "down")

            def mousePressEvent(self, event):
                if event.button() != QtCore.Qt.MouseButton.LeftButton:
                    return
                self._active = self._hit_direction(event.position().y())
                if on_step is not None:
                    on_step(0.05 if self._active == "up" else -0.05)
                self.update()

            def mouseReleaseEvent(self, event):
                self._active = None
                self._hover = self._hit_direction(event.position().y())
                self.update()

            def mouseMoveEvent(self, event):
                self._hover = self._hit_direction(event.position().y())
                self.update()

            def leaveEvent(self, event):
                self._active = None
                self._hover = None
                self.update()

            def _hit_direction(self, y):
                return "up" if y < self.height() / 2 else "down"

            def _draw_chevron(self, painter, direction):
                if self._active == direction:
                    color = "#e0e0e0"
                elif self._hover == direction:
                    color = "#9e9e9e"
                else:
                    color = "#666666"
                pen = QtGui.QPen(QtGui.QColor(color))
                pen.setWidthF(1.4)
                pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                if direction == "up":
                    points = [
                        QtCore.QPointF(2.5, 5.0),
                        QtCore.QPointF(5.0, 2.5),
                        QtCore.QPointF(7.5, 5.0),
                    ]
                else:
                    points = [
                        QtCore.QPointF(2.5, 9.0),
                        QtCore.QPointF(5.0, 11.5),
                        QtCore.QPointF(7.5, 9.0),
                    ]
                painter.drawPolyline(points)

        return _SpinArrows()


class CompactChevronDown:
    """Small painted down chevron without a child hover surface."""

    def __new__(cls):
        from PySide6 import QtCore, QtGui, QtWidgets

        class _ChevronDown(QtWidgets.QWidget):
            def __init__(self):
                super().__init__()
                self.setObjectName("RizumMockIcon")
                self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
                self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground, True)
                self.setFixedSize(10, 10)

            def paintEvent(self, event):
                painter = QtGui.QPainter(self)
                painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
                pen = QtGui.QPen(QtGui.QColor("#9e9e9e"))
                pen.setWidthF(1.4)
                pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                painter.drawPolyline(
                    [
                        QtCore.QPointF(2.5, 4.0),
                        QtCore.QPointF(5.0, 6.5),
                        QtCore.QPointF(7.5, 4.0),
                    ]
                )

        return _ChevronDown()


def make_mock_checkbox():
    """Create the filled/outline checkbox used by compact Rizum panels."""
    from PySide6 import QtCore, QtGui, QtWidgets

    class _Checkbox(QtWidgets.QWidget):
        def __init__(self):
            super().__init__()
            self.setObjectName("RizumMockCheckbox")
            self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            self.setFixedSize(14, 14)
            self._checked = True
            self.setProperty("checked", True)

        def toggle(self):
            self.set_checked(not self._checked)

        def set_checked(self, checked):
            self._checked = checked
            self.setProperty("checked", checked)
            self.update()

        def isChecked(self):
            return self._checked

        def setChecked(self, checked):
            self.set_checked(bool(checked))

        def mousePressEvent(self, event):
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self.toggle()

        def paintEvent(self, event):
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

            if self._checked:
                painter.setPen(QtCore.Qt.PenStyle.NoPen)
                painter.setBrush(QtGui.QColor("#ffffff"))
                painter.drawRoundedRect(QtCore.QRectF(0, 0, 14, 14), 3, 3)

                pen = QtGui.QPen(QtGui.QColor("#1b1b1b"))
                pen.setWidthF(1.6)
                pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                painter.drawPolyline(
                    [
                        QtCore.QPointF(4.0, 7.2),
                        QtCore.QPointF(6.0, 9.2),
                        QtCore.QPointF(10.0, 4.8),
                    ]
                )
            else:
                rect = QtCore.QRectF(0.75, 0.75, 12.5, 12.5)
                pen = QtGui.QPen(QtGui.QColor("#ffffff"))
                pen.setWidthF(1.5)
                pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
                painter.setPen(pen)
                painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(rect, 3, 3)

    return _Checkbox()


def make_field_row(label_text, control, label_width=50, gap=18, width=None):
    """Create a compact label/control row with Painter-style spacing."""
    from PySide6 import QtCore, QtWidgets

    widget = QtWidgets.QWidget()
    widget.setObjectName("RizumTransparent")
    widget.setFixedHeight(32)
    row = QtWidgets.QHBoxLayout(widget)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(gap)
    label = FieldLabel.create(label_text)
    label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    label.setFixedWidth(label_width)
    row.addWidget(label)
    if width is not None:
        control.setFixedWidth(width)
        row.addWidget(control)
        row.addStretch(1)
    else:
        row.addWidget(control, 1)
    return widget
