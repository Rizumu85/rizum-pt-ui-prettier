"""Interactive preview for the proposed Rizum Liquify dock workflow."""

from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from rizum_ui import (
    AnimatedSaveButton,
    PAINTER_DIALOG_STYLE,
    SecondaryActionButton,
    StatusBanner,
    TextActionButton,
    apply_compact_dock_surface,
    install_compact_tooltip,
    make_combo_input,
    make_compact_dock_card,
    make_compact_dock_layout,
    make_icon_button,
    make_inset_separator,
)


_TEXT = {
    "en": {
        "state": "State",
        "width": "Width",
        "empty": "First use",
        "ready": "Ready",
        "active": "Liquifying",
        "repair": "Needs repair",
        "blocked": "Apply blocked",
        "complete": "Applied",
        "narrow": "Narrow",
        "standard": "Standard",
        "wide": "Wide",
        "target_none": "No Liquify targets",
        "target_folder": "Folder · Character",
        "target_set": "Layer Set 01 · 3 layers",
        "empty_title": "No Liquify target",
        "empty_subtitle": "The current selection can become a target.",
        "ready_title": "Ready · Folder · Character",
        "ready_subtitle": "3 layers ready to apply",
        "active_title": "Liquify active · Folder · Character",
        "active_subtitle": "Flow painting · 3 layers ready",
        "active_brief": "Liquify active",
        "repair_title": "Target structure needs repair",
        "repair_subtitle": "Managed layers are incomplete",
        "blocked_title": "Apply is blocked",
        "blocked_subtitle": "2 layer structures need attention",
        "complete_title": "Applied to 3 layers",
        "complete_subtitle": "The target was removed safely",
        "create": "Create target from selection",
        "start": "Start Liquify",
        "return": "Return to Painting",
        "repair_start": "Repair and Start",
        "repair_action": "Repair",
        "view": "View",
        "hide": "Hide",
        "apply": "Apply",
        "clear": "Clear Flow",
        "add_members": "Add selected layers",
        "remove_members": "Remove selected layers",
        "delete_target": "Delete target",
        "copy_diagnostics": "Copy diagnostics",
        "new_target_tip": "Create a new target from the current selection",
        "refresh_tip": "Refresh Liquify targets",
        "repair_tip": "Repair the selected target",
        "more_tip": "Target actions",
        "mode_tip": "Liquify modes and 3D/UV alignment remain in Painter Assets.",
        "blockers": "Blocking structures",
        "blocker_1": "Character / Skin / Masked Group",
        "blocker_2": "Character / Details / Instance",
        "cleared_title": "Flow cleared",
        "cleared_subtitle": "The target remains ready",
    },
    "de": {
        "state": "Status", "width": "Breite", "empty": "Erster Start", "ready": "Bereit", "active": "Verflüssigen", "repair": "Reparatur nötig", "blocked": "Anwenden blockiert", "complete": "Angewendet", "narrow": "Schmal", "standard": "Standard", "wide": "Breit",
        "target_none": "Keine Verflüssigungsziele", "target_folder": "Ordner · Charakter", "target_set": "Ebenenset 01 · 3 Ebenen",
        "empty_title": "Kein Verflüssigungsziel", "empty_subtitle": "Die aktuelle Auswahl kann ein Ziel werden.", "ready_title": "Bereit · Ordner · Charakter", "ready_subtitle": "3 Ebenen bereit zum Anwenden", "active_title": "Verflüssigung aktiv · Charakter", "active_subtitle": "Flow-Malerei · 3 Ebenen bereit", "active_brief": "Verflüssigung aktiv", "repair_title": "Zielstruktur muss repariert werden", "repair_subtitle": "Verwaltete Ebenen sind unvollständig", "blocked_title": "Anwenden ist blockiert", "blocked_subtitle": "2 Ebenenstrukturen benötigen Aufmerksamkeit", "complete_title": "Auf 3 Ebenen angewendet", "complete_subtitle": "Das Ziel wurde sicher entfernt",
        "create": "Ziel aus Auswahl erstellen", "start": "Verflüssigen starten", "return": "Zurück zum Malen", "repair_start": "Reparieren und starten", "repair_action": "Reparieren", "view": "Anzeigen", "hide": "Ausblenden", "apply": "Anwenden", "clear": "Flow leeren", "add_members": "Ausgewählte Ebenen hinzufügen", "remove_members": "Ausgewählte Ebenen entfernen", "delete_target": "Ziel löschen", "copy_diagnostics": "Diagnose kopieren", "new_target_tip": "Neues Ziel aus der aktuellen Auswahl erstellen", "refresh_tip": "Verflüssigungsziele aktualisieren", "repair_tip": "Ausgewähltes Ziel reparieren", "more_tip": "Zielaktionen", "mode_tip": "Modi und 3D/UV-Ausrichtung bleiben in Painter Assets.", "blockers": "Blockierende Strukturen", "blocker_1": "Charakter / Haut / Maskierte Gruppe", "blocker_2": "Charakter / Details / Instanz", "cleared_title": "Flow geleert", "cleared_subtitle": "Das Ziel bleibt bereit",
    },
    "es": {
        "state": "Estado", "width": "Ancho", "empty": "Primer uso", "ready": "Listo", "active": "Licuar", "repair": "Requiere reparación", "blocked": "Aplicación bloqueada", "complete": "Aplicado", "narrow": "Estrecho", "standard": "Estándar", "wide": "Ancho",
        "target_none": "Sin objetivos de Licuar", "target_folder": "Carpeta · Personaje", "target_set": "Conjunto 01 · 3 capas", "empty_title": "Sin objetivo de Licuar", "empty_subtitle": "La selección actual puede convertirse en objetivo.", "ready_title": "Listo · Carpeta · Personaje", "ready_subtitle": "3 capas listas para aplicar", "active_title": "Licuar activo · Personaje", "active_subtitle": "Pintura de Flow · 3 capas listas", "active_brief": "Licuar activo", "repair_title": "La estructura necesita reparación", "repair_subtitle": "Las capas gestionadas están incompletas", "blocked_title": "Aplicar está bloqueado", "blocked_subtitle": "2 estructuras requieren atención", "complete_title": "Aplicado a 3 capas", "complete_subtitle": "El objetivo se eliminó de forma segura", "create": "Crear objetivo desde la selección", "start": "Iniciar Licuar", "return": "Volver a pintar", "repair_start": "Reparar e iniciar", "repair_action": "Reparar", "view": "Ver", "hide": "Ocultar", "apply": "Aplicar", "clear": "Borrar Flow", "add_members": "Añadir capas seleccionadas", "remove_members": "Quitar capas seleccionadas", "delete_target": "Eliminar objetivo", "copy_diagnostics": "Copiar diagnóstico", "new_target_tip": "Crear un objetivo desde la selección actual", "refresh_tip": "Actualizar objetivos", "repair_tip": "Reparar el objetivo seleccionado", "more_tip": "Acciones del objetivo", "mode_tip": "Los modos y la alineación 3D/UV permanecen en Assets.", "blockers": "Estructuras bloqueantes", "blocker_1": "Personaje / Piel / Grupo con máscara", "blocker_2": "Personaje / Detalles / Instancia", "cleared_title": "Flow borrado", "cleared_subtitle": "El objetivo sigue listo",
    },
    "fr": {
        "state": "État", "width": "Largeur", "empty": "Première utilisation", "ready": "Prêt", "active": "Liquify actif", "repair": "Réparation requise", "blocked": "Application bloquée", "complete": "Appliqué", "narrow": "Étroit", "standard": "Standard", "wide": "Large",
        "target_none": "Aucune cible Liquify", "target_folder": "Dossier · Personnage", "target_set": "Jeu de calques 01 · 3 calques", "empty_title": "Aucune cible Liquify", "empty_subtitle": "La sélection actuelle peut devenir une cible.", "ready_title": "Prêt · Dossier · Personnage", "ready_subtitle": "3 calques prêts à être appliqués", "active_title": "Liquify actif · Personnage", "active_subtitle": "Peinture Flow · 3 calques prêts", "active_brief": "Liquify actif", "repair_title": "La structure doit être réparée", "repair_subtitle": "Les calques gérés sont incomplets", "blocked_title": "L’application est bloquée", "blocked_subtitle": "2 structures nécessitent votre attention", "complete_title": "Appliqué à 3 calques", "complete_subtitle": "La cible a été supprimée en sécurité", "create": "Créer une cible depuis la sélection", "start": "Démarrer Liquify", "return": "Retour à la peinture", "repair_start": "Réparer et démarrer", "repair_action": "Réparer", "view": "Afficher", "hide": "Masquer", "apply": "Appliquer", "clear": "Effacer le Flow", "add_members": "Ajouter les calques sélectionnés", "remove_members": "Retirer les calques sélectionnés", "delete_target": "Supprimer la cible", "copy_diagnostics": "Copier le diagnostic", "new_target_tip": "Créer une cible depuis la sélection actuelle", "refresh_tip": "Actualiser les cibles", "repair_tip": "Réparer la cible sélectionnée", "more_tip": "Actions de la cible", "mode_tip": "Les modes et l’alignement 3D/UV restent dans Assets.", "blockers": "Structures bloquantes", "blocker_1": "Personnage / Peau / Groupe masqué", "blocker_2": "Personnage / Détails / Instance", "cleared_title": "Flow effacé", "cleared_subtitle": "La cible reste prête",
    },
    "it": {
        "state": "Stato", "width": "Larghezza", "empty": "Primo utilizzo", "ready": "Pronto", "active": "Liquify attivo", "repair": "Riparazione necessaria", "blocked": "Applicazione bloccata", "complete": "Applicato", "narrow": "Stretto", "standard": "Standard", "wide": "Largo",
        "target_none": "Nessun obiettivo Liquify", "target_folder": "Cartella · Personaggio", "target_set": "Set livelli 01 · 3 livelli", "empty_title": "Nessun obiettivo Liquify", "empty_subtitle": "La selezione corrente può diventare un obiettivo.", "ready_title": "Pronto · Cartella · Personaggio", "ready_subtitle": "3 livelli pronti per l’applicazione", "active_title": "Liquify attivo · Personaggio", "active_subtitle": "Pittura Flow · 3 livelli pronti", "active_brief": "Liquify attivo", "repair_title": "La struttura richiede riparazione", "repair_subtitle": "I livelli gestiti sono incompleti", "blocked_title": "Applicazione bloccata", "blocked_subtitle": "2 strutture richiedono attenzione", "complete_title": "Applicato a 3 livelli", "complete_subtitle": "L’obiettivo è stato rimosso in sicurezza", "create": "Crea obiettivo dalla selezione", "start": "Avvia Liquify", "return": "Torna alla pittura", "repair_start": "Ripara e avvia", "repair_action": "Ripara", "view": "Mostra", "hide": "Nascondi", "apply": "Applica", "clear": "Cancella Flow", "add_members": "Aggiungi livelli selezionati", "remove_members": "Rimuovi livelli selezionati", "delete_target": "Elimina obiettivo", "copy_diagnostics": "Copia diagnostica", "new_target_tip": "Crea un obiettivo dalla selezione corrente", "refresh_tip": "Aggiorna obiettivi", "repair_tip": "Ripara l’obiettivo selezionato", "more_tip": "Azioni obiettivo", "mode_tip": "Modalità e allineamento 3D/UV restano in Assets.", "blockers": "Strutture bloccanti", "blocker_1": "Personaggio / Pelle / Gruppo mascherato", "blocker_2": "Personaggio / Dettagli / Istanza", "cleared_title": "Flow cancellato", "cleared_subtitle": "L’obiettivo resta pronto",
    },
    "ja_JP": {
        "state": "状態", "width": "幅", "empty": "初回", "ready": "準備完了", "active": "リキファイ中", "repair": "修復が必要", "blocked": "適用不可", "complete": "適用済み", "narrow": "狭い", "standard": "標準", "wide": "広い",
        "target_none": "リキファイターゲットなし", "target_folder": "フォルダー · キャラクター", "target_set": "レイヤーセット 01 · 3レイヤー", "empty_title": "リキファイターゲットなし", "empty_subtitle": "現在の選択からターゲットを作成できます。", "ready_title": "準備完了 · キャラクター", "ready_subtitle": "3レイヤーを適用可能", "active_title": "リキファイ中 · キャラクター", "active_subtitle": "Flowペイント · 3レイヤー準備完了", "active_brief": "リキファイ中", "repair_title": "ターゲット構造の修復が必要", "repair_subtitle": "管理レイヤーが不完全です", "blocked_title": "適用できません", "blocked_subtitle": "2つの構造を確認してください", "complete_title": "3レイヤーに適用済み", "complete_subtitle": "ターゲットは安全に削除されました", "create": "選択からターゲットを作成", "start": "リキファイ開始", "return": "ペイントに戻る", "repair_start": "修復して開始", "repair_action": "修復", "view": "表示", "hide": "隠す", "apply": "適用", "clear": "Flowを消去", "add_members": "選択レイヤーを追加", "remove_members": "選択レイヤーを削除", "delete_target": "ターゲットを削除", "copy_diagnostics": "診断をコピー", "new_target_tip": "現在の選択から新規ターゲットを作成", "refresh_tip": "ターゲットを更新", "repair_tip": "選択ターゲットを修復", "more_tip": "ターゲット操作", "mode_tip": "モードと3D/UV配置はAssetsで選択します。", "blockers": "ブロックしている構造", "blocker_1": "キャラクター / スキン / マスクグループ", "blocker_2": "キャラクター / ディテール / インスタンス", "cleared_title": "Flowを消去しました", "cleared_subtitle": "ターゲットは準備完了です",
    },
    "ko": {
        "state": "상태", "width": "너비", "empty": "처음 사용", "ready": "준비됨", "active": "리퀴파이 중", "repair": "복구 필요", "blocked": "적용 차단", "complete": "적용됨", "narrow": "좁게", "standard": "표준", "wide": "넓게",
        "target_none": "Liquify 대상 없음", "target_folder": "폴더 · 캐릭터", "target_set": "레이어 세트 01 · 3개", "empty_title": "Liquify 대상 없음", "empty_subtitle": "현재 선택으로 대상을 만들 수 있습니다.", "ready_title": "준비됨 · 폴더 · 캐릭터", "ready_subtitle": "3개 레이어 적용 준비", "active_title": "Liquify 활성 · 캐릭터", "active_subtitle": "Flow 페인팅 · 3개 레이어 준비", "active_brief": "Liquify 활성", "repair_title": "대상 구조 복구 필요", "repair_subtitle": "관리 레이어가 완전하지 않습니다", "blocked_title": "적용할 수 없음", "blocked_subtitle": "2개 구조를 확인해야 합니다", "complete_title": "3개 레이어에 적용됨", "complete_subtitle": "대상이 안전하게 제거되었습니다", "create": "선택에서 대상 만들기", "start": "Liquify 시작", "return": "페인팅으로 돌아가기", "repair_start": "복구 후 시작", "repair_action": "복구", "view": "보기", "hide": "숨기기", "apply": "적용", "clear": "Flow 지우기", "add_members": "선택 레이어 추가", "remove_members": "선택 레이어 제거", "delete_target": "대상 삭제", "copy_diagnostics": "진단 복사", "new_target_tip": "현재 선택에서 새 대상 만들기", "refresh_tip": "대상 새로 고침", "repair_tip": "선택한 대상 복구", "more_tip": "대상 작업", "mode_tip": "모드와 3D/UV 정렬은 Painter Assets에 유지됩니다.", "blockers": "차단 구조", "blocker_1": "캐릭터 / 스킨 / 마스크 그룹", "blocker_2": "캐릭터 / 디테일 / 인스턴스", "cleared_title": "Flow를 지웠습니다", "cleared_subtitle": "대상은 준비 상태입니다",
    },
    "pt": {
        "state": "Estado", "width": "Largura", "empty": "Primeiro uso", "ready": "Pronto", "active": "Liquify ativo", "repair": "Reparo necessário", "blocked": "Aplicação bloqueada", "complete": "Aplicado", "narrow": "Estreito", "standard": "Padrão", "wide": "Largo",
        "target_none": "Sem alvos do Liquify", "target_folder": "Pasta · Personagem", "target_set": "Conjunto 01 · 3 camadas", "empty_title": "Sem alvo do Liquify", "empty_subtitle": "A seleção atual pode se tornar um alvo.", "ready_title": "Pronto · Pasta · Personagem", "ready_subtitle": "3 camadas prontas para aplicar", "active_title": "Liquify ativo · Personagem", "active_subtitle": "Pintura Flow · 3 camadas prontas", "active_brief": "Liquify ativo", "repair_title": "A estrutura precisa de reparo", "repair_subtitle": "As camadas gerenciadas estão incompletas", "blocked_title": "Aplicação bloqueada", "blocked_subtitle": "2 estruturas precisam de atenção", "complete_title": "Aplicado em 3 camadas", "complete_subtitle": "O alvo foi removido com segurança", "create": "Criar alvo da seleção", "start": "Iniciar Liquify", "return": "Voltar à pintura", "repair_start": "Reparar e iniciar", "repair_action": "Reparar", "view": "Ver", "hide": "Ocultar", "apply": "Aplicar", "clear": "Limpar Flow", "add_members": "Adicionar camadas selecionadas", "remove_members": "Remover camadas selecionadas", "delete_target": "Excluir alvo", "copy_diagnostics": "Copiar diagnóstico", "new_target_tip": "Criar alvo da seleção atual", "refresh_tip": "Atualizar alvos", "repair_tip": "Reparar o alvo selecionado", "more_tip": "Ações do alvo", "mode_tip": "Os modos e o alinhamento 3D/UV permanecem em Assets.", "blockers": "Estruturas bloqueadoras", "blocker_1": "Personagem / Pele / Grupo com máscara", "blocker_2": "Personagem / Detalhes / Instância", "cleared_title": "Flow limpo", "cleared_subtitle": "O alvo continua pronto",
    },
    "zh_CN": {
        "state": "状态", "width": "宽度", "empty": "首次使用", "ready": "已就绪", "active": "液化中", "repair": "需要修复", "blocked": "应用受阻", "complete": "应用完成", "narrow": "窄", "standard": "标准", "wide": "宽",
        "target_none": "尚无液化目标", "target_folder": "文件夹 · 角色", "target_set": "图层集 01 · 3 层", "empty_title": "尚无液化目标", "empty_subtitle": "当前选择可以创建为目标", "ready_title": "已就绪 · 文件夹 · 角色", "ready_subtitle": "3 层可以安全应用", "active_title": "液化中 · 文件夹 · 角色", "active_subtitle": "正在绘制 Flow · 3 层已就绪", "active_brief": "液化中", "repair_title": "目标结构需要修复", "repair_subtitle": "托管图层结构不完整", "blocked_title": "暂时不能应用", "blocked_subtitle": "有 2 个图层结构需要处理", "complete_title": "已应用到 3 个图层", "complete_subtitle": "目标已安全移除", "create": "从选择创建目标", "start": "开始液化", "return": "返回绘画", "repair_start": "修复并开始", "repair_action": "修复", "view": "查看", "hide": "收起", "apply": "应用", "clear": "清空 Flow", "add_members": "加入所选图层", "remove_members": "移除所选图层", "delete_target": "删除目标", "copy_diagnostics": "复制诊断", "new_target_tip": "从当前选择创建新目标", "refresh_tip": "刷新液化目标", "repair_tip": "修复当前目标", "more_tip": "目标操作", "mode_tip": "液化模式和 3D/UV 对齐继续由 Painter Assets 管理。", "blockers": "阻塞结构", "blocker_1": "角色 / 皮肤 / 带遮罩文件夹", "blocker_2": "角色 / 细节 / 实例图层", "cleared_title": "Flow 已清空", "cleared_subtitle": "目标仍处于就绪状态",
    },
}

