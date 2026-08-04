"""Standalone concept preview for a compact View Roll settings panel.

Fresh alternative design built on the shared Rizum UI kit: the Painter
settings dialog surface, segmented control, compact steppers, and footer
buttons. The shortcut capture field is concept-local; if the concept ships
it can graduate into ``rizum_ui`` with the same sizing contract it already
follows here (``setCompactHeight`` with a 0.75x floor, no closure sizes).
"""

from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from rizum_ui import (
    FOOTER_BUTTON_PADDING_X,
    PAINTER_FOOTER_MARGIN_BOTTOM,
    PAINTER_FOOTER_MARGIN_X,
    PAINTER_SETTINGS_FRAME_COLOR,
    ActionButton,
    PainterSettingsDialog,
    install_compact_tooltip,
    make_compact_stepper,
    make_inset_separator,
    make_painter_title_bar,
    make_painter_window_content,
    make_segmented_control,
    set_compact_footer_button_width,
)
from rizum_ui.theme import default_theme


ROTATION_MODES = [
    ("Continuous", "continuous"),
    ("15°", "step_15"),
    ("Custom", "custom"),
]

SHORTCUT_ACTIONS = [
    ("roll_left", "Roll 3D Left"),
    ("roll_right", "Roll 3D Right"),
    ("roll_reset", "Reset 3D Roll"),
]

DEFAULTS = {
    "mode": "step_15",
    "angle": 45,
    "speed": 90,
    "shortcuts": {
        "roll_left": "Alt+Left",
        "roll_right": "Alt+Right",
        "roll_reset": "Alt+0",
    },
}

DESIGN_VARIANTS = {
    "original": {
        "label": "Original",
        "surface": default_theme.surface,
    },
    "codex": {
        "label": "Codex",
        "surface": "#202123",
        "control": "#303236",
        "control_hover": "#383a3e",
        "text": "#f0f0f0",
        "muted": "#a8acb2",
        "faint": "#858a90",
        "accent": "#f2f2f2",
        "accent_text": "#202123",
    },
    "kimi": {
        "label": "Kimi K3",
        "surface": "#26282c",
        "control": "#33363b",
        "control_hover": "#3d4046",
        "border": "#494d54",
        "text": "#e6e8ea",
        "muted": "#9ba0a6",
        "faint": "#7e838a",
        "accent": "#3a3e44",
        "accent_text": "#f2f2f2",
        "field_radius": 4,
    },
}

_VIEW_ROLL_TEXT = {
    "zh_CN": {
        "title": "视图旋转设置",
        "rotation": "旋转",
        "mode": "模式",
        "continuous": "无极",
        "custom": "自定义",
        "speed": "速度",
        "angle": "角度",
        "shortcuts": "快捷键",
        "roll_left": "3D 视图左转",
        "roll_right": "3D 视图右转",
        "roll_reset": "重置 3D 旋转",
        "restore": "恢复默认",
        "cancel": "取消",
        "save": "保存",
        "shortcut_tip": "点击后录入新快捷键。Esc 取消，Delete 清除。",
    },
    "ja_JP": {
        "title": "ビュー回転設定",
        "rotation": "回転",
        "mode": "モード",
        "continuous": "連続",
        "custom": "カスタム",
        "speed": "速度",
        "angle": "角度",
        "shortcuts": "ショートカット",
        "roll_left": "3Dビューを左に回転",
        "roll_right": "3Dビューを右に回転",
        "roll_reset": "3D回転をリセット",
        "restore": "初期設定に戻す",
        "cancel": "キャンセル",
        "save": "保存",
        "shortcut_tip": "クリックしてショートカットを入力。Escで取消、Deleteで消去。",
    },
}


def _preview_text(key, fallback):
    app = QtWidgets.QApplication.instance()
    language = str(app.property("rizumPreviewLanguage") or "en") if app else "en"
    return _VIEW_ROLL_TEXT.get(language, {}).get(key, fallback)

def _copy_state(state):
    return {
        "mode": state["mode"],
        "angle": state["angle"],
        "speed": state["speed"],
        "shortcuts": dict(state["shortcuts"]),
    }


class TextActionButton(QtWidgets.QAbstractButton):
    """Text-only secondary action with quiet, tactile state feedback."""

    BASE_HEIGHT = 28
    MIN_HEIGHT = 21

    def __init__(self, text, muted, active, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setObjectName("RizumViewRollTextAction")
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self._muted = QtGui.QColor(muted)
        self._active = QtGui.QColor(active)
        self._compact_height = self.BASE_HEIGHT
        self._hover_progress = 0.0
        self._press_progress = 0.0
        self._hover_animation = None
        self._press_animation = None
        self.setCompactHeight(self.BASE_HEIGHT)

    def _scale(self):
        return self._compact_height / float(self.BASE_HEIGHT)

    def _font(self):
        font = QtGui.QFont(self.font())
        font.setPixelSize(max(9, int(round(12 * self._scale()))))
        font.setWeight(QtGui.QFont.Weight.Normal)
        return font

    def sizeHint(self):
        width = QtGui.QFontMetrics(self._font()).horizontalAdvance(self.text()) + 2
        return QtCore.QSize(max(1, width), self._compact_height)

    def setCompactHeight(self, height):
        self._compact_height = max(self.MIN_HEIGHT, int(round(height)))
        hint = self.sizeHint()
        self.setFixedSize(hint.width(), self._compact_height)
        self.updateGeometry()
        self.update()

    def _animate(self, name, target, duration):
        attribute = f"_{name}_animation"
        previous = getattr(self, attribute)
        if previous is not None:
            previous.stop()
        animation = QtCore.QPropertyAnimation(
            self,
            b"hoverProgress" if name == "hover" else b"pressProgress",
            self,
        )
        animation.setDuration(duration)
        animation.setStartValue(
            self._hover_progress if name == "hover" else self._press_progress
        )
        animation.setEndValue(float(target))
        animation.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
        setattr(self, attribute, animation)
        animation.start()

    def getHoverProgress(self):
        return self._hover_progress

    def setHoverProgress(self, value):
        self._hover_progress = max(0.0, min(1.0, float(value)))
        self.update()

    hoverProgress = QtCore.Property(float, getHoverProgress, setHoverProgress)

    def getPressProgress(self):
        return self._press_progress

    def setPressProgress(self, value):
        self._press_progress = max(0.0, min(1.0, float(value)))
        self.update()

    pressProgress = QtCore.Property(float, getPressProgress, setPressProgress)

    def enterEvent(self, event):
        self._animate("hover", 1.0, 120)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate("hover", 0.0, 140)
        self._animate("press", 0.0, 100)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._animate("press", 1.0, 70)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._animate("press", 0.0, 120)
        super().mouseReleaseEvent(event)

    def focusInEvent(self, event):
        self._animate("hover", 1.0, 120)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        if not self.underMouse():
            self._animate("hover", 0.0, 140)
        self._animate("press", 0.0, 100)
        super().focusOutEvent(event)

    def paintEvent(self, event):
        del event
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing, True)
        color = QtGui.QColor(
            round(
                self._muted.red()
                + (self._active.red() - self._muted.red()) * self._hover_progress
            ),
            round(
                self._muted.green()
                + (self._active.green() - self._muted.green())
                * self._hover_progress
            ),
            round(
                self._muted.blue()
                + (self._active.blue() - self._muted.blue())
                * self._hover_progress
            ),
        )
        if self._press_progress:
            color.setAlphaF(max(0.62, 1.0 - 0.28 * self._press_progress))
        painter.setFont(self._font())
        painter.setPen(color)
        y_offset = round(self._press_progress * max(1.0, self._scale()))
        painter.drawText(
            self.rect().translated(0, y_offset),
            QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter,
            self.text(),
        )
        painter.end()


