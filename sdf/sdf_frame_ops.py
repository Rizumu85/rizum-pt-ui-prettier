import substance_painter as sp

from .sdf_layer_setup import USER0, _find_sdf_group, _frame_name, _frame_value


def _sync_frame_values_impl(group):
    """Inner: no ScopedModification wrapper.
    Called by sync_frame_values (standalone) and add_frame (inside its scope).
    """
    layers = list(reversed(group.sub_layers()))  # bottom-to-top
    total = len(layers)
    if total == 0:
        return
    for i, layer in enumerate(layers, start=1):
        value = _frame_value(i, total)
        layer.set_source(USER0,
                         sp.colormanagement.Color(value, value, value))
        layer.set_name(_frame_name(i, value))


def sync_frame_values():
    group = _find_sdf_group()
    if group is None:
        raise RuntimeError("SDF_Generator group not found.")
    with sp.layerstack.ScopedModification("Sync SDF Frame Values"):
        _sync_frame_values_impl(group)


def get_frame_mask_mode(frame_fill) -> bool:
    """Return True if the frame is in additive mode (black mask background),
    False if subtractive (white mask background).
    """
    return frame_fill.get_mask_background() == sp.layerstack.MaskBackground.Black


def set_frame_mask_mode(frame_fill, additive: bool):
    """Toggle between additive (black base, paint white) and
    subtractive (white base, paint black). Updates both the mask
    background and the base fill effect color.
    """
    bg = sp.layerstack.MaskBackground.Black if additive \
        else sp.layerstack.MaskBackground.White
    base_color = sp.colormanagement.Color(0.0, 0.0, 0.0) if additive \
        else sp.colormanagement.Color(1.0, 1.0, 1.0)

    with sp.layerstack.ScopedModification("Toggle SDF Frame Mask Mode"):
        frame_fill.set_mask_background(bg)
        for effect in frame_fill.mask_effects():
            if effect.get_name() == "base":
                effect.set_source(None, base_color)
                break


def add_frame(reference_layer=None):
    """Insert a new frame above reference_layer (or at the top of the group),
    then redistribute all values. Single undo step.
    """
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

        # Sync inside the same scope → single undo step.
        _sync_frame_values_impl(group)


def borrow_shape_from_layer(source_layer, target_frame_fill):
    """Reference one layer's output inside an SDF frame mask."""
    with sp.layerstack.ScopedModification("Borrow Shape for SDF Frame"):
        anchor_pos = sp.layerstack.InsertPosition.inside_node(
            source_layer, sp.layerstack.NodeStack.Content)
        anchor = sp.layerstack.insert_anchor_point_effect(
            anchor_pos, f"anchor_{source_layer.get_name()}")

        effects = list(target_frame_fill.mask_effects())
        if effects:
            fill_pos = sp.layerstack.InsertPosition.above_node(effects[0])
        else:
            fill_pos = sp.layerstack.InsertPosition.inside_node(
                target_frame_fill, sp.layerstack.NodeStack.Mask)
        fill_ref = sp.layerstack.insert_fill(fill_pos)
        fill_ref.set_name(f"borrow_{source_layer.get_name()}")
        fill_ref.set_source(None, anchor)

        levels_pos = sp.layerstack.InsertPosition.above_node(fill_ref)
        levels = sp.layerstack.insert_levels_effect(levels_pos)
        levels.set_name("Threshold (adjust me)")


def ui_borrow_shape(target_frame_fill):
    """Borrow the currently selected source layer into the target SDF frame."""
    stack = sp.textureset.get_active_stack()
    selected = sp.layerstack.get_selected_nodes(stack)
    if not selected:
        raise RuntimeError("Select the source layer in Painter first.")

    source_layer = selected[0]
    if not isinstance(source_layer, sp.layerstack.LayerNode):
        raise RuntimeError("Select a layer as the borrow source, not a mask/effect node.")
    if source_layer.uid() == target_frame_fill.uid():
        raise RuntimeError("Select a different layer as the borrow source.")

    borrow_shape_from_layer(source_layer, target_frame_fill)
