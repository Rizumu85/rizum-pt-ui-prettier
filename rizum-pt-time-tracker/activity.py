"""Positive evidence policy; unconfirmed UI inputs never extend work sessions."""
from PySide6 import QtWidgets


def input_context(widget, main_window):
    viewport = False
    current = widget
    while current is not None and current is not main_window:
        name = current.objectName().casefold()
        if isinstance(current, (QtWidgets.QMenu, QtWidgets.QMenuBar, QtWidgets.QDialog)):
            return 'excluded'
        if name.startswith(('rizum', 'python-addon')) or not type(current).__module__.startswith('PySide6.'):
            return 'excluded'
        viewport = viewport or name in ('viewer3d', 'viewer2d')
        current = current.parent()
    if current is not main_window or widget is main_window:
        return 'excluded'
    return 'viewport' if viewport else 'candidate'


class ActivityPolicy:
    CONFIRM_SECONDS = 0.75

    def __init__(self, clock):
        self.clock = clock
        self.pending = None

    def stop(self):
        self.pending = None
        self.clock.stop()

    def offer(self, context, mono, wall):
        if self.pending is not None:
            self.stop()
        if context == 'excluded':
            self.stop()
        elif context == 'viewport':
            self.clock.input(mono, wall)
        else:
            self.pending = (mono, wall)

    def confirm(self, mono):
        if self.pending is None:
            return
        timestamp, wall = self.pending
        self.pending = None
        if 0 <= mono - timestamp <= self.CONFIRM_SECONDS:
            self.clock.input(timestamp, wall)
        else:
            self.clock.stop()

    def expire(self, mono):
        if self.pending is not None and mono - self.pending[0] > self.CONFIRM_SECONDS:
            self.stop()