_COMPACT_CREATE_TEXT = {
    "en": "Create Target",
    "de": "Ziel erstellen",
    "es": "Crear objetivo",
    "fr": "Créer la cible",
    "it": "Crea obiettivo",
    "ja_JP": "ターゲット作成",
    "ko": "대상 만들기",
    "pt": "Criar alvo",
    "zh_CN": "创建目标",
}

_V2_PRIMARY_TEXT = {
    "en": {"start": "Start Liquify", "return": "Back to Paint", "repair_start": "Repair & Start"},
    "de": {"start": "Liquify starten", "return": "Zurück zum Malen", "repair_start": "Reparieren"},
    "es": {"start": "Iniciar Liquify", "return": "Volver a pintar", "repair_start": "Reparar e iniciar"},
    "fr": {"start": "Lancer Liquify", "return": "Retour peinture", "repair_start": "Réparer et lancer"},
    "it": {"start": "Avvia Liquify", "return": "Torna a dipingere", "repair_start": "Ripara e avvia"},
    "ja_JP": {"start": "リキファイ開始", "return": "ペイントに戻る", "repair_start": "修復して開始"},
    "ko": {"start": "Liquify 시작", "return": "페인팅으로 돌아가기", "repair_start": "복구 후 시작"},
    "pt": {"start": "Iniciar Liquify", "return": "Voltar à pintura", "repair_start": "Reparar e iniciar"},
    "zh_CN": {"start": "开始液化", "return": "返回绘画", "repair_start": "修复并开始"},
}


