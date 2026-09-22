from __future__ import annotations

import csv
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from PySide6 import QtCore, QtGui, QtWidgets
from .core import Ledger, ActivityClock

KIT = Path(__file__).resolve().parent.parent / 'rizum-pt-ui-prettier'
if str(KIT) not in sys.path:
    sys.path.insert(0, str(KIT))
from rizum_ui import (apply_theme, apply_compact_dock_surface, SecondaryActionButton,
                      TextActionButton, make_icon_button, default_theme)


def duration(seconds):
    seconds = max(0, int(seconds))
    return f'{seconds // 3600:02d}:{seconds // 60 % 60:02d}:{seconds % 60:02d}'


class Panel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('RizumTimeTrackerPanel')
        apply_theme(self, mode='overlay')
        apply_compact_dock_surface(self)
        self.setStyleSheet(self.styleSheet() + f'''
            QWidget#RizumTimeTrackerPanel QLabel {{ color: {default_theme.text}; background: transparent; }}
            QWidget#RizumTimeTrackerPanel QLabel[muted="true"] {{ color: {default_theme.text_muted}; }}
        ''')
        self.box = QtWidgets.QVBoxLayout(self)
        self.box.setContentsMargins(16, 12, 16, 12)
        self.box.setSpacing(8)
        top = QtWidgets.QHBoxLayout()
        self.name = QtWidgets.QLabel('No project')
        self.name.setWordWrap(True)
        self.name.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.menu = make_icon_button('ellipsis.svg', 'Work and records')
        top.addWidget(self.name, 1)
        top.addWidget(self.menu)
        self.box.addLayout(top)
        self.total = QtWidgets.QLabel('00:00:00')
        font = self.total.font()
        font.setPointSizeF(max(18, font.pointSizeF() * 1.8))
        self.total.setFont(font)
        self.box.addWidget(self.total)
        self.detail = QtWidgets.QLabel('Today 00:00:00')
        self.detail.setProperty('muted', True)
        self.detail.setWordWrap(True)
        self.detail.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.box.addWidget(self.detail)
        self.state = QtWidgets.QLabel('Open a saved Painter project')
        self.state.setProperty('muted', True)
        self.state.setWordWrap(True)
        self.box.addWidget(self.state)
        self.assign = TextActionButton('Assign work')
        self.pause = SecondaryActionButton('Pause')
        self.box.addWidget(self.assign)
        self.box.addWidget(self.pause)
        self.box.addStretch(1)
        self.scale_controls()

    def scale_controls(self):
        scale = max(0.75, self.fontMetrics().height() / 16.0)
        self.box.setContentsMargins(*[round(x * scale) for x in (16, 12, 16, 12)])
        self.box.setSpacing(round(8 * scale))
        for button in (self.assign, self.pause):
            button.setCompactHeight(round(28 * scale))
            button.setMinimumWidth(button.sizeHint().width())
        self.menu.setFixedSize(round(28 * scale), round(28 * scale))
        self.menu.setPaintedIconSize(round(16 * scale))
        self.menu.setCompactTooltipScale(scale)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QtCore.QEvent.Type.FontChange and hasattr(self, 'pause'):
            self.scale_controls()


