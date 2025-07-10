# Painter API import
import substance_painter
from substance_painter import ui, logging

# 3rd party UI lib import
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QDialog, QDialogButtonBox
from PySide6.QtCore import QSettings
from PySide6.QtGui import QAction

# Import the shared menu system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rizum_toolkit_menu import get_toolkit_menu

rizum_drag_distance_plugin = None
plugin_ui_elements = []

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Drag Distance Settings")
        self.setModal(True)
        self.resize(241, 100)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create spin box for drag distance
        spin_layout = QHBoxLayout()
        label = QLabel("Drag Distance:")
        self.spin_box = QSpinBox()
        self.spin_box.setRange(1, 100)
        self.spin_box.setValue(15)
        pixels_label = QLabel("pixels")
        
        # Add label on the left
        spin_layout.addWidget(label)
        # Add stretch to push spinbox and pixels to the right
        spin_layout.addStretch()
        # Add spinbox and pixels label on the right
        spin_layout.addWidget(self.spin_box)
        spin_layout.addWidget(pixels_label)
        
        # Add to main layout
        layout.addLayout(spin_layout)
        
        # Add dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Load current settings
        self.load_settings()
    
    def load_settings(self):
        """Load current settings from QSettings."""
        settings = QSettings("RizumDragDistance", "Settings")
        drag_distance = settings.value("drag_distance", 15, type=int)
        self.spin_box.setValue(drag_distance)
    
    def save_settings(self):
        """Save current settings to QSettings."""
        settings = QSettings("RizumDragDistance", "Settings")
        settings.setValue("drag_distance", self.spin_box.value())
    
    def get_drag_distance(self):
        """Get the current drag distance value."""
        return self.spin_box.value()

class RizumDragDistanceSettings:
    def __init__(self):
        self.current_action = None
        self.settings_action = None
        self.toolkit_menu = get_toolkit_menu()
        # Apply settings on startup
        self.apply_current_settings()
        self.setup_menu()
    
    def setup_menu(self):
        """Setup menu integration with RizumToolkit."""
        # Add separator if other plugins exist
        if self.toolkit_menu.menu and self.toolkit_menu.menu.actions():
            self.toolkit_menu.add_separator()
        
        # Add current value action (display only)
        self.toolkit_menu.add_plugin_action(
            "drag_distance_current",
            "Current: 15 pixels",
            self.show_current_value
        )
        
        # Add settings action
        self.toolkit_menu.add_plugin_action(
            "drag_distance_settings",
            "Drag Distance Settings",
            self.open_settings
        )
        
        # Store references for updating text
        self.current_action = self.toolkit_menu.plugin_actions.get("drag_distance_current")
        self.settings_action = self.toolkit_menu.plugin_actions.get("drag_distance_settings")
    
    def get_current_drag_distance(self):
        """Get the current drag distance from QApplication."""
        return QtWidgets.QApplication.startDragDistance()
    
    def apply_current_settings(self):
        """Apply the current drag distance setting."""
        settings = QSettings("RizumDragDistance", "Settings")
        drag_distance = settings.value("drag_distance", 15, type=int)
        
        # Set the QApplication start drag distance
        QtWidgets.QApplication.setStartDragDistance(drag_distance)
        
        logging.info(f"Drag distance set to {drag_distance} pixels")
        self.update_current_action_text()
    
    def update_current_action_text(self):
        """Update the current value action text."""
        current_distance = self.get_current_drag_distance()
        if self.current_action is not None:
            self.current_action.setText(f"Current: {current_distance} pixels")
    
    def open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog.save_settings()
            self.apply_current_settings()
    
    def show_current_value(self):
        """Show current drag distance (display only action)."""
        current_distance = self.get_current_drag_distance()
        logging.info(f"Current drag distance: {current_distance} pixels")

def start_plugin():
    """Called when the plugin is started."""
    global rizum_drag_distance_plugin
    
    # Clean up any existing instance first
    if rizum_drag_distance_plugin is not None:
        close_plugin()
    
    # Create new instance
    rizum_drag_distance_plugin = RizumDragDistanceSettings()
    
    logging.info("Rizum Drag Distance Settings activated.")
    return rizum_drag_distance_plugin

def close_plugin():
    """Called when the plugin is stopped."""
    global rizum_drag_distance_plugin, plugin_ui_elements
    
    # Remove all added UI elements
    for element in plugin_ui_elements:
        try:
            ui.delete_ui_element(element)
        except Exception as e:
            logging.warning(f"Error deleting UI element: {e}")
    
    plugin_ui_elements.clear()
    rizum_drag_distance_plugin = None
    
    logging.info("Rizum Drag Distance Settings deactivated.") 