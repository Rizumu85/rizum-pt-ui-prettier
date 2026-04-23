# SDF Real-Time Generator — Implementation Plan

## Goal

Build a Substance Painter Python plugin that:
1. Sets up a flexible layer structure for real-time SDF painting in User0.
2. Provides a UI to manage frames (add, remove, reorder, sync values, mask mode toggle).
3. Supports borrowing shapes from other channels via anchor points.
4. Supports external editing round-trips (export frame → edit in Photoshop/CSP → reimport).
5. Optionally bakes a production-quality SDF using the SDF interpolation algorithm.

---

## Architecture Overview

```
Plugin UI (PySide6 Panel)
    ├── [Setup SDF Group]
    ├── Frame list (live-synced with layer stack)
    │     └── Per row: name, angle %, [+/-] mode, [→] select, [↑] export, [↓] import
    ├── [+ Add Frame]   [↺ Sync Values]
    ├── [⊕ Borrow Shape]
    └── [⚙ Bake SDF]

Layer Stack — User0 Channel:
    SDF_Generator [Group]
        Frame_03 [Fill, value=0.7]
            MASK:
                PaintEffectNode        ← SP corrections on top
                FillEffectNode         ← external PNG (optional)
                PaintEffectNode        ← duplicated from Frame_02, modified (optional)
                PaintEffectNode        ← main painting
                FillEffectNode [base]  ← black (additive) or white (subtractive)
        Frame_02 [Fill, value=0.8]
            MASK: ...
        Frame_01 [Fill, value=0.9]
            MASK: ...
```

**Why fill layers (not groups) as the frame unit**: a fill layer's mask stack accepts any number
of `PaintEffectNode` and `FillEffectNode` layers. This covers all user scenarios without
needing groups-within-groups (which the API does not allow in mask stacks).

---

## Phase 1: Initial Setup

### `setup_sdf_group(n_frames)`

Creates the `SDF_Generator` group with N fill layers, each with a threshold fill value and a
two-effect mask stack (base fill + one paint effect). Wrapped in `ScopedModification` for
single-step undo.

```python
import substance_painter as sp

USER0 = sp.textureset.ChannelType.User0

def setup_sdf_group(n_frames: int = 9):
    stack = sp.textureset.get_active_stack()
    if USER0 not in stack.all_channels():
        raise ValueError("User0 channel not found. Add it in Texture Set Settings.")

    with sp.layerstack.ScopedModification("Setup SDF Generator"):
        pos = sp.layerstack.InsertPosition.from_textureset_stack(stack)
        group = sp.layerstack.insert_group(pos)
        group.set_name("SDF_Generator")

        # inside_node(group, Substack) inserts at the TOP each time.
        # Iterate 1→N so Frame_01 stays at the bottom and Frame_N ends up at
        # the top. Values run high→low bottom-to-top, so the narrowest frame
        # (deepest shadow only) is at the bottom and the stack broadens upward.
        # Matches FaceShadowBlend's `a→h` ordering (a=narrowest at bottom).
        for i in range(1, n_frames + 1):
            _insert_frame(group, i, n_frames, additive=True)
```

### `_insert_frame(group, index, total, additive)`

```python
def _insert_frame(group, index: int, total: int, additive: bool = True):
    value = round((total - index + 1) / total, 6)
    pos = sp.layerstack.InsertPosition.inside_node(
        group, sp.layerstack.NodeStack.Substack)

    fill = sp.layerstack.insert_fill(pos)
    fill.set_name(_frame_name(index, value))
    fill.set_source(USER0, sp.colormanagement.Color(value, value, value))
    fill.active_channels = {USER0}

    bg = sp.layerstack.MaskBackground.Black if additive \
         else sp.layerstack.MaskBackground.White
    fill.add_mask(bg)

    mask_pos = sp.layerstack.InsertPosition.inside_node(
        fill, sp.layerstack.NodeStack.Mask)
    # Base fill sets the starting canvas (black or white)
    base = sp.layerstack.insert_fill(mask_pos)
    base.set_name("base")
    base.set_source(None, sp.colormanagement.Color(
        0.0, 0.0, 0.0) if additive else sp.colormanagement.Color(1.0, 1.0, 1.0))
    # Empty paint effect — user paints here
    paint = sp.layerstack.insert_paint(mask_pos)
    paint.set_name("paint")

def _frame_name(index: int, value: float) -> str:
    return f"Frame_{index:02d}  [{int(round(value * 100))}%]"

def _find_sdf_group() -> sp.layerstack.GroupLayerNode | None:
    for node in sp.layerstack.get_root_layer_nodes(
            sp.textureset.get_active_stack()):
        if node.get_name() == "SDF_Generator":
            return node
    return None
```

**Verify**: `SDF_Generator` group has N fill layers. Each has a mask with a base fill effect +
one empty paint effect. User0 values run high → low bottom-to-top, so `Frame_01` is the
**narrowest** frame (deep-shadow / always-shadowed regions only) and `Frame_N` is the
broadest. This matches FaceShadowBlend's `a→h` order and proper SDF semantics
(high threshold value = pixel stays in shadow even at high NdotL).

---

## Phase 2: Sync Values

Redistributes gray threshold values evenly based on current layer count and order.
Safe to run any time: after inserting a frame, deleting one, or reordering by hand.

```python
def _sync_frame_values_impl(group):
    """Inner implementation — no ScopedModification wrapper.
    Called by sync_frame_values() (standalone) and add_frame() (inside its own scope).
    """
    # sub_layers() = top-to-bottom; reverse for bottom=index 1
    layers = list(reversed(group.sub_layers()))
    total = len(layers)
    if total == 0:
        return
    for i, layer in enumerate(layers, start=1):
        value = round((total - i + 1) / total, 6)
        layer.set_source(USER0,
                         sp.colormanagement.Color(value, value, value))
        layer.set_name(_frame_name(i, value))

def sync_frame_values():
    """Standalone sync — wraps _sync_frame_values_impl in its own ScopedModification."""
    group = _find_sdf_group()
    if group is None:
        raise RuntimeError("SDF_Generator group not found.")
    with sp.layerstack.ScopedModification("Sync SDF Frame Values"):
        _sync_frame_values_impl(group)
```

