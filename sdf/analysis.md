# SDF Real-Time Generator — Analysis

## Context

The goal is to let artists paint face/body shadow frames directly in Substance Painter and see
the SDF result live in the viewport through `Rizum_Anime_ToonShader_V12`. Existing SDF
generators are offline tools — you generate the SDF separately, import it, and can no longer
adjust the source frames while seeing the result.

---

## How the Toon Shader Uses SDF (User0 Channel)

```glsl
float lightAngle = (lightDir.x + 1.0) * 0.5;
shadowMask = smoothstep(sdfData.r - 0.05, sdfData.r + 0.05, lightAngle);
```

Each pixel's User0 value is a **threshold angle**:
- `shadowMask = 0` (shadow) when `lightAngle < sdfData.r`
- `shadowMask = 1` (lit) when `lightAngle > sdfData.r`

So `sdfData.r` means: *"the minimum light angle at which this pixel becomes lit."*
- `0.0` → always lit
- `1.0` → always in shadow

---

## Two Distinct Things Per Frame

This is the most important distinction:

| What | What it looks like | Who controls it | Purpose |
|---|---|---|---|
| **Fill layer content** | A fixed flat gray value, e.g. `0.3` | Plugin sets and manages | Encodes the angle threshold into User0 |
| **Mask stack** | Black/white painting, multiple layers | Artist paints freely | Controls WHERE this threshold applies |

The artist **only ever paints black/white** — into the mask stack. The gray value in the fill
layer content is invisible during painting; the plugin manages it entirely.

**Analogy**: each frame is a stencil (mask) + a pre-printed gray sheet (fill content). The
artist cuts the stencil shape. The plugin pre-prints the correct shade of gray. The compositor
combines them.

---

## The Real-Time Solution: Native Layer Compositing

Substance Painter's own compositor acts as the SDF generator with zero Python computation, if
the layer stack is structured correctly.

### Structure

Stack N fill layers (bottom → top) inside a `SDF_Generator` group in the User0 channel:

| Layer order | Fill content (User0) | Mask meaning |
|---|---|---|
| Bottom — Frame_01 | `1.0` (100% angle) | Artist paints the broadest / most-shadowed frame first |
| Frame_02 | `0.9` | Slightly narrower shadow |
| ... | ... | ... |
| Top — Frame_09 | `0.1` (10% angle) | Narrowest / least-shadowed frame |

With **Normal blending**, the topmost layer that covers a pixel wins:
- Pixels in all shadows → keep the narrowest surviving frame's value ✓
- Pixels only in the widest shadow → keep the broad bottom frame's high value ✓
- Pixels never covered → get 0 — always lit ✓

This is exactly the SDF encoding the toon shader expects. No computation needed. SP composites
it in real time; the viewport updates as the user paints.

### Quality note

This approach is step-quantized — a pixel snaps to the nearest frame's value (0.1, 0.2, etc.).
This is sufficient for live preview. The Bake step (Phase 5) produces smooth sub-step values.

Stacks authored under the previous convention may need their frame order corrected and then
re-synced before preview/bake match the current broad-first workflow.

---

## Mask Stack: Multi-Layer Painting Per Frame

Each fill layer's mask is not limited to a single paint layer. The mask stack accepts any number
of `PaintEffectNode` and `FillEffectNode` stacked together. They blend bottom-to-top exactly
like a mini layer stack, all contributing to the same single mask channel.

```
Frame_03 Fill Layer
│
├── CONTENT: gray 0.3 → writes into User0
│
└── MASK (single channel, result of all effects below combined):
      PaintEffectNode   ← SP refinements painted on top
      FillEffectNode    ← external PNG from Photoshop/CSP
      PaintEffectNode   ← duplicated from Frame_02, modified
      PaintEffectNode   ← main shadow painting
      FillEffectNode    ← base (black = additive, white = subtractive)
```

**Key constraint**: `PaintEffectNode` and `FillEffectNode` inside a mask stack **cannot have
their own sub-masks**. They don't need them — they ARE the mask. They paint directly into the
parent fill layer's single mask channel. Multiple effects stack and blend using their blending
modes.

---

## Flexible Frame Management

### Adding frames between existing ones

Gray values must not be hardcoded at creation. They are **derived from layer position** and
redistributed whenever the user adds, removes, or reorders frames. The `sync_frame_values()`
operation walks the group bottom-to-top and evenly redistributes values based on current count.

### Additive vs subtractive painting

| Mode | Base fill | Artist paints | Best when |
|---|---|---|---|
| **Additive** | Black base | White to ADD shadow | Default workflow; broad frame first, narrower frames later |
| **Subtractive** | White base | Black to REMOVE shadow | Optional carve-out workflow when that feels easier |

The base fill effect at the bottom of each frame's mask stack sets the starting point.
Per-frame toggle in the plugin UI calls `set_mask_background()`.

### Duplicate-and-modify from another frame

