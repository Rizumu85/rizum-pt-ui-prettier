from __future__ import annotations

import csv
import os
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from PySide6 import QtCore, QtGui, QtWidgets
from .core import Ledger, ActivityClock, filename_group


def duration(seconds):
    seconds = max(0, int(seconds))
    return f'{seconds // 3600:02d}:{seconds // 60 % 60:02d}:{seconds % 60:02d}'


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
        self.failed = False
        self.closing = False
        self.closed = False
        self.dialog = None
        self.in_tools = False
        self.last_tick = time.monotonic()
        self.window = sp.ui.get_main_window()
        self.menu = QtWidgets.QMenu('Time Tracker', self.window)
        self.menu.setObjectName('rizum_pt_time_tracker_menu')
        self.title_action = self.menu.addAction('No saved project')
        self.total_action = self.menu.addAction('Total\t00:00:00')
        self.today_action = self.menu.addAction('Today\t00:00:00')
        self.part_action = self.menu.addAction('Part\t00:00:00')
        self.state_action = self.menu.addAction('Idle')
        for action in (self.title_action, self.total_action, self.today_action, self.part_action, self.state_action):
            action.setEnabled(False)
        self.menu.addSeparator()
        self.pause_action = self.menu.addAction('Pause tracking', self.pause)
        self.history_action = self.menu.addAction('Work history...', lambda: self.run_tool('history'))
        self.menu.addSeparator()
        self.manage_menu = self.menu.addMenu('Manage')
        self.group_action = self.manage_menu.addAction('Change work / part...', self.assign)
        self.manual_action = self.manage_menu.addAction('Add time...', lambda: self.run_tool('manual'))
        self.export_action = self.manage_menu.addAction('Export records...', lambda: self.run_tool('export'))
        self.manage_menu.addSeparator()
        self.manage_menu.addAction('Idle timeout...', lambda: self.run_tool('idle'))
        self.manage_menu.addAction('Open records folder', lambda: self.run_tool('folder'))
        self.menu.aboutToShow.connect(self.menu_opened)
        sp.ui.add_menu(self.menu)
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
        self.refresh()

    def project_entered(self, _event=None):
        self.closing = False
        self.project_changed()

    def foreground(self):
        return self.app.applicationState() == QtCore.Qt.ApplicationState.ApplicationActive

    def project_changed(self, _event=None):
        if self.closing or self.closed or self.failed:
            return
        try:
            raw_path = self.sp.project.file_path() if self.sp.project.is_open() else None
            path = os.path.normcase(os.path.abspath(raw_path)) if raw_path else None
            if path == self.path:
                return
            self.clock.switch(None)
            self.path = path
            if path:
                self.ledger.auto_bind(raw_path)
                self.clock.switch(path)
            self.refresh()
        except Exception as error:
            self.fail(error)

    def project_closed(self, _event=None):
        try:
            self.closing = True
            self.clock.switch(None)
            self.path = None
            self.refresh()
        except Exception as error:
            self.fail(error)

    def fail(self, error):
        self.failed = True
        self.state_action.setText('Recording stopped: ' + str(error))
        self.pause_action.setEnabled(False)
        self.sp.logging.error('Rizum Time Tracker: ' + str(error))

    def eventFilter(self, watched, event):
        if self.failed or self.closed:
            return False
        kind = event.type()
        try:
            if kind == QtCore.QEvent.Type.ApplicationDeactivate:
                self.clock.stop()
            elif self.path and not self.paused and self.dialog is None and not self.in_tools and self.foreground():
                if self.menu.isVisible() or self.manage_menu.isVisible():
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
            if self.menu.isVisible():
                self.refresh()
        except Exception as error:
            self.fail(error)

    def refresh(self):
        if self.failed or self.closed:
            return
        binding = self.ledger.binding(self.path) if self.path else None
        for action in (self.pause_action, self.history_action, self.group_action, self.manual_action, self.export_action):
            action.setEnabled(bool(binding))
        self.pause_action.setText('Resume tracking' if self.paused else 'Pause tracking')
        for action in (self.total_action, self.today_action, self.part_action):
            action.setVisible(bool(binding))
        if not binding:
            self.title_action.setText('No saved project')
            self.state_action.setText('Waiting for a saved project')
            return
        midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        rows = self.ledger.summary(binding['work'], midnight)
        total = sum(row['total'] for row in rows)
        today = sum(row['today'] for row in rows)
        part = next((row['total'] for row in rows if row['id'] == binding['part']), 0)
        self.title_action.setText(binding['work_name'].replace('&', '&&'))
        self.total_action.setText('Total\t' + duration(total))
        self.today_action.setText('Today\t' + duration(today))
        self.part_action.setText(binding['part_name'].replace('&', '&&') + '\t' + duration(part))
        self.state_action.setText('Paused' if self.paused else ('Recording' if self.clock.last is not None else 'Idle'))

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
        dialog = QtWidgets.QDialog(self.window)
        self.dialog = dialog
        dialog.setWindowTitle('Work and part')
        layout = QtWidgets.QFormLayout(dialog)
        work = QtWidgets.QComboBox()
        work.addItem('New work', None)
        for row in self.ledger.works():
            work.addItem(row['name'], row['id'])
        suggested_work, suggested_part = filename_group(path)
        work_name = QtWidgets.QLineEdit(suggested_work)
        part = QtWidgets.QComboBox()
        part_name = QtWidgets.QLineEdit(suggested_part)
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
        except Exception as error:
            self.fail(error)
        finally:
            self.dialog = None
            dialog.deleteLater()
        self.refresh()

    def menu_opened(self):
        try:
            self.clock.flush()
            self.refresh()
        except Exception as error:
            self.fail(error)

    def run_tool(self, command):
        self.clock.stop()
        self.in_tools = True
        try:
            self.open_tool(command)
        except Exception as error:
            QtWidgets.QMessageBox.warning(self.window, 'Time Tracker', str(error))
        finally:
            self.in_tools = False

    def open_tool(self, command):
        binding = self.ledger.binding(self.path) if self.path else None
        if command == 'folder':
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(Path(self.ledger.db.execute('PRAGMA database_list').fetchone()[2]).parent)))
        elif command == 'idle':
            value, ok = QtWidgets.QInputDialog.getInt(self.window, 'Idle timeout', 'Seconds without input', self.clock.idle, 30, 1800, 30)
            if ok:
                self.clock.stop()
                self.clock.idle = value
                self.settings.setValue('idle_seconds', value)
        elif command == 'manual' and binding:
            path = self.path
            value, ok = QtWidgets.QInputDialog.getInt(self.window, 'Add time', 'Minutes for the current part', 10, 1, 1440)
            if ok:
                now = time.time()
                self.ledger.save_session(uuid4().hex, path, now, now, value*60, True)
                self.refresh()
        elif command == 'history' and binding:
            self.show_history(binding)
        elif command == 'export' and binding:
            self.export(binding)

    def show_history(self, binding):
        dialog = QtWidgets.QDialog(self.window)
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
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self.window, 'Export records', 'time-records.csv', 'CSV (*.csv)')
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
                QtWidgets.QMessageBox.warning(self.window, 'Export records', str(error))

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
            self.sp.ui.delete_ui_element(self.menu)
            self.deleteLater()
