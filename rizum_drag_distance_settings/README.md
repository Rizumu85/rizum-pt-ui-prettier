# Rizum Drag Distance Settings Plugin

A Substance 3D Painter plugin that provides easy access to view and modify the application's drag distance setting through a menu interface.

## Features

- **Menu Integration**: Adds a "DragDistance" menu to Substance Painter's main menu bar
- **Current Value Display**: Shows the current drag distance setting in the menu
- **Settings Dialog**: Provides a user-friendly dialog to adjust the drag distance value
- **Persistent Settings**: Settings are saved and restored between application sessions
- **Real-time Updates**: Menu text updates automatically when settings change

## Menu Structure

The plugin creates a menu with two options:

```
DragDistance
├── "Current: X pixels" (display only)
└── "Settings..." (opens configuration dialog)
```

## Usage

### Installation
1. Place the `rizum_drag_distance_settings` folder in your Substance Painter plugins directory
2. Restart Substance Painter or reload plugins
3. The "DragDistance" menu will appear in the main menu bar

### Viewing Current Setting
- Click on "Current: X pixels" in the DragDistance menu
- The current drag distance value will be logged to the console
- The menu text always shows the current value

### Adjusting Settings
1. Click "Settings..." in the DragDistance menu
2. Adjust the drag distance value (1-100 pixels) using the spin box
3. Click "OK" to save and apply the new setting
4. The menu text will update automatically

## What is Drag Distance?

The drag distance setting determines how far a user must drag the mouse before a drag operation begins. This helps prevent accidental drag operations while still allowing intentional drags.

- **Lower values** (1-10 pixels): More sensitive, drags start quickly
- **Higher values** (20-100 pixels): Less sensitive, requires more deliberate dragging

## Default Value

The default drag distance is set to 15 pixels, which provides a good balance between preventing accidental drags and allowing intentional drag operations.

## Settings Storage

Settings are stored using QSettings under the "RizumDragDistance" organization and "Settings" application name, ensuring they persist between Substance Painter sessions.

## Technical Details

- **API Integration**: Uses Substance Painter's official `ui` and `logging` APIs
- **Qt Integration**: Leverages PySide6 for UI components and QApplication for drag distance control
- **Error Handling**: Includes proper error handling and logging for all operations
- **Cleanup**: Properly removes UI elements when the plugin is deactivated

## Compatibility

- **Substance 3D Painter**: Compatible with recent versions
- **Python**: Uses PySide6 for UI components
- **Platform**: Cross-platform compatibility

## Troubleshooting

If the menu doesn't appear:
1. Check that the plugin folder is in the correct plugins directory
2. Restart Substance Painter
3. Check the console for any error messages

If settings don't persist:
1. Check that the application has write permissions to the settings directory
2. Try resetting the plugin by removing and re-adding it

## Development

The plugin follows Substance Painter's official plugin development patterns:
- Uses `start_plugin()` and `close_plugin()` lifecycle functions
- Properly manages UI element cleanup
- Follows the official API patterns for menu creation and management 