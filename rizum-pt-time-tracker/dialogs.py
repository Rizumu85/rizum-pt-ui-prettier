"""Time Tracker dialogs composed from the shared Painter UI kit."""
from dataclasses import replace
from datetime import datetime
from pathlib import Path
import sys

from PySide6 import QtCore, QtWidgets

KIT = Path(__file__).resolve().parent.parent / 'rizum-pt-ui-prettier'
if str(KIT) not in sys.path:
    sys.path.insert(0, str(KIT))
from rizum_ui import (PainterSettingsDialog, PAINTER_SETTINGS_LAYOUT as METRICS,
                      PAINTER_DIALOG_STYLE as COLORS, SecondaryActionButton,
                      AnimatedSaveButton, TextActionButton, build_stylesheet, default_theme,
                      make_combo_input, make_compact_stepper, make_inset_separator)
from .core import filename_group


class TrackerDialog(PainterSettingsDialog):
    def __init__(self, title, parent=None, *, action='Save', cancel=True, wide=False):
        super().__init__(parent, theme=replace(default_theme, surface=COLORS['surface']))
        self.setWindowTitle(title)
        self.controls = []
        self.wide = wide
        self.body = QtWidgets.QWidget()
        self.body_layout = QtWidgets.QVBoxLayout(self.body)
        self.settingsSurfaceLayout().addWidget(self.body, 1)
        self.footer = QtWidgets.QWidget()
        self.footer_layout = QtWidgets.QHBoxLayout(self.footer)
        self.footer_layout.addStretch(1)
        self.cancel_button = SecondaryActionButton('Cancel')
        self.cancel_button.setVisible(cancel)
        self.cancel_button.clicked.connect(self.reject)
        self.save_button = AnimatedSaveButton(action)
        self.save_button.setDirty(True, animate=False)
        self.save_button.clicked.connect(self.accept)
        self.footer_layout.addWidget(self.cancel_button)
        self.footer_layout.addWidget(self.save_button)
        self.settingsSurfaceLayout().addWidget(self.footer)
        self.settingsUiScaleChanged.connect(self.apply_metrics)
        self.apply_metrics()

    def add_field(self, text, control):
        row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QtWidgets.QLabel(text)
        layout.addWidget(label)
        layout.addWidget(control, 1)
        self.body_layout.addWidget(row)
        self.controls.append((row, label, control))
        self.apply_metrics()
        return row

    def apply_metrics(self, _scale=None):
        m = lambda token: token.resolve(self)
        theme = replace(default_theme, bg=COLORS['surface'], surface=COLORS['surface'],
                        surface_control=COLORS['control'], text=COLORS['text'],
                        text_muted=COLORS['muted'], radius_button=default_theme.radius_small,
                        font_size=self.settingsMetric(12))
        self.setStyleSheet(build_stylesheet(theme, mode='full') + f'''
            QLabel {{ color: {theme.text}; background: transparent; font-size: {theme.font_size}px; }}
            QLineEdit {{ min-height: 0; padding: 0 {self.settingsMetric(8)}px; }}
            QTableWidget {{ color: {theme.text}; font-size: {theme.font_size}px; }}
            QHeaderView::section {{ background: {theme.surface}; color: {theme.text_muted};
                border: 0; border-bottom: 1px solid {theme.border};
                padding: {self.settingsMetric(8)}px; font-size: {theme.font_size}px; }}
            QTableWidget::item {{ padding: {self.settingsMetric(5)}px; }}
            QTableWidget::item:selected {{ background: {COLORS['control_hover']}; color: {theme.text}; }}
        ''')
        self.body_layout.setContentsMargins(m(METRICS.body_margin_x), m(METRICS.body_margin_top),
                                           m(METRICS.body_margin_x), m(METRICS.body_margin_bottom))
        self.body_layout.setSpacing(m(METRICS.body_spacing))
        self.footer_layout.setContentsMargins(m(METRICS.footer_margin_x), m(METRICS.footer_top),
                                             m(METRICS.footer_margin_x), m(METRICS.footer_bottom))
        self.footer_layout.setSpacing(self.settingsMetric(METRICS.footer_button_spacing))
        for row, label, control in self.controls:
            row.setMinimumHeight(m(METRICS.row_height))
            row.layout().setSpacing(self.settingsMetric(METRICS.row_spacing))
            label.setMinimumWidth(self.settingsMetric(80))
            if hasattr(control, 'setCompactHeight'):
                control.setCompactHeight(m(METRICS.control_height))
            else:
                control.setFixedHeight(m(METRICS.control_height))
        for button in (self.cancel_button, self.save_button):
            button.setCompactHeight(m(METRICS.footer_button_height))
            button.setFixedWidth(max(self.settingsMetric(68), button.sizeHint().width()))
        self.setMinimumWidth(self.settingsMetric(600 if self.wide else 360))


