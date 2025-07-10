# Painter API import
import substance_painter
from substance_painter import ui, logging

# 3rd party UI lib import
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QDialog, QDialogButtonBox, QCheckBox,
                               QSlider, QComboBox, QSpinBox, QTextEdit, QFrame)
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
        
        # Export buttons
        self.layer_btn = QPushButton("Layer")
        self.layer_btn.clicked.connect(self.export_layer)
        layout.addWidget(self.layer_btn)
        
        self.mask_btn = QPushButton("Mask")
        self.mask_btn.clicked.connect(self.export_mask)
        layout.addWidget(self.mask_btn)
        
        self.applied_btn = QPushButton("Applied")
        self.applied_btn.clicked.connect(self.export_applied)
        layout.addWidget(self.applied_btn)
        
        # Instructions section
        self.setup_instructions(layout)
        
        self.setLayout(layout)
    
    def setup_instructions(self, parent_layout):
        """Setup the collapsible instructions section."""
        # Instructions frame
        self.instructions_frame = QFrame()
        self.instructions_frame.setFrameStyle(QFrame.StyledPanel)
        instructions_layout = QVBoxLayout()
        
        # Instructions header with toggle button
        header_layout = QHBoxLayout()
        self.toggle_btn = QPushButton("▼ Instructions")
        self.toggle_btn.setMaximumWidth(120)
        self.toggle_btn.clicked.connect(self.toggle_instructions)
        header_layout.addWidget(self.toggle_btn)
        header_layout.addStretch()
        instructions_layout.addLayout(header_layout)
        
        # Instructions text
        self.instructions_text = QTextEdit()
        self.instructions_text.setMaximumHeight(100)
        self.instructions_text.setReadOnly(True)
        self.instructions_text.setPlainText(
            "Layer: Exports the currently selected layer\n"
            "Mask: Exports the mask of the selected layer\n"
            "Applied: Exports the layer with its mask applied"
        )
        self.instructions_text.hide()
        instructions_layout.addWidget(self.instructions_text)
        
        self.instructions_frame.setLayout(instructions_layout)
        parent_layout.addWidget(self.instructions_frame)
    
    def toggle_instructions(self):
        """Toggle the instructions visibility."""
        if self.instructions_text.isVisible():
            self.instructions_text.hide()
            self.toggle_btn.setText("▼ Instructions")
        else:
            self.instructions_text.show()
            self.toggle_btn.setText("▲ Instructions")
    
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
        self.resize(300, 200)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the settings dialog UI."""
        layout = QVBoxLayout()
        
        # Infinite Dilation toggle
        self.infinite_dilation_cb = QCheckBox("Enable Infinite Dilation")
        layout.addWidget(self.infinite_dilation_cb)
        self.infinite_dilation_cb.toggled.connect(self.on_infinite_dilation_toggled)
        
        # Dilation slider (only visible when infinite dilation is off)
        dilation_layout = QHBoxLayout()
        dilation_layout.addWidget(QLabel("Dilation (Pixels):"))
        self.dilation_slider = QSlider(Qt.Horizontal)
        self.dilation_slider.setRange(1, 20)
        self.dilation_slider.setValue(3)
        dilation_layout.addWidget(self.dilation_slider)
        self.dilation_spinbox = QSpinBox()
        self.dilation_spinbox.setRange(1, 20)
        self.dilation_spinbox.setValue(3)
        dilation_layout.addWidget(self.dilation_spinbox)
        
        # Connect slider and spinbox
        self.dilation_slider.valueChanged.connect(self.dilation_spinbox.setValue)
        self.dilation_spinbox.valueChanged.connect(self.dilation_slider.setValue)
        
        layout.addLayout(dilation_layout)
        
        # Bit depth dropdown
        bit_depth_layout = QHBoxLayout()
        bit_depth_layout.addWidget(QLabel("Bit Depth:"))
        self.bit_depth_combo = QComboBox()
        self.bit_depth_combo.addItems(["8 bits", "16 bits"])
        bit_depth_layout.addWidget(self.bit_depth_combo)
        bit_depth_layout.addStretch()
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
        self.dilation_spinbox.setEnabled(not checked)
    
    def load_settings(self):
        """Load current settings from QSettings."""
        settings = QSettings("RizumClipboardExporter", "Settings")
        infinite_dilation = settings.value("infinite_dilation", False, type=bool)
        dilation_pixels = settings.value("dilation_pixels", 3, type=int)
        bit_depth = settings.value("bit_depth", "8 bits", type=str)
        
        self.infinite_dilation_cb.setChecked(infinite_dilation)
        self.dilation_slider.setValue(dilation_pixels)
        self.dilation_spinbox.setValue(dilation_pixels)
        self.bit_depth_combo.setCurrentText(bit_depth)
        
        # Update UI state
        self.on_infinite_dilation_toggled(infinite_dilation)
    
    def save_settings(self):
        """Save current settings to QSettings."""
        settings = QSettings("RizumClipboardExporter", "Settings")
        settings.setValue("infinite_dilation", self.infinite_dilation_cb.isChecked())
        settings.setValue("dilation_pixels", self.dilation_spinbox.value())
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