**Verify**: Drag layers to reorder → click Sync → all names and fill values update correctly.

---

## Phase 3: Per-Frame Controls

### Add Frame

Inserts a new empty frame above the given reference layer (or at the top of the group), then
calls `sync_frame_values()` to redistribute all values.

```python
def add_frame(reference_layer=None):
    group = _find_sdf_group()
    if group is None:
        raise RuntimeError("SDF_Generator group not found.")

    with sp.layerstack.ScopedModification("Add SDF Frame"):
        if reference_layer is not None:
            pos = sp.layerstack.InsertPosition.above_node(reference_layer)
        else:
            pos = sp.layerstack.InsertPosition.inside_node(
                group, sp.layerstack.NodeStack.Substack)

        fill = sp.layerstack.insert_fill(pos)
        fill.set_name("Frame_new")
        fill.set_source(USER0, sp.colormanagement.Color(0.5, 0.5, 0.5))
        fill.active_channels = {USER0}
        fill.add_mask(sp.layerstack.MaskBackground.Black)
        mask_pos = sp.layerstack.InsertPosition.inside_node(
            fill, sp.layerstack.NodeStack.Mask)
        base = sp.layerstack.insert_fill(mask_pos)
        base.set_name("base")
        base.set_source(None, sp.colormanagement.Color(0.0, 0.0, 0.0))
        paint = sp.layerstack.insert_paint(mask_pos)
        paint.set_name("paint")

        # Sync inside the same ScopedModification → single undo step.
        # Uses _sync_frame_values_impl (no wrapper) to avoid nested ScopedModification.
        _sync_frame_values_impl(group)
```

### Mask Mode Toggle (Additive ↔ Subtractive)

```python
def set_frame_mask_mode(frame_fill, additive: bool):
    """
    Toggle between additive (black base, paint white to add shadow)
    and subtractive (white base, paint black to remove shadow).
    Updates both the mask background and the base fill effect color.
    """
    bg = sp.layerstack.MaskBackground.Black if additive \
         else sp.layerstack.MaskBackground.White
    base_color = sp.colormanagement.Color(0.0, 0.0, 0.0) if additive \
                 else sp.colormanagement.Color(1.0, 1.0, 1.0)

    frame_fill.set_mask_background(bg)

    # Update the base fill effect color to match
    for effect in frame_fill.mask_effects():
        if effect.get_name() == "base":
            effect.set_source(None, base_color)
            break
```

**When to use each mode**:

| Frame | Shadow size | Recommended mode |
|---|---|---|
| Frame_01–03 | Small (deep shadow only) | Additive — start black and paint tight white patches in the deepest crevices |
| Frame_04–06 | Medium | Additive by default; subtractive is optional if carve-out feels easier |
| Frame_07–09 | Large (most of face) | Additive — paint progressively broader white regions that contain the smaller frames below |

### Duplicate-and-modify (no plugin code needed)

Artist right-clicks a `PaintEffectNode` in one frame's mask stack in SP's Layers panel,
selects Duplicate, drags the copy into another frame's mask stack. Native SP behavior —
plugin does not handle this.

---

## Phase 4: Borrow Shape from Another Channel

When an artist wants to reuse a shape already painted elsewhere (e.g., a knee from BaseColor):

1. An `AnchorPointEffectNode` is placed above the source layer to expose its output.
2. A `FillEffectNode` in the SDF frame's mask references that anchor point.
3. A `LevelsEffectNode` above it thresholds the borrowed shape to clean black/white.

```python
def borrow_shape_from_layer(source_layer, target_frame_fill):
    """
    Place an anchor point above source_layer in its own stack,
    then wire it into target_frame_fill's mask stack with a levels effect.
    """
    with sp.layerstack.ScopedModification("Borrow Shape for SDF Frame"):
        # CONSTRAINT: AnchorPointEffectNode can ONLY go inside Content or Mask
        # stacks — NOT above/below a LayerNode. Use NodeStack.Content.
        anchor_pos = sp.layerstack.InsertPosition.inside_node(
            source_layer, sp.layerstack.NodeStack.Content)
        anchor = sp.layerstack.insert_anchor_point_effect(anchor_pos)
        anchor.set_name(f"anchor_{source_layer.get_name()}")

        # FillEffectNode in the SDF frame mask referencing the anchor
        mask_pos = sp.layerstack.InsertPosition.inside_node(
            target_frame_fill, sp.layerstack.NodeStack.Mask)
        fill_ref = sp.layerstack.insert_fill(mask_pos)
        fill_ref.set_name(f"borrow_{source_layer.get_name()}")
        fill_ref.set_source(None, anchor)  # None = mask context

        # Levels effect above it to threshold → clean black/white mask
        levels = sp.layerstack.insert_levels_effect(mask_pos)
        levels.set_name("Threshold (adjust me)")
```

**Live reference**: if the user modifies the source layer in BaseColor, the SDF mask updates
automatically. No re-export needed.

**Plugin UI**: "Borrow Shape" button — requires user to have one layer selected in SP's panel
(the source) and one SDF frame selected in the plugin list (the target).

```python
def ui_borrow_shape(target_frame_fill):
    selected = sp.layerstack.get_selected_nodes(
        sp.textureset.get_active_stack())
    if not selected:
        raise RuntimeError("Select the source layer in SP's Layers panel first.")
    borrow_shape_from_layer(selected[0], target_frame_fill)
```

---

## Phase 5: External Editing Round-Trip

For editing a frame's mask in Photoshop, Clip Studio Paint, or any external app.

### Export frame for external editing

Exports the current composited mask of one frame by isolating it with visibility toggle.

