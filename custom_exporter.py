import substance_painter
import substance_painter_plugins
from PySide2.QtWidgets import QWidget, QGridLayout, QCheckBox, QLabel, QComboBox, QPushButton
from PySide2 import QtCore

# Global variable
custom_exporter = None

class CustomExporter:
    def __init__(self):
        self.initialization()
        
    def initialization(self):
        self.init_widget_window()
        self.connect_slots()
        self.show_ui_widget()


    def init_widget_window(self):
        self.widget = QWidget()
        self.widget.setObjectName("Custom exporter")
        self.widget.setWindowTitle("Custom Exporter")

        self.main_layout = QGridLayout(self.widget)

        # Personal Export Checkbox
        self.personal_export_cb = QCheckBox("Personal Export")
        self.main_layout.addWidget(self.personal_export_cb)

        # Asset Type Label
        self.asset_type_lbl = QLabel("Asset Type")
        self.main_layout.addWidget(self.asset_type_lbl)

        # Asset Type Combo Box
        self.asset_type_cmbx = QComboBox()
        self.asset_type_cmbx.addItems(["Character", "Environment", "Prop"])
        self.main_layout.addWidget(self.asset_type_cmbx)

        # Export Button
        self.export_btn = QPushButton("Export")
        self.main_layout.addWidget(self.export_btn)

    def connect_slots(self):
        self.export_btn.clicked.connect(self.on_export_requested)
        self.personal_export_cb.stateChanged.connect(self.on_toggle_personal_export)
        self.asset_type_cmbx.currentIndexChanged.connect(self.on_asset_type_changed)

    def show_ui_widget(self):
        plugin = substance_painter_plugins.plugins.get("custom_exporter", None)
        if plugin is not None:
            # Refresh of the widget
            self.delete_widget()
            self.init_widget_window()

        substance_painter.ui.add_dock_widget(self.widget)
        self.widget.show()

    def delete_widget(self):
        if self.widget is not None:
            substance_painter.ui.delete_ui_element(self.widget)

    def on_export_requested(self):
        substance_painter.logging.log(substance_painter.logging.INFO, "Custom Exporter", "Export button clicked")

    def on_toggle_personal_export(self, state):
        if state == QtCore.Qt.CheckState.Checked:
            print("Personal Export is enabled")
        else:
            print("Personal Export is disabled")

    def on_asset_type_changed(self, current_index):
        current_asset_type_text = self.asset_type_cmbx.itemText(current_index)
        print(f"Asset Type changed to  {current_asset_type_text}")

# Mandatory functions
def start_plugin():
    global custom_exporter
    custom_exporter = CustomExporter()

def close_plugin():
    global custom_exporter
    custom_exporter.delete_widget()

if __name__ == "__main__":
    start_plugin()