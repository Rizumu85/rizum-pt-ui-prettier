import os
import shutil
import subprocess

import substance_painter as sp

from .sdf_external import _add_temp_baseline
from .sdf_layer_setup import USER0, _find_sdf_group


def _build_bake_export_config(texture_set_name: str, export_dir: str, out_name: str):
    return {
        "exportPath": export_dir,
        "exportShaderParams": False,
        "defaultExportPreset": "bake_frame",
        "exportPresets": [{
            "name": "bake_frame",
            "maps": [{
                "fileName": out_name,
                "channels": [{
                    "destChannel": "L",
                    "srcChannel": "R",
                    "srcMapType": "documentMap",
                    "srcMapName": "user0",
                }],
                "parameters": {
                    "fileFormat": "png",
                    "bitDepth": "8",
                },
            }],
        }],
        "exportList": [{"rootPath": texture_set_name}],
        "exportParameters": [{
            "parameters": {
                "dithering": False,
                "paddingAlgorithm": "transparent",
                "dilationDistance": 16,
            },
        }],
    }


def export_all_frames(
    group_node,
    texture_set_name: str,
    export_dir: str,
    on_progress=None,
) -> list[str]:
    """Export each SDF frame as a binary PNG in canonical broad->narrow order."""
    # sub_layers() is top-to-bottom, so reverse to keep the canonical bake order:
    # bottom broad frame first (Frame_01), narrower frames later.
    frame_layers = list(reversed(group_node.sub_layers()))
    total = len(frame_layers)
    original_values = {
        layer.uid(): layer.get_source(USER0).get_color()
        for layer in frame_layers
    }
    original_visibility = {
        layer.uid(): layer.is_visible()
        for layer in frame_layers
    }
    temp_baseline = None
    frame_paths = []

    try:
        with sp.layerstack.ScopedModification("SDF Bake Export Setup"):
            temp_baseline = _add_temp_baseline(group_node)
            for layer in frame_layers:
                layer.set_visible(False)

        for index, layer in enumerate(frame_layers, start=1):
            if on_progress is not None:
                on_progress("Exporting frames", index, total)
            out_name = f"sdf_frame_{index:02d}"
            out_path = os.path.join(export_dir, f"{out_name}.png")

            with sp.layerstack.ScopedModification("SDF Bake Export Frame"):
                layer.set_visible(True)
                layer.set_source(USER0, sp.colormanagement.Color(1.0, 1.0, 1.0))

            config = _build_bake_export_config(texture_set_name, export_dir, out_name)
            sp.export.export_project_textures(config)
            frame_paths.append(out_path)

            with sp.layerstack.ScopedModification("SDF Bake Export Restore Frame"):
                layer.set_source(USER0, original_values[layer.uid()])
                layer.set_visible(False)
    finally:
        with sp.layerstack.ScopedModification("SDF Bake Export Cleanup"):
            for layer in frame_layers:
                layer.set_source(USER0, original_values[layer.uid()])
                layer.set_visible(original_visibility[layer.uid()])
            if temp_baseline is not None:
                sp.layerstack.delete_node(temp_baseline)

    return frame_paths