def _language() -> str:
    app = QtWidgets.QApplication.instance()
    return str(app.property("rizumPreviewLanguage") or "en") if app else "en"


def _text(key: str) -> str:
    language = _language()
    if key == "create":
        return _COMPACT_CREATE_TEXT.get(language, _COMPACT_CREATE_TEXT["en"])
    return _TEXT.get(language, _TEXT["en"]).get(key, _TEXT["en"][key])


def _v2_primary_text(key: str) -> str:
    language = _language()
    return _V2_PRIMARY_TEXT.get(language, _V2_PRIMARY_TEXT["en"]).get(
        key,
        _text(key),
    )


def _set_combo_items(combo, has_target: bool) -> None:
    blocker = QtCore.QSignalBlocker(combo)
    combo.clear()
    if has_target:
        combo.addItem(_text("target_folder"), "folder")
        combo.addItem(_text("target_set"), "set")
        combo.setEnabled(True)
    else:
        combo.addItem(_text("target_none"), None)
        combo.setEnabled(False)
    del blocker


def _make_blocker_details(parent):
    frame = QtWidgets.QFrame(parent)
    frame.setObjectName("RizumLiquifyBlockers")
    layout = QtWidgets.QVBoxLayout(frame)
    layout.setContentsMargins(10, 8, 10, 8)
    layout.setSpacing(4)
    title = QtWidgets.QLabel(_text("blockers"), frame)
    title.setObjectName("RizumLiquifyBlockerTitle")
    layout.addWidget(title)
    labels = []
    for key in ("blocker_1", "blocker_2"):
        label = QtWidgets.QLabel(_text(key), frame)
        label.setObjectName("RizumLiquifyBlockerPath")
        label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Ignored,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        layout.addWidget(label)
        labels.append(label)
    frame.setStyleSheet(
        """
QFrame#RizumLiquifyBlockers {
    background: #202020;
    border: 0;
    border-radius: 6px;
}
QLabel#RizumLiquifyBlockerTitle {
    color: #d69a38;
    font-weight: 600;
    background: transparent;
    border: 0;
}
QLabel#RizumLiquifyBlockerPath {
    color: #9a9a9a;
    background: transparent;
    border: 0;
}
"""
    )
    frame.hide()
    return frame, labels


