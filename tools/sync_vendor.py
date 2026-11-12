"""Vendor the approved UI-kit snapshot into shareable plugin folders.

The script is intentionally conservative:

- dry-run by default;
- only copies the shared `rizum_ui` package and shared SVG icons;
- only deletes stale files when `--delete-stale` is passed and the stale file was
  recorded in a previous vendor manifest.

Without `--target` it syncs every sibling `rizum-pt-*` folder that already has
a vendor manifest. A manifest with `"pinned": "<reason>"` keeps its plugin out
of that set: the plugin holds its own edits or a deliberate older snapshot, and
is synced only when named with `--target`.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PATTERN = "rizum-pt-*"
MANIFEST_NAME = "rizum_ui_vendor_manifest.json"
MANAGED_ROOTS = ("rizum_ui", "icons")


@dataclass(frozen=True)
class VendorFile:
    source: Path
    relative: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy the shared Rizum UI kit into self-contained plugin folders.",
    )
    parser.add_argument(
        "--target",
        action="append",
        type=Path,
        help=(
            "Target plugin folder. May be passed more than once. "
            "Defaults to every sibling plugin with a vendor manifest that is "
            "not pinned."
        ),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually copy files. Without this flag the command only prints a dry-run.",
    )
    parser.add_argument(
        "--delete-stale",
        action="store_true",
        help="Delete stale files that were listed in a previous vendor manifest.",
    )
    return parser.parse_args()


def iter_vendor_files() -> list[VendorFile]:
    files: list[VendorFile] = []
    for root_name in MANAGED_ROOTS:
        root = ROOT / root_name
        for source in sorted(root.rglob("*")):
            if not source.is_file():
                continue
            if "__pycache__" in source.parts or source.suffix == ".pyc":
                continue
            if root_name == "rizum_ui" and source.suffix != ".py":
                continue
            if root_name == "icons" and source.suffix.lower() != ".svg":
                continue
            files.append(VendorFile(source=source, relative=source.relative_to(ROOT)))
    return files


def content(path: Path) -> bytes:
    # Compared without regard to line endings: each repository checks its
    # files out with its own, and raw bytes reported unchanged files as
    # updates on every run.
    return path.read_bytes().replace(b"\r\n", b"\n")


def git_value(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return "unknown"
    return result.stdout.strip()


def default_targets(plugins: Path) -> tuple[list[Path], list[tuple[Path, str]]]:
    """Plugins in ``plugins`` to sync, and the pinned ones with their reason."""
    targets: list[Path] = []
    pinned: list[tuple[Path, str]] = []
    for folder in sorted(plugins.glob(PLUGIN_PATTERN)):
        if not (folder / MANIFEST_NAME).is_file():
            continue
        reason = load_previous_manifest(folder).get("pinned")
        if reason:
            pinned.append((folder, str(reason)))
        else:
            targets.append(folder)
    return targets, pinned


def ensure_inside_target(target: Path, candidate: Path) -> Path:
    resolved_target = target.resolve()
    resolved_candidate = candidate.resolve()
    if resolved_candidate == resolved_target:
        return resolved_candidate
    if resolved_target not in resolved_candidate.parents:
        raise RuntimeError(f"Refusing to touch path outside target: {resolved_candidate}")
    return resolved_candidate


def load_previous_manifest(target: Path) -> dict:
    manifest_path = target / MANIFEST_NAME
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def stale_files(target: Path, next_relatives: set[str]) -> list[Path]:
    previous = load_previous_manifest(target)
    stale: list[Path] = []
    for relative in previous.get("files", []):
        if relative in next_relatives:
            continue
        candidate = ensure_inside_target(target, target / relative)
        if candidate.exists() and candidate.is_file():
            stale.append(candidate)
    return stale


def write_manifest(target: Path, files: list[VendorFile]) -> None:
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        # Name only: an absolute path would publish the local folder layout.
        "source_root": ROOT.name,
        "source_git_head": git_value("rev-parse", "--short", "HEAD"),
        "source_git_status": git_value(
            "status", "--short", "--", *MANAGED_ROOTS
        ),
        "managed_roots": list(MANAGED_ROOTS),
        "files": [file.relative.as_posix() for file in files],
    }
    pinned = load_previous_manifest(target).get("pinned")
    if pinned:
        # A sync by name does not lift the pin; only editing the manifest does.
        manifest["pinned"] = pinned
    manifest_path = target / MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def sync_target(target: Path, files: list[VendorFile], apply: bool, delete_stale: bool) -> None:
    if not target.exists() or not target.is_dir():
        raise RuntimeError(f"Target plugin folder does not exist: {target}")

    next_relatives = {file.relative.as_posix() for file in files}
    copied = updated = unchanged = 0

    print(f"\nTarget: {target}")
    for file in files:
        destination = ensure_inside_target(target, target / file.relative)
        if destination.exists() and destination.is_file():
            if content(file.source) == content(destination):
                unchanged += 1
                status = "same"
            else:
                updated += 1
                status = "update"
        else:
            copied += 1
            status = "new"

        print(f"  {status:6} {file.relative.as_posix()}")
        if apply and status != "same":
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file.source, destination)

    stale = stale_files(target, next_relatives)
    for path in stale:
        print(f"  stale  {path.relative_to(target).as_posix()}")
        if apply and delete_stale:
            path.unlink()

    if apply:
        write_manifest(target, files)
        action = "synced"
    else:
        action = "dry-run"

    stale_note = f", stale={len(stale)}"
    if stale and not delete_stale:
        stale_note += " (kept; pass --delete-stale to remove)"
    print(
        f"  {action}: new={copied}, update={updated}, same={unchanged}{stale_note}"
    )


def main() -> int:
    args = parse_args()
    files = iter_vendor_files()
    if args.target:
        targets, pinned = [path.resolve() for path in args.target], []
    else:
        targets, pinned = default_targets(ROOT.parent)
    if not targets:
        raise SystemExit("No target plugin folders found. Pass --target PATH.")

    print(f"Source: {ROOT}")
    print(f"Mode: {'apply' if args.apply else 'dry-run'}")
    print(f"Files: {len(files)}")

    for target in targets:
        sync_target(target, files, args.apply, args.delete_stale)
    for target, reason in pinned:
        print(f"\nSkipped (pinned): {target}\n  {reason}")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to copy files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
