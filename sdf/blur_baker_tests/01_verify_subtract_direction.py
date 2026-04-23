"""
Step 1: Verify the subtract direction used by FaceShadowBlend's ring masks.

Loads one adjacent pair from the example resources and writes:
- a.png, b.png      : the two source frames (so we can see which is broader)
- a_minus_b.png     : np.clip(a - b, 0, 255)
- b_minus_a.png     : np.clip(b - a, 0, 255)

The "ring" mask should be a thin band — whichever direction produces that band
matches Substance's subtract semantics for this graph (dest - src clamped).
"""
import os
import cv2
import numpy as np

SRC = r"C:\Downloads\卡通渲染流程【番外-SDF】\SDFFaceLightMap\SDFFaceLightMap.resources"
OUT = os.path.dirname(os.path.abspath(__file__))


def imread_unicode(path, flags=cv2.IMREAD_GRAYSCALE):
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, flags)


def imwrite_unicode(path, img):
    ext = os.path.splitext(path)[1]
    ok, buf = cv2.imencode(ext, img)
    if ok:
        buf.tofile(path)


a = imread_unicode(os.path.join(SRC, "XXXXXX-a.png"))
b = imread_unicode(os.path.join(SRC, "XXXXXX-b-1.png"))

assert a is not None and b is not None, "Failed to load source PNGs"
print(f"a shape={a.shape} dtype={a.dtype} mean={a.mean():.2f} white_px={(a > 127).sum()}")
print(f"b shape={b.shape} dtype={b.dtype} mean={b.mean():.2f} white_px={(b > 127).sum()}")

ai = a.astype(np.int16)
bi = b.astype(np.int16)
a_minus_b = np.clip(ai - bi, 0, 255).astype(np.uint8)
b_minus_a = np.clip(bi - ai, 0, 255).astype(np.uint8)

imwrite_unicode(os.path.join(OUT, "a.png"), a)
imwrite_unicode(os.path.join(OUT, "b.png"), b)
imwrite_unicode(os.path.join(OUT, "a_minus_b.png"), a_minus_b)
imwrite_unicode(os.path.join(OUT, "b_minus_a.png"), b_minus_a)

print(f"a-b nonzero px = {(a_minus_b > 0).sum()}")
print(f"b-a nonzero px = {(b_minus_a > 0).sum()}")
print(f"Wrote outputs to: {OUT}")
