"""Standalone concept preview for a compact View Roll settings panel.

Fresh alternative design built on the shared Rizum UI kit: the Painter
settings dialog surface, segmented control, compact steppers, shortcut
capture, and stateful footer actions.
"""

from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from rizum_ui import (
    AnimatedSaveButton as SharedAnimatedSaveButton,
    FOOTER_BUTTON_PADDING_X,
    ModeParameterSlot,
    PAINTER_FOOTER_MARGIN_BOTTOM,
    PAINTER_FOOTER_MARGIN_X,
    PAINTER_SETTINGS_FRAME_COLOR,
    ActionButton,
    PainterSettingsDialog,
    SecondaryActionButton,
    ShortcutCaptureField as SharedShortcutCaptureField,
    TextActionButton as SharedTextActionButton,
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

PARAMETER_TRANSITION_DURATION = 140

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
    "de": {
        "title": "Einstellungen für Ansichtsrotation",
        "rotation": "Rotation",
        "mode": "Modus",
        "continuous": "Stufenlos",
        "custom": "Benutzerdefiniert",
        "speed": "Geschwindigkeit",
        "angle": "Winkel",
        "shortcuts": "Tastenkürzel",
        "roll_left": "3D-Ansicht nach links drehen",
        "roll_right": "3D-Ansicht nach rechts drehen",
        "roll_reset": "3D-Rotation zurücksetzen",
        "restore": "Zurücksetzen",
        "cancel": "Abbrechen",
        "save": "Speichern",
        "shortcut_tip": "Klicken, um ein neues Tastenkürzel einzugeben. Esc bricht ab, Entf löscht.",
        "shortcut_capture": "Tastenkürzel eingeben…",
        "shortcut_unset": "Nicht festgelegt",
        "shortcut_conflict": "Tastenkürzelkonflikt",
        "save_failed": "Änderungen konnten nicht gespeichert werden.",
    },
    "es": {
        "title": "Ajustes de rotación de vista",
        "rotation": "Rotación",
        "mode": "Modo",
        "continuous": "Continuo",
        "custom": "Personalizado",
        "speed": "Velocidad",
        "angle": "Ángulo",
        "shortcuts": "Atajos",
        "roll_left": "Girar vista 3D a la izquierda",
        "roll_right": "Girar vista 3D a la derecha",
        "roll_reset": "Restablecer rotación 3D",
        "restore": "Restablecer",
        "cancel": "Cancelar",
        "save": "Guardar",
        "shortcut_tip": "Haz clic para introducir un atajo nuevo. Esc cancela; Supr borra.",
        "shortcut_capture": "Pulsa el atajo…",
        "shortcut_unset": "Sin asignar",
        "shortcut_conflict": "Conflicto de atajos",
        "save_failed": "No se pudieron guardar los cambios.",
    },
    "fr": {
        "title": "Paramètres de rotation de la vue",
        "rotation": "Rotation",
        "mode": "Mode",
        "continuous": "Continu",
        "custom": "Personnalisé",
        "speed": "Vitesse",
        "angle": "Angle",
        "shortcuts": "Raccourcis",
        "roll_left": "Faire pivoter la vue 3D à gauche",
        "roll_right": "Faire pivoter la vue 3D à droite",
        "roll_reset": "Réinitialiser la rotation 3D",
        "restore": "Réinitialiser",
        "cancel": "Annuler",
        "save": "Enregistrer",
        "shortcut_tip": "Cliquez pour saisir un nouveau raccourci. Échap annule, Suppr efface.",
        "shortcut_capture": "Saisissez le raccourci…",
        "shortcut_unset": "Non défini",
        "shortcut_conflict": "Conflit de raccourcis",
        "save_failed": "Impossible d’enregistrer les modifications.",
    },
    "it": {
        "title": "Impostazioni rotazione vista",
        "rotation": "Rotazione",
        "mode": "Modalità",
        "continuous": "Continuo",
        "custom": "Personalizzato",
        "speed": "Velocità",
        "angle": "Angolo",
        "shortcuts": "Scorciatoie",
        "roll_left": "Ruota vista 3D a sinistra",
        "roll_right": "Ruota vista 3D a destra",
        "roll_reset": "Ripristina rotazione 3D",
        "restore": "Ripristina",
        "cancel": "Annulla",
        "save": "Salva",
        "shortcut_tip": "Fai clic per inserire una nuova scorciatoia. Esc annulla, Canc elimina.",
        "shortcut_capture": "Inserisci scorciatoia…",
        "shortcut_unset": "Non impostata",
        "shortcut_conflict": "Conflitto di scorciatoie",
        "save_failed": "Impossibile salvare le modifiche.",
    },
    "ko": {
        "title": "뷰 회전 설정",
        "rotation": "회전",
        "mode": "모드",
        "continuous": "연속",
        "custom": "사용자 지정",
        "speed": "속도",
        "angle": "각도",
        "shortcuts": "단축키",
        "roll_left": "3D 뷰 왼쪽으로 회전",
        "roll_right": "3D 뷰 오른쪽으로 회전",
        "roll_reset": "3D 회전 초기화",
        "restore": "초기화",
        "cancel": "취소",
        "save": "저장",
        "shortcut_tip": "클릭하여 새 단축키를 입력합니다. Esc는 취소, Delete는 지우기입니다.",
        "shortcut_capture": "단축키 입력…",
        "shortcut_unset": "설정 안 함",
        "shortcut_conflict": "단축키 충돌",
        "save_failed": "변경 내용을 저장할 수 없습니다.",
    },
    "pt": {
        "title": "Configurações de rotação da vista",
        "rotation": "Rotação",
        "mode": "Modo",
        "continuous": "Contínuo",
        "custom": "Personalizado",
        "speed": "Velocidade",
        "angle": "Ângulo",
        "shortcuts": "Atalhos",
        "roll_left": "Girar vista 3D para a esquerda",
        "roll_right": "Girar vista 3D para a direita",
        "roll_reset": "Redefinir rotação 3D",
        "restore": "Redefinir",
        "cancel": "Cancelar",
        "save": "Salvar",
        "shortcut_tip": "Clique para inserir um novo atalho. Esc cancela; Delete limpa.",
        "shortcut_capture": "Digite o atalho…",
        "shortcut_unset": "Não definido",
        "shortcut_conflict": "Conflito de atalhos",
        "save_failed": "Não foi possível salvar as alterações.",
    },
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
        "shortcut_capture": "请按快捷键…",
        "shortcut_unset": "未设置",
        "shortcut_conflict": "快捷键冲突",
        "save_failed": "无法保存更改。",
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
        "shortcut_capture": "ショートカットを入力…",
        "shortcut_unset": "未設定",
        "shortcut_conflict": "ショートカットの競合",
        "save_failed": "変更を保存できませんでした。",
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


class AnimatedSaveButton(QtWidgets.QAbstractButton):
    """Save action whose light, pulse, and checkmark communicate state."""

    BASE_HEIGHT = 28
    MIN_HEIGHT = 21
    ACTIVATION_DURATION = 140
    FEEDBACK_DURATION = 500

    def __init__(
        self,
        text,
        disabled_background,
        disabled_text,
        active_background,
        active_text,
        radius,
        parent=None,
    ):
        super().__init__(parent)
        self.setText(text)
        self.setObjectName("RizumViewRollSave")
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self.setStyleSheet(
            "QAbstractButton#RizumViewRollSave { background: transparent; border: 0; }"
        )
        self._disabled_background = QtGui.QColor(disabled_background)
        self._disabled_text = QtGui.QColor(disabled_text)
        self._active_background = QtGui.QColor(active_background)
        self._active_text = QtGui.QColor(active_text)
        self._radius = float(radius)
        self._compact_height = self.BASE_HEIGHT
        self._dirty = None
        self._feedback_active = False
        self._activation_progress = 0.0
        self._pulse_progress = 0.0
        self._check_progress = 0.0
        self._state_animation = None
        self._feedback_animation = None
        self.setCompactHeight(self.BASE_HEIGHT)
        self.setDirty(False, animate=False)

    @staticmethod
    def _blend(start, end, progress):
        progress = max(0.0, min(1.0, float(progress)))
        return QtGui.QColor(
            round(start.red() + (end.red() - start.red()) * progress),
            round(start.green() + (end.green() - start.green()) * progress),
            round(start.blue() + (end.blue() - start.blue()) * progress),
            round(start.alpha() + (end.alpha() - start.alpha()) * progress),
        )

    def _scale(self):
        return self._compact_height / float(self.BASE_HEIGHT)

    def _font(self):
        font = QtGui.QFont(self.font())
        font.setPixelSize(max(9, int(round(12 * self._scale()))))
        font.setWeight(QtGui.QFont.Weight.Normal)
        return font

    def sizeHint(self):
        text_width = QtGui.QFontMetrics(self._font()).horizontalAdvance(self.text())
        return QtCore.QSize(
            text_width + 2 * FOOTER_BUTTON_PADDING_X + 2,
            self._compact_height,
        )

    def setCompactHeight(self, height):
        self._compact_height = max(self.MIN_HEIGHT, int(round(height)))
        self.setFont(self._font())
        self.setFixedHeight(self._compact_height)
        self.updateGeometry()
        self.update()

    def activationDuration(self):
        return self.ACTIVATION_DURATION

    def feedbackDuration(self):
        return self.FEEDBACK_DURATION

    def feedbackActive(self):
        return self._feedback_active

    def activationProgress(self):
        return self._activation_progress

    def setActivationProgress(self, value):
        self._activation_progress = max(0.0, min(1.0, float(value)))
        self.update()

    animatedActivationProgress = QtCore.Property(
        float, activationProgress, setActivationProgress
    )

    def pulseProgress(self):
        return self._pulse_progress

    def setPulseProgress(self, value):
        self._pulse_progress = max(0.0, min(1.0, float(value)))
        self.update()

    animatedPulseProgress = QtCore.Property(
        float, pulseProgress, setPulseProgress
    )

    def checkProgress(self):
        return self._check_progress

    def setCheckProgress(self, value):
        self._check_progress = max(0.0, min(1.0, float(value)))
        self.update()

    animatedCheckProgress = QtCore.Property(
        float, checkProgress, setCheckProgress
    )

    def _stop_animation(self, attribute):
        animation = getattr(self, attribute)
        if animation is None:
            return
        animation.stop()
        animation.deleteLater()
        setattr(self, attribute, None)

    def _clear_animation(self, attribute, animation):
        if getattr(self, attribute) is animation:
            setattr(self, attribute, None)
        animation.deleteLater()

    def setDirty(self, dirty, animate=True):
        dirty = bool(dirty)
        if self._feedback_active and not dirty:
            self._dirty = False
            return
        if dirty and self._feedback_active:
            self._stop_animation("_feedback_animation")
            self._feedback_active = False
            self.setCheckProgress(0.0)
        if dirty == self._dirty and not self._feedback_active:
            return
        self._dirty = dirty
        self._stop_animation("_state_animation")
        self.setCursor(
            QtCore.Qt.CursorShape.PointingHandCursor
            if dirty
            else QtCore.Qt.CursorShape.ArrowCursor
        )
        super().setEnabled(dirty)

        target = 1.0 if dirty else 0.0
        if not animate:
            self.setActivationProgress(target)
            self.setPulseProgress(0.0)
            return

        group = QtCore.QParallelAnimationGroup(self)
        activation = QtCore.QPropertyAnimation(
            self, b"animatedActivationProgress", group
        )
        activation.setDuration(self.ACTIVATION_DURATION if dirty else 120)
        activation.setStartValue(self._activation_progress)
        activation.setEndValue(target)
        activation.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
        group.addAnimation(activation)
        if dirty:
            pulse = QtCore.QPropertyAnimation(
                self, b"animatedPulseProgress", group
            )
            pulse.setDuration(190)
            pulse.setStartValue(0.0)
            pulse.setKeyValueAt(0.58, 0.0)
            pulse.setKeyValueAt(0.78, 1.0)
            pulse.setEndValue(0.0)
            pulse.setEasingCurve(QtCore.QEasingCurve.Type.InOutSine)
            group.addAnimation(pulse)
        else:
            self.setPulseProgress(0.0)
        self._state_animation = group
        group.finished.connect(
            lambda: self._clear_animation("_state_animation", group)
        )
        group.start()

    def showSavedFeedback(self):
        if not self._dirty:
            return
        self._stop_animation("_state_animation")
        self._stop_animation("_feedback_animation")
        self._dirty = False
        self._feedback_active = True
        super().setEnabled(False)
        self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        self.setActivationProgress(1.0)
        self.setPulseProgress(0.0)
        self.setCheckProgress(0.0)

        group = QtCore.QParallelAnimationGroup(self)
        check = QtCore.QPropertyAnimation(self, b"animatedCheckProgress", group)
        check.setDuration(self.FEEDBACK_DURATION)
        check.setStartValue(0.0)
        check.setKeyValueAt(0.22, 1.0)
        check.setKeyValueAt(0.72, 1.0)
        check.setEndValue(0.0)
        group.addAnimation(check)
        activation = QtCore.QPropertyAnimation(
            self, b"animatedActivationProgress", group
        )
        activation.setDuration(self.FEEDBACK_DURATION)
        activation.setStartValue(1.0)
        activation.setKeyValueAt(0.72, 1.0)
        activation.setEndValue(0.0)
        activation.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic)
        group.addAnimation(activation)
        self._feedback_animation = group

        def finish():
            self._feedback_active = False
            self.setCheckProgress(0.0)
            self.setActivationProgress(0.0)
            self._clear_animation("_feedback_animation", group)

        group.finished.connect(finish)
        group.start()

    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.update()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.update()

    def paintEvent(self, event):
        del event
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing, True)

        background = self._blend(
            self._disabled_background,
            self._active_background,
            self._activation_progress,
        )
        if self._pulse_progress:
            background = self._blend(
                background, QtGui.QColor("#ffffff"), 0.12 * self._pulse_progress
            )
        if self._dirty and self.isEnabled():
            if self.isDown():
                background = background.darker(112)
            elif self.underMouse():
                background = background.lighter(104)
        text_color = self._blend(
            self._disabled_text,
            self._active_text,
            self._activation_progress,
        )
        radius = max(4.0, self._radius * self._scale())
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(background)
        painter.drawRoundedRect(
            QtCore.QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5),
            radius,
            radius,
        )

        painter.setFont(self._font())
        painter.setPen(text_color)
        painter.setOpacity(1.0 - self._check_progress)
        painter.drawText(self.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, self.text())

        painter.setOpacity(self._check_progress)
        scale = self._scale()
        center = QtCore.QPointF(self.rect().center())
        pen = QtGui.QPen(text_color, max(1.4, 1.7 * scale))
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPolyline(
            QtGui.QPolygonF(
                [
                    QtCore.QPointF(center.x() - 4.5 * scale, center.y()),
                    QtCore.QPointF(
                        center.x() - 1.2 * scale, center.y() + 3.0 * scale
                    ),
                    QtCore.QPointF(
                        center.x() + 5.2 * scale, center.y() - 3.8 * scale
                    ),
                ]
            )
        )
        painter.end()


