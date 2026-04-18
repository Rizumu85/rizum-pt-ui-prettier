# Zhihu Article Analysis — "卡通渲染流程【番外-使用SD批量生成面部SDF贴图】"

Author: **Heee** (zhuanlan.zhihu.com)
Local archive: `卡通渲染流程【番外-使用SD批量生成面部SDF贴图】 - 知乎.htm`

## Why this article matters

It describes the **SD node graph** that `FaceShadowBlend.sbsar` appears to implement. Our previous `Reverse_Engineering_Log.md` recipe (Linear-Dodge staircase + Distance node + single Non-Uniform Blur driven by an SDF gradient) does **not** match the article. The article's recipe explains the behaviors we observed during black-box testing:

| Observation | Article's recipe explains it |
|---|---|
| Silhouette stays sharp at all Blur_Intensity values | Blur Map is zero outside the transition bands → no blur outside the shape |
| Brightest pixel never migrates as intensity rises | Per-pixel blur is modulated by a narrow edge band, not directional smearing |
| Steps progressively dissolve into a smooth gradient | Each adjacent-pair transition is feathered, then summed |
| "Right-to-left flow" perception | Artifact of ordered staircase steps dissolving — not directional smearing |

## The node recipe (as stated in the article text)

### Columns (left to right, as laid out in the article's graph screenshot)

**1. `Lightmap-8Bitmap`** (teal group)
N Bitmap inputs (article example uses 8; our `.sbsar` exposes up to 11). Each is a binary/near-binary grayscale mask representing shadow coverage at one light angle. Masks are ordered so that each successive one covers more of the face.

> Authoring constraint from the article: **"相邻贴图不建议相隔过远：会导致严重锯齿"** — adjacent masks must not be far apart in coverage, or the result aliases heavily.

**2. `AddSDF`** (gray group) — the transition bands (灰度走向图)
For each **adjacent pair** `(bitmap[i], bitmap[i+1])` a **Blend node in Subtract mode** produces `bitmap[i] − bitmap[i+1]`. The result is a thin crescent-shaped band at the boundary between the two masks. Article: "通过 blend（subtract）获取灰度走向图". There are `N−1` of these for `N` bitmaps.

**3. Non Uniform Blur Grayscale** (red nodes) — **one per adjacent pair (N−1 total)**
Article text: "通过 Non Uniform Blur Grayscale 生成**两 Lightmap 的过渡图**" — each NUB produces the **transition image between a pair of Lightmaps**, not per individual mask. Wiring per pair `(i, i+1)`:
- **Grayscale input** ← one of the pair's bitmaps (most likely `bitmap[i]`, the smaller-coverage mask of the pair)
- **Blur Map input** ← the Subtract band `bitmap[i] − bitmap[i+1]` from step 2

Exposed parameters (from `FaceShadowBlend.xml`):
| Parameter | Exposed as |
|---|---|
| Intensity | `Blur_Intensity` |
| Samples | `Blur_Samples` (article: up to 16; lower if fine detail is lost) |
| Blades | `Blur_Blades` (higher = more random pattern) |

The article **does not** state values for Anisotropy, Asymmetry, or Angle in text. The earlier version of this doc claimed `Anisotropy=0, Asymmetry=0, Intensity≈11.69, Blades=5` from a screenshot thumbnail — **those are screenshot-inferred and unverified**. To confirm, read the compiled graph defaults from `FaceShadowBlend.xml` or open the `.sbsar` in SD.

**4. Combine stage — Linear Dodge (Add) + Copy-blend at `Opacity = 1/N`** (tan group)
The article names both mechanisms as part of the combine stage:
- "通过 blend 中的**线性减淡混合（add-linear dodge）**" — the N−1 NUB outputs are summed via Linear-Dodge (Add) blends.
- "根据贴图数控制 blend（copy模式）中 opacity 的透明度（例：8张-透明度为0.125）" — a Copy-blend with `Opacity = 1/N` is used for normalization (0.125 for 8 bitmaps, ≈0.091 for 11).

The most plausible wiring (pending SD graph inspection): the N−1 feathered transition images are Linear-Dodge-summed, and a Copy-blend at 1/N scales the accumulated sum back into `[0,1]`. This matches the "2–8 张贴图对应 1–7 输出通道" statement (8 bitmaps → 7 transitions → output tap 7) and the observation that `Blur_Intensity=0` produces a clean stair-step: with zero blur, each NUB returns its grayscale input unchanged, and the sum of the N−1 adjacent-pair transitions reconstructs the staircase.

**5. Output chain** (blue group) — intermediate "angle" outputs
The article notes `2-8张贴图对应1-7输出通道` ("2–8 bitmaps correspond to output channels 1–7"). Taps on the progressive accumulation let the user pick the output matching how many bitmaps they actually fed in. For N=8, use tap 7.

