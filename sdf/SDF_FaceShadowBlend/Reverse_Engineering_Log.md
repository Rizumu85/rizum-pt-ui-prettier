# Reverse_Engineering_Log.md (FINAL)

## Project Overview
- **File Name:** FaceShadowBlend.sbsar
- **Target Logic:** Multi-angle SDF face shadow interpolator.
- **Ultimate Goal:** Replicate the logic to build a real-time SDF generator/previewer via a Substance Painter Python plugin.

## Phase 1 & 2: Black-Box Analysis
- **Inputs:** Up to 11 discrete shadow masks representing different light angles.
- **Blending:** Additive (Linear Dodge). Stacking the masks creates a stepped "staircase" grayscale image.
- **Smoothing:** A blur kernel is applied to smear the distinct steps into a continuous gradient. 
- **Outputs:** 
  - `FaceShadowOutput`: The final baked gradient ramp.
  - `TestOutput`: A thresholded preview of the shadow at a specific time/angle.

## Phase 3 & 4: Logic Translation & Node Mapping
The `.sbsar` can be perfectly recreated in Substance Designer (or via Painter's API) using the following node recipe:

### 1. The "Staircase" Generator
- **Nodes:** `Input Grayscale` -> `Blend`
- **Logic:** Add all active masks together using **Linear Dodge (Add)** blending. If using 11 masks, each mask contributes roughly `1/11` (or `0.09`) to the total opacity to create an evenly stepped 0-to-1 grayscale ramp.

### 2. The SDF Gradient (The "Glow")
- **Node:** `Distance`
- **Logic:** Feed the "Staircase" result into the `Source` of a `Distance` node. Set the Maximum Distance high (e.g., 256). This creates a gradient field radiating from the shadow edges.

### 3. The Smoothing Engine (The Secret Sauce)
- **Node:** `Non-Uniform Blur Grayscale`
- **Wiring:** 
  - Grayscale Input: The "Staircase" (`Blend` output).
  - Blur Map / Anisotropy Input: The SDF Gradient (`Distance` output).
- **Parameters Map:**
  - `Blur_Intensity` = node **Intensity**
  - `Blur_Samples` = node **Samples**
  - `Blur_Blades` = node **Blades** (Controls the shape/direction of the blur).
- **Result:** The jagged staircase is smeared precisely along the distance field, creating a flawless 3D-like shadow ramp.

### 4. The Angle Previewer (`TestOutput`)
- **Node:** `Histogram Scan` (or `Threshold`)
- **Logic:** Feed the output of the Non-Uniform Blur into this node. Map the `Position` parameter to a 0-1 slider (`Test_Output`). Setting `Contrast` to 1.0 gives you the sharp, hard-edged anime shadow preview for that specific light angle.