def _make_primary_button(parent) -> SecondaryActionButton:
    button = SecondaryActionButton(
        "",
        background=PAINTER_DIALOG_STYLE["accent"],
        hover_background=PAINTER_DIALOG_STYLE["accent_hover"],
        pressed_background=PAINTER_DIALOG_STYLE["accent_pressed"],
        text_color=PAINTER_DIALOG_STYLE["accent_text"],
        parent=parent,
    )
    button.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Fixed,
    )
    return button


class LiquifyPreviewPanel(QtWidgets.QWidget):
    stateChanged = QtCore.Signal(str)

    STATES = ("empty", "ready", "active", "repair", "blocked", "complete")
    BASE_WIDTHS = {"narrow": 250, "standard": 360, "wide": 440}

    def __init__(self, state: str = "ready", width_mode: str = "standard", parent=None):
        super().__init__(parent)
        self._state = "ready"
        self._width_mode = width_mode
        self._blockers_expanded = False
        self._restore_state = "ready"
        self._restore_timer = QtCore.QTimer(self)
        self._restore_timer.setSingleShot(True)
        self._restore_timer.timeout.connect(
            lambda: self.setState(self._restore_state)
        )

        apply_compact_dock_surface(self)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        outer = make_compact_dock_layout(self)
        self._card = make_compact_dock_card(self)
        self._card_layout = self._card.layout()
        self._card_layout.setContentsMargins(0, 0, 0, 8)
        outer.addWidget(self._card)

        content = QtWidgets.QWidget(self._card)
        content.setObjectName("RizumTransparent")
        self._content_layout = QtWidgets.QVBoxLayout(content)
        self._content_layout.setContentsMargins(12, 12, 12, 6)
        self._content_layout.setSpacing(10)

        target_row = QtWidgets.QWidget(content)
        target_row.setObjectName("RizumTransparent")
        self._target_layout = QtWidgets.QHBoxLayout(target_row)
        self._target_layout.setContentsMargins(0, 0, 0, 0)
        self._target_layout.setSpacing(4)
        self.target_combo = make_combo_input()
        self.target_combo.setFitToContents(False)
        self.target_combo.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self._target_layout.addWidget(self.target_combo, 1)
        self.new_target_button = make_icon_button("plus.svg", _text("new_target_tip"))
        self.refresh_button = make_icon_button("refresh.svg", _text("refresh_tip"))
        self.repair_button = make_icon_button("wrench.svg", _text("repair_tip"))
        for button in (
            self.new_target_button,
            self.refresh_button,
            self.repair_button,
        ):
            self._target_layout.addWidget(button)
        self._content_layout.addWidget(target_row)

        self.status_banner = StatusBanner(parent=content)
        install_compact_tooltip(self.status_banner, _text("mode_tip"))
        self._content_layout.addWidget(self.status_banner)

        self.blocker_details, self._blocker_labels = _make_blocker_details(content)
        self._content_layout.addWidget(self.blocker_details)

        self.primary_button = _make_primary_button(content)
        self._content_layout.addWidget(self.primary_button)
        self._card_layout.addWidget(content)
        self._card_layout.addWidget(make_inset_separator(12, 1))

        self._footer = QtWidgets.QWidget(self._card)
        self._footer.setObjectName("RizumTransparent")
        self._footer_layout = QtWidgets.QHBoxLayout(self._footer)
        self._footer_layout.setContentsMargins(10, 0, 10, 0)
        self._footer_layout.setSpacing(8)
        self.apply_button = AnimatedSaveButton(_text("apply"), parent=self._footer)
        self.apply_button.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.clear_button = TextActionButton(
            _text("clear"),
            muted=PAINTER_DIALOG_STYLE["faint"],
            parent=self._footer,
        )
        self.more_button = make_icon_button("ellipsis.svg", _text("more_tip"))
        self._footer_layout.addWidget(self.apply_button, 1)
        self._footer_layout.addWidget(self.clear_button)
        self._footer_layout.addWidget(self.more_button)
        self._card_layout.addWidget(self._footer)

        self._menu = QtWidgets.QMenu(self)
        self._menu.setObjectName("RizumPopupMenu")
        self._add_action = self._menu.addAction(_text("add_members"))
        self._remove_action = self._menu.addAction(_text("remove_members"))
        self._menu.addSeparator()
        self._delete_action = self._menu.addAction(_text("delete_target"))
        self._copy_action = self._menu.addAction(_text("copy_diagnostics"))

        self.new_target_button.clicked.connect(lambda: self.setState("active"))
        self.refresh_button.clicked.connect(lambda: self.setState(self._state))
        self.repair_button.clicked.connect(lambda: self.setState("active"))
        self.primary_button.clicked.connect(self._primary_action)
        self.status_banner.actionTriggered.connect(self._banner_action)
        self.apply_button.clicked.connect(self._apply)
        self.clear_button.clicked.connect(self._clear_flow)
        self.more_button.clicked.connect(self._show_menu)
        self._delete_action.triggered.connect(lambda: self.setState("empty"))
        self.setState(state, emit=False)
        self.refreshMetrics()

    def state(self) -> str:
        return self._state

    def widthMode(self) -> str:
        return self._width_mode

    def setWidthMode(self, mode: str) -> None:
        self._width_mode = mode if mode in self.BASE_WIDTHS else "standard"
        self.refreshMetrics()

    def setState(self, state: str, *, emit: bool = True) -> None:
        state = state if state in self.STATES else "ready"
        self._restore_timer.stop()
        self._state = state
        has_target = state not in {"empty", "complete"}
        _set_combo_items(self.target_combo, has_target)
        self._blockers_expanded = False
        self.blocker_details.hide()
        self.repair_button.setEnabled(state == "repair")
        self.repair_button.setProperty("accent", state == "repair")
        self.clear_button.setEnabled(has_target)
        self.more_button.setEnabled(has_target)
        self._add_action.setEnabled(has_target)
        self._remove_action.setEnabled(has_target)
        self._delete_action.setEnabled(has_target)
        can_apply = state in {"ready", "active"}
        self.apply_button.setDirty(can_apply, animate=False)

        if state == "empty":
            banner = ("empty_title", "empty_subtitle", "neutral", "")
            primary = "create"
        elif state == "ready":
            banner = ("ready_title", "ready_subtitle", "good", "")
            primary = "start"
        elif state == "active":
            banner = ("active_title", "active_subtitle", "accent", "")
            primary = "return"
        elif state == "repair":
            banner = ("repair_title", "repair_subtitle", "warn", "repair_action")
            primary = "repair_start"
        elif state == "blocked":
            banner = ("blocked_title", "blocked_subtitle", "warn", "view")
            primary = "start"
        else:
            banner = ("complete_title", "complete_subtitle", "good", "")
            primary = "create"

        self.status_banner.setStatus(
            _text(banner[0]),
            _text(banner[1]),
            banner[2],
            _text(banner[3]) if banner[3] else "",
        )
        self.primary_button.setText(_text(primary))
        self.refreshMetrics()
        if emit:
            self.stateChanged.emit(state)

    def _primary_action(self) -> None:
        transitions = {
            "empty": "active",
            "ready": "active",
            "active": "ready",
            "repair": "active",
            "blocked": "active",
            "complete": "active",
        }
        self.setState(transitions[self._state])

    def _banner_action(self) -> None:
        if self._state == "repair":
            self.setState("active")
            return
        if self._state != "blocked":
            return
        self._blockers_expanded = not self._blockers_expanded
        self.blocker_details.setVisible(self._blockers_expanded)
        self.status_banner.setStatus(
            _text("blocked_title"),
            _text("blocked_subtitle"),
            "warn",
            _text("hide" if self._blockers_expanded else "view"),
        )
        self._resize_to_content()

    def _apply(self) -> None:
        if not self.apply_button.isEnabled():
            return
        self.apply_button.showSavedFeedback()
        QtCore.QTimer.singleShot(520, lambda: self.setState("complete"))

    def _clear_flow(self) -> None:
        if not self.clear_button.isEnabled():
            return
        self._restore_state = self._state
        self.status_banner.setStatus(
            _text("cleared_title"),
            _text("cleared_subtitle"),
            "good",
        )
        self._restore_timer.start(900)

    def _show_menu(self) -> None:
        position = self.more_button.mapToGlobal(self.more_button.rect().bottomRight())
        self._menu.popup(position)

    def refreshMetrics(self) -> None:
        app = QtWidgets.QApplication.instance()
        scale = float(app.property("rizumUiFontScale") or 1.0) if app else 1.0

        def metric(value: int, minimum: int | None = None) -> int:
            result = int(round(value * scale))
            return max(minimum, result) if minimum is not None else result

        self.setFixedWidth(max(250, metric(self.BASE_WIDTHS[self._width_mode])))
        row_height = metric(32, 24)
        self.target_combo.setCompactHeight(row_height)
        self.target_combo.setMinimumWidth(metric(88, 66))
        self._target_layout.setSpacing(metric(4, 3))
        icon_frame = metric(22, 17)
        icon_size = metric(16, 12)
        for button in (
            self.new_target_button,
            self.refresh_button,
            self.repair_button,
            self.more_button,
        ):
            button.setFixedSize(icon_frame, icon_frame)
            button.setPaintedIconSize(icon_size)
            if hasattr(button, "setCompactTooltipScale"):
                button.setCompactTooltipScale(scale)

        self._card_layout.setContentsMargins(0, 0, 0, metric(8, 6))
        self._content_layout.setContentsMargins(
            metric(12, 9), metric(12, 9), metric(12, 9), metric(6, 4)
        )
        self._content_layout.setSpacing(metric(10, 8))
        self.status_banner.setCompactHeight(metric(54, 41))
        action_height = metric(28, 21)
        self.primary_button.setCompactHeight(action_height)
        self.apply_button.setCompactHeight(action_height)
        self.clear_button.setCompactHeight(action_height)
        footer_height = metric(48, 36)
        self._footer.setFixedHeight(footer_height)
        footer_margin = metric(10, 8)
        self._footer_layout.setContentsMargins(footer_margin, 0, footer_margin, 0)
        self._footer_layout.setSpacing(metric(8, 6))
        self._resize_to_content()

    def _resize_to_content(self) -> None:
        for layout in (
            self._content_layout,
            self._card_layout,
            self.layout(),
        ):
            layout.invalidate()
            layout.activate()
        self.setFixedHeight(self.sizeHint().height())
        self.updateGeometry()