**6. Preview / TestOutput** — threshold at a chosen Position
A **Histogram Scan** node feeds the final gradient with:
- `Position` exposed as a 0–1 slider → `Test_Output` in the `.sbsar`
- `Contrast` = 1 → hard edge, producing a sharp anime-style shadow at that angle

## Differences from our current `Reverse_Engineering_Log.md`

| Step | Current log | Article |
|---|---|---|
| Combine stage | Linear Dodge (Add) only | Linear-Dodge (Add) of NUB outputs **plus** Copy-blend at `1/N` for normalization |
| Transition map | `Distance` node on staircase | `Blend-Subtract` between adjacent pairs |
| Smoothing | Single Non-Uniform Blur with staircase + SDF gradient | Non-Uniform Blur **per adjacent pair** (N−1 nodes) with one mask + its subtract band |
| Number of NUB nodes | 1 | **N−1** |
| Distance node | Used | Not mentioned in the article (presumed unused) |
| NUB Anisotropy / Asymmetry | Assumed > 0 | **Not stated in article text** — verify from `.sbsar` defaults |
| Final containment | Needs explicit silhouette mask | Emerges naturally from Blur Map = 0 outside bands |

## Supporting evidence from our black-box testing

- `Blur_Intensity = 0` preview showed a clean staircase. With `Intensity=0` each NUB is a pass-through, so the Linear-Dodge sum of the N−1 subtract bands reconstructs the original staircase. Matches.
- Intensity sweep (`gen_0` → `gen_100`) showed silhouette preserved and brightest pixel stationary, steps progressively smoothing. Consistent with each transition band being feathered in place and summed, not global directional smearing.
- Our Distance-node experiments produced a field bright *outside* the staircase, which never matched observed behavior — consistent with the article's graph not using Distance.

## Anti-aliasing note from the article

The article flags that SDF-thresholded shadows have aliasing ("SDF纹理锯齿") and leaves it as future work, linking to Drew Cassidy's "SDF Antialiasing" (https://drewcassidy.me/2020/06/26/sdf-antialiasing/). Relevant for the Painter plugin's preview path.

## Implementation implications for the Python plugin

If we're replicating this in code (NumPy / compute shader / Substance API):

1. For each adjacent pair `(i, i+1)`, compute `sub[i] = clamp(mask[i] − mask[i+1], 0, 1)`. Produces `N−1` bands.
2. For each pair `i`, compute `feathered[i] = non_uniform_blur(mask[i], blur_map=sub[i], intensity=I, samples=16)` where `non_uniform_blur` is a per-pixel Gaussian whose radius scales with the blur map value.
3. Final output = `clamp(sum(feathered[0..N-2]), 0, 1) · (1/N)` — Linear-Dodge sum of the N−1 transitions, normalized by 1/N as per the article.
4. Optional threshold preview: `step(final, position)` for a hard shadow at that angle, with AA per Cassidy.

The per-pixel variable-radius blur is the only non-trivial kernel to port; everything else is arithmetic.

## Parameters the `.sbsar` exposes that map to this graph

From `FaceShadowBlend.xml`:
- 11 grayscale inputs → the Bitmap column (N=11 in our variant, not 8)
- `Blur_Intensity` → NUB Intensity (shared across all NUB nodes)
- `Blur_Samples` → NUB Samples
- `Blur_Blades` → NUB Blades
- `Test_Output` → Histogram Scan Position
- `FaceShadowOutput` → final averaged gradient
- `TestOutput` → Histogram Scan result

Copy-blend normalization opacity is fixed at `1/N` inside the compiled graph (not exposed); for our 11-input variant that is `1/11 ≈ 0.0909`.

## Open questions / verifications remaining

- Confirm which bitmap each per-pair NUB feeds into its Grayscale input (`bitmap[i]` vs `bitmap[i+1]`) and which subtract band is the Blur Map. Needs SD graph inspection.
- Confirm NUB `Anisotropy`, `Asymmetry`, `Angle`, `Blades`, `Samples` defaults from `FaceShadowBlend.xml` — the previous screenshot-derived values (0/0/0/5/16, Intensity≈11.69) are unverified.
- Confirm the exact Combine-stage topology: Linear-Dodge sum then single 1/N Copy-blend, vs. a chain of Copy-blends at 1/N, vs. some mixed progressive accumulation. The "2–8 bitmaps → output channels 1–7" statement hints at a progressive chain with intermediate taps.
- Confirm the mask ordering convention (smallest coverage → largest, or the reverse) in our `.sbsar` vs. the article's.

## Source
Heee, "卡通渲染流程【番外-使用SD批量生成面部SDF贴图】", Zhihu, 2022-07-27. Local archive in the project folder.
