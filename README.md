# Rizum PT UI Prettier

Shared PySide6 UI helpers for Rizum Substance 3D Painter plugins.

## What This Is

This folder is the source of the UI kit shared by the Rizum Painter plugins. It is not a Painter plugin itself: every `rizum-pt-*` plugin beside it holds its own copy of `rizum_ui/` and `icons/`, written by `tools/sync_vendor.py`.

It provides theme tokens, a generated Qt stylesheet, reusable widget factories, the mechanisms every plugin shares (Painter languages, the exit guard, shortcut conflicts), and a standalone preview app. The rules a plugin follows are in `docs/integration.md`.

## Preview

Run this from the `rizum-pt-ui-prettier` folder:

```powershell
python preview.py
```

This starts a no-Painter preview with a Painter-like dark Qt baseline plus the Rizum overlay stylesheet. It watches `rizum_ui/*.py` and refreshes the preview automatically when you save changes.

The external preview is intentionally approximate. It is good for fast layout and component iteration, but Painter's real palette, font metrics, embedded dock behavior, and host styles can differ.

To keep the preview open but disable auto-refresh:

```powershell
python preview.py --no-watch
```

To preview the full override stylesheet:

```powershell
python preview.py --full
```

To compare the live preview against browser screenshots at 1x scale:

```powershell
python preview.py --scale-1x
```

Use `--scale-1x` only for external visual debugging. Painter should keep its normal Qt DPI behavior.

The browser-based visual diff helpers use Playwright. Install the local Node dependencies before running those tools:

```powershell
npm install
```

You can keep Substance 3D Painter open while this preview runs. The preview is a separate Python process, so iterating on `theme.py`, `stylesheet.py`, or `components.py` does not require Painter or a Painter plugin reload. Changes to `preview.py` itself still require restarting the preview process.

The standalone preview uses a fixed Painter-like host baseline instead of reading a palette exported from Painter. Use live Painter checks only as final visual validation before vendoring the shared UI kit into a plugin.

If your normal Python does not have PySide6, run the preview from an environment that does:

```powershell
python -m pip install PySide6
python preview.py
```

Substance Painter includes PySide6 in its plugin runtime, so missing PySide6 in system Python does not mean the Painter plugin path is blocked.

## Vendor Into The Plugins

Use this repository as the upstream preview/component lab. After a component pass is approved in live Painter, sync the snapshot into the plugins; a plugin imports its own copy (`from .rizum_ui import ...`), so users install nothing but the plugin.

Preview the copy operation, then apply it:

```powershell
python tools/sync_vendor.py
python tools/sync_vendor.py --apply
```

Without `--target` this covers every sibling `rizum-pt-*` folder that already has a `rizum_ui_vendor_manifest.json`, except the ones whose manifest is pinned (`"pinned": "<reason>"`); those are printed as skipped.

Apply it to one plugin folder, a new or a pinned one included:

```powershell
python tools/sync_vendor.py --target ..\rizum-pt-to-ps-bridge --apply
```

The sync copies only `rizum_ui/*.py` and `icons/*.svg`, then writes `rizum_ui_vendor_manifest.json` into the target plugin. Stale files are kept by default; pass `--delete-stale` with `--apply` only when you want to remove files that were listed in a previous manifest but are no longer part of the shared snapshot.

## Directory Map

- `rizum_ui/` and `icons/`: the reusable PySide6 component package and shared SVG assets.
- `preview.py`: the standalone component preview app.
- `tools/`: visual comparison and vendoring utilities.
- `docs/`: project notes, integration guidance, and design rationale.
- `references/html/` and `references/media/`: source mockups and animation references used while matching the UI.
- `tmp/` and `visual-diff/`: generated local screenshots; ignored and safe to regenerate.
