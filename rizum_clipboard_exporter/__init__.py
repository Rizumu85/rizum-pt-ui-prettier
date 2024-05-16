import os

# Substance 3D Painter modules
import substance_painter.ui
import substance_painter.export
import substance_painter.project
import substance_painter.textureset

# PySide module to build custom UI
from PySide2 import QtWidgets

plugin_widgets = []

def start_plugin():
    # Create a widget windows
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Clipboard Exporter")

    # Create a central widget
    central_widget = QtWidgets.QWidget()
    window.setCentralWidget(central_widget)

    # Create a layout
    layout = QtWidgets.QVBoxLayout()
    central_widget.setLayout(layout)

    # Create a button
    layer_btn = QtWidgets.QPushButton("Layer")
    layer_btn.setFixedSize(20, 20)
    layout.addWidget(layer_btn)

    mask_btn = QtWidgets.QPushButton("Mask")
    mask_btn.setFixedSize(20, 20)
    layout.addWidget(mask_btn)

    applied_btn = QtWidgets.QPushButton("Applied")
    applied_btn.setFixedSize(20, 20)
    layout.addWidget(applied_btn)

    # Add this widget to the Substance Painter UI
    substance_painter.ui.add_dock_widget(window)
    
    # Store the widget for proper cleanup later when stopping the plugin
    plugin_widgets.append(window)

def close_plugin():
    for widget in plugin_widgets:
        substance_painter.ui.delete_ui_element(widget)

    plugin_widgets.clear()

if __name__ == '__main__':
    start_plugin()