class LiquifyPreviewPanelV2(QtWidgets.QWidget):
    """Kimi K3 V2 comparison panel: same workflow, lower default density.

    Decisions a refactor should not undo:
    - "ready" shows no banner; the combo, the enabled Apply button, and the
      Start Liquify action already carry that state. The banner only appears
      when it adds information (empty/active/repair/blocked/complete, or a
      transient clear-flow confirmation).
    - Refresh, repair, member maintenance, Clear Flow, and diagnostics live
      in one target menu; only target creation keeps a permanent icon.
    - Repair has a single path (the primary action), matching the real
      plugin's one repair entry point instead of three overlapping ones.
    """

    stateChanged = QtCore.Signal(str)

    STATES = LiquifyPreviewPanel.STATES
    BASE_WIDTHS = LiquifyPreviewPanel.BASE_WIDTHS

    def __init__(self, state: str = "ready", width_mode: str = "standard", parent=None):
        super().__init__(parent)
        self._state = "ready"
        self._width_mode = width_mode
        self._blockers_expanded = False
        self._restore_state = "ready"
        self._restore_timer = QtCore.QTimer(self)
        self._restore_timer.setSingleShot(True)
        self._restore_timer.timeout.connect(
            lambda: self.setState(self._restore_state)
        )

        apply_compact_dock_surface(self)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        outer = make_compact_dock_layout(self)
        self._card = make_compact_dock_card(self)
        self._card_layout = self._card.layout()
        self._card_layout.setContentsMargins(0, 0, 0, 8)
        outer.addWidget(self._card)

        content = QtWidgets.QWidget(self._card)
        content.setObjectName("RizumTransparent")
        self._content_layout = QtWidgets.QVBoxLayout(content)
        self._content_layout.setContentsMargins(12, 12, 12, 6)
        self._content_layout.setSpacing(10)

        target_row = QtWidgets.QWidget(content)
        target_row.setObjectName("RizumTransparent")
        self._target_layout = QtWidgets.QHBoxLayout(target_row)
        self._target_layout.setContentsMargins(0, 0, 0, 0)
        self._target_layout.setSpacing(4)
        self.target_combo = make_combo_input()
        self.target_combo.setFitToContents(False)
        self.target_combo.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self._target_layout.addWidget(self.target_combo, 1)
        self.new_target_button = make_icon_button("plus.svg", _text("new_target_tip"))
        self.more_button = make_icon_button("ellipsis.svg", _text("more_tip"))
        self._target_layout.addWidget(self.new_target_button)
        self._target_layout.addWidget(self.more_button)
        self._content_layout.addWidget(target_row)

        self.status_banner = StatusBanner(parent=content)
        self._content_layout.addWidget(self.status_banner)

        self.blocker_details, self._blocker_labels = _make_blocker_details(content)
        self._content_layout.addWidget(self.blocker_details)

        self.primary_button = _make_primary_button(content)
        self._content_layout.addWidget(self.primary_button)
        self._card_layout.addWidget(content)
        self._card_layout.addWidget(make_inset_separator(12, 1))

        self._footer = QtWidgets.QWidget(self._card)
        self._footer.setObjectName("RizumTransparent")
        self._footer_layout = QtWidgets.QHBoxLayout(self._footer)
        self._footer_layout.setContentsMargins(10, 0, 10, 0)
        self._footer_layout.setSpacing(8)
        self.apply_button = AnimatedSaveButton(_text("apply"), parent=self._footer)
        self.apply_button.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self._footer_layout.addWidget(self.apply_button, 1)
        self._card_layout.addWidget(self._footer)

        self._menu = QtWidgets.QMenu(self)
        self._menu.setObjectName("RizumPopupMenu")
        self._refresh_action = self._menu.addAction(_text("refresh_tip"))
        self._repair_action = self._menu.addAction(_text("repair_action"))
        self._menu.addSeparator()
        self._add_action = self._menu.addAction(_text("add_members"))
        self._remove_action = self._menu.addAction(_text("remove_members"))
        self._delete_action = self._menu.addAction(_text("delete_target"))
        self._menu.addSeparator()
        self._clear_action = self._menu.addAction(_text("clear"))
        self._copy_action = self._menu.addAction(_text("copy_diagnostics"))

        self.new_target_button.clicked.connect(lambda: self.setState("active"))
        self.more_button.clicked.connect(self._show_menu)
        self.primary_button.clicked.connect(self._primary_action)
        self.status_banner.actionTriggered.connect(self._banner_action)
        self.apply_button.clicked.connect(self._apply)
        self._refresh_action.triggered.connect(lambda: self.setState(self._state))
        self._repair_action.triggered.connect(lambda: self.setState("active"))
        self._delete_action.triggered.connect(lambda: self.setState("empty"))
        self._clear_action.triggered.connect(self._clear_flow)
        self._menu.aboutToShow.connect(self._sync_menu_actions)
        self.setState(state, emit=False)
        self.refreshMetrics()

    def state(self) -> str:
        return self._state

    def widthMode(self) -> str:
        return self._width_mode

    def setWidthMode(self, mode: str) -> None:
        self._width_mode = mode if mode in self.BASE_WIDTHS else "standard"
        self.refreshMetrics()

    def setState(self, state: str, *, emit: bool = True) -> None:
        state = state if state in self.STATES else "ready"
        self._restore_timer.stop()
        self._state = state
        has_target = state not in {"empty", "complete"}
        _set_combo_items(self.target_combo, has_target)
        self._blockers_expanded = False
        self.blocker_details.hide()
        self._sync_menu_actions()
        can_apply = state in {"ready", "active"}
        self.apply_button.setDirty(can_apply, animate=False)

        if state == "empty":
            banner = ("empty_title", "empty_subtitle", "neutral", "")
            primary = "create"
        elif state == "ready":
            banner = None
            primary = "start"
        elif state == "active":
            banner = ("active_brief", "mode_tip", "accent", "")
            primary = "return"
        elif state == "repair":
            banner = ("repair_title", "repair_subtitle", "warn", "")
            primary = "repair_start"
        elif state == "blocked":
            banner = ("blocked_title", "blocked_subtitle", "warn", "view")
            primary = "start"
        else:
            banner = ("complete_title", "complete_subtitle", "good", "")
            primary = "create"

        if banner is None:
            self.status_banner.hide()
        else:
            self.status_banner.setStatus(
                _text(banner[0]),
                _text(banner[1]),
                banner[2],
                _text(banner[3]) if banner[3] else "",
            )
            self.status_banner.show()
        self.primary_button.setText(_v2_primary_text(primary))
        self.refreshMetrics()
        if emit:
            self.stateChanged.emit(state)

    def _sync_menu_actions(self) -> None:
        has_target = self._state not in {"empty", "complete"}
        # Member maintenance only exists for layer-set targets in the real
        # plugin; folder targets expose repair/clear but not membership.
        is_set = has_target and self.target_combo.currentData() == "set"
        self._repair_action.setEnabled(has_target)
        self._add_action.setEnabled(is_set)
        self._remove_action.setEnabled(is_set)
        self._delete_action.setEnabled(is_set)
        self._clear_action.setEnabled(has_target)

    def _primary_action(self) -> None:
        transitions = {
            "empty": "active",
            "ready": "active",
            "active": "ready",
            "repair": "active",
            "blocked": "active",
            "complete": "active",
        }
        self.setState(transitions[self._state])

    def _banner_action(self) -> None:
        if self._state != "blocked":
            return
        self._blockers_expanded = not self._blockers_expanded
        self.blocker_details.setVisible(self._blockers_expanded)
        self.status_banner.setStatus(
            _text("blocked_title"),
            _text("blocked_subtitle"),
            "warn",
            _text("hide" if self._blockers_expanded else "view"),
        )
        self._resize_to_content()

    def _apply(self) -> None:
        if not self.apply_button.isEnabled():
            return
        self.apply_button.showSavedFeedback()
        QtCore.QTimer.singleShot(520, lambda: self.setState("complete"))

    def _clear_flow(self) -> None:
        if not self._clear_action.isEnabled():
            return
        self._restore_state = self._state
        self.status_banner.setStatus(
            _text("cleared_title"),
            _text("cleared_subtitle"),
            "good",
        )
        self.status_banner.show()
        self._resize_to_content()
        self._restore_timer.start(900)

    def _show_menu(self) -> None:
        position = self.more_button.mapToGlobal(self.more_button.rect().bottomRight())
        self._menu.popup(position)

    def refreshMetrics(self) -> None:
        app = QtWidgets.QApplication.instance()
        scale = float(app.property("rizumUiFontScale") or 1.0) if app else 1.0

        def metric(value: int, minimum: int | None = None) -> int:
            result = int(round(value * scale))
            return max(minimum, result) if minimum is not None else result

        self.setFixedWidth(max(250, metric(self.BASE_WIDTHS[self._width_mode])))
        row_height = metric(32, 24)
        self.target_combo.setCompactHeight(row_height)
        self.target_combo.setMinimumWidth(metric(88, 66))
        self._target_layout.setSpacing(metric(4, 3))
        icon_frame = metric(22, 17)
        icon_size = metric(16, 12)
        for button in (
            self.new_target_button,
            self.more_button,
        ):
            button.setFixedSize(icon_frame, icon_frame)
            button.setPaintedIconSize(icon_size)
            if hasattr(button, "setCompactTooltipScale"):
                button.setCompactTooltipScale(scale)

        self._card_layout.setContentsMargins(0, 0, 0, metric(8, 6))
        self._content_layout.setContentsMargins(
            metric(12, 9), metric(12, 9), metric(12, 9), metric(6, 4)
        )
        self._content_layout.setSpacing(metric(10, 8))
        self.status_banner.setCompactHeight(metric(54, 41))
        action_height = metric(28, 21)
        self.primary_button.setCompactHeight(action_height)
        self.apply_button.setCompactHeight(action_height)
        footer_height = metric(48, 36)
        self._footer.setFixedHeight(footer_height)
        footer_margin = metric(10, 8)
        self._footer_layout.setContentsMargins(footer_margin, 0, footer_margin, 0)
        self._footer_layout.setSpacing(metric(8, 6))
        self._resize_to_content()

    def _resize_to_content(self) -> None:
        for layout in (
            self._content_layout,
            self._card_layout,
            self.layout(),
        ):
            layout.invalidate()
            layout.activate()
        self.setFixedHeight(self.sizeHint().height())
        self.updateGeometry()


