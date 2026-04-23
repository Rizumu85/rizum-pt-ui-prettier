"""
Step 2: Approximate Substance Designer's `Non-Uniform Blur Grayscale` for one pair.

Source : XXXXXX-a (narrowest white)
Mask   : ring = clip(b - a, 0, 255)        # the band where the next-broader differs
Goal   : feather a's boundary OUTWARD into the ring zone, leave the rest untouched.

Approximation strategy:
- Compute a Gaussian-blurred version of the source with sigma proportional to intensity.
- Per-pixel lerp between original and blurred, weighted by the (normalized) ring mask.
  Inside the ring → blurred wins. Outside → original wins.

Intensity calibration is empirical for now; SD's "Intensity 38.38" is a relative number we
will calibrate against the .sbsar render later. We try a few sigmas and write all of them
so the user can pick the closest visual match.
"""
import os
import cv2
import numpy as np

SRC = r"C:\Downloads\卡通渲染流程【番外-SDF】\SDFFaceLightMap\SDFFaceLightMap.resources"
OUT = os.path.dirname(os.path.abspath(__file__))


def imread_unicode(path, flags=cv2.IMREAD_GRAYSCALE):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), flags)


def imwrite_unicode(path, img):
    ext = os.path.splitext(path)[1]
    ok, buf = cv2.imencode(ext, img)
    if ok:
        buf.tofile(path)


def non_uniform_blur(source: np.ndarray, mask: np.ndarray,
                     sigma_px: float) -> np.ndarray:
    """Blur source with sigma_px, then lerp original ↔ blurred by normalized mask."""
    src = source.astype(np.float32)
    msk = mask.astype(np.float32) / 255.0
    blurred = cv2.GaussianBlur(src, ksize=(0, 0), sigmaX=sigma_px)
    out = src * (1.0 - msk) + blurred * msk
    return np.clip(out, 0, 255).astype(np.uint8)


a = imread_unicode(os.path.join(SRC, "XXXXXX-a.png"))
b = imread_unicode(os.path.join(SRC, "XXXXXX-b-1.png"))
assert a is not None and b is not None

ring = np.clip(b.astype(np.int16) - a.astype(np.int16), 0, 255).astype(np.uint8)
imwrite_unicode(os.path.join(OUT, "step2_ring_b_minus_a.png"), ring)

# Try a few sigma values. SD's "Intensity 38.38" is unitless. For a 2048-px
# texture, plausible blur radii span ~5 px (subtle) to ~80 px (heavy). Sweep
# logarithmically so we can pick the closest match by eye.
for sigma_px in [4, 8, 16, 32, 64, 96]:
    out = non_uniform_blur(a, ring, sigma_px=sigma_px)
    name = f"step2_nub_a_sigma{sigma_px:03d}.png"
    imwrite_unicode(os.path.join(OUT, name), out)
    print(f"wrote {name} (sigma={sigma_px}px)")

print(f"\nAll outputs in: {OUT}")
print("Compare visually: each PNG should show `a`'s white blob with a soft "
      "outward feather contained within the ring band.")