class SettingsDialog(TrackerDialog):
    def __init__(self, ledger, path, idle, parent=None):
        super().__init__('Time Tracker Settings', parent)
        self.ledger = ledger
        self.path = path
        self.initial_idle = idle
        binding = ledger.binding(path) if path else None
        work_name, part_name = filename_group(path) if path else ('', '')
        self.section('CURRENT FILE')
        self.work = make_combo_input([('New work', None)] + [(r['name'], r['id']) for r in ledger.works()])
        self.work.setFitToContents(False)
        self.part = make_combo_input([('New part', None)])
        self.part.setFitToContents(False)
        self.work_name = QtWidgets.QLineEdit(work_name)
        self.part_name = QtWidgets.QLineEdit(part_name)
        self.add_field('Work', self.work)
        self.work_name_row = self.add_field('Name', self.work_name)
        self.add_field('Part', self.part)
        self.part_name_row = self.add_field('Name', self.part_name)
        self.work.currentIndexChanged.connect(self.update_parts)
        self.part.currentIndexChanged.connect(self.validate)
        self.work_name.textChanged.connect(self.validate)
        self.part_name.textChanged.connect(self.validate)
        if binding:
            self.work.setCurrentIndex(self.work.findData(binding['work']))
            self.update_parts()
            self.part.setCurrentIndex(self.part.findData(binding['part']))
        self.initial = self.selection()
        if not path:
            for row, _, _ in self.controls:
                row.hide()
            self.body_layout.addWidget(QtWidgets.QLabel('No saved project'))
        self.section('TRACKING')
        self.idle = make_compact_stepper(idle, 30, 1800, step=30)
        self.add_field('Idle seconds', self.idle)
        self.section('RECORDS')
        self.minutes = make_compact_stepper(0, 0, 1440)
        self.minutes.setEnabled(bool(path))
        self.add_field('Add minutes', self.minutes)
        actions = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(actions)
        layout.setContentsMargins(0, 0, 0, 0)
        self.export_button = TextActionButton('Export CSV...')
        self.folder_button = TextActionButton('Open folder')
        self.export_button.setEnabled(bool(binding))
        layout.addWidget(self.export_button)
        layout.addStretch(1)
        layout.addWidget(self.folder_button)
        self.body_layout.addWidget(actions)
        self.idle.valueChanged.connect(self.validate)
        self.minutes.valueChanged.connect(self.validate)
        self.validate()
        self.apply_metrics()

    def section(self, text):
        label = QtWidgets.QLabel(text)
        label.setProperty('muted', True)
        label.setMinimumHeight(METRICS.section_height.resolve(self))
        self.body_layout.addWidget(label)

    def apply_metrics(self, _scale=None):
        super().apply_metrics(_scale)
        for name in ('export_button', 'folder_button'):
            button = getattr(self, name, None)
            if button is not None:
                button.setCompactHeight(METRICS.footer_button_height.resolve(self))
        for label in self.body.findChildren(QtWidgets.QLabel):
            if label.property('muted'):
                label.setMinimumHeight(METRICS.section_height.resolve(self))

    def selection(self):
        return (self.work_name.text().strip() if self.work.currentData() is None else '',
                self.part_name.text().strip() if self.part.currentData() is None else '',
                self.work.currentData(), self.part.currentData())

    def update_parts(self, *_args):
        items = [('New part', None)]
        if self.work.currentData():
            items += [(r['name'], r['id']) for r in self.ledger.parts(self.work.currentData())]
        self.part.setItems(items)
        self.validate()

    def validate(self, *_args):
        new_work = self.work.currentData() is None
        new_part = self.part.currentData() is None
        self.work_name_row.setVisible(bool(self.path) and new_work)
        self.part_name_row.setVisible(bool(self.path) and new_part)
        valid = not self.path or ((not new_work or bool(self.work_name.text().strip())) and (not new_part or bool(self.part_name.text().strip())))
        changed = bool(self.path) and self.selection() != getattr(self, 'initial', None)
        if hasattr(self, 'idle'):
            changed = changed or self.idle.value() != self.initial_idle or self.minutes.value() > 0
        self.save_button.setDirty(valid and changed, animate=False)


class HistoryDialog(TrackerDialog):
    def __init__(self, title, rows, parent=None):
        super().__init__(title, parent, action='Done', cancel=False, wide=True)
        self.table = QtWidgets.QTableWidget(0, 4, self.body)
        self.table.setHorizontalHeaderLabels(['Started', 'Part', 'Time', 'Source'])
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().hide()
        for row in rows:
            if row['seconds'] < 1:
                continue
            index = self.table.rowCount()
            self.table.insertRow(index)
            seconds = int(row['seconds'])
            values = [datetime.fromtimestamp(row['start']).strftime('%Y-%m-%d %H:%M'), row['part_name'],
                      f'{seconds // 3600:02d}:{seconds // 60 % 60:02d}:{seconds % 60:02d}',
                      'Manual' if row['manual'] else 'Activity']
            for column, value in enumerate(values):
                self.table.setItem(index, column, QtWidgets.QTableWidgetItem(value))
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        if self.table.rowCount():
            self.body_layout.addWidget(self.table)
        else:
            self.table.hide()
            empty = QtWidgets.QLabel('No recorded time yet.')
            empty.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.body_layout.addWidget(empty, 1)
        self.body_layout.addWidget(make_inset_separator(0))
        self.apply_metrics()
        self.resize(self.settingsMetric(600), self.settingsMetric(360))


class MessageDialog(TrackerDialog):
    def __init__(self, title, text, parent=None):
        super().__init__(title, parent, action='OK', cancel=False)
        label = QtWidgets.QLabel(text)
        label.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        label.setWordWrap(True)
        self.body_layout.addWidget(label)
        self.apply_metrics()
