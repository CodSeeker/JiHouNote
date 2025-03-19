import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile, QTextStream
from main_window import MainWindow

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容PyInstaller打包后的情况"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的路径
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境下的路径
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), relative_path)

def load_stylesheet(app):
    """加载应用程序样式表"""
    style_file = get_resource_path(os.path.join("resources", "style.qss"))
    
    if os.path.exists(style_file):
        print(f"找到样式表文件: {style_file}")
        file = QFile(style_file)
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        style_content = stream.readAll()
        app.setStyleSheet(style_content)
        print("样式表已加载")
    else:
        print(f"样式表文件不存在: {style_file}")

def ensure_directories():
    """确保必要的目录存在"""
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    resources_dir = os.path.join(app_dir, "resources")
    
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)

if __name__ == "__main__":
    # 确保必要的目录存在
    ensure_directories()
    
    app = QApplication(sys.argv)
    
    # 加载样式表
    load_stylesheet(app)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())