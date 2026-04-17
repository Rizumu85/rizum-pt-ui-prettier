import substance_painter as sp
from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QApplication, QProgressDialog

from . import sdf_bake
from . import sdf_layer_setup
from . import sdf_frame_ops
from . import sdf_external


_dock = None
_panel = None


class SDFPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.selected_frame_uid = None
        self._last_stack_key = None
        self.target_group = QtWidgets.QButtonGroup(self)
        self.target_group.setExclusive(True)
        metrics = QFontMetrics(self.font())
        self.frame_name_width = metrics.horizontalAdvance("Frame_99") + 4
        self.frame_percent_width = metrics.horizontalAdvance("[100%]") + 2
        layout = QtWidgets.QVBoxLayout(self)

        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel("Frames:"))
        self.frame_count = QtWidgets.QSpinBox()
        self.frame_count.setRange(2, 32)
        self.frame_count.setValue(9)
        row.addWidget(self.frame_count)
        layout.addLayout(row)

        self.setup_btn = QtWidgets.QPushButton("Setup SDF Group")
        self.setup_btn.clicked.connect(self._on_setup)
        layout.addWidget(self.setup_btn)

        self.sync_btn = QtWidgets.QPushButton("Sync Values")
        self.sync_btn.clicked.connect(self._on_sync)
        layout.addWidget(self.sync_btn)

        self.add_btn = QtWidgets.QPushButton("+ Add Frame")
        self.add_btn.clicked.connect(self._on_add_frame)
        layout.addWidget(self.add_btn)

        self.borrow_btn = QtWidgets.QPushButton("⊕ Borrow Shape")
        self.borrow_btn.setToolTip(
            "Use the selected Painter layer as source and the selected frame row as target")
        self.borrow_btn.clicked.connect(self._on_borrow_shape)
        layout.addWidget(self.borrow_btn)

        self.bake_btn = QtWidgets.QPushButton("Bake SDF")
        self.bake_btn.setToolTip(
            "Export frames, run the SDF tool, and import SDF_Baked_Result")
        self.bake_btn.clicked.connect(self._on_bake_sdf)
        layout.addWidget(self.bake_btn)

        self.frame_list = QtWidgets.QVBoxLayout()
        layout.addLayout(self.frame_list)

        layout.addStretch()
        self._stack_poll_timer = QTimer(self)
        self._stack_poll_timer.setInterval(750)
        self._stack_poll_timer.timeout.connect(self._poll_active_stack)
        self._stack_poll_timer.start()
        self.refresh_frames()

    def refresh_frames(self):
        # clear existing rows
        while self.frame_list.count():
            item = self.frame_list.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        for button in self.target_group.buttons():
            self.target_group.removeButton(button)

        try:
            self._last_stack_key = self._get_active_stack_key()
            group = sdf_layer_setup._find_sdf_group()
        except Exception:
            self.frame_list.addWidget(
                QtWidgets.QLabel("(No project loaded)"))
            return
        if group is None:
            self.frame_list.addWidget(
                QtWidgets.QLabel("(No SDF_Generator group)"))
            return

        layers = list(group.sub_layers())
        if self.selected_frame_uid not in {layer.uid() for layer in layers}:
            self.selected_frame_uid = layers[0].uid() if layers else None

        for layer in layers:  # top-to-bottom
            row = QtWidgets.QWidget()
            row_layout = QtWidgets.QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            uid = layer.uid()

            target_btn = QtWidgets.QRadioButton()
            target_btn.setChecked(uid == self.selected_frame_uid)
            target_btn.setToolTip("Use this frame as the target for Borrow Shape")
            target_btn.setFixedWidth(16)
            self.target_group.addButton(target_btn)
            target_btn.toggled.connect(
                lambda checked, u=uid: self._on_target_frame_toggled(u, checked))
            row_layout.addWidget(target_btn)

            row_layout.setSpacing(2)
            frame_name, percent_text = self._split_frame_label(layer.get_name())

            name_label = QtWidgets.QLabel(frame_name)
            name_label.setFixedWidth(self.frame_name_width)
            name_label.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            row_layout.addWidget(name_label)

            percent_label = QtWidgets.QLabel(percent_text)
            percent_label.setFixedWidth(self.frame_percent_width)
            percent_label.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row_layout.addWidget(percent_label)

            additive = sdf_frame_ops.get_frame_mask_mode(layer)
            mode_btn = QtWidgets.QPushButton("+" if additive else "-")
            mode_btn.setFixedWidth(24)
            mode_btn.setToolTip(
                "Additive (black base, paint white)" if additive
                else "Subtractive (white base, paint black)")
            mode_btn.clicked.connect(
                lambda _c=False, u=uid: self._on_toggle_mode(u))
            row_layout.addWidget(mode_btn)

            select_btn = QtWidgets.QPushButton("→")
            select_btn.setFixedWidth(28)
            select_btn.clicked.connect(
                lambda _checked=False, u=uid: self._on_select(u))
            row_layout.addWidget(select_btn)

            export_btn = QtWidgets.QPushButton("↑")
            export_btn.setFixedWidth(28)
            export_btn.setToolTip("Export this frame's mask to a PNG")
            export_btn.clicked.connect(
                lambda _c=False, u=uid: self._on_export_frame(u))
            row_layout.addWidget(export_btn)

            import_btn = QtWidgets.QPushButton("↓")
            import_btn.setFixedWidth(28)
            import_btn.setToolTip(
                "Import an edited PNG and promote it to the top of this frame's mask")
            import_btn.clicked.connect(
                lambda _c=False, u=uid: self._on_import_frame(u))
            row_layout.addWidget(import_btn)

            self.frame_list.addWidget(row)

    def _find_frame_by_uid(self, layer_uid):
        group = sdf_layer_setup._find_sdf_group()
        if group is None:
            return None
        return next((layer for layer in group.sub_layers()
                     if layer.uid() == layer_uid), None)

    def _get_active_stack_key(self):
        stack = sp.textureset.get_active_stack()
        texture_set = stack.material()
        texture_set_name = (
            texture_set.name() if callable(texture_set.name) else texture_set.name)
        return (texture_set_name, stack.name())

    def _poll_active_stack(self):
        try:
            current_key = self._get_active_stack_key()
        except Exception:
            current_key = None
        if current_key != self._last_stack_key:
            self.refresh_frames()

    def _split_frame_label(self, label_text):
        parts = label_text.rsplit("  ", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return label_text, ""

    def _set_selected_frame_uid(self, layer_uid, refresh=False):
        self.selected_frame_uid = layer_uid
        if refresh:
            self.refresh_frames()

    def _on_target_frame_toggled(self, layer_uid, checked):
        if checked:
            self.selected_frame_uid = layer_uid

    def _on_export_frame(self, layer_uid):
        try:
            self._set_selected_frame_uid(layer_uid, refresh=True)
            group = sdf_layer_setup._find_sdf_group()
            if group is None:
                return
            frame = next((l for l in group.sub_layers()
                          if l.uid() == layer_uid), None)
            if frame is None:
                return
            default_name = frame.get_name().split()[0] + ".png"
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Export Frame Mask", default_name,
                "PNG Image (*.png)")
            if not path:
                return
            sdf_external.export_frame_for_external(frame, path)
            sp.logging.info(f"SDF frame exported: {path}")
        except Exception as e:
            sp.logging.error(f"SDF export failed: {e}")

    def _on_import_frame(self, layer_uid):
        try:
            self._set_selected_frame_uid(layer_uid, refresh=True)
            group = sdf_layer_setup._find_sdf_group()
            if group is None:
                return
            frame = next((l for l in group.sub_layers()
                          if l.uid() == layer_uid), None)
            if frame is None:
                return
            path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Import Frame Mask", "",
                "PNG Image (*.png);;All Files (*)")
            if not path:
                return
            sdf_external.import_external_edit(frame, path)
            sp.logging.info(f"SDF frame imported: {path}")
        except Exception as e:
            sp.logging.error(f"SDF import failed: {e}")

    def _on_toggle_mode(self, layer_uid):
        try:
            self._set_selected_frame_uid(layer_uid)
            layer = self._find_frame_by_uid(layer_uid)
            if layer is None:
                return
            current = sdf_frame_ops.get_frame_mask_mode(layer)
            sdf_frame_ops.set_frame_mask_mode(layer, not current)
            self.refresh_frames()
        except Exception as e:
            sp.logging.error(f"SDF toggle mode failed: {e}")

    def _on_select(self, layer_uid):
        try:
            layer = self._find_frame_by_uid(layer_uid)
            if layer is None:
                return
            self._set_selected_frame_uid(layer_uid)
            sp.layerstack.set_selected_nodes([layer])
            sp.layerstack.set_selection_type(
                layer, sp.layerstack.SelectionType.Mask)
            self.refresh_frames()
        except Exception as e:
            sp.logging.error(f"SDF select failed: {e}")

    def _on_setup(self):
        try:
            sdf_layer_setup.setup_sdf_group(self.frame_count.value())
            self.refresh_frames()
        except Exception as e:
            sp.logging.error(f"SDF setup failed: {e}")

    def _on_sync(self):
        try:
            sdf_frame_ops.sync_frame_values()
            self.refresh_frames()
        except Exception as e:
            sp.logging.error(f"SDF sync failed: {e}")

    def _on_add_frame(self):
        try:
            stack = sp.textureset.get_active_stack()
            selected = sp.layerstack.get_selected_nodes(stack)
            ref = None
            group = sdf_layer_setup._find_sdf_group()
            if group is not None and selected:
                # Use the selected layer as reference if it's a frame in the group
                frame_uids = {l.uid() for l in group.sub_layers()}
                for n in selected:
                    if n.uid() in frame_uids:
                        ref = n
                        break
            sdf_frame_ops.add_frame(ref)
            self.refresh_frames()
        except Exception as e:
            sp.logging.error(f"SDF add frame failed: {e}")

    def _on_borrow_shape(self):
        try:
            if self.selected_frame_uid is None:
                raise RuntimeError("Select a target frame row first.")
            frame = self._find_frame_by_uid(self.selected_frame_uid)
            if frame is None:
                raise RuntimeError("Selected target frame no longer exists.")
            sdf_frame_ops.ui_borrow_shape(frame)
            sp.logging.info(
                f"SDF borrowed shape into frame: {frame.get_name()}")
            self.refresh_frames()
        except Exception as e:
            sp.logging.error(f"SDF borrow shape failed: {e}")

    def _on_bake_sdf(self):
        dialog = QProgressDialog("Starting bake...", "", 0, 0, self)
        dialog.setWindowTitle("Bake SDF")
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.setCancelButton(None)
        dialog.setMinimumDuration(0)
        dialog.setAutoClose(False)
        dialog.setAutoReset(False)
        dialog.show()
        QApplication.processEvents()

        def on_progress(stage, current, total):
            dialog.setLabelText(
                f"{stage} ({current}/{total})" if total > 1 else stage)
            dialog.setMaximum(total)
            dialog.setValue(current)
            QApplication.processEvents()

        try:
            baked_path = sdf_bake.bake_sdf(on_progress=on_progress)
            sp.logging.info(f"SDF bake completed: {baked_path}")
        except Exception as e:
            sp.logging.error(f"SDF bake failed: {e}")
        finally:
            dialog.close()


def start_plugin():
    global _dock, _panel
    _panel = SDFPanel()
    _panel.setWindowTitle("SDF Real-Time Generator")
    _dock = sp.ui.add_dock_widget(_panel)
    _dock.setWindowTitle("SDF Real-Time Generator")
    _dock.show()
    _dock.raise_()
    sp.logging.info("SDF plugin loaded")


def close_plugin():
    global _dock, _panel
    if _dock is not None:
        sp.ui.delete_ui_element(_dock)
        _dock = None
    _panel = None
    sp.logging.info("SDF plugin unloaded")
