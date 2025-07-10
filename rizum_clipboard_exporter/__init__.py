# Painter API import
import substance_painter
from substance_painter import ui, logging

# 3rd party UI lib import
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QDialog, QDialogButtonBox, QCheckBox,
                               QSlider, QComboBox, QSpinBox, QTextEdit, QFrame,
                               QGroupBox)
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction

# Import the shared menu system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rizum_toolkit_menu import get_toolkit_menu

clipboard_exporter = None
plugin_ui_elements = []

class ClipboardExporterWidget(QWidget):
    """Main widget for the clipboard exporter."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rizum Clipboard Exporter")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        
        # Export buttons in horizontal layout
        buttons_layout = QHBoxLayout()
        self.layer_btn = QPushButton("Layer")
        self.layer_btn.clicked.connect(self.export_layer)
        buttons_layout.addWidget(self.layer_btn)
        
        self.mask_btn = QPushButton("Mask")
        self.mask_btn.clicked.connect(self.export_mask)
        buttons_layout.addWidget(self.mask_btn)
        
        self.applied_btn = QPushButton("Applied")
        self.applied_btn.clicked.connect(self.export_applied)
        buttons_layout.addWidget(self.applied_btn)
        
        layout.addLayout(buttons_layout)
        
        # Instructions section
        self.setup_instructions(layout)
        
        self.setLayout(layout)
    
    def setup_instructions(self, parent_layout):
        """Setup the instructions section as a group box."""
        # Instructions group box
        self.instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout()
        
        # Instructions text
        self.instructions_text = QTextEdit()
        self.instructions_text.setMaximumHeight(100)
        self.instructions_text.setReadOnly(True)
        self.instructions_text.setPlainText(
            "Layer: Exports the currently selected layer\n"
            "Mask: Exports the mask of the selected layer\n"
            "Applied: Exports the layer with its mask applied"
        )
        instructions_layout.addWidget(self.instructions_text)
        
        self.instructions_group.setLayout(instructions_layout)
        parent_layout.addWidget(self.instructions_group)
    
    def export_layer(self):
        """Export the current layer to clipboard."""
        # TODO: Implement layer export
        logging.info("Export Layer clicked")
    
    def export_mask(self):
        """Export the current mask to clipboard."""
        # TODO: Implement mask export
        logging.info("Export Mask clicked")
    
    def export_applied(self):
        """Export the layer with mask applied to clipboard."""
        # TODO: Implement applied export
        logging.info("Export Applied clicked")

class SettingsDialog(QDialog):
    """Settings dialog for clipboard exporter."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clipboard Exporter Settings")
        self.setModal(True)
        self.resize(350, 200)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the settings dialog UI."""
        layout = QVBoxLayout()
        
        # Infinite Dilation toggle (left centered, toggle right centered)
        infinite_dilation_layout = QHBoxLayout()
        infinite_dilation_layout.addWidget(QLabel("Infinite Dilation"))
        infinite_dilation_layout.addStretch()
        self.infinite_dilation_cb = QCheckBox()
        infinite_dilation_layout.addWidget(self.infinite_dilation_cb)
        self.infinite_dilation_cb.toggled.connect(self.on_infinite_dilation_toggled)
        layout.addLayout(infinite_dilation_layout)
        
        # Dilation slider (left centered, indented, no spinbox)
        dilation_layout = QHBoxLayout()
        dilation_layout.addSpacing(20)  # Indent
        dilation_layout.addWidget(QLabel("Dilation (Pixels)"))
        dilation_layout.addStretch()
        self.dilation_slider = QSlider(Qt.Horizontal)
        self.dilation_slider.setRange(1, 20)
        self.dilation_slider.setValue(3)
        self.dilation_slider.setMaximumWidth(150)
        dilation_layout.addWidget(self.dilation_slider)
        layout.addLayout(dilation_layout)
        
        # Bit depth dropdown (left centered, dropdown right centered)
        bit_depth_layout = QHBoxLayout()
        bit_depth_layout.addWidget(QLabel("Bit Depth"))
        bit_depth_layout.addStretch()
        self.bit_depth_combo = QComboBox()
        self.bit_depth_combo.addItems(["8 bits", "16 bits"])
        self.bit_depth_combo.setMaximumWidth(100)
        bit_depth_layout.addWidget(self.bit_depth_combo)
        layout.addLayout(bit_depth_layout)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def on_infinite_dilation_toggled(self, checked):
        """Handle infinite dilation toggle."""
        self.dilation_slider.setEnabled(not checked)
    
    def load_settings(self):
        """Load current settings from QSettings."""
        settings = QSettings("RizumClipboardExporter", "Settings")
        infinite_dilation = settings.value("infinite_dilation", False, type=bool)
        dilation_pixels = settings.value("dilation_pixels", 3, type=int)
        bit_depth = settings.value("bit_depth", "8 bits", type=str)
        
        self.infinite_dilation_cb.setChecked(infinite_dilation)
        self.dilation_slider.setValue(dilation_pixels)
        self.bit_depth_combo.setCurrentText(bit_depth)
        
        # Update UI state
        self.on_infinite_dilation_toggled(infinite_dilation)
    
    def save_settings(self):
        """Save current settings to QSettings."""
        settings = QSettings("RizumClipboardExporter", "Settings")
        settings.setValue("infinite_dilation", self.infinite_dilation_cb.isChecked())
        settings.setValue("dilation_pixels", self.dilation_slider.value())
        settings.setValue("bit_depth", self.bit_depth_combo.currentText())

class RizumClipboardExporter:
    """Main plugin class for clipboard exporter."""
    
    def __init__(self):
        self.widget = None
        self.settings_dialog = None
        self.toolkit_menu = get_toolkit_menu()
        self.setup_menu()
    
    def setup_menu(self):
        """Setup menu integration with RizumToolkit."""
        # Add separator if other plugins exist
        if self.toolkit_menu.menu and self.toolkit_menu.menu.actions():
            self.toolkit_menu.add_separator()
        
        # Add clipboard exporter action
        self.toolkit_menu.add_plugin_action(
            "clipboard_exporter",
            "Clipboard Exporter",
            self.show_widget
        )
        
        # Add settings action
        self.toolkit_menu.add_plugin_action(
            "clipboard_settings",
            "Clipboard Exporter Settings",
            self.show_settings
        )
    
    def show_widget(self):
        """Show the clipboard exporter widget."""
        if self.widget is None:
            self.widget = ClipboardExporterWidget()
            ui.add_dock_widget(self.widget)
        else:
            self.widget.show()
            self.widget.raise_()
    
    def show_settings(self):
        """Show the settings dialog."""
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog()
        
        if self.settings_dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings_dialog.save_settings()
    
    def delete_widget(self):
        """Delete the widget."""
        if self.widget is not None:
            ui.delete_ui_element(self.widget)
            self.widget = None

def start_plugin():
    """Called when the plugin is started."""
    global clipboard_exporter
    
    # Clean up any existing instance first
    if clipboard_exporter is not None:
        close_plugin()
    
    # Create new instance
    clipboard_exporter = RizumClipboardExporter()
    
    logging.info("Rizum Clipboard Exporter activated.")
    return clipboard_exporter

def close_plugin():
    """Called when the plugin is stopped."""
    global clipboard_exporter
    
    if clipboard_exporter is not None:
        clipboard_exporter.delete_widget()
        clipboard_exporter = None
    
    logging.info("Rizum Clipboard Exporter deactivated.")

if __name__ == "__main__":
    start_plugin()
