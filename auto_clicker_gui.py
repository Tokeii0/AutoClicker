import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QSpinBox, QFileDialog, QMessageBox)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QThread, Signal
import cv2
import numpy as np
from auto_clicker import AutoClicker

class ClickerThread(QThread):
    status_update = Signal(str)
    match_found = Signal(bool, tuple)
    
    def __init__(self, clicker):
        super().__init__()
        self.clicker = clicker
        self.running = False
        
    def run(self):
        self.running = True
        self.status_update.emit("自动点击器已启动...")
        
        try:
            while self.running:
                result = self.clicker.find_and_click()
                if result:
                    # 如果找到匹配，发出信号
                    self.match_found.emit(True, (0, 0))  # 这里可以传递实际的点击坐标
                self.msleep(int(self.clicker.interval * 1000))
        except Exception as e:
            self.status_update.emit(f"错误: {str(e)}")
        
        self.status_update.emit("自动点击器已停止")
    
    def stop(self):
        self.running = False

class AutoClickerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.template_path = ""
        self.clicker = None
        self.clicker_thread = None
        
        self.init_ui()
    
    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle("自动点击器")
        self.setMinimumSize(400, 400)
        
        # 创建中央部件和布局
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # 图片预览区域
        self.preview_label = QLabel("未选择图片")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("border: 1px solid #cccccc;")
        main_layout.addWidget(self.preview_label)
        
        # 间隔时间设置
        interval_layout = QHBoxLayout()
        interval_label = QLabel("点击间隔(秒):")
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 3600)
        self.interval_spinbox.setValue(30)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_spinbox)
        main_layout.addLayout(interval_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 导入图片按钮
        self.import_button = QPushButton("导入图片")
        self.import_button.clicked.connect(self.import_template)
        button_layout.addWidget(self.import_button)
        
        # 开始按钮
        self.start_button = QPushButton("开始")
        self.start_button.clicked.connect(self.start_clicker)
        self.start_button.setEnabled(False)  # 初始禁用
        button_layout.addWidget(self.start_button)
        
        # 停止按钮
        self.stop_button = QPushButton("停止")
        self.stop_button.clicked.connect(self.stop_clicker)
        self.stop_button.setEnabled(False)  # 初始禁用
        button_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(button_layout)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        main_layout.addWidget(self.status_label)
        
        self.setCentralWidget(central_widget)
    
    def import_template(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择模板图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            self.template_path = file_path
            
            # 显示预览图片
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # 调整图片大小以适应预览区域
                pixmap = pixmap.scaled(
                    self.preview_label.width(), 
                    self.preview_label.height(),
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.preview_label.setPixmap(pixmap)
                
                # 启用开始按钮
                self.start_button.setEnabled(True)
                self.status_label.setText(f"已加载模板图片: {os.path.basename(file_path)}")
            else:
                QMessageBox.warning(self, "错误", "无法加载所选图片")
    
    def start_clicker(self):
        if not self.template_path:
            QMessageBox.warning(self, "错误", "请先导入模板图片")
            return
        
        interval = self.interval_spinbox.value()
        
        try:
            # 创建自动点击器实例
            self.clicker = AutoClicker(self.template_path, interval)
            
            # 创建并启动线程
            self.clicker_thread = ClickerThread(self.clicker)
            self.clicker_thread.status_update.connect(self.update_status)
            self.clicker_thread.match_found.connect(self.on_match_found)
            self.clicker_thread.start()
            
            # 更新UI状态
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.import_button.setEnabled(False)
            self.interval_spinbox.setEnabled(False)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动自动点击器失败: {str(e)}")
    
    def stop_clicker(self):
        if self.clicker_thread and self.clicker_thread.isRunning():
            self.clicker_thread.stop()
            self.clicker_thread.wait()  # 等待线程结束
            
            # 更新UI状态
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.import_button.setEnabled(True)
            self.interval_spinbox.setEnabled(True)
    
    def update_status(self, message):
        self.status_label.setText(message)
    
    def on_match_found(self, found, position):
        # 可以在这里添加匹配成功的处理逻辑
        pass
    
    def closeEvent(self, event):
        # 关闭窗口时停止线程
        self.stop_clicker()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = AutoClickerGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()