class TransientErrorNotice(QtWidgets.QFrame):
    """Layout-independent error notice for failures that need interruption."""

    BASE_HEIGHT = 32
    MIN_HEIGHT = 24
    FADE_IN_DURATION = 120
    DISPLAY_DURATION = 1800
    FADE_OUT_DURATION = 180

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RizumViewRollErrorNotice")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(
            QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        self.setAutoFillBackground(False)
        self._compact_height = self.BASE_HEIGHT
        self._animation = None

        layout = QtWidgets.QHBoxLayout(self)
        layout.setSpacing(0)
        self._layout = layout
        self._label = QtWidgets.QLabel("")
        self._label.setObjectName("RizumViewRollErrorNoticeText")
        self._label.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self._label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(self._label)

        self._opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)
        self.setCompactHeight(self.BASE_HEIGHT)
        self.hide()

    def _scale(self):
        return self._compact_height / float(self.BASE_HEIGHT)

    def _scaled(self, value):
        return max(int(round(value * 0.75)), int(round(value * self._scale())))

    def _font(self):
        font = QtGui.QFont(self.font())
        font.setPixelSize(self._scaled(11))
        font.setWeight(QtGui.QFont.Weight.Medium)
        return font

    def setCompactHeight(self, height):
        self._compact_height = max(self.MIN_HEIGHT, int(round(height)))
        font = self._font()
        family = font.family().replace("\\", "\\\\").replace('"', '\\"')
        self._label.setFont(font)
        self._label.setStyleSheet(
            "background: transparent; border: 0; color: #f0f0f0; "
            f'font-family: "{family}"; font-size: {font.pixelSize()}px; '
            f"font-weight: {font.weight()};"
        )
        self._layout.setContentsMargins(
            self._scaled(34), 0, self._scaled(12), 0
        )
        self.setFixedHeight(self._compact_height)
        self.updateGeometry()
        self.update()

    def message(self):
        return self._label.text()

    def sizeHint(self):
        margins = self._layout.contentsMargins()
        text_width = QtGui.QFontMetrics(self._font()).horizontalAdvance(
            self._label.text()
        )
        return QtCore.QSize(
            margins.left() + text_width + margins.right(),
            self._compact_height,
        )

    def showMessage(self, message, duration=None):
        self._label.setText(str(message))
        width = self.sizeHint().width()
        if self.parentWidget() is not None:
            width = min(
                width,
                max(self._scaled(120), self.parentWidget().width() - 24),
            )
        self.setFixedSize(width, self._compact_height)

        if self._animation is not None:
            self._animation.stop()
            self._animation.deleteLater()
        self._opacity_effect.setOpacity(0.0)
        self.show()
        self.raise_()

        sequence = QtCore.QSequentialAnimationGroup(self)
        fade_in = QtCore.QPropertyAnimation(
            self._opacity_effect, b"opacity", sequence
        )
        fade_in.setDuration(self.FADE_IN_DURATION)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
        sequence.addAnimation(fade_in)
        sequence.addPause(
            self.DISPLAY_DURATION if duration is None else max(0, int(duration))
        )
        fade_out = QtCore.QPropertyAnimation(
            self._opacity_effect, b"opacity", sequence
        )
        fade_out.setDuration(self.FADE_OUT_DURATION)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QtCore.QEasingCurve.Type.InCubic)
        sequence.addAnimation(fade_out)

        def finish():
            self.hide()
            if self._animation is sequence:
                self._animation = None
            sequence.deleteLater()

        sequence.finished.connect(finish)
        self._animation = sequence
        sequence.start()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing, True)
        rect = QtCore.QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        radius = float(self._scaled(default_theme.radius_small))
        border = QtGui.QColor(default_theme.danger)
        border.setAlpha(190)
        painter.setPen(QtGui.QPen(border, 1))
        painter.setBrush(QtGui.QColor("#2a2223"))
        painter.drawRoundedRect(rect, radius, radius)

        icon_size = self._scaled(12)
        icon_rect = QtCore.QRectF(
            self._scaled(12),
            (self.height() - icon_size) / 2,
            icon_size,
            icon_size,
        )
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor(default_theme.danger))
        painter.drawEllipse(icon_rect)
        icon_font = QtGui.QFont(self._font())
        icon_font.setPixelSize(self._scaled(9))
        icon_font.setWeight(QtGui.QFont.Weight.Bold)
        painter.setFont(icon_font)
        painter.setPen(QtGui.QColor("#21191a"))
        painter.drawText(icon_rect, QtCore.Qt.AlignmentFlag.AlignCenter, "!")
        painter.end()


