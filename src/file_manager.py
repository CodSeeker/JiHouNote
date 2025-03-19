import os
import shutil
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeView, QMenu, QAction, QMessageBox, QFileDialog, QFileSystemModel, QInputDialog
from PyQt5.QtCore import Qt, pyqtSignal, QEvent, QModelIndex

class FileManager(QWidget):
    file_clicked = pyqtSignal(str)
    
    def __init__(self, data_dir):
        super().__init__()
        self.data_dir = data_dir
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 创建文件系统模型
        self.model = QFileSystemModel()
        self.model.setRootPath(self.data_dir)
        
        # 创建树形视图
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(self.data_dir))
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        
        # 隐藏额外的列，只显示文件名列
        for i in range(1, self.model.columnCount()):
            self.tree_view.hideColumn(i)
        
        # 设置文件名列宽度
        self.tree_view.setColumnWidth(0, 250)
        
        # 设置上下文菜单
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        
        # 单击事件处理
        self.tree_view.clicked.connect(self.on_item_clicked)
        
        # 添加鼠标按下事件处理，用于处理空白区域点击
        self.tree_view.viewport().installEventFilter(self)
        
        layout.addWidget(self.tree_view)

    def on_item_clicked(self, index):
        """处理单击事件"""
        if index.isValid():
            file_path = self.model.filePath(index)
            # 只有当点击的是文件时才打开
            if os.path.isfile(file_path):
                # 发射信号通知主窗口打开文件
                self.file_clicked.emit(file_path)
    
    def eventFilter(self, obj, event):
        if obj is self.tree_view.viewport():
            if event.type() == QEvent.MouseButtonPress:
                # 获取点击位置对应的索引
                index = self.tree_view.indexAt(event.pos())
                if not index.isValid():
                    # 如果点击的是空白区域，清除当前选择
                    self.tree_view.clearSelection()
                    self.tree_view.setCurrentIndex(QModelIndex())
                    return True  # 事件已处理
    
        # 对于其他事件，交给父类处理
        return super().eventFilter(obj, event)
    
    def on_tree_view_clicked(self, index):
        """处理树视图点击事件"""
        if index.isValid():
            file_path = self.model.filePath(index)
            file_info = QFileInfo(file_path)
            size_str = self.format_size(file_info.size())
            modified_str = file_info.lastModified().toString("yyyy-MM-dd hh:mm:ss")
            
            # 发射信号更新状态栏
            self.status_message.emit(f"文件: {file_path} | 大小: {size_str} | 修改时间: {modified_str}")
        else:
            # 如果点击的是空白区域，清除当前选择
            self.tree_view.clearSelection()
            self.tree_view.setCurrentIndex(QModelIndex())
            self.status_message.emit("")
    
    def format_size(self, size):
        """格式化文件大小显示"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.2f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size/(1024*1024):.2f} MB"
        else:
            return f"{size/(1024*1024*1024):.2f} GB"
    
    def on_double_click(self, index):
        """处理双击事件，打开文件"""
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            # 发射信号通知主窗口打开文件
            self.file_clicked.emit(file_path)
        
    def set_root_path(self, path):
        self.root_path = path
        self.model.setRootPath(path)
        self.tree_view.setRootIndex(self.model.index(path))
    
    def refresh(self):
        """刷新文件管理器视图"""
        # 保存当前选中的路径
        current_index = self.tree_view.currentIndex()
        current_path = self.model.filePath(current_index) if current_index.isValid() else None
        
        # 刷新模型
        self.model.setRootPath(self.data_dir)
        
        # 如果之前有选中的路径，尝试重新选中它
        if current_path and os.path.exists(current_path):
            new_index = self.model.index(current_path)
            if new_index.isValid():
                self.tree_view.setCurrentIndex(new_index)
    
    def on_file_clicked(self, index):
        file_path = self.model.filePath(index)
        
        if os.path.isfile(file_path):
            self.file_selected.emit(file_path)
    
    def show_context_menu(self, position):
        """显示上下文菜单"""
        index = self.tree_view.indexAt(position)
        menu = QMenu()
        
        # 添加新建文件和文件夹选项（无论是否选中项）
        new_file_action = QAction("新建文件", self)
        new_file_action.triggered.connect(self.create_new_file)
        menu.addAction(new_file_action)
        
        new_folder_action = QAction("新建文件夹", self)
        new_folder_action.triggered.connect(self.create_new_folder)
        menu.addAction(new_folder_action)
        
        # 如果点击在有效项上，添加复制和删除选项
        if index.isValid():
            menu.addSeparator()
            
            copy_action = QAction("复制", self)
            copy_action.triggered.connect(lambda: self.copy_item(index))
            menu.addAction(copy_action)
            
            delete_action = QAction("删除", self)
            delete_action.triggered.connect(lambda: self.delete_item(index))
            menu.addAction(delete_action)
        
        menu.exec_(self.tree_view.viewport().mapToGlobal(position))
    
    def create_new_folder(self):
        """创建新文件夹"""
        # 获取当前选中的目录
        index = self.tree_view.currentIndex()
        if index.isValid():
            path = self.model.filePath(index)
            # 如果选中的是文件，则使用其所在目录
            if not os.path.isdir(path):
                path = os.path.dirname(path)
        else:
            # 如果没有选中项，则使用根目录
            path = self.data_dir
        
        # 弹出对话框获取文件夹名称
        folder_name, ok = QInputDialog.getText(None, "新建文件夹", "请输入文件夹名称:")
        if ok and folder_name:
            folder_path = os.path.join(path, folder_name)
            try:
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    # 刷新文件管理器
                    self.refresh()
                    
                    # 展开父目录
                    parent_index = self.model.index(path)
                    self.tree_view.expand(parent_index)
                    
                    # 选中新文件夹
                    new_folder_index = self.model.index(folder_path)
                    self.tree_view.setCurrentIndex(new_folder_index)
                else:
                    QMessageBox.warning(None, "警告", f"文件夹 '{folder_name}' 已存在")
            except Exception as e:
                QMessageBox.critical(None, "错误", f"创建文件夹失败: {str(e)}")
    
    def create_new_file(self):
        """创建新文件"""
        # 获取当前选中的目录
        index = self.tree_view.currentIndex()
        if index.isValid():
            path = self.model.filePath(index)
            # 如果选中的是文件，则使用其所在目录
            if not os.path.isdir(path):
                path = os.path.dirname(path)
        else:
            # 如果没有选中项，则使用根目录
            path = self.data_dir
        
        # 弹出对话框获取文件名称
        from PyQt5.QtWidgets import QInputDialog
        file_name, ok = QInputDialog.getText(self, "新建文件", "请输入文件名称:")
        if ok and file_name:
            # 如果没有扩展名，默认添加.md扩展名
            if not file_name.endswith(('.txt', '.md')):
                file_name += '.md'
            
            file_path = os.path.join(path, file_name)
            try:
                if not os.path.exists(file_path):
                    # 创建空文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('')
                    
                    # 刷新文件管理器
                    self.refresh()
                    
                    # 返回新文件路径，以便主窗口打开它
                    return file_path
                else:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "警告", f"文件 '{file_name}' 已存在")
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "错误", f"创建文件失败: {str(e)}")
        
        return None

    def delete_item(self, index):
        """删除选中的文件或文件夹"""
        if not index.isValid():
            return
        
        file_path = self.model.filePath(index)
        file_name = os.path.basename(file_path)
        
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除 '{file_name}' 吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                
                # 刷新文件管理器
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "删除失败", f"删除 '{file_name}' 失败: {str(e)}")
    
    def copy_item(self, index):
        """复制选中的文件或文件夹"""
        if not index.isValid():
            return
        
        source_path = self.model.filePath(index)
        source_name = os.path.basename(source_path)
        
        # 获取目标路径
        target_dir = QFileDialog.getExistingDirectory(
            self, "选择目标文件夹", self.data_dir, QFileDialog.ShowDirsOnly)
        
        if not target_dir:
            return
        
        target_path = os.path.join(target_dir, source_name)
        
        # 检查目标路径是否已存在
        if os.path.exists(target_path):
            reply = QMessageBox.question(
                self, "文件已存在", 
                f"目标位置已存在名为 '{source_name}' 的文件或文件夹，是否覆盖？",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.No:
                return
        
        try:
            if os.path.isdir(source_path):
                # 如果目标存在，先删除
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                shutil.copytree(source_path, target_path)
            else:
                shutil.copy2(source_path, target_path)
            
            # 刷新文件管理器
            self.refresh()
            
            QMessageBox.information(self, "复制成功", f"已成功复制到 {target_path}")
        except Exception as e:
            QMessageBox.critical(self, "复制失败", f"复制 '{source_name}' 失败: {str(e)}")