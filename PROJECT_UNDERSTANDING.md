# RizumToolkit & Clipboard Exporter Project Understanding

## Project Overview

A Substance 3D Painter plugin system consisting of:
1. **RizumToolkit Menu System** - Shared menu infrastructure for multiple plugins
2. **Clipboard Exporter Plugin** - Export selected layers/masks to clipboard
3. **Drag Distance Settings Plugin** - Adjust application drag distance

## Current Architecture

### 1. RizumToolkit Menu System (`rizum_toolkit_menu.py`)
- **Purpose**: Unified menu system for multiple independent plugins
- **Status**: ✅ Complete and working
- **Features**:
  - Creates "RizumToolkit" menu in Substance Painter
  - Allows plugins to register themselves independently
  - Automatic separators between plugins
  - Proper cleanup and UI management

### 2. Clipboard Exporter Plugin (`rizum_clipboard_exporter/__init__.py`)
- **Purpose**: Export selected layers/masks to clipboard as PNG
- **Status**: 🟡 UI Complete, Export Logic Pending
- **Features**:
  - Dockable widget with Layer/Mask/Applied buttons
  - Collapsible instructions
  - Settings dialog with dilation and bit depth options
  - Integration with RizumToolkit menu

### 3. Drag Distance Settings Plugin (`rizum_drag_distance_settings/__init__.py`)
- **Purpose**: Adjust Substance Painter's drag distance setting
- **Status**: ✅ Complete and working
- **Features**:
  - Shows current drag distance in menu
  - Settings dialog for adjustment
  - Integration with RizumToolkit menu

## Technical Implementation

### UI Components
- **CustomSlider**: Styled slider with progress bar effect
- **CustomSpinBox**: Right-aligned spinbox with custom styling
- **ClipboardExporterWidget**: Main widget with compact layout
- **SettingsDialog**: Settings dialog with dilation and bit depth options

### Menu Integration
- All plugins register with `get_toolkit_menu()`
- Independent installation/uninstallation
- Clean separation of concerns

### Settings Management
- Uses QSettings for persistence
- Separate settings for each plugin
- Proper loading/saving of user preferences

## Export Strategy (Planned)

### Approach: Targeted JSON Export
1. **Get Current Layer**: Use `get_selected_nodes()` and `get_selection_type()`
2. **Create JSON Config**: Configure export to target only the selected layer/mask
3. **Export Single Layer**: Use `export_project_textures(json_config)`
4. **Clipboard Integration**: Read exported PNG and copy to clipboard

### Required Research
- JSON configuration structure for single layer export
- How to specify layer content vs mask in export config
- How to apply user settings (dilation, bit depth) to export

## Current Status

### ✅ Completed
- RizumToolkit menu system
- Clipboard exporter UI (widget and settings dialog)
- Drag distance settings plugin
- Custom styling (slider, spinbox, buttons)
- Settings persistence
- Plugin integration and cleanup

### 🟡 In Progress
- Export logic implementation
- Clipboard integration
- Error handling and user feedback

### ❌ Not Started
- Actual layer/mask export functionality
- PNG to clipboard conversion
- Dilation and bit depth application
- Error handling for edge cases

## File Structure
```
plugins/
├── rizum_toolkit_menu.py              # Shared menu system
├── rizum_clipboard_exporter/
│   └── __init__.py                    # Clipboard exporter plugin
├── rizum_drag_distance_settings/
│   └── __init__.py                    # Drag distance settings plugin
├── test_rizum_toolkit.py              # Test script
├── README_RizumToolkit.md             # Documentation
└── python-doc-md/                     # API documentation
```

## TODOs

### High Priority
1. **Research JSON Export Configuration**
   - Understand how to target single layer in export config
   - Learn how to specify layer content vs mask
   - Figure out how to apply user settings to export

2. **Implement Export Logic**
   - Get selected layer/mask using layerstack API
   - Create targeted JSON configuration
   - Export single layer/mask as PNG

3. **Add Clipboard Integration**
   - Read exported PNG file
   - Copy to system clipboard using Qt
   - Clean up temporary files

### Medium Priority
4. **Apply User Settings**
   - Implement dilation (finite and infinite)
   - Apply bit depth settings (8/16 bits)
   - Handle padding algorithms

5. **Error Handling**
   - No layer selected
   - Export failures
   - Clipboard access issues
   - User-friendly error messages

### Low Priority
6. **Polish and Optimization**
   - Performance optimization
   - Memory management
   - Additional error cases
   - User experience improvements

## Unclear Areas

### 1. JSON Export Configuration
- **Question**: How to construct JSON config to export only a specific layer?
- **Research Needed**: Study the export.md documentation more thoroughly
- **Status**: 🔍 Needs investigation

### 2. Layer/Mask Targeting
- **Question**: How to specify whether to export layer content or mask?
- **Research Needed**: Understand the relationship between layerstack selection and export config
- **Status**: 🔍 Needs investigation

### 3. Settings Application
- **Question**: How to apply dilation and bit depth settings to the export?
- **Research Needed**: Find export parameters for these settings
- **Status**: 🔍 Needs investigation

### 4. Clipboard Integration
- **Question**: Best way to read PNG file and copy to clipboard?
- **Research Needed**: Qt clipboard API and file handling
- **Status**: 🔍 Needs investigation

## API Documentation Available
- `python-doc-md/substance_painter/export.md` - Export functionality
- `python-doc-md/substance_painter/layerstack/` - Layer manipulation
- Local Substance Painter Python API documentation

## Next Steps
1. Deep dive into export.md documentation
2. Research JSON configuration examples
3. Test layer selection and identification
4. Implement basic export functionality
5. Add clipboard integration
6. Apply user settings
7. Add error handling and polish

## Notes
- All UI components are complete and styled
- Menu system is working and extensible
- Settings persistence is implemented
- Plugin architecture is clean and modular
- Ready to implement export logic using the planned approach 