def find_python_with_deps() -> str | None:
    """Find a system Python that can import numpy and cv2."""
    for command in ["python", "python3", "py"]:
        python_exe = shutil.which(command)
        if not python_exe:
            continue
        try:
            result = subprocess.run(
                [python_exe, "-c", "import numpy, cv2"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if result.returncode == 0:
            return python_exe
    return None


def run_sdf_tool(
    python_exe: str,
    frame_dir: str,
    output_dir: str,
    output_name: str = "sdf_baked",
    filter_mode: str = "gaussian",
    bit_depth: int = 16,
    on_progress=None,
) -> str:
    """Run the bundled SDF interpolation tool and return the baked PNG path."""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_name + ".png")
    if os.path.exists(output_path):
        os.remove(output_path)

    if on_progress is not None:
        on_progress("Running SDF tool", 0, 1)

    run_script = os.path.join(
        os.path.dirname(__file__),
        "sdf_shadow_threshold_map-main",
        "run.py",
    )
    result = subprocess.run(
        [
            python_exe,
            run_script,
            "-i",
            frame_dir,
            "-o",
            output_dir,
            "-n",
            output_name,
            "-b",
            str(bit_depth),
            "-c",
            "gray",
            "-f",
            filter_mode,
            "-r",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        details = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"SDF tool failed: {details}")
    if on_progress is not None:
        on_progress("Running SDF tool", 1, 1)
    return output_path


def reimport_baked_sdf(baked_path: str, on_progress=None):
    """Import the baked SDF PNG and assign it to a result fill layer in User0."""
    if on_progress is not None:
        on_progress("Importing baked result", 0, 1)
    resource = sp.resource.import_session_resource(
        baked_path,
        sp.resource.Usage.TEXTURE,
        name="SDF_Baked",
    )
    resource_id = resource.identifier()

    stack = sp.textureset.get_active_stack()
    root_nodes = sp.layerstack.get_root_layer_nodes(stack)
    result_layer = next(
        (node for node in root_nodes if node.get_name() == "SDF_Baked_Result"),
        None,
    )

    with sp.layerstack.ScopedModification("Import SDF Baked Result"):
        if result_layer is None:
            pos = sp.layerstack.InsertPosition.from_textureset_stack(stack)
            result_layer = sp.layerstack.insert_fill(pos)
            result_layer.set_name("SDF_Baked_Result")
            result_layer.active_channels = {USER0}
        result_layer.set_source(USER0, resource_id)
    if on_progress is not None:
        on_progress("Importing baked result", 1, 1)


def _resolve_bake_debug_dir() -> str:
    """Pick a persistent folder for the bake's intermediate frames and output.

    Uses the saved project's directory if available, otherwise the user's
    Documents folder. Artists can inspect `frames/*.png` and `sdf_baked.png`
    after a bake to diagnose issues.
    """
    project_path = None
    try:
        project_path = sp.project.file_path()
    except Exception:
        project_path = None
    if project_path:
        base = os.path.dirname(project_path)
    else:
        base = os.path.join(os.path.expanduser("~"), "Documents")
    debug_dir = os.path.join(base, "sdf_bake_debug")
    frames_dir = os.path.join(debug_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    return debug_dir


def bake_sdf(on_progress=None) -> str:
    """Run the validated bake flow and import the result into Painter.

    Intermediate frames and the baked PNG are written to a persistent
    `sdf_bake_debug/` folder next to the project so they can be inspected.
    """
    group = _find_sdf_group()
    if group is None:
        raise RuntimeError("SDF_Generator group not found. Run Setup first.")

    stack = sp.textureset.get_active_stack()
    texture_set = stack.material()
    texture_set_name = (
        texture_set.name() if callable(texture_set.name) else texture_set.name
    )

    python_exe = find_python_with_deps()
    if python_exe is None:
        raise RuntimeError("No system Python with numpy and cv2 was found on PATH.")

    debug_dir = _resolve_bake_debug_dir()
    frames_dir = os.path.join(debug_dir, "frames")
    # Wipe stale frames from the prior bake so leftover PNGs don't feed the tool.
    for name in os.listdir(frames_dir):
        if name.lower().endswith(".png"):
            try:
                os.remove(os.path.join(frames_dir, name))
            except OSError:
                pass

    export_all_frames(group, texture_set_name, frames_dir, on_progress=on_progress)
    baked_path = run_sdf_tool(
        python_exe,
        frames_dir,
        debug_dir,
        output_name="sdf_baked",
        filter_mode="gaussian",
        bit_depth=16,
        on_progress=on_progress,
    )
    reimport_baked_sdf(baked_path, on_progress=on_progress)
    if on_progress is not None:
        on_progress("Done", 1, 1)
    sp.logging.info(f"SDF bake artifacts saved to: {debug_dir}")
    return baked_path
