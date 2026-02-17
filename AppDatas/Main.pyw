import sys
import json
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QListWidget, QLabel,
                             QLineEdit, QTextEdit, QFrame, QSplitter,
                             QListWidgetItem, QMessageBox, QDialog, QGridLayout,
                             QComboBox, QSpinBox, QCheckBox, QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer, QProcess
from PyQt5.QtGui import QFont, QIcon, QClipboard
from PyQt5.QtGui import QIcon

# ===== 隐藏控制台窗口 =====
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
# ==========================

COLORS = {
    'bg': '#f5f5f7',
    'card': '#ffffff',
    'primary': '#1a73e8',
    'primary_hover': '#1557b0',
    'text': '#202124',
    'text_secondary': '#5f6368',
    'border': '#dadce0',
    'success': '#34a853',
    'warning': '#f9ab00',
    'error': '#ea4335'
}


# ========== 指令模拟器对话框（保留原有）==========
class CommandSimulatorDialog(QDialog):
    # ...（此处省略，保持与原代码完全一致）...
    pass
# ============================================


class MinecraftCommandHelper(QMainWindow):
    def __init__(self):
        super().__init__()
        # ===== 设置窗口图标 =====
        import os
        from PyQt5.QtGui import QIcon
        icon_path = os.path.join(os.path.dirname(__file__), "data", "res", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        # ========================

        self.all_commands = []
        self.filtered_commands = []
        self.command_dict = {}
        self.initUI()
        self.load_commands()
        
    def initUI(self):
        self.setWindowTitle("MineCodes · 我的世界指令助手")
        self.setMinimumSize(1000, 650)
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['bg']};
            }}
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
            QPushButton.flat {{
                background-color: transparent;
                color: {COLORS['primary']};
                border: 1px solid {COLORS['border']};
            }}
            QPushButton.flat:hover {{
                background-color: #e8f0fe;
            }}
            QLineEdit {{
                padding: 8px;
                border: 1px solid {COLORS['border']};
                border-radius: 20px;
                font-size: 13px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
                outline: none;
            }}
            QListWidget {{
                background-color: white;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 5px;
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 4px;
                margin: 2px 0;
            }}
            QListWidget::item:hover {{
                background-color: #f1f3f4;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QTextEdit {{
                background-color: white;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }}
            QFrame.category {{
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }}
            QLabel.category {{
                padding: 6px 12px;
                border-radius: 16px;
                background-color: #f1f3f4;
                color: {COLORS['text']};
                font-size: 12px;
            }}
            QLabel#explain {{
                background-color: {COLORS['bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                color: {COLORS['text_secondary']};
            }}
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ========== 顶部标题和搜索 ==========
        top_layout = QHBoxLayout()
        
        title = QLabel("⛏️ MineCodes")
        title.setStyleSheet(f"font-size: 24px; font-weight: 400; color: {COLORS['primary']};")
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 搜索指令 (例如: give, tp, summon...)")
        self.search_box.textChanged.connect(self.filter_commands)
        
        top_layout.addWidget(title)
        top_layout.addStretch()
        self.search_box.setMaximumWidth(400)
        top_layout.addWidget(self.search_box)
        
        # 功能按钮 - 统一设置最小宽度
        self.simulator_btn = QPushButton("🎮 指令助手")
        self.simulator_btn.setCursor(Qt.PointingHandCursor)
        self.simulator_btn.setMinimumWidth(100)          # 统一宽度
        self.simulator_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 20px;
                padding: 6px 16px;
                font-size: 13px;
                margin-left: 10px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']}20;
            }}
        """)
        self.simulator_btn.clicked.connect(self.open_command_helper)
        
        self.itemdb_btn = QPushButton("📦 物品ID查询")
        self.itemdb_btn.setCursor(Qt.PointingHandCursor)
        self.itemdb_btn.setMinimumWidth(100)              # 统一宽度
        self.itemdb_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['success']};
                border: 1px solid {COLORS['success']};
                border-radius: 20px;
                padding: 6px 16px;
                font-size: 13px;
                margin-left: 10px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['success']}20;
            }}
        """)
        self.itemdb_btn.clicked.connect(self.open_item_database)
        
        # 新增设置按钮
        self.settings_btn = QPushButton("⚙️ 设置")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setMinimumWidth(100)            # 统一宽度
        self.settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 20px;
                padding: 6px 16px;
                font-size: 13px;
                margin-left: 10px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['text']}10;
            }}
        """)
        self.settings_btn.clicked.connect(self.open_settings)
        
        top_layout.addWidget(self.simulator_btn)
        top_layout.addWidget(self.itemdb_btn)
        top_layout.addWidget(self.settings_btn)
        
        main_layout.addLayout(top_layout)
        
        # ========== 分类标签 ==========
        categories_layout = QHBoxLayout()
        categories_layout.setSpacing(10)
        
        self.category_btns = []
        categories = [
            ("全部", "all", COLORS['primary']),
            ("⭐ 常用", "常用", COLORS['success']),
            ("👑 管理员", "管理员", COLORS['error']),
            ("🌍 世界", "世界", COLORS['warning']),
            ("👤 玩家", "玩家", COLORS['primary']),
            ("⚔️ 战斗", "战斗", COLORS['error']),
            ("📦 物品", "物品", COLORS['success'])
        ]
        
        for i, (name, cat, color) in enumerate(categories):
            btn = QPushButton(name)
            btn.setProperty("category", cat)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {color};
                    border: 1px solid {color};
                    border-radius: 20px;
                    padding: 6px 16px;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {color}20;
                }}
                QPushButton:checked {{
                    background-color: {color};
                    color: white;
                }}
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, c=cat: self.filter_by_category(c))
            categories_layout.addWidget(btn)
            self.category_btns.append(btn)
            if i == 0:
                btn.setChecked(True)
        
        categories_layout.addStretch()
        main_layout.addLayout(categories_layout)
        
        # ========== 主内容区 ==========
        content_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧列表
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_frame.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border: none;
            }}
        """)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        list_header = QHBoxLayout()
        list_title = QLabel("📋 指令列表")
        list_title.setStyleSheet(f"font-size: 16px; font-weight: 500; color: {COLORS['text']};")
        self.count_label = QLabel("0 个指令")
        self.count_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        list_header.addWidget(list_title)
        list_header.addStretch()
        list_header.addWidget(self.count_label)
        left_layout.addLayout(list_header)
        
        self.command_list = QListWidget()
        self.command_list.itemClicked.connect(self.show_command_detail)
        left_layout.addWidget(self.command_list)
        
        # 右侧详情 + 输入区
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_frame.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border: none;
            }}
        """)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        detail_title = QLabel("📖 指令详情")
        detail_title.setStyleSheet(f"font-size: 16px; font-weight: 500; color: {COLORS['text']};")
        right_layout.addWidget(detail_title)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        right_layout.addWidget(self.detail_text)
        
        # 指令输入区
        input_label = QLabel("✏️ 指令输入")
        input_label.setStyleSheet(f"font-size: 14px; font-weight: 500; color: {COLORS['text']}; margin-top: 5px;")
        right_layout.addWidget(input_label)
        
        input_layout = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("在此输入指令，例如 /tp @p 10 20 30")
        self.cmd_input.textChanged.connect(self.update_command_explain)
        
        self.copy_input_btn = QPushButton("📋 复制")
        self.copy_input_btn.setFixedWidth(60)
        self.copy_input_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
        """)
        self.copy_input_btn.clicked.connect(self.copy_input_text)
        
        input_layout.addWidget(self.cmd_input)
        input_layout.addWidget(self.copy_input_btn)
        right_layout.addLayout(input_layout)
        
        self.cmd_explain_label = QLabel("等待输入...")
        self.cmd_explain_label.setObjectName("explain")
        self.cmd_explain_label.setWordWrap(True)
        right_layout.addWidget(self.cmd_explain_label)
        
        content_splitter.addWidget(left_frame)
        content_splitter.addWidget(right_frame)
        content_splitter.setSizes([350, 650])
        
        main_layout.addWidget(content_splitter)
        
        status_bar = self.statusBar()
        status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: white;
                border-top: 1px solid {COLORS['border']};
                color: {COLORS['text_secondary']};
            }}
        """)
        status_bar.showMessage("✨ 点击指令查看详细用法，或在下方输入框尝试指令")
    
    def open_command_helper(self):
        """打开指令助手程序"""
        import sys
        import os
        import subprocess
        
        # 判断是否在打包环境中
        if getattr(sys, 'frozen', False):
            # 打包环境：exe 文件应该和主程序在同一目录
            base_path = os.path.dirname(sys.executable)
            helper_name = "MineCodes_CommandHelper.exe"
        else:
            # 源码环境：使用 pyw 文件
            base_path = os.path.dirname(os.path.abspath(__file__))
            helper_name = "CommandHelper.pyw"
        
        helper_path = os.path.join(base_path, helper_name)
        
        if not os.path.exists(helper_path):
            QMessageBox.warning(self, "提示", f"未找到程序：{helper_path}\n请确保 {helper_name} 在同一目录下。")
            return
        
        try:
            if sys.platform == 'win32':
                subprocess.Popen(['start', '', helper_path], shell=True)
            else:
                subprocess.Popen([helper_path])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动失败：{str(e)}")

    def open_item_database(self):
        """打开物品ID查询程序"""
        import sys
        import os
        import subprocess
        
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            helper_name = "MineCodes_ItemIDHelper.exe"
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            helper_name = "ItemIDHelper.pyw"
        
        helper_path = os.path.join(base_path, helper_name)
        
        if not os.path.exists(helper_path):
            QMessageBox.warning(self, "提示", f"未找到程序：{helper_path}\n请确保 {helper_name} 在同一目录下。")
            return
        
        try:
            if sys.platform == 'win32':
                subprocess.Popen(['start', '', helper_path], shell=True)
            else:
                subprocess.Popen([helper_path])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动失败：{str(e)}")

    def open_settings(self):
        """打开设置程序"""
        import sys
        import os
        import subprocess
        
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            helper_name = "MineCodes_Settings.exe"
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            helper_name = "Settings.pyw"
        
        helper_path = os.path.join(base_path, helper_name)
        
        if not os.path.exists(helper_path):
            QMessageBox.warning(self, "提示", f"未找到程序：{helper_path}\n请确保 {helper_name} 在同一目录下。")
            return
        
        try:
            if sys.platform == 'win32':
                subprocess.Popen(['start', '', helper_path], shell=True)
            else:
                subprocess.Popen([helper_path])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动失败：{str(e)}")
    
    # ===== 复制输入框内容 =====
    def copy_input_text(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.cmd_input.text())
        QMessageBox.information(self, "提示", "指令已复制到剪贴板")
    
    # ===== 实时解释指令 =====
    def update_command_explain(self):
        text = self.cmd_input.text().strip()
        if not text:
            self.cmd_explain_label.setText("等待输入...")
            return
        parts = text.split()
        if not parts:
            return
        cmd_name = parts[0].lower()
        if not cmd_name.startswith('/'):
            cmd_name = '/' + cmd_name
        if cmd_name in self.command_dict:
            cmd_data = self.command_dict[cmd_name]
            base_desc = cmd_data['description']
            if len(parts) == 1:
                explain = f"📌 {cmd_name} - {base_desc}"
            else:
                explain = f"📌 {cmd_name} - {base_desc}\n当前参数：{' '.join(parts[1:])}"
        else:
            explain = f"⚠️ 未知指令：{cmd_name}"
        self.cmd_explain_label.setText(explain)
    
    # ===== 加载指令数据 =====
    def load_commands(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "commands.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                commands_data = json.load(f)
        except FileNotFoundError:
            QMessageBox.critical(self, "错误", f"找不到指令数据文件：{json_path}")
            commands_data = []
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取指令数据文件失败：{str(e)}")
            commands_data = []
        
        self.all_commands = []
        self.command_dict = {}
        for cmd in commands_data:
            self.all_commands.append({
                'command': cmd['command'],
                'description': cmd['description'],
                'usage': cmd['usage'],
                'category': cmd['category']
            })
            self.command_dict[cmd['command'].lower()] = {
                'command': cmd['command'],
                'description': cmd['description'],
                'usage': cmd['usage'],
                'category': cmd['category']
            }
        
        self.filtered_commands = self.all_commands.copy()
        self.update_command_list()
        if self.command_list.count() > 0:
            self.command_list.setCurrentRow(0)
            self.show_command_detail(self.command_list.item(0))
    
    def update_command_list(self):
        self.command_list.clear()
        for cmd in self.filtered_commands:
            item = QListWidgetItem(f"{cmd['command']} - {cmd['description']}")
            item.setData(Qt.UserRole, cmd)
            self.command_list.addItem(item)
        self.count_label.setText(f"{len(self.filtered_commands)} 个指令")
    
    def filter_commands(self):
        search_text = self.search_box.text().lower()
        if not search_text:
            self.filtered_commands = self.all_commands.copy()
        else:
            self.filtered_commands = [
                cmd for cmd in self.all_commands 
                if search_text in cmd['command'].lower() 
                or search_text in cmd['description'].lower()
            ]
        self.update_command_list()
        for btn in self.category_btns:
            if btn.property("category") == "all":
                btn.setChecked(True)
            else:
                btn.setChecked(False)
    
    def filter_by_category(self, category):
        if category == "all":
            self.filtered_commands = self.all_commands.copy()
        else:
            self.filtered_commands = [
                cmd for cmd in self.all_commands 
                if cmd['category'] == category
            ]
        self.update_command_list()
        self.search_box.clear()
        if self.command_list.count() > 0:
            self.command_list.setCurrentRow(0)
            self.show_command_detail(self.command_list.item(0))
    
    def show_command_detail(self, item):
        cmd_data = item.data(Qt.UserRole)
        detail = f"""
        <style>
            .command {{ font-size: 28px; font-weight: bold; color: {COLORS['primary']}; margin-bottom: 10px; }}
            .description {{ font-size: 16px; color: {COLORS['text']}; margin-bottom: 20px; }}
            .usage-title {{ font-size: 18px; font-weight: 500; color: {COLORS['text']}; margin-top: 20px; margin-bottom: 10px; border-left: 4px solid {COLORS['primary']}; padding-left: 10px; }}
            .usage {{ background-color: {COLORS['bg']}; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 14px; color: {COLORS['text']}; white-space: pre-wrap; line-height: 1.6; }}
            .category {{ display: inline-block; padding: 4px 12px; border-radius: 16px; background-color: {COLORS['primary']}20; color: {COLORS['primary']}; font-size: 12px; margin-top: 10px; }}
        </style>
        <div class="command">{cmd_data['command']}</div>
        <div class="description">{cmd_data['description']}</div>
        <div class="usage-title">📌 用法说明</div>
        <div class="usage">{cmd_data['usage'].replace(chr(10), '<br>')}</div>
        <div class="category">{cmd_data['category']}</div>
        """
        self.detail_text.setHtml(detail)
        self.cmd_input.setText(cmd_data['command'] + " ")
        self.cmd_input.setFocus()
        self.cmd_input.end(False)
        self.update_command_explain()


def main():
    app = QApplication(sys.argv)
    # 设置应用图标（任务栏）
    import os
    from PyQt5.QtGui import QIcon
    icon_path = os.path.join(os.path.dirname(__file__), "data", "res", "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    app.setFont(QFont("Microsoft YaHei", 9))
    window = MinecraftCommandHelper()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()