class ShortcutCaptureField(QtWidgets.QFrame):
    """Painted shortcut field with capture, clear, and conflict states."""

    shortcutChanged = QtCore.Signal(str)
    captureStateChanged = QtCore.Signal(bool)

    BASE_HEIGHT = 30
    MIN_HEIGHT = 23  # BASE_HEIGHT x 0.75, per the font-scale contract

    def __init__(self, action_name, parent=None, visual_style=None):
        super().__init__(parent)
        self.setObjectName("RizumShortcutCapture")
        self._action_name = action_name
        self._visual_style = dict(visual_style or {})
        self._shortcut = ""
        self._capturing = False
        self._conflicted = False
        self._pending_modifiers = ""
        self._compact_height = self.BASE_HEIGHT
        self._hovered = False
        self._hover_clear = False
        self._pressed_clear = False
        self.setFixedHeight(self.BASE_HEIGHT)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_Hover, True)
        self.refreshMetrics()

    def actionName(self):
        return self._action_name

    def shortcut(self):
        return self._shortcut

    def setShortcut(self, text, emit=True):
        text = str(text or "").strip()
        if text == self._shortcut:
            self.update()
            return
        self._shortcut = text
        self.refreshMetrics()
        self.update()
        if emit:
            self.shortcutChanged.emit(self._shortcut)

    def isCapturing(self):
        return self._capturing

    def setConflicted(self, conflicted):
        conflicted = bool(conflicted)
        if conflicted == self._conflicted:
            return
        self._conflicted = conflicted
        self.update()

    def setCompactHeight(self, height):
        """Scale the frame and every painted metric from the 30px baseline."""
        self._compact_height = max(self.MIN_HEIGHT, int(round(height)))
        self.setFixedHeight(self._compact_height)
        self.refreshMetrics()
        self.update()

    def refreshMetrics(self):
        # Fixed (not minimum) width: the row layout can never squeeze the
        # field below the width its placeholder/clear slot were measured for.
        self.setFixedWidth(self.sizeHint().width())
        self.updateGeometry()

    def _scale(self):
        return self._compact_height / float(self.BASE_HEIGHT)

    def _scaled(self, value):
        return max(int(round(value * 0.75)), int(round(value * self._scale())))

    def _font(self):
        font = QtGui.QFont(self.font())
        font.setPixelSize(self._scaled(12))
        font.setWeight(QtGui.QFont.Weight.Medium)
        return font

    def _display_text(self):
        if self._capturing:
            return self._pending_modifiers or "Type shortcut…"
        return self._shortcut or "Not set"

    def _clear_slot_width(self):
        return self._scaled(22) if self._shortcut and not self._capturing else 0

    def _reserved_clear_slot_width(self):
        return self._scaled(22) if self._shortcut else 0

    def _clear_rect(self):
        slot = self._clear_slot_width()
        if not slot:
            return QtCore.QRectF()
        return QtCore.QRectF(self.width() - slot, 0, slot, self.height())

    def sizeHint(self):
        metrics = QtGui.QFontMetrics(self._font())
        candidates = [self._display_text(), "Type shortcut…", "Not set"]
        if self._shortcut:
            candidates.append(self._shortcut)
        text_width = max(metrics.horizontalAdvance(text) for text in candidates)
        width = (
            self._scaled(10)
            + text_width
            + self._reserved_clear_slot_width()
            + self._scaled(8)
        )
        return QtCore.QSize(max(self._scaled(64), width), self._compact_height)

    def minimumSizeHint(self):
        return self.sizeHint()

    def startCapture(self):
        if self._capturing:
            return
        self._capturing = True
        self._pending_modifiers = ""
        self.setFocus(QtCore.Qt.FocusReason.MouseFocusReason)
        self.refreshMetrics()
        self.update()
        self.captureStateChanged.emit(True)

    def cancelCapture(self):
        if not self._capturing:
            return
        self._capturing = False
        self._pending_modifiers = ""
        self.refreshMetrics()
        self.update()
        self.captureStateChanged.emit(False)

    def _finish_capture(self, text):
        self._capturing = False
        self._pending_modifiers = ""
        self.setShortcut(text)
        self.captureStateChanged.emit(False)

    def keyPressEvent(self, event):
        if self._capturing:
            key = event.key()
            if key == QtCore.Qt.Key.Key_Escape:
                self.cancelCapture()
                event.accept()
                return
            if key in (QtCore.Qt.Key.Key_Backspace, QtCore.Qt.Key.Key_Delete):
                self._finish_capture("")
                event.accept()
                return
            if key in (
                QtCore.Qt.Key.Key_Control,
                QtCore.Qt.Key.Key_Shift,
                QtCore.Qt.Key.Key_Alt,
                QtCore.Qt.Key.Key_Meta,
                QtCore.Qt.Key.Key_unknown,
            ):
                parts = []
                modifiers = event.modifiers()
                if modifiers & QtCore.Qt.KeyboardModifier.ControlModifier:
                    parts.append("Ctrl")
                if modifiers & QtCore.Qt.KeyboardModifier.AltModifier:
                    parts.append("Alt")
                if modifiers & QtCore.Qt.KeyboardModifier.ShiftModifier:
                    parts.append("Shift")
                if modifiers & QtCore.Qt.KeyboardModifier.MetaModifier:
                    parts.append("Meta")
                self._pending_modifiers = "+".join(parts) + ("+" if parts else "")
                self.update()
                event.accept()
                return
            if key in (QtCore.Qt.Key.Key_Tab, QtCore.Qt.Key.Key_Backtab):
                self.cancelCapture()
                event.ignore()
                return
            sequence = QtGui.QKeySequence(int(event.modifiers()) | key)
            text = sequence.toString(QtGui.QKeySequence.SequenceFormat.PortableText)
            if text:
                self._finish_capture(text)
                event.accept()
                return
            event.accept()
            return
        if event.key() in (
            QtCore.Qt.Key.Key_Return,
            QtCore.Qt.Key.Key_Enter,
            QtCore.Qt.Key.Key_Space,
        ):
            self.startCapture()
            event.accept()
            return
        if event.key() in (QtCore.Qt.Key.Key_Backspace, QtCore.Qt.Key.Key_Delete):
            if self._shortcut:
                self.setShortcut("")
            event.accept()
            return
        super().keyPressEvent(event)

    def focusOutEvent(self, event):
        self.cancelCapture()
        super().focusOutEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if self._clear_rect().contains(event.position()):
                self._pressed_clear = True
            else:
                self.startCapture()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            was_clear = self._pressed_clear
            self._pressed_clear = False
            if was_clear and self._clear_rect().contains(event.position()):
                self.setShortcut("")
            self.update()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        hover_clear = self._clear_rect().contains(event.position())
        if hover_clear != self._hover_clear:
            self._hover_clear = hover_clear
            self.update()
        super().mouseMoveEvent(event)

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._hover_clear = False
        self._pressed_clear = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing, True)

        theme = default_theme
        radius = float(self._scaled(self._visual_style.get("field_radius", 6)))
        rect = QtCore.QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)

        background = QtGui.QColor(
            self._visual_style.get("control", theme.surface_control)
        )
        if self._hovered or self._capturing:
            hover = self._visual_style.get("control_hover")
            background = QtGui.QColor(hover) if hover else background.lighter(112)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(background)
        painter.drawRoundedRect(rect, radius, radius)

        border_color = None
        if self._capturing:
            border_color = QtGui.QColor(theme.accent)
        elif self._conflicted:
            border_color = QtGui.QColor(theme.warning)
        elif self.hasFocus():
            border_color = QtGui.QColor(theme.border)
        elif self._visual_style.get("border"):
            border_color = QtGui.QColor(self._visual_style["border"])
        if border_color is not None:
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.setPen(QtGui.QPen(border_color, 1))
            painter.drawRoundedRect(rect, radius, radius)

        text = self._display_text()
        if self._conflicted and not self._capturing:
            text_color = QtGui.QColor(theme.warning)
        elif self._capturing:
            text_color = QtGui.QColor(
                self._visual_style.get("muted", theme.text_muted)
            )
        elif self._shortcut:
            text_color = QtGui.QColor(self._visual_style.get("text", theme.text))
        else:
            text_color = QtGui.QColor(
                self._visual_style.get("faint", theme.text_faint)
            )
        font = self._font()
        painter.setFont(font)
        painter.setPen(text_color)
        metrics = QtGui.QFontMetricsF(font)
        # Elide as a safety net; refreshMetrics sizes the field so this
        # should never actually trigger.
        available = (
            rect.width()
            - self._scaled(10)
            - self._clear_slot_width()
            - self._scaled(8)
        )
        text = metrics.elidedText(
            text, QtCore.Qt.TextElideMode.ElideRight, int(available)
        )
        baseline = rect.center().y() + (metrics.ascent() - metrics.descent()) / 2
        painter.drawText(QtCore.QPointF(self._scaled(10), baseline), text)

        clear_rect = self._clear_rect()
        if not clear_rect.isEmpty():
            glyph_color = (
                QtGui.QColor(self._visual_style.get("text", theme.text))
                if self._hover_clear
                else QtGui.QColor(
                    self._visual_style.get("faint", theme.text_faint)
                )
            )
            scale = self._scale()
            pen = QtGui.QPen(glyph_color, max(1.2, 1.4 * scale))
            pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            half = 3.2 * scale
            center = clear_rect.center()
            painter.drawLine(
                QtCore.QPointF(center.x() - half, center.y() - half),
                QtCore.QPointF(center.x() + half, center.y() + half),
            )
            painter.drawLine(
                QtCore.QPointF(center.x() - half, center.y() + half),
                QtCore.QPointF(center.x() + half, center.y() - half),
            )
        painter.end()


