"""
Rizum Clipboard Exporter Plugin for Substance Painter
- Provides UI for exporting layer/mask/applied to clipboard
- Includes settings dialog for dilation and bit depth
- Integrates with RizumToolkit menu system
"""
# Painter API import
import substance_painter
from substance_painter import ui, logging

# 3rd party UI lib import
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QDialog, QDialogButtonBox, QCheckBox,
                               QSlider, QComboBox, QSpinBox, QTextEdit, QToolButton)
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction

# Import the shared menu system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rizum_toolkit_menu import get_toolkit_menu

clipboard_exporter = None

class CustomSlider(QSlider):
    """Custom styled slider."""
    
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                height: 4px;
                background: #666666;
                border-radius: 2px;
            }
            
            QSlider::sub-page:horizontal {
                background: #cccccc;
                border-radius: 2px;
            }
            
            QSlider::handle:horizontal {
                background: #cccccc;
                border: none;
                width: 8px;
                height: 16px;
                margin: -6px 0;
            }
            
            QSlider::handle:horizontal:hover {
                background: #dddddd;
            }
        """)

class CustomSpinBox(QSpinBox):
    """Custom styled spinbox."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QSpinBox {
                border: none;
                border-bottom: 2px solid #4d4d4d;
                background: transparent;
                padding: 2px;
                margin-right: 8px;
                text-align: right;
            }
            
            QSpinBox:focus {
                border-bottom: 2px solid #666666;
                background: #1a1a1a;
            }
        """)
        # Set text alignment to right
        self.setAlignment(Qt.AlignRight)

class ClipboardExporterWidget(QWidget):
    """Main widget for the clipboard exporter."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rizum Clipboard Exporter")
        self.setMinimumHeight(100)
        self.setMaximumHeight(250)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(6)  # Reduce vertical spacing
        layout.setContentsMargins(8, 8, 8, 8)  # Tighter margins
        
        # Export buttons in horizontal layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)  # Reduce spacing between buttons
        
        # Layer button
        self.layer_btn = QPushButton("Layer")
        self.layer_btn.clicked.connect(self.export_layer)
        self.layer_btn.setMaximumWidth(self.layer_btn.sizeHint().width())
        buttons_layout.addWidget(self.layer_btn)
        
        # Mask button
        self.mask_btn = QPushButton("Mask")
        self.mask_btn.clicked.connect(self.export_mask)
        self.mask_btn.setMaximumWidth(self.mask_btn.sizeHint().width())
        buttons_layout.addWidget(self.mask_btn)
        
        # Applied button (using QToolButton for better size control)
        self.applied_btn = QToolButton()
        self.applied_btn.setText("⤵️")
        self.applied_btn.clicked.connect(self.export_applied)
        self.applied_btn.setFixedSize(32, 32)
        self.applied_btn.setToolTip("Applied")
        self.applied_btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
        buttons_layout.addWidget(self.applied_btn)
        
        # Add stretch to push buttons to the left
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Instructions section
        self.setup_instructions(layout)
        
        self.setLayout(layout)
    
    def setup_instructions(self, parent_layout):
        """Setup the collapsible instructions section."""
        # Instructions header with toggle button
        header_layout = QHBoxLayout()
        self.toggle_btn = QPushButton("▶ INSTRUCTIONS")
        self.toggle_btn.clicked.connect(self.toggle_instructions)
        font = self.toggle_btn.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() + 1)
        self.toggle_btn.setFont(font)
        self.toggle_btn.setMinimumWidth(200)
        self.toggle_btn.setFixedHeight(28)  # Make button shorter
        header_layout.addWidget(self.toggle_btn)
        parent_layout.addLayout(header_layout)
        
        # Instructions text
        self.instructions_text = QTextEdit()
        self.instructions_text.setMaximumHeight(70)  # Make instructions box shorter
        self.instructions_text.setReadOnly(True)
        self.instructions_text.setPlainText(
            "Layer: Exports the currently selected layer\n"
            "Mask: Exports the mask of the selected layer\n"
            "Applied: Exports the layer with its mask applied"
        )
        self.instructions_text.hide()
        parent_layout.addWidget(self.instructions_text)
    
    def toggle_instructions(self):
        """Toggle the instructions visibility and adjust widget height."""
        if self.instructions_text.isVisible():
            self.instructions_text.hide()
            self.toggle_btn.setText("▶ INSTRUCTIONS")
            self.setMinimumHeight(100)
            self.setMaximumHeight(100)
            self.resize(self.width(), 100)
        else:
            self.instructions_text.show()
            self.toggle_btn.setText("▼ INSTRUCTIONS")
            # Estimate expanded height (can be tweaked)
            expanded_height = 100 + self.instructions_text.maximumHeight()
            self.setMinimumHeight(expanded_height)
            self.setMaximumHeight(250)
            self.resize(self.width(), expanded_height)
    
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
        
        # Dilation slider and spinbox
        dilation_layout = QHBoxLayout()
        dilation_layout.addWidget(QLabel("Dilation (Pixels)"))
        dilation_layout.addStretch()
        
        # Custom slider
        self.dilation_slider = CustomSlider(Qt.Horizontal)
        self.dilation_slider.setRange(1, 256)
        self.dilation_slider.setValue(3)
        self.dilation_slider.setMaximumWidth(200)
        dilation_layout.addWidget(self.dilation_slider)
        
        # Custom spinbox (matching drag_distance settings style)
        self.dilation_spinbox = CustomSpinBox()
        self.dilation_spinbox.setRange(1, 20)
        self.dilation_spinbox.setValue(3)
        self.dilation_spinbox.setMinimumWidth(60)
        self.dilation_spinbox.setMaximumWidth(80)
        dilation_layout.addWidget(self.dilation_spinbox)
        
        # Connect slider and spinbox
        self.dilation_slider.valueChanged.connect(self.dilation_spinbox.setValue)
        self.dilation_spinbox.valueChanged.connect(self.dilation_slider.setValue)
        
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
