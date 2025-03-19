from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QLabel, QListWidgetItem
from PyQt5.QtCore import Qt
import os

class SearchWidget(QWidget):
    # 添加file_clicked信号
    file_clicked = pyqtSignal(str)
    
    def __init__(self, data_dir):
        super().__init__()
        self.data_dir = data_dir
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 搜索框和按钮
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入搜索关键词...")
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.search_files)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        
        # 结果列表
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        layout.addLayout(search_layout)
        layout.addWidget(QLabel("搜索结果:"))
        layout.addWidget(self.results_list)
    
    def search_files(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            return
        
        self.results_list.clear()
        
        # 搜索文件内容
        for root, _, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith(('.txt', '.md')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if keyword.lower() in content.lower():
                                relative_path = os.path.relpath(file_path, self.data_dir)
                                item = QListWidgetItem(relative_path)
                                item.setData(Qt.UserRole, file_path)
                                self.results_list.addItem(item)
                    except Exception as e:
                        print(f"搜索文件时出错: {file_path}, 错误: {str(e)}")
    
    def on_item_double_clicked(self, item):
        file_path = item.data(Qt.UserRole)
        if file_path:
            # 发射信号通知主窗口打开文件
            self.file_clicked.emit(file_path)