class ShortcutCaptureField(QtWidgets.QFrame):
    """Painted shortcut field with capture, clear, and conflict states."""

    shortcutChanged = QtCore.Signal(str)
    captureStateChanged = QtCore.Signal(bool)

    BASE_HEIGHT = 30
    MIN_HEIGHT = 23  # BASE_HEIGHT x 0.75, per the font-scale contract

    def __init__(
        self,
        action_name,
        parent=None,
        visual_style=None,
        capture_text="Type shortcut…",
        empty_text="Not set",
        conflict_text="Shortcut conflict",
    ):
        super().__init__(parent)
        self.setObjectName("RizumShortcutCapture")
        self._action_name = action_name
        self._visual_style = dict(visual_style or {})
        self._capture_text = str(capture_text)
        self._empty_text = str(empty_text)
        self._conflict_text = str(conflict_text)
        self._shortcut = ""
        self._capturing = False
        self._conflicted = False
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
        self.setAccessibleDescription(self._conflict_text if conflicted else "")
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
            return self._capture_text
        return self._shortcut or self._empty_text

    def _clear_slot_width(self):
        return self._scaled(22) if self._shortcut and not self._capturing else 0

    def _reserved_clear_slot_width(self):
        return self._scaled(22) if self._shortcut else 0

    def _clear_rect(self):
        slot = self._clear_slot_width()
        if not slot:
            return QtCore.QRectF()
        return QtCore.QRectF(self.width() - slot, 0, slot, self.height())

    def _conflict_rect(self):
        if not self._conflicted or self._capturing:
            return QtCore.QRectF()
        return self._clear_rect()

    def sizeHint(self):
        metrics = QtGui.QFontMetrics(self._font())
        candidates = [self._display_text(), self._capture_text, self._empty_text]
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
        self.setFocus(QtCore.Qt.FocusReason.MouseFocusReason)
        self.refreshMetrics()
        self.update()
        self.captureStateChanged.emit(True)

    def cancelCapture(self):
        if not self._capturing:
            return
        self._capturing = False
        self.refreshMetrics()
        self.update()
        self.captureStateChanged.emit(False)

    def _finish_capture(self, text):
        self._capturing = False
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

        conflict_rect = self._conflict_rect()
        if not conflict_rect.isEmpty() and not self._hover_clear:
            marker_size = self._scaled(10)
            marker = QtCore.QRectF(
                conflict_rect.center().x() - marker_size / 2,
                conflict_rect.center().y() - marker_size / 2,
                marker_size,
                marker_size,
            )
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(QtGui.QColor(theme.warning))
            painter.drawEllipse(marker)
            marker_font = QtGui.QFont(font)
            marker_font.setPixelSize(self._scaled(8))
            marker_font.setWeight(QtGui.QFont.Weight.Bold)
            painter.setFont(marker_font)
            painter.setPen(background)
            painter.drawText(marker, QtCore.Qt.AlignmentFlag.AlignCenter, "!")

        clear_rect = self._clear_rect()
        if not clear_rect.isEmpty() and (
            not self._conflicted or self._hover_clear
        ):
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
        duration=PARAMETER_TRANSITION_DURATION,
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
            max(70, round(self._duration * abs(target - self._progress)))
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


