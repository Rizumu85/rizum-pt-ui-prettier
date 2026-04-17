from PySide6 import QtWidgets
from PySide6.QtGui import QAction
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QDialog
import substance_painter.logging as logging
import substance_painter.ui as sp_ui

from .ui import SettingsDialog

class RizumDragDistanceSettings:
    def __init__(self):
        self.menu = None
        self.current_action = None
        self.settings_action = None
        
        # 启动时应用设置
        self.apply_current_settings()
        self.setup_menu()
    
    def setup_menu(self):
        """使用 Painter 原生 API 设置菜单"""
        # 与 painter_plugins_ui.PluginsMenu 一致：带主窗口父级，且 add_menu() 只接受 QMenu，不能传标题字符串
        main = sp_ui.get_main_window()
        self.menu = QtWidgets.QMenu("Rizum Drag Distance", main)
        self.menu.setObjectName("rizum_drag_distance_settings_menu")
        
        # 2. 创建并添加“当前值”展示项
        self.current_action = QAction("Current: 15 pixels", self.menu)
        self.current_action.setEnabled(False) 
        self.menu.addAction(self.current_action)  # 直接使用 Qt 的 addAction
        
        # 3. 创建并添加“设置”点击项
        self.settings_action = QAction("Drag Distance Settings...", self.menu)
        self.settings_action.triggered.connect(self.open_settings)
        self.menu.addAction(self.settings_action)
        
        # 4. 最后把组装好的菜单对象，交给 Painter 添加到顶部菜单栏
        sp_ui.add_menu(self.menu)
        
        # 确保初始显示的文字是正确的
        self.update_current_action_text()
    
    def get_current_drag_distance(self):
        return QtWidgets.QApplication.startDragDistance()
    
    def apply_current_settings(self):
        """将拖拽距离应用到 QApplication"""
        settings = QSettings("RizumDragDistance", "Settings")
        drag_distance = settings.value("drag_distance", 15, type=int)
        
        QtWidgets.QApplication.setStartDragDistance(drag_distance)
        logging.info(f"Drag distance set to {drag_distance} pixels")
        self.update_current_action_text()
    
    def update_current_action_text(self):
        """更新菜单中显示的当前数值"""
        current_distance = self.get_current_drag_distance()
        if self.current_action is not None:
            self.current_action.setText(f"Current: {current_distance} pixels")
    
    def open_settings(self):
        """打开设置界面"""
        dialog = SettingsDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog.save_settings()
            self.apply_current_settings()