import substance_painter as sp

USER0 = sp.textureset.ChannelType.User0


def _frame_name(index: int, value: float) -> str:
    return f"Frame_{index:02d}  [{int(round(value * 100))}%]"


def _frame_value(index: int, total: int) -> float:
    return round((total - index + 1) / total, 6)


def _find_sdf_group():
    stack = sp.textureset.get_active_stack()
    for node in sp.layerstack.get_root_layer_nodes(stack):
        if node.get_name() == "SDF_Generator":
            return node
    return None


def _insert_frame(group, index: int, total: int, additive: bool = True):
    value = _frame_value(index, total)
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
    base = sp.layerstack.insert_fill(mask_pos)
    base.set_name("base")
    base_color = sp.colormanagement.Color(0.0, 0.0, 0.0) if additive \
        else sp.colormanagement.Color(1.0, 1.0, 1.0)
    base.set_source(None, base_color)

    paint = sp.layerstack.insert_paint(mask_pos)
    paint.set_name("paint")


def setup_sdf_group(n_frames: int = 9):
    stack = sp.textureset.get_active_stack()
    if USER0 not in stack.all_channels():
        raise ValueError(
            "User0 channel not found. Add it in Texture Set Settings.")

    if _find_sdf_group() is not None:
        raise RuntimeError("SDF_Generator group already exists.")

    with sp.layerstack.ScopedModification("Setup SDF Generator"):
        pos = sp.layerstack.InsertPosition.from_textureset_stack(stack)
        group = sp.layerstack.insert_group(pos)
        group.set_name("SDF_Generator")

        # inside_node(group, Substack) inserts at TOP each time.
        # Iterate 1→N so Frame_01 stays at the bottom and Frame_N ends up at
        # the top. Values run high→low bottom-to-top, matching the canonical
        # broad-shadow-first workflow.
        for i in range(1, n_frames + 1):
            _insert_frame(group, i, n_frames, additive=True)
