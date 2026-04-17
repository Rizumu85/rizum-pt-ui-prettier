from substance_painter import ui, logging
from .plugin import RizumDragDistanceSettings

rizum_drag_distance_plugin = None

def start_plugin():
    """Substance Painter 启动插件时调用"""
    global rizum_drag_distance_plugin
    
    # 防止重复加载，先清理存在的实例
    if rizum_drag_distance_plugin is not None:
        close_plugin()
    
    # 实例化我们的核心类
    rizum_drag_distance_plugin = RizumDragDistanceSettings()
    
    return rizum_drag_distance_plugin

def close_plugin():
    """Substance Painter 关闭插件时调用"""
    global rizum_drag_distance_plugin
    
    # 清理我们在 core.py 中创建的原生 UI 菜单
    if rizum_drag_distance_plugin is not None:
        if rizum_drag_distance_plugin.menu:
            try:
                # 使用 Painter 的 API 删掉整个菜单
                ui.delete_ui_element(rizum_drag_distance_plugin.menu)
            except Exception as e:
                logging.warning(f"Error deleting menu: {e}")
                
        rizum_drag_distance_plugin = None