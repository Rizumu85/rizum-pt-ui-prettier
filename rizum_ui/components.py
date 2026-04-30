"""Reusable PySide6 widgets for Rizum Painter plugins."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

COMPACT_DOCK_MIN_WIDTH = 250
COMPACT_DOCK_DEFAULT_WIDTH = COMPACT_DOCK_MIN_WIDTH
COMPACT_DOCK_DEFAULT_HEIGHT = 184
COMPACT_DOCK_OUTER_MARGINS = (3, 0, 3, 3)
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


def update_compact_field_row(row_widget, label_width=None, control_width=None):
    """Refresh fixed field-row metrics after a runtime font change."""
    try:
        label = row_widget._rizum_label
    except AttributeError:
        label = None
    try:
        control = row_widget._rizum_control
    except AttributeError:
        control = None

    if label is not None and label_width is not None:
        label.setFixedWidth(int(label_width))
    if control is not None and control_width is not None:
        control.setFixedWidth(int(control_width))
    try:
        row_widget.updateGeometry()
    except Exception:
        pass


def compact_text_width(text, widget=None, minimum=0, maximum=None, padding=0):
    """Return a clamped text width using the active Qt font metrics."""
    from PySide6 import QtGui, QtWidgets

    if widget is not None:
        font = widget.font()
    else:
        app = QtWidgets.QApplication.instance()
        font = app.font() if app is not None else QtGui.QFont()
    width = QtGui.QFontMetrics(font).horizontalAdvance(str(text)) + padding
    width = max(minimum, width)
    if maximum is not None:
        width = min(maximum, width)
    return int(width)


def compact_label_width(labels, widget=None, minimum=28, maximum=56, padding=0):
    """Size compact field labels from localized text without bloating English."""
    if isinstance(labels, str):
        labels = [labels]
    width = minimum
    for label in labels:
        width = max(
            width,
            compact_text_width(label, widget=widget, minimum=minimum, padding=padding),
        )
    return min(maximum, int(width))


def compact_footer_button_width(button, minimum=56, maximum=112, padding=22):
    """Return a localized footer button width while preserving compact bounds."""
    return compact_text_width(
        button.text(),
        widget=button,
        minimum=minimum,
        maximum=maximum,
        padding=padding,
    )


def make_inline_checkbox_row(label_text, checkbox, parent=None, minimum=88, maximum=150):
    """Create a compact localized label + checkbox row."""
    from PySide6 import QtCore, QtWidgets

    widget = QtWidgets.QWidget(parent)
    widget.setObjectName("RizumInlineCheckbox")
    widget.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    layout = QtWidgets.QHBoxLayout(widget)
    layout.setContentsMargins(6, 3, 6, 3)
    layout.setSpacing(6)

    label = QtWidgets.QLabel(label_text)
    label.setObjectName("RizumHintLabel")
    text_width = compact_text_width(label_text, widget=label, minimum=0, maximum=maximum - 26)
    label.setMinimumWidth(text_width)
    label.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Preferred,
        QtWidgets.QSizePolicy.Policy.Preferred,
    )
    layout.addWidget(label)
    layout.addWidget(checkbox)

    row_width = min(maximum, max(minimum, text_width + checkbox.width() + 24))
    widget.setMinimumWidth(row_width)
    widget._rizum_label = label
    widget._rizum_checkbox = checkbox
    widget._rizum_minimum = minimum
    widget._rizum_maximum = maximum

    def toggle(event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            checkbox.toggle()

    widget.mousePressEvent = toggle
    return widget


def update_inline_checkbox_row(widget, label_text=None, minimum=None, maximum=None):
    """Refresh an inline checkbox row after translation or font-scale changes."""
    from PySide6 import QtWidgets

    label = getattr(widget, "_rizum_label", None)
    checkbox = getattr(widget, "_rizum_checkbox", None)
    minimum = int(minimum if minimum is not None else getattr(widget, "_rizum_minimum", 88))
    maximum = int(maximum if maximum is not None else getattr(widget, "_rizum_maximum", 150))
    if label is None:
        label = widget.findChild(QtWidgets.QLabel, "RizumHintLabel")
    if checkbox is None:
        checkbox = widget.findChild(QtWidgets.QWidget, "RizumMockCheckbox")
    if label is None or checkbox is None:
        return

    if label_text is not None:
        label.setText(label_text)
    text_width = compact_text_width(
        label.text(),
        widget=label,
        minimum=0,
        maximum=max(0, maximum - 26),
    )
    label.setMinimumWidth(text_width)
    row_width = min(maximum, max(minimum, text_width + checkbox.width() + 24))
    widget.setMinimumWidth(row_width)
    try:
        widget.updateGeometry()
    except Exception:
        pass


def make_collapsible_group(
    title,
    subtitle="",
    children=None,
    leading_widget=None,
    trailing_widget=None,
    expanded=True,
    show_chevron=True,
    parent=None,
):
    """Create an animated folder-like group with optional leading/trailing slots."""
    from PySide6 import QtCore, QtGui, QtWidgets

    duration = 300

    class _CollapsibleChevron(QtWidgets.QWidget):
        def __init__(self, is_expanded):
            super().__init__()
            self.setObjectName("RizumCollapsibleChevron")
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.setFixedSize(14, 14)
            self._angle = 90.0 if is_expanded else 0.0

        def getAngle(self):
            return self._angle

        def setAngle(self, angle):
            self._angle = float(angle)
            self.update()

        angle = QtCore.Property(float, getAngle, setAngle)

        def paintEvent(self, event):
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
            painter.translate(self.width() / 2, self.height() / 2)
            painter.rotate(self._angle)
            painter.translate(-self.width() / 2, -self.height() / 2)
            pen = QtGui.QPen(QtGui.QColor("#9e9e9e"))
            pen.setWidthF(1.7)
            pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPolyline(
                [
                    QtCore.QPointF(5.0, 3.7),
                    QtCore.QPointF(8.4, 7.0),
                    QtCore.QPointF(5.0, 10.3),
                ]
            )

    class _AnimatedHeightFrame(QtWidgets.QFrame):
        def __init__(self):
            super().__init__()
            self._animated_height = 0
            self.setAutoFillBackground(False)
            clipped_attr = getattr(QtCore.Qt.WidgetAttribute, "WA_Clipped", None)
            if clipped_attr is not None:
                self.setAttribute(clipped_attr, True)
            clip_attr = getattr(QtCore.Qt.WidgetAttribute, "WA_ClipChildren", None)
            if clip_attr is not None:
                self.setAttribute(clip_attr, True)

        def resizeEvent(self, event):
            super().resizeEvent(event)
            for child in self.findChildren(QtWidgets.QWidget, options=QtCore.Qt.FindChildOption.FindDirectChildrenOnly):
                child.resize(self.width(), child.sizeHint().height())

        def getAnimatedHeight(self):
            return self._animated_height

        def setAnimatedHeight(self, value):
            self._animated_height = max(0, int(round(value)))
            self.setFixedHeight(self._animated_height)
            self.update()
            self.updateGeometry()

        animatedHeight = QtCore.Property(int, getAnimatedHeight, setAnimatedHeight)

    group = QtWidgets.QFrame(parent)
    group.setObjectName("RizumCollapsibleGroup")
    group.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
    group.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    group_layout = QtWidgets.QVBoxLayout(group)
    group_layout.setContentsMargins(0, 2, 0, 2)
    group_layout.setSpacing(0)

    header = QtWidgets.QFrame()
    header.setObjectName("RizumCollapsibleHeader")
    header.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
    header.setFixedHeight(36)
    header_layout = QtWidgets.QHBoxLayout(header)
    header_layout.setContentsMargins(8, 4, 8, 4)
    header_layout.setSpacing(10)

    chevron = None
    if show_chevron:
        chevron = _CollapsibleChevron(expanded)
        header_layout.addWidget(chevron)

    if leading_widget is not None:
        header_layout.addWidget(leading_widget)

    if subtitle:
        title_layout = QtWidgets.QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("RizumCollapsibleTitle")
        subtitle_label = QtWidgets.QLabel(subtitle)
        subtitle_label.setObjectName("RizumCollapsibleSubtitle")
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.addStretch(1)
        header_layout.addLayout(title_layout)
    else:
        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("RizumCollapsibleTitle")
        header_layout.addWidget(title_label)

    header_layout.addStretch(1)
    if trailing_widget is not None:
        header_layout.addWidget(trailing_widget)
    group_layout.addWidget(header)

    content = _AnimatedHeightFrame()
    content.setObjectName("RizumCollapsibleContent")
    content.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
    content.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Fixed,
    )
    content_inner = QtWidgets.QWidget(content)
    content_inner.setObjectName("RizumCollapsibleContentInner")
    content_inner.setAutoFillBackground(False)
    content_layout = QtWidgets.QVBoxLayout(content_inner)
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(2)
    for child in children or []:
        content_layout.addWidget(child)
    group_layout.addWidget(content)

    def content_height():
        content_inner.adjustSize()
        return content_inner.sizeHint().height()

    def sync_inner_size():
        content_inner.resize(content.width(), content_inner.sizeHint().height())

    content.setVisible(True)
    sync_inner_size()
    if expanded:
        initial_height = content_height()
        content.setAnimatedHeight(initial_height)
    else:
        content.setAnimatedHeight(0)
        content_inner.move(0, 0)
    content_inner.setVisible(bool(expanded))

    def update_chevron(next_expanded):
        if chevron is None:
            return
        chevron.setAngle(90.0 if next_expanded else 0.0)

    def set_expanded(next_expanded):
        next_expanded = bool(next_expanded)
        if group._rizum_expanded == next_expanded:
            return
        group._rizum_expanded = next_expanded
        group._rizum_animation_token += 1
        animation_token = group._rizum_animation_token
        content.setVisible(True)
        content.updateGeometry()
        target_height = content_height() if next_expanded else 0
        start_height = content.getAnimatedHeight()
        sync_inner_size()
        content_inner.move(0, 0)
        content_inner.setVisible(True)

        old_animation = getattr(group, "_rizum_collapse_animation", None)
        if old_animation is not None:
            old_animation.stop()

        height_animation = QtCore.QPropertyAnimation(content, b"animatedHeight", group)
        height_animation.setDuration(duration)
        height_animation.setStartValue(start_height)
        height_animation.setEndValue(target_height)
        height_animation.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)

        animation_group = QtCore.QParallelAnimationGroup(group)
        animation_group.addAnimation(height_animation)
        if chevron is not None:
            chevron_animation = QtCore.QPropertyAnimation(chevron, b"angle", group)
            chevron_animation.setDuration(duration)
            chevron_animation.setStartValue(chevron.getAngle())
            chevron_animation.setEndValue(90.0 if next_expanded else 0.0)
            chevron_animation.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
            animation_group.addAnimation(chevron_animation)

        def finish():
            if animation_token != group._rizum_animation_token:
                return
            content.setAnimatedHeight(target_height)
            content_inner.setVisible(next_expanded)
            update_chevron(next_expanded)

        animation_group.finished.connect(finish)
        group._rizum_collapse_animation = animation_group
        animation_group.start()

    def toggle():
        set_expanded(not group._rizum_expanded)

    group._rizum_expanded = bool(expanded)
    group._rizum_animation_token = 0
    group._rizum_header = header
    group._rizum_content = content
    group._rizum_content_inner = content_inner
    group._rizum_content_layout = content_layout
    group.setExpanded = set_expanded
    group.isExpanded = lambda: group._rizum_expanded
    group.toggle = toggle
    header.mousePressEvent = lambda event: toggle() if event.button() == QtCore.Qt.MouseButton.LeftButton else None
    return group


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


def make_icon_button(icon_name, tooltip="", size=16, compact=True):
    """Create a themed icon button from the shared icons folder."""
    from PySide6 import QtCore, QtGui, QtWidgets

    try:
        from PySide6 import QtSvg
    except Exception:
        QtSvg = None

    class _AnimatedIconButton(QtWidgets.QPushButton):
        def __init__(self, icon_path):
            super().__init__("")
            self._icon_path = icon_path
            self._icon = QtGui.QIcon(str(icon_path))
            self._icon_source = ""
            try:
                self._icon_source = icon_path.read_text(encoding="utf-8")
            except Exception:
                pass
            self._pixmap_cache = {}
            self._visual_scale = 1.0
            self._visual_opacity = 1.0
            self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        def getVisualScale(self):
            return self._visual_scale

        def setVisualScale(self, value):
            self._visual_scale = float(value)
            self.update()

        def getVisualOpacity(self):
            return self._visual_opacity

        def setVisualOpacity(self, value):
            self._visual_opacity = float(value)
            self.update()

        visualScale = QtCore.Property(float, getVisualScale, setVisualScale)
        visualOpacity = QtCore.Property(float, getVisualOpacity, setVisualOpacity)

        def enterEvent(self, event):
            super().enterEvent(event)
            self.update()

        def leaveEvent(self, event):
            super().leaveEvent(event)
            if not self.isDown():
                self._animate_icon(1.0, 1.0, 160)
            self.update()

        def mousePressEvent(self, event):
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self._animate_icon(0.85, 0.7, 80)
            super().mousePressEvent(event)

        def mouseReleaseEvent(self, event):
            super().mouseReleaseEvent(event)
            self._animate_icon(1.0, 1.0, 180)

        def _animate_icon(self, scale, opacity, duration):
            old_animation = getattr(self, "_rizum_icon_animation", None)
            if old_animation is not None:
                old_animation.stop()
            easing = QtCore.QEasingCurve.Type.OutCubic
            scale_animation = QtCore.QPropertyAnimation(self, b"visualScale", self)
            scale_animation.setDuration(duration)
            scale_animation.setStartValue(self._visual_scale)
            scale_animation.setEndValue(scale)
            scale_animation.setEasingCurve(easing)
            opacity_animation = QtCore.QPropertyAnimation(self, b"visualOpacity", self)
            opacity_animation.setDuration(duration)
            opacity_animation.setStartValue(self._visual_opacity)
            opacity_animation.setEndValue(opacity)
            opacity_animation.setEasingCurve(easing)
            animation_group = QtCore.QParallelAnimationGroup(self)
            animation_group.addAnimation(scale_animation)
            animation_group.addAnimation(opacity_animation)
            self._rizum_icon_animation = animation_group
            animation_group.start()

        def _rendered_pixmap(self, color):
            dpr = self.devicePixelRatioF()
            key = (color, round(dpr, 2), size)
            if key in self._pixmap_cache:
                return self._pixmap_cache[key]
            pixel_size = max(1, int(round(size * dpr)))
            pixmap = QtGui.QPixmap(pixel_size, pixel_size)
            pixmap.setDevicePixelRatio(dpr)
            pixmap.fill(QtCore.Qt.GlobalColor.transparent)
            if QtSvg is not None and self._icon_source:
                source = self._icon_source
                for old_color in ("#9E9E9E", "#9e9e9e", "#E0E0E0", "#e0e0e0"):
                    source = source.replace(old_color, color)
                source = source.replace('viewBox="0 0 24 24"', 'viewBox="-1 -1 26 26"')
                renderer = QtSvg.QSvgRenderer(QtCore.QByteArray(source.encode("utf-8")))
                painter = QtGui.QPainter(pixmap)
                renderer.render(painter, QtCore.QRectF(0, 0, size, size))
                painter.end()
            else:
                base = self._icon.pixmap(QtCore.QSize(pixel_size, pixel_size))
                painter = QtGui.QPainter(pixmap)
                painter.drawPixmap(QtCore.QRectF(0, 0, size, size), base, QtCore.QRectF(base.rect()))
                painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceIn)
                painter.fillRect(QtCore.QRectF(0, 0, size, size), QtGui.QColor(color))
                painter.end()
            self._pixmap_cache[key] = pixmap
            return pixmap

        def paintEvent(self, event):
            super().paintEvent(event)
            color = "#ffffff" if self.underMouse() else "#9e9e9e"
            pixmap = self._rendered_pixmap(color)
            visual_size = max(1, int(round(size * self._visual_scale)))
            target = QtCore.QRect(
                int((self.width() - visual_size) / 2),
                int((self.height() - visual_size) / 2),
                visual_size,
                visual_size,
            )
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform, True)
            painter.setOpacity(max(0.0, min(1.0, self._visual_opacity)))
            painter.drawPixmap(target, pixmap)
            painter.end()

    icon_path = ROOT / "icons" / icon_name
    button = _AnimatedIconButton(icon_path)
    button.setProperty("variant", "icon")
    if compact:
        button.setProperty("compact", True)
    button.setMinimumHeight(32)
    if tooltip:
        button.setToolTip(tooltip)
    return button


def make_svg_label(icon_name, size):
    """Create a passive SVG label that does not take its own hover state."""
    from PySide6 import QtCore, QtGui, QtWidgets

    label = QtWidgets.QLabel()
    label.setObjectName("RizumSvgLabel")
    label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    label.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground, True)
    label.setPixmap(QtGui.QIcon(str(ROOT / "icons" / icon_name)).pixmap(QtCore.QSize(size, size)))
    label.setFixedSize(size, size)
    label.setStyleSheet("background: transparent; border: 0;")
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
            self._menu = None
            self._last_menu_close_ms = 0
            self._fit_to_contents = True

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
            self._arrow = CompactChevronDown()
            layout.addWidget(self._arrow)

            for item in options or []:
                if isinstance(item, tuple):
                    self.addItem(item[0], item[1])
                else:
                    self.addItem(item, item)
            self.fitToContents()

        def clear(self):
            self._items = []
            self._current_index = -1
            self._label.setText("")

        def addItem(self, text, userData=None):
            self._items.append((text, userData))
            if self._current_index < 0:
                self.setCurrentIndex(0)
            self.fitToContents()

        def setFitToContents(self, enabled):
            self._fit_to_contents = bool(enabled)
            if self._fit_to_contents:
                self.fitToContents()
            else:
                self.setMinimumWidth(0)
                self.setMaximumWidth(16777215)

        def fitToContents(self):
            if not self._fit_to_contents or not self._items:
                return
            metrics = self.fontMetrics()
            text_width = max(metrics.horizontalAdvance(item[0]) for item in self._items)
            margins = self.layout().contentsMargins()
            width = text_width + margins.left() + margins.right() + self.layout().spacing() + self._arrow.width()
            self.setFixedWidth(width)

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
            now = QtCore.QDateTime.currentMSecsSinceEpoch()
            if now - self._last_menu_close_ms < 180:
                return
            if self._menu is not None and self._menu.isVisible():
                self._menu.close()
                return
            menu = QtWidgets.QMenu(self)
            menu.setObjectName("RizumPopupMenu")
            for index, item in enumerate(self._items):
                action = menu.addAction(item[0])
                action.triggered.connect(lambda checked=False, i=index: self.setCurrentIndex(i))
            self._menu = menu
            menu.aboutToHide.connect(self._close_menu)
            self._arrow.setOpen(True)
            menu.popup(self.mapToGlobal(QtCore.QPoint(0, self.height() + 4)))

        def _close_menu(self):
            self._arrow.setOpen(False)
            self._last_menu_close_ms = QtCore.QDateTime.currentMSecsSinceEpoch()
            self._menu = None

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
                self.setObjectName("RizumChevronIcon")
                self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
                self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, False)
                self.setAutoFillBackground(False)
                self.setFixedSize(10, 10)
                self.setStyleSheet("background: transparent; border: 0;")
                self._angle = 0.0

            def getAngle(self):
                return self._angle

            def setAngle(self, angle):
                self._angle = float(angle)
                self.update()

            angle = QtCore.Property(float, getAngle, setAngle)

            def setOpen(self, is_open):
                old_animation = getattr(self, "_rizum_arrow_animation", None)
                if old_animation is not None:
                    old_animation.stop()
                animation = QtCore.QPropertyAnimation(self, b"angle", self)
                animation.setDuration(400)
                animation.setStartValue(self._angle)
                animation.setEndValue(180.0 if is_open else 0.0)
                animation.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
                self._rizum_arrow_animation = animation
                animation.start()

            def paintEvent(self, event):
                painter = QtGui.QPainter(self)
                painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
                painter.translate(self.width() / 2, self.height() / 2)
                painter.rotate(self._angle)
                painter.translate(-self.width() / 2, -self.height() / 2)
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


def make_mock_checkbox(checked=True):
    """Create the filled/outline checkbox used by compact Rizum panels."""
    from PySide6 import QtCore, QtGui, QtWidgets

    class _Checkbox(QtWidgets.QWidget):
        def __init__(self):
            super().__init__()
            self.setObjectName("RizumMockCheckbox")
            self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            self.setFixedSize(14, 14)
            self._checked = bool(checked)
            self._indeterminate = False
            self.setProperty("checked", self._checked)
            self.setProperty("indeterminate", False)

        def toggle(self):
            self.set_checked(not self._checked)

        def set_checked(self, checked):
            self._checked = checked
            self._indeterminate = False
            self.setProperty("checked", checked)
            self.setProperty("indeterminate", False)
            self.update()

        def set_indeterminate(self, indeterminate):
            self._indeterminate = bool(indeterminate)
            if self._indeterminate:
                self._checked = False
            self.setProperty("checked", self._checked)
            self.setProperty("indeterminate", self._indeterminate)
            self.update()

        def is_indeterminate(self):
            return self._indeterminate

        def isChecked(self):
            return self._checked and not self._indeterminate

        def setChecked(self, checked):
            self.set_checked(bool(checked))

        def setIndeterminate(self, indeterminate):
            self.set_indeterminate(bool(indeterminate))

        def mousePressEvent(self, event):
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self.toggle()

        def paintEvent(self, event):
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

            if self._checked or self._indeterminate:
                painter.setPen(QtCore.Qt.PenStyle.NoPen)
                painter.setBrush(QtGui.QColor("#ffffff"))
                painter.drawRoundedRect(QtCore.QRectF(0, 0, 14, 14), 3, 3)

                pen = QtGui.QPen(QtGui.QColor("#1b1b1b"))
                pen.setWidthF(1.6)
                pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                if self._indeterminate:
                    painter.drawLine(QtCore.QPointF(3.6, 7.0), QtCore.QPointF(10.4, 7.0))
                else:
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
    widget._rizum_label = label
    widget._rizum_control = control
    return widget
