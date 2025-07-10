# Painter API import
import substance_painter
from substance_painter import ui, logging

# 3rd party UI lib import
from PySide6 import QtWidgets, QtGui
from PySide6.QtGui import QAction

# Global variables for menu management
rizum_toolkit_menu = None
plugin_ui_elements = []

class RizumToolkitMenu:
    """Shared menu system for RizumToolkit plugins."""
    
    def __init__(self):
        self.menu = None
        self.plugin_actions = {}
    
    def create_menu(self):
        """Create the RizumToolkit menu."""
        # Get the main window
        main_window = ui.get_main_window()
        
        # Create the RizumToolkit menu
        self.menu = QtWidgets.QMenu("RizumToolkit", main_window)
        ui.add_menu(self.menu)
        plugin_ui_elements.append(self.menu)
        
        logging.info("RizumToolkit menu created.")
    
    def add_plugin_action(self, plugin_name, action_text, callback, shortcut=None):
        """Add a plugin action to the menu."""
        if self.menu is None:
            self.create_menu()
        
        action = QAction(action_text, self.menu)
        action.triggered.connect(callback)
        if shortcut:
            action.setShortcut(QtGui.QKeySequence(shortcut))
        
        self.menu.addAction(action)
        self.plugin_actions[plugin_name] = action
        
        logging.info(f"Added {plugin_name} action to RizumToolkit menu.")
    
    def add_separator(self):
        """Add a separator to the menu."""
        if self.menu is None:
            self.create_menu()
        
        self.menu.addSeparator()
    
    def remove_plugin_action(self, plugin_name):
        """Remove a plugin action from the menu."""
        if plugin_name in self.plugin_actions:
            action = self.plugin_actions[plugin_name]
            self.menu.removeAction(action)
            del self.plugin_actions[plugin_name]
            logging.info(f"Removed {plugin_name} action from RizumToolkit menu.")

# Global instance
toolkit_menu = None

def get_toolkit_menu():
    """Get or create the RizumToolkit menu instance."""
    global toolkit_menu
    if toolkit_menu is None:
        toolkit_menu = RizumToolkitMenu()
    return toolkit_menu

def start_toolkit_menu():
    """Initialize the RizumToolkit menu system."""
    global toolkit_menu
    toolkit_menu = get_toolkit_menu()
    toolkit_menu.create_menu()
    logging.info("RizumToolkit menu system started.")

def close_toolkit_menu():
    """Clean up the RizumToolkit menu system."""
    global toolkit_menu, plugin_ui_elements
    
    # Remove all added UI elements
    for element in plugin_ui_elements:
        try:
            ui.delete_ui_element(element)
        except Exception as e:
            logging.warning(f"Error deleting UI element: {e}")
    
    plugin_ui_elements.clear()
    toolkit_menu = None
    
    logging.info("RizumToolkit menu system closed.")

if __name__ == "__main__":
    start_toolkit_menu() 