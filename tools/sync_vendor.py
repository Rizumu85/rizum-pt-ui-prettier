"""Vendor the approved UI-kit snapshot into shareable plugin folders.

The script is intentionally conservative:

- dry-run by default;
- only copies the shared `rizum_ui` package and shared SVG icons;
- only deletes stale files when `--delete-stale` is passed and the stale file was
  recorded in a previous vendor manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGETS = (
    ROOT.parent / "rizum-pt-to-ps-bridge",
    ROOT.parent / "rizum-pt-ui-font",
)
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
            "Defaults to known sibling Rizum plugins."
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    return result.stdout.strip() or "unknown"


def target_paths(paths: list[Path] | None) -> list[Path]:
    if paths:
        return [path.resolve() for path in paths]
    return [path.resolve() for path in DEFAULT_TARGETS if path.exists()]


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
        "source_root": str(ROOT),
        "source_git_head": git_value("rev-parse", "--short", "HEAD"),
        "source_git_status": git_value("status", "--short"),
        "managed_roots": list(MANAGED_ROOTS),
        "files": [file.relative.as_posix() for file in files],
    }
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
            if sha256(file.source) == sha256(destination):
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
    targets = target_paths(args.target)
    if not targets:
        raise SystemExit("No target plugin folders found. Pass --target PATH.")

    print(f"Source: {ROOT}")
    print(f"Mode: {'apply' if args.apply else 'dry-run'}")
    print(f"Files: {len(files)}")

    for target in targets:
        sync_target(target, files, args.apply, args.delete_stale)

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to copy files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
