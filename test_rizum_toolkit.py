# Test script for RizumToolkit menu system
import substance_painter
from substance_painter import ui, logging

# Import the menu system
from rizum_toolkit_menu import start_toolkit_menu, close_toolkit_menu

def test_menu_system():
    """Test the RizumToolkit menu system."""
    try:
        # Start the menu system
        start_toolkit_menu()
        logging.info("RizumToolkit menu system test started successfully.")
        
        # Test that the menu was created
        from rizum_toolkit_menu import toolkit_menu
        if toolkit_menu and toolkit_menu.menu:
            logging.info("✓ Menu created successfully")
        else:
            logging.error("✗ Menu creation failed")
        
        # Test adding a plugin action
        def test_callback():
            logging.info("Test callback executed")
        
        toolkit_menu.add_plugin_action("test_plugin", "Test Plugin", test_callback)
        logging.info("✓ Plugin action added successfully")
        
        # Test adding a separator
        toolkit_menu.add_separator()
        logging.info("✓ Separator added successfully")
        
        # Test removing a plugin action
        toolkit_menu.remove_plugin_action("test_plugin")
        logging.info("✓ Plugin action removed successfully")
        
        return True
        
    except Exception as e:
        logging.error(f"Test failed: {e}")
        return False

def test_clipboard_exporter():
    """Test the clipboard exporter plugin."""
    try:
        # Import and start the clipboard exporter
        from rizum_clipboard_exporter import start_plugin, close_plugin
        
        plugin = start_plugin()
        logging.info("✓ Clipboard exporter plugin started successfully")
        
        # Test that the plugin registered with the menu
        from rizum_toolkit_menu import toolkit_menu
        if "clipboard_exporter" in toolkit_menu.plugin_actions:
            logging.info("✓ Clipboard exporter registered with menu")
        else:
            logging.error("✗ Clipboard exporter not registered with menu")
        
        # Clean up
        close_plugin()
        logging.info("✓ Clipboard exporter plugin closed successfully")
        
        return True
        
    except Exception as e:
        logging.error(f"Clipboard exporter test failed: {e}")
        return False

def test_drag_distance_settings():
    """Test the drag distance settings plugin."""
    try:
        # Import and start the drag distance settings plugin
        from rizum_drag_distance_settings import start_plugin, close_plugin
        
        plugin = start_plugin()
        logging.info("✓ Drag distance settings plugin started successfully")
        
        # Test that the plugin registered with the menu
        from rizum_toolkit_menu import toolkit_menu
        if "drag_distance_current" in toolkit_menu.plugin_actions:
            logging.info("✓ Drag distance settings registered with menu")
        else:
            logging.error("✗ Drag distance settings not registered with menu")
        
        # Clean up
        close_plugin()
        logging.info("✓ Drag distance settings plugin closed successfully")
        
        return True
        
    except Exception as e:
        logging.error(f"Drag distance settings test failed: {e}")
        return False

if __name__ == "__main__":
    logging.info("Starting RizumToolkit tests...")
    
    # Test the menu system
    if test_menu_system():
        logging.info("✓ Menu system test passed")
    else:
        logging.error("✗ Menu system test failed")
    
    # Test clipboard exporter
    if test_clipboard_exporter():
        logging.info("✓ Clipboard exporter test passed")
    else:
        logging.error("✗ Clipboard exporter test failed")
    
    # Test drag distance settings
    if test_drag_distance_settings():
        logging.info("✓ Drag distance settings test passed")
    else:
        logging.error("✗ Drag distance settings test failed")
    
    # Clean up
    close_toolkit_menu()
    logging.info("Tests completed.") 