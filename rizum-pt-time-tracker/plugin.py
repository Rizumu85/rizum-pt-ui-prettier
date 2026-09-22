from __future__ import annotations

import csv
import os
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from PySide6 import QtCore, QtGui, QtWidgets
from .core import Ledger, ActivityClock
from .activity import ActivityPolicy, input_context
from .dialogs import SettingsDialog, HistoryDialog, MessageDialog


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
        self.activity = ActivityPolicy(self.clock)
        self.busy = bool(sp.project.is_busy()) if sp.project.is_open() else False
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
        self.settings_action = self.menu.addAction('Settings...', self.show_settings)
        self.menu.aboutToShow.connect(self.menu_opened)
        sp.ui.add_menu(self.menu)
        self.app = QtWidgets.QApplication.instance()
        self.app.installEventFilter(self)
        self.events = []
        for name, callback in [('ProjectEditionEntered', self.project_entered),
                               ('ProjectSaved', self.project_changed),
                               ('LayerStacksModelDataChanged', self.model_changed),
                               ('BusyStatusChanged', self.busy_changed),
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

    def busy_changed(self, event):
        self.busy = event.busy
        if self.busy:
            self.activity.stop()

    def model_changed(self, _event=None):
        if self.closed or self.failed:
            return
        try:
            if self.path and not self.paused and not self.busy and not self.in_tools and self.dialog is None and self.foreground():
                self.activity.confirm(time.monotonic())
            else:
                self.activity.stop()
        except Exception as error:
            self.fail(error)

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
            self.activity.stop()
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
            self.activity.stop()
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
            if kind == QtCore.QEvent.Type.Show and isinstance(watched, (QtWidgets.QMenu, QtWidgets.QDialog)):
                self.activity.stop()
                return False
            if kind == QtCore.QEvent.Type.ApplicationDeactivate:
                self.activity.stop()
            elif self.path and not self.paused and not self.busy and self.dialog is None and not self.in_tools and self.foreground():
                if self.app.activePopupWidget() is not None or self.app.activeModalWidget() is not None:
                    self.activity.stop()
                    return False
                if time.monotonic() - self.last_tick > 5:
                    self.activity.stop()
                active = kind in (QtCore.QEvent.Type.MouseButtonPress, QtCore.QEvent.Type.MouseButtonRelease,
                                  QtCore.QEvent.Type.KeyPress, QtCore.QEvent.Type.Wheel,
                                  QtCore.QEvent.Type.TabletPress, QtCore.QEvent.Type.TabletRelease)
                if kind == QtCore.QEvent.Type.MouseMove:
                    active = bool(event.buttons())
                elif kind == QtCore.QEvent.Type.TabletMove:
                    active = event.pressure() > 0 or bool(event.buttons())
                if active:
                    target = watched
                    if kind == QtCore.QEvent.Type.KeyPress:
                        target = self.app.focusWidget() or watched
                    elif hasattr(event, 'globalPosition'):
                        target = self.app.widgetAt(event.globalPosition().toPoint()) or watched
                    if not isinstance(target, QtWidgets.QWidget):
                        return False
                    # Qt can deliver the same native input to a parent after its child.
                    stamp = (kind, event.timestamp())
                    if event.timestamp() and getattr(self, '_last_input_stamp', None) == stamp:
                        return False
                    self._last_input_stamp = stamp
                    context = input_context(target, self.window)
                    if kind == QtCore.QEvent.Type.KeyPress and context == 'viewport':
                        if event.key() in (QtCore.Qt.Key.Key_Control, QtCore.Qt.Key.Key_Shift,
                                           QtCore.Qt.Key.Key_Alt, QtCore.Qt.Key.Key_Meta):
                            return False
                        # Shortcuts need a document-change signal; arbitrary typing is not work.
                        context = 'candidate'
                    self.activity.offer(context, time.monotonic(), time.time())
        except Exception as error:
            self.fail(error)
        return False

    def tick(self):
        if self.failed:
            return
        try:
            self.project_changed()
            now = time.monotonic()
            self.activity.expire(now)
            if now - self.last_tick > 5:
                self.activity.stop()
            self.last_tick = now
            if not self.foreground() or (self.clock.last is not None and now-self.clock.last >= self.clock.idle):
                self.activity.stop()
            self.clock.flush()
            if self.menu.isVisible():
                self.refresh()
        except Exception as error:
            self.fail(error)

    def refresh(self):
        if self.failed or self.closed:
            return
        binding = self.ledger.binding(self.path) if self.path else None
        for action in (self.pause_action, self.history_action):
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
        self.activity.stop()
        self.paused = not self.paused
        self.refresh()

    def show_settings(self):
        if self.dialog is not None:
            return
        path = self.path
        self.activity.stop()
        dialog = SettingsDialog(self.ledger, path, self.clock.idle, self.window)
        binding = self.ledger.binding(path) if path else None
        dialog.export_button.clicked.connect(lambda: self.export(binding))
        dialog.folder_button.clicked.connect(lambda: self.open_tool('folder'))
        self.dialog = dialog
        try:
            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                if path and dialog.selection() != dialog.initial:
                    self.ledger.bind(path, *dialog.selection())
                if path and dialog.minutes.value() > 0:
                    now = time.time()
                    self.ledger.save_session(uuid4().hex, path, now, now, int(dialog.minutes.value()) * 60, True)
                self.clock.idle = int(dialog.idle.value())
                self.settings.setValue('idle_seconds', self.clock.idle)
        except Exception as error:
            self.fail(error)
        finally:
            self.dialog = None
            dialog.deleteLater()
        self.refresh()

    def menu_opened(self):
        try:
            self.activity.stop()
            self.refresh()
        except Exception as error:
            self.fail(error)

    def run_tool(self, command):
        self.activity.stop()
        self.in_tools = True
        try:
            self.open_tool(command)
        except Exception as error:
            self.show_message('Time Tracker', str(error))
        finally:
            self.in_tools = False

    def open_tool(self, command):
        binding = self.ledger.binding(self.path) if self.path else None
        if command == 'folder':
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(Path(self.ledger.db.execute('PRAGMA database_list').fetchone()[2]).parent)))
        elif command == 'history' and binding:
            self.show_history(binding)
        elif command == 'export' and binding:
            self.export(binding)

    def show_history(self, binding):
        self.exec_dialog(HistoryDialog(binding['work_name'], self.ledger.history(binding['work']), self.window))

    def exec_dialog(self, dialog):
        previous = self.dialog
        self.dialog = dialog
        try:
            return dialog.exec()
        finally:
            self.dialog = previous
            dialog.deleteLater()

    def show_message(self, title, text):
        self.exec_dialog(MessageDialog(title, text, self.window))

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
                self.show_message('Export records', str(error))

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
            self.activity.stop()
        finally:
            self.ledger.close()
            self.sp.ui.delete_ui_element(self.menu)
            self.deleteLater()