```python
import os, tempfile

def export_frame_for_external(frame_fill, output_path: str):
    """
    Export the composited User0 output of this one frame to a PNG.
    Hides all other frames, exports, restores visibility.
    """
    group = _find_sdf_group()
    all_frames = group.sub_layers()

    for f in all_frames:
        f.set_visible(f.uid() == frame_fill.uid())

    try:
        texture_set_name = (sp.textureset.get_active_stack()
                            .get_texture_set().name())
        out_dir = os.path.dirname(output_path)
        out_name = os.path.splitext(os.path.basename(output_path))[0]
        config = {
            "exportPath": out_dir,
            "defaultExportPreset": "frame_ext_export",
            "exportPresets": [{"name": "frame_ext_export", "maps": [{
                "fileName": out_name,
                "channels": [{"destChannel": "L", "srcChannel": "R",
                              "srcMapType": "documentMap",
                              "srcMapName": "user0"}],
                "parameters": {"fileFormat": "png", "bitDepth": "16",
                               "paddingAlgorithm": "transparent"}
            }]}],
            "exportList": [{"rootPath": texture_set_name}]
        }
        # NOTE: destChannel "L" (Luminance) produces a proper grayscale PNG.
        # Using "R" alone creates an R-only PNG where cv2's BGR→gray conversion
        # computes 0.299×R = 76 for white, which binarizes to black at threshold 127.
        sp.export.export_project_textures(config)
    finally:
        for f in all_frames:
            f.set_visible(True)
```

### Import external edit back

First import: creates a new `FillEffectNode` in the mask stack with the bitmap.
Subsequent imports: re-import the bitmap and ensure the refreshed external result becomes the
topmost visible mask contribution for that frame.

```python
def import_external_edit(frame_fill, png_path: str):
    """
    Import a PNG from external software into the frame's mask stack.
    Sets GenericColorSpace.Raw to prevent gamma correction on the mask values.

    On every import round-trip, the external fill should end up at the TOP of the
    mask stack so the latest external pass wins visually, even if the user added
    new PaintEffectNode layers in SP after the previous import.

    NOTE: We re-import and reposition the external fill rather than relying on
    reload_modified_resources_async(ResourcesListFilter([id])). Same-path auto-
    reload only refreshes pixels on the existing resource/effect and preserves
    the current stack order. Explicit import keeps the ordering deterministic,
    works even if the file path changed between edits, and returns synchronously
    (no need to wait for ReloadResourcesEnded).
    """
    # Track any older external fills already present in this frame's mask
    existing_fills = [
        effect for effect in frame_fill.mask_effects()
        if effect.get_name().startswith("ext_")
    ]

    # Import the resource (both first-time and update paths need this)
    resource = sp.resource.import_project_resource(
        png_path,
        sp.resource.Usage.TEXTURE,
        name=f"ext_{frame_fill.get_name()}")
    resource_id = resource.identifier()

    # Always insert relative to the current top mask effect, not relative to the
    # previous ext_* node. This guarantees the latest external import ends up
    # above any SP paint effects the user added after the prior round-trip.
    effects = frame_fill.mask_effects()
    if effects:
        new_pos = sp.layerstack.InsertPosition.above_node(effects[0])
    else:
        new_pos = sp.layerstack.InsertPosition.inside_node(
            frame_fill, sp.layerstack.NodeStack.Mask)

    fill_effect = sp.layerstack.insert_fill(new_pos)
    fill_effect.set_name(f"ext_{frame_fill.get_name()}")
    source = fill_effect.set_source(None, resource_id)
    source.set_color_space(sp.colormanagement.GenericColorSpace.Raw)

    for old_fill in existing_fills:
        sp.layerstack.delete_node(old_fill)
```

**Why `GenericColorSpace.Raw`**: external apps paint in sRGB. SP's mask channel is linear.
A 0.5 gray in sRGB becomes ~0.214 in linear after gamma conversion — mask boundaries shift
visibly. Raw bypasses this conversion so painted values come through unchanged.
Note: `DataColorSpace` only has `Data` and `DataSigned` — no `.Raw`. Use `GenericColorSpace.Raw`.

**Re-editing flow**:
1. Click `[↑ Export]` on a frame → plugin exports current mask to a chosen path.
2. Edit in Photoshop/CSP → save as PNG (flatten).
3. Click `[↓ Import]` on the same frame → plugin re-imports the PNG and places the refreshed
   `ext_` fill at the top of the mask stack.
4. If the user later adds more SP paint effects above it, the next explicit `[↓ Import]`
   round-trip promotes the latest external pass to the top again.
5. Saving over the same file path may auto-refresh the resource in Painter, but that does not
   change stack order; use `[↓ Import]` when the newest external pass must move back to the top.

---

## Phase 6: Bake (Production Quality)

Produces smooth sub-step SDF values using the `sdf_shadow_threshold_map-main` algorithm.

### Algorithm recap

For each consecutive frame pair (i, i+1):
1. `distanceTransform(mask)` per binary mask → SDF gradient peaking at boundary
2. `sdf1 / (sdf1 + sdf2)` → smooth 0→1 gradient across transition zone
3. `lerp(step_start, step_end, gradient) × diff_mask` → per-zone contribution
4. Sum all pairs → final shadow threshold map

### Export all frames (visibility toggle)