The artist duplicates a `PaintEffectNode` from one frame's mask stack into another's using
SP's native right-click → duplicate, drag. The plugin does not handle this — it is native SP
layer management. No API needed because strokes are not accessible via Python anyway.

---

## Borrowing Shapes from Other Channels (Anchor Points)

When an artist wants to reuse a shape already painted in another channel (e.g., a knee shape
from the BaseColor channel), they use **Anchor Points**.

An `AnchorPointEffectNode` exposes the composited layer output at a specific point in any stack
and makes it referenceable elsewhere. A `FillEffectNode` in a mask stack can accept an
`AnchorPointEffectNode` directly as its source:

```python
fill_effect.set_source(None, anchor_point_node)  # None = mask context
```

This is **live** — edits to the referenced layer automatically update the SDF mask. A
`LevelsEffectNode` above it in the mask stack thresholds the borrowed shape to clean black/white.
In the plugin UI, the artist picks the target SDF frame with a per-row radio selector, then
clicks **Borrow Shape** after selecting the source layer in Painter.

**Insertion constraint**: `AnchorPointEffectNode` can **only** be inserted inside a `Content`
or `Mask` stack (via `InsertPosition.inside_node(layer, NodeStack.Content)`). It **cannot** be
placed above/below a `LayerNode` using `InsertPosition.above_node()` or `below_node()`. This
is enforced by the API — see the insertion rules table in the `layerstack.edition` docs.

---

## External Editing Workflow (Photoshop / Clip Studio Paint)

Artists sometimes need to edit a frame mask in an external app. The imported PNG is flattened
— no layers. This is handled by making the imported bitmap **one FillEffectNode** in the mask
stack:

```
Frame_03 mask stack:
    FillEffectNode           ← latest explicit external import (promoted to top)
    PaintEffectNode          ← SP corrections from the previous round-trip
    FillEffectNode [black]   ← base
```

The external edit contributes as one composited layer. On every explicit re-import, the plugin
creates a refreshed external fill at the top of the mask stack and removes older `ext_*` fills,
so the newest external pass becomes the visible source of truth for the next round-trip.

### Color space: the one real technical problem

External apps work in sRGB. SP's mask channel is linear. A 0.5 gray in sRGB becomes ~0.214
in linear after gamma conversion — mask boundaries shift. The bitmap source must be set to
`GenericColorSpace.Raw` to prevent SP from applying gamma correction:

```python
source = fill_effect.set_source(None, resource_id)
source.set_color_space(sp.colormanagement.GenericColorSpace.Raw)
```

**API note**: `DataColorSpace` only has `Data` and `DataSigned` members — there is no
`DataColorSpace.Raw`. Use `GenericColorSpace.Raw` which accepts `sRGB`, `Working`, or `Raw`.

### Re-editing flow

On subsequent rounds (edit → import → edit again), the simplest and most robust approach is
to **re-import** and insert a refreshed external fill at the top of the mask stack. This stays
synchronous, works whether or not the file path changed, and preserves the intended workflow
where the newest external pass wins visually.

```python
resource = sp.resource.import_project_resource(path, Usage.TEXTURE, name=...)
fill_effect = sp.layerstack.insert_fill(top_mask_position)
source = fill_effect.set_source(None, resource.identifier())
source.set_color_space(sp.colormanagement.GenericColorSpace.Raw)
```

Alternative (when the path is guaranteed stable): `reload_modified_resources_async()` with
`ResourcesListFilter([resource_id])` — but this is async and requires the plugin to wait for
the `ReloadResourcesEnded` event before reporting success. It also preserves the current stack
order, so it does not help when the desired behavior is "latest external import becomes topmost".
Explicit re-import is simpler and matches the chosen workflow better.

---

## The Bake Step: SDF Interpolation Algorithm

The `sdf_shadow_threshold_map-main` project in this directory implements the proper algorithm.

### What it does

For each consecutive frame pair (i, i+1):
1. **SDF from each binary mask**: `sdf = |distanceTransform(mask) - distanceTransform(inverted)|`
   Produces a gradient that peaks at the mask boundary edge.
2. **Gradient**: `sdf1 / (sdf1 + sdf2)` — smoothly transitions 0→1 across the boundary zone.
3. **Transition zone mask**: `abs(img1_normalized - img2_normalized)` — only pixels that
   change between the two frames.
4. **Lerp + mask**: maps gradient into `[step_start, step_end]`, multiplied by the transition mask.
5. **Sum all pairs** → final shadow threshold map.

### Quality difference vs. native compositing

| Approach | Transition zone |
|---|---|
| Native compositing (preview) | Hard-snaps to nearest frame value |
| SDF interpolation (bake) | Smooth sub-step value from SDF distance to each boundary |

A pixel halfway between frame 3 and frame 4's boundary gets exactly `0.35`, not `0.3` or `0.4`.

### Binarization behavior in sdftool

`sdftool/__init__.py` loads each frame image with `cv2.imread()`, converts via
`cv2.cvtColor(BGR2GRAY)`, then binarizes at threshold 127. This has two critical implications
for how frames are exported from SP:

