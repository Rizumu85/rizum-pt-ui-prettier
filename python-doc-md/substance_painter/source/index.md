# SourceReference

`SourceReference` is a type of source where you can use an `AnchorPointEffectNode` from the layerstack.

## Example

```python
import substance_painter as sp

# Get the currently displayed stack
stack = sp.textureset.get_active_stack()

# Insert a paint layer
position = sp.layerstack.InsertPosition.from_textureset_stack(stack)
paint = sp.layerstack.insert_paint(position)

# Insert an anchor point in the content stack
position = sp.layerstack.InsertPosition.inside_node(paint, sp.layerstack.NodeStack.Content)
anchor = sp.layerstack.insert_anchor_point_effect(position, "anchor")

# Insert a fill layer with a mask
position = sp.layerstack.InsertPosition.from_textureset_stack(stack)
fill = sp.layerstack.insert_fill(position)
fill.add_mask(sp.layerstack.MaskBackground.White)

# Insert a reference on `anchor` in multi-channel context
source = fill.set_material_source(anchor)

# Edit the channel mapping
new_mapping = {
    sp.textureset.ChannelType.BaseColor: sp.textureset.ChannelType.Metallic,
    sp.textureset.ChannelType.Metallic: sp.textureset.ChannelType.BaseColor,
    sp.textureset.ChannelType.Roughness: sp.textureset.ChannelType.Height,
    sp.textureset.ChannelType.Normal: sp.textureset.ChannelType.BaseColor,
    sp.textureset.ChannelType.Height: sp.textureset.ChannelType.Metallic
}
for dst_chn, src_chn in new_mapping.items():
    source.channel_mapping[dst_chn] = src_chn

# Select the Fill layer
sp.layerstack.set_selected_nodes([fill])
```

## class substance_painter.source.SourceReference(uid)

A class that represents an reference to an anchor point.

### property channel_mapping: ChannelMapping

The channels mapping property.

**Getter:** Returns the channel mapping property.
**Type:** ChannelMapping
**Raises:** EditionContextException – If the current context of the reference is not multi-channel.

### property referenced_channel: ChannelType

The referenced channel of the source.

**Getter:** Returns the referenced channel of the source.
**Setter:** Set the referenced channel of the source.
**Type:** ChannelMapping
**Raises:** EditionContextException – If the current context of the reference is not single-channel or if the context of the target anchor point is not multi-channel.

### property anchor: AnchorPointEffectNode

The anchor used by this source.

**Getter:** Returns the anchor used by the source.
**Type:** layerstack.AnchorPointEffectNode

### property alpha_matte: AlphaMatte

The alpha matte used by this source.

**Getter:** Returns the alpha matte of the source.
**Setter:** Set the alpha matte of the source.
**Type:** AlphaMatte

### get_levels() → LevelsParamsMono | LevelsParamsRGB

Get the parameters used by the levels of this source.

**Returns:** The parameters used by the levels of this source.
**Return type:** LevelsParamsMono | LevelsParamsRGB

### set_levels(params: LevelsParamsMono | LevelsParamsRGB) → None

Set the parameters used by the levels of this source.

**Parameters:** params (LevelsParamsMono | LevelsParamsRGB) – The parameters used by the levels of this source.
**Return type:** None

## class substance_painter.source.ChannelMapping(uid)

This class gives access to the active channels of a source reference in a dict-like fashion. See `channel_mapping` property.

Example:

```python
import substance_painter as sp
mapping = some_SourceReference_object.channel_mapping
mapping[sp.textureset.ChannelType.BaseColor] = sp.textureset.ChannelType.Specular
for channel in mapping:
    print(mapping[channel])
```

> **See also:** For more technical informations, see the official [KeysView ABCs container](https://docs.python.org/3/library/collections.abc.html#collections.abc.KeysView) documentation as well as [__getitem__](https://docs.python.org/3/reference/datamodel.html#object.__getitem__) and [__setitem__](https://docs.python.org/3/reference/datamodel.html#object.__setitem__) methods.

## Enums

### class substance_painter.source.AlphaMatte(value)

Members:

| Name | Description |
|------|-------------|
| `KeepAlpha` | Keep the alpha. |
| `ExtractAlpha` | Extract the alpha. |
| `DefaultBackgroundColor` | Matte the alpha with a default background color. |

> **Note:** The name used to define members is available as a string via the `.name` attribute (see [python enum.Enum](https://docs.python.org/3/library/enum.html#enum.Enum)).