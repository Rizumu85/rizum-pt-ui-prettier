"""Rizum Time Tracker for Substance 3D Painter."""
_plugin = None


def start_plugin():
    global _plugin
    close_plugin()
    from .plugin import Plugin
    _plugin = Plugin()


def close_plugin():
    global _plugin
    if _plugin is not None:
        _plugin.close()
        _plugin = None
