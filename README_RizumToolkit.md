# RizumToolkit Menu System

A shared menu system for Substance 3D Painter plugins that provides a unified "RizumToolkit" menu for multiple independent plugins.

## Overview

The RizumToolkit menu system allows multiple plugins to register themselves under a single "RizumToolkit" menu in Substance Painter's main menu bar. This provides a clean, organized way to access various tools while keeping plugins independent.

## Architecture

### Core Components

1. **`rizum_toolkit_menu.py`** - The shared menu system
2. **Plugin Integration** - Each plugin registers itself with the menu system
3. **Independent Operation** - Plugins can be installed/uninstalled separately

### Menu Structure

```
RizumToolkit
├── Current: X pixels (Drag Distance Settings)
├── Drag Distance Settings
├── ────────────────────── (separator)
├── Clipboard Exporter
└── Clipboard Exporter Settings
```

## Current Plugins

### 1. Drag Distance Settings
- **Current: X pixels** - Shows current drag distance (display only)
- **Drag Distance Settings** - Opens settings dialog to adjust drag distance

### 2. Clipboard Exporter
- **Clipboard Exporter** - Opens the clipboard exporter widget
- **Clipboard Exporter Settings** - Opens settings dialog for export options

## Plugin Integration

To integrate a new plugin with RizumToolkit:

1. **Import the menu system:**
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rizum_toolkit_menu import get_toolkit_menu
```

2. **Register with the menu:**
```python
def setup_menu(self):
    self.toolkit_menu = get_toolkit_menu()
    
    # Add separator if other plugins exist
    if self.toolkit_menu.menu and self.toolkit_menu.menu.actions():
        self.toolkit_menu.add_separator()
    
    # Add your plugin actions
    self.toolkit_menu.add_plugin_action(
        "your_plugin_name",
        "Your Plugin Action",
        self.your_callback_function
    )
```

3. **Clean up on plugin close:**
```python
def close_plugin():
    # Your cleanup code here
    pass
```

## Features

### Shared Menu System
- **Unified Interface**: All plugins appear under one menu
- **Independent Installation**: Plugins can be installed/uninstalled separately
- **Automatic Separators**: Separators are added between different plugins
- **Clean Cleanup**: Proper UI element cleanup when plugins are deactivated

### Plugin Management
- **Dynamic Registration**: Plugins register themselves on startup
- **Action Management**: Easy addition/removal of menu actions
- **Shortcut Support**: Optional keyboard shortcuts for actions
- **State Persistence**: Settings are saved per plugin

## Installation

1. **Install the menu system:**
   - Place `rizum_toolkit_menu.py` in your plugins directory

2. **Install individual plugins:**
   - Place plugin folders (e.g., `rizum_clipboard_exporter/`) in your plugins directory
   - Each plugin will automatically register with the RizumToolkit menu

3. **Restart Substance Painter:**
   - The "RizumToolkit" menu will appear in the main menu bar

## Development

### Adding New Plugins

1. **Create your plugin folder:**
```
your_plugin/
├── __init__.py
└── README.md
```

2. **Implement the plugin interface:**
```python
# In __init__.py
from rizum_toolkit_menu import get_toolkit_menu

class YourPlugin:
    def __init__(self):
        self.toolkit_menu = get_toolkit_menu()
        self.setup_menu()
    
    def setup_menu(self):
        # Register with menu system
        pass

def start_plugin():
    # Initialize your plugin
    pass

def close_plugin():
    # Clean up your plugin
    pass
```

3. **Test your integration:**
```python
# Run the test script
python test_rizum_toolkit.py
```

### Menu System API

#### `RizumToolkitMenu` Class

- **`create_menu()`** - Creates the RizumToolkit menu
- **`add_plugin_action(name, text, callback, shortcut=None)`** - Add a plugin action
- **`add_separator()`** - Add a separator between plugins
- **`remove_plugin_action(name)`** - Remove a plugin action

#### Global Functions

- **`get_toolkit_menu()`** - Get or create the menu instance
- **`start_toolkit_menu()`** - Initialize the menu system
- **`close_toolkit_menu()`** - Clean up the menu system

## Testing

Run the test script to verify the menu system works correctly:

```bash
python test_rizum_toolkit.py
```

This will test:
- Menu system creation
- Plugin registration
- Action management
- Cleanup procedures

## Troubleshooting

### Menu Doesn't Appear
1. Check that `rizum_toolkit_menu.py` is in the correct plugins directory
2. Restart Substance Painter
3. Check the console for error messages

### Plugin Not Showing in Menu
1. Verify the plugin imports the menu system correctly
2. Check that the plugin calls `setup_menu()` in its initialization
3. Ensure the plugin has proper error handling

### Settings Not Persisting
1. Check that the plugin uses QSettings correctly
2. Verify write permissions to the settings directory
3. Check for conflicting plugin names

## Future Enhancements

- **Plugin Categories**: Group plugins by category (e.g., "Export", "Settings")
- **Plugin Dependencies**: Handle plugin dependencies and load order
- **Plugin Configuration**: Allow plugins to configure their menu appearance
- **Plugin Discovery**: Automatic discovery of available plugins
- **Plugin Updates**: System for updating plugins independently

## Compatibility

- **Substance 3D Painter**: Compatible with recent versions
- **Python**: Uses PySide6 for UI components
- **Platform**: Cross-platform compatibility
- **Plugin Architecture**: Follows Substance Painter's official plugin patterns 