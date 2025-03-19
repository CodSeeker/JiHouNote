from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QTextEdit, 
                           QTabWidget, QLabel, QPushButton, QComboBox)
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QSyntaxHighlighter, QTextCursor, QTextOption, QTextFormat, QPainter
from PyQt5.QtCore import Qt, QRect, QSize

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # 标题格式
        header_format = QTextCharFormat()
        header_format.setFontWeight(QFont.Bold)
        header_format.setForeground(QColor("#0000FF"))
        header_format.setFontPointSize(14)
        self.highlighting_rules.append((r'^\s*#\s+.+$', header_format))
        
        header2_format = QTextCharFormat()
        header2_format.setFontWeight(QFont.Bold)
        header2_format.setForeground(QColor("#0000FF"))
        header2_format.setFontPointSize(12)
        self.highlighting_rules.append((r'^\s*##\s+.+$', header2_format))
        
        # 粗体格式
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r'\*\*(.+?)\*\*', bold_format))
        self.highlighting_rules.append((r'__(.+?)__', bold_format))
        
        # 斜体格式
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.highlighting_rules.append((r'\*(.+?)\*', italic_format))
        self.highlighting_rules.append((r'_(.+?)_', italic_format))
        
        # 代码块格式
        code_format = QTextCharFormat()
        code_format.setFontFamily("Courier New")
        code_format.setBackground(QColor("#F0F0F0"))
        self.highlighting_rules.append((r'`(.+?)`', code_format))
        
        # 链接格式
        link_format = QTextCharFormat()
        link_format.setForeground(QColor("#0000FF"))
        link_format.setFontUnderline(True)
        self.highlighting_rules.append((r'\[(.+?)\]\((.+?)\)', link_format))
        
        # 列表格式
        list_format = QTextCharFormat()
        list_format.setForeground(QColor("#AA0000"))
        list_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r'^\s*[\*\-\+]\s+', list_format))
        self.highlighting_rules.append((r'^\s*\d+\.\s+', list_format))
    
    def highlightBlock(self, text):
        import re
        for pattern, format in self.highlighting_rules:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)

class MarkdownEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        # 工具栏
        self.toolbar = QHBoxLayout()
        
        # 字体选择
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Consolas", "Arial", "Times New Roman", "Courier New", "微软雅黑", "宋体"])
        self.font_combo.currentTextChanged.connect(self.change_font)
        self.toolbar.addWidget(QLabel("字体:"))
        self.toolbar.addWidget(self.font_combo)
        
        # 字号选择
        self.size_combo = QComboBox()
        self.size_combo.addItems(["9", "10", "11", "12", "14", "16", "18", "20", "22", "24"])
        self.size_combo.setCurrentText("12")
        self.size_combo.currentTextChanged.connect(self.change_font_size)
        self.toolbar.addWidget(QLabel("字号:"))
        self.toolbar.addWidget(self.size_combo)
        
        # 加粗按钮
        self.bold_btn = QPushButton("加粗")
        self.bold_btn.clicked.connect(self.toggle_bold)
        self.toolbar.addWidget(self.bold_btn)
        
        # 斜体按钮
        self.italic_btn = QPushButton("斜体")
        self.italic_btn.clicked.connect(self.toggle_italic)
        self.toolbar.addWidget(self.italic_btn)
        
        # 标题按钮
        self.header_btn = QPushButton("标题")
        self.header_btn.clicked.connect(self.insert_header)
        self.toolbar.addWidget(self.header_btn)
        
        # 列表按钮
        self.list_btn = QPushButton("列表")
        self.list_btn.clicked.connect(self.insert_list)
        self.toolbar.addWidget(self.list_btn)
        
        # 代码按钮
        self.code_btn = QPushButton("代码")
        self.code_btn.clicked.connect(self.insert_code)
        self.toolbar.addWidget(self.code_btn)
        
        # 链接按钮
        self.link_btn = QPushButton("链接")
        self.link_btn.clicked.connect(self.insert_link)
        self.toolbar.addWidget(self.link_btn)
        
        self.toolbar.addStretch()
        self.layout.addLayout(self.toolbar)

        # 初始化行号显示状态
        self.line_numbers_visible = True
        
        # 使用QPlainTextEdit替代QTextEdit以支持行号
        self.editor = QPlainTextEdit(self)  # 传入self作为父对象
        self.editor.setFont(QFont("Consolas", 12))  # 设置默认字体为Consolas
        self.editor.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        
        # 设置行号区域
        self.line_number_area = LineNumberArea(self.editor)
        self.editor.blockCountChanged.connect(self.update_line_number_area_width)
        self.editor.updateRequest.connect(self.update_line_number_area)
        self.editor.cursorPositionChanged.connect(self.highlight_current_line)
        
        # 初始化行号区域宽度
        self.update_line_number_area_width(0)
        
        # 添加语法高亮
        self.highlighter = MarkdownHighlighter(self.editor.document())
        
        # 添加到布局
        self.layout.addWidget(self.editor)
        
        # 初始化当前文件路径
        self.current_file = None
        
        # 高亮当前行
        self.highlight_current_line()
    
    # 添加行号相关方法
    def line_number_area_width(self):
        """计算行号区域的宽度"""
        # 设置固定宽度，假设最多支持9999行
        digits = 4
        space = 10 + self.editor.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self, _):
        """更新行号区域宽度"""
        if hasattr(self, 'editor') and hasattr(self, 'line_number_area_width'):
            width = self.line_number_area_width()
            self.editor.setViewportMargins(width, 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        """更新行号区域"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.editor.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """处理调整大小事件"""
        super().resizeEvent(event)
        cr = self.editor.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
    
    def line_number_area_paint_event(self, event):
        """绘制行号区域"""
        painter = QPainter(self.line_number_area)
        
        # 使用更柔和的背景色
        painter.fillRect(event.rect(), QColor(245, 245, 245))  # 更浅的灰色背景
        
        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())
        
        # 绘制行号
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                # 使用更柔和的文字颜色
                painter.setPen(QColor(130, 130, 130))  # 稍微深一点的灰色文字
                # 添加右侧间隔，将行号向左移动一些
                painter.drawText(0, top, self.line_number_area.width() - 5, 
                                self.editor.fontMetrics().height(),
                                Qt.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            block_number += 1
        
        # 在行号区域右侧绘制一条分隔线
        painter.setPen(QColor(210, 210, 210))  # 浅灰色分隔线
        painter.drawLine(
            event.rect().width() - 1, event.rect().top(),
            event.rect().width() - 1, event.rect().bottom()
        )
    
    def highlight_current_line(self):
        """高亮当前行"""
        extra_selections = []
        
        if not self.editor.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(Qt.yellow).lighter(180)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.editor.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.editor.setExtraSelections(extra_selections)
    
    # 修改现有方法以适应QPlainTextEdit
    def set_content(self, content):
        # 保存当前行号显示状态
        line_numbers_visible = True
        if hasattr(self, 'line_numbers_visible'):
            line_numbers_visible = self.line_numbers_visible
        
        # 设置内容
        self.editor.setPlainText(content)
        
        # 恢复行号显示状态
        self.line_numbers_visible = line_numbers_visible
        if not self.line_numbers_visible:
            self.line_number_area.hide()
            self.editor.setViewportMargins(0, 0, 0, 0)
    
    def get_content(self):
        return self.editor.toPlainText()
    
    # 修改工具栏功能方法以适应QPlainTextEdit
    def change_font(self, font_name):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            position = cursor.position()
            anchor = cursor.anchor()
            
            format = QTextCharFormat()
            format.setFontFamily(font_name)
            
            cursor.mergeCharFormat(format)
            self.editor.setTextCursor(cursor)
        else:
            self.editor.setFont(QFont(font_name, int(self.size_combo.currentText())))
    
    def change_font_size(self, size):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            position = cursor.position()
            anchor = cursor.anchor()
            
            format = QTextCharFormat()
            format.setFontPointSize(float(size))
            
            cursor.mergeCharFormat(format)
            self.editor.setTextCursor(cursor)
        else:
            font = self.editor.font()
            font.setPointSize(int(size))
            self.editor.setFont(font)
    
    def toggle_bold(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.removeSelectedText()
            cursor.insertText(f"**{text}**")
        else:
            cursor.insertText("****")
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 2)
            self.editor.setTextCursor(cursor)
    
    def toggle_italic(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.removeSelectedText()
            cursor.insertText(f"*{text}*")
        else:
            cursor.insertText("**")
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
            self.editor.setTextCursor(cursor)
    
    def insert_header(self):
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.insertText("# ")
    
    def insert_list(self):
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.insertText("* ")
    
    def insert_code(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.removeSelectedText()
            cursor.insertText(f"`{text}`")
        else:
            cursor.insertText("``")
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
            self.editor.setTextCursor(cursor)
    
    def insert_link(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.removeSelectedText()
            cursor.insertText(f"[{text}](url)")
        else:
            cursor.insertText("[链接文本](url)")
            # 选中url部分
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 3)
            self.editor.setTextCursor(cursor)

    def toggle_line_numbers(self):
        """切换行号显示状态"""
        self.line_numbers_visible = not self.line_numbers_visible
        
        if self.line_numbers_visible:
            # 显示行号
            self.line_number_area.show()
            self.update_line_number_area_width(0)
        else:
            # 隐藏行号，同时移除左侧间距
            self.line_number_area.hide()
            self.editor.setViewportMargins(0, 0, 0, 0)
        
        # 更新编辑器
        self.editor.update()


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.markdown_editor = editor.parent()  # 获取MarkdownEditor实例
        self.editor = editor  # 保存QPlainTextEdit实例

    def sizeHint(self):
        return QSize(self.markdown_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.markdown_editor.line_number_area_paint_event(event)