class _RevealRow(QtWidgets.QFrame):
    """Height-animated collapsible row, mirroring the settings preview."""

    def __init__(
        self,
        content,
        expanded_height,
        parent=None,
        fade_content=False,
        duration=320,
    ):
        super().__init__(parent)
        self.setObjectName("RizumViewRollReveal")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self._expanded_height = int(expanded_height)
        self._duration = int(duration)
        self._progress = 1.0
        self._expanded = True
        self._animation = None
        self._geometry_callback = None
        self._fade_effect = None
        if fade_content:
            self._fade_effect = QtWidgets.QGraphicsOpacityEffect(content)
            content.setGraphicsEffect(self._fade_effect)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(content)
        self.setFixedHeight(self._expanded_height)

    def progress(self):
        return self._progress

    def expandedHeight(self):
        return self._expanded_height

    def setExpandedHeight(self, height):
        self._expanded_height = max(0, int(round(height)))
        self._sync_geometry()

    def setGeometryCallback(self, callback):
        self._geometry_callback = callback

    def _sync_geometry(self):
        progress = max(0.0, min(1.0, self._progress))
        self.setFixedHeight(round(self._expanded_height * progress))
        if self._fade_effect is not None:
            # Keep clipped text quiet until enough row height exists to read
            # it. This also turns Continuous <-> Custom into a soft crossfade
            # instead of two labels visibly shearing through one another.
            fade = max(0.0, min(1.0, (progress - 0.12) / 0.88))
            self._fade_effect.setOpacity(fade * fade * (3.0 - 2.0 * fade))
        if self._geometry_callback is not None:
            self._geometry_callback(progress)

    def getRevealProgress(self):
        return self._progress

    def setRevealProgress(self, value):
        self._progress = float(value)
        self._sync_geometry()

    revealProgress = QtCore.Property(float, getRevealProgress, setRevealProgress)

    def setExpanded(self, expanded, animate=True):
        expanded = bool(expanded)
        self._expanded = expanded
        target = 1.0 if expanded else 0.0
        if self._animation is not None:
            self._animation.stop()
        if not animate or abs(self._progress - target) < 0.001:
            self.setRevealProgress(target)
            self.setAttribute(
                QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, not expanded
            )
            return
        self.setAttribute(
            QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, not expanded
        )
        animation = QtCore.QPropertyAnimation(self, b"revealProgress", self)
        animation.setDuration(
            max(100, round(self._duration * abs(target - self._progress)))
        )
        animation.setStartValue(self._progress)
        animation.setEndValue(target)
        animation.setEasingCurve(
            QtCore.QEasingCurve.Type.InOutCubic
            if self._fade_effect is not None
            else QtCore.QEasingCurve.Type.OutQuart
        )
        self._animation = animation
        animation.start()


class ViewRollConceptPanel(QtWidgets.QWidget):
    """Tab content for the View Roll settings concept."""

    def __init__(self, parent=None, design_variant="original"):
        super().__init__(parent)
        self.setObjectName("RizumViewRollPreview")
        if design_variant not in DESIGN_VARIANTS:
            raise ValueError(f"Unknown View Roll design variant: {design_variant}")
        self.design_variant = design_variant
        self._visual_style = DESIGN_VARIANTS[design_variant]
        self.setProperty("designVariant", design_variant)
        self._saved_state = _copy_state(DEFAULTS)
        self._base_height = None
        self._design_dialog_width = None
        self._design_base_height = None
        self._footer_metrics = None
        self._restoring = False
        self._name_labels = []
        self._texts_blocks = []

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(10)

        self.dialog = PainterSettingsDialog(self)
        self.dialog.setWindowFlags(QtCore.Qt.WindowType.Widget)
        surface_layout = self.dialog.settingsSurfaceLayout()

        self.native_title_bar = make_painter_title_bar(
            _preview_text("title", "View Roll Settings")
        )
        surface_layout.addWidget(self.native_title_bar)

        content = make_painter_window_content(self._visual_style["surface"])
        if self.design_variant == "kimi":
            content.setStyleSheet(
                content.styleSheet()
                + """
QFrame#RizumPainterWindowContent {
    border-top-left-radius: 2px;
    border-top-right-radius: 2px;
    border-bottom-left-radius: 2px;
    border-bottom-right-radius: 2px;
}
"""
            )
        content_layout = content.contentLayout()
        surface_layout.addWidget(content, 1)

        body = QtWidgets.QWidget()
        body.setObjectName("RizumViewRollBody")
        self._body_layout = QtWidgets.QVBoxLayout(body)
        self._body_layout.setContentsMargins(12, 8, 12, 16)
        self._body_layout.setSpacing(2)

        self._section_rotation = self._make_section(
            _preview_text("rotation", "Rotation"), first=True
        )
        self._body_layout.addWidget(self._section_rotation)

        localized_modes = [
            (_preview_text("continuous", "Continuous"), "continuous"),
            ("15°", "step_15"),
            (_preview_text("custom", "Custom"), "custom"),
        ]
        self.mode_segment = make_segmented_control(
            localized_modes, current=self._saved_state["mode"]
        )
        if self.design_variant != "original":
            segment_theme = {
                "segment_bg": self._visual_style["control"],
                "segment_slider_bg": self._visual_style["accent"],
                "segment_active_text": self._visual_style["accent_text"],
                "muted": self._visual_style["muted"],
                "hover": self._visual_style["control_hover"],
            }
            if self.design_variant == "kimi":
                segment_theme["segment_slider_border"] = "#565b63"
                self.mode_segment.setCornerRadius(4)
            elif self.design_variant == "codex":
                # The shared medium radius gives both end caps a readable
                # curve at 30px high; the default 7px edge looked clipped.
                self.mode_segment.setCornerRadius(default_theme.radius)
            self.mode_segment.setTheme(segment_theme)
        mode_row, mode_layout = self._make_row()
        mode_layout.addWidget(self._make_name(_preview_text("mode", "Mode")))
        mode_layout.addStretch(1)
        mode_layout.addWidget(self.mode_segment)
        self._body_layout.addWidget(mode_row)

        self.speed_stepper = make_compact_stepper(
            self._saved_state["speed"], minimum=1, maximum=360, step=5, decimals=0
        )
        self._theme_stepper(self.speed_stepper)
        speed_row, speed_layout = self._make_row(tall=True)
        self.speed_texts = self._make_texts(_preview_text("speed", "Speed"), "°/s")
        speed_layout.addWidget(
            self.speed_texts, 0, QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        speed_layout.addStretch(1)
        speed_layout.addWidget(self.speed_stepper)
        self.speed_reveal = _RevealRow(
            speed_row,
            speed_row.height(),
            fade_content=self.design_variant == "codex",
            duration=220 if self.design_variant == "codex" else 320,
        )
        self.speed_reveal.setGeometryCallback(self._sync_dialog_height)
        self._body_layout.addWidget(self.speed_reveal)

        self.angle_stepper = make_compact_stepper(
            self._saved_state["angle"], minimum=1, maximum=180, step=1, decimals=0
        )
        self._theme_stepper(self.angle_stepper)
        angle_row, angle_layout = self._make_row(tall=True)
        self.angle_texts = self._make_texts(_preview_text("angle", "Angle"), "°")
        angle_layout.addWidget(
            self.angle_texts, 0, QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        angle_layout.addStretch(1)
        angle_layout.addWidget(self.angle_stepper)
        self.angle_reveal = _RevealRow(
            angle_row,
            angle_row.height(),
            fade_content=self.design_variant == "codex",
            duration=220 if self.design_variant == "codex" else 320,
        )
        self.angle_reveal.setGeometryCallback(self._sync_dialog_height)
        self._body_layout.addWidget(self.angle_reveal)

        self._section_shortcuts = self._make_section(
            _preview_text("shortcuts", "Shortcuts")
        )
        self._body_layout.addWidget(self._section_shortcuts)

        self.shortcut_fields = {}
        for action_id, action_name in SHORTCUT_ACTIONS:
            action_name = _preview_text(action_id, action_name)
            field = ShortcutCaptureField(
                action_name,
                visual_style=(
                    self._visual_style if self.design_variant != "original" else None
                ),
            )
            field.setShortcut(self._saved_state["shortcuts"][action_id], emit=False)
            install_compact_tooltip(
                field,
                _preview_text(
                    "shortcut_tip",
                    "Click to capture a new shortcut. Esc cancels, Delete clears.",
                ),
            )
            row, row_layout = self._make_row()
            name_label = self._make_name(action_name)
            row_layout.addWidget(name_label)
            row_layout.addStretch(1)
            row_layout.addWidget(field)
            self._body_layout.addWidget(row)
            field._rizum_name_label = name_label
            self.shortcut_fields[action_id] = field
            field.shortcutChanged.connect(self._on_shortcut_changed)
            field.captureStateChanged.connect(
                lambda _capturing: self._refresh_status()
            )

        content_layout.addWidget(body, 1)
        self._footer_separator = None
        if self.design_variant == "codex":
            self._footer_separator = make_inset_separator(20, thickness=1)
            self._footer_separator.setObjectName("RizumViewRollFooterDivider")
            content_layout.addWidget(self._footer_separator)

        footer = QtWidgets.QWidget()
        footer.setObjectName("RizumViewRollFooter")
        self._footer = footer
        footer_outer = QtWidgets.QVBoxLayout(footer)
        footer_outer.setContentsMargins(0, 0, 0, 0)
        footer_outer.setSpacing(0)
        # The status hint lives in a collapsible reveal above the actions: it
        # only claims footer height while there is something worth reporting,
        # so the idle footer is just the compact action row. Height-only
        # animation, same language as the speed/angle reveals.
        status_line = QtWidgets.QWidget()
        status_line.setObjectName("RizumViewRollStatusLine")
        self._status_line = status_line
        self._status_layout = QtWidgets.QHBoxLayout(status_line)
        self._status_layout.setContentsMargins(16, 0, 16, 0)
        self._status_layout.setSpacing(0)
        self._status_text = ""
        self._status_tone = ""
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setObjectName("RizumSettingsFooterHint")
        self.status_label.setAlignment(
            (
                QtCore.Qt.AlignmentFlag.AlignRight
                if self.design_variant == "codex"
                else QtCore.Qt.AlignmentFlag.AlignLeft
            )
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.status_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Ignored,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        self._status_layout.addWidget(self.status_label)
        self.status_reveal = _RevealRow(status_line, 22)
        self.status_reveal.setGeometryCallback(self._on_status_geometry)
        footer_outer.addWidget(self.status_reveal)
        button_row = QtWidgets.QWidget()
        button_row.setObjectName("RizumViewRollFooterRow")
        self._button_row = button_row
        self._button_layout = QtWidgets.QHBoxLayout(button_row)
        self._button_layout.setContentsMargins(16, 0, 16, 0)
        self._button_layout.setSpacing(8)
        if self.design_variant == "codex":
            self.restore_button = TextActionButton(
                _preview_text("restore", "Restore"),
                self._visual_style["muted"],
                self._visual_style["text"],
            )
        else:
            self.restore_button = ActionButton.create(
                _preview_text("restore", "Restore"), "dialog-secondary"
            )
        self.restore_button.setObjectName("RizumViewRollRestore")
        self.cancel_button = ActionButton.create(
            _preview_text("cancel", "Cancel"), "dialog-secondary"
        )
        self.cancel_button.setObjectName("RizumViewRollCancel")
        self.save_button = ActionButton.create(
            _preview_text("save", "Save"), "dialog-primary"
        )
        self.save_button.setObjectName("RizumViewRollSave")
        self._button_layout.addWidget(self.restore_button)
        self._button_layout.addStretch(1)
        self._button_layout.addWidget(self.cancel_button)
        self._button_layout.addWidget(self.save_button)
        footer_outer.addWidget(button_row)
        content_layout.addWidget(footer)

        outer.addWidget(
            self.dialog,
            0,
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter,
        )
        outer.addStretch(1)

        self.mode_segment.currentDataChanged.connect(self._on_mode_changed)
        self.angle_stepper.valueChanged.connect(self._on_value_edited)
        self.speed_stepper.valueChanged.connect(self._on_value_edited)
        self.restore_button.clicked.connect(self.restore_defaults)
        self.cancel_button.clicked.connect(self.cancel_changes)
        self.save_button.clicked.connect(self.save_changes)
        self.dialog.settingsUiScaleChanged.connect(self._on_ui_scale_changed)

        self._apply_mode_reveals(animate=False)
        self._apply_scale()
        self._remeasure_base_height()
        self._refresh_conflicts()
        self._refresh_status()

    # --- widget helpers -------------------------------------------------

    def _theme_stepper(self, stepper):
        if self.design_variant == "original":
            return
        stepper.setTheme(
            {
                "window_bg": self._visual_style["surface"],
                "text": self._visual_style["text"],
                "muted": self._visual_style["muted"],
                "control_hover": self._visual_style["control_hover"],
            }
        )

    def _make_section(self, text, first=False):
        label = QtWidgets.QLabel(text.upper())
        label.setObjectName("RizumSettingsSection")
        label._rizum_first = first
        if self.design_variant == "codex":
            height = 26 if first else 36
        elif self.design_variant == "kimi":
            height = 26 if first else 30
        else:
            height = 28 if first else 40
        label.setFixedHeight(height)
        return label

    def _make_name(self, text):
        # Keep QLabel's minimum size hint. QSizePolicy.Ignored collapses these
        # names to zero when the fixed-width control claims the row.
        label = QtWidgets.QLabel(text)
        label.setObjectName("RizumSettingsItemName")
        # Measured against the stylesheet's base metrics (13px/500), not a
        # per-character guess: len()*7 clipped "Speed" to "Speec" at 1.0x.
        font = QtGui.QFont(self.font())
        font.setPixelSize(13)
        font.setWeight(QtGui.QFont.Weight.Medium)
        width = QtGui.QFontMetrics(font).horizontalAdvance(text) + 8
        label._rizum_base_width = max(32, width)
        label.setFixedWidth(label._rizum_base_width)
        self._name_labels.append(label)
        return label

    def _make_texts(self, name, meta):
        widget = QtWidgets.QWidget()
        widget.setObjectName("RizumViewRollTexts")
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        name_label = self._make_name(name)
        layout.addWidget(name_label)
        meta_label = QtWidgets.QLabel(meta)
        meta_label.setObjectName("RizumSettingsItemMeta")
        layout.addWidget(meta_label)
        widget._rizum_name_label = name_label
        widget._rizum_meta_label = meta_label
        self._texts_blocks.append(widget)
        return widget

    def _make_row(self, tall=False):
        row = QtWidgets.QFrame()
        row.setObjectName("RizumViewRollRow")
        if self.design_variant == "kimi":
            row.setFixedHeight(42 if tall else 36)
        else:
            row.setFixedHeight(46 if tall else 40)
        layout = QtWidgets.QHBoxLayout(row)
        if self.design_variant == "kimi":
            layout.setContentsMargins(0, 4, 0, 4)
        else:
            layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(8)
        return row, layout

    def _metric(self, pixels, minimum=None):
        return self.dialog.settingsMetric(pixels, minimum)

    # --- state ----------------------------------------------------------

    def current_state(self):
        return {
            "mode": self.mode_segment.currentData(),
            "angle": self.angle_stepper.value(),
            "speed": self.speed_stepper.value(),
            "shortcuts": {
                action_id: field.shortcut()
                for action_id, field in self.shortcut_fields.items()
            },
        }

    def is_dirty(self):
        return self.current_state() != self._saved_state

    def _apply_state(self, state, emit=False):
        self._restoring = True
        try:
            self.mode_segment.setCurrentData(state["mode"], animate=False, emit=emit)
            self.angle_stepper.setValue(state["angle"], emit=emit)
            self.speed_stepper.setValue(state["speed"], emit=emit)
            for action_id, field in self.shortcut_fields.items():
                field.cancelCapture()
                field.setShortcut(state["shortcuts"][action_id], emit=emit)
            self._apply_mode_reveals(animate=False)
        finally:
            self._restoring = False
        self._refresh_conflicts()
        self._refresh_status()

    def save_changes(self):
        self._saved_state = self.current_state()
        # No "Saved." filler: the disabled Save button and the collapsing
        # status line already carry the confirmation.
        self._refresh_status()

    def cancel_changes(self):
        self._apply_state(self._saved_state)

    def restore_defaults(self):
        self._apply_state(_copy_state(DEFAULTS))

    # --- interactions ---------------------------------------------------

    def _on_mode_changed(self, _data):
        self._apply_mode_reveals(animate=True)
        if not self._restoring:
            self._refresh_status()

    def _apply_mode_reveals(self, animate):
        mode = self.mode_segment.currentData()
        self.speed_reveal.setExpanded(mode == "continuous", animate=animate)
        self.angle_reveal.setExpanded(mode == "custom", animate=animate)
        if not animate:
            self._remeasure_base_height()

    def _on_value_edited(self, _value):
        if not self._restoring:
            self._refresh_status()

    def _on_shortcut_changed(self, _text):
        if self._restoring:
            return
        self._refresh_conflicts()
        self._refresh_status()

    def _conflicting_actions(self):
        owners = {}
        for action_id, field in self.shortcut_fields.items():
            shortcut = field.shortcut()
            if shortcut:
                owners.setdefault(shortcut.lower(), []).append(action_id)
        conflicted = set()
        for action_ids in owners.values():
            if len(action_ids) > 1:
                conflicted.update(action_ids)
        return conflicted

    def _refresh_conflicts(self):
        conflicted = self._conflicting_actions()
        for action_id, field in self.shortcut_fields.items():
            field.setConflicted(action_id in conflicted)

    def _refresh_status(self):
        capturing = next(
            (field for field in self.shortcut_fields.values() if field.isCapturing()),
            None,
        )
        conflicted = self._conflicting_actions()
        dirty = self.is_dirty()
        self.save_button.setEnabled(dirty)
        if capturing is not None:
            self._status_tone = ""
            self._status_text = (
                f"Editing {capturing.actionName()} — press keys, Esc to cancel."
            )
        elif conflicted:
            names = " and ".join(
                self.shortcut_fields[action_id].actionName()
                for action_id in sorted(conflicted)
            )
            self._status_tone = "warn"
            self._status_text = f"{names} use the same shortcut."
        elif dirty:
            self._status_tone = ""
            self._status_text = "Unsaved changes."
        else:
            self._status_tone = ""
            self._status_text = ""
        self._sync_status_text()
        # Animate only when on screen; setup and tests settle instantly.
        self.status_reveal.setExpanded(
            bool(self._status_text), animate=self.isVisible()
        )

    def _status_font(self):
        font = QtGui.QFont(self.font())
        font.setPixelSize(self._metric(11))
        font.setWeight(
            QtGui.QFont.Weight.Normal
            if self.design_variant == "codex"
            else QtGui.QFont.Weight.Medium
        )
        return font

    def _name_font(self):
        """Matches the surface stylesheet's RizumSettingsItemName rule."""
        font = QtGui.QFont(self.font())
        font.setPixelSize(self._metric(13))
        font.setWeight(QtGui.QFont.Weight.Medium)
        return font

    def _meta_font(self):
        """Matches the surface stylesheet's RizumSettingsItemMeta rule."""
        font = QtGui.QFont(self.font())
        font.setPixelSize(self._metric(11))
        font.setWeight(QtGui.QFont.Weight.Medium)
        return font

    def _sync_status_text(self):
        """Elide the status hint to the width its line actually has."""
        text = self._status_text
        if text:
            frame = self.dialog.settingsFrameWidth()
            margins = self._status_layout.contentsMargins()
            available = (
                self.dialog.width()
                - 2 * frame
                - margins.left()
                - margins.right()
            )
            if available > 0:
                metrics = QtGui.QFontMetrics(self._status_font())
                text = metrics.elidedText(
                    text, QtCore.Qt.TextElideMode.ElideRight, available
                )
        self.status_label.setProperty("tone", self._status_tone)
        self.status_label.setText(text)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    # --- UI font scale ----------------------------------------------------

    def _on_ui_scale_changed(self, scale):
        self._apply_scale()
        self._remeasure_base_height()

    def _apply_scale(self):
        """Scale every row, control, and footer button from the dialog scale."""
        if self.design_variant == "kimi":
            row_base, tall_base = 36, 42
            body_margins = (20, 12, 20, 14)
            row_margins = (0, 4, 0, 4)
            section_heights = (26, 30)
            control_heights = (28, 28, 28)
            footer_values = (20, 8, 8, 32, 16)
        elif self.design_variant == "codex":
            row_base, tall_base = 40, 46
            body_margins = (20, 12, 20, 20)
            row_margins = (0, 5, 0, 5)
            section_heights = (26, 36)
            control_heights = (30, 32, 30)
            footer_values = (20, 8, 6, 32, 16)
        else:
            row_base, tall_base = 40, 46
            body_margins = (12, 8, 12, 16)
            row_margins = (8, 5, 8, 5)
            section_heights = (28, 40)
            control_heights = (30, 32, 30)
            footer_values = (
                PAINTER_FOOTER_MARGIN_X,
                6,
                8,
                36,
                PAINTER_FOOTER_MARGIN_BOTTOM,
            )

        if self.design_variant == "original":
            row_height = self._metric(40, 30)
            tall_height = self._metric(46, 35)
        else:
            row_height = self._metric(row_base, round(row_base * 0.75))
            tall_height = self._metric(tall_base, round(tall_base * 0.75))
        status_height = (
            self._metric(18, 14)
            if self.design_variant == "codex"
            else self._metric(22, 17)
        )
        if self.design_variant == "original":
            footer_margin = self._metric(PAINTER_FOOTER_MARGIN_X, 12)
            footer_top = self._metric(6, 5)
            footer_gap = self._metric(8, 6)
            buttons_height = self._metric(36, 27)
            footer_bottom = self._metric(PAINTER_FOOTER_MARGIN_BOTTOM, 11)
        else:
            footer_margin = self._metric(
                footer_values[0], round(footer_values[0] * 0.75)
            )
            footer_top = self._metric(
                footer_values[1], round(footer_values[1] * 0.75)
            )
            footer_gap = self._metric(
                footer_values[2], round(footer_values[2] * 0.75)
            )
            buttons_height = self._metric(
                footer_values[3], round(footer_values[3] * 0.75)
            )
            footer_bottom = self._metric(
                footer_values[4], round(footer_values[4] * 0.75)
            )

        # The footer breathes like the body does: air around the separator,
        # the status hint, and below the buttons. Horizontal margins stay put.
        # The status row is collapsible, so its slice of the footer height
        # comes from the reveal, not a fixed slot (see _sync_footer_height).
        footer_outer = self._footer.layout()
        footer_outer.setContentsMargins(0, footer_top, 0, footer_bottom)
        footer_outer.setSpacing(footer_gap)
        self._footer_metrics = (footer_top, footer_gap, buttons_height, footer_bottom)
        self.status_reveal.setExpandedHeight(status_height)
        self._sync_footer_height()
        self._status_line.setFixedHeight(status_height)
        self._button_row.setFixedHeight(buttons_height)
        self._status_layout.setContentsMargins(footer_margin, 0, footer_margin, 0)
        self._button_layout.setContentsMargins(footer_margin, 0, footer_margin, 0)
        if self._footer_separator is not None:
            self._footer_separator.layout().setContentsMargins(
                footer_margin, 0, footer_margin, 0
            )
        self._section_rotation.setFixedHeight(
            self._metric(section_heights[0], round(section_heights[0] * 0.75))
        )
        self._section_shortcuts.setFixedHeight(
            self._metric(section_heights[1], round(section_heights[1] * 0.75))
        )
        self._body_layout.setContentsMargins(
            *(
                self._metric(value, round(value * 0.75))
                for value in body_margins
            )
        )
        if self.design_variant != "original":
            for row in self.findChildren(QtWidgets.QFrame, "RizumViewRollRow"):
                row.layout().setContentsMargins(
                    *(
                        self._metric(value, round(value * 0.75))
                        for value in row_margins
                    )
                )
        for label in self._name_labels:
            base_width = label._rizum_base_width
            label.setFixedWidth(
                self._metric(base_width, max(24, int(round(base_width * 0.75))))
            )

        # Tight name+meta stack with line heights from the rendered fonts, so
        # the block centers as one unit against the stepper next to it.
        name_metrics = QtGui.QFontMetrics(self._name_font())
        meta_metrics = QtGui.QFontMetrics(self._meta_font())
        texts_spacing = self._metric(2, 1)
        for block in self._texts_blocks:
            block._rizum_name_label.setFixedHeight(name_metrics.height())
            block._rizum_meta_label.setFixedHeight(meta_metrics.height())
            block.layout().setSpacing(texts_spacing)
            block.setFixedHeight(
                name_metrics.height() + texts_spacing + meta_metrics.height()
            )

        if self.design_variant == "original":
            self.mode_segment.setCompactHeight(self._metric(30, 23))
            self.speed_stepper.setCompactHeight(self._metric(32, 24))
            self.angle_stepper.setCompactHeight(self._metric(32, 24))
        else:
            self.mode_segment.setCompactHeight(
                self._metric(control_heights[0], round(control_heights[0] * 0.75))
            )
            self.speed_stepper.setCompactHeight(
                self._metric(control_heights[1], round(control_heights[1] * 0.75))
            )
            self.angle_stepper.setCompactHeight(
                self._metric(control_heights[1], round(control_heights[1] * 0.75))
            )
        for field in self.shortcut_fields.values():
            if self.design_variant == "original":
                field.setCompactHeight(self._metric(30, 23))
            else:
                field.setCompactHeight(
                    self._metric(
                        control_heights[2], round(control_heights[2] * 0.75)
                    )
                )
            if hasattr(field, "setCompactTooltipScale"):
                field.setCompactTooltipScale(self.dialog.settingsUiScale())

        mode_row = self.mode_segment.parentWidget()
        mode_row.setFixedHeight(row_height)
        for reveal, stepper in (
            (self.speed_reveal, self.speed_stepper),
            (self.angle_reveal, self.angle_stepper),
        ):
            stepper.parentWidget().setFixedHeight(tall_height)
            reveal.setExpandedHeight(tall_height)
        for field in self.shortcut_fields.values():
            field.parentWidget().setFixedHeight(row_height)

        footer_button_base = (
            28 if self.design_variant in ("codex", "kimi") else 26
        )
        footer_button_height = self._metric(
            footer_button_base, round(footer_button_base * 0.75)
        )
        for button, minimum, maximum in (
            (self.restore_button, 56, 112),
            (self.cancel_button, 56, 96),
            (self.save_button, 52, 92),
        ):
            if isinstance(button, TextActionButton):
                button.setCompactHeight(footer_button_height)
                continue
            width = self._footer_button_width(
                button, minimum=minimum, maximum=maximum
            )
            set_compact_footer_button_width(
                button, width, height=footer_button_height
            )

        # Width is measured, not fixed: stay at the compact baseline unless
        # the scaled footer buttons or field rows genuinely need more room.
        self.dialog.setFixedWidth(self._required_dialog_width())
        self._restyle()
        self._sync_status_text()

    def _footer_button_font(self):
        """The font the dialog stylesheet renders footer buttons in.

        Measuring with ``button.font()`` before polish misses the stylesheet
        ``font-size``, which is what truncated the buttons at 1.10x.
        """
        font = QtGui.QFont(self.font())
        font.setPixelSize(self._metric(12))
        font.setWeight(QtGui.QFont.Weight.Normal)
        return font

    def _footer_button_width(self, button, minimum, maximum):
        scale = self.dialog.settingsUiScale()
        text_width = QtGui.QFontMetrics(
            self._footer_button_font()
        ).horizontalAdvance(button.text())
        # +2: set_compact_footer_button_width reserves padding*2 + 2 for chrome.
        width = text_width + 2 * FOOTER_BUTTON_PADDING_X + 2
        if self.design_variant == "codex":
            # The square footer silhouette needs more air than the original
            # pill buttons; distribute this extra width evenly around the text.
            width += self._metric(16, 12)
        return max(
            self._metric(minimum),
            min(int(round(maximum * scale)), width),
        )

    def _required_dialog_width(self):
        scale = self.dialog.settingsUiScale()
        base = self._metric(300, 240)
        footer_margin_base = 20 if self.design_variant != "original" else 16
        footer_margin = self._metric(
            footer_margin_base, round(footer_margin_base * 0.75)
        )
        row_margin = 0 if self.design_variant in ("codex", "kimi") else 8
        row_spacing = 8
        body_margin_base = {
            "original": 12,
            "codex": 20,
            "kimi": 20,
        }[self.design_variant]
        body_margin = self._metric(
            body_margin_base, round(body_margin_base * 0.75)
        )

        button_spacing = self._button_layout.spacing()
        buttons_width = sum(
            button.width()
            for button in (
                self.restore_button,
                self.cancel_button,
                self.save_button,
            )
        )
        footer_need = buttons_width + 2 * button_spacing + 2 * footer_margin

        def control_row_need(control_width):
            # The compact baseline already includes the name column. Grow only
            # when a scaled fixed-size control genuinely exceeds that budget.
            return control_width + row_spacing + 2 * row_margin + 2 * body_margin

        def labeled_row_need(label_width, control_width):
            return label_width + control_row_need(control_width)

        stepper_need = max(
            control_row_need(stepper.width())
            for stepper in (self.speed_stepper, self.angle_stepper)
        )
        shortcut_need = max(
            labeled_row_need(
                field._rizum_name_label.width(),
                field.sizeHint().width(),
            )
            for field in self.shortcut_fields.values()
        )

        content_need = max(footer_need, stepper_need, shortcut_need)
        measured_width = max(
            base,
            content_need + 2 * self.dialog.settingsFrameWidth() + 2,
        )
        if self._design_dialog_width is None:
            normalizer = scale if scale >= 1.0 else 1.0
            self._design_dialog_width = int(round(measured_width / normalizer))
        proportional_width = int(round(self._design_dialog_width * scale))
        return max(measured_width, proportional_width)

    def _restyle(self):
        theme = default_theme
        hint_px = self._metric(11)
        text = self._visual_style.get("text", theme.text)
        muted = self._visual_style.get("muted", theme.text_muted)
        faint = self._visual_style.get("faint", theme.text_faint)
        control = self._visual_style.get("control", theme.surface_control)
        control_hover = self._visual_style.get("control_hover", "#3b3b3b")
        accent = self._visual_style.get("accent", theme.accent)
        accent_text = self._visual_style.get("accent_text", theme.accent_text)
        if self.design_variant == "kimi":
            button_radius = 4
        elif self.design_variant == "codex":
            button_radius = theme.radius_small
        else:
            button_radius = 13
        variant_rules = ""
        if self.design_variant != "original":
            variant_rules = f"""
QLabel#RizumSettingsSection {{
    color: {faint};
}}
QLabel#RizumSettingsItemName {{
    color: {text};
}}
QLabel#RizumSettingsItemMeta {{
    color: {muted};
}}
QPushButton#RizumViewRollRestore,
QPushButton#RizumViewRollCancel {{
    color: {text};
    background: {control};
    border-radius: {button_radius}px;
}}
QPushButton#RizumViewRollRestore:hover,
QPushButton#RizumViewRollCancel:hover {{
    background: {control_hover};
}}
QPushButton#RizumViewRollSave {{
    color: {accent_text};
    background: {accent};
    border-radius: {button_radius}px;
}}
"""
        # Rebuild the dialog's base stylesheet first so repeated restyles
        # never stack duplicate concept rules on top of each other.
        self.dialog._update_surface_stylesheet()
        surface = self.dialog.settingsSurface()
        surface.setStyleSheet(
            surface.styleSheet()
            + f"""
QFrame#RizumPainterSettingsSurface {{
    background: {PAINTER_SETTINGS_FRAME_COLOR};
}}
QWidget#RizumViewRollBody,
QWidget#RizumViewRollFooter,
QWidget#RizumViewRollStatusLine,
QWidget#RizumViewRollFooterRow,
QWidget#RizumViewRollTexts,
QWidget#RizumViewRollFooterDivider,
QFrame#RizumViewRollReveal {{
    background: transparent;
    border: 0;
}}
QFrame#RizumViewRollRow {{
    background: transparent;
    border: 0;
    border-radius: 6px;
}}
QWidget#RizumViewRollFooterDivider QFrame#RizumInsetSeparator {{
    background: #3a3b3e;
}}
{variant_rules}
QLabel#RizumSettingsFooterHint[tone="warn"] {{
    color: {theme.warning};
}}
QLabel#RizumViewRollScaleHint {{
    color: {theme.text_faint};
    font-size: {hint_px}px;
    background: transparent;
    border: 0;
}}
"""
        )
        if self.design_variant in ("codex", "kimi"):
            restore_color = (
                "#8f949b"
                if self.design_variant == "kimi"
                else self._visual_style["muted"]
            )
            surface.setStyleSheet(
                surface.styleSheet()
                + f"""
QPushButton#RizumViewRollRestore {{
    color: {restore_color};
    background: transparent;
    border: 0;
}}
QPushButton#RizumViewRollRestore:hover {{
    color: {text};
    background: {control_hover};
}}
"""
            )
        if self.design_variant == "codex":
            surface.setStyleSheet(
                surface.styleSheet()
                + f"""
QLabel#RizumSettingsFooterHint {{
    color: {faint};
    font-weight: 400;
}}
"""
            )
        if self.design_variant == "kimi":
            surface.setStyleSheet(
                surface.styleSheet()
                + """
QPushButton#RizumViewRollCancel {
    background: transparent;
    border: 1px solid #4a4e55;
}
"""
            )

    # --- geometry ---------------------------------------------------------

    def _current_extra_height(self):
        extra = 0
        for reveal in (self.speed_reveal, self.angle_reveal, self.status_reveal):
            extra += round(reveal.expandedHeight() * reveal.progress())
        return extra

    def _on_status_geometry(self, _progress):
        self._sync_footer_height()
        self._sync_dialog_height()

    def _sync_footer_height(self):
        """Footer fixed height tracks the status reveal's animated height.

        The top margin and the single gap around the collapsed status slot
        keep the action row separated from the body without drawing a rule.
        """
        if self._footer_metrics is None:
            return
        top, gap, buttons_height, bottom = self._footer_metrics
        self._footer.setFixedHeight(
            top
            + self.status_reveal.height()
            + gap
            + buttons_height
            + bottom
        )

    def _remeasure_base_height(self):
        self.dialog.setMinimumHeight(0)
        self.dialog.setMaximumHeight(16777215)
        hint = self.dialog.sizeHint().height()
        measured_base = max(1, hint - self._current_extra_height())
        scale = self.dialog.settingsUiScale()
        if self._design_base_height is None:
            normalizer = scale if scale >= 1.0 else 1.0
            self._design_base_height = int(round(measured_base / normalizer))
        proportional_base = int(round(self._design_base_height * scale))
        self._base_height = max(measured_base, proportional_base)
        self._sync_dialog_height()

    def _sync_dialog_height(self, _progress=0.0):
        if self._base_height is None:
            return
        self.dialog.setFixedHeight(self._base_height + self._current_extra_height())


class ViewRollComparisonPanel(QtWidgets.QScrollArea):
    """Side-by-side comparison of the shipped, Codex, and Kimi directions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RizumViewRollComparison")
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setStyleSheet(
            """
QScrollArea#RizumViewRollComparison,
QWidget#RizumViewRollComparisonCanvas,
QWidget#RizumViewRollComparisonColumn {
    background: transparent;
    border: 0;
}
QLabel#RizumViewRollComparisonLabel {
    color: #858a90;
    background: transparent;
    border: 0;
    padding: 0;
    font-size: 11px;
    font-weight: 500;
}
"""
        )

        canvas = QtWidgets.QWidget()
        canvas.setObjectName("RizumViewRollComparisonCanvas")
        row = QtWidgets.QHBoxLayout(canvas)
        row.setContentsMargins(0, 0, 0, 12)
        row.setSpacing(12)
        row.addStretch(1)

        self.panels = {}
        for variant in ("original", "codex", "kimi"):
            column = QtWidgets.QWidget()
            column.setObjectName("RizumViewRollComparisonColumn")
            column_layout = QtWidgets.QVBoxLayout(column)
            column_layout.setContentsMargins(0, 0, 0, 0)
            column_layout.setSpacing(8)
            label = QtWidgets.QLabel(DESIGN_VARIANTS[variant]["label"].upper())
            label.setObjectName("RizumViewRollComparisonLabel")
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
            panel = ViewRollConceptPanel(design_variant=variant)
            self.panels[variant] = panel
            column_layout.addWidget(label)
            column_layout.addWidget(panel)
            column_layout.addStretch(1)
            row.addWidget(column, 0, QtCore.Qt.AlignmentFlag.AlignTop)

        row.addStretch(1)
        canvas.setMinimumSize(row.sizeHint())
        self.setWidget(canvas)


def build_view_roll_preview(QtWidgets):
    """Build the View Roll Concept comparison for the standalone preview."""
    return ViewRollComparisonPanel()