```python
def export_all_frames(group_node, texture_set_name: str,
                      export_dir: str) -> list:
    """
    Export each frame as a binary PNG by toggling visibility.
    Returns paths ordered bottom-to-top (Frame_01 first).

    CRITICAL: Two fixes applied here:
    1. destChannel "L" (Luminance) — not "R". An R-only PNG causes cv2's
       BGR→gray to compute 0.299×R=76 for white, which binarizes to black.
    2. Temp fill value 1.0 — the broadest frame at the top of the stack can
       have a low fill value such as ~0.111, which is 8-bit value ~28 and
       below the binarization threshold 127. Temporarily set each exported
       frame to 1.0 so masked pixels export as white (255), then restore the
       original value.
    """
    # sub_layers() is top-to-bottom; reverse for bottom-first ordering
    frame_layers = list(reversed(group_node.sub_layers()))

    # Save original fill values, then hide all frames
    original_values = {}
    for layer in frame_layers:
        source = layer.get_source(USER0)
        original_values[layer.uid()] = source.get_color()
        layer.set_visible(False)

    frame_paths = []
    try:
        for i, layer in enumerate(frame_layers):
            layer.set_visible(True)
            # Temporarily set fill to 1.0 so masked pixels export as white (255)
            layer.set_source(USER0,
                             sp.colormanagement.Color(1.0, 1.0, 1.0))

            out_name = f"sdf_frame_{str(i + 1).zfill(2)}"
            config = {
                "exportPath": export_dir,
                "defaultExportPreset": "bake_frame",
                "exportPresets": [{"name": "bake_frame", "maps": [{
                    "fileName": out_name,
                    "channels": [{"destChannel": "L", "srcChannel": "R",
                                  "srcMapType": "documentMap",
                                  "srcMapName": "user0"}],
                    "parameters": {"fileFormat": "png", "bitDepth": "8",
                                   "paddingAlgorithm": "transparent"}
                }]}],
                "exportList": [{"rootPath": texture_set_name}]
            }
            sp.export.export_project_textures(config)
            frame_paths.append(
                os.path.join(export_dir, f"{out_name}.png"))

            # Restore original fill value and hide
            layer.set_source(USER0, original_values[layer.uid()])
            layer.set_visible(False)
    finally:
        # Restore visibility and fill values for all frames
        for layer in frame_layers:
            layer.set_source(USER0, original_values[layer.uid()])
            layer.set_visible(True)

    return frame_paths
```

### Run SDF interpolation

**Development path**: subprocess call to system Python with numpy+cv2.

```python
import subprocess, shutil, sys

def find_python_with_deps() -> str | None:
    for cmd in ["python", "python3", "py"]:
        exe = shutil.which(cmd)
        if not exe:
            continue
        r = subprocess.run([exe, "-c", "import numpy, cv2"],
                           capture_output=True, timeout=10)
        if r.returncode == 0:
            return exe
    return None

def run_sdf_tool(python_exe: str, frame_dir: str, output_dir: str,
                 output_name: str = "sdf_baked",
                 filter_mode: str = "gaussian",
                 bit_depth: int = 16) -> str:
    run_script = os.path.join(os.path.dirname(__file__),
                              "sdf_shadow_threshold_map-main", "run.py")
    r = subprocess.run(
        [python_exe, run_script,
         "-i", frame_dir, "-o", output_dir,
         "-n", output_name, "-b", str(bit_depth),
         "-c", "gray", "-f", filter_mode],
        capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"SDF tool failed:\n{r.stderr}")
    return os.path.join(output_dir, output_name + ".png")
```

**Distribution-safe release path**: for non-technical users, prefer a bundled bake executable
that already contains the SDF tool and its `numpy`/`cv2` dependencies. The plugin should call
that bundled executable directly and keep `find_python_with_deps()` / `run_sdf_tool()` as a
development fallback only. Do not rely on artists having Python, pip, PATH, or OpenCV set up
correctly.

**License reminder for bundled bake executable**: if the release executable is built from
`sdf_shadow_threshold_map-main` (including a modified version adapted for this plugin), keep the
upstream MIT license and copyright notice in the distributed package. The Painter integration is
custom, but the current bake core is based on that MIT-licensed tool.

**Subprocess hazard**: `sdftool.save_image(..., confirm_overwrite=True)` calls `input()` for
terminal confirmation when the output file already exists. This would hang the subprocess.
Safe in the final bake flow because we write to a fresh `TemporaryDirectory` where no pre-existing
file exists. For repeatable development/test runs that reuse a stable output folder, delete the
target output PNG before invoking the tool so the subprocess never reaches that prompt.

**Fallback**: QImage proxy smooth (no deps, inferior quality).

```python
def _export_composited_user0(texture_set_name: str, output_dir: str) -> str:
    """Export the composited User0 channel with all frames visible.
    Used for the QImage fallback when system Python with numpy+cv2 is unavailable.
    """
    out_name = "sdf_composited"
    config = {
        "exportPath": output_dir,
        "defaultExportPreset": "composited_export",
        "exportPresets": [{"name": "composited_export", "maps": [{
            "fileName": out_name,
            "channels": [{"destChannel": "L", "srcChannel": "R",
                          "srcMapType": "documentMap",
                          "srcMapName": "user0"}],
            "parameters": {"fileFormat": "png", "bitDepth": "8",
                           "paddingAlgorithm": "transparent"}
        }]}],
        "exportList": [{"rootPath": texture_set_name}]
    }
    sp.export.export_project_textures(config)
    return os.path.join(output_dir, f"{out_name}.png")

from PySide6.QtGui import QImage
from PySide6.QtCore import Qt

def smooth_sdf_qimage(composited_path: str, output_path: str,
                      radius: int = 4) -> str:
    img = QImage(composited_path)
    w, h = img.width(), img.height()
    f = radius * 2 + 1
    blurred = (img
        .scaled(max(1, w // f), max(1, h // f),
                Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        .scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
    blurred.save(output_path)
    return output_path
```

### Reimport and assign to User0

```python
def reimport_baked_sdf(baked_path: str):
    resource = sp.resource.import_session_resource(
        baked_path, sp.resource.Usage.TEXTURE, name="SDF_Baked")
    resource_id = resource.identifier()

    stack = sp.textureset.get_active_stack()
    root_nodes = sp.layerstack.get_root_layer_nodes(stack)
    result_layer = next(
        (n for n in root_nodes if n.get_name() == "SDF_Baked_Result"), None)

    if result_layer is None:
        pos = sp.layerstack.InsertPosition.from_textureset_stack(stack)
        result_layer = sp.layerstack.insert_fill(pos)
        result_layer.set_name("SDF_Baked_Result")
        result_layer.active_channels = {USER0}

    result_layer.set_source(USER0, resource_id)
```

### Full bake flow

```python
def bake_sdf():
    group = _find_sdf_group()
    if group is None:
        raise RuntimeError("SDF_Generator group not found. Run Setup first.")

    stack = sp.textureset.get_active_stack()
    texture_set = stack.material()
    texture_set_name = (
        texture_set.name() if callable(texture_set.name) else texture_set.name
    )

    python_exe = find_python_with_deps()
    if python_exe is None:
        raise RuntimeError("No system Python with numpy and cv2 was found on PATH.")

    with tempfile.TemporaryDirectory(prefix="sdf_bake_") as temp_dir:
        frames_dir = os.path.join(temp_dir, "frames")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(frames_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        export_all_frames(group, texture_set_name, frames_dir)
        baked_path = run_sdf_tool(
            python_exe,
            frames_dir,
            output_dir,
            output_name="sdf_baked",
            filter_mode="gaussian",
            bit_depth=16,
        )
        reimport_baked_sdf(baked_path)
```

---

## Phase 7: Plugin UI

### Layout

```
┌──────────────────────────────────────────┐
│  SDF Real-Time Generator                 │
├──────────────────────────────────────────┤
│  Frames: [9 ▲▼]   [Setup SDF Group]     │
├──────────────────────────────────────────┤
│  ┌────────────────────────────────────┐  │
│  │( ) Frame_03 [78%] [+] [→] [↑] [↓] │  │
│  │( ) Frame_02 [89%] [+] [→] [↑] [↓] │  │
│  │( ) Frame_01 [100%][+] [→] [↑] [↓] │  │
│  └────────────────────────────────────┘  │
│  [+ Add Frame]      [↺ Sync Values]      │
│  [⊕ Borrow Shape]                        │
├──────────────────────────────────────────┤
│  [⚙ Bake SDF]                            │
└──────────────────────────────────────────┘
```

### Per-row controls

| Button | Action |
|---|---|
| `[+]` / `[-]` | Toggle additive/subtractive mask mode for this frame. Calls `set_frame_mask_mode()`. |
| `[→]` | Select this frame's fill layer in SP's Layers panel. `sp.layerstack.set_selected_nodes([fill])`. **CONSTRAINT**: raises `RuntimeError` if called inside a `ScopedModification` block — must be called outside. |
| `[↑]` | Export this frame's mask to a user-chosen file for external editing. |
| `[↓]` | Import a PNG back as a `FillEffectNode` in this frame's mask. Creates on first use; subsequent imports re-place the external fill at the top so the latest external pass wins visually. |
| `( )` | Select this frame as the current target for `[⊕ Borrow Shape]`. The row selector is a single exclusive `QButtonGroup`, so only one frame can be targeted at a time. |

All row actions should also mark that frame as the currently selected frame in the panel.

### Top-level controls

| Button | Action |
|---|---|
| `[Setup SDF Group]` | Runs `setup_sdf_group(n_frames)`. Disabled if group already exists. |
| `[+ Add Frame]` | Calls `add_frame(selected_frame)`. Inserts above the currently selected row. |
| `[↺ Sync Values]` | Calls `sync_frame_values()`. Always safe to run. |
| `[⊕ Borrow Shape]` | Calls `ui_borrow_shape(selected_frame)`. Requires user to select the source layer in SP's Layers panel and choose the target frame row in the plugin first. |
| `[⚙ Bake SDF]` | Calls `bake_sdf()`. Exports the frames to a temp directory, runs the SDF tool, and imports/updates `SDF_Baked_Result`. |

### Frame list refresh

```python
# Refresh immediately after plugin actions, and poll the active stack key so
# switching texture sets / opening older projects clears or rebuilds the panel
# automatically even when no explicit stack-change event exists for that action.
```

`refresh_frame_list()` reads `_find_sdf_group().sub_layers()` and rebuilds the list rows.
If the active stack has no usable SDF setup, the panel should show the empty state immediately
instead of keeping stale rows from the previous stack.

---

## Phase 8: Workflow Integration

### Full user workflow

1. Open project with `Rizum_Anime_ToonShader_V12` shader and **User0** channel present.
2. Open the **SDF Real-Time Generator** panel.
3. Set frame count → click **Setup SDF Group**.
4. **Paint frame by frame** (each frame is independent):
   - Click **[→]** to jump to a frame → click its mask thumbnail in SP → paint.
   - The default/common workflow is **[+]** additive: start black and add white.
   - Build from `Frame_01` upward: broadest white mask first, then progressively narrower masks.
   - Add extra paint effects inside a frame's mask via SP's Layers panel for complex shapes.
   - Duplicate a paint effect from a previous frame's mask into the current one via SP right-click → duplicate, drag.
5. **Improvise freely**:
   - Need a frame between 04 and 05? Click **[+ Add Frame]** → click **[↺ Sync Values]**.
   - Want to reuse a shape from BaseColor? Select that layer in SP, choose the target frame row in the plugin, then click **[⊕ Borrow Shape]**.
   - Want to refine in Photoshop? Click **[↑ Export]** on the frame → edit externally → click **[↓ Import]**.
6. **Viewport updates in real-time** throughout — drag environment light to preview shadow sweep.
7. Satisfied with the result → click **[⚙ Bake SDF]** for production-quality output.
8. Compare: toggle visibility of `SDF_Baked_Result` (baked) vs `SDF_Generator` group (preview).

### Painting tips to show in the UI

- Frame_01 (bottom) covers the **least** face area — paint only the deepest, always-shadowed crevices here. Frame_N (top) covers the **most** face area. Build downward-to-upward = narrow to broad.
- Each frame's shadow region should be a **superset** of the frame below it (broader contains narrower).
- Sync Values is safe to click anytime — only updates gray fill values and names.
- After baking, the `SDF_Baked_Result` layer sits above the generator group — toggle it to compare.
- For the bake step, install numpy and opencv-python in your system Python for best quality.
- Older stacks built under the previous convention may need the layers reordered, then
  `Sync Values` clicked once, before bake results match the current convention.

---

## File Structure

```
sdf/
├── __init__.py               # SP plugin entry: start_plugin() / close_plugin()
├── sdf_realtime_plugin.py    # UI panel (PySide6), event wiring, plugin lifecycle
├── sdf_layer_setup.py        # setup_sdf_group, _insert_frame, _find_sdf_group,
│                             # _frame_name
├── sdf_frame_ops.py          # _sync_frame_values_impl, sync_frame_values, add_frame,
│                             # set_frame_mask_mode, borrow_shape_from_layer,
│                             # ui_borrow_shape
├── sdf_external.py           # export_frame_for_external, import_external_edit
├── sdf_bake.py               # export_all_frames, _export_composited_user0,
│                             # find_python_with_deps, run_sdf_tool,
│                             # smooth_sdf_qimage, reimport_baked_sdf, bake_sdf
├── sdf_shadow_threshold_map-main/  # Reference SDF tool (subprocess target)
├── agent.md
├── analysis.md
└── plan.md
```

**`__init__.py`**: SP loads the `sdf/` directory as a Python package. It must contain
`start_plugin()` and `close_plugin()` at module level. Minimal implementation:

```python
from . import sdf_realtime_plugin

def start_plugin():
    sdf_realtime_plugin.start_plugin()

def close_plugin():
    sdf_realtime_plugin.close_plugin()
```

---

## Implementation Order

| Step | Task | Verify |
|---|---|---|
| 1 | `__init__.py` + `sdf_layer_setup.py`: `setup_sdf_group()`, `_insert_frame()`, `_find_sdf_group()`, `_frame_name()` | Group with N fill layers (Frame_N at top, Frame_01 at bottom), each has base fill + paint effect in mask. User0 values run high→low bottom-to-top, so Frame_01 is the **narrowest** (deep-shadow-only) frame and Frame_N is the broadest. |
| 2 | `sdf_frame_ops.py`: `_sync_frame_values_impl()`, `sync_frame_values()` | Reorder layers, click Sync → values and names update. Single undo step. |
| 3 | `sdf_realtime_plugin.py`: Minimal UI — Setup button + frame list + [→] select | Panel shows rows, clicking [→] selects layer in SP (outside ScopedModification). |
| 4 | Real-time preview test | Paint on a mask → viewport shadow updates immediately. |
| 5 | `add_frame()` (calls `_sync_frame_values_impl` inside scope) + Add Frame button | New frame inserted above selected, values redistributed, single undo step. |
| 6 | `set_frame_mask_mode()` + [+/-] toggle | Toggle changes base fill color and mask background. |
| 7 | `sdf_external.py`: `export_frame_for_external()` + [↑] button | PNG exported with `destChannel: "L"`, correct frame isolated. |
| 8 | `import_external_edit()` + [↓] button | PNG imported as FillEffectNode with `GenericColorSpace.Raw`. Re-import promotes the refreshed external fill to the top of the mask stack. |
| 9 | `borrow_shape_from_layer()` + [⊕ Borrow Shape] button | Anchor point inside source Content stack, wired into frame mask, levels effect added. |
| 10 | `sdf_bake.py`: `export_all_frames()` | N zero-padded PNGs exported in canonical narrow→broad order (Frame_01 first = narrowest, matching FaceShadowBlend `a→h`), with temp 1.0 fill (white where masked, black elsewhere). |
| 11 | `find_python_with_deps()` + `run_sdf_tool()` | (Paused — see steps 15–17.) Originally documented `-r` reverse-gradient flag for the old broad→narrow order; under the current narrow→broad convention the flag should not be needed for a `sdftool`-based bake either. The active bake direction is the FaceShadowBlend-style blur baker (step 17), not `sdftool`. |
| 12 | `_export_composited_user0()` + `smooth_sdf_qimage()` | Deferred for now; current bake path requires a system Python with `numpy` + `cv2` or, later, a bundled executable. |
| 13 | `reimport_baked_sdf()` + Bake button | Real `Bake SDF` button runs export → tool → import and updates `SDF_Baked_Result` in User0. |
| 14 | Bake progress indication ✅ | `Bake SDF` shows clear stage progress: exporting frames, running SDF tool, importing baked result. Implemented via optional `on_progress(stage, current, total)` callback threaded through `bake_sdf` / `export_all_frames` / `run_sdf_tool` / `reimport_baked_sdf`, rendered by a modal `QProgressDialog` in `_on_bake_sdf` (no cancel — subprocess is uninterruptible). Non-UI callers still work by omitting the callback. **Also reverted an off-plan `export_live_composite` + `composite_tool_with_live` merge step that was producing "Frame_08 duplicated" bakes: `np.maximum(tool, live)` let the live stepped composite dominate the SDF tool output wherever a frame's gray value was higher than the tool's smooth interpolation. `bake_sdf()` is now the clean 3-step flow from Phase 6 (export → tool → reimport).** |
| 15 | Pause current `sdftool` patching path | **Current decision**: stop iterating on bake post-process patches for the `sdf_shadow_threshold_map-main` path. The custom-mask artifacts were reduced but not solved cleanly, and later fixes introduced different regressions (black interior lines, then unwanted white spill). Do not resume from more heuristic patching. |
| 16 | Resume from Substance graph / `.sbsar` analysis data | After external analysis in Substance Designer or from unpacked graph metadata, document how `FaceShadowBlend` actually blends frames, what assumptions it makes about mask nesting, and whether it is blur-based, threshold-stack-based, or something else. Use that data to choose the next implementation path instead of guessing. |
| 17 | Replan bake direction after analysis ✅ | **Direction**: build a separate **blur-based baker** matching `FaceShadowBlend.sbs`. Verified structure from `SDFFaceLightMap.md` XML + `01_verify_subtract_direction.py`: <br>• `N` ordered masks, sorted **narrow→broad** (matches FaceShadowBlend `a→h`, matches our Frame_01→Frame_N convention).<br>• `N-1` adjacent-pair subtract bands. Substance subtract = `dest − src` clamped; with `dest=broader, src=narrower` this yields the **ring** between them.<br>• **`N` (not N-1)** Non-Uniform Blur Grayscale nodes: each NUB uses the lower (narrower) frame as **source** and the corresponding ring as the blur-mask **effect**. The topmost (broadest) frame **reuses the last ring** as its mask — that's the extra Nth NUB.<br>• Per-branch opacity = `1/N` (matches "Opacity=1/贴图数" comment).<br>• Progressive **add-chain** sums all N weighted NUB outputs.<br>• Intensity is **not uniform** in the reference graph (38.38, 24.27, then 11.69×6 for N=8). Broader-end pairs use larger feathering. Make this a parameter — possibly a per-pair list or a curve. <br>• Final grayscale output + `Histogram Scan` preview tap. <br>**Out of scope**: `sbsrender` / Automation Toolkit. Return to `sdftool` only if this implementation fails empirically. |

---

## Export Config — Required Fields (learned during Step 7)

The minimal export config that actually works requires all of these; missing any one errors
out. Use this exact shape for every export call in the plugin:

```python
config = {
    "exportPath": out_dir,
    "exportShaderParams": False,            # required: must be present
    "defaultExportPreset": "my_preset",
    "exportPresets": [{
        "name": "my_preset",
        "maps": [{
            "fileName": out_name,
            "channels": [{
                "destChannel": "L",          # L = proper grayscale
                "srcChannel":  "R",
                "srcMapType":  "documentMap",
                "srcMapName":  "user0",
            }],
            "parameters": {
                "fileFormat": "png",
                "bitDepth":   "16",
            },
        }],
    }],
    "exportList": [{"rootPath": texture_set_name}],
    # Global params are REQUIRED — "dithering" and "paddingAlgorithm" must be set here,
    # not inside the map's "parameters". "transparent" padding requires "dilationDistance".
    "exportParameters": [{
        "parameters": {
            "dithering":         False,
            "paddingAlgorithm":  "transparent",
            "dilationDistance":  16,
        },
    }],
}
```

### Temp baseline layer — required for single-frame export

Hiding all frames except the target leaves unpainted pixels as **transparent** (no
contribution) in User0 — not 0. With any dilation/padding, transparent regions get filled
with the nearest painted value, producing an all-white or all-lit export.

**Fix**: before exporting a single frame, insert a temp black fill layer at the **bottom**
of the `SDF_Generator` group (User0 = 0, full white mask). This makes unpainted pixels
export as explicit black (0). Remove the temp layer in the `finally` block.

```python
temp = sp.layerstack.insert_fill(
    sp.layerstack.InsertPosition.below_node(bottom_frame))
temp.active_channels = {USER0}
temp.set_source(USER0, sp.colormanagement.Color(0.0, 0.0, 0.0))
# ... export ...
sp.layerstack.delete_node(temp)
```

### "infinite" padding is a trap

`"paddingAlgorithm": "infinite"` spreads non-zero pixel values across the *entire* texture
outside UVs — a single white stroke becomes all-white. Use `"transparent"` with a bounded
`dilationDistance` (e.g. 16) for any mask-style export.

## Future Enhancement: Padding Settings Panel

Add a settings icon/section to the UI exposing:
- Padding algorithm dropdown: `transparent`, `infinite`, `diffusion`, `color`
- Dilation distance spinbox (only enabled when padding ≠ infinite)
- Bit depth: 8 / 16
- These settings apply to external export (`[↑]`) and the bake's per-frame export.
Store the values in the panel class; pass them into the export functions as parameters.

## Development Notes

- **SP plugin reload caches submodules**: SP's "Reload Plugins Folder" calls
  `close_plugin()` / `start_plugin()` but does not re-import already-loaded submodules.
  When editing files mid-session, edits to `sdf_realtime_plugin.py` (or any submodule
  imported via `from . import x`) may not take effect until SP is restarted. Verified during
  Step 3 testing — first reload after editing did nothing; restart fixed it.
- **Dock widget GC pitfall**: `add_dock_widget(widget)` does not hold a strong Python
  reference to the inner widget. Store it in a module-level global, otherwise the widget
  is garbage-collected and the dock appears empty. Set the title on the returned
  QDockWidget, not the inner widget.
- **Row target radios need a shared button group**: putting one `QRadioButton` in each row
  widget does not make them mutually exclusive. Use a single `QButtonGroup` across all rows.
- **Row gap was caused by stretch, not layout spacing**: `row_layout.addWidget(name_label, 1)`
  made the name column absorb extra width and pushed the percentage away. Fixed by using
  font-metric-based fixed widths for `Frame_99` and `[100%]` plus a small explicit spacing.
- **Frame convention — current (Option A, aligned with FaceShadowBlend)**: `Frame_01` sits at
  the bottom with the highest User0 value (1.0) and represents the **narrowest** shadow region
  (deep crevices only). `Frame_N` sits at the top with the lowest value and represents the
  **broadest** shadow region. This matches FaceShadowBlend's `a→h` ordering (`a`=narrowest at
  bottom). The value formula `(total - index + 1) / total` and iteration order are unchanged
  from the previous convention — only the painting/labeling intent flipped. Older stacks that
  were authored under the broad-at-bottom interpretation will look semantically inverted; either
  re-author the masks or treat them as reverse-direction tests.
- **Hidden-frame bake trap**: bake currently depends on the frame set being visible unless the
  bake flow explicitly overrides visibility during export. This should be fixed so manual hiding
  in the Layers panel never causes a misleading one-color or empty bake result.
- **Best time to split UI into its own file**: keep `sdf_realtime_plugin.py` as-is while core
  behavior is still changing quickly. The best cleanup point is after the remaining functional
  milestones are stable, especially once the bake flow is implemented and verified. At that
  point, move `SDFPanel` and row-rendering code into a dedicated `sdf_panel.py`, while leaving
  plugin lifecycle (`start_plugin()` / `close_plugin()`) in `sdf_realtime_plugin.py`.
- **Bake distribution strategy**: PATH-based Python detection works for development, but it is
  not the right shared-user experience. For release, bundle the bake tool as a self-contained
  executable (preferred) or ship a private embedded Python runtime with the plugin. Treat system
  Python discovery as a fallback/debug path, not the primary artist workflow.
- **Current bake-status decision**: pause work on the current `sdftool` post-processing branch.
  The recent experiments (frame normalization, exact-zero dead-zone fill, and debug snapshots)
  helped characterize the failure modes, but the remaining visual mismatch suggests this path is
  not the desired look target. Resume only after external Substance graph / `.sbsar` analysis
  data is available.

## Open Questions (for runtime verification)

1. **SP version targeting**: `layerstack` API expanded in SP 9.x. Confirm minimum version.
2. **`insert_paint()` in mask stack**: API docs confirm this is valid. One quick console test to verify no edge cases with fill layers specifically.
3. **`set_source(None, Color)` for base fill in mask**: `None` channel is correct for mask context per docs. Verify the base fill effect's color actually appears as mask value (not as channel color).
4. **Bundled bake runtime vs system Python**: for shipping, prefer a bundled executable instead
   of relying on PATH/system Python. If a development override is still needed later, consider a
   settings field for an explicit Python path.
5. **Visibility toggle + event listener feedback**: Disconnect `LayerStacksModelDataChanged` listener before the bake's visibility toggle loop. Reconnect after. Otherwise the UI refresh fires for every toggle.
6. **What does `FaceShadowBlend` actually do?**: gather the external analysis results before any
   further bake implementation work. At minimum, capture:
   - the effective frame ordering the graph expects
   - whether it requires strict subset / nesting masks
   - whether it blends via blur, threshold stacking, pairwise differences, or a hybrid method
   - whether there is a practical route to reproducing it in Python vs. calling it directly

## Pause / Resume Point

Current stop point: do **not** continue patching the current `sdf_shadow_threshold_map-main`
bake branch.

When resuming, start from the external analysis of:
- `FaceShadowBlend.sbsar` opened in Substance Designer, if possible
- `SDF_FaceShadowBlend/_unpack/assemblies/content/0000/FaceShadowBlend.xml`
- any screenshots / notes of the graph nodes, parameters, and blend order

Expected resume output:
1. A short note describing how the graph appears to work.
2. A decision on the next bake direction (`sbsrender`, blur-based reimplementation, or a proven
   correction to the current `sdftool` path).
3. Only after that, update `sdf_bake.py` again.

## Bake Fix Log

- **Black-interior dots in the baked output** → Fixed by compositing the SDF
  tool's ring output with the live User0 composite via `np.maximum`. The ring
  algorithm inherently returns 0 wherever a pixel is the same across every
  frame (interior of narrowest mask, exterior of broadest). The live composite
  is the stepped ground-truth map the real-time preview shows; taking the pixel
  max keeps the tool's smooth gradients in the transition zones and fills the
  dead zones with the correct stepped value. New helpers in `sdf_bake.py`:
  `export_live_composite()` and `composite_tool_with_live()`. `bake_sdf()` now
  does: export frames → run tool → export live composite → merge → reimport.
- **Non-issue (originally misread)**: an earlier hypothesis that file naming
  was inverted vs. layer names turned out to be a misread of an old export
  folder. Current naming (`Frame_01` → `sdf_frame_01.png`, broadest first)
  is correct; no reorder / no `-r` flag needed.
- **Later `sdftool` patch experiments were not accepted as the final direction**:
  bake-time frame normalization and dead-zone filling partially reduced the custom-mask failure,
  but the visual result still diverged from the desired Substance look and introduced new artifact
  trade-offs. Keep these experiments as debugging history only; do not treat them as the final
  bake design.

## Resolved Questions (already fixed in this plan)

- **`ScopedModification` nesting** → Fixed: `_sync_frame_values_impl()` extracted without wrapper; `add_frame()` calls it inside its own scope. Single undo step.
- **`reload_modified_resources_async` timing** → Replaced: external edits now re-import and update source via `set_source()` — synchronous, and works even if the file path changes between edits. `ResourcesListFilter` exists but is async (fires `ReloadResourcesEnded`) and requires the path to stay identical.
- **Round-trip ordering after new SP paint** → Updated: the chosen workflow is that the latest explicit `[↓] Import` must place the refreshed external fill at the top of the mask stack. Same-path auto-reload may refresh pixels, but it preserves the existing stack order and is not enough for this workflow.
- **`set_selected_nodes()` inside ScopedModification** → Documented: raises `RuntimeError`. Must be called outside `with` block.
- **AnchorPoint placement** → Fixed: must use `InsertPosition.inside_node(layer, NodeStack.Content)`, not `above_node()`.
- **Export channel format** → Fixed: `"destChannel": "L"` (luminance) instead of `"R"`.
- **Frame fill binarization** → Fixed: temp 1.0 fill during export so sdftool binarizes correctly.
- **`DataColorSpace.Raw`** → Fixed: doesn't exist. Use `GenericColorSpace.Raw`.
- **PySide version** → Fixed: SP 10.x+ uses PySide6, not PySide2.
- **sdftool `input()` hazard** → Documented: `save_image()` calls `input()` — safe only in fresh temp dirs.
- **Missing `_export_composited_user0()`** → Added: exports composited User0 for QImage fallback.
- **Missing `__init__.py`** → Added: SP plugin package entry point.

---

## Non-Goals

- No live-linking of layers across frames — duplicate-and-modify is native SP behavior.
- This plugin does not replace `FaceShadowBlend.sbsar` — that remains the offline precision tool.
- No auto-detection of light direction or animation — that is the shader's job.
- No stroke-level programmatic painting — strokes are not accessible via the Python API.
