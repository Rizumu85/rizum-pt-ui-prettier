"""Standalone visual preview using the real dock widget."""
import importlib
import sys
from pathlib import Path
from PySide6 import QtGui, QtWidgets

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
Panel = importlib.import_module('rizum-pt-time-tracker.plugin').Panel
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
QtGui.QFontDatabase.addApplicationFont('C:/Windows/Fonts/segoeui.ttf')
app.setFont(QtGui.QFont('Segoe UI', 10))
panel = Panel()
panel.setWindowTitle('Rizum Time Tracker')
panel.name.setText('Penglai Wedding')
panel.total.setText('07:24:18')
panel.detail.setText('Today 01:12:36\nHair  02:04:18')
panel.state.setText('Recording')
panel.assign.setText('Change work / part')
panel.assign.hide()
panel.resize(330, 245)
panel.show()
if '--screenshot' in sys.argv:
    app.processEvents()
    panel.grab().save(sys.argv[sys.argv.index('--screenshot') + 1])
else:
    sys.exit(app.exec())