def build_liquify_preview(QtWidgets_module=None):
    del QtWidgets_module
    page = QtWidgets.QWidget()
    page.setObjectName("RizumLiquifyPreviewPage")
    page_layout = QtWidgets.QVBoxLayout(page)
    page_layout.setContentsMargins(0, 12, 0, 0)
    page_layout.setSpacing(12)

    controls = QtWidgets.QWidget(page)
    controls.setObjectName("RizumTransparent")
    controls_layout = QtWidgets.QHBoxLayout(controls)
    controls_layout.setContentsMargins(0, 0, 0, 0)
    controls_layout.setSpacing(8)
    controls_layout.addStretch(1)
    state_label = QtWidgets.QLabel(_text("state"), controls)
    state_label.setObjectName("RizumPreviewToolLabel")
    controls_layout.addWidget(state_label)
    state_control = make_combo_input(
        [(_text(key), key) for key in LiquifyPreviewPanel.STATES]
    )
    state_control.setCompactHeight(26)
    state_control.setCurrentIndex(state_control.findData("ready"))
    controls_layout.addWidget(state_control)
    width_label = QtWidgets.QLabel(_text("width"), controls)
    width_label.setObjectName("RizumPreviewToolLabel")
    controls_layout.addWidget(width_label)
    width_control = make_combo_input(
        [
            (_text("narrow"), "narrow"),
            (_text("standard"), "standard"),
            (_text("wide"), "wide"),
        ]
    )
    width_control.setCompactHeight(26)
    width_control.setCurrentIndex(width_control.findData("standard"))
    controls_layout.addWidget(width_control)
    controls_layout.addStretch(1)
    page_layout.addWidget(controls)

    panels_host = QtWidgets.QWidget(page)
    panels_host.setObjectName("RizumTransparent")
    host_layout = QtWidgets.QHBoxLayout(panels_host)
    host_layout.setContentsMargins(0, 0, 0, 0)
    host_layout.setSpacing(16)
    host_layout.addStretch(1)

    codex_panel = LiquifyPreviewPanel()
    kimi_panel = LiquifyPreviewPanelV2()
    panels = (codex_panel, kimi_panel)
    for tag, panel in (("CODEX", codex_panel), ("KIMI K3 V2", kimi_panel)):
        column = QtWidgets.QWidget(panels_host)
        column.setObjectName("RizumTransparent")
        column_layout = QtWidgets.QVBoxLayout(column)
        column_layout.setContentsMargins(0, 0, 0, 0)
        column_layout.setSpacing(6)
        tag_label = QtWidgets.QLabel(tag, column)
        tag_label.setObjectName("RizumPreviewToolLabel")
        tag_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        column_layout.addWidget(tag_label)
        column_layout.addWidget(panel, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        host_layout.addWidget(column, 0, QtCore.Qt.AlignmentFlag.AlignTop)
    host_layout.addStretch(1)
    page_layout.addWidget(panels_host, 1)

    def select_state(_index: int) -> None:
        state = str(state_control.currentData() or "ready")
        for panel in panels:
            panel.setState(state, emit=False)

    def select_width(_index: int) -> None:
        mode = str(width_control.currentData() or "standard")
        for panel in panels:
            panel.setWidthMode(mode)

    def sync_state(state: str) -> None:
        index = state_control.findData(state)
        if index >= 0 and index != state_control.currentIndex():
            blocker = QtCore.QSignalBlocker(state_control)
            state_control.setCurrentIndex(index)
            del blocker
        for panel in panels:
            if panel.state() != state:
                panel.setState(state, emit=False)

    state_control.currentIndexChanged.connect(select_state)
    width_control.currentIndexChanged.connect(select_width)
    for panel in panels:
        panel.stateChanged.connect(sync_state)
    page._rizum_panel = codex_panel
    page._rizum_panel_v2 = kimi_panel
    page._rizum_state_control = state_control
    page._rizum_width_control = width_control
    return page


__all__ = ["LiquifyPreviewPanel", "LiquifyPreviewPanelV2", "build_liquify_preview"]
