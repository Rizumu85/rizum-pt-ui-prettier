"""
Baked Map Painter — Substance Painter Plugin
============================================
Click any baked mesh map card to open a live paint canvas inside SP.
Paint directly over baking artifacts (AO, Normal, Curvature, etc.)
then hit Apply — the edited map is re-imported into the project
without ever leaving Substance Painter.

Installation
------------
Copy this file to:
  Windows : %USERPROFILE%\Documents\Adobe\Adobe Substance 3D Painter\python\plugins\
  macOS   : ~/Documents/Adobe/Adobe Substance 3D Painter/python/plugins/
  Linux   : ~/Documents/Adobe/Adobe Substance 3D Painter/python/plugins/

Then: Edit → Plugins… → baked_map_manager → Load

Requirements
------------
- Substance Painter 2023+ (PySide6) or 8.x (PySide2)
- No extra Python packages needed for core painting.
  (Pillow is only used as a fallback image loader if QImage can't read the format.)
"""

import os
import shutil
import tempfile
import traceback

# ── Substance Painter ─────────────────────────────────────────────────────────
import substance_painter.ui        as spui
import substance_painter.project   as spproject
import substance_painter.textureset as spset
import substance_painter.resource  as spresource
import substance_painter.logging   as splog
import substance_painter.event     as spevent

# ── Qt shim: PySide6 (SP 2023+) or PySide2 (SP 8.x) ─────────────────────────
try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from PySide6.QtCore import Qt, QPoint, QRect, QSize, QPointF
    from PySide6.QtGui  import (QImage, QPixmap, QPainter, QPen, QBrush,
                                 QColor, QRadialGradient, QPainterPath)
    if not hasattr(QtWidgets.QDialog, "exec_"):
        QtWidgets.QDialog.exec_ = QtWidgets.QDialog.exec
    _QT = 6
    _AlignCenter      = Qt.AlignmentFlag.AlignCenter
    _CrossCursor      = Qt.CursorShape.CrossCursor
    _ClosedHandCursor = Qt.CursorShape.ClosedHandCursor
    _PointingHand     = Qt.CursorShape.PointingHandCursor
    _WhatsThis        = Qt.CursorShape.WhatsThisCursor
    _NoPen            = Qt.PenStyle.NoPen
    _NoBrush          = Qt.BrushStyle.NoBrush
    _HLine            = QtWidgets.QFrame.Shape.HLine
    _VLine            = QtWidgets.QFrame.Shape.VLine
    _Sunken           = QtWidgets.QFrame.Shadow.Sunken
    _SBAlwaysOff      = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    _KeepAR           = Qt.AspectRatioMode.KeepAspectRatio
    _SmoothXform      = Qt.TransformationMode.SmoothTransformation
    _HorizSlider      = Qt.Orientation.Horizontal
    _SrcOver          = QPainter.CompositionMode.CompositionMode_SourceOver
    _Clear            = QPainter.CompositionMode.CompositionMode_Clear
    _AA               = QPainter.RenderHint.Antialiasing
    _ImgFmt           = QImage.Format.Format_ARGB32
    _ShowAlpha        = QtWidgets.QColorDialog.ColorDialogOption.ShowAlphaChannel
    _LMB              = Qt.MouseButton.LeftButton
    _MMB              = Qt.MouseButton.MiddleButton
    _CtrlMod          = Qt.KeyboardModifier.ControlModifier
    _ShiftMod         = Qt.KeyboardModifier.ShiftModifier
    _Key_Z = Qt.Key.Key_Z;  _Key_B = Qt.Key.Key_B
    _Key_E = Qt.Key.Key_E;  _Key_F = Qt.Key.Key_F
    _Key_I = Qt.Key.Key_I
except ModuleNotFoundError:
    from PySide2 import QtWidgets, QtCore, QtGui
    from PySide2.QtCore import Qt, QPoint, QRect, QSize, QPointF
    from PySide2.QtGui  import (QImage, QPixmap, QPainter, QPen, QBrush,
                                 QColor, QRadialGradient, QPainterPath)
    _QT = 2
    _AlignCenter      = Qt.AlignCenter
    _CrossCursor      = Qt.CrossCursor
    _ClosedHandCursor = Qt.ClosedHandCursor
    _PointingHand     = Qt.PointingHandCursor
    _WhatsThis        = Qt.WhatsThisCursor
    _NoPen            = Qt.NoPen
    _NoBrush          = Qt.NoBrush
    _HLine            = QtWidgets.QFrame.HLine
    _VLine            = QtWidgets.QFrame.VLine
    _Sunken           = QtWidgets.QFrame.Sunken
    _SBAlwaysOff      = Qt.ScrollBarAlwaysOff
    _KeepAR           = Qt.KeepAspectRatio
    _SmoothXform      = Qt.SmoothTransformation
    _HorizSlider      = Qt.Horizontal
    _SrcOver          = QPainter.CompositionMode_SourceOver
    _Clear            = QPainter.CompositionMode_Clear
    _AA               = QPainter.Antialiasing
    _ImgFmt           = QImage.Format_ARGB32
    _ShowAlpha        = QtWidgets.QColorDialog.ShowAlphaChannel
    _LMB              = Qt.LeftButton
    _MMB              = Qt.MidButton
    _CtrlMod          = Qt.ControlModifier
    _ShiftMod         = Qt.ShiftModifier
    _Key_Z = Qt.Key_Z;  _Key_B = Qt.Key_B
    _Key_E = Qt.Key_E;  _Key_F = Qt.Key_F
    _Key_I = Qt.Key_I

# ─────────────────────────────────────────────────────────────────────────────
PLUGIN_NAME    = "Baked Map Painter"
PLUGIN_VERSION = "2.0.0"

MESH_MAP_INFO = {
    spset.MeshMapUsage.Normal:           ("Normal",            "#4A9EFF"),
    spset.MeshMapUsage.WorldSpaceNormal: ("World Normal",      "#7B6FFF"),
    spset.MeshMapUsage.Curvature:        ("Curvature",         "#FF9E4A"),
    spset.MeshMapUsage.AO:               ("Ambient Occlusion", "#A8A8A8"),
    spset.MeshMapUsage.Position:         ("Position",          "#4AFF9E"),
    spset.MeshMapUsage.Thickness:        ("Thickness",         "#FF4A9E"),
    spset.MeshMapUsage.BentNormals:      ("Bent Normals",      "#9EFF4A"),
    spset.MeshMapUsage.Height:           ("Height",            "#FFD04A"),
    spset.MeshMapUsage.ID:               ("ID / Color ID",     "#FF6B6B"),
    spset.MeshMapUsage.Opacity:          ("Opacity",           "#CCCCCC"),
}

# ─────────────────────────────────────────────────────────────────────────────
def _log(msg, level="info"):
    fn = {"error": splog.error, "warning": splog.warning}.get(level, splog.info)
    fn(f"[{PLUGIN_NAME}] {msg}")

# ─────────────────────────────────────────────────────────────────────────────
# Mesh map → SP export srcMapName string
# Confirmed names from substance_painter.export documentation:
#   ambient_occlusion, id, curvature, normal_base,
#   world_space_normals, position, thickness
# Remaining names derived from SP internal naming conventions.
# ─────────────────────────────────────────────────────────────────────────────
_EXPORT_MAP_NAME = {
    spset.MeshMapUsage.AO:               "ambient_occlusion",
    spset.MeshMapUsage.Normal:           "normal_base",
    spset.MeshMapUsage.WorldSpaceNormal: "world_space_normals",
    spset.MeshMapUsage.Curvature:        "curvature",
    spset.MeshMapUsage.Position:         "position",
    spset.MeshMapUsage.Thickness:        "thickness",
    spset.MeshMapUsage.ID:               "id",
    spset.MeshMapUsage.BentNormals:      "bent_normals",
    spset.MeshMapUsage.Height:           "height",
    spset.MeshMapUsage.Opacity:          "opacity",
}

# Persistent temp dir reused across calls so we don't litter the filesystem.
_WORK_DIR = os.path.join(tempfile.gettempdir(), "baked_map_painter")


def _work_dir():
    os.makedirs(_WORK_DIR, exist_ok=True)
    return _WORK_DIR


def _export_map_to_file(texture_set, usage):
    """
    Export a single baked mesh map to a PNG in our work directory and return
    the path.  Uses SP's export API with a targeted single-channel preset so
    we get exactly the map we want at its native resolution.

    This is the ONLY way to reliably get a file path — resource URLs are
    internal and don't always resolve to a real file on disk.
    """
    import substance_painter.export as spexport

    map_name   = _EXPORT_MAP_NAME.get(usage)
    label      = MESH_MAP_INFO[usage][0].replace(" ", "_")
    ts_name    = texture_set.name()
    # Safe filename: strip chars that break file paths
    safe_ts    = "".join(c if c.isalnum() or c in "-_." else "_" for c in ts_name)

    # Check for UDIM — include $udim token in filename
    has_udim = False
    try:
        has_udim = texture_set.has_uv_tiles()
    except Exception:
        pass
    if has_udim:
        file_stem = f"{safe_ts}_{label}_$udim"
    else:
        file_stem = f"{safe_ts}_{label}"
    # For non-UDIM this is the final path; for UDIM it's the thumbnail cache path
    cache_path = os.path.join(_work_dir(), f"{safe_ts}_{label}.png")
    out_path   = cache_path

    if map_name is None:
        _log(f"No export name known for {label}", "warning")
        return None

    # Build a minimal custom export preset that outputs only this mesh map.
    # We export R/G/B from the same mesh map source — for greyscale maps
    # (AO, Curvature, etc.) all three channels carry identical data, which
    # is fine; QImage will see it as a proper greyscale-ish RGB image.
    channels = [
        {"destChannel": "R", "srcMapType": "meshMap", "srcMapName": map_name, "srcChannel": "R"},
        {"destChannel": "G", "srcMapType": "meshMap", "srcMapName": map_name, "srcChannel": "G"},
        {"destChannel": "B", "srcMapType": "meshMap", "srcMapName": map_name, "srcChannel": "B"},
    ]

    export_cfg = {
        "exportPath":        _work_dir(),
        "exportShaderParams": False,
        "exportList": [{"rootPath": ts_name}],
        "exportPresets": [{
            "name": "__bmpainter_preset__",
            "maps": [{
                "fileName": file_stem,
                "parameters": {
                    "fileFormat":       "png",
                    "bitDepth":         "8",
                    "dithering":        False,
                    "sRGB":             False,
                    "paddingAlgorithm": "passthrough",
                    "dilationDistance": 16,
                },
                "channels": channels,
            }],
        }],
        "defaultExportPreset": "__bmpainter_preset__",
    }

    _log(f"Exporting {label} for '{ts_name}' → {out_path}")
    import json as _json
    _log("Export config: " + _json.dumps(export_cfg, indent=2))

    # Snapshot the work dir BEFORE export so we can detect any new file SP creates
    _EXTS = {".png", ".tga", ".exr", ".tif", ".tiff", ".jpg", ".jpeg"}
    try:
        before = set(os.listdir(_work_dir()))
    except Exception:
        before = set()

    try:
        result = spexport.export_project_textures(export_cfg)
        if hasattr(result, "status"):
            import substance_painter.export as _exp
            if result.status != _exp.ExportStatus.Success:
                _log(f"Export status: {result.status}  msg: {getattr(result, 'message', '')}", "warning")
                return None
    except Exception as e:
        _log(f"Export API error: {e}", "error")
        return None

    # 1. Non-UDIM: expected path (exact stem + .png)
    if not has_udim and os.path.isfile(out_path):
        _log(f"Export OK → {out_path}")
        return out_path

    # 2. Scan for any NEW image file in the work dir that contains our stem
    stem_base = file_stem.replace("_$udim", "")
    try:
        after = set(os.listdir(_work_dir()))
        new_files = after - before
        _log(f"New files after export: {new_files}")

        if has_udim:
            # UDIM: find all new tiles, keep their names intact, return first
            import re as _re_udim
            udim_pattern = _re_udim.compile(
                _re_udim.escape(stem_base) + r'[._](\d{4})\.\w+$', _re_udim.IGNORECASE)
            tiles = []
            for fname in sorted(new_files):
                if os.path.splitext(fname)[1].lower() in _EXTS:
                    m = udim_pattern.match(fname)
                    if m:
                        tiles.append((int(m.group(1)), fname))
            if tiles:
                tiles.sort()
                first_tile = os.path.join(_work_dir(), tiles[0][1])
                _log(f"UDIM export OK — {len(tiles)} tile(s), first: {first_tile}")
                # Copy first tile to cache path for thumbnail
                try:
                    shutil.copy2(first_tile, cache_path)
                except Exception:
                    pass
                return first_tile
            # Fallback: any new image containing the stem
            for fname in sorted(new_files):
                if os.path.splitext(fname)[1].lower() in _EXTS and stem_base in fname:
                    found = os.path.join(_work_dir(), fname)
                    _log(f"UDIM fallback found: {found}")
                    try:
                        shutil.copy2(found, cache_path)
                    except Exception:
                        pass
                    return found
        else:
            # Non-UDIM: rename first new image to cache path
            for fname in sorted(new_files):
                if os.path.splitext(fname)[1].lower() in _EXTS:
                    found = os.path.join(_work_dir(), fname)
                    try:
                        os.replace(found, out_path)
                        _log(f"Renamed '{fname}' → {out_path}")
                        return out_path
                    except Exception:
                        _log(f"Found (no rename): {found}")
                        return found
    except Exception as e:
        _log(f"Post-export scan error: {e}", "warning")

    # 3. Broader scan: any file matching the label anywhere in work dir
    try:
        for fname in os.listdir(_work_dir()):
            if label.lower() in fname.lower() and os.path.splitext(fname)[1].lower() in _EXTS:
                found = os.path.join(_work_dir(), fname)
                _log(f"Found by label scan: {found}")
                return found
    except Exception:
        pass

    _log(f"Export produced no recognisable output file in {_work_dir()}", "error")
    return None


def _find_udim_tiles(directory, stem_base):
    """Discover all UDIM tile files matching a base stem in *directory*.

    Returns a sorted list of (tile_id, file_path) tuples,
    e.g. [(1001, '/tmp/MyTS_Normal_1001.png'), (1002, ...)].
    """
    import re as _re_ut
    _EXTS = {".png", ".tga", ".exr", ".tif", ".tiff", ".jpg", ".jpeg"}
    # Match both MARI naming (name.UDIM.ext) and underscore (name_UDIM.ext)
    pattern = _re_ut.compile(
        _re_ut.escape(stem_base) + r'[._](\d{4})\.\w+$', _re_ut.IGNORECASE)
    tiles = []
    try:
        for fname in os.listdir(directory):
            if os.path.splitext(fname)[1].lower() not in _EXTS:
                continue
            m = pattern.match(fname)
            if m:
                tiles.append((int(m.group(1)), os.path.join(directory, fname)))
    except Exception as e:
        _log(f"_find_udim_tiles scan error: {e}", "warning")
    tiles.sort()
    return tiles


def _find_texture_usage():
    """
    Locate the correct Usage enum member for importing a plain image/texture.
    SP versions differ — try the most likely names in order.
    Logs all available Usage members so future debugging is easy.
    """
    try:
        import enum
        members = {m.name: m for m in spresource.Usage
                   if isinstance(m, spresource.Usage)}
        _log(f"Available Usage members: {list(members.keys())}")
    except Exception:
        members = {}
        # Enumerate via dir() as fallback
        for attr in dir(spresource.Usage):
            if not attr.startswith("_"):
                try:
                    val = getattr(spresource.Usage, attr)
                    if callable(getattr(val, 'value', None)) or hasattr(val, 'value'):
                        members[attr] = val
                except Exception:
                    pass
        _log(f"Usage members (dir fallback): {list(members.keys())}")

    # Preference order for plain-image texture imports
    for name in ("Texture", "texture", "TEXTURE",
                 "BASE_COLOR", "BaseColor", "base_color",
                 "DIFFUSE", "Diffuse", "diffuse",
                 "IMAGE", "Image", "image"):
        if name in members:
            _log(f"Using Usage.{name} for texture import")
            return members[name]

    # Last resort: return first member
    if members:
        first = next(iter(members.values()))
        _log(f"Falling back to first Usage member: {first!r}", "warning")
        return first

    _log("Could not determine any Usage member — import will likely fail", "error")
    return None


def _srgb_to_linear_file(path):
    """Convert an sRGB PNG file to linear color space in-place.

    The paint mode puts linear mesh-map data into the Base Color channel,
    which SP displays through an implicit linear→sRGB curve.  When we
    export that channel the pixel values are in sRGB space, but the mesh
    map slot expects linear values.  Applying sRGB→linear here closes the
    colour-space round-trip so values stay stable across apply cycles.
    """
    # Fast path: numpy + Pillow (both ship with SP)
    try:
        from PIL import Image as _PILImage
        import numpy as _np

        img = _PILImage.open(path)
        has_alpha = img.mode in ("RGBA", "LA", "PA")
        arr = _np.array(img, dtype=_np.float64)

        # sRGB→linear on RGB channels only (leave alpha untouched)
        rgb = arr[..., :3] / 255.0
        low = rgb <= 0.04045
        rgb[low]  = rgb[low] / 12.92
        rgb[~low] = ((rgb[~low] + 0.055) / 1.055) ** 2.4
        arr[..., :3] = _np.clip(rgb * 255.0, 0, 255).astype(_np.uint8)

        _PILImage.fromarray(arr.astype(_np.uint8)).save(path, "PNG")
        _log(f"sRGB→linear conversion applied to {os.path.basename(path)}")
        return True
    except ImportError:
        pass

    # Fallback: QImage with LUT (slower but no extra dependencies)
    try:
        img = QImage(path)
        if img.isNull():
            return False
        # Use ARGB32 format (0xAARRGGBB packed as 32-bit)
        img = img.convertToFormat(_ImgFmt)

        # Build sRGB→linear LUT
        lut = [0] * 256
        for i in range(256):
            c = i / 255.0
            lut[i] = max(0, min(255, int((
                (c / 12.92) if c <= 0.04045
                else ((c + 0.055) / 1.055) ** 2.4
            ) * 255.0 + 0.5)))

        w, h = img.width(), img.height()
        for y in range(h):
            for x in range(w):
                px = img.pixel(x, y)
                # ARGB32: (A << 24) | (R << 16) | (G << 8) | B
                a = (px >> 24) & 0xFF
                r = lut[(px >> 16) & 0xFF]
                g = lut[(px >> 8) & 0xFF]
                b = lut[px & 0xFF]
                img.setPixel(x, y, (a << 24) | (r << 16) | (g << 8) | b)

        img.save(path, "PNG")
        _log(f"sRGB→linear conversion applied (QImage) to {os.path.basename(path)}")
        return True
    except Exception as e:
        _log(f"sRGB→linear conversion failed: {e}", "warning")
        return False


def _linear_to_srgb_file(path):
    """Convert a linear PNG file to sRGB color space in-place.

    Used to pre-encode linear mesh-map data before importing into the
    Base Color fill layer.  SP's Base Color channel is sRGB, so raw linear
    values look wrong in the viewport.  Pre-encoding with linear→sRGB
    means SP's sRGB display pipeline gives back the correct linear
    appearance.
    """
    try:
        from PIL import Image as _PILImage
        import numpy as _np

        img = _PILImage.open(path)
        arr = _np.array(img, dtype=_np.float64)

        rgb = arr[..., :3] / 255.0
        low = rgb <= 0.0031308
        rgb[low]  = rgb[low] * 12.92
        rgb[~low] = 1.055 * _np.power(rgb[~low], 1.0 / 2.4) - 0.055
        arr[..., :3] = _np.clip(rgb * 255.0, 0, 255).astype(_np.uint8)

        _PILImage.fromarray(arr.astype(_np.uint8)).save(path, "PNG")
        _log(f"linear→sRGB encoding applied to {os.path.basename(path)}")
        return True
    except ImportError:
        pass

    # Fallback: QImage with LUT
    try:
        img = QImage(path)
        if img.isNull():
            return False
        img = img.convertToFormat(_ImgFmt)

        lut = [0] * 256
        for i in range(256):
            c = i / 255.0
            lut[i] = max(0, min(255, int((
                (c * 12.92) if c <= 0.0031308
                else (1.055 * (c ** (1.0 / 2.4)) - 0.055)
            ) * 255.0 + 0.5)))

        w, h = img.width(), img.height()
        for y in range(h):
            for x in range(w):
                px = img.pixel(x, y)
                a = (px >> 24) & 0xFF
                r = lut[(px >> 16) & 0xFF]
                g = lut[(px >> 8) & 0xFF]
                b = lut[px & 0xFF]
                img.setPixel(x, y, (a << 24) | (r << 16) | (g << 8) | b)

        img.save(path, "PNG")
        _log(f"linear→sRGB encoding applied (QImage) to {os.path.basename(path)}")
        return True
    except Exception as e:
        _log(f"linear→sRGB conversion failed: {e}", "warning")
        return False


def _prepare_udim_for_import(tile_paths, base_name="bmpaint"):
    """Copy UDIM tile files to a temp directory using MARI naming convention
    (``name.UDIM.ext``) which SP's resource import recognises for
    automatic sequence discovery.

    *tile_paths* is a list of existing tile file paths whose filenames
    end with ``_DDDD.ext`` (underscore-separated UDIM number).

    Returns the path to the **first** tile in the new directory,
    ready to pass to ``import_project_resource``.
    """
    import re as _re_prep
    tmp = tempfile.mkdtemp(prefix="bmpaint_udim_")
    pattern = _re_prep.compile(r'.*?_(\d{4})\.\w+$')
    first = None
    for src in sorted(tile_paths):
        m = pattern.match(os.path.basename(src))
        if not m:
            continue
        tid = m.group(1)
        ext = os.path.splitext(src)[1]
        dst = os.path.join(tmp, f"{base_name}.{tid}{ext}")
        shutil.copy2(src, dst)
        if first is None:
            first = dst
        _log(f"UDIM copy: {os.path.basename(src)} → {os.path.basename(dst)}")
    return first