class Plugin(QtCore.QObject):
    def __init__(self):
        import substance_painter as sp
        super().__init__()
        self.sp = sp
        root = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'Rizum' / 'TimeTracker'
        self.ledger = Ledger(root / 'time.sqlite3')
        self.settings = QtCore.QSettings('Rizum', 'TimeTracker')
        self.clock = ActivityClock(self.ledger, max(30, int(self.settings.value('idle_seconds', 120))))
        self.path = None
        self.paused = False
        self.branch = False
        self.failed = False
        self.closing = False
        self.closed = False
        self.dialog = None
        self.in_tools = False
        self.last_tick = time.monotonic()
        self.panel = Panel()
        self.dock = sp.ui.add_dock_widget(self.panel)
        self.dock.setObjectName('RizumTimeTrackerDock')
        self.dock.setWindowTitle('Rizum Time Tracker')
        self.panel.assign.clicked.connect(self.assign)
        self.panel.pause.clicked.connect(self.pause)
        self.panel.menu.clicked.connect(self.menu)
        self.app = QtWidgets.QApplication.instance()
        self.app.installEventFilter(self)
        self.events = []
        for name, callback in [('ProjectEditionEntered', self.project_entered),
                               ('ProjectSaved', self.project_changed),
                               ('ProjectAboutToClose', self.project_closed)]:
            event = getattr(sp.event, name)
            sp.event.DISPATCHER.connect(event, callback)
            self.events.append((event, callback))
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.tick)
        self.timer.start()
        self.project_changed()

    def project_entered(self, _event=None):
        self.closing = False
        self.project_changed()

    def foreground(self):
        return self.app.applicationState() == QtCore.Qt.ApplicationState.ApplicationActive

    def project_changed(self, _event=None):
        if self.closing or self.closed or self.failed:
            return
        try:
            path = self.sp.project.file_path() if self.sp.project.is_open() else None
            path = os.path.normcase(os.path.abspath(path)) if path else None
            if path == self.path:
                return
            old = self.path
            self.clock.switch(None)
            self.path = path
            self.branch = False
            if path and old and not self.ledger.binding(path):
                self.branch = bool(self.ledger.inherit(path, old))
            if path and self.ledger.binding(path):
                self.clock.switch(path)
            self.refresh()
        except Exception as error:
            self.fail(error)

    def project_closed(self, _event=None):
        try:
            self.closing = True
            self.clock.switch(None)
            self.path = None
            self.branch = False
            self.refresh()
        except Exception as error:
            self.fail(error)

    def fail(self, error):
        self.failed = True
        self.panel.state.setText('Recording stopped: ' + str(error))
        self.sp.logging.error('Rizum Time Tracker: ' + str(error))

    def eventFilter(self, watched, event):
        if self.failed or self.closed:
            return False
        kind = event.type()
        try:
            if kind == QtCore.QEvent.Type.ApplicationDeactivate:
                self.clock.stop()
            elif self.path and not self.paused and self.dialog is None and not self.in_tools and self.foreground():
                if isinstance(watched, QtWidgets.QWidget) and (watched is self.panel or self.panel.isAncestorOf(watched)):
                    return False
                if self.app.activeModalWidget() is not None:
                    self.clock.stop()
                    return False
                if time.monotonic() - self.last_tick > 5:
                    self.clock.stop()
                active = kind in (QtCore.QEvent.Type.MouseButtonPress, QtCore.QEvent.Type.MouseButtonRelease,
                                  QtCore.QEvent.Type.KeyPress, QtCore.QEvent.Type.Wheel,
                                  QtCore.QEvent.Type.TabletPress, QtCore.QEvent.Type.TabletRelease)
                if kind == QtCore.QEvent.Type.MouseMove:
                    active = bool(event.buttons())
                elif kind == QtCore.QEvent.Type.TabletMove:
                    active = event.pressure() > 0 or bool(event.buttons())
                if active:
                    self.clock.input()
        except Exception as error:
            self.fail(error)
        return False

    def tick(self):
        if self.failed:
            return
        try:
            self.project_changed()
            now = time.monotonic()
            if now - self.last_tick > 5:
                self.clock.stop()
            self.last_tick = now
            if not self.foreground() or (self.clock.last is not None and now-self.clock.last >= self.clock.idle):
                self.clock.stop()
            self.clock.flush()
            self.refresh()
        except Exception as error:
            self.fail(error)

    def refresh(self):
        if self.failed or self.closed:
            return
        binding = self.ledger.binding(self.path) if self.path else None
        self.panel.assign.setVisible(bool(self.path) and (self.branch or not binding))
        self.panel.assign.setText('Choose part for saved copy' if self.branch else ('Change work / part' if binding else 'Assign work'))
        self.panel.pause.setEnabled(bool(binding) and not self.failed)
        self.panel.pause.setText('Resume' if self.paused else 'Pause')
        self.panel.scale_controls()
        if not binding:
            self.panel.name.setText(Path(self.path).stem if self.path else 'No saved project')
            self.panel.total.setText('00:00:00')
            self.panel.detail.setText('Today 00:00:00')
            self.panel.state.setText('Assign this file to a work' if self.path else 'Open or save a Painter project')
            return
        midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        rows = self.ledger.summary(binding['work'], midnight)
        total = sum(row['total'] for row in rows)
        today = sum(row['today'] for row in rows)
        part = next((row['total'] for row in rows if row['id'] == binding['part']), 0)
        self.panel.name.setText(binding['work_name'])
        self.panel.total.setText(duration(total))
        self.panel.detail.setText(f"Today {duration(today)}\n{binding['part_name']}  {duration(part)}")
        self.panel.state.setText('Paused' if self.paused else ('Recording' if self.clock.last is not None else 'Idle'))

    def pause(self):
        self.clock.stop()
        self.paused = not self.paused
        self.refresh()

    def assign(self):
        if not self.path or self.dialog is not None:
            return
        path = self.path
        binding = self.ledger.binding(path)
        self.clock.stop()
        dialog = QtWidgets.QDialog(self.panel)
        self.dialog = dialog
        dialog.setWindowTitle('Work and part')
        layout = QtWidgets.QFormLayout(dialog)
        work = QtWidgets.QComboBox()
        work.addItem('New work', None)
        for row in self.ledger.works():
            work.addItem(row['name'], row['id'])
        work_name = QtWidgets.QLineEdit(Path(path).stem.split('.')[0])
        part = QtWidgets.QComboBox()
        part_name = QtWidgets.QLineEdit(Path(path).stem.rsplit('.', 1)[-1])
        layout.addRow('Work', work)
        layout.addRow('New work name', work_name)
        layout.addRow('Part', part)
        layout.addRow('New part name', part_name)
        note = QtWidgets.QLabel('Changes the grouping of this file and its recorded time.')
        note.setWordWrap(True)
        layout.addRow(note)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Save |
                                            QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        layout.addRow(buttons)

        def update_parts():
            work_name.setEnabled(work.currentData() is None)
            part.clear()
            part.addItem('New part', None)
            if work.currentData():
                for row in self.ledger.parts(work.currentData()):
                    part.addItem(row['name'], row['id'])

        def validate():
            part_name.setEnabled(part.currentData() is None)
            valid = (work.currentData() is not None or bool(work_name.text().strip())) and (
                part.currentData() is not None or bool(part_name.text().strip()))
            buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Save).setEnabled(valid)

        work.currentIndexChanged.connect(update_parts)
        work.currentIndexChanged.connect(validate)
        part.currentIndexChanged.connect(validate)
        work_name.textChanged.connect(validate)
        part_name.textChanged.connect(validate)
        update_parts()
        if binding:
            work.setCurrentIndex(work.findData(binding['work']))
            part.setCurrentIndex(part.findData(binding['part']))
        validate()
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        try:
            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                self.ledger.bind(path, work_name.text(), part_name.text(), work.currentData(), part.currentData())
                if self.path == path:
                    self.clock.switch(path)
                    self.branch = False
        except Exception as error:
            self.fail(error)
        finally:
            self.dialog = None
            dialog.deleteLater()
        self.refresh()

    def menu(self):
        self.clock.stop()
        self.in_tools = True
        try:
            self.open_menu()
        except Exception as error:
            QtWidgets.QMessageBox.warning(self.panel, 'Time Tracker', str(error))
        finally:
            self.in_tools = False

    def open_menu(self):
        menu = QtWidgets.QMenu(self.panel)
        group = menu.addAction('Change work / part...')
        group.setEnabled(bool(self.path))
        menu.addSeparator()
        history = menu.addAction('Work history')
        export = menu.addAction('Export records...')
        manual = menu.addAction('Add time...')
        binding = self.ledger.binding(self.path) if self.path else None
        for action in (history, export, manual):
            action.setEnabled(bool(binding))
        menu.addSeparator()
        idle = menu.addAction('Idle timeout...')
        folder = menu.addAction('Open records folder')
        chosen = menu.exec(self.panel.menu.mapToGlobal(self.panel.menu.rect().bottomLeft()))
        if chosen == group:
            self.assign()
        elif chosen == folder:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(Path(self.ledger.db.execute('PRAGMA database_list').fetchone()[2]).parent)))
        elif chosen == idle:
            value, ok = QtWidgets.QInputDialog.getInt(self.panel, 'Idle timeout', 'Seconds without input', self.clock.idle, 30, 1800, 30)
            if ok:
                self.clock.stop()
                self.clock.idle = value
                self.settings.setValue('idle_seconds', value)
        elif chosen == manual:
            value, ok = QtWidgets.QInputDialog.getInt(self.panel, 'Add time', 'Minutes for the current part', 10, 1, 1440)
            if ok:
                now = time.time()
                self.ledger.save_session(uuid4().hex, self.path, now, now, value*60, True)
                self.refresh()
        elif chosen == history:
            self.show_history(binding)
        elif chosen == export:
            self.export(binding)
        menu.deleteLater()

    def show_history(self, binding):
        dialog = QtWidgets.QDialog(self.panel)
        dialog.setWindowTitle(binding['work_name'])
        layout = QtWidgets.QVBoxLayout(dialog)
        table = QtWidgets.QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(['Started', 'Part', 'Time', 'Source'])
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        for row in self.ledger.history(binding['work']):
            if row['seconds'] < 1:
                continue
            index = table.rowCount()
            table.insertRow(index)
            for column, value in enumerate([datetime.fromtimestamp(row['start']).strftime('%Y-%m-%d %H:%M'),
                                            row['part_name'], duration(row['seconds']), 'Manual' if row['manual'] else 'Activity']):
                table.setItem(index, column, QtWidgets.QTableWidgetItem(value))
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(table)
        dialog.resize(600, 380)
        dialog.exec()
        dialog.deleteLater()

    def export(self, binding):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self.panel, 'Export records', 'time-records.csv', 'CSV (*.csv)')
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8-sig') as handle:
                    writer = csv.writer(handle)
                    writer.writerow(['Work', 'Part', 'File', 'Started', 'Seconds', 'Manual'])
                    for row in self.ledger.history(binding['work']):
                        values = [binding['work_name'], row['part_name'], row['file'],
                                  datetime.fromtimestamp(row['start']).isoformat(), round(row['seconds'], 2), row['manual']]
                        writer.writerow(["'" + value if isinstance(value, str) and value.startswith(('=', '+', '-', '@')) else value for value in values])
            except OSError as error:
                QtWidgets.QMessageBox.warning(self.panel, 'Export records', str(error))

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.timer.stop()
        if self.dialog is not None:
            self.dialog.reject()
        self.app.removeEventFilter(self)
        for event, callback in self.events:
            self.sp.event.DISPATCHER.disconnect(event, callback)
        try:
            self.clock.stop()
        finally:
            self.ledger.close()
            self.sp.ui.delete_ui_element(self.dock)
            self.deleteLater()