# The concept and the shipped plugin use the same interaction widgets. Keep
# the preview-specific names stable for callers while the implementations live
# in the vendored component package.
TextActionButton = SharedTextActionButton
AnimatedSaveButton = SharedAnimatedSaveButton
ShortcutCaptureField = SharedShortcutCaptureField


class ViewRollConceptPanel(QtWidgets.QWidget):
    """Tab content for the View Roll settings concept."""

    def __init__(
        self, parent=None, design_variant="original", save_handler=None
    ):
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
        self._save_handler = save_handler
        self._last_save_error = None
        self._name_labels = []
        self._texts_blocks = []

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(10)

        self.dialog = PainterSettingsDialog(self)
        self.dialog.setWindowFlags(QtCore.Qt.WindowType.Widget)
        self.dialog.setSettingsFrameBottomWidth(
            self.dialog.settingsFrameWidth()
        )
        self.dialog.setSettingsBottomEdgeExtensionEnabled(False)
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
                self.mode_segment.setCornerRadius(default_theme.radius)
                # A small paint gutter keeps Qt's antialiasing
                # from flattening the end caps against the widget boundary.
                self.mode_segment.setPaintInset(1.5)
            self.mode_segment.setTheme(segment_theme)
        mode_row, mode_layout = self._make_row()
        self.mode_label = self._make_name(_preview_text("mode", "Mode"))
        mode_layout.addWidget(self.mode_label)
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
        self.speed_row = speed_row

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
        self.angle_row = angle_row
        self.parameter_slot = None
        self.speed_reveal = None
        self.angle_reveal = None
        if self.design_variant == "codex":
            self.parameter_slot = ModeParameterSlot(
                {"continuous": speed_row, "custom": angle_row},
                speed_row.height(),
            )
            self.parameter_slot.setGeometryCallback(self._sync_dialog_height)
            self._body_layout.addWidget(self.parameter_slot)
        else:
            self.speed_reveal = _RevealRow(speed_row, speed_row.height())
            self.speed_reveal.setGeometryCallback(self._sync_dialog_height)
            self._body_layout.addWidget(self.speed_reveal)
            self.angle_reveal = _RevealRow(angle_row, angle_row.height())
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
                capture_text=_preview_text(
                    "shortcut_capture", "Type shortcut…"
                ),
                empty_text=_preview_text("shortcut_unset", "Not set"),
                conflict_text=_preview_text(
                    "shortcut_conflict", "Shortcut conflict"
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
        if self.design_variant == "codex":
            self.cancel_button = SecondaryActionButton(
                _preview_text("cancel", "Cancel"),
                self._visual_style["control"],
                self._visual_style["control_hover"],
                "#2b2d30",
                self._visual_style["text"],
                default_theme.radius_small,
            )
        else:
            self.cancel_button = ActionButton.create(
                _preview_text("cancel", "Cancel"), "dialog-secondary"
            )
        self.cancel_button.setObjectName("RizumViewRollCancel")
        if self.design_variant == "codex":
            self.save_button = AnimatedSaveButton(
                _preview_text("save", "Save"),
                self._visual_style["control"],
                self._visual_style["faint"],
                self._visual_style["accent"],
                self._visual_style["accent_text"],
                default_theme.radius_small,
            )
        else:
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
        self.error_notice = TransientErrorNotice(content)

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
        self._refresh_save_state()

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
        self._refresh_save_state()

    def save_changes(self):
        next_state = self.current_state()
        if next_state == self._saved_state:
            self._refresh_save_state()
            return True
        show_feedback = isinstance(
            self.save_button, AnimatedSaveButton
        )
        if self._save_handler is not None:
            try:
                saved = self._save_handler(_copy_state(next_state))
                if saved is False:
                    raise RuntimeError("Save handler rejected the settings")
            except Exception as error:
                self._last_save_error = error
                self.show_save_error()
                self._refresh_save_state()
                return False
        self._last_save_error = None
        self._saved_state = next_state
        if show_feedback:
            self.save_button.showSavedFeedback()
        self._refresh_save_state()
        return True

    def cancel_changes(self):
        self._apply_state(self._saved_state)

    def restore_defaults(self):
        self._apply_state(_copy_state(DEFAULTS))

    # --- interactions ---------------------------------------------------

    def _on_mode_changed(self, _data):
        self._apply_mode_reveals(animate=True)
        if not self._restoring:
            self._refresh_save_state()

    def _apply_mode_reveals(self, animate):
        mode = self.mode_segment.currentData()
        if self.parameter_slot is not None:
            self.parameter_slot.setMode(mode, animate=animate)
        else:
            self.speed_reveal.setExpanded(mode == "continuous", animate=animate)
            self.angle_reveal.setExpanded(mode == "custom", animate=animate)
        if not animate:
            self._remeasure_base_height()

    def _on_value_edited(self, _value):
        if not self._restoring:
            self._refresh_save_state()

    def _on_shortcut_changed(self, _text):
        if self._restoring:
            return
        self._refresh_conflicts()
        self._refresh_save_state()

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

    def _refresh_save_state(self):
        dirty = self.is_dirty()
        if isinstance(self.save_button, AnimatedSaveButton):
            self.save_button.setDirty(dirty)
        else:
            self.save_button.setEnabled(dirty)

    def show_save_error(self, message=None):
        self.error_notice.showMessage(
            message
            or _preview_text("save_failed", "Could not save changes.")
        )
        self._position_error_notice()

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

        # Preserve the established separator-to-action rhythm without keeping
        # an empty status row in the footer.
        footer_outer = self._footer.layout()
        footer_outer.setContentsMargins(
            0, footer_top + footer_gap, 0, footer_bottom
        )
        footer_outer.setSpacing(0)
        self._footer_metrics = (footer_top, footer_gap, buttons_height, footer_bottom)
        self._sync_footer_height()
        self._button_row.setFixedHeight(buttons_height)
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
        for stepper in (self.speed_stepper, self.angle_stepper):
            stepper.parentWidget().setFixedHeight(tall_height)
        if self.parameter_slot is not None:
            self.parameter_slot.setExpandedHeight(tall_height)
        else:
            self.speed_reveal.setExpandedHeight(tall_height)
            self.angle_reveal.setExpandedHeight(tall_height)
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
            (self.cancel_button, 56, 112),
            (self.save_button, 52, 92),
        ):
            if isinstance(button, TextActionButton):
                button.setCompactHeight(footer_button_height)
                continue
            if isinstance(button, AnimatedSaveButton):
                button.setCompactHeight(footer_button_height)
                width = self._footer_button_width(
                    button, minimum=minimum, maximum=maximum
                )
                button.setFixedSize(width, footer_button_height)
                continue
            if isinstance(button, SecondaryActionButton):
                button.setCompactHeight(footer_button_height)
                width = self._footer_button_width(
                    button, minimum=minimum, maximum=maximum
                )
                button.setFixedSize(width, footer_button_height)
                continue
            width = self._footer_button_width(
                button, minimum=minimum, maximum=maximum
            )
            set_compact_footer_button_width(
                button, width, height=footer_button_height
            )
        self.error_notice.setCompactHeight(self._metric(32, 24))

        # Width is measured, not fixed: stay at the compact baseline unless
        # the scaled footer buttons or field rows genuinely need more room.
        self.dialog.setFixedWidth(self._required_dialog_width())
        self._restyle()
        self._position_error_notice()

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
        if isinstance(button, (SecondaryActionButton, AnimatedSaveButton)):
            width = button.sizeHint().width()
        else:
            text_width = QtGui.QFontMetrics(
                self._footer_button_font()
            ).horizontalAdvance(button.text())
            # +2: the QSS button helper reserves padding*2 + 2 for chrome.
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
        mode_need = labeled_row_need(
            self.mode_label.width(), self.mode_segment.sizeHint().width()
        )
        shortcut_need = max(
            labeled_row_need(
                field._rizum_name_label.width(),
                field.sizeHint().width(),
            )
            for field in self.shortcut_fields.values()
        )

        content_need = max(footer_need, mode_need, stepper_need, shortcut_need)
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
QWidget#RizumViewRollFooterRow,
QWidget#RizumViewRollTexts,
QWidget#RizumViewRollFooterDivider,
QFrame#RizumViewRollReveal,
QFrame#RizumModeParameterSlot {{
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
        if self.parameter_slot is not None:
            extra = round(
                self.parameter_slot.expandedHeight()
                * self.parameter_slot.heightProgress()
            )
        else:
            extra = sum(
                round(reveal.expandedHeight() * reveal.progress())
                for reveal in (self.speed_reveal, self.angle_reveal)
            )
        return extra

    def _sync_footer_height(self):
        """Keep the footer rhythm fixed while all feedback stays elsewhere."""
        if self._footer_metrics is None:
            return
        top, gap, buttons_height, bottom = self._footer_metrics
        self._footer.setFixedHeight(top + gap + buttons_height + bottom)

    def _position_error_notice(self):
        if not hasattr(self, "error_notice"):
            return
        content = self.error_notice.parentWidget()
        if content is None or not self.error_notice.isVisible():
            return
        footer_top = self._footer.mapTo(content, QtCore.QPoint(0, 0)).y()
        x = max(0, (content.width() - self.error_notice.width()) // 2)
        y = max(
            0,
            footer_top - self.error_notice.height() - self._metric(8, 6),
        )
        self.error_notice.move(x, y)
        self.error_notice.raise_()

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
        self._position_error_notice()


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
