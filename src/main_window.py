import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTreeView, QListView, QTabWidget, QAction, 
                            QFileDialog, QInputDialog, QMessageBox, QSplitter,
                            QFileSystemModel)  # 从QtWidgets导入QFileSystemModel
from PyQt5.QtCore import Qt, QDir  # 移除了QFileSystemModel
from PyQt5.QtGui import QIcon, QKeySequence

from editor import MarkdownEditor
from file_manager import FileManager
from search_widget import SearchWidget
from tag_manager import TagManager
from config_manager import ConfigManager
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTabWidget, QAction, QFileDialog, QMessageBox, QInputDialog, QSplitter, QShortcut
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 获取应用程序目录
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 加载配置，传递app_dir参数
        self.config_manager = ConfigManager(app_dir)
        
        # 设置数据目录
        self.data_dir = self.config_manager.get("data_dir")
        if not self.data_dir or not os.path.exists(self.data_dir):
            # 默认使用用户文档目录下的JiHou文件夹
            self.data_dir = os.path.join(os.path.expanduser("~"), "Documents", "JiHou")
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            self.config_manager.set("data_dir", self.data_dir)
        
        # 移除对init_ui的调用，直接在这里初始化UI
        # self.init_ui()  # 删除这一行
        
        # 设置窗口属性
        self.setWindowTitle("JiHouNote")  # 修改窗口标题
        self.setGeometry(100, 100, 1200, 800)
        
        # 在__init__方法中修改布局部分
        # 创建主布局
        main_layout = QHBoxLayout()
        
        # 创建左侧面板
        self.left_panel = QWidget()
        self.left_panel.setObjectName("left_panel")  # 设置对象名，以便在样式表中引用
        self.left_panel.setMinimumWidth(200)  # 设置最小宽度
        self.left_panel.setMaximumWidth(500)  # 设置最大宽度
        left_layout = QVBoxLayout(self.left_panel)
        
        # 创建标签页
        self.left_tabs = QTabWidget()
        
        # 文件管理器标签页
        self.file_manager = FileManager(self.data_dir)
        self.file_manager.file_clicked.connect(self.open_file)  # 确保这行代码存在
        self.left_tabs.addTab(self.file_manager, "文件")
        
        # 搜索标签页
        self.search_widget = SearchWidget(self.data_dir)
        self.search_widget.file_clicked.connect(self.open_file)
        self.left_tabs.addTab(self.search_widget, "搜索")
        
        # 标签管理器标签页
        #self.tag_manager = TagManager(self.data_dir)
        # 修改这一行，使用tag_selected而不是tag_clicked
        #self.tag_manager.tag_selected.connect(self.show_files_by_tag)
        #self.left_tabs.addTab(self.tag_manager, "标签")
        
        left_layout.addWidget(self.left_tabs)
        
        # 创建编辑器
        self.editor = MarkdownEditor()
        
        # 创建分割器
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setObjectName("main_splitter")
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.editor)
        self.splitter.setStretchFactor(1, 1)  # 编辑器区域可以伸展
        
        # 添加到主布局
        main_layout.addWidget(self.splitter)
        
        # 创建中央窗口部件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # 创建菜单和工具栏
        self.create_menus()
        
        # 设置快捷键
        self.setup_shortcuts()
    
    # 在create_menus方法中修改视图菜单部分
    def create_menus(self):
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        new_file_action = QAction("新建文件", self)
        new_file_action.triggered.connect(self.new_file)
        file_menu.addAction(new_file_action)
        
        new_folder_action = QAction("新建文件夹", self)
        new_folder_action.triggered.connect(self.new_folder)
        file_menu.addAction(new_folder_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("保存", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("另存为", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("导出", self)
        export_action.triggered.connect(self.export_file)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        
        # 移除添加标签选项
        # add_tag_action = QAction("添加标签", self)
        # add_tag_action.triggered.connect(self.add_tag_to_current_file)
        # edit_menu.addAction(add_tag_action)
        
        # 视图菜单
        view_menu = self.menuBar().addMenu("视图")
        
        # 添加切换行号显示的菜单项
        toggle_line_numbers_action = QAction("显示/隐藏行号", self)
        toggle_line_numbers_action.setCheckable(True)
        toggle_line_numbers_action.setChecked(True)  # 默认显示行号
        toggle_line_numbers_action.triggered.connect(self.toggle_line_numbers)
        view_menu.addAction(toggle_line_numbers_action)
        
        # 帮助菜单
        help_menu = self.menuBar().addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # 添加设置菜单
        settings_menu = self.menuBar().addMenu("设置")
        
        # 显示当前数据目录
        show_data_dir_action = QAction(f"当前数据目录: {self.data_dir}", self)
        show_data_dir_action.setEnabled(False)  # 设置为不可点击，仅显示信息
        settings_menu.addAction(show_data_dir_action)
        self.show_data_dir_action = show_data_dir_action  # 保存引用以便后续更新
        
        # 更改数据目录
        data_dir_action = QAction("更改数据目录", self)
        data_dir_action.triggered.connect(self.change_data_dir)
        settings_menu.addAction(data_dir_action)
    
    def new_file(self):
        """新建文件"""
        self.file_manager.create_new_file()
        name, ok = QInputDialog.getText(self, "新建文件", "请输入文件名:")
        if ok and name:
            if not name.endswith(('.txt', '.md')):
                name += '.md'  # 默认使用Markdown格式
            file_path = os.path.join(self.data_dir, name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('')
            self.file_manager.refresh()
            self.open_file(file_path)
    
    def open_file_dialog(self):
        """打开文件对话框"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开文件", "", "文本文件 (*.txt *.md);;所有文件 (*.*)")
        
        if file_path:
            self.open_file(file_path)
    
    def open_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor.set_content(content)
            self.editor.current_file = file_path
            self.setWindowTitle(f"积厚文本管理工具 - {os.path.basename(file_path)}")
            
            # 在状态栏显示完整路径
            self.statusBar().showMessage(f"文件: {file_path}")
            
            # 移除更新当前文件的标签
            # self.tag_manager.update_current_file_tags(file_path)
            
            # 根据当前行号显示状态更新编辑器
            if hasattr(self.editor, 'line_numbers_visible') and not self.editor.line_numbers_visible:
                # 如果行号当前是隐藏状态，确保在新文件中也隐藏行号
                self.editor.line_number_area.hide()
                self.editor.editor.setViewportMargins(0, 0, 0, 0)
                self.editor.editor.update()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")
    
    def save_file(self):
        if hasattr(self.editor, 'current_file') and self.editor.current_file:
            try:
                with open(self.editor.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.editor.get_content())
                
                # 优化保存成功提示，减小宽度
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("保存成功")
                msg_box.setText("文件已保存")  # 简化文本
                msg_box.setIcon(QMessageBox.Information)
                
                # 设置按钮样式
                ok_button = msg_box.addButton("确定", QMessageBox.AcceptRole)
                ok_button.setStyleSheet("""
                    QPushButton {
                        background-color: #3366cc;
                        color: white;
                        border: none;
                        padding: 5px 15px;
                        border-radius: 3px;
                        min-width: 60px;  /* 减小按钮宽度 */
                    }
                    QPushButton:hover {
                        background-color: #4477dd;
                    }
                    QPushButton:pressed {
                        background-color: #2255bb;
                    }
                """)
                
                # 设置整体样式，减小宽度
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #f8f8f8;
                    }
                    QLabel {
                        font-size: 11pt;
                        padding: 8px;
                        min-width: 120px;  /* 减小标签宽度 */
                        max-width: 150px;  /* 限制最大宽度 */
                    }
                """)
                
                # 显示1.5秒后自动关闭
                QTimer.singleShot(1500, msg_box.accept)
                
                msg_box.exec_()
                
                # 更新状态栏
                self.statusBar().showMessage(f"文件已保存", 2000)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存文件失败: {str(e)}")
        else:
            self.save_file_as()
    
    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", self.data_dir, "文本文件 (*.txt);;Markdown文件 (*.md);;所有文件 (*.*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.editor.get_content())
                self.editor.current_file = file_path
                self.setWindowTitle(f"积厚文本管理工具 - {os.path.basename(file_path)}")
                
                # 优化保存成功提示，减小宽度
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("保存成功")
                msg_box.setText("文件已保存")  # 简化文本
                msg_box.setIcon(QMessageBox.Information)
                
                # 设置按钮样式
                ok_button = msg_box.addButton("确定", QMessageBox.AcceptRole)
                ok_button.setStyleSheet("""
                    QPushButton {
                        background-color: #3366cc;
                        color: white;
                        border: none;
                        padding: 5px 15px;
                        border-radius: 3px;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #4477dd;
                    }
                    QPushButton:pressed {
                        background-color: #2255bb;
                    }
                """)
                
                # 设置整体样式
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #f8f8f8;
                    }
                    QLabel {
                        font-size: 12pt;
                        padding: 10px;
                        min-width: 200px;
                    }
                """)
                
                # 显示2秒后自动关闭
                QTimer.singleShot(2000, msg_box.accept)
                
                msg_box.exec_()
                
                # 更新状态栏
                self.statusBar().showMessage(f"文件已保存: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存文件失败: {str(e)}")
    
    def import_file(self):
        """导入外部文件到知识库"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "导入文件", "", "文本文件 (*.txt *.md);;所有文件 (*.*)")
        
        if not file_paths:
            return
        
        # 选择导入目标文件夹
        target_dir = self.select_import_target()
        if not target_dir:
            return
        
        imported_count = 0
        for file_path in file_paths:
            try:
                # 获取文件名
                file_name = os.path.basename(file_path)
                # 目标路径
                target_path = os.path.join(target_dir, file_name)
                
                # 检查目标文件是否已存在
                if os.path.exists(target_path):
                    reply = QMessageBox.question(
                        self, "文件已存在", 
                        f"文件 {file_name} 已存在，是否覆盖？",
                        QMessageBox.Yes | QMessageBox.No)
                    
                    if reply == QMessageBox.No:
                        continue
                
                # 复制文件
                with open(file_path, 'r', encoding='utf-8') as src_file:
                    content = src_file.read()
                
                with open(target_path, 'w', encoding='utf-8') as dst_file:
                    dst_file.write(content)
                
                imported_count += 1
            
            except Exception as e:
                QMessageBox.warning(self, "导入失败", f"导入文件 {file_path} 失败: {str(e)}")
        
        if imported_count > 0:
            # 刷新文件管理器
            self.file_manager.refresh()
            QMessageBox.information(self, "导入完成", f"成功导入 {imported_count} 个文件")
    
    def select_import_target(self):
        """选择导入目标文件夹"""
        # 默认使用当前数据目录
        target_dir = self.data_dir
        
        # 获取当前选中的目录
        index = self.file_manager.tree_view.currentIndex()
        if index.isValid():
            path = self.file_manager.model.filePath(index)
            if os.path.isdir(path):
                target_dir = path
        
        # 确认对话框
        reply = QMessageBox.question(
            self, "选择导入位置", 
            f"是否将文件导入到以下位置？\n{target_dir}\n\n选择'否'可以手动选择其他位置",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        
        if reply == QMessageBox.Cancel:
            return None
        
        if reply == QMessageBox.No:
            # 手动选择目录
            dir_path = QFileDialog.getExistingDirectory(
                self, "选择导入位置", target_dir, QFileDialog.ShowDirsOnly)
            
            if not dir_path:
                return None
            
            return dir_path
        
        return target_dir
        

    
    def export_file(self):
        if not hasattr(self.editor, 'current_file') or not self.editor.current_file:
            QMessageBox.warning(self, "警告", "没有打开的文件可导出")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出文件", "", "文本文件 (*.txt);;Markdown文件 (*.md);;HTML文件 (*.html);;所有文件 (*.*)")
        
        if file_path:
            try:
                content = self.editor.get_content()
                
                # 如果导出为HTML格式
                if file_path.endswith('.html'):
                    import markdown
                    html_content = markdown.markdown(content)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{os.path.basename(self.editor.current_file)}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }}
        h1, h2, h3 {{ color: #333; }}
        code {{ background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #ddd; padding-left: 10px; color: #666; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>""")
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                QMessageBox.information(self, "导出成功", f"文件已导出到 {file_path}")
            
            except Exception as e:
                QMessageBox.critical(self, "导出错误", f"导出文件失败: {str(e)}")
    
    # 移除这些方法
    # def add_tag_to_current_file(self):
    #     if not hasattr(self.editor, 'current_file') or not self.editor.current_file:
    #         QMessageBox.warning(self, "警告", "没有打开的文件可添加标签")
    #         return
    #     
    #     tag, ok = QInputDialog.getText(self, "添加标签", "请输入标签名:")
    #     if ok and tag:
    #         self.tag_manager.add_tag_to_file(self.editor.current_file, tag)
    
    # def show_files_by_tag(self, tag):
    #     files = self.tag_manager.get_files_by_tag(tag)
    #     if not files:
    #         QMessageBox.information(self, "标签搜索", f"没有找到带有标签 '{tag}' 的文件")
    #         return
    #     
    #     # 在搜索结果中显示
    #     self.search_widget.results_list.clear()
    #     for file_path in files:
    #         relative_path = os.path.relpath(file_path, self.data_dir)
    #         item = QListWidgetItem(f"{relative_path} [标签: {tag}]")
    #         item.setData(Qt.UserRole, file_path)
    #         self.search_widget.results_list.addItem(item)
    #     
    #     # 切换到搜索标签页
    #     self.left_tabs.setCurrentWidget(self.search_widget)
    def show_about(self):
        about_box = QMessageBox(self)
        about_box.setWindowTitle("关于")
        about_box.setTextFormat(Qt.RichText)
        
        # 使用HTML格式美化内容
        about_text = f"""
        <div style="text-align: center;">
            <h2 style="color: #3366cc;">积厚文本管理工具</h2>
            <p style="font-size: 14px; margin: 5px 0;">版本: 1.0</p>
            <p style="font-size: 14px; margin: 5px 0;">基于Python和Qt开发</p>
            <p style="font-size: 14px; margin: 5px 0;">支持Markdown格式</p>
            <hr style="margin: 10px 0;">
            <p style="font-size: 12px; color: #666;">Copyright © 2025</p>
            <p style="font-size: 12px; color: #666;">保留所有权利</p>
        </div>
        """
        
        about_box.setText(about_text)
        
        # 设置图标 - 修正方法名大小写
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "resources", "icon.ico")
        if os.path.exists(icon_path):
            about_box.setIconPixmap(QIcon(icon_path).pixmap(64, 64))  # 将setIconPixMap改为setIconPixmap
        
        # 设置按钮
        about_box.setStandardButtons(QMessageBox.Ok)
        ok_button = about_box.button(QMessageBox.Ok)
        if ok_button:
            ok_button.setText("确定")
            ok_button.setStyleSheet("""
                QPushButton {
                    background-color: #3366cc;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #4477dd;
                }
                QPushButton:pressed {
                    background-color: #2255bb;
                }
            """)
        
        # 设置整体样式
        about_box.setStyleSheet("""
            QMessageBox {
                background-color: #f8f8f8;
            }
            QLabel {
                min-width: 300px;
            }
        """)
        
        about_box.exec_()
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # 保存文件快捷键
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_file)
        
        # 如果需要添加更多快捷键，可以在这里添加
        pass

    def new_folder(self):
        """新建文件夹"""
        # 获取当前选中的目录
        index = self.file_manager.tree_view.currentIndex()
        if index.isValid():
            path = self.file_manager.model.filePath(index)
            # 如果选中的是文件，则使用其所在目录
            if not os.path.isdir(path):
                path = os.path.dirname(path)
        else:
            # 如果没有选中项，则使用根目录
            path = self.data_dir
        
        # 弹出对话框获取文件夹名称
        folder_name, ok = QInputDialog.getText(self, "新建文件夹", "请输入文件夹名称:")
        if ok and folder_name:
            folder_path = os.path.join(path, folder_name)
            try:
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    # 刷新文件管理器
                    self.file_manager.refresh()
                    
                    # 展开父目录
                    parent_index = self.file_manager.model.index(path)
                    self.file_manager.tree_view.expand(parent_index)
                    
                    # 选中新文件夹
                    new_folder_index = self.file_manager.model.index(folder_path)
                    self.file_manager.tree_view.setCurrentIndex(new_folder_index)
                else:
                    QMessageBox.warning(self, "警告", f"文件夹 '{folder_name}' 已存在")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建文件夹失败: {str(e)}")

    def change_data_dir(self):
        """更改数据保存目录"""
        new_dir = QFileDialog.getExistingDirectory(
            self, "选择数据目录", self.data_dir, QFileDialog.ShowDirsOnly)
        
        if new_dir:
            # 确认是否移动现有数据
            if os.path.exists(self.data_dir) and os.listdir(self.data_dir):
                reply = QMessageBox.question(
                    self, "移动数据", 
                    "是否将现有数据移动到新目录？\n选择'是'将复制现有数据到新目录\n选择'否'将使用空白的新目录",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                
                if reply == QMessageBox.Cancel:
                    return
                
                if reply == QMessageBox.Yes:
                    try:
                        import shutil
                        # 如果新目录不存在，创建它
                        if not os.path.exists(new_dir):
                            os.makedirs(new_dir)
                        
                        # 复制所有文件
                        for item in os.listdir(self.data_dir):
                            src_path = os.path.join(self.data_dir, item)
                            dst_path = os.path.join(new_dir, item)
                            
                            if os.path.isdir(src_path):
                                if os.path.exists(dst_path):
                                    shutil.rmtree(dst_path)
                                shutil.copytree(src_path, dst_path)
                            else:
                                shutil.copy2(src_path, dst_path)
                    
                    except Exception as e:
                        QMessageBox.critical(self, "错误", f"移动数据失败: {str(e)}")
                        return
            
            # 更新配置
            self.config_manager.set("data_dir", new_dir)
            self.data_dir = new_dir
            
            # 更新菜单显示
            self.show_data_dir_action.setText(f"当前数据目录: {self.data_dir}")
            
            # 更新文件管理器
            self.file_manager.set_root_path(new_dir)
            
            # 更新标签管理器
            self.tag_manager = TagManager(new_dir)
            self.left_tabs.removeTab(2)  # 移除旧的标签页
            self.left_tabs.insertTab(2, self.tag_manager, "标签")
            
            QMessageBox.information(self, "成功", f"数据目录已更改为:\n{new_dir}")

    def toggle_line_numbers(self):
        """切换行号显示状态"""
        # 确保editor属性存在并且是MarkdownEditor类的实例
        if hasattr(self, 'editor') and self.editor:
            # 打印调试信息
            # print("切换行号显示")
            # print(f"编辑器类型: {type(self.editor)}")
            # print(f"编辑器方法: {dir(self.editor)}")
            
            # 调用toggle_line_numbers方法
            self.editor.toggle_line_numbers()  # 添加这一行，修复缺少的代码块