#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MineCodes 设置程序
- 左侧菜单栏（设置、关于、帮助）
- 右侧内容区，支持加载外部 Markdown 文件
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFrame, QListWidget,
                             QListWidgetItem, QStackedWidget, QTextBrowser,
                             QMessageBox)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtGui import QIcon

# ===== 隐藏控制台窗口 =====
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

COLORS = {
    'bg': '#f5f5f7',
    'primary': '#1a73e8',
    'primary_hover': '#1557b0',
    'text': '#202124',
    'text_secondary': '#5f6368',
    'border': '#dadce0',
    'menu_hover': '#f1f3f4',
    'menu_selected': '#e8f0fe'
}


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        # ===== 设置窗口图标 =====
        import os
        from PyQt5.QtGui import QIcon
        icon_path = os.path.join(os.path.dirname(__file__), "data", "res", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        # ========================

        self.setWindowTitle("MineCodes · 设置")
        self.setMinimumSize(750, 550)
        self.resize(800, 600)
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg']};
                font-family: 'Microsoft YaHei';
            }}
            QListWidget {{
                background-color: white;
                border: none;
                border-right: 1px solid {COLORS['border']};
                outline: none;
                font-size: 14px;
            }}
            QListWidget::item {{
                padding: 12px 20px;
                border-left: 3px solid transparent;
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['menu_hover']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['menu_selected']};
                border-left: 3px solid {COLORS['primary']};
                color: {COLORS['primary']};
                font-weight: 500;
            }}
            QTextBrowser {{
                background-color: white;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }}
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
            QFrame {{
                background-color: white;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        
        # 主布局：水平布局，左侧菜单 + 右侧内容
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ========== 左侧菜单栏（窄） ==========
        self.menu_list = QListWidget()
        self.menu_list.setMaximumWidth(180)
        self.menu_list.setMinimumWidth(150)
        
        # 添加菜单项
        menu_items = [
            {"text": "通用设置", "icon": "⚙️"},
            {"text": "关于 MineCodes", "icon": "📖"},
            {"text": "帮助与支持", "icon": "❓"}
        ]
        
        for item in menu_items:
            list_item = QListWidgetItem(f"{item['icon']}  {item['text']}")
            list_item.setData(Qt.UserRole, item['text'])
            self.menu_list.addItem(list_item)
        
        # 默认选中第一项
        self.menu_list.setCurrentRow(0)
        
        # ========== 右侧内容区（堆叠窗口） ==========
        self.stacked_widget = QStackedWidget()
        
        # 页面1：通用设置
        self.page_settings = self.create_settings_page()
        
        # 页面2：关于页面（加载 Markdown 文件）
        self.page_about = self.create_about_page()
        
        # 页面3：帮助页面
        self.page_help = self.create_help_page()
        
        self.stacked_widget.addWidget(self.page_settings)
        self.stacked_widget.addWidget(self.page_about)
        self.stacked_widget.addWidget(self.page_help)
        
        # 绑定菜单切换事件
        self.menu_list.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)
        
        # 添加到主布局
        main_layout.addWidget(self.menu_list)
        main_layout.addWidget(self.stacked_widget, 1)  # 1 表示拉伸因子
        
        # 初始加载 Markdown 文件
        self.load_about_markdown()
    
    def create_settings_page(self):
        """创建通用设置页面"""
        page = QFrame()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel("⚙️ 通用设置")
        title.setStyleSheet(f"font-size: 20px; font-weight: 500; color: {COLORS['primary']};")
        layout.addWidget(title)
        
        # 设置选项卡片
        settings_frame = QFrame()
        settings_frame.setFrameShape(QFrame.StyledPanel)
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setSpacing(15)
        
        # 示例设置项
        settings_layout.addWidget(QLabel("🔧 此页面为预留设置项，后续版本将支持以下功能："))
        settings_layout.addWidget(QLabel("• 自定义数据文件路径"))
        settings_layout.addWidget(QLabel("• 界面主题切换（亮色/暗色）"))
        settings_layout.addWidget(QLabel("• 默认指令前缀设置"))
        settings_layout.addWidget(QLabel("• 语言选择（简体中文/English）"))
        
        layout.addWidget(settings_frame)
        layout.addStretch()
        
        return page
    
    def create_about_page(self):
        """创建关于页面（Markdown 渲染）"""
        page = QFrame()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("📖 关于 MineCodes")
        title.setStyleSheet(f"font-size: 20px; font-weight: 500; color: {COLORS['primary']};")
        layout.addWidget(title)
        
        # Markdown 渲染器
        self.markdown_viewer = QTextBrowser()
        self.markdown_viewer.setOpenExternalLinks(True)  # 允许打开外部链接
        
        # 设置 Markdown 样式
        self.markdown_viewer.document().setDefaultStyleSheet(f"""
            body {{ font-family: 'Microsoft YaHei'; font-size: 14px; line-height: 1.6; color: {COLORS['text']}; }}
            h1 {{ color: {COLORS['primary']}; font-size: 24px; margin-top: 20px; }}
            h2 {{ color: {COLORS['primary']}; font-size: 20px; margin-top: 15px; border-bottom: 1px solid {COLORS['border']}; padding-bottom: 5px; }}
            h3 {{ font-size: 18px; margin-top: 10px; }}
            a {{ color: {COLORS['primary']}; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            code {{ background-color: {COLORS['bg']}; padding: 2px 4px; border-radius: 4px; font-family: monospace; }}
            pre {{ background-color: {COLORS['bg']}; padding: 10px; border-radius: 8px; overflow-x: auto; }}
            blockquote {{ border-left: 4px solid {COLORS['primary']}; padding-left: 15px; margin-left: 0; color: {COLORS['text_secondary']}; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid {COLORS['border']}; padding: 8px; text-align: left; }}
            th {{ background-color: {COLORS['bg']}; }}
        """)
        
        layout.addWidget(self.markdown_viewer)
        
        # 底部版本信息
        version_label = QLabel("MineCodes v2.0 · 我的世界指令助手")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; margin-top: 10px;")
        layout.addWidget(version_label)
        
        return page
    
    def create_help_page(self):
        """创建帮助页面"""
        page = QFrame()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title = QLabel("❓ 帮助与支持")
        title.setStyleSheet(f"font-size: 20px; font-weight: 500; color: {COLORS['primary']};")
        layout.addWidget(title)
        
        help_frame = QFrame()
        help_frame.setFrameShape(QFrame.StyledPanel)
        help_layout = QVBoxLayout(help_frame)
        
        # 更新链接：GitHub 仓库和博客
        help_text = f"""
        <style>
            .section {{ font-size: 16px; font-weight: 500; color: {COLORS['primary']}; margin-top: 15px; }}
            .content {{ margin-left: 15px; }}
        </style>
        
        <div class='section'>📌 快速入门</div>
        <div class='content'>
        • 在搜索框中输入指令关键词（如 give、tp）即可快速查找<br>
        • 点击左侧指令列表查看详细信息<br>
        • 在下方输入框可以尝试输入指令，实时查看解释<br>
        • 点击右上角按钮可打开独立工具
        </div>
        
        <div class='section'>🎮 指令助手</div>
        <div class='content'>
        • 通过表单填写参数，自动生成完整指令<br>
        • 支持 40+ 常用指令，按标签页分类<br>
        • 点击复制按钮即可粘贴到游戏中
        </div>
        
        <div class='section'>📦 物品百科</div>
        <div class='content'>
        • 搜索物品名称或 ID 快速查找<br>
        • 查看物品详细信息、获取途径、用途等<br>
        • 可一键复制获取指令 /give @s [物品ID]
        </div>
        
        <div class='section'>📧 联系我们</div>
        <div class='content'>
        • GitHub：<a href='https://github.com/Zionyas-Van/MineCodes'>github.com/Zionyas-Van/MineCodes</a><br>
        • 博客：<a href='https://zionyas-van.github.io/'>zionyas-van.github.io</a><br>
        • 反馈问题：在 GitHub 提交 Issue
        </div>
        """
        
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setOpenExternalLinks(True)
        help_label.setStyleSheet("font-size: 14px; line-height: 1.8;")
        
        help_layout.addWidget(help_label)
        layout.addWidget(help_frame)
        layout.addStretch()
        
        return page
    
    def load_about_markdown(self):
        """加载关于页面的 Markdown 文件"""
        # 方法1：从外部 MD 文件加载
        current_dir = os.path.dirname(os.path.abspath(__file__))
        md_path = os.path.join(current_dir, "ABOUT.md")
        
        try:
            if os.path.exists(md_path):
                with open(md_path, "r", encoding="utf-8") as f:
                    md_content = f.read()
                self.markdown_viewer.setMarkdown(md_content)
            else:
                # 方法2：使用内置的默认 Markdown 内容（已更新链接）
                default_md = self.get_default_about_markdown()
                self.markdown_viewer.setMarkdown(default_md)
        except Exception as e:
            self.markdown_viewer.setPlainText(f"加载 Markdown 文件失败：{str(e)}")
    
    def get_default_about_markdown(self):
        """返回默认的关于 Markdown 内容（如果外部文件不存在时使用，已更新链接）"""
        return f"""
# MineCodes 我的世界指令助手

MineCodes 是一款开源的 Minecraft 指令辅助工具，旨在帮助玩家快速查询、构建和理解游戏指令。

## ✨ 主要功能

### 📋 指令查询
- 按分类浏览所有常用指令
- 实时搜索，快速定位
- 详细用法说明和示例

### 🎮 指令助手
- 通过表单构建复杂指令
- 一键复制到剪贴板
- 支持 40+ 常用指令类型

### 📦 物品百科
- 查询所有物品 ID 和详细信息
- 按类别浏览物品
- 获取合成配方、用途、掉落等信息

### 📝 实时解释
- 输入指令时自动解析含义
- 新手友好，一看就懂

## 🚀 使用方法

1. **指令查询**：在左侧列表点击指令，右侧显示详细用法
2. **搜索指令**：顶部搜索框输入关键词（如 `give`、`tp`）
3. **指令助手**：点击右上角“指令助手”按钮，打开独立工具
4. **物品查询**：点击“物品ID查询”按钮，查找物品信息

## 📅 版本历史

### v2.0 (2024-02)
- ✨ 全新界面设计
- ✨ 增加指令助手工具
- ✨ 增加物品百科工具
- ✨ 支持实时指令解释
- ✨ 数据与代码分离，便于更新

### v1.0 (2024-01)
- 🎉 首个版本发布
- 基础指令查询功能

## 👨‍💻 开发团队

- **设计/开发**：Zionyas-Van
- **特别感谢**：DeepSeek AI 辅助编程
- **开源协议**：MIT License

## 🔗 相关链接

- [GitHub 仓库](https://github.com/Zionyas-Van/MineCodes)
- [作者博客](https://zionyas-van.github.io/)
- [Minecraft Wiki](https://minecraft.fandom.com/zh/wiki/)
- [问题反馈](https://github.com/Zionyas-Van/MineCodes/issues)

---
*让指令更简单，让游戏更快乐！*
        """


def main():
    app = QApplication(sys.argv)
    
    # 设置图标
    icon_path = os.path.join(os.path.dirname(__file__), "data", "res", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    app.setFont(QFont("Microsoft YaHei", 9))
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()