1. **Export channel format**: Use `"destChannel": "L"` (luminance) in the export config, **not**
   `"destChannel": "R"`. An R-only PNG produces (R=255, G=0, B=0) for white pixels. OpenCV's
   BGR→gray conversion computes `0.299×R + 0.587×G + 0.114×B = 76`, which falls **below** the
   127 threshold and binarizes to black. `"L"` produces a proper grayscale PNG where 255 stays 255.

2. **Fill values vs binarization threshold**: the narrowest frame in a 9-frame setup can have a
   fill value near `0.111`, which produces 8-bit pixel value ~28 in the exported PNG. This is
   below 127 and binarizes to black — that frame would silently export as an empty mask. **Fix**:
   during per-frame export, temporarily set the fill value to 1.0 so masked pixels export as
   white (255), then restore the original value. The fill value only matters for the composited
   preview; the bake algorithm derives its own gradients from the binary mask shapes.

### Dependency

`sdftool/__init__.py` uses `numpy` and `cv2`. Neither ships with SP's Python.

| Option | Trade-off |
|---|---|
| Bundled bake executable | Best distribution story for non-technical users; no Python/pip setup |
| Subprocess to system Python + `run.py` | Fine for development, but requires users to have numpy+cv2 in system Python |
| QImage proxy smooth fallback | No deps, inferior quality |

For a shared artist-facing plugin, the preferred bake path is a bundled executable. The
system-Python subprocess path is still useful during development and debugging, but should not
be the main distribution strategy. If neither bundled bake nor system Python is available, fall
back to the QImage smooth preview only as a lower-quality safety net.

**Subprocess hazard**: `sdftool.save_image(..., confirm_overwrite=True)` calls `input()` to ask
for terminal confirmation when the output file already exists. This would hang a subprocess.
Safe only because the bake workflow writes to a fresh temp directory where no pre-existing file
exists. The implementing agent should ensure `confirm_overwrite` remains `True` (the default)
and the output path is always in a clean temp directory.

---

## Key API Capabilities Confirmed

| Capability | API |
|---|---|
| Create group / fill / paint layers | `insert_group()`, `insert_fill()`, `insert_paint()` |
| Set flat color on fill layer | `fill.set_source(channel, Color(v, v, v))` |
| Restrict fill to User0 only | `fill.active_channels = {ChannelType.User0}` |
| Multi-layer mask stack | `insert_fill()` / `insert_paint()` with `NodeStack.Mask` |
| Set mask background per frame | `fill.set_mask_background(MaskBackground.Black/White)` |
| Anchor point for shape reuse | `insert_anchor_point_effect()` + `set_source(None, anchor)` |
| Bitmap import | `import_project_resource()` / `import_session_resource()` |
| Set bitmap color space | `source.set_color_space(GenericColorSpace.Raw)` |
| Reload modified resource (async) | `reload_modified_resources_async(ResourcesListFilter([id]))` — requires same file path |
| Replace bitmap source (sync) | Re-import + `fill_effect.set_source(None, new_resource_id)` — works across path changes |
| Export composited channel | `export_project_textures()` |
| Redistribute frame values | Walk `group.sub_layers()`, call `set_source()` per layer |
| Single undo for bulk ops | `ScopedModification` context manager |
| Detect layer stack changes | `event.LayerStacksModelDataChanged` (500ms min throttle) |

## Key API Constraints

| Limitation | Implication |
|---|---|
| `export_project_textures()` exports composited result only | Per-frame export requires visibility toggle loop |
| Paint strokes not accessible via Python | Artist must paint manually; plugin only creates structure |
| `PaintEffectNode` / `FillEffectNode` in mask stack have no sub-masks | They ARE the mask; no nesting needed |
| `GroupLayerNode` cannot be inserted inside a mask stack | Multi-layer per frame done via multiple effects, not nested groups |
| `AnchorPointEffectNode` only valid inside Content/Mask stacks | Must use `InsertPosition.inside_node(layer, NodeStack.Content)` — NOT `above_node()` or `below_node()` |
| `set_selected_nodes()` raises `RuntimeError` inside `ScopedModification` | Must call outside `with` block, or defer to after scope exits |
| `DataColorSpace` has no `.Raw` member | Use `GenericColorSpace.Raw` for raw/unmanaged color data |
| `reload_modified_resources_async()` is async — requires awaiting `ReloadResourcesEnded` event, and the file path must stay identical | For round-trip edits, prefer sync re-import + `set_source()` update — works across path changes with no event waiting |
| SP ships without numpy / cv2 / PIL | Bake step requires system Python subprocess or QImage fallback |
| `TextureStateEvent` minimum throttle: 500ms | Max 2 update events/second per texture |
| SP 10.x+ uses PySide6 (not PySide2) | All Qt imports must use `PySide6.QtWidgets`, `PySide6.QtGui`, etc. |
