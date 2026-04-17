import os

import substance_painter as sp

from .sdf_layer_setup import _find_sdf_group, USER0


def import_external_edit(frame_fill, png_path: str):
    """Import a PNG into this frame's mask stack as a FillEffectNode.
    - First call: creates a new 'ext_*' FillEffectNode in the mask.
    - Subsequent calls: create a refreshed topmost external fill, then remove
      older external fills so the latest external pass wins visually.
    Uses GenericColorSpace.Raw to bypass sRGB gamma on mask values.
    """
    existing_fills = [
        effect for effect in frame_fill.mask_effects()
        if effect.get_name().startswith("ext_")
    ]

    resource = sp.resource.import_project_resource(
        png_path,
        sp.resource.Usage.TEXTURE,
        name=f"ext_{frame_fill.get_name()}")
    resource_id = resource.identifier()

    with sp.layerstack.ScopedModification("Import SDF External Edit"):
        effects = list(frame_fill.mask_effects())
        if effects:
            mask_pos = sp.layerstack.InsertPosition.above_node(effects[0])
        else:
            mask_pos = sp.layerstack.InsertPosition.inside_node(
                frame_fill, sp.layerstack.NodeStack.Mask)

        fill_effect = sp.layerstack.insert_fill(mask_pos)
        fill_effect.set_name(f"ext_{frame_fill.get_name()}")
        source = fill_effect.set_source(None, resource_id)
        source.set_color_space(sp.colormanagement.GenericColorSpace.Raw)

        for old_fill in existing_fills:
            sp.layerstack.delete_node(old_fill)


def _add_temp_baseline(group):
    """Insert a temp black-fill at the BOTTOM of the group (User0 = 0).
    Ensures unpainted areas export as explicit black, not transparent.
    Returns the temp layer's uid for later removal.
    """
    sub = group.sub_layers()
    if sub:
        # bottom = last in top-to-bottom order
        pos = sp.layerstack.InsertPosition.below_node(sub[-1])
    else:
        pos = sp.layerstack.InsertPosition.inside_node(
            group, sp.layerstack.NodeStack.Substack)
    temp = sp.layerstack.insert_fill(pos)
    temp.set_name("__sdf_export_baseline")
    temp.active_channels = {USER0}
    temp.set_source(USER0, sp.colormanagement.Color(0.0, 0.0, 0.0))
    return temp


def export_frame_for_external(frame_fill, output_path: str):
    """Export this single frame's composited User0 mask to a PNG.
    Hides all other frames in the SDF_Generator group during export.
    """
    group = _find_sdf_group()
    if group is None:
        raise RuntimeError("SDF_Generator group not found.")

    all_frames = list(group.sub_layers())
    target_uid = frame_fill.uid()

    original_visibility = {f.uid(): f.is_visible() for f in all_frames}
    original_color = frame_fill.get_source(USER0).get_color()
    temp_baseline = None

    try:
        with sp.layerstack.ScopedModification("SDF Export Frame Setup"):
            temp_baseline = _add_temp_baseline(group)
            for f in all_frames:
                f.set_visible(f.uid() == target_uid)
            frame_fill.set_source(
                USER0, sp.colormanagement.Color(1.0, 1.0, 1.0))

        texture_set_name = frame_fill.get_texture_set().name()
        out_dir = os.path.dirname(output_path)
        out_name = os.path.splitext(os.path.basename(output_path))[0]
        config = {
            "exportPath": out_dir,
            "exportShaderParams": False,
            "defaultExportPreset": "frame_ext_export",
            "exportPresets": [{
                "name": "frame_ext_export",
                "maps": [{
                    "fileName": out_name,
                    "channels": [{
                        "destChannel": "L",
                        "srcChannel": "R",
                        "srcMapType": "documentMap",
                        "srcMapName": "user0",
                    }],
                    "parameters": {
                        "fileFormat": "png",
                        "bitDepth": "16",
                    },
                }],
            }],
            "exportList": [{"rootPath": texture_set_name}],
            "exportParameters": [{
                "parameters": {
                    "dithering": False,
                    "paddingAlgorithm": "transparent",
                    "dilationDistance": 16,
                },
            }],
        }
        sp.export.export_project_textures(config)
    finally:
        with sp.layerstack.ScopedModification("SDF Export Frame Restore"):
            if temp_baseline is not None:
                sp.layerstack.delete_node(temp_baseline)
            frame_fill.set_source(USER0, original_color)
            for f in all_frames:
                f.set_visible(original_visibility.get(f.uid(), True))