def _import_and_apply(texture_set, usage, file_path):
    """Import file_path as a project resource and assign it to the map slot.

    For UDIM texture sets, sibling tile files in the same directory are
    copied to a temp directory with MARI naming (``name.UDIM.ext``) so
    that SP's import_project_resource can discover them as a sequence.
    """
    try:
        texture_usage = _find_texture_usage()
        if texture_usage is None:
            return False

        import_path = file_path

        # Derive a clean base name for the resource (no UDIM number)
        res_name = os.path.splitext(os.path.basename(import_path))[0]
        import re as _re_rn
        res_name = _re_rn.sub(r'[\._]\d{4}$', '', res_name)

        _log(f"Importing '{os.path.basename(import_path)}' name='{res_name}' "
             f"Usage={texture_usage!r}")

        # Prefer import_project_resource so the resource lives in the project.
        # Fall back to import_session_resource if that fails.
        res = None
        try:
            res = spresource.import_project_resource(
                import_path, texture_usage, name=res_name)
            _log(f"import_project_resource → {res!r}")
        except Exception as e1:
            _log(f"import_project_resource failed ({e1}), trying session import…",
                 "warning")
            try:
                res = spresource.import_session_resource(
                    import_path, texture_usage, name=res_name)
                _log(f"import_session_resource → {res!r}")
            except Exception as e2:
                _log(f"import_session_resource also failed: {e2}", "error")
                return False

        if res is None:
            _log("Import returned None", "error")
            return False

        # set_mesh_map_resource calls .url() internally, so it needs a ResourceID not a Resource
        texture_set.set_mesh_map_resource(usage, res.identifier())
        _log(f"Applied {MESH_MAP_INFO[usage][0]} → '{texture_set.name()}'")
        return True

    except Exception as e:
        _log(f"Import failed: {e}", "error")
        _log(traceback.format_exc(), "error")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# 3D Paint Mode — uses SP's native painting via temporary layer stack
# ─────────────────────────────────────────────────────────────────────────────

# Module-level reference to the active 3D-paint apply widget (only one at a time)
_active_3d_paint_widget = None


class _BMPApplyWidget(QtWidgets.QDialog):
    """Frameless floating bar at bottom-center of screen during
    2D/3D baked-map painting mode. Always on top of SP."""

    _LAYER_NAME = "__BMP_Paint__"

    def __init__(self, texture_set, usage, fill_layer_node,
                 paint_effect_node, source_path, parent_dock,
                 paint_mode='3D', parent=None):
        super().__init__(None)  # No parent — independent top-level window
        self._ts = texture_set
        self._usage = usage
        self._fill_node = fill_layer_node
        self._paint_node = paint_effect_node
        self._source_path = source_path
        self._parent_dock = parent_dock
        self._paint_mode = paint_mode  # '2D' or '3D'

        # Cache previous state so we can restore on Apply/Cancel
        self._prev_ui_mode = _get_sp_ui_mode()

        # Frameless, always-on-top, tool window (no taskbar entry)
        flags = (Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.WindowStaysOnTopHint |
                 Qt.WindowType.Tool) if _QT == 6 else (
                 Qt.FramelessWindowHint |
                 Qt.WindowStaysOnTopHint |
                 Qt.Tool)
        self.setWindowFlags(flags)
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground if _QT == 6
            else Qt.WA_TranslucentBackground)

        label = MESH_MAP_INFO[usage][0]

        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(12)

        # Background bar
        self.setStyleSheet(
            "_BMPApplyWidget { background: rgba(25,25,25,230);"
            "border: 1px solid #555; border-radius: 8px; }")

        mode_color = '#6af' if paint_mode == '3D' else '#fa6'
        info = QtWidgets.QLabel(
            f"<span style='color:{mode_color}; font-weight:bold;'>{paint_mode} Paint</span>"
            f"<span style='color:#999;'>  —  {label}</span>")
        lay.addWidget(info)

        lay.addSpacing(8)

        btn_apply = QtWidgets.QPushButton("  ✔ Apply  ")
        btn_apply.setStyleSheet(
            "QPushButton{background:#2d7a3a;color:white;font-weight:bold;"
            "padding:6px 18px; border-radius:4px; font-size:11px;}"
            "QPushButton:hover{background:#3a9a4a;}")
        btn_apply.clicked.connect(self._apply)
        lay.addWidget(btn_apply)

        btn_cancel = QtWidgets.QPushButton("  ✖ Cancel  ")
        btn_cancel.setStyleSheet(
            "QPushButton{background:#5a2222;color:white;padding:6px 14px;"
            "border-radius:4px; font-size:11px;}"
            "QPushButton:hover{background:#7a2929;}")
        btn_cancel.clicked.connect(self._cancel)
        lay.addWidget(btn_cancel)

        self.adjustSize()
        self._position_bottom_center()
        self.show()
        self.raise_()

        # Reposition periodically to follow SP window moves
        self._pos_timer = QtCore.QTimer(self)
        self._pos_timer.timeout.connect(self._position_bottom_center)
        self._pos_timer.start(500)

    def _find_viewport_rect(self):
        """Get the screen-space rectangle of SP's viewport area.
        Returns (x, y, w, h) in global screen coords, or None."""
        main_win = _find_sp_main_window()
        if not main_win:
            return None
        try:
            import shiboken6
        except ImportError:
            try:
                import shiboken2 as shiboken6
            except ImportError:
                shiboken6 = None
        try:
            cw = main_win.centralWidget()
            # Check if the C++ object is still valid
            if cw and (shiboken6 is None or shiboken6.isValid(cw)):
                if cw.isVisible() and cw.width() > 200:
                    pos = cw.mapToGlobal(QPoint(0, 0))
                    return (pos.x(), pos.y(), cw.width(), cw.height())
        except (RuntimeError, Exception):
            pass
        # Fallback: use the main window geometry
        try:
            geo = main_win.geometry()
            return (geo.x(), geo.y(), geo.width(), geo.height())
        except (RuntimeError, Exception):
            pass
        return None

    def _position_bottom_center(self):
        """Position at bottom center of SP's viewport."""
        try:
            rect = self._find_viewport_rect()
            if rect:
                rx, ry, rw, rh = rect
                w = self.width()
                h = self.height()
                x = rx + (rw - w) // 2
                y = ry + rh - h - 30
                self.move(x, y)
        except (RuntimeError, Exception):
            pass

    def _apply(self):
        """Export the painted result, apply to baked map, clean up.
        Handles both single-tile and UDIM texture sets."""
        global _active_3d_paint_widget
        self.hide()
        try:
            import substance_painter.export as spexport

            ts_name = self._ts.name()
            label = MESH_MAP_INFO[self._usage][0].replace(" ", "_")
            safe_ts = "".join(c if c.isalnum() or c in "-_." else "_" for c in ts_name)

            # Check if this texture set uses UDIMs
            has_udim = False
            try:
                has_udim = self._ts.has_uv_tiles()
            except Exception:
                pass

            # For UDIM, use _$udim in the export filename (SP's expected
            # token format).  After export we rename to MARI naming
            # (name.UDIM.ext) before importing.
            if has_udim:
                file_stem = f"{safe_ts}_{label}_3dpaint_$udim"
            else:
                file_stem = f"{safe_ts}_{label}_3dpaint"

            # Snapshot work dir before export to detect new files
            try:
                before = set(os.listdir(_work_dir()))
            except Exception:
                before = set()

            export_cfg = {
                "exportPath": _work_dir(),
                "exportShaderParams": False,
                "exportList": [{"rootPath": ts_name}],
                "exportPresets": [{
                    "name": "__bmp3d_export__",
                    "maps": [{
                        "fileName": file_stem,
                        "parameters": {
                            "fileFormat": "png",
                            "bitDepth": "8",
                            "dithering": False,
                            "sRGB": False,
                            "paddingAlgorithm": "diffusion",
                            "dilationDistance": 16,
                        },
                        "channels": [
                            {"destChannel": "R", "srcMapType": "documentMap",
                             "srcMapName": "basecolor", "srcChannel": "R"},
                            {"destChannel": "G", "srcMapType": "documentMap",
                             "srcMapName": "basecolor", "srcChannel": "G"},
                            {"destChannel": "B", "srcMapType": "documentMap",
                             "srcMapName": "basecolor", "srcChannel": "B"},
                        ],
                    }],
                }],
                "defaultExportPreset": "__bmp3d_export__",
            }

            _log("Paint mode: exporting painted Base Color…")
            spexport.export_project_textures(export_cfg)

            # Find exported files
            try:
                after = set(os.listdir(_work_dir()))
                new_files = sorted(after - before)
            except Exception:
                new_files = []

            # Collect all exported PNGs matching our stem.
            # On repeat applies the files already exist (overwritten in
            # place), so we can't rely only on new_files — also scan for
            # any file in work_dir that matches the stem.
            stem_base = file_stem.replace("_$udim", "")
            exported = []
            try:
                for f in sorted(os.listdir(_work_dir())):
                    if f.endswith('.png') and stem_base in f:
                        exported.append(os.path.join(_work_dir(), f))
            except Exception:
                pass

            if not exported:
                raise RuntimeError("Export produced no files")

            _log(f"Paint mode: exported {len(exported)} file(s)")

            # For UDIM: rename exported tiles from underscore naming
            # (name_1001.png) to MARI naming (name.1001.png) so that
            # import_project_resource can discover the full sequence.
            if has_udim:
                import re as _re_rename
                renamed = []
                for ep in exported:
                    fname = os.path.basename(ep)
                    m = _re_rename.match(r'^(.+?)_(\d{4})(\.png)$', fname)
                    if m:
                        new_name = f"{m.group(1)}.{m.group(2)}{m.group(3)}"
                        new_path = os.path.join(os.path.dirname(ep), new_name)
                        os.replace(ep, new_path)
                        renamed.append(new_path)
                    else:
                        renamed.append(ep)
                exported = renamed
                _log(f"Renamed {len(exported)} tile(s) to MARI naming")

            import_path = exported[0]

            if not _import_and_apply(self._ts, self._usage, import_path):
                raise RuntimeError("Failed to re-import the painted map into SP")

            # Update the cache for the card thumbnail
            cache_path = os.path.join(_work_dir(), f"{safe_ts}_{label}.png")
            try:
                shutil.copy2(import_path, cache_path)
            except Exception:
                pass

            _log(f"3D Paint: applied {MESH_MAP_INFO[self._usage][0]} successfully")

        except Exception as e:
            _log(f"3D Paint apply failed: {e}", "error")
            _log(traceback.format_exc(), "error")
            self.show()  # Re-show so user can retry
            QtWidgets.QMessageBox.critical(
                None, "3D Paint Apply Failed",
                f"Could not apply painted map:\n\n{e}")
            return  # Don't clean up — let user retry

        # Clean up
        self._cleanup()

    def _cancel(self):
        """Cancel 3D paint mode without applying."""
        self.hide()
        self._cleanup()

    def _cleanup(self):
        """Remove temp layers, restore view, remove this widget."""
        global _active_3d_paint_widget
        import substance_painter.layerstack as splayerstack

        # IMPORTANT: restore viewport to Material BEFORE deleting layers.
        # If we delete the layer while viewport is in solo channel mode,
        # SP crashes with "Invalid edition context".
        _restore_viewport_material()

        # Small delay to let the viewport mode switch complete before layer deletion
        QtCore.QTimer.singleShot(100, lambda: self._finish_cleanup(splayerstack))

    def _finish_cleanup(self, splayerstack):
        """Second phase of cleanup — delete layers, restore UI mode, remove widget."""
        global _active_3d_paint_widget

        try:
            splayerstack.delete_node(self._fill_node)
            _log("Paint mode: temp layer deleted")
        except Exception as e:
            _log(f"Paint mode: layer cleanup failed: {e}", "warning")

        # Restore previous UI mode (2D/3D/2D+3D)
        if self._prev_ui_mode is not None:
            try:
                import _substance_painter.ui as _spui_internal
                _spui_internal.switch_to_mode(self._prev_ui_mode)
                _log(f"Paint mode: restored UI mode to {self._prev_ui_mode}")
            except Exception as e:
                _log(f"Paint mode: UI mode restore failed: {e}", "warning")

        # Refresh only the specific map card that was edited
        if self._parent_dock:
            try:
                self._parent_dock._refresh_single_thumbnail(self._usage)
            except Exception:
                pass

        # Remove this overlay
        _active_3d_paint_widget = None
        self._pos_timer.stop()
        self.close()
        self.deleteLater()


def _find_sp_main_window():
    """Find SP's QMainWindow."""
    for w in QtWidgets.QApplication.topLevelWidgets():
        if isinstance(w, QtWidgets.QMainWindow):
            return w
    return None


def _get_sp_ui_mode():
    """Get SP's current UI mode (2D/3D/2D+3D) and the UIMode enum."""
    try:
        import _substance_painter.ui as _spui_internal
        mode = _spui_internal.get_current_mode()
        if not hasattr(_get_sp_ui_mode, '_probed'):
            _get_sp_ui_mode._probed = True
            members = [m for m in dir(_spui_internal.UIMode) if not m.startswith('_')]
            _log(f"UIMode members: {members}, current: {mode}")
        return mode
    except Exception as e:
        _log(f"get_current_mode failed: {e}", "warning")
        return None


def _set_sp_ui_mode(mode_name):
    """Set SP's UI mode by name (e.g., 'Painting' for 3D, 'Painting2D' for 2D)."""
    try:
        import _substance_painter.ui as _spui_internal
        mode_enum = _spui_internal.UIMode
        # Try the given name first, then common alternatives
        for name in [mode_name, mode_name.replace(' ', ''),
                     mode_name.lower(), mode_name.upper()]:
            if hasattr(mode_enum, name):
                _spui_internal.switch_to_mode(getattr(mode_enum, name))
                _log(f"UI mode switched to {name}")
                return True
        # Log available modes for debugging
        members = [m for m in dir(mode_enum) if not m.startswith('_')]
        _log(f"UI mode '{mode_name}' not found. Available: {members}", "warning")
        return False
    except Exception as e:
        _log(f"switch_to_mode failed: {e}", "warning")
        return False


def _find_viewport_menu_action(action_text):
    """Find a QAction in SP's Viewport menu by its text."""
    main_win = _find_sp_main_window()
    if not main_win or not hasattr(main_win, 'menuBar'):
        return None
    menu_bar = main_win.menuBar()
    if not menu_bar:
        return None
    for menu_action in menu_bar.actions():
        menu = menu_action.menu()
        if not menu:
            continue
        menu_name = menu_action.text().replace('&', '').strip()
        if menu_name != 'Viewport':
            continue
        for sa in menu.actions():
            t = sa.text().replace('&', '').strip()
            if t == action_text:
                return sa
    return None


def _switch_viewport_solo_basecolor():
    """No-op — viewport mode is left unchanged. User sets it manually."""
    pass


def _restore_viewport_material():
    """No-op — viewport mode is left unchanged. User restores it manually."""
    pass


def _enter_paint_mode(texture_set, usage, source_path, parent_dock, mode=None):
    """Set up SP's native layer stack for baked-map painting.
    Creates a Fill layer with the baked map, adds a Paint Effect on top,
    switches viewport to solo Base Color, and shows Apply bar.
    Keeps the current 2D/3D viewport mode (doesn't switch)."""
    global _active_3d_paint_widget
    import substance_painter.layerstack as splayerstack
    import substance_painter.textureset as spts

    try:
        # Switch to the correct texture set's stack before creating layers
        ts_stack = spts.Stack.from_name(texture_set.name())
        spts.set_active_stack(ts_stack)
        stack = ts_stack
        _log(f"Paint mode: switched to texture set '{texture_set.name()}'")

        # source_path is already in MARI naming (name.UDIM.ext) for UDIM
        # texture sets, so SP's import should discover sibling tiles.
        import_path = source_path

        texture_usage = _find_texture_usage()
        if texture_usage is None:
            raise RuntimeError("Cannot find texture usage enum")

        # Derive clean base name (strip UDIM number) to help SP
        # recognise the UDIM sequence on import
        import re as _re_rn2
        res_name = os.path.splitext(os.path.basename(import_path))[0]
        res_name = _re_rn2.sub(r'[\._]\d{4}$', '', res_name)

        res = spresource.import_project_resource(
            import_path, texture_usage, name=res_name)
        res_id = res.identifier()
        _log(f"Paint mode: imported '{os.path.basename(import_path)}' "
             f"name='{res_name}' → {res_id}")

        # Create Fill layer at top of stack
        pos_top = splayerstack.InsertPosition.from_textureset_stack(stack)
        fill_layer = splayerstack.insert_fill(pos_top)
        fill_layer.set_name(_BMPApplyWidget._LAYER_NAME)

        # Set the fill layer's Base Color source to our baked map texture
        from substance_painter.textureset import ChannelType
        try:
            fill_layer.set_source(ChannelType.BaseColor, res_id)
        except Exception:
            try:
                fill_layer.set_source(None, res_id)
            except Exception:
                pass

        # Insert a Paint Effect inside the fill layer's Content stack
        pos_content = splayerstack.InsertPosition.inside_node(
            fill_layer, splayerstack.NodeStack.Content)
        paint_effect = splayerstack.insert_paint(pos_content)

        # Select the paint effect so it's the active painting target
        splayerstack.set_selected_nodes([paint_effect])

        # Solo Base Color channel — first go to Material, then next channel
        _switch_viewport_solo_basecolor()

        # Create the overlay Apply/Cancel bar (no mode switch — keep current 2D/3D)
        label = MESH_MAP_INFO[usage][0]
        apply_widget = _BMPApplyWidget(
            texture_set, usage, fill_layer, paint_effect,
            source_path, parent_dock, paint_mode='Paint')
        _active_3d_paint_widget = apply_widget
        _log(f"Paint mode activated for {label} — paint with SP tools, then click Apply")

        return True

    except Exception as e:
        _log(f"Paint mode setup failed: {e}", "error")
        _log(traceback.format_exc(), "error")
        QtWidgets.QMessageBox.critical(
            None, "Paint Setup Failed",
            f"Could not set up paint mode:\n\n{e}\n\n"
            "Check the Python Console for details.")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Paint Canvas
# ─────────────────────────────────────────────────────────────────────────────


import math    as _math
import zipfile as _zipfile
import ctypes  as _ctypes

# ─────────────────────────────────────────────────────────────────────────────
# Auto-extract mesh from .spp (it's a ZIP)
# ─────────────────────────────────────────────────────────────────────────────

def _extract_mesh_from_project():
    """
    Find the project's source mesh file.

    Strategy (in order):
    1. spproject.metadata() — cleanest, returns project metadata dict
    2. Scan the .spp binary for embedded file-path strings ending in mesh extensions
       (.fbx, .obj, .dae, .ply) — SPP is HDF5 so strings are stored as raw UTF-8
    3. Return None and let the user pick manually via Load Mesh…
    """
    MESH_EXTS = (b'.fbx', b'.FBX', b'.obj', b'.OBJ',
                 b'.dae', b'.DAE', b'.ply', b'.PLY')

    # ── Strategy 1: Python API metadata ──────────────────────────────────────
    try:
        if hasattr(spproject, 'metadata'):
            meta = spproject.metadata()
            if isinstance(meta, dict):
                for key in ('mesh_file_path', 'meshFilePath', 'mesh', 'source_mesh'):
                    v = meta.get(key)
                    if v and os.path.isfile(str(v)):
                        _log(f"Mesh from metadata[{key}]: {v}")
                        return str(v)
    except Exception as e:
        _log(f"metadata() failed: {e}", "warning")

    # ── Strategy 2: scan the .spp binary for path strings ────────────────────
    try:
        spp = spproject.file_path()
    except Exception as e:
        _log(f"project.file_path(): {e}", "warning"); spp = None

    if spp and os.path.isfile(spp):
        try:
            import re as _re
            with open(spp, 'rb') as f:
                data = f.read()

            # Match any null-terminated or quote-delimited path string that ends
            # in a known mesh extension. HDF5 stores strings as raw UTF-8 bytes.
            candidates = []
            # Valid path characters: alphanumeric, path separators, spaces, dots,
            # underscores, hyphens, colons (drive letter), percent (URL encoding)
            import re as _re2
            _PATH_CHARS = set(
                'abcdefghijklmnopqrstuvwxyz'
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                '0123456789'
                '/\\:._- %()[]{}+='
            )
            for ext in MESH_EXTS:
                idx = 0
                while True:
                    pos = data.find(ext, idx)
                    if pos < 0: break
                    # Walk backward to find the start of the path string
                    # Only include valid path characters
                    start = pos
                    while start > 0:
                        byte = data[start-1:start]
                        if byte in (b'\x00', b'"', b"'", b'\n', b'\r'):
                            break
                        try:
                            ch = byte.decode('ascii')
                            if ch not in _PATH_CHARS:
                                break
                        except (UnicodeDecodeError, ValueError):
                            break
                        start -= 1
                    path_bytes = data[start:pos+len(ext)]
                    try:
                        path_str = path_bytes.decode('utf-8', errors='strict').strip('\x00 "\'')
                        # Sanity: must contain a drive letter or path separator,
                        # must look like a real path (e.g. C:\... or /home/...)
                        if len(path_str) > 4 and (':\\' in path_str or ':/' in path_str or path_str.startswith('/')):
                            # Reject if it has control characters
                            if not any(ord(c) < 32 for c in path_str):
                                candidates.append(path_str)
                    except Exception:
                        pass
                    idx = pos + 1

            def _clean_path(raw):
                """Normalise a raw path string extracted from the SPP binary."""
                import urllib.parse as _up
                p = raw.strip()
                # Strip leading garbage bytes / punctuation that aren't part of a path
                while p and p[0] in (',', "'", '"', '%', ' ', ';', '(', ')'):
                    p = p[1:]
                # Handle file:/// URIs with any number of slashes/backslashes
                # e.g. "file:///C:/foo", "file:\\\\\\C:\\foo"
                import re as _re3
                m = _re3.match(r'file:[/\\]+(.*)', p, _re3.IGNORECASE)
                if m:
                    p = _up.unquote(m.group(1))
                # Normalise slashes on Windows
                p = p.replace('/', os.sep)
                return p

            cleaned = []
            for raw in candidates:
                c = _clean_path(raw)
                if len(c) > 4:
                    cleaned.append(c)

            # Filter to existing files, prefer shortest (most direct) path
            existing = sorted(set(c for c in cleaned if os.path.isfile(c)), key=len)
            if existing:
                best = existing[0]
                _log(f"Mesh found by SPP binary scan: {best}")
                # If it's not an OBJ, look for an OBJ with the same stem first
                return best   # FBX, OBJ, DAE, PLY — all handled natively

            if cleaned:
                _log(f"Found mesh paths in SPP but none exist on disk: {cleaned[:3]}", "warning")
        except Exception as e:
            _log(f"SPP binary scan failed: {e}", "error")
    else:
        _log("Project not saved yet or file not found — use 'Load Mesh…'", "warning")

    return None


