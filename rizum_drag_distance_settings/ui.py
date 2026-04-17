from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDialogButtonBox
from PySide6.QtCore import QSettings

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Drag Distance Settings")
        self.setModal(True)
        self.resize(240, 100)
        
        # 创建布局
        layout = QVBoxLayout()
        spin_layout = QHBoxLayout()
        
        # 创建控件
        label = QLabel("Drag Distance:")
        self.spin_box = QSpinBox()
        self.spin_box.setRange(1, 100)
        self.spin_box.setValue(15)
        pixels_label = QLabel("pixels")
        
        # 排版
        spin_layout.addWidget(label)
        spin_layout.addStretch()
        spin_layout.addWidget(self.spin_box)
        spin_layout.addWidget(pixels_label)
        layout.addLayout(spin_layout)
        
        # 对话框按钮 (OK / Cancel)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.load_settings()
    
    def load_settings(self):
        """从本地加载设置"""
        settings = QSettings("RizumDragDistance", "Settings")
        drag_distance = settings.value("drag_distance", 15, type=int)
        self.spin_box.setValue(drag_distance)
    
    def save_settings(self):
        """保存设置到本地"""
        settings = QSettings("RizumDragDistance", "Settings")
        settings.setValue("drag_distance", self.spin_box.value())
    
    def get_drag_distance(self):
        return self.spin_box.value()