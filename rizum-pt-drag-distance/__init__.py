from __future__ import annotations

from substance_painter import logging, ui

from .plugin import RizumDragDistanceSettings


rizum_drag_distance_plugin = None


def start_plugin():
    global rizum_drag_distance_plugin

    if rizum_drag_distance_plugin is not None:
        close_plugin()

    rizum_drag_distance_plugin = RizumDragDistanceSettings()
    return rizum_drag_distance_plugin


def close_plugin() -> None:
    global rizum_drag_distance_plugin

    if rizum_drag_distance_plugin is None:
        return

    if rizum_drag_distance_plugin.menu:
        try:
            ui.delete_ui_element(rizum_drag_distance_plugin.menu)
        except Exception as error:
            logging.warning(f"Error deleting Drag Distance menu: {error}")

    rizum_drag_distance_plugin = None