# ─────────────────────────────────────────────────────────────────────────────
# Math
# ─────────────────────────────────────────────────────────────────────────────


def _v3sub(a,b): return (a[0]-b[0],a[1]-b[1],a[2]-b[2])
def _v3dot(a,b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def _v3cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def _v3norm(a):
    l=(_v3dot(a,a))**0.5 or 1e-9; return (a[0]/l,a[1]/l,a[2]/l)

def _ray_tri(o,d,v0,v1,v2):
    e1=_v3sub(v1,v0); e2=_v3sub(v2,v0); h=_v3cross(d,e2); a=_v3dot(e1,h)
    if abs(a)<1e-7: return None
    f=1/a; s=_v3sub(o,v0); u=f*_v3dot(s,h)
    if not(0<=u<=1): return None
    q=_v3cross(s,e1); v=f*_v3dot(d,q)
    if v<0 or u+v>1: return None
    t=f*_v3dot(e2,q); return (t,u,v) if t>1e-7 else None

def _eye(yr, pr, dist, tgt):
    """Compute eye position on a sphere around tgt."""
    return (tgt[0] + dist * _math.cos(pr) * _math.sin(yr),
            tgt[1] + dist * _math.sin(pr),
            tgt[2] + dist * _math.cos(pr) * _math.cos(yr))

def _rotate_point_around(point, pivot, dyaw_deg, dpitch_deg, right_axis):
    """Rotate a 3D point around a pivot by dyaw (around world Y) then dpitch (around right_axis)."""
    # Translate to pivot-relative
    px, py, pz = point[0]-pivot[0], point[1]-pivot[1], point[2]-pivot[2]
    # Yaw rotation around world Y
    yr = _math.radians(dyaw_deg)
    cy, sy = _math.cos(yr), _math.sin(yr)
    rx, ry_, rz = cy*px + sy*pz, py, -sy*px + cy*pz
    # Pitch rotation around the right axis (Rodrigues' formula)
    pr = _math.radians(dpitch_deg)
    cp, sp = _math.cos(pr), _math.sin(pr)
    ax, ay, az = right_axis
    dot = ax*rx + ay*ry_ + az*rz
    cx_, cy_, cz_ = ay*rz - az*ry_, az*rx - ax*rz, ax*ry_ - ay*rx
    ox = rx*cp + cx_*sp + ax*dot*(1-cp)
    oy = ry_*cp + cy_*sp + ay*dot*(1-cp)
    oz = rz*cp + cz_*sp + az*dot*(1-cp)
    return (ox+pivot[0], oy+pivot[1], oz+pivot[2])

def _look_at_mat(eye, cen, up):
    f = _v3norm(_v3sub(cen, eye))
    r = _v3cross(f, _v3norm(up))
    rlen = (r[0]**2 + r[1]**2 + r[2]**2) ** 0.5
    if rlen < 1e-8:
        # f is nearly parallel to up — pick a fallback right vector
        r = _v3cross(f, (0, 0, 1) if abs(up[1]) > 0.9 else (0, 1, 0))
        rlen = (r[0]**2 + r[1]**2 + r[2]**2) ** 0.5
        if rlen < 1e-8:
            r = (1, 0, 0)
            rlen = 1.0
    r = (r[0]/rlen, r[1]/rlen, r[2]/rlen)
    u = _v3cross(r, f)
    # column-major
    return [r[0],u[0],-f[0],0, r[1],u[1],-f[1],0, r[2],u[2],-f[2],0,
            -_v3dot(r,eye),-_v3dot(u,eye),_v3dot(f,eye),1]

def _persp_mat(fovy,aspect,near,far):
    f=1/_math.tan(_math.radians(fovy)*0.5); nf=1/(near-far)
    return [f/aspect,0,0,0, 0,f,0,0, 0,0,(far+near)*nf,-1, 0,0,2*far*near*nf,0]

def _mat_mul(a,b):
    r=[0.0]*16
    for c in range(4):
        for row in range(4):
            r[c*4+row]=sum(a[k*4+row]*b[c*4+k] for k in range(4))
    return r


# ─────────────────────────────────────────────────────────────────────────────
# OBJ loader
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# Minimal FBX binary parser
# Supports FBX 7.1+ (binary format, magic "Kaydara FBX Binary  \x00\x1a\x00")
# Extracts: Vertices, PolygonVertexIndex, UV, Normals from all Geometry nodes.
# ─────────────────────────────────────────────────────────────────────────────

def _parse_fbx_binary(path):
    """
    Parse an FBX binary file and return (verts, uvs, normals, poly_indices).
    All lists are flat Python lists. poly_indices use FBX convention where the
    last index of each polygon is bitwise-NOT (negative-minus-one).
    Returns None on failure.
    """
    import struct as _st

    FBX_MAGIC = b"Kaydara FBX Binary  "

    try:
        with open(path, 'rb') as f:
            data = f.read()
    except Exception as e:
        _log(f"FBX read error: {e}", "error"); return None

    if not data.startswith(FBX_MAGIC):
        header_hex = data[:24].hex(' ')
        header_ascii = data[:40].decode('ascii', errors='replace')
        _log(f"Not a valid FBX binary file. Header hex: {header_hex}", "warning")
        _log(f"Header ASCII: {header_ascii!r}", "warning")
        return None

    version = _st.unpack_from('<I', data, 23)[0]
    is64 = version >= 7500   # FBX 7.5+ uses 64-bit offsets
    _log(f"FBX version: {version}, 64-bit: {is64}")

    # ── Low-level node reader ─────────────────────────────────────────────────

    def read_node(pos):
        """Read one FBX node record. Returns (name, props_dict, children, next_pos)."""
        if is64:
            if pos + 25 > len(data): return None
            end_off, n_props, prop_list_len = _st.unpack_from('<QQQ', data, pos)
            name_len = _st.unpack_from('<B', data, pos+24)[0]
            header_size = 25
        else:
            if pos + 13 > len(data): return None
            end_off, n_props, prop_list_len = _st.unpack_from('<III', data, pos)
            name_len = _st.unpack_from('<B', data, pos+12)[0]
            header_size = 13

        if end_off == 0:
            return None  # null record (end sentinel)

        name = data[pos+header_size : pos+header_size+name_len].decode('utf-8', errors='replace')
        prop_start = pos + header_size + name_len
        prop_end   = prop_start + prop_list_len

        # Parse properties
        props = []
        p = prop_start
        while p < prop_end:
            type_code = chr(data[p]); p += 1
            if type_code == 'C':   # bool
                props.append(bool(data[p])); p += 1
            elif type_code == 'Y': # int16
                props.append(_st.unpack_from('<h', data, p)[0]); p += 2
            elif type_code == 'I': # int32
                props.append(_st.unpack_from('<i', data, p)[0]); p += 4
            elif type_code == 'L': # int64
                props.append(_st.unpack_from('<q', data, p)[0]); p += 8
            elif type_code == 'F': # float32
                props.append(_st.unpack_from('<f', data, p)[0]); p += 4
            elif type_code == 'D': # float64
                props.append(_st.unpack_from('<d', data, p)[0]); p += 8
            elif type_code == 'S': # string
                slen = _st.unpack_from('<I', data, p)[0]; p += 4
                props.append(data[p:p+slen].decode('utf-8', errors='replace')); p += slen
            elif type_code == 'R': # raw bytes
                rlen = _st.unpack_from('<I', data, p)[0]; p += 4
                props.append(data[p:p+rlen]); p += rlen
            elif type_code in ('f','d','l','i','b'): # typed arrays
                arr_len  = _st.unpack_from('<I', data, p)[0]; p += 4
                encoding = _st.unpack_from('<I', data, p)[0]; p += 4
                comp_len = _st.unpack_from('<I', data, p)[0]; p += 4
                raw = data[p:p+comp_len]; p += comp_len
                if encoding == 1:
                    import zlib as _zl
                    raw = _zl.decompress(raw)
                fmt = {'f':'f','d':'d','l':'q','i':'i','b':'?'}[type_code]
                elem_size = {'f':4,'d':8,'l':8,'i':4,'b':1}[type_code]
                arr = list(_st.unpack_from(f'<{arr_len}{fmt}', raw))
                props.append(arr)
            else:
                break  # unknown type, skip rest of props

        # Parse children
        children = []
        child_pos = prop_end
        while child_pos < end_off:
            # Check for null sentinel
            sentinel_size = 25 if is64 else 13
            if child_pos + sentinel_size <= end_off:
                sentinel = data[child_pos:child_pos+sentinel_size]
                if all(b == 0 for b in sentinel):
                    break
            result = read_node(child_pos)
            if result is None: break
            c_name, c_props, c_children, child_pos = result
            children.append((c_name, c_props, c_children))

        return name, props, children, int(end_off)

    # ── Walk top-level nodes ──────────────────────────────────────────────────

    def find_children(node_list, name):
        return [(p,c) for (n,p,c) in node_list if n == name]

    def find_child(node_list, name):
        r = find_children(node_list, name)
        return r[0] if r else None

    # Parse all top-level nodes
    top_nodes = []
    pos = 27  # skip magic + version
    while pos < len(data) - (25 if is64 else 13):
        result = read_node(pos)
        if result is None: break
        name, props, children, next_pos = result
        if next_pos <= pos: break
        top_nodes.append((name, props, children))
        pos = next_pos

    # Find Objects node
    objects = find_child(top_nodes, 'Objects')
    if not objects:
        _log("FBX: No 'Objects' node found", "warning"); return None

    _, obj_children = objects

    # Collect all Geometry nodes
    all_verts = []; all_uvs = []; all_norms = []; all_poly = []

    for geom_props, geom_children in find_children(obj_children, 'Geometry'):
        # Check this is a Mesh geometry
        is_mesh = any(isinstance(p, str) and p == 'Mesh' for p in geom_props)
        if not is_mesh and len(geom_props) >= 3:
            is_mesh = (isinstance(geom_props[2], str) and 'Mesh' in geom_props[2])
        # Some files just have all geometry, accept anyway

        verts_node = find_child(geom_children, 'Vertices')
        poly_node  = find_child(geom_children, 'PolygonVertexIndex')

        if not verts_node or not poly_node: continue

        vp, _ = verts_node
        pp, _ = poly_node
        verts_flat = vp[0] if vp and isinstance(vp[0], list) else []
        poly_idx   = pp[0] if pp and isinstance(pp[0], list) else []
        if not verts_flat or not poly_idx: continue

        # Build position list: every 3 floats is one vertex
        positions = [(verts_flat[i],verts_flat[i+1],verts_flat[i+2])
                     for i in range(0, len(verts_flat)-2, 3)]

        # UVs — inside LayerElementUV
        uv_coords = []; uv_index = []; uv_by_vertex = False
        for le_props, le_children in find_children(geom_children, 'LayerElementUV'):
            uv_node  = find_child(le_children, 'UV')
            uvi_node = find_child(le_children, 'UVIndex')
            mm_node  = find_child(le_children, 'MappingInformationType')
            ri_node  = find_child(le_children, 'ReferenceInformationType')
            if mm_node:
                mp, _ = mm_node
                mapping = mp[0] if mp else ''
                uv_by_vertex = mapping in ('ByVertice', 'ByControlPoint')
            if uv_node:
                up, _ = uv_node
                raw = up[0] if up and isinstance(up[0], list) else []
                uv_coords = [(raw[i],raw[i+1]) for i in range(0,len(raw)-1,2)]
            if uvi_node:
                up, _ = uvi_node
                uv_index = up[0] if up and isinstance(up[0], list) else []
            break  # use first UV layer

        # Normals — inside LayerElementNormal
        norm_vals = []; norm_index = []; norm_by_vertex = False
        for le_props, le_children in find_children(geom_children, 'LayerElementNormal'):
            n_node  = find_child(le_children, 'Normals')
            ni_node = find_child(le_children, 'NormalsIndex')
            mm_node = find_child(le_children, 'MappingInformationType')
            if mm_node:
                mp, _ = mm_node
                mapping = mp[0] if mp else ''
                # ByVertice / ByControlPoint = normals indexed by vertex index
                norm_by_vertex = mapping in ('ByVertice', 'ByControlPoint')
            if n_node:
                np_, _ = n_node
                raw = np_[0] if np_ and isinstance(np_[0], list) else []
                norm_vals = [(raw[i],raw[i+1],raw[i+2]) for i in range(0,len(raw)-2,3)]
            if ni_node:
                np_, _ = ni_node
                norm_index = np_[0] if np_ and isinstance(np_[0], list) else []
            break

        # Triangulate polygons
        # FBX stores polygons: last vertex index is ~index (bitwise NOT)
        vertices_out = []; uvs_out = []; norms_out = []
        pv_cursor = 0  # running index into the polygon vertex stream
        face_verts = []
        face_pv_indices = []  # positions within the poly stream for UV/normal lookup

        for raw_idx in poly_idx:
            is_last = raw_idx < 0
            vi = (~raw_idx) if is_last else raw_idx
            face_verts.append(vi)
            face_pv_indices.append(pv_cursor)
            pv_cursor += 1

            if is_last:
                # Triangulate fan
                for j in range(1, len(face_verts)-1):
                    for k in (0, j, j+1):
                        vi_k = face_verts[k]
                        pv_k = face_pv_indices[k]

                        # Position
                        pos3 = positions[vi_k] if vi_k < len(positions) else (0,0,0)

                        # UV — ByVertice uses vertex index, ByPolygonVertex uses pv cursor
                        if uv_coords:
                            if uv_by_vertex:
                                uv = uv_coords[vi_k] if vi_k < len(uv_coords) else (0,0)
                            elif uv_index:
                                ui = uv_index[pv_k] if pv_k < len(uv_index) else 0
                                uv = uv_coords[ui] if ui < len(uv_coords) else (0,0)
                            else:
                                uv = uv_coords[pv_k] if pv_k < len(uv_coords) else (0,0)
                        else:
                            uv = (0.0, 0.0)

                        # Normal — ByVertice uses vertex index, ByPolygonVertex uses pv cursor
                        if norm_vals:
                            if norm_by_vertex:
                                n3 = norm_vals[vi_k] if vi_k < len(norm_vals) else (0,1,0)
                            elif norm_index:
                                ni2 = norm_index[pv_k] if pv_k < len(norm_index) else 0
                                n3 = norm_vals[ni2] if ni2 < len(norm_vals) else (0,1,0)
                            else:
                                n3 = norm_vals[pv_k] if pv_k < len(norm_vals) else (0,1,0)
                        else:
                            n3 = (0,1,0)

                        vertices_out.append(pos3)
                        uvs_out.append(uv)
                        norms_out.append(n3)

                face_verts = []; face_pv_indices = []

        if vertices_out:
            all_verts  += vertices_out
            all_uvs    += uvs_out
            all_norms  += norms_out

    if not all_verts:
        _log("FBX: No geometry data found", "warning"); return None

    _log(f"FBX parsed: {len(all_verts)//3} triangles from {len(all_verts)} verts")
    return all_verts, all_uvs, all_norms


def _parse_fbx_ascii(path):
    """
    Parse an ASCII FBX file and return (verts, uvs, normals).
    ASCII FBX files start with lines like:
        ; FBX 7.x project file
    or
        FBXHeaderExtension:  {
    Returns None on failure.
    """
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    except Exception as e:
        _log(f"FBX ASCII read error: {e}", "error")
        return None

    # Quick sanity check — ASCII FBX files contain these markers
    if 'FBXHeaderExtension' not in text and 'FBX' not in text[:200]:
        _log("Not a valid ASCII FBX file", "warning")
        return None

    import re

    def _extract_numbers(block_text):
        """Extract all numbers from a comma/whitespace-separated block."""
        return [float(x) for x in re.findall(r'-?\d+\.?\d*(?:[eE][+-]?\d+)?', block_text)]

    # Find Geometry objects (Model or Geometry blocks containing Vertices)
    all_verts = []
    all_uvs = []
    all_norms = []

    # Strategy: find Vertices, PolygonVertexIndex, UV, Normals blocks
    # Pattern for named data arrays like:  Vertices: *12345 {\n  a: 1.0,2.0,...\n  }
    def _find_array_block(name, search_text):
        """Find a named array block and extract its numbers."""
        # Match: Name: *COUNT { ... a: DATA ... }
        pattern = re.compile(
            rf'{name}\s*:\s*\*\d+\s*\{{[^}}]*?a:\s*([\s\S]*?)\}}',
            re.MULTILINE
        )
        m = pattern.search(search_text)
        if m:
            return _extract_numbers(m.group(1))
        # Fallback: older FBX ASCII format without *COUNT
        pattern2 = re.compile(
            rf'{name}\s*:\s*([\d\s.,eE+\-]+)',
            re.MULTILINE
        )
        m2 = pattern2.search(search_text)
        if m2:
            return _extract_numbers(m2.group(1))
        return []

    # Find all Geometry sections
    geo_pattern = re.compile(
        r'(?:Geometry|Model)\s*:.*?\{([\s\S]*?)(?=\n\s*(?:Geometry|Model|Objects)\s*:|\Z)',
        re.MULTILINE
    )

    geo_blocks = geo_pattern.findall(text)
    if not geo_blocks:
        # Try the whole file as one block
        geo_blocks = [text]

    for block in geo_blocks:
        verts_flat = _find_array_block('Vertices', block)
        poly_idx_raw = _find_array_block('PolygonVertexIndex', block)

        if not verts_flat or not poly_idx_raw:
            continue

        poly_idx = [int(x) for x in poly_idx_raw]

        # Build position list
        positions = [(verts_flat[i], verts_flat[i+1], verts_flat[i+2])
                     for i in range(0, len(verts_flat) - 2, 3)]

        # UVs
        uv_raw = _find_array_block('UV ', block)  # note trailing space to avoid matching UVIndex
        if not uv_raw:
            uv_raw = _find_array_block(r'UV(?=\s*:)', block)
        uv_index_raw = _find_array_block('UVIndex', block)
        uv_coords = [(uv_raw[i], uv_raw[i+1]) for i in range(0, len(uv_raw) - 1, 2)] if uv_raw else []
        uv_index = [int(x) for x in uv_index_raw] if uv_index_raw else []

        # Normals
        norm_raw = _find_array_block('Normals', block)
        norm_index_raw = _find_array_block('NormalsIndex', block)
        norm_vals = [(norm_raw[i], norm_raw[i+1], norm_raw[i+2])
                     for i in range(0, len(norm_raw) - 2, 3)] if norm_raw else []
        norm_index = [int(x) for x in norm_index_raw] if norm_index_raw else []

        # Triangulate using FBX bitwise-NOT convention (same as binary parser)
        vertices_out = []
        uvs_out = []
        norms_out = []
        pv_cursor = 0
        face_verts = []
        face_pv_indices = []

        for raw_idx in poly_idx:
            is_last = raw_idx < 0
            vi = (~raw_idx) if is_last else raw_idx
            face_verts.append(vi)
            face_pv_indices.append(pv_cursor)
            pv_cursor += 1

            if is_last:
                for j in range(1, len(face_verts) - 1):
                    for k in (0, j, j + 1):
                        vi_k = face_verts[k]
                        pv_k = face_pv_indices[k]

                        pos3 = positions[vi_k] if vi_k < len(positions) else (0, 0, 0)

                        if uv_coords:
                            if uv_index:
                                ui = uv_index[pv_k] if pv_k < len(uv_index) else 0
                                uv = uv_coords[ui] if ui < len(uv_coords) else (0, 0)
                            else:
                                uv = uv_coords[pv_k] if pv_k < len(uv_coords) else (0, 0)
                        else:
                            uv = (0.0, 0.0)

                        if norm_vals:
                            if norm_index:
                                ni2 = norm_index[pv_k] if pv_k < len(norm_index) else 0
                                n3 = norm_vals[ni2] if ni2 < len(norm_vals) else (0, 1, 0)
                            else:
                                n3 = norm_vals[pv_k] if pv_k < len(norm_vals) else (0, 1, 0)
                        else:
                            n3 = (0, 1, 0)

                        vertices_out.append(pos3)
                        uvs_out.append(uv)
                        norms_out.append(n3)

                face_verts = []
                face_pv_indices = []

        if vertices_out:
            all_verts += vertices_out
            all_uvs += uvs_out
            all_norms += norms_out

    if not all_verts:
        _log("ASCII FBX: No geometry data found", "warning")
        return None

    _log(f"ASCII FBX parsed: {len(all_verts) // 3} triangles from {len(all_verts)} verts")
    return all_verts, all_uvs, all_norms


class MeshData:
    __slots__=('tris','vbo_data','tri_count','_grid','_grid_res','_grid_min','_grid_inv','_pos_map','_pos_map_size')
    def __init__(self):
        self.tris=[]; self.vbo_data=None; self.tri_count=0
        self._grid=None; self._grid_res=0; self._grid_min=None; self._grid_inv=None
        self._pos_map=None; self._pos_map_size=0

    def build_position_map(self, tex_w, tex_h):
        """Build a texture-pixel → 3D world position map by rasterizing all
        triangles, then dilating outward to fill gaps (like SP's padding).
        _pos_map[py*w+px] = (world_x, world_y, world_z)."""
        _log(f"Building position map {tex_w}x{tex_h} from {self.tri_count} tris…")
        pos_map = {}
        for tri in self.tris:
            v0, v1, v2, uv0, uv1, uv2 = tri
            u0x, u0y = uv0[0]*tex_w, (1-uv0[1])*tex_h
            u1x, u1y = uv1[0]*tex_w, (1-uv1[1])*tex_h
            u2x, u2y = uv2[0]*tex_w, (1-uv2[1])*tex_h
            min_px = max(0, int(min(u0x, u1x, u2x)) - 1)
            max_px = min(tex_w-1, int(max(u0x, u1x, u2x)) + 2)
            min_py = max(0, int(min(u0y, u1y, u2y)) - 1)
            max_py = min(tex_h-1, int(max(u0y, u1y, u2y)) + 2)
            if max_px - min_px > 512 or max_py - min_py > 512:
                continue
            det = (u1y-u2y)*(u0x-u2x) + (u2x-u1x)*(u0y-u2y)
            if abs(det) < 1e-6:
                continue
            inv_det = 1.0 / det
            for py in range(min_py, max_py + 1):
                for px in range(min_px, max_px + 1):
                    w0 = ((u1y-u2y)*(px-u2x) + (u2x-u1x)*(py-u2y)) * inv_det
                    w1 = ((u2y-u0y)*(px-u2x) + (u0x-u2x)*(py-u2y)) * inv_det
                    w2 = 1.0 - w0 - w1
                    if w0 < -0.01 or w1 < -0.01 or w2 < -0.01:
                        continue
                    pos_map[py * tex_w + px] = (
                        w0*v0[0]+w1*v1[0]+w2*v2[0],
                        w0*v0[1]+w1*v1[1]+w2*v2[1],
                        w0*v0[2]+w1*v1[2]+w2*v2[2])

        # Dilation: expand mapped pixels outward to fill triangle-edge gaps.
        # Same concept as SP's "dilation distance" — prevents seam artifacts.
        _DILATE_POS = 8
        current = set(pos_map.keys())
        for _ in range(_DILATE_POS):
            border = set()
            for key in current:
                px_k = key % tex_w
                py_k = key // tex_w
                for ddx, ddy in ((-1,0),(1,0),(0,-1),(0,1)):
                    nx, ny = px_k+ddx, py_k+ddy
                    if 0 <= nx < tex_w and 0 <= ny < tex_h:
                        nk = ny * tex_w + nx
                        if nk not in pos_map:
                            border.add(nk)
            if not border:
                break
            for nk in border:
                nx = nk % tex_w
                ny = nk // tex_w
                for ddx, ddy in ((-1,0),(1,0),(0,-1),(0,1),
                                 (-1,-1),(1,-1),(-1,1),(1,1)):
                    sx, sy = nx+ddx, ny+ddy
                    if 0 <= sx < tex_w and 0 <= sy < tex_h:
                        sk = sy * tex_w + sx
                        if sk in pos_map:
                            pos_map[nk] = pos_map[sk]
                            break
            current = border

        self._pos_map = pos_map
        self._pos_map_size = (tex_w, tex_h)
        _log(f"Position map built: {len(pos_map)} mapped pixels ({_DILATE_POS}px dilation)")

    def build_grid(self, res=32):
        """Build a uniform grid for fast ray-triangle intersection.
        Bins triangles by their AABB projected into the grid."""
        if not self.tris:
            return
        # Find scene AABB (mesh is normalised to unit sphere so ~[-1,1])
        mn = [-1.5, -1.5, -1.5]
        mx = [1.5, 1.5, 1.5]
        inv = [res / (mx[i] - mn[i]) for i in range(3)]
        grid = {}
        for ti, t in enumerate(self.tris):
            v0, v1, v2 = t[0], t[1], t[2]
            # Triangle AABB
            tmin = [min(v0[a], v1[a], v2[a]) for a in range(3)]
            tmax = [max(v0[a], v1[a], v2[a]) for a in range(3)]
            # Grid cell range
            for a in range(3):
                tmin[a] = max(0, int((tmin[a] - mn[a]) * inv[a]))
                tmax[a] = min(res - 1, int((tmax[a] - mn[a]) * inv[a]))
            for gx in range(tmin[0], tmax[0] + 1):
                for gy in range(tmin[1], tmax[1] + 1):
                    for gz in range(tmin[2], tmax[2] + 1):
                        key = (gx, gy, gz)
                        if key not in grid:
                            grid[key] = []
                        grid[key].append(ti)
        self._grid = grid
        self._grid_res = res
        self._grid_min = mn
        self._grid_inv = inv
        _log(f"Spatial grid built: {res}^3, {len(grid)} occupied cells")

    @staticmethod
    def from_file(path):
        """Auto-dispatch to the correct loader based on file extension."""
        ext = os.path.splitext(path)[1].lower()
        if ext == '.fbx':
            return MeshData.from_fbx(path)
        elif ext == '.obj':
            return MeshData.from_obj(path)
        else:
            _log(f"Unsupported mesh format: {ext}", "warning")
            return None

    @staticmethod
    def from_fbx(path):
        """Load mesh from FBX file (binary or ASCII)."""
        result = _parse_fbx_binary(path)
        if result is None:
            _log("Binary FBX parse failed, trying ASCII FBX parser…", "info")
            result = _parse_fbx_ascii(path)
        if result is None:
            return None
        verts, uvs, norms = result
        return MeshData._build(verts, uvs, norms, path)

    @staticmethod
    def from_obj(path):
        import struct as _s
        pl,tl,nl=[],[],[]
        verts=[]   # interleaved: pos(3) uv(2) norm(3)
        tris_rc=[] # for raycasting: (v0,v1,v2,uv0,uv1,uv2)

        def fv(s):
            p=s.split('/'); pi=int(p[0])-1
            ti=int(p[1])-1 if len(p)>1 and p[1] else 0
            ni=int(p[2])-1 if len(p)>2 and p[2] else -1
            return pi,ti,ni
        try:
            with open(path,'r',encoding='utf-8',errors='ignore') as f:
                for line in f:
                    w=line.split()
                    if not w: continue
                    t=w[0]
                    if   t=='v':  pl.append((float(w[1]),float(w[2]),float(w[3])))
                    elif t=='vt': tl.append((float(w[1]),float(w[2]) if len(w)>2 else 0.0))
                    elif t=='vn': nl.append((float(w[1]),float(w[2]),float(w[3])))
                    elif t=='f':
                        fvs=[fv(x) for x in w[1:]]
                        for i in range(1,len(fvs)-1):
                            pts=[fvs[0],fvs[i],fvs[i+1]]
                            vs =[pl[p[0]] for p in pts]
                            uvs=[tl[p[1]] if tl and 0<=p[1]<len(tl) else (0.0,0.0) for p in pts]
                            e1=_v3sub(vs[1],vs[0]); e2=_v3sub(vs[2],vs[0])
                            fn=_v3norm(_v3cross(e1,e2))
                            ns=[nl[p[2]] if p[2]>=0 and nl else fn for p in pts]
                            for vi in range(3):
                                verts+=[vs[vi][0],vs[vi][1],vs[vi][2],
                                        uvs[vi][0],uvs[vi][1],
                                        ns[vi][0],ns[vi][1],ns[vi][2]]
                            tris_rc.append((vs[0],vs[1],vs[2],uvs[0],uvs[1],uvs[2]))
        except Exception as e:
            _log(f"OBJ error: {e}","error"); return None
        if not verts: return None
        return MeshData._build(
            [pl[p[0]] for tri in tris_rc for p in [tri] for _ in range(1)],  # placeholder
            None, None, path,
            _verts_flat=verts, _tris_rc=tris_rc)

    @staticmethod
    def _build(vert_list, uv_list, norm_list, path,
               _verts_flat=None, _tris_rc=None):
        """
        Shared normalise + GPU pack step.
        Two calling modes:
          OBJ: pass _verts_flat (interleaved list) + _tris_rc
          FBX: pass vert_list (list of (x,y,z)), uv_list, norm_list
        """
        import struct as _s

        if _verts_flat is not None:
            # OBJ path — already interleaved
            verts = _verts_flat
            xs=verts[0::8]; ys=verts[1::8]; zs=verts[2::8]
            cx=(max(xs)+min(xs))/2; cy=(max(ys)+min(ys))/2; cz=(max(zs)+min(zs))/2
            r=max(((x-cx)**2+(y-cy)**2+(z-cz)**2)**0.5 for x,y,z in zip(xs,ys,zs)) or 1
            def nc(v,c): return (v-c)/r
            nverts=[]
            for i in range(0,len(verts),8):
                nverts+=[nc(verts[i],cx),nc(verts[i+1],cy),nc(verts[i+2],cz),
                         verts[i+3],verts[i+4],
                         verts[i+5],verts[i+6],verts[i+7]]
            def cnp(p): return ((p[0]-cx)/r,(p[1]-cy)/r,(p[2]-cz)/r)
            ntris=[(cnp(t[0]),cnp(t[1]),cnp(t[2]),t[3],t[4],t[5]) for t in _tris_rc]
        else:
            # FBX path — separate lists, one entry per triangle vertex
            if not vert_list: return None

            # FBX / Unreal / Maya use Z-up; our viewer is Y-up.
            # Detect: if max |Z| span > max |Y| span, assume Z-up → swizzle.
            ys_raw = [p[1] for p in vert_list]
            zs_raw = [p[2] for p in vert_list]
            y_span = max(ys_raw) - min(ys_raw) if ys_raw else 0
            z_span = max(zs_raw) - min(zs_raw) if zs_raw else 0
            z_up = z_span > y_span * 1.2   # heuristic: Z-up if Z range is taller

            def _swiz(p):
                """Swizzle vertex (x,y,z) from Z-up to Y-up if needed."""
                if z_up:
                    return (p[0], p[2], -p[1])   # X, Z→Y, -Y→Z
                return p

            def _swiz_n(n):
                """Swizzle normal."""
                if z_up:
                    return (n[0], n[2], -n[1])
                return n

            vl = [_swiz(p) for p in vert_list]
            xs=[p[0] for p in vl]; ys=[p[1] for p in vl]; zs=[p[2] for p in vl]
            cx=(max(xs)+min(xs))/2; cy=(max(ys)+min(ys))/2; cz=(max(zs)+min(zs))/2
            r=max(((p[0]-cx)**2+(p[1]-cy)**2+(p[2]-cz)**2)**0.5 for p in vl) or 1
            def cnp(p): return ((p[0]-cx)/r,(p[1]-cy)/r,(p[2]-cz)/r)
            uvl  = uv_list   or [(0.0,0.0)]*len(vert_list)
            norl = norm_list or [(0.0,1.0,0.0)]*len(vert_list)
            nverts = []
            ntris  = []
            for i in range(0, len(vert_list)-2, 3):
                v0=cnp(vl[i]); v1=cnp(vl[i+1]); v2=cnp(vl[i+2])
                u0=uvl[i]; u1=uvl[i+1]; u2=uvl[i+2]
                n0=_swiz_n(norl[i]); n1=_swiz_n(norl[i+1]); n2=_swiz_n(norl[i+2])
                for v,u,n in ((v0,u0,n0),(v1,u1,n1),(v2,u2,n2)):
                    nverts+=[v[0],v[1],v[2], u[0],u[1], n[0],n[1],n[2]]
                ntris.append((v0,v1,v2,u0,u1,u2))
            if z_up:
                _log("Mesh: detected Z-up, swizzled to Y-up")

        if not nverts: return None
        md=MeshData()
        md.tris=ntris
        md.tri_count=len(ntris)
        md.vbo_data=_s.pack(f'{len(nverts)}f',*nverts)
        md.build_grid()
        _log(f"Mesh loaded ({os.path.splitext(path)[1]}): {md.tri_count} tris")
        return md


# ─────────────────────────────────────────────────────────────────────────────
# GL helpers — raw calls via ctypes into opengl32 / libGL
# ─────────────────────────────────────────────────────────────────────────────

_GL_COLOR_BUFFER_BIT = 0x4000
_GL_DEPTH_BUFFER_BIT = 0x0100
_GL_DEPTH_TEST       = 0x0B71
_GL_TRIANGLES        = 0x0004
_GL_FLOAT            = 0x1406
_GL_TEXTURE_2D       = 0x0DE1
_GL_RGBA             = 0x1908
_GL_RGBA8            = 0x8058
_GL_UNSIGNED_BYTE    = 0x1401
_GL_LINEAR           = 0x2601
_GL_NEAREST          = 0x2600
_GL_TEXTURE_MIN_F    = 0x2801
_GL_TEXTURE_MAG_F    = 0x2800
_GL_TEXTURE0         = 0x84C0
_GL_ARRAY_BUFFER     = 0x8892
_GL_STATIC_DRAW      = 0x88B4
_GL_VERTEX_SHADER    = 0x8B31
_GL_FRAGMENT_SHADER  = 0x8B30
_GL_COMPILE_STATUS   = 0x8B81
_GL_LINK_STATUS      = 0x8B82


# ─────────────────────────────────────────────────────────────────────────────
# Viewport3D — QOpenGLWindow wrapped in createWindowContainer
# Gives a fully isolated GL context; SP's context is untouched.
# Controls:  Alt+LMB=orbit  Alt+MMB=pan  Alt+RMB or scroll=zoom  (same as SP)
# ─────────────────────────────────────────────────────────────────────────────

class _GL3DWindow(QtGui.QWindow):
    """
    QWindow with its own OpenGL context (isolated from SP's context).
    Renders via raw GL calls — no QOpenGLWidget.
    """

    _VS = b"""#version 130
in vec3 aPos; in vec2 aUV; in vec3 aNorm;
uniform mat4 uMVP;
uniform mat4 uMV;
out vec2 vUV; out vec3 vNormEye;
void main(){
    gl_Position = uMVP * vec4(aPos,1.0);
    vUV  = vec2(aUV.x, 1.0-aUV.y);
    // Transform normal to eye space for camera-relative lighting
    vNormEye = mat3(uMV) * aNorm;
}"""

    _FS = b"""#version 130
in vec2 vUV; in vec3 vNormEye;
uniform sampler2D uTex;
uniform int uHasTex;
out vec4 fColor;
void main(){
    vec3 N = normalize(vNormEye);
    // Light from camera direction (0,0,1 in eye space)
    float d = clamp(dot(N, vec3(0.0, 0.0, 1.0)), 0.0, 1.0) * 0.7 + 0.3;
    vec4 c = uHasTex != 0 ? texture(uTex, vUV) : vec4(0.55, 0.60, 0.65, 1.0);
    fColor = vec4(c.rgb * d, 1.0);
}"""

    def __init__(self, parent_widget):
        super().__init__()
        self._parent_widget = parent_widget
        self.setSurfaceType(QtGui.QWindow.SurfaceType.OpenGLSurface
                            if _QT==6 else QtGui.QWindow.OpenGLSurface)

        fmt = QtGui.QSurfaceFormat()
        fmt.setDepthBufferSize(24)
        fmt.setVersion(3, 0)
        fmt.setProfile(QtGui.QSurfaceFormat.OpenGLContextProfile.CompatibilityProfile
                       if _QT==6 else QtGui.QSurfaceFormat.CompatibilityProfile)
        self.setFormat(fmt)

        self._ctx     = None
        self._ready   = False
        self._prog    = 0
        self._vao     = 0
        self._vbo     = 0
        self._tex_id  = 0
        self._vcount  = 0
        self._gl      = None   # ctypes GL lib

        self._mesh      = None
        self._canvas    = None
        self._tex_dirty = True

        # camera — spherical orbit
        self._yaw   = 25.0
        self._pitch = 18.0
        self._dist  = 2.5
        self._tgt   = [0.0, 0.0, 0.0]

        self._last  = None
        self._mode  = None
        self._orbit_pivot = None    # 3D point to orbit around (smart pivot)
        self._cursor_pos  = None    # (mx, my) logical — for brush cursor
        self._cursor_hit  = None    # (world_x, world_y, world_z) — 3D hit for cursor
        self._cursor_normal = None  # surface normal at cursor hit

    # ── GL context ────────────────────────────────────────────────────────────

    def _ensure_ctx(self):
        if self._ctx is None:
            self._ctx = QtGui.QOpenGLContext()
            self._ctx.setFormat(self.format())
            if not self._ctx.create():
                _log("Failed to create GL context","error"); return False
            self._load_gl()
        return True

    def _load_gl(self):
        """Load the platform OpenGL library via ctypes."""
        import sys, ctypes
        try:
            if sys.platform == 'win32':
                self._gl = ctypes.WinDLL('opengl32')
            elif sys.platform == 'darwin':
                self._gl = ctypes.CDLL('/System/Library/Frameworks/OpenGL.framework/OpenGL')
            else:
                self._gl = ctypes.CDLL('libGL.so.1')
            # Extension loader (needed for shaders, VBOs, VAOs on Windows)
            if sys.platform == 'win32':
                self._wgl_get_proc = ctypes.windll.opengl32.wglGetProcAddress
                self._wgl_get_proc.restype = ctypes.c_void_p
        except Exception as e:
            _log(f"Could not load GL library: {e}", "error")
            self._gl = None

    def _get_proc(self, name):
        """Get a GL extension function pointer."""
        import ctypes
        if hasattr(self, '_wgl_get_proc') and self._wgl_get_proc:
            ptr = self._wgl_get_proc(name.encode())
            if ptr:
                return ctypes.cast(ptr, ctypes.c_void_p)
        return None

    def initialize(self):
        """Called once after context is made current."""
        if not self._gl: return

        # Use PySide's QOpenGLFunctions for portability
        try:
            if _QT == 6:
                from PySide6.QtOpenGL import QOpenGLShaderProgram, QOpenGLShader, QOpenGLBuffer
                from PySide6.QtOpenGL import QOpenGLVertexArrayObject as QVAO
            else:
                from PySide2.QtOpenGL import QOpenGLShaderProgram, QOpenGLShader, QOpenGLBuffer
                from PySide2.QtOpenGL import QOpenGLVertexArrayObject as QVAO

            f = self._ctx.functions()
            f.initializeOpenGLFunctions()
            self._f = f

            f.glEnable(_GL_DEPTH_TEST)
            f.glClearColor(0.10, 0.10, 0.10, 1.0)

            sv = QOpenGLShader.ShaderTypeBit.Vertex   if _QT==6 else QOpenGLShader.Vertex
            sf = QOpenGLShader.ShaderTypeBit.Fragment if _QT==6 else QOpenGLShader.Fragment

            self._prog_obj = QOpenGLShaderProgram()
            self._prog_obj.addShaderFromSourceCode(sv, self._VS.decode())
            self._prog_obj.addShaderFromSourceCode(sf, self._FS.decode())
            # Bind attribute locations BEFORE linking
            self._prog_obj.bindAttributeLocation("aPos",  0)
            self._prog_obj.bindAttributeLocation("aUV",   1)
            self._prog_obj.bindAttributeLocation("aNorm", 2)
            ok = self._prog_obj.link()
            if not ok:
                _log(f"Shader error: {self._prog_obj.log()}", "error"); return
            _log(f"Shader linked OK. aPos={self._prog_obj.attributeLocation('aPos')}"
                 f" aUV={self._prog_obj.attributeLocation('aUV')}"
                 f" aNorm={self._prog_obj.attributeLocation('aNorm')}")

            # VAO — required by OpenGL 3.0+ for draw calls
            self._vao_obj = QVAO()
            if not self._vao_obj.create():
                _log("VAO create failed — draw calls may not work", "warning")

            vbt = QOpenGLBuffer.Type.VertexBuffer if _QT==6 else QOpenGLBuffer.VertexBuffer
            self._vbo_obj = QOpenGLBuffer(vbt)
            self._vbo_obj.create()

            # Allocate texture via QOpenGLTexture or raw GL
            try:
                if _QT == 6:
                    from PySide6.QtOpenGL import QOpenGLTexture
                else:
                    from PySide2.QtOpenGL import QOpenGLTexture
                self._qt_tex = QOpenGLTexture(QOpenGLTexture.Target.Target2D
                                              if _QT == 6 else QOpenGLTexture.Target2D)
                self._qt_tex.create()
                self._tex_id = self._qt_tex.textureId()
                self._qt_tex.setMinMagFilters(
                    QOpenGLTexture.Filter.Linear if _QT == 6 else QOpenGLTexture.Linear,
                    QOpenGLTexture.Filter.Linear if _QT == 6 else QOpenGLTexture.Linear)
                _log(f"Texture created via QOpenGLTexture, id={self._tex_id}")
            except Exception as tex_e:
                _log(f"QOpenGLTexture failed ({tex_e}), using raw GL", "warning")
                import ctypes
                tid = (ctypes.c_uint * 1)(0)
                f.glGenTextures(1, tid)
                self._tex_id = tid[0]
                f.glBindTexture(_GL_TEXTURE_2D, self._tex_id)
                f.glTexParameteri(_GL_TEXTURE_2D, _GL_TEXTURE_MIN_F, _GL_LINEAR)
                f.glTexParameteri(_GL_TEXTURE_2D, _GL_TEXTURE_MAG_F, _GL_LINEAR)

            self._ready = True
            if self._mesh:
                self._upload_mesh()

        except Exception as e:
            _log(f"GL init error: {e}\n{traceback.format_exc()}", "error")

    def load_mesh(self, path):
        md = MeshData.from_file(path)
        if md is None: return False
        self._mesh = md
        if self._ready and self._ctx:
            self._ctx.makeCurrent(self)
            self._upload_mesh()
            self._ctx.doneCurrent()
            self.render()
        # Build position map in background (deferred so UI stays responsive)
        if self._canvas:
            QtCore.QTimer.singleShot(200, self._build_pos_map_deferred)
        return True

    def _build_pos_map_deferred(self):
        """Build the position map after mesh load, using the canvas texture size."""
        if self._mesh and self._canvas:
            img = self._canvas.image()
            self._mesh.build_position_map(img.width(), img.height())

    def _upload_mesh(self):
        if not self._mesh or not self._ready: return
        self._vbo_obj.bind()
        d = self._mesh.vbo_data
        self._vbo_obj.allocate(d, len(d))
        self._vbo_obj.release()
        self._vcount = self._mesh.tri_count * 3
        _log(f"Mesh uploaded to GPU: {self._vcount} vertices")

    def _upload_texture(self):
        if not self._canvas or not self._ready: return
        try:
            img = self._canvas.image()
            fmt_out = QImage.Format.Format_RGBA8888 if _QT == 6 else QImage.Format_RGBA8888
            img = img.convertToFormat(fmt_out)
            w, h = img.width(), img.height()

            self._f.glBindTexture(_GL_TEXTURE_2D, self._tex_id)
            self._f.glTexParameteri(_GL_TEXTURE_2D, _GL_TEXTURE_MIN_F, _GL_LINEAR)
            self._f.glTexParameteri(_GL_TEXTURE_2D, _GL_TEXTURE_MAG_F, _GL_LINEAR)

            # Use ctypes to call glTexImage2D directly — PySide6's wrapper
            # doesn't handle the data pointer correctly for raw pixel bytes.
            import ctypes as _ct
            import sys
            if sys.platform == 'win32':
                _gl_lib = _ct.windll.opengl32
            elif sys.platform == 'darwin':
                _gl_lib = _ct.CDLL('/System/Library/Frameworks/OpenGL.framework/OpenGL')
            else:
                _gl_lib = _ct.CDLL('libGL.so.1')

            glTexImage2D = _gl_lib.glTexImage2D
            glTexImage2D.restype = None
            glTexImage2D.argtypes = [
                _ct.c_uint, _ct.c_int, _ct.c_int,    # target, level, internalformat
                _ct.c_int, _ct.c_int, _ct.c_int,      # width, height, border
                _ct.c_uint, _ct.c_uint, _ct.c_void_p,  # format, type, data
            ]

            # Get raw pointer from QImage
            bits = img.constBits()
            if hasattr(bits, 'tobytes'):
                pixel_bytes = bits.tobytes()
            else:
                pixel_bytes = bytes(bits)
            c_data = (_ct.c_ubyte * len(pixel_bytes)).from_buffer_copy(pixel_bytes)

            glTexImage2D(
                _GL_TEXTURE_2D, 0, _GL_RGBA8,
                w, h, 0,
                _GL_RGBA, _GL_UNSIGNED_BYTE,
                _ct.cast(c_data, _ct.c_void_p),
            )

            if not hasattr(self, '_tex_upload_logged'):
                _log(f"Texture uploaded via ctypes: {w}x{h}, {len(pixel_bytes)} bytes")
                self._tex_upload_logged = True

            self._tex_dirty = False
        except Exception as e:
            _log(f"Texture upload error: {e}\n{traceback.format_exc()}", "error")

    def _build_matrices(self):
        """Return (MVP, MV) as QMatrix4x4 objects."""
        w, h = max(self.width(), 1), max(self.height(), 1)
        yr = _math.radians(self._yaw)
        pr = _math.radians(self._pitch)
        e = _eye(yr, pr, self._dist, self._tgt)
        V = _look_at_mat(e, tuple(self._tgt), (0, 1, 0))
        P = _persp_mat(45.0, w / h, 0.01, 100.0)
        mvp = _mat_mul(P, V)
        if _QT == 6:
            from PySide6.QtGui import QMatrix4x4
        else:
            from PySide2.QtGui import QMatrix4x4

        def _to_qmat(m):
            rm = [0.0] * 16
            for c in range(4):
                for r in range(4):
                    rm[r * 4 + c] = m[c * 4 + r]
            return QMatrix4x4(*rm)

        return _to_qmat(mvp), _to_qmat(V)

    # ── QWindow overrides ─────────────────────────────────────────────────────

    def exposeEvent(self, event):
        if self.isExposed():
            self.render()

    def render(self):
        if not self.isExposed():
            _log("render: not exposed", "warning"); return
        if not self._ensure_ctx():
            _log("render: ctx failed", "warning"); return
        if not self._ctx.makeCurrent(self):
            _log("render: makeCurrent failed", "warning"); return

        if not self._ready:
            self.initialize()

        if not self._ready:
            _log("render: not ready after init", "warning")
            self._ctx.doneCurrent(); return

        if self._tex_dirty:
            self._upload_texture()

        pw, ph = self._physical_size()
        self._f.glViewport(0, 0, pw, ph)
        self._f.glClear(_GL_COLOR_BUFFER_BIT | _GL_DEPTH_BUFFER_BIT)

        if self._vcount > 0:
            # Bind VAO first — required by GL 3.0+
            if self._vao_obj:
                self._vao_obj.bind()

            self._prog_obj.bind()

            mvp, mv = self._build_matrices()
            self._prog_obj.setUniformValue("uMVP", mvp)
            self._prog_obj.setUniformValue("uMV", mv)

            # Use ctypes glUniform1i for int/sampler uniforms —
            # PySide6's setUniformValue(str, int) is unreliable.
            import ctypes as _ct
            import sys as _sys
            if _sys.platform == 'win32':
                _gll = _ct.windll.opengl32
                _get = _gll.wglGetProcAddress
                _get.restype = _ct.c_void_p
                _get.argtypes = [_ct.c_char_p]
                _glUniform1i_ptr = _get(b"glUniform1i")
                if _glUniform1i_ptr:
                    _glUniform1i = _ct.CFUNCTYPE(None, _ct.c_int, _ct.c_int)(_glUniform1i_ptr)
                else:
                    _glUniform1i = None
            else:
                _glUniform1i = getattr(_gll, 'glUniform1i', None)

            has_tex = 1 if (self._canvas is not None and not self._tex_dirty) else 0
            loc_hasTex = self._prog_obj.uniformLocation("uHasTex")
            loc_tex    = self._prog_obj.uniformLocation("uTex")

            if _glUniform1i:
                if loc_hasTex >= 0:
                    _glUniform1i(loc_hasTex, has_tex)
                if loc_tex >= 0:
                    _glUniform1i(loc_tex, 0)
            else:
                self._prog_obj.setUniformValue(loc_hasTex, has_tex)
                self._prog_obj.setUniformValue(loc_tex, 0)

            self._f.glActiveTexture(_GL_TEXTURE0)
            self._f.glBindTexture(_GL_TEXTURE_2D, self._tex_id)

            self._vbo_obj.bind()
            stride = 8 * 4  # 8 floats × 4 bytes

            loc_pos  = self._prog_obj.attributeLocation("aPos")
            loc_uv   = self._prog_obj.attributeLocation("aUV")
            loc_norm = self._prog_obj.attributeLocation("aNorm")

            if not hasattr(self, '_render_logged'):
                _log(f"render: vcount={self._vcount} "
                     f"logical={self.width()}x{self.height()} "
                     f"physical={pw}x{ph} dpr={self._dpr()} "
                     f"has_tex={has_tex}")
                self._render_logged = True

            if loc_pos >= 0:
                self._prog_obj.enableAttributeArray(loc_pos)
                self._prog_obj.setAttributeBuffer(loc_pos, _GL_FLOAT, 0, 3, stride)
            if loc_uv >= 0:
                self._prog_obj.enableAttributeArray(loc_uv)
                self._prog_obj.setAttributeBuffer(loc_uv, _GL_FLOAT, 12, 2, stride)
            if loc_norm >= 0:
                self._prog_obj.enableAttributeArray(loc_norm)
                self._prog_obj.setAttributeBuffer(loc_norm, _GL_FLOAT, 20, 3, stride)

            # Clear any prior errors before draw
            while self._f.glGetError() != 0:
                pass

            self._f.glDrawArrays(_GL_TRIANGLES, 0, self._vcount)

            err = self._f.glGetError()
            if err != 0 and not hasattr(self, '_gl_err_logged'):
                _log(f"render: glGetError after draw={err:#x}", "error")
                self._gl_err_logged = True

            self._vbo_obj.release()
            self._prog_obj.release()
            if self._vao_obj:
                self._vao_obj.release()

        # ── Brush cursor circle ────────────────────────────────────────
        if self._cursor_pos and self._canvas and self._mode != 'orbit':
            self._draw_brush_cursor(pw, ph)

        self._ctx.swapBuffers(self)
        self._ctx.doneCurrent()

    def _draw_brush_cursor(self, pw, ph):
        """Draw a screen-space brush cursor circle at the cursor position."""
        import struct as _s
        if not self._cursor_pos or not self._canvas:
            return
        mx, my = self._cursor_pos
        brush_r = self._canvas.brush_size * 0.5  # screen-pixel radius

        # Convert screen coords to NDC: x: [0,w] → [-1,1], y: [0,h] → [1,-1]
        w, h = max(self.width(), 1), max(self.height(), 1)
        dpr = self._dpr()
        cx_ndc = (mx / w) * 2.0 - 1.0
        cy_ndc = 1.0 - (my / h) * 2.0
        # Brush radius in NDC
        rx_ndc = brush_r / w * 2.0
        ry_ndc = brush_r / h * 2.0

        # Generate circle in NDC
        n_segs = 32
        verts_2d = []
        for i in range(n_segs + 1):
            a = 2.0 * _math.pi * i / n_segs
            ndx = cx_ndc + rx_ndc * _math.cos(a)
            ndy = cy_ndc + ry_ndc * _math.sin(a)
            verts_2d.append((ndx, ndy))

        # Draw cursor circle using GL_LINE_STRIP with identity MVP
        self._f.glDisable(_GL_DEPTH_TEST)

        if self._vao_obj:
            self._vao_obj.bind()
        self._prog_obj.bind()

        if _QT == 6:
            from PySide6.QtGui import QMatrix4x4
        else:
            from PySide2.QtGui import QMatrix4x4
        ident = QMatrix4x4()
        self._prog_obj.setUniformValue("uMVP", ident)
        self._prog_obj.setUniformValue("uMV", ident)

        # Set uHasTex=0 via ctypes
        loc_hasTex = self._prog_obj.uniformLocation("uHasTex")
        if loc_hasTex >= 0:
            import ctypes as _ct
            import sys as _sys2
            _gll = _ct.WinDLL('opengl32') if _sys2.platform == 'win32' else None
            if _gll:
                _get = _gll.wglGetProcAddress; _get.restype = _ct.c_void_p; _get.argtypes = [_ct.c_char_p]
                ptr = _get(b"glUniform1i")
                if ptr:
                    _ct.CFUNCTYPE(None, _ct.c_int, _ct.c_int)(ptr)(loc_hasTex, 0)

        # Build line strip VBO (pos3+uv2+norm3 = 8 floats per vert)
        line_data = []
        for ndx, ndy in verts_2d:
            line_data += [ndx, ndy, 0.0,  0.0, 0.0,  0.0, 0.0, 1.0]

        buf = _s.pack(f'{len(line_data)}f', *line_data)

        # Use a persistent cursor VBO (avoid create/destroy every frame)
        if not hasattr(self, '_cursor_vbo') or self._cursor_vbo is None:
            if _QT == 6:
                from PySide6.QtOpenGL import QOpenGLBuffer
            else:
                from PySide2.QtOpenGL import QOpenGLBuffer
            self._cursor_vbo = QOpenGLBuffer(
                QOpenGLBuffer.Type.VertexBuffer if _QT==6
                else QOpenGLBuffer.VertexBuffer)
            self._cursor_vbo.create()
            self._cursor_vbo.setUsagePattern(
                QOpenGLBuffer.UsagePattern.DynamicDraw if _QT==6
                else QOpenGLBuffer.DynamicDraw)

        self._cursor_vbo.bind()
        self._cursor_vbo.allocate(buf, len(buf))

        stride = 8 * 4
        loc_pos  = self._prog_obj.attributeLocation("aPos")
        loc_uv   = self._prog_obj.attributeLocation("aUV")
        loc_norm = self._prog_obj.attributeLocation("aNorm")
        if loc_pos >= 0:
            self._prog_obj.enableAttributeArray(loc_pos)
            self._prog_obj.setAttributeBuffer(loc_pos, _GL_FLOAT, 0, 3, stride)
        if loc_uv >= 0:
            self._prog_obj.enableAttributeArray(loc_uv)
            self._prog_obj.setAttributeBuffer(loc_uv, _GL_FLOAT, 12, 2, stride)
        if loc_norm >= 0:
            self._prog_obj.enableAttributeArray(loc_norm)
            self._prog_obj.setAttributeBuffer(loc_norm, _GL_FLOAT, 20, 3, stride)

        _GL_LINE_STRIP = 0x0003
        self._f.glDrawArrays(_GL_LINE_STRIP, 0, len(verts_2d))

        self._cursor_vbo.release()
        self._prog_obj.release()
        if self._vao_obj:
            self._vao_obj.release()
        self._f.glEnable(_GL_DEPTH_TEST)

    def resizeEvent(self, event):
        if self._ready and self._ctx.makeCurrent(self):
            pw, ph = self._physical_size()
            self._f.glViewport(0, 0, pw, ph)
            self._ctx.doneCurrent()
        self.render()

    # ── Input — SP-style: Alt+LMB=orbit  Alt+MMB=pan  Alt+RMB/scroll=zoom ────

    def _alt(self, event):
        ALT = Qt.KeyboardModifier.AltModifier if _QT==6 else Qt.AltModifier
        return bool(event.modifiers() & ALT)

    def mousePressEvent(self, event):
        self._last = event.position().toPoint() if _QT==6 else event.pos()
        LMB = Qt.MouseButton.LeftButton   if _QT==6 else Qt.LeftButton
        MMB = Qt.MouseButton.MiddleButton if _QT==6 else Qt.MidButton
        RMB = Qt.MouseButton.RightButton  if _QT==6 else Qt.RightButton
        btn = event.button()
        alt = self._alt(event)
        if   alt and btn==LMB:
            self._mode='orbit'
            # Smart pivot: raycast to find surface point under cursor
            hit = self._raycast_point(self._last.x(), self._last.y())
            if hit is not None:
                self._orbit_pivot = hit
            # If no hit, _orbit_pivot keeps its previous value (or None → orbit around _tgt)
        elif alt and btn==MMB: self._mode='pan'
        elif alt and btn==RMB: self._mode='zoom'
        elif btn==LMB:
            self._mode='paint'
            if self._canvas and self._canvas.tool in (
                    PaintCanvas.TOOL_BRUSH, PaintCanvas.TOOL_ERASER):
                self._canvas._push_undo()
                self._paint_last_screen = None
                self._paint_accum = 0.0
                self._do_paint_stroke(self._last.x(), self._last.y())
            elif self._canvas and self._canvas.tool == PaintCanvas.TOOL_EYEDROP:
                self._do_eyedrop(self._last.x(), self._last.y())
            elif self._canvas and self._canvas.tool == PaintCanvas.TOOL_FILL:
                self._canvas._push_undo()
                self._do_fill(self._last.x(), self._last.y())
        else:
            self._mode=None

    def mouseMoveEvent(self, event):
        cur = event.position().toPoint() if _QT==6 else event.pos()
        if self._last is None: self._last=cur; return
        dx=cur.x()-self._last.x(); dy=cur.y()-self._last.y()
        if self._mode=='orbit':
            dyaw  = -dx * 0.4
            dpitch = -dy * 0.4
            pv = self._orbit_pivot
            if pv is not None:
                # Smart pivot: rotate both eye and _tgt around the pivot point.
                # This keeps the pivot at the same screen position (no jump).
                yr = _math.radians(self._yaw)
                pr = _math.radians(self._pitch)
                old_eye = _eye(yr, pr, self._dist, self._tgt)
                old_tgt = tuple(self._tgt)
                # Camera right vector (for pitch rotation axis)
                fwd = _v3norm(_v3sub(old_tgt, old_eye))
                rgt = _v3norm(_v3cross(fwd, (0, 1, 0)))
                new_eye = _rotate_point_around(old_eye, pv, dyaw, dpitch, rgt)
                new_tgt = _rotate_point_around(old_tgt, pv, dyaw, dpitch, rgt)
                # Back-compute yaw/pitch/dist from the relative vector
                rel = (new_eye[0]-new_tgt[0], new_eye[1]-new_tgt[1], new_eye[2]-new_tgt[2])
                self._dist = max(0.05, (rel[0]**2+rel[1]**2+rel[2]**2)**0.5)
                horiz = (rel[0]**2 + rel[2]**2)**0.5
                self._pitch = _math.degrees(_math.atan2(rel[1], horiz))
                self._yaw = _math.degrees(_math.atan2(rel[0], rel[2]))
                self._tgt = list(new_tgt)
            else:
                # No pivot — simple orbit around _tgt
                self._yaw   += dyaw
                self._pitch += dpitch
            self._last = cur
            self.render()
        elif self._mode=='pan':
            yr=_math.radians(self._yaw); pr=_math.radians(self._pitch)
            e=_eye(yr,pr,self._dist,self._tgt)
            fwd=_v3norm(_v3sub(tuple(self._tgt),e))
            rgt=_v3norm(_v3cross(fwd,(0,1,0)))
            up =_v3norm(_v3cross(rgt,fwd))
            s=self._dist*0.002
            self._tgt[0]-=(rgt[0]*dx-up[0]*dy)*s
            self._tgt[1]-=(rgt[1]*dx-up[1]*dy)*s
            self._tgt[2]-=(rgt[2]*dx-up[2]*dy)*s
            self._last=cur
            self.render()
        elif self._mode=='zoom':
            self._dist=max(0.05,self._dist*(1-dy*0.01))
            self._last=cur
            self.render()
        elif self._mode=='paint':
            if self._canvas and self._canvas.tool in (
                    PaintCanvas.TOOL_BRUSH, PaintCanvas.TOOL_ERASER):
                self._do_paint_stroke(cur.x(), cur.y())
            self._cursor_pos = (cur.x(), cur.y())
            self._last=cur
            self.render()
        else:
            self._cursor_pos = (cur.x(), cur.y())
            self._last=cur
            self.render()

    def _update_cursor(self, mx, my):
        """Update the brush cursor screen position."""
        self._cursor_pos = (mx, my)

    def mouseReleaseEvent(self, event):
        self._mode=None; self._last=None
        self._paint_last_screen = None

    def wheelEvent(self, event):
        delta=event.angleDelta().y() if _QT==6 else event.delta()
        self._dist=max(0.05,self._dist*(0.9 if delta>0 else 1.1))
        self.render()

    # ── Raycast helpers ──────────────────────────────────────────────────────

    def _dpr(self):
        """Device pixel ratio — logical → physical multiplier."""
        d = self.devicePixelRatio() if hasattr(self, 'devicePixelRatio') else 1.0
        return d if d > 0.1 else 1.0

    def _physical_size(self):
        """Framebuffer size in physical pixels (for glViewport)."""
        dpr = self._dpr()
        return max(int(self.width() * dpr), 1), max(int(self.height() * dpr), 1)

    def _screen_to_ray(self, mx, my):
        """Convert screen coords (logical pixels) to world-space ray."""
        w, h = max(self.width(), 1), max(self.height(), 1)
        yr = _math.radians(self._yaw)
        pr = _math.radians(self._pitch)
        e = _eye(yr, pr, self._dist, self._tgt)
        fwd = _v3norm(_v3sub(tuple(self._tgt), e))
        rgt = _v3norm(_v3cross(fwd, (0, 1, 0)))
        up  = _v3norm(_v3cross(rgt, fwd))
        ftan = _math.tan(_math.radians(45.0) * 0.5)
        ar = w / h
        nx = (2.0 * mx / w) - 1.0
        ny = 1.0 - (2.0 * my / h)
        d = _v3norm((rgt[0]*nx*ftan*ar + up[0]*ny*ftan + fwd[0],
                     rgt[1]*nx*ftan*ar + up[1]*ny*ftan + fwd[1],
                     rgt[2]*nx*ftan*ar + up[2]*ny*ftan + fwd[2]))
        return e, d

    def _raycast(self, mx, my):
        """Raycast screen point → closest UV hit. Returns (u,v) or None."""
        hit = self._raycast_full(mx, my)
        return hit['uv'] if hit else None

    def _raycast_full(self, mx, my, backface_cull=True):
        """Raycast screen point → dict with uv, pos, normal, t, uv_density, or None."""
        if not self._mesh:
            return None
        e, d = self._screen_to_ray(mx, my)
        mesh = self._mesh
        tris = mesh.tris
        best_t = 1e18
        best = None

        def _check_tri(tri_data):
            nonlocal best_t, best
            v0, v1, v2 = tri_data[0], tri_data[1], tri_data[2]
            # Backface cull: check if triangle faces camera
            if backface_cull:
                e1c = _v3sub(v1, v0); e2c = _v3sub(v2, v0)
                fn = _v3cross(e1c, e2c)
                # View direction from camera to triangle centroid
                cm = ((v0[0]+v1[0]+v2[0])*0.333333,
                      (v0[1]+v1[1]+v2[1])*0.333333,
                      (v0[2]+v1[2]+v2[2])*0.333333)
                vd = (cm[0]-e[0], cm[1]-e[1], cm[2]-e[2])
                if _v3dot(fn, vd) > 0:
                    return  # backfacing — skip

            hit = _ray_tri(e, d, v0, v1, v2)
            if hit and hit[0] < best_t:
                best_t = hit[0]
                _, bu, bv = hit
                bw = 1 - bu - bv
                uv = (bw*tri_data[3][0] + bu*tri_data[4][0] + bv*tri_data[5][0],
                      bw*tri_data[3][1] + bu*tri_data[4][1] + bv*tri_data[5][1])
                pos = (e[0]+d[0]*hit[0], e[1]+d[1]*hit[0], e[2]+d[2]*hit[0])
                e1 = _v3sub(v1, v0); e2 = _v3sub(v2, v0)
                n = _v3norm(_v3cross(e1, e2))
                # Compute UV density: texels per world unit
                cross_3d = _v3cross(e1, e2)
                area_3d = 0.5 * (cross_3d[0]**2+cross_3d[1]**2+cross_3d[2]**2)**0.5
                uv0, uv1, uv2 = tri_data[3], tri_data[4], tri_data[5]
                area_uv = 0.5 * abs((uv1[0]-uv0[0])*(uv2[1]-uv0[1]) -
                                    (uv2[0]-uv0[0])*(uv1[1]-uv0[1]))
                # UV units per world unit
                uv_per_world = (area_uv / area_3d)**0.5 if area_3d > 1e-12 else 1.0
                best.update({'uv': uv, 'pos': pos, 'normal': n, 't': hit[0],
                             'uv_per_world': uv_per_world})

        best = {}
        if mesh._grid is not None:
            mn, inv_g, res = mesh._grid_min, mesh._grid_inv, mesh._grid_res
            grid = mesh._grid
            tested = set()
            # Adaptive ray march: start near the camera, end well past the mesh
            t_max = max(self._dist * 3 + 4.0, 6.0)
            n_steps = 96
            for step_i in range(n_steps):
                t_s = 0.001 + step_i * t_max / n_steps
                px = e[0]+d[0]*t_s; py = e[1]+d[1]*t_s; pz = e[2]+d[2]*t_s
                gx = int((px-mn[0])*inv_g[0])
                gy = int((py-mn[1])*inv_g[1])
                gz = int((pz-mn[2])*inv_g[2])
                if 0 <= gx < res and 0 <= gy < res and 0 <= gz < res:
                    key = (gx, gy, gz)
                    if key in grid and key not in tested:
                        tested.add(key)
                        for ti in grid[key]:
                            _check_tri(tris[ti])
        else:
            for tri in tris:
                _check_tri(tri)
        return best if best else None

    def _raycast_point(self, mx, my):
        """Raycast screen point → 3D world-space hit position, or None."""
        if not self._mesh:
            return None
        e, d = self._screen_to_ray(mx, my)
        tris = self._mesh.tris
        best_t = 1e18
        # Reuse the same grid/brute-force logic but only need t
        if self._mesh._grid is not None:
            mn = self._mesh._grid_min
            inv = self._mesh._grid_inv
            res = self._mesh._grid_res
            grid = self._mesh._grid
            tested = set()
            t_max = max(self._dist * 3 + 4.0, 6.0)
            n_steps = 96
            for step_i in range(n_steps):
                t_sample = 0.001 + step_i * t_max / n_steps
                px = e[0] + d[0] * t_sample
                py = e[1] + d[1] * t_sample
                pz = e[2] + d[2] * t_sample
                gx = int((px - mn[0]) * inv[0])
                gy = int((py - mn[1]) * inv[1])
                gz = int((pz - mn[2]) * inv[2])
                if 0 <= gx < res and 0 <= gy < res and 0 <= gz < res:
                    key = (gx, gy, gz)
                    if key in grid and key not in tested:
                        tested.add(key)
                        for ti in grid[key]:
                            t = tris[ti]
                            hit = _ray_tri(e, d, t[0], t[1], t[2])
                            if hit and hit[0] < best_t:
                                best_t = hit[0]
        else:
            for t in tris:
                hit = _ray_tri(e, d, t[0], t[1], t[2])
                if hit and hit[0] < best_t:
                    best_t = hit[0]
        if best_t < 1e17:
            return (e[0] + d[0] * best_t,
                    e[1] + d[1] * best_t,
                    e[2] + d[2] * best_t)
        return None

    def _uv_to_pixel(self, uv):
        """Convert UV coords to image pixel coords."""
        img = self._canvas.image()
        ix = int(uv[0] * img.width())  % img.width()
        iy = int((1 - uv[1]) * img.height()) % img.height()
        return QPoint(ix, iy)

    # ── 3D painting ──────────────────────────────────────────────────────────

    def _screen_to_tex_brush_size(self, hit):
        """Convert screen-space brush size to texture-pixel brush size.
        Uses hit depth and local UV density for accurate conversion."""
        canvas = self._canvas
        screen_r = canvas.brush_size * 0.5  # screen pixel radius
        fov_half = _math.radians(45.0) * 0.5
        h = max(self.height(), 1)
        # Screen pixels → world units at the surface depth
        world_r = screen_r * 2.0 * hit['t'] * _math.tan(fov_half) / h
        # World units → UV units → texture pixels
        uv_per_world = hit.get('uv_per_world', 1.0)
        img = canvas.image()
        tex_size = max(img.width(), img.height())
        tex_r = world_r * uv_per_world * tex_size
        # Clamp to reasonable range
        return max(1, int(tex_r * 2))  # return diameter

    def _ensure_pos_map(self):
        """Lazily build the position map when first needed."""
        mesh = self._mesh
        canvas = self._canvas
        if not mesh or not canvas:
            return
        img = canvas.image()
        iw, ih = img.width(), img.height()
        if mesh._pos_map is None or mesh._pos_map_size != (iw, ih):
            mesh.build_position_map(iw, ih)

    def _paint_3d_dab(self, mx, my):
        """Paint one dab: single raycast → compute texture brush size → paint
        a 3D-validated circle (only pixels whose 3D position is near the hit)."""
        if not self._mesh or not self._canvas:
            return False
        hit = self._raycast_full(mx, my, backface_cull=True)
        if not hit:
            return False

        self._ensure_pos_map()

        canvas = self._canvas
        img = canvas.image()
        iw, ih = img.width(), img.height()
        hit_pos = hit['pos']

        # Compute texture brush size from screen brush size + depth + UV density
        tex_brush_size = self._screen_to_tex_brush_size(hit)
        tex_r = max(1, tex_brush_size // 2)

        # UV center pixel
        uv = hit['uv']
        cx = int(uv[0] * iw) % iw
        cy = int((1 - uv[1]) * ih) % ih

        # Compute 3D brush radius for validation
        # Use the world-space radius corresponding to the screen brush size
        fov_half = _math.radians(45.0) * 0.5
        h = max(self.height(), 1)
        screen_r = canvas.brush_size * 0.5
        world_r = screen_r * 2.0 * hit['t'] * _math.tan(fov_half) / h
        world_r_sq = world_r * world_r * 1.5  # slight tolerance

        # Paint with 3D position validation
        pos_map = self._mesh._pos_map or {}
        hardness = canvas.brush_hardness
        base_opacity = canvas.brush_opacity
        is_eraser = canvas.tool == PaintCanvas.TOOL_ERASER
        if not is_eraser:
            bc = canvas.brush_color
            br, bg, bb = bc.red(), bc.green(), bc.blue()

        p = QPainter(img)
        p.setRenderHint(_AA, False)
        if is_eraser:
            p.setCompositionMode(_Clear)
        else:
            p.setCompositionMode(_SrcOver)

        r_sq = tex_r * tex_r
        hp = hit_pos
        painted = False
        for dy in range(-tex_r, tex_r + 1):
            py = (cy + dy) % ih
            for dx in range(-tex_r, tex_r + 1):
                # Circle test in texture space
                d_sq = dx*dx + dy*dy
                if d_sq > r_sq:
                    continue
                px = (cx + dx) % iw

                # 3D position validation — only paint pixels that have a
                # valid 3D position AND are within brush radius in world space
                key = py * iw + px
                pos = pos_map.get(key)
                if pos is None:
                    continue  # pixel not on any triangle — skip
                dist_3d_sq = ((pos[0]-hp[0])**2 +
                              (pos[1]-hp[1])**2 +
                              (pos[2]-hp[2])**2)
                if dist_3d_sq > world_r_sq:
                    continue  # this pixel is on a distant UV island

                # Compute falloff
                t = (d_sq / r_sq) ** 0.5 if r_sq > 0 else 0.0
                if hardness >= 0.99:
                    alpha = base_opacity
                else:
                    if t <= hardness:
                        alpha = base_opacity
                    else:
                        alpha = base_opacity * (1.0 - (t - hardness) / (1.0 - hardness + 1e-6))
                if alpha < 0.004:
                    continue

                ia = int(255 * alpha)
                if is_eraser:
                    p.fillRect(px, py, 1, 1, QColor(0, 0, 0, ia))
                else:
                    p.fillRect(px, py, 1, 1, QColor(br, bg, bb, ia))
                painted = True

        p.end()
        return painted

    def _do_paint_stroke(self, mx, my):
        """Paint along a stroke with proper spacing — raycasts at intervals."""
        if not self._mesh or not self._canvas:
            return

        brush_size = self._canvas.brush_size
        spacing_pct = self._canvas.brush_spacing_pct
        # Spacing in screen pixels — consistent regardless of zoom
        step = max(1.0, brush_size * spacing_pct / 100.0)

        if self._paint_last_screen is None:
            if self._paint_3d_dab(mx, my):
                self._tex_dirty = True
            self._paint_last_screen = (float(mx), float(my))
            self._paint_accum = 0.0
            self.render()
            return

        lx, ly = self._paint_last_screen
        ddx = mx - lx
        ddy = my - ly
        seg_dist = (ddx*ddx + ddy*ddy) ** 0.5
        self._paint_accum += seg_dist

        if self._paint_accum < step:
            self._paint_last_screen = (float(mx), float(my))
            return

        n_dabs = int(self._paint_accum / step)
        n_dabs = min(n_dabs, 16)
        painted = False

        for i in range(n_dabs):
            t = (i + 1) / n_dabs
            sx = lx + ddx * t
            sy = ly + ddy * t
            if self._paint_3d_dab(sx, sy):
                painted = True

        self._paint_accum -= n_dabs * step
        self._paint_last_screen = (float(mx), float(my))

        if painted:
            self._tex_dirty = True
            self.render()

    def _do_eyedrop(self, mx, my):
        """Pick colour from the mesh surface at screen position."""
        uv = self._raycast(mx, my)
        if uv:
            px = self._uv_to_pixel(uv)
            self._canvas._pick_color(px)

    def _do_fill(self, mx, my):
        """Flood-fill on the texture at the UV hit point."""
        uv = self._raycast(mx, my)
        if uv:
            px = self._uv_to_pixel(uv)
            self._canvas._flood_fill(px)
            self._tex_dirty = True
            self.render()


# Wrapper widget that embeds _GL3DWindow via createWindowContainer
class Viewport3D(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._win = _GL3DWindow(self)
        self._ctn = QtWidgets.QWidget.createWindowContainer(self._win, self)
        self._ctn.setMouseTracking(True)
        self._ctn.installEventFilter(self)
        self._ctn.setMinimumSize(100, 100)
        expanding = (QtWidgets.QSizePolicy.Policy.Expanding if _QT == 6
                     else QtWidgets.QSizePolicy.Expanding)
        self._ctn.setSizePolicy(expanding, expanding)

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(1, 1, 1, 1)   # 1px border
        lay.addWidget(self._ctn)
        self.setStyleSheet(
            "Viewport3D { border: 1px solid #555; background: #1a1a1a; }")

        # Overlay label shown before mesh is loaded
        self._overlay = QtWidgets.QLabel(
            "Mesh auto-loading…\nIf nothing appears, try 'Load Mesh…'", self)
        self._overlay.setAlignment(_AlignCenter)
        self._overlay.setStyleSheet(
            "background:rgba(20,20,20,180);color:#666;font-size:11px;"
            "border:none;")
        self._overlay.setGeometry(self.rect())
        self._overlay.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents if _QT == 6
            else Qt.WA_TransparentForMouseEvents)

    def eventFilter(self, obj, event):
        """Forward hover-move from container widget to the GL window for brush cursor."""
        if obj is self._ctn:
            etype = event.type()
            move_type = (QtCore.QEvent.Type.MouseMove if _QT == 6
                         else QtCore.QEvent.MouseMove)
            if etype == move_type:
                pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                self._win._cursor_pos = (pos.x(), pos.y())
                if self._win._ready:
                    self._win.render()
        return super().eventFilter(obj, event)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self._overlay and self._overlay.isVisible():
            self._overlay.setGeometry(self.rect())
        if self._win._ready:
            self._win.render()

    def load_mesh(self, path):
        ok = self._win.load_mesh(path)
        if ok:
            self._overlay.hide()
        return ok

    def attach_canvas(self, canvas):
        self._win._canvas = canvas
        self._win._tex_dirty = True
        canvas.imageChanged.connect(self.mark_dirty)

    def mark_dirty(self):
        self._win._tex_dirty = True
        self._win.render()


class PaintCanvas(QtWidgets.QWidget):

    TOOL_BRUSH   = "brush"
    TOOL_ERASER  = "eraser"
    TOOL_FILL    = "fill"
    TOOL_EYEDROP = "eyedrop"

    colorPicked   = QtCore.Signal(QColor)
    imageChanged  = QtCore.Signal()        # emitted on undo/redo so 3D viewport refreshes

    def __init__(self, image: QImage, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(_CrossCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus if _QT == 6
                            else Qt.StrongFocus)

        self._image      = image.convertToFormat(_ImgFmt)
        self._undo_stack = []   # list of QImage copies
        self._redo_stack = []

        self._zoom        = 1.0
        self._offset      = QPoint(0, 0)
        self._drag_start  = None

        self.tool                = self.TOOL_BRUSH
        self.brush_color         = QColor(255, 255, 255)
        self.brush_size          = 20
        self.brush_opacity       = 1.0
        self.brush_hardness      = 0.8
        self.brush_spacing_pct   = 10    # % of brush diameter between dabs

        # Tablet support
        self._tablet_active      = False
        self._tablet_pressure    = 1.0
        self.tablet_pressure_size    = True   # pressure → size
        self.tablet_pressure_opacity = True   # pressure → opacity

        self._drawing       = False
        self._last_pos      = None   # last painted position (for spacing)
        self._cursor_pos    = None   # current mouse position (for cursor circle)
        self._dist_accum    = 0.0    # accumulated distance for spacing

        # Enable tablet events
        self.setAttribute(Qt.WidgetAttribute.WA_TabletTracking if _QT == 6
                          else Qt.WA_TabletTracking, True)

        self.setMinimumSize(400, 400)

    # ── Image access ──────────────────────────────────────────────────────────

    def image(self):
        return self._image

    def set_image(self, img: QImage):
        """Replace the canvas image (used for UDIM tile switching)."""
        self._image = img.convertToFormat(_ImgFmt)
        self._undo_stack.clear()
        self._redo_stack.clear()
        self.fit_to_view()
        self.imageChanged.emit()

    # ── Undo / Redo ───────────────────────────────────────────────────────────

    def _push_undo(self):
        self._undo_stack.append(self._image.copy())
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self):
        if not self._undo_stack:
            return
        self._redo_stack.append(self._image.copy())
        self._image = self._undo_stack.pop()
        self.update()
        self.imageChanged.emit()

    def redo(self):
        if not self._redo_stack:
            return
        self._undo_stack.append(self._image.copy())
        self._image = self._redo_stack.pop()
        self.update()
        self.imageChanged.emit()

    # ── View ──────────────────────────────────────────────────────────────────

    def fit_to_view(self):
        w, h = self.width(), self.height()
        iw, ih = self._image.width(), self._image.height()
        if w < 1 or h < 1 or iw < 1 or ih < 1:
            return
        self._zoom = min(w / iw, h / ih) * 0.95
        self._center_image()
        self.update()

    def _center_image(self):
        iw = int(self._image.width()  * self._zoom)
        ih = int(self._image.height() * self._zoom)
        self._offset = QPoint((self.width() - iw) // 2,
                               (self.height() - ih) // 2)

    def _widget_to_image(self, pos):
        x = (pos.x() - self._offset.x()) / self._zoom
        y = (pos.y() - self._offset.y()) / self._zoom
        return QPoint(int(x), int(y))

    def resizeEvent(self, event):
        self.fit_to_view()

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(_AA)

        # Checker background
        cs = 12
        for cx in range(0, self.width(), cs):
            for cy in range(0, self.height(), cs):
                col = QColor(80, 80, 80) if (cx // cs + cy // cs) % 2 == 0 \
                      else QColor(60, 60, 60)
                p.fillRect(cx, cy, cs, cs, col)

        iw = int(self._image.width()  * self._zoom)
        ih = int(self._image.height() * self._zoom)
        dest = QRect(self._offset.x(), self._offset.y(), iw, ih)
        p.drawPixmap(dest, QPixmap.fromImage(self._image))

        p.setPen(QPen(QColor(180, 180, 180, 100), 1))
        p.drawRect(dest)

        # Brush cursor
        if self.tool in (self.TOOL_BRUSH, self.TOOL_ERASER) and self._cursor_pos:
            r = max(2, int(self.brush_size * self._zoom / 2))
            pen_col = QColor(255, 255, 255, 180) if self.tool == self.TOOL_ERASER \
                      else QColor(0, 0, 0, 200)
            p.setPen(QPen(pen_col, 1))
            p.setBrush(_NoBrush if _QT == 6 else Qt.NoBrush)
            p.drawEllipse(self._cursor_pos, r, r)

    def wheelEvent(self, event):
        delta = event.angleDelta().y() if _QT == 6 else event.delta()
        factor = 1.15 if delta > 0 else 1 / 1.15
        pos = event.position().toPoint() if _QT == 6 else event.pos()
        old = self._zoom
        self._zoom = max(0.05, min(32.0, self._zoom * factor))
        ratio = self._zoom / old
        self._offset = QPoint(
            int(pos.x() - ratio * (pos.x() - self._offset.x())),
            int(pos.y() - ratio * (pos.y() - self._offset.y())),
        )
        self.update()

    def keyPressEvent(self, event):
        k = event.key()
        ctrl  = bool(event.modifiers() & _CtrlMod)
        shift = bool(event.modifiers() & _ShiftMod)
        if k == _Key_Z:
            if ctrl and shift: self.redo()
            elif ctrl:         self.undo()
        event.accept()

    def mousePressEvent(self, event):
        if self._tablet_active:
            event.accept()
            return  # tablet events handled in tabletEvent
        if event.button() == _MMB:
            self._drag_start = event.pos()
            self.setCursor(_ClosedHandCursor)
            return
        if event.button() != _LMB:
            return

        ip = self._widget_to_image(event.pos())

        if self.tool == self.TOOL_EYEDROP:
            self._pick_color(ip)
            return

        if self.tool == self.TOOL_FILL:
            self._push_undo()
            self._flood_fill(ip)
            self.update()
            return

        self._push_undo()
        self._drawing    = True
        self._dist_accum = 0.0
        self._last_pos   = event.pos()   # spacing anchor
        self._cursor_pos = event.pos()
        self._paint_dot_pressure(ip)
        self.update()

    def tabletEvent(self, event):
        """Handle Wacom/tablet events for pressure sensitivity."""
        if _QT == 6:
            from PySide6.QtGui import QTabletEvent
            etype = event.type()
            Press   = QTabletEvent.Type.TabletPress
            Move    = QTabletEvent.Type.TabletMove
            Release = QTabletEvent.Type.TabletRelease
        else:
            from PySide2.QtCore import QEvent
            Press   = QEvent.TabletPress
            Move    = QEvent.TabletMove
            Release = QEvent.TabletRelease

        self._tablet_active   = True
        self._tablet_pressure = event.pressure()

        pos = event.position().toPoint() if _QT == 6 else event.pos()

        if event.type() == Press:
            self._tablet_active = True
            ip = self._widget_to_image(pos)
            if self.tool == self.TOOL_EYEDROP:
                self._pick_color(ip)
            elif self.tool == self.TOOL_FILL:
                self._push_undo()
                self._flood_fill(ip)
                self.update()
            else:
                self._push_undo()
                self._drawing    = True
                self._dist_accum = 0.0
                self._last_pos   = pos   # anchor for spacing
                self._cursor_pos = pos
                self._paint_dot_pressure(ip)
            self.update()

        elif event.type() == Move:
            self._cursor_pos = pos
            if self._drawing:
                self._paint_with_spacing(pos)
            self.update()

        elif event.type() == Release:
            self._drawing       = False
            self._tablet_active = False

        event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_start is not None:
            self._offset += event.pos() - self._drag_start
            self._drag_start = event.pos()
            self.update()
            return
        # NOTE: do NOT set self._last_pos here — _paint_with_spacing owns it.
        # Only update it for the cursor-circle repaint (separate variable would be
        # cleaner, but we reuse _last_pos for the visual cursor too).
        # We store a separate _cursor_pos for the cursor and leave _last_pos for spacing.
        self._cursor_pos = event.pos()
        if self._drawing and not self._tablet_active:
            self._paint_with_spacing(event.pos())
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == _MMB:
            self._drag_start = None
            self.setCursor(_CrossCursor)
        if event.button() == _LMB:
            self._drawing = False

    # ── Primitives ────────────────────────────────────────────────────────────

    def _paint_dot(self, ip: QPoint):
        p = QPainter(self._image)
        p.setRenderHint(_AA)
        r = max(1, self.brush_size // 2)

        if self.tool == self.TOOL_ERASER:
            p.setCompositionMode(_Clear)
            color = QColor(0, 0, 0, int(255 * self.brush_opacity))
        else:
            p.setCompositionMode(_SrcOver)
            color = QColor(self.brush_color.red(),
                           self.brush_color.green(),
                           self.brush_color.blue(),
                           int(255 * self.brush_opacity))

        if self.brush_hardness >= 0.99:
            p.setPen(_NoPen)
            p.setBrush(QBrush(color))
            p.drawEllipse(ip, r, r)
        else:
            g = QRadialGradient(QPointF(ip.x(), ip.y()), float(r))
            alpha_core = int(255 * self.brush_opacity)
            if self.tool == self.TOOL_ERASER:
                g.setColorAt(0.0,                  QColor(0, 0, 0, alpha_core))
                g.setColorAt(self.brush_hardness,  QColor(0, 0, 0, alpha_core))
                g.setColorAt(1.0,                  QColor(0, 0, 0, 0))
            else:
                c = self.brush_color
                g.setColorAt(0.0,                  QColor(c.red(), c.green(), c.blue(), alpha_core))
                g.setColorAt(self.brush_hardness,  QColor(c.red(), c.green(), c.blue(), alpha_core))
                g.setColorAt(1.0,                  QColor(c.red(), c.green(), c.blue(), 0))
            p.setPen(_NoPen)
            p.setBrush(QBrush(g))
            p.drawEllipse(ip, r, r)
        p.end()

    def _flood_fill(self, pos: QPoint):
        w, h = self._image.width(), self._image.height()
        if not (0 <= pos.x() < w and 0 <= pos.y() < h):
            return
        target = self._image.pixel(pos.x(), pos.y())
        fill   = QColor(self.brush_color.red(),
                        self.brush_color.green(),
                        self.brush_color.blue(),
                        int(255 * self.brush_opacity))
        if target == fill.rgba():
            return
        p = QPainter(self._image)
        stack   = [(pos.x(), pos.y())]
        visited = {(pos.x(), pos.y())}
        while stack:
            cx, cy = stack.pop()
            if self._image.pixel(cx, cy) != target:
                continue
            lx, rx = cx, cx
            while lx > 0     and self._image.pixel(lx-1, cy) == target: lx -= 1
            while rx < w - 1 and self._image.pixel(rx+1, cy) == target: rx += 1
            p.fillRect(lx, cy, rx - lx + 1, 1, fill)
            for nx in range(lx, rx + 1):
                for ny in (cy - 1, cy + 1):
                    if 0 <= ny < h and (nx, ny) not in visited:
                        if self._image.pixel(nx, ny) == target:
                            stack.append((nx, ny))
                            visited.add((nx, ny))
        p.end()

    def _paint_with_spacing(self, widget_pos: QPoint):
        """Paint dabs along the stroke respecting brush_spacing_pct."""
        if self._last_pos is None:
            self._last_pos = widget_pos
            return

        # Distance in widget pixels
        dx = widget_pos.x() - self._last_pos.x()
        dy = widget_pos.y() - self._last_pos.y()
        dist = (dx * dx + dy * dy) ** 0.5

        # Spacing threshold in widget pixels (brush diameter × spacing%)
        step = max(1.0, self.brush_size * self._zoom * self.brush_spacing_pct / 100.0)

        self._dist_accum += dist
        steps = int(self._dist_accum / step)
        if steps == 0:
            return

        # Interpolate dab positions along the segment
        total_dist = max(dist, 1e-6)
        for i in range(steps):
            t = ((self._dist_accum - steps * step + (i + 1) * step) / total_dist)
            t = max(0.0, min(1.0, t))
            wx = int(self._last_pos.x() + dx * t)
            wy = int(self._last_pos.y() + dy * t)
            ip = self._widget_to_image(QPoint(wx, wy))
            self._paint_dot_pressure(ip)

        self._dist_accum -= steps * step
        self._last_pos = widget_pos

    def _paint_dot_pressure(self, ip: QPoint):
        """Paint one dab, scaling size/opacity by tablet pressure if active."""
        base_size    = self.brush_size
        base_opacity = self.brush_opacity
        p = self._tablet_pressure  # 0.0–1.0, always 1.0 for mouse

        # Apply pressure curves
        size_mul    = (0.3 + 0.7 * p) if (self._tablet_active and self.tablet_pressure_size)    else 1.0
        opacity_mul = (p ** 0.7)       if (self._tablet_active and self.tablet_pressure_opacity) else 1.0

        # Temporarily patch then restore
        self.brush_size    = max(1, int(base_size    * size_mul))
        self.brush_opacity = max(0.01, base_opacity  * opacity_mul)
        self._paint_dot(ip)
        self.brush_size    = base_size
        self.brush_opacity = base_opacity

    def _paint_dot_at(self, ip: QPoint, radius: int, falloff: float = 1.0):
        """Paint a small dab at ip with given radius and opacity falloff (0-1)."""
        p = QPainter(self._image)
        p.setRenderHint(_AA)
        r = max(1, radius)
        opacity = self.brush_opacity * falloff

        if self.tool == self.TOOL_ERASER:
            p.setCompositionMode(_Clear)
            color = QColor(0, 0, 0, int(255 * opacity))
        else:
            p.setCompositionMode(_SrcOver)
            color = QColor(self.brush_color.red(),
                           self.brush_color.green(),
                           self.brush_color.blue(),
                           int(255 * opacity))

        if self.brush_hardness >= 0.99:
            p.setPen(_NoPen)
            p.setBrush(QBrush(color))
            p.drawEllipse(ip, r, r)
        else:
            g = QRadialGradient(QPointF(ip.x(), ip.y()), float(r))
            alpha = int(255 * opacity)
            if self.tool == self.TOOL_ERASER:
                g.setColorAt(0.0, QColor(0, 0, 0, alpha))
                g.setColorAt(self.brush_hardness, QColor(0, 0, 0, alpha))
                g.setColorAt(1.0, QColor(0, 0, 0, 0))
            else:
                c = self.brush_color
                g.setColorAt(0.0, QColor(c.red(), c.green(), c.blue(), alpha))
                g.setColorAt(self.brush_hardness, QColor(c.red(), c.green(), c.blue(), alpha))
                g.setColorAt(1.0, QColor(c.red(), c.green(), c.blue(), 0))
            p.setPen(_NoPen)
            p.setBrush(QBrush(g))
            p.drawEllipse(ip, r, r)
        p.end()

    def _pick_color(self, ip: QPoint):
        if 0 <= ip.x() < self._image.width() and 0 <= ip.y() < self._image.height():
            self.colorPicked.emit(QColor(self._image.pixel(ip.x(), ip.y())))


# ─────────────────────────────────────────────────────────────────────────────
# Colour swatch button
# ─────────────────────────────────────────────────────────────────────────────

class ColorSwatch(QtWidgets.QPushButton):
    colorChanged = QtCore.Signal(QColor)

    def __init__(self, color=None, parent=None):
        super().__init__(parent)
        self._color = color or QColor(255, 255, 255)
        self.setFixedSize(34, 34)
        self.setToolTip("Brush colour — click to change")
        self.clicked.connect(self._pick)
        self._update_style()

    def color(self): return self._color

    def set_color(self, c: QColor):
        self._color = c
        self._update_style()
        self.colorChanged.emit(c)

    def _update_style(self):
        self.setStyleSheet(
            f"background:{self._color.name()}; border:2px solid #888; border-radius:4px;"
        )

    def _pick(self):
        c = QtWidgets.QColorDialog.getColor(self._color, self, "Brush Colour", _ShowAlpha)
        if c.isValid():
            self.set_color(c)


# ─────────────────────────────────────────────────────────────────────────────
# Paint Window
# ─────────────────────────────────────────────────────────────────────────────

class PaintWindow(QtWidgets.QDialog):

    def __init__(self, texture_set, usage, image_path, parent=None,
                 udim_tiles=None):
        """
        Parameters
        ----------
        udim_tiles : list[(int, str)] or None
            For UDIM texture sets, a sorted list of (tile_id, file_path)
            tuples. When provided, the window shows a tile selector combo.
        """
        super().__init__(parent)
        self._ts          = texture_set
        self._usage       = usage
        self._source_path = image_path
        self._map_label   = MESH_MAP_INFO[usage][0]

        # UDIM state
        self._udim_tiles      = udim_tiles or []
        self._tile_images     = {}   # tile_id → QImage (lazily loaded)
        self._current_tile_id = None

        self.setWindowTitle(
            f"Paint Baked Map  ·  {self._map_label}  [{texture_set.name()}]"
        )
        self.resize(1120, 780)
        self.setModal(False)

        if self._udim_tiles:
            # Load the first tile
            self._current_tile_id = self._udim_tiles[0][0]
            img = self._load_tile_image(self._udim_tiles[0][1])
        else:
            img = self._load_image_file(image_path)

        if img is None or img.isNull():
            raise RuntimeError(f"Could not load image: {image_path}")

        self._build_ui(img)

    @staticmethod
    def _load_image_file(path):
        """Load a QImage from path with Pillow fallback."""
        img = QImage(path)
        if img.isNull():
            try:
                from PIL import Image as PilImage
                import io
                pil_img = PilImage.open(path).convert("RGBA")
                buf = io.BytesIO()
                pil_img.save(buf, "PNG")
                buf.seek(0)
                img.loadFromData(buf.read())
            except Exception:
                pass
        return img

    def _load_tile_image(self, path):
        """Load a tile image, caching it in _tile_images."""
        img = self._load_image_file(path)
        if img and not img.isNull():
            # Find tile_id from path
            for tid, tpath in self._udim_tiles:
                if tpath == path:
                    self._tile_images[tid] = img
                    break
        return img

    def _build_ui(self, img: QImage):
        root = QtWidgets.QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── LEFT TOOLBAR ──────────────────────────────────────────────────────
        tb = QtWidgets.QWidget()
        tb.setFixedWidth(64)
        tb.setStyleSheet("background:#252525; border-right:1px solid #333;")
        tl = QtWidgets.QVBoxLayout(tb)
        tl.setContentsMargins(4, 10, 4, 10)
        tl.setSpacing(4)

        btn_style_active   = ("QPushButton{background:#3a5a7a;color:white;"
                               "border:1px solid #5a8aba; border-radius:4px; font-size:15px;}"
                               "QPushButton:hover{background:#4a6a8a;}")
        btn_style_inactive = ("QPushButton{background:#333;color:#aaa;"
                               "border:1px solid #444; border-radius:4px; font-size:15px;}"
                               "QPushButton:hover{background:#444;}")

        self._tool_btns = {}
        for tool_id, icon, tip in [
            (PaintCanvas.TOOL_BRUSH,   "✏",  "Brush  (B)"),
            (PaintCanvas.TOOL_ERASER,  "⌫",  "Eraser  (E)"),
            (PaintCanvas.TOOL_FILL,    "🪣",  "Fill bucket  (F)"),
            (PaintCanvas.TOOL_EYEDROP, "🔎",  "Eyedropper — pick colour  (I)"),
        ]:
            btn = QtWidgets.QPushButton(icon)
            btn.setFixedSize(42, 42)
            btn.setCheckable(True)
            btn.setToolTip(tip)
            btn.setStyleSheet(btn_style_inactive)
            btn.clicked.connect(lambda *_, t=tool_id: self._set_tool(t))
            tl.addWidget(btn)
            self._tool_btns[tool_id] = btn

        tl.addSpacing(10)

        for icon, tip, slot in [("↩", "Undo  Ctrl+Z",         lambda *_: self._canvas.undo()),
                                  ("↪", "Redo  Ctrl+Shift+Z",  lambda *_: self._canvas.redo()),
                                  ("⊞", "Fit image  (Home)",   lambda *_: self._canvas.fit_to_view())]:
            btn = QtWidgets.QPushButton(icon)
            btn.setFixedSize(42, 42)
            btn.setToolTip(tip)
            btn.setStyleSheet(btn_style_inactive)
            btn.clicked.connect(slot)
            tl.addWidget(btn)

        tl.addStretch()

        # Resolution label
        res_lbl = QtWidgets.QLabel(f"{img.width()}\n×\n{img.height()}")
        res_lbl.setAlignment(_AlignCenter)
        res_lbl.setStyleSheet("color:#555; font-size:9px;")
        tl.addWidget(res_lbl)

        root.addWidget(tb)

        # ── CENTRE ────────────────────────────────────────────────────────────
        centre = QtWidgets.QWidget()
        cl = QtWidgets.QVBoxLayout(centre)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        # Info bar (with 2D/3D toggle on the right)
        color = MESH_MAP_INFO[self._usage][1]
        info_bar = QtWidgets.QWidget()
        info_bar.setStyleSheet("background:#1a1a1a;")
        ib_lay = QtWidgets.QHBoxLayout(info_bar)
        ib_lay.setContentsMargins(6, 2, 6, 2)
        ib_lay.setSpacing(0)

        info_lbl = QtWidgets.QLabel(
            f"<span style='color:{color}; font-weight:bold;'>{self._map_label}</span>"
            f"  ·  {self._ts.name()}"
            f"  ·  {img.width()} × {img.height()} px"
            f"  ·  Scroll=zoom  ·  Middle/Alt-drag=pan"
        )
        info_lbl.setStyleSheet("color:#777; font-size:10px;")
        ib_lay.addWidget(info_lbl, 1)

        # UDIM tile selector
        self._udim_combo = None
        if self._udim_tiles:
            udim_lbl = QtWidgets.QLabel("Tile:")
            udim_lbl.setStyleSheet("color:#888; font-size:10px;")
            ib_lay.addWidget(udim_lbl)
            ib_lay.addSpacing(4)
            self._udim_combo = QtWidgets.QComboBox()
            self._udim_combo.setStyleSheet(
                "QComboBox{background:#2a2a2a; color:#ccc; border:1px solid #3a3a3a;"
                "padding:1px 4px; font-size:10px; min-width:60px;}")
            for tid, _ in self._udim_tiles:
                self._udim_combo.addItem(str(tid), userData=tid)
            self._udim_combo.currentIndexChanged.connect(self._on_tile_changed)
            ib_lay.addWidget(self._udim_combo)
            ib_lay.addSpacing(8)

        # 2D / 3D toggle
        self._btn_2d = QtWidgets.QPushButton("2D")
        self._btn_3d = QtWidgets.QPushButton("3D")
        for btn, active in ((self._btn_2d, True), (self._btn_3d, False)):
            btn.setFixedSize(36, 22)
            btn.setCheckable(True)
            btn.setChecked(active)
            btn.setStyleSheet(
                "QPushButton{background:#333;color:#777;border:1px solid #555;"
                "border-radius:3px;font-size:10px;font-weight:bold;}"
                "QPushButton:checked{background:#3a5a7a;color:white;border:1px solid #5a8aba;}"
                "QPushButton:hover{background:#444;}"
            )
        ib_lay.addWidget(self._btn_2d)
        ib_lay.addSpacing(2)
        ib_lay.addWidget(self._btn_3d)

        self._btn_2d.clicked.connect(lambda *_: self._switch_view(False))
        self._btn_3d.clicked.connect(lambda *_: self._switch_view(True))

        # Load mesh button (hidden by default, shown in 3D mode)
        self._btn_load_mesh = QtWidgets.QPushButton("Load Mesh…")
        self._btn_load_mesh.setFixedHeight(22)
        self._btn_load_mesh.setVisible(False)
        self._btn_load_mesh.setStyleSheet(
            "QPushButton{background:#2a4a2a;color:#8c8;border:1px solid #4a7a4a;"
            "border-radius:3px;font-size:10px;padding:0 8px;}"
            "QPushButton:hover{background:#3a6a3a;}"
        )
        self._btn_load_mesh.clicked.connect(lambda *_: self._load_mesh())
        ib_lay.addSpacing(6)
        ib_lay.addWidget(self._btn_load_mesh)

        cl.addWidget(info_bar)

        # Stacked widget — index 0 = 2D canvas, index 1 = 3D viewport placeholder
        # Viewport3D is created lazily on first switch to avoid GL context conflicts
        self._stack = QtWidgets.QStackedWidget()
        self._viewport3d = None   # created on demand

        self._canvas = PaintCanvas(img)
        self._canvas.colorPicked.connect(self._on_color_picked)
        self._stack.addWidget(self._canvas)   # index 0

        # Placeholder shown before the 3D viewport is initialised
        self._placeholder_3d = QtWidgets.QLabel(
            "Click 'Load Mesh…' to load an OBJ and activate the 3D viewport"
        )
        self._placeholder_3d.setAlignment(_AlignCenter)
        self._placeholder_3d.setStyleSheet("background:#1a1a1a; color:#666; font-size:12px;")
        self._stack.addWidget(self._placeholder_3d)   # index 1

        self._stack.setCurrentIndex(0)
        cl.addWidget(self._stack, 1)

        # ── BOTTOM BAR ────────────────────────────────────────────────────────
        bb = QtWidgets.QWidget()
        bb.setStyleSheet("background:#252525; border-top:1px solid #333;")
        bl = QtWidgets.QHBoxLayout(bb)
        bl.setContentsMargins(10, 6, 10, 6)
        bl.setSpacing(10)

        # Colour swatch
        self._swatch = ColorSwatch(QColor(255, 255, 255))
        self._swatch.colorChanged.connect(self._on_swatch_changed)
        bl.addWidget(self._swatch)

        # Quick grey-value slider (very useful for AO/Height/Curvature)
        bl.addWidget(self._lbl("Value"))
        self._sld_value = self._slider(0, 255, 255, 90)
        self._sld_value.setToolTip(
            "Quick greyscale value — handy for AO, Height, Curvature maps"
        )
        self._sld_value.valueChanged.connect(self._on_value_changed)
        bl.addWidget(self._sld_value)

        bl.addWidget(self._vsep())

        # Brush size
        bl.addWidget(self._lbl("Size"))
        self._sld_size = self._slider(1, 400, 20, 110)
        self._lbl_size = self._lbl("20px", w=36)
        self._sld_size.valueChanged.connect(lambda v: (
            setattr(self._canvas, "brush_size", v),
            self._lbl_size.setText(f"{v}px")
        ))
        bl.addWidget(self._sld_size)
        bl.addWidget(self._lbl_size)

        bl.addWidget(self._vsep())

        # Opacity
        bl.addWidget(self._lbl("Opacity"))
        self._sld_opacity = self._slider(1, 100, 100, 90)
        self._lbl_opacity = self._lbl("100%", w=36)
        self._sld_opacity.valueChanged.connect(lambda v: (
            setattr(self._canvas, "brush_opacity", v / 100.0),
            self._lbl_opacity.setText(f"{v}%")
        ))
        bl.addWidget(self._sld_opacity)
        bl.addWidget(self._lbl_opacity)

        bl.addWidget(self._vsep())

        # Hardness
        bl.addWidget(self._lbl("Hardness"))
        self._sld_hard = self._slider(0, 100, 80, 90)
        self._lbl_hard = self._lbl("80%", w=36)
        self._sld_hard.valueChanged.connect(lambda v: (
            setattr(self._canvas, "brush_hardness", v / 100.0),
            self._lbl_hard.setText(f"{v}%")
        ))
        bl.addWidget(self._sld_hard)
        bl.addWidget(self._lbl_hard)

        bl.addWidget(self._vsep())

        # Spacing
        bl.addWidget(self._lbl("Spacing"))
        self._sld_spacing = self._slider(1, 200, 10, 80)
        self._lbl_spacing = self._lbl("10%", w=36)
        self._sld_spacing.setToolTip(
            "Distance between brush dabs as % of brush size\n"
            "Low = smooth stroke, High = separated dabs"
        )
        self._sld_spacing.valueChanged.connect(lambda v: (
            setattr(self._canvas, "brush_spacing_pct", v),
            self._lbl_spacing.setText(f"{v}%")
        ))
        bl.addWidget(self._sld_spacing)
        bl.addWidget(self._lbl_spacing)

        bl.addStretch()

        # Apply / Cancel
        self._btn_apply = QtWidgets.QPushButton("  ✔  Apply to SP  ")
        self._btn_apply.setStyleSheet(
            "QPushButton{background:#2d7a3a;color:white;font-weight:bold;"
            "padding:6px 16px; border-radius:4px;}"
            "QPushButton:hover{background:#3a9a4a;}"
            "QPushButton:disabled{background:#1a4a22; color:#555;}"
        )
        self._btn_apply.setToolTip("Save edits and re-import map into Substance Painter")
        self._btn_apply.clicked.connect(self._apply)
        bl.addWidget(self._btn_apply)

        btn_cancel = QtWidgets.QPushButton("  ✖  Cancel  ")
        btn_cancel.setStyleSheet(
            "QPushButton{background:#5a2222;color:white;padding:6px 14px; border-radius:4px;}"
            "QPushButton:hover{background:#7a2929;}"
        )
        btn_cancel.clicked.connect(self.reject)
        bl.addWidget(btn_cancel)

        cl.addWidget(bb)
        root.addWidget(centre, 1)

        # Activate default tool
        self._set_tool(PaintCanvas.TOOL_BRUSH)

        # Install window-wide shortcuts (work regardless of focused child widget)
        self._setup_shortcuts()

    # ── Widget factories ──────────────────────────────────────────────────────

    @staticmethod
    def _lbl(text, w=None):
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet("color:#888; font-size:10px;")
        if w:
            lbl.setFixedWidth(w)
        return lbl

    @staticmethod
    def _slider(lo, hi, val, width):
        s = QtWidgets.QSlider(_HorizSlider)
        s.setRange(lo, hi)
        s.setValue(val)
        s.setFixedWidth(width)
        return s

    @staticmethod
    def _vsep():
        sep = QtWidgets.QFrame()
        sep.setFrameShape(_VLine)
        sep.setFrameShadow(_Sunken)
        sep.setStyleSheet("color:#444;")
        return sep

    # ── Slots ─────────────────────────────────────────────────────────────────

    # ── 2D / 3D switching ────────────────────────────────────────────────────

    def _switch_view(self, to_3d: bool):
        if not to_3d:
            self._btn_2d.setChecked(True)
            self._btn_3d.setChecked(False)
            self._stack.setCurrentIndex(0)
            self._canvas.update()
            return

        # ── 3D Paint Mode: use SP's native painting tools ──
        try:
            label = self._map_label.replace(" ", "_")
            safe_ts = "".join(c if c.isalnum() or c in "-_." else "_"
                              for c in self._ts.name())

            if self._udim_tiles:
                # Save current canvas back to tile cache
                if self._current_tile_id is not None:
                    self._tile_images[self._current_tile_id] = self._canvas.image().copy()
                # Save all tiles with UDIM naming for 3D mode
                stem = f"{safe_ts}_{label}_for3d"
                for tid, orig_path in self._udim_tiles:
                    tile_path = os.path.join(_work_dir(), f"{stem}_{tid}.png")
                    if tid in self._tile_images:
                        self._tile_images[tid].save(tile_path, "PNG")
                    else:
                        shutil.copy2(orig_path, tile_path)
                map_path = os.path.join(_work_dir(), f"{stem}_{self._udim_tiles[0][0]}.png")
            else:
                # Save current 2D canvas edits to a temp PNG
                map_path = os.path.join(_work_dir(), f"{safe_ts}_{label}_for3d.png")
                self._canvas.image().save(map_path, "PNG")

            # Find the parent dock widget (BakedMapManagerWidget)
            parent_dock = self.parent()

            # Enter 3D paint mode — creates temp layers in SP
            if _enter_paint_mode(self._ts, self._usage, map_path, parent_dock, mode='3D'):
                self.accept()  # close paint window
            else:
                self._btn_2d.setChecked(True)
                self._btn_3d.setChecked(False)

        except Exception as e:
            _log(f"3D paint switch failed: {e}", "error")
            _log(traceback.format_exc(), "error")
            self._btn_2d.setChecked(True)
            self._btn_3d.setChecked(False)
            QtWidgets.QMessageBox.critical(
                self, "3D Paint Failed", str(e))

    def _auto_load_mesh(self):
        """Try to extract and load the mesh from the current SP project automatically."""
        if self._viewport3d is None: return
        self._btn_load_mesh.setText("Loading mesh…")
        QtWidgets.QApplication.processEvents()
        path = _extract_mesh_from_project()
        if path:
            ok = self._viewport3d.load_mesh(path)
            self._btn_load_mesh.setText("Load Mesh…" if ok else "Load Mesh…  ⚠")
            return
        # Auto-load failed — leave button visible for manual pick
        self._btn_load_mesh.setText("Load Mesh…")

    def _load_mesh(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load OBJ Mesh", os.path.expanduser("~"),
            "Mesh Files (*.fbx *.obj *.dae *.ply);;FBX (*.fbx);;OBJ (*.obj)"
        )
        if not path:
            return
        self._btn_load_mesh.setText("Loading…")
        QtWidgets.QApplication.processEvents()
        ok = self._viewport3d.load_mesh(path)
        self._btn_load_mesh.setText("Load Mesh…" if ok else "Load failed — retry")

    # ── Tools ─────────────────────────────────────────────────────────────────

    def _set_tool(self, tool_id):
        self._canvas.tool = tool_id
        active_style = ("QPushButton{background:#3a5a7a;color:white;"
                         "border:1px solid #5a8aba; border-radius:4px; font-size:15px;}"
                         "QPushButton:hover{background:#4a6a8a;}")
        inactive_style = ("QPushButton{background:#333;color:#aaa;"
                           "border:1px solid #444; border-radius:4px; font-size:15px;}"
                           "QPushButton:hover{background:#444;}")
        for tid, btn in self._tool_btns.items():
            btn.setChecked(tid == tool_id)
            btn.setStyleSheet(active_style if tid == tool_id else inactive_style)
        cursors = {
            PaintCanvas.TOOL_BRUSH:   _CrossCursor,
            PaintCanvas.TOOL_ERASER:  _CrossCursor,
            PaintCanvas.TOOL_FILL:    _PointingHand,
            PaintCanvas.TOOL_EYEDROP: _WhatsThis,
        }
        self._canvas.setCursor(cursors.get(tool_id, _CrossCursor))

    def _on_tile_changed(self, idx):
        """Switch the canvas to a different UDIM tile."""
        if not self._udim_tiles or idx < 0:
            return
        new_tid = self._udim_combo.itemData(idx)
        if new_tid == self._current_tile_id:
            return

        # Save current canvas back to tile cache
        if self._current_tile_id is not None:
            self._tile_images[self._current_tile_id] = self._canvas.image().copy()

        # Load new tile (from cache or disk)
        if new_tid in self._tile_images:
            new_img = self._tile_images[new_tid]
        else:
            for tid, tpath in self._udim_tiles:
                if tid == new_tid:
                    new_img = self._load_image_file(tpath)
                    if new_img and not new_img.isNull():
                        self._tile_images[new_tid] = new_img
                    break
            else:
                return

        if new_img is None or new_img.isNull():
            _log(f"Failed to load UDIM tile {new_tid}", "warning")
            return

        self._current_tile_id = new_tid
        self._canvas.set_image(new_img)
        _log(f"Switched to UDIM tile {new_tid}")

    def _on_swatch_changed(self, c: QColor):
        self._canvas.brush_color = c
        grey = (c.red() + c.green() + c.blue()) // 3
        self._sld_value.blockSignals(True)
        self._sld_value.setValue(grey)
        self._sld_value.blockSignals(False)

    def _on_color_picked(self, c: QColor):
        self._swatch.set_color(c)
        self._canvas.brush_color = c
        grey = (c.red() + c.green() + c.blue()) // 3
        self._sld_value.blockSignals(True)
        self._sld_value.setValue(grey)
        self._sld_value.blockSignals(False)

    def _on_value_changed(self, v: int):
        c = QColor(v, v, v)
        self._swatch.set_color(c)
        self._canvas.brush_color = c

    def _setup_shortcuts(self):
        """Use QShortcut so hotkeys work regardless of which child has focus."""
        def sc(key_str, fn):
            if _QT == 6:
                from PySide6.QtGui import QShortcut, QKeySequence
            else:
                from PySide2.QtWidgets import QShortcut
                from PySide2.QtGui import QKeySequence
            s = QShortcut(QKeySequence(key_str), self)
            s.activated.connect(fn)

        sc("B",         lambda: self._set_tool(PaintCanvas.TOOL_BRUSH))
        sc("E",         lambda: self._set_tool(PaintCanvas.TOOL_ERASER))
        sc("F",         lambda: self._set_tool(PaintCanvas.TOOL_FILL))
        sc("I",         lambda: self._set_tool(PaintCanvas.TOOL_EYEDROP))
        sc("Ctrl+Z",    lambda: self._canvas.undo())
        sc("Ctrl+Y",    lambda: self._canvas.redo())
        sc("Ctrl+Shift+Z", lambda: self._canvas.redo())

    def keyPressEvent(self, event):
        # QShortcut handles tool/undo keys; pass everything else up
        super().keyPressEvent(event)

    # ── Apply ─────────────────────────────────────────────────────────────────

    def _apply(self):
        self._btn_apply.setEnabled(False)
        self._btn_apply.setText("  Saving…  ")
        QtWidgets.QApplication.processEvents()

        try:
            out_dir  = tempfile.mkdtemp(prefix="bmpainter_out_")
            label    = self._map_label.replace(" ", "_")
            safe_ts  = "".join(c if c.isalnum() or c in "-_." else "_"
                               for c in self._ts.name())

            if self._udim_tiles:
                # ── UDIM: save all tiles with proper naming ──────────────
                # Save current canvas back to tile cache first
                if self._current_tile_id is not None:
                    self._tile_images[self._current_tile_id] = self._canvas.image().copy()

                stem = f"{self._ts.name()}_{label}_painted"
                first_path = None
                for tid, orig_path in self._udim_tiles:
                    tile_path = os.path.join(out_dir, f"{stem}.{tid}.png")
                    if tid in self._tile_images:
                        saved = self._tile_images[tid].save(tile_path, "PNG")
                    else:
                        # Tile wasn't edited — copy original
                        shutil.copy2(orig_path, tile_path)
                        saved = True
                    if not saved:
                        raise RuntimeError(f"Failed to save tile {tid}")
                    if first_path is None:
                        first_path = tile_path
                    _log(f"UDIM tile {tid} saved → {tile_path}")

                # Import first tile — SP auto-discovers the rest via naming
                if not _import_and_apply(self._ts, self._usage, first_path):
                    raise RuntimeError("Failed to re-import UDIM tiles into SP")

                # Update thumbnail cache with first tile
                cache_path = os.path.join(_work_dir(), f"{safe_ts}_{label}.png")
                try:
                    shutil.copy2(first_path, cache_path)
                except Exception:
                    pass

            else:
                # ── Single tile (non-UDIM) ───────────────────────────────
                out_path = os.path.join(out_dir, f"{self._ts.name()}_{label}_painted.png")

                # Backup the original
                base, ext = os.path.splitext(self._source_path)
                backup    = base + "_backup" + ext
                if not os.path.exists(backup):
                    shutil.copy2(self._source_path, backup)
                    _log(f"Backup saved: {backup}")

                # Save the painted image
                saved = self._canvas.image().save(out_path, "PNG")
                if not saved:
                    raise RuntimeError("QImage.save() failed — check disk space / permissions")

                # Re-import into Substance Painter
                if not _import_and_apply(self._ts, self._usage, out_path):
                    raise RuntimeError("Failed to re-import the map into SP")

                # Update the work-dir cache so the card thumbnail refreshes
                cache_path = os.path.join(_work_dir(), f"{safe_ts}_{label}.png")
                try:
                    shutil.copy2(out_path, cache_path)
                    _log(f"Cache updated: {cache_path}")
                except Exception as ce:
                    _log(f"Cache copy failed (non-fatal): {ce}", "warning")

            self.accept()

        except Exception as e:
            _log(traceback.format_exc(), "error")
            QtWidgets.QMessageBox.critical(
                self, "Apply Failed",
                f"Could not apply painted map:\n\n{e}\n\n"
                "Check the SP Python log (Window → Views → Python Console) for details."
            )
            self._btn_apply.setEnabled(True)
            self._btn_apply.setText("  ✔  Apply to SP  ")


# ─────────────────────────────────────────────────────────────────────────────
# Map Card  (clickable tile in the main panel)
# ─────────────────────────────────────────────────────────────────────────────

class MapCard(QtWidgets.QWidget):

    open_paint = QtCore.Signal(object)   # emits MeshMapUsage

    def __init__(self, usage, parent=None):
        super().__init__(parent)
        self.usage     = usage
        self._is_baked = False
        self._hovered  = False
        label, color   = MESH_MAP_INFO[usage]

        self.setFixedHeight(58)
        self.setCursor(_PointingHand)
        self.setToolTip(f"Click to paint {label} map")

        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(8, 6, 8, 6)
        lay.setSpacing(10)

        self._thumb = QtWidgets.QLabel()
        self._thumb.setFixedSize(44, 44)
        self._thumb.setAlignment(_AlignCenter)
        self._thumb.setStyleSheet("border:1px solid #3a3a3a; background:#1a1a1a;")
        lay.addWidget(self._thumb)

        info = QtWidgets.QWidget()
        il   = QtWidgets.QVBoxLayout(info)
        il.setContentsMargins(0, 0, 0, 0)
        il.setSpacing(1)

        self._lbl_name = QtWidgets.QLabel(label)
        self._lbl_name.setStyleSheet(
            f"color:{color}; font-weight:bold; font-size:12px;"
        )
        il.addWidget(self._lbl_name)

        self._lbl_status = QtWidgets.QLabel("Not baked")
        self._lbl_status.setStyleSheet("color:#555; font-size:10px;")
        il.addWidget(self._lbl_status)

        lay.addWidget(info, 1)

        self._arrow = QtWidgets.QLabel("▶")
        self._arrow.setStyleSheet("color:#444; font-size:11px;")
        lay.addWidget(self._arrow)

    def set_baked(self, baked, pixmap=None):
        self._is_baked = baked
        if baked:
            self._lbl_status.setText("● Baked — click to paint")
            self._lbl_status.setStyleSheet("color:#4AFF9E; font-size:10px;")
            self._arrow.setStyleSheet("color:#4A9EFF; font-size:11px;")
        else:
            self._lbl_status.setText("○ Not baked")
            self._lbl_status.setStyleSheet("color:#444; font-size:10px;")
            self._arrow.setStyleSheet("color:#333; font-size:11px;")
            self._thumb.clear()
            self._thumb.setText("—")
            self._thumb.setStyleSheet(
                "border:1px solid #2a2a2a; background:#1a1a1a; color:#444; font-size:10px;"
            )

        if pixmap and not pixmap.isNull():
            self._thumb.setPixmap(
                pixmap.scaled(44, 44, _KeepAR, _SmoothXform)
            )
            self._thumb.setStyleSheet("border:1px solid #3a3a3a;")

    def set_loading(self, loading: bool):
        if loading:
            self._lbl_status.setText("⟳ Exporting…")
            self._lbl_status.setStyleSheet("color:#FFD04A; font-size:10px;")
            self._arrow.setStyleSheet("color:#FFD04A; font-size:11px;")
            self.setCursor(Qt.CursorShape.WaitCursor if _QT == 6 else Qt.WaitCursor)
        else:
            self.setCursor(_PointingHand)
            self.update()

    def mousePressEvent(self, event):
        if event.button() == _LMB and self._is_baked:
            self.open_paint.emit(self.usage)

    def paintEvent(self, event):
        p = QPainter(self)
        if self._is_baked and self._hovered:
            p.fillRect(self.rect(), QColor(255, 255, 255, 12))
        elif self._is_baked:
            p.fillRect(self.rect(), QColor(38, 38, 38))
        else:
            p.fillRect(self.rect(), QColor(28, 28, 28))
        p.setPen(QPen(QColor(48, 48, 48)))
        p.drawLine(0, self.height()-1, self.width(), self.height()-1)

    def enterEvent(self, e):
        self._hovered = True
        self.update()

    def leaveEvent(self, e):
        self._hovered = False
        self.update()


# ─────────────────────────────────────────────────────────────────────────────
# Main docked panel
# ─────────────────────────────────────────────────────────────────────────────

class BakedMapManagerWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(PLUGIN_NAME)
        self.setMinimumWidth(300)
        self._cards          = {}
        self._paint_windows  = []
        self._build_ui()
        self._connect_events()
        self._refresh()

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        hdr = QtWidgets.QWidget()
        hdr.setStyleSheet("background:#1a1a1a;")
        hl  = QtWidgets.QHBoxLayout(hdr)
        hl.setContentsMargins(10, 8, 8, 8)
        title = QtWidgets.QLabel(
            f"<b style='color:#ddd;font-size:13px;'>{PLUGIN_NAME}</b>"
            f"<span style='color:#444; font-size:10px;'> v{PLUGIN_VERSION}</span>"
            f"<span style='color:#444; font-size:10px;'> By Elijah Sparshott</span>"
        )
        hl.addWidget(title)
        hl.addStretch()
        btn_r = QtWidgets.QPushButton("↺")
        btn_r.setFixedSize(26, 26)
        btn_r.setStyleSheet(
            "QPushButton{background:#333;color:#888;border:none;border-radius:3px;}"
            "QPushButton:hover{background:#444;}"
        )
        btn_r.setToolTip("Refresh")
        btn_r.clicked.connect(self._refresh_all_thumbnails)
        hl.addWidget(btn_r)
        root.addWidget(hdr)

        # Texture set bar
        ts_bar = QtWidgets.QWidget()
        ts_bar.setStyleSheet("background:#202020; border-bottom:1px solid #2e2e2e;")
        tl = QtWidgets.QHBoxLayout(ts_bar)
        tl.setContentsMargins(8, 4, 8, 4)
        lbl = QtWidgets.QLabel("Texture Set:")
        lbl.setStyleSheet("color:#777; font-size:10px;")
        tl.addWidget(lbl)
        self.combo_ts = QtWidgets.QComboBox()
        self.combo_ts.setStyleSheet(
            "QComboBox{background:#2a2a2a; color:#ccc; border:1px solid #3a3a3a; padding:2px;}"
        )
        self.combo_ts.currentIndexChanged.connect(self._on_ts_changed)
        tl.addWidget(self.combo_ts, 1)
        root.addWidget(ts_bar)

        # Hint
        hint = QtWidgets.QLabel("  Click any baked map to open the paint window")
        hint.setStyleSheet("background:#1c1c1c; color:#555; font-size:10px; padding:3px 8px;")
        root.addWidget(hint)

        # Cards
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(_SBAlwaysOff)
        scroll.setStyleSheet("QScrollArea{border:none; background:#1c1c1c;}")

        container = QtWidgets.QWidget()
        container.setStyleSheet("background:#1c1c1c;")
        cl = QtWidgets.QVBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        for usage in MESH_MAP_INFO:
            card = MapCard(usage)
            card.open_paint.connect(self._start_paint_mode)
            cl.addWidget(card)
            self._cards[usage] = card

        cl.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        # Status bar
        self._status = QtWidgets.QLabel("  Ready")
        self._status.setStyleSheet(
            "background:#111; color:#555; font-size:10px; padding:3px 8px;"
        )
        root.addWidget(self._status)

    def _connect_events(self):
        for ev in (spevent.ProjectOpened, spevent.ProjectClosed,
                   spevent.ProjectCreated, spevent.BakingProcessEnded):
            spevent.DISPATCHER.connect(ev, self._on_project_event)

    def _disconnect_events(self):
        for ev in (spevent.ProjectOpened, spevent.ProjectClosed,
                   spevent.ProjectCreated, spevent.BakingProcessEnded):
            spevent.DISPATCHER.disconnect(ev, self._on_project_event)

    def _on_project_event(self, event):
        # When a new project is opened/created, clear the cached maps from the
        # previous project so stale thumbnails don't bleed through.
        if isinstance(event, (spevent.ProjectOpened, spevent.ProjectCreated)):
            self._clear_work_dir()
        self._refresh()
        # After a bake, proactively export fresh thumbnails for all baked maps
        # that don't have a cache file yet (non-blocking: best-effort).
        if isinstance(event, spevent.BakingProcessEnded):
            self._refresh_thumbnails_async()

    def _clear_work_dir(self):
        """Remove cached PNGs from the work directory."""
        wd = _work_dir()
        for f in os.listdir(wd):
            if f.lower().endswith(".png"):
                try:
                    os.remove(os.path.join(wd, f))
                except OSError:
                    pass

    def _refresh_thumbnails_async(self):
        """Export thumbnails for baked maps not yet cached. Called after bake."""
        ts = self._current_ts()
        if ts is None:
            return
        for usage, card in self._cards.items():
            try:
                baked = ts.get_mesh_map_resource(usage) is not None
            except Exception:
                baked = False
            if not baked:
                continue
            label   = MESH_MAP_INFO[usage][0].replace(" ", "_")
            safe_ts = "".join(c if c.isalnum() or c in "-_." else "_" for c in ts.name())
            cached  = os.path.join(_work_dir(), f"{safe_ts}_{label}.png")
            if not os.path.isfile(cached):
                # Export this map to populate the thumbnail cache
                try:
                    path = _export_map_to_file(ts, usage)
                    if path:
                        px = QPixmap(path)
                        if not px.isNull():
                            card.set_baked(True, px)
                            QtWidgets.QApplication.processEvents()
                except Exception as e:
                    _log(f"Thumbnail export failed for {label}: {e}", "warning")

    def _refresh(self):
        self.combo_ts.blockSignals(True)
        prev = self.combo_ts.currentText()
        self.combo_ts.clear()

        if not spproject.is_open():
            self.combo_ts.blockSignals(False)
            for c in self._cards.values(): c.set_baked(False)
            self._set_status("No project open")
            return

        for ts in spset.all_texture_sets():
            self.combo_ts.addItem(ts.name(), userData=ts)

        idx = self.combo_ts.findText(prev)
        if idx >= 0:
            self.combo_ts.setCurrentIndex(idx)

        self.combo_ts.blockSignals(False)
        self._update_cards()
        self._set_status(f"{self.combo_ts.count()} texture set(s)")

    def _current_ts(self):
        return self.combo_ts.currentData()

    def _on_ts_changed(self, _):
        self._update_cards()

    def _update_cards(self):
        ts = self._current_ts()
        for usage, card in self._cards.items():
            if ts is None:
                card.set_baked(False)
                continue
            try:
                baked = ts.get_mesh_map_resource(usage) is not None
            except Exception:
                baked = False

            # Only show thumbnails for maps already exported to the work dir —
            # never trigger a full export just to refresh the card list.
            thumb = None
            if baked:
                label   = MESH_MAP_INFO[usage][0].replace(" ", "_")
                safe_ts = "".join(c if c.isalnum() or c in "-_." else "_"
                                  for c in ts.name())
                cached  = os.path.join(_work_dir(), f"{safe_ts}_{label}.png")
                if os.path.isfile(cached):
                    px = QPixmap(cached)
                    if not px.isNull():
                        thumb = px

            card.set_baked(baked, thumb)

    def _open_paint_window(self, usage):
        ts = self._current_ts()
        if ts is None:
            return

        label = MESH_MAP_INFO[usage][0]
        card  = self._cards.get(usage)

        # ── Step 1: auto-export the baked map to a known file ─────────────────
        # This is the reliable path — we never try to guess the resource URL.
        self._set_status(f"Exporting {label}…")
        if card:
            card.set_loading(True)
        QtWidgets.QApplication.processEvents()

        path = None
        try:
            path = _export_map_to_file(ts, usage)
        except Exception:
            _log(traceback.format_exc(), "error")
        finally:
            if card:
                card.set_loading(False)

        if not path:
            self._set_status(f"Export failed for {label}", warn=True)
            QtWidgets.QMessageBox.critical(
                self, "Export Failed",
                f"Could not export the {label} map.\n\n"
                "Possible reasons:\n"
                "  • The map hasn't been baked yet for this Texture Set.\n"
                "  • The mesh map name used by the export preset doesn't match\n"
                "    what SP expects for this map type.\n\n"
                "Check the SP Python Console (Window → Views → Python Console)\n"
                "for the detailed error."
            )
            return

        # ── Step 2: detect UDIM tiles ────────────────────────────────────────
        udim_tiles = None
        try:
            if ts.has_uv_tiles():
                safe_ts = "".join(c if c.isalnum() or c in "-_." else "_"
                                  for c in ts.name())
                stem_base = f"{safe_ts}_{label.replace(' ', '_')}"
                udim_tiles = _find_udim_tiles(_work_dir(), stem_base)
                if udim_tiles:
                    _log(f"UDIM tiles found: {[t[0] for t in udim_tiles]}")
                else:
                    _log("UDIM texture set but no tiles found — opening single file")
        except Exception:
            pass

        # ── Step 3: open the paint window ─────────────────────────────────────
        try:
            win = PaintWindow(ts, usage, path, parent=self,
                              udim_tiles=udim_tiles)
            self._paint_windows.append(win)
            win.finished.connect(lambda result, w=win: self._on_win_closed(w))
            win.show()
            win.raise_()
            tile_info = f" ({len(udim_tiles)} tiles)" if udim_tiles else ""
            self._set_status(f"Paint window open — {label}{tile_info}")
        except Exception as e:
            _log(traceback.format_exc(), "error")
            QtWidgets.QMessageBox.critical(self, "Error Opening Paint Window", str(e))

    def _start_paint_mode(self, usage):
        """Export the baked map and enter SP-native paint mode.
        Automatically uses whichever 2D/3D mode SP is currently in."""
        global _active_3d_paint_widget

        ts = self._current_ts()
        if ts is None:
            return

        if _active_3d_paint_widget is not None:
            QtWidgets.QMessageBox.information(
                self, "Paint Mode Active",
                "A paint session is already active.\n"
                "Click Apply or Cancel first.")
            return

        label = MESH_MAP_INFO[usage][0]
        card = self._cards.get(usage)

        # Export the baked map
        self._set_status(f"Exporting {label}…")
        if card:
            card.set_loading(True)
        QtWidgets.QApplication.processEvents()

        path = None
        try:
            path = _export_map_to_file(ts, usage)
        except Exception:
            _log(traceback.format_exc(), "error")
        finally:
            if card:
                card.set_loading(False)

        if not path:
            self._set_status(f"Export failed for {label}", warn=True)
            QtWidgets.QMessageBox.critical(
                self, "Export Failed",
                f"Could not export the {label} map.")
            return

        # Enter paint mode (keeps current 2D/3D viewport mode)
        if _enter_paint_mode(ts, usage, path, self):
            self._set_status(f"Paint — {label}")
        else:
            self._set_status("Paint setup failed", warn=True)
            self._set_status("Error opening paint window", warn=True)

    def _on_win_closed(self, win):
        self._paint_windows = [w for w in self._paint_windows if w is not win]
        self._update_cards()
        self._set_status("Map updated — thumbnails refreshed")

    def _refresh_single_thumbnail(self, usage):
        """Re-export and refresh just one map card's thumbnail."""
        ts = self._current_ts()
        if ts is None:
            return
        card = self._cards.get(usage)
        if not card:
            return
        try:
            path = _export_map_to_file(ts, usage)
            if path:
                px = QPixmap(path)
                if not px.isNull():
                    card.set_baked(True, px)
        except Exception as e:
            _log(f"Single thumbnail refresh failed: {e}", "warning")

    def _refresh_all_thumbnails(self):
        """Explicitly re-export all baked map thumbnails (called by refresh button)."""
        self._refresh()
        ts = self._current_ts()
        if ts is None:
            return
        self._set_status("Refreshing thumbnails…")
        QtWidgets.QApplication.processEvents()
        count = 0
        for usage, card in self._cards.items():
            try:
                baked = ts.get_mesh_map_resource(usage) is not None
            except Exception:
                baked = False
            if not baked:
                continue
            try:
                path = _export_map_to_file(ts, usage)
                if path:
                    px = QPixmap(path)
                    if not px.isNull():
                        card.set_baked(True, px)
                        count += 1
                        QtWidgets.QApplication.processEvents()
            except Exception as e:
                _log(f"Thumbnail refresh failed: {e}", "warning")
        self._set_status(f"Thumbnails refreshed — {count} map(s)")

    def _set_status(self, msg, warn=False):
        col = "#FF9E4A" if warn else "#555"
        self._status.setStyleSheet(
            f"background:#111; color:{col}; font-size:10px; padding:3px 8px;"
        )
        self._status.setText(f"  {msg}")

    def closeEvent(self, event):
        self._disconnect_events()
        super().closeEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
# Plugin entry-points
# ─────────────────────────────────────────────────────────────────────────────

_widget = None


def start_plugin():
    global _widget
    _widget = BakedMapManagerWidget()
    spui.add_dock_widget(_widget)
    _log(f"Loaded  {PLUGIN_NAME} v{PLUGIN_VERSION}")


def close_plugin():
    global _widget
    if _widget:
        spui.delete_ui_element(_widget)
        _widget = None
    _log("Unloaded.")
