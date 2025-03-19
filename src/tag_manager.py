import os
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QListWidget, QListWidgetItem,
                           QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal

class TagManager(QWidget):
    tag_selected = pyqtSignal(str)
    
    def __init__(self, data_dir):
        super().__init__()
        self.data_dir = data_dir
        self.tags_file = os.path.join(data_dir, ".tags.json")
        self.file_tags = {}
        self.all_tags = set()
        
        self.layout = QVBoxLayout(self)
        
        # 标题
        self.title = QLabel("标签管理")
        self.layout.addWidget(self.title)
        
        # 添加标签区域
        self.add_tag_layout = QHBoxLayout()
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("新标签...")
        self.tag_input.returnPressed.connect(self.add_tag)
        self.add_btn = QPushButton("添加")
        self.add_btn.clicked.connect(self.add_tag)
        
        self.add_tag_layout.addWidget(self.tag_input)
        self.add_tag_layout.addWidget(self.add_btn)
        
        self.layout.addLayout(self.add_tag_layout)
        
        # 标签列表
        self.tags_list = QListWidget()
        self.tags_list.itemClicked.connect(self.on_tag_selected)
        self.tags_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tags_list.customContextMenuRequested.connect(self.show_tag_context_menu)
        
        self.layout.addWidget(self.tags_list)
        
        # 当前文件标签
        self.current_file_label = QLabel("当前文件标签:")
        self.layout.addWidget(self.current_file_label)
        
        self.current_file_tags = QListWidget()
        self.current_file_tags.setMaximumHeight(100)
        self.layout.addWidget(self.current_file_tags)
        
        # 加载标签数据
        self.load_tags()
    
    def load_tags(self):
        if os.path.exists(self.tags_file):
            try:
                with open(self.tags_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.file_tags = data.get("file_tags", {})
                    
                    # 提取所有标签
                    self.all_tags = set()
                    for tags in self.file_tags.values():
                        self.all_tags.update(tags)
                    
                    # 更新标签列表
                    self.update_tags_list()
            except Exception as e:
                QMessageBox.warning(self, "加载标签失败", f"无法加载标签数据: {str(e)}")
    
    def save_tags(self):
        try:
            data = {
                "file_tags": self.file_tags
            }
            with open(self.tags_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "保存标签失败", f"无法保存标签数据: {str(e)}")
    
    def update_tags_list(self):
        self.tags_list.clear()
        for tag in sorted(self.all_tags):
            item = QListWidgetItem(tag)
            self.tags_list.addItem(item)
    
    def update_current_file_tags(self, file_path):
        self.current_file_tags.clear()
        if file_path in self.file_tags:
            for tag in sorted(self.file_tags[file_path]):
                item = QListWidgetItem(tag)
                self.current_file_tags.addItem(item)
    
    def add_tag(self):
        tag = self.tag_input.text().strip()
        if tag:
            self.all_tags.add(tag)
            self.update_tags_list()
            self.tag_input.clear()
            self.save_tags()
    
    def add_tag_to_file(self, file_path, tag):
        if file_path not in self.file_tags:
            self.file_tags[file_path] = []
        
        if tag not in self.file_tags[file_path]:
            self.file_tags[file_path].append(tag)
            self.update_current_file_tags(file_path)
            self.save_tags()
    
    def remove_tag_from_file(self, file_path, tag):
        if file_path in self.file_tags and tag in self.file_tags[file_path]:
            self.file_tags[file_path].remove(tag)
            self.update_current_file_tags(file_path)
            self.save_tags()
    
    def on_tag_selected(self, item):
        tag = item.text()
        self.tag_selected.emit(tag)
    
    def show_tag_context_menu(self, position):
        from PyQt5.QtWidgets import QMenu, QAction
        
        item = self.tags_list.itemAt(position)
        if not item:
            return
        
        tag = item.text()
        
        menu = QMenu()
        
        rename_action = QAction("重命名", self)
        rename_action.triggered.connect(lambda: self.rename_tag(tag))
        menu.addAction(rename_action)
        
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self.delete_tag(tag))
        menu.addAction(delete_action)
        
        menu.exec_(self.tags_list.viewport().mapToGlobal(position))
    
    def rename_tag(self, old_tag):
        new_tag, ok = QInputDialog.getText(self, "重命名标签", "新标签名:", text=old_tag)
        
        if ok and new_tag and new_tag != old_tag:
            # 更新所有文件中的标签
            for file_path, tags in self.file_tags.items():
                if old_tag in tags:
                    tags.remove(old_tag)
                    tags.append(new_tag)
            
            # 更新标签集合
            self.all_tags.remove(old_tag)
            self.all_tags.add(new_tag)
            
            # 更新界面
            self.update_tags_list()
            self.save_tags()
    
    def delete_tag(self, tag):
        reply = QMessageBox.question(self, "确认删除", 
                                   f"确定要删除标签 '{tag}' 吗?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 从所有文件中移除该标签
            for file_path, tags in self.file_tags.items():
                if tag in tags:
                    tags.remove(tag)
            
            # 从标签集合中移除
            self.all_tags.remove(tag)
            
            # 更新界面
            self.update_tags_list()
            self.save_tags()
    
    def get_files_by_tag(self, tag):
        """返回包含指定标签的所有文件路径"""
        files = []
        for file_path, tags in self.file_tags.items():
            if tag in tags:
                files.append(file_path)
        return files