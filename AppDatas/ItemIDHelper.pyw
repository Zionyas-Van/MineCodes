#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
物品ID查询工具 - MineCodes 配套程序
版本：支持从JSON读取详情，兼容旧格式
"""

import sys
import json
import os
from PyQt5.QtGui import QIcon

if sys.platform == 'win32':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QFrame, QSplitter, QListWidget, QListWidgetItem,
                             QMessageBox, QTextBrowser)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QClipboard

COLORS = {
    'bg': '#f5f5f7',
    'card': '#ffffff',
    'primary': '#1a73e8',
    'primary_hover': '#1557b0',
    'text': '#202124',
    'text_secondary': '#5f6368',
    'border': '#dadce0',
}


class ItemIDHelper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.all_items = []
        self.filtered_items = []
        self.current_item = None
        self.initUI()
        self.load_items()
    
    def initUI(self):
        self.setWindowTitle("MineCodes · 物品百科")
        self.setMinimumSize(1000, 650)
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['bg']};
            }}
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #1557b0;
            }}
            QPushButton.secondary {{
                background-color: transparent;
                color: {COLORS['primary']};
                border: 1px solid {COLORS['border']};
            }}
            QPushButton.secondary:hover {{
                background-color: {COLORS['primary']}10;
            }}
            QLineEdit {{
                padding: 10px 15px;
                border: 1px solid {COLORS['border']};
                border-radius: 25px;
                font-size: 14px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
            }}
            QListWidget {{
                background-color: white;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 5px;
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 10px 12px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QListWidget::item:last {{
                border-bottom: none;
            }}
            QListWidget::item:hover {{
                background-color: #f1f3f4;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QTextBrowser {{
                background-color: white;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }}
            QLabel#count {{
                color: {COLORS['text_secondary']};
                font-size: 12px;
                padding: 5px;
            }}
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)                     # 减小垂直间距
        main_layout.setContentsMargins(20, 10, 20, 20) # 减小上边距
        
        # 标题居中
        top_layout = QHBoxLayout()
        title = QLabel("MineCodes · 物品百科")
        title.setStyleSheet(f"font-size: 22px; font-weight: 400; color: {COLORS['primary']};")
        title.setAlignment(Qt.AlignCenter)
        top_layout.addStretch()
        top_layout.addWidget(title)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)
        
        # 搜索框
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 输入物品名称或ID进行搜索...")
        self.search_box.textChanged.connect(self.filter_items)
        search_layout.addWidget(self.search_box)
        
        self.count_label = QLabel("加载中...")
        self.count_label.setObjectName("count")
        search_layout.addWidget(self.count_label)
        main_layout.addLayout(search_layout)
        
        # 主内容区
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧列表
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("📋 物品列表"))
        self.item_list = QListWidget()
        self.item_list.itemClicked.connect(self.on_item_selected)
        left_layout.addWidget(self.item_list)
        
        # 右侧详情
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(QLabel("📖 详细信息"))
        self.detail_view = QTextBrowser()
        right_layout.addWidget(self.detail_view)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        self.copy_give_btn = QPushButton("🎁 复制获取指令 (/give @s ...)")
        self.copy_give_btn.clicked.connect(self.copy_give_command)
        self.copy_id_btn = QPushButton("📋 复制ID")
        self.copy_id_btn.setProperty("class", "secondary")
        self.copy_id_btn.clicked.connect(self.copy_item_id)
        btn_layout.addWidget(self.copy_give_btn)
        btn_layout.addWidget(self.copy_id_btn)
        btn_layout.addStretch()
        right_layout.addLayout(btn_layout)
        
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([350, 650])
        main_layout.addWidget(splitter)
        
        self.statusBar().showMessage("✨ 点击物品查看详细信息")
    
    def load_items(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "items.json")
        
        try:
            with open(json_path, "r", encoding="utf-8-sig") as f:
                categories = json.load(f)
        except FileNotFoundError:
            QMessageBox.critical(self, "错误", f"找不到物品数据文件：{json_path}")
            return
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取物品数据文件失败：{str(e)}")
            return
        
        self.all_items = []
        for cat, items in categories.items():
            for item_data in items:
                # 兼容旧格式 [name, id] 和新格式 {"name":..., "id":..., "detail":...}
                if isinstance(item_data, list) and len(item_data) >= 2:
                    name = item_data[0]
                    item_id = item_data[1]
                    detail = self.generate_item_detail(name, item_id, cat)
                elif isinstance(item_data, dict):
                    name = item_data.get('name', '未知')
                    item_id = item_data.get('id', '')
                    detail = item_data.get('detail', self.generate_item_detail(name, item_id, cat))
                else:
                    continue
                
                self.all_items.append({
                    'category': cat,
                    'name': name,
                    'id': item_id,
                    'detail': detail
                })
        
        self.all_items.sort(key=lambda x: x['name'])
        self.filtered_items = self.all_items.copy()
        self.update_item_list()
        self.count_label.setText(f"共 {len(self.filtered_items)} 个物品")
    
    def generate_item_detail(self, name, item_id, category):
        """生成默认详情（用于旧格式数据或备用）"""
        detail = f"""
        <style>
            .item-name {{ font-size: 24px; font-weight: bold; color: {COLORS['primary']}; margin-bottom: 10px; }}
            .item-id {{ font-family: monospace; background-color: {COLORS['bg']}; padding: 5px 10px; border-radius: 4px; margin: 10px 0; }}
            .section-title {{ font-size: 18px; font-weight: 500; color: {COLORS['text']}; margin-top: 20px; margin-bottom: 10px; border-left: 4px solid {COLORS['primary']}; padding-left: 10px; }}
            .info-line {{ margin: 5px 0; }}
            .badge {{ display: inline-block; background-color: {COLORS['primary']}20; color: {COLORS['primary']}; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-right: 5px; }}
        </style>
        
        <div class="item-name">{name}</div>
        <div class="item-id">ID：{item_id}</div>
        <div class="badge">{category}</div>
        """
        
        if "方块" in category:
            detail += """
            <div class="section-title">📦 方块信息</div>
            <div class="info-line">• <b>类型：</b>固体方块</div>
            <div class="info-line">• <b>爆炸抗性：</b>6</div>
            <div class="info-line">• <b>硬度：</b>1.5</div>
            <div class="info-line">• <b>合适工具：</b>镐</div>
            """
        elif "工具" in category or "武器" in category:
            detail += """
            <div class="section-title">⚔️ 工具信息</div>
            <div class="info-line">• <b>类型：</b>工具/武器</div>
            <div class="info-line">• <b>耐久度：</b>250</div>
            <div class="info-line">• <b>攻击伤害：</b>6</div>
            """
        elif "食物" in category:
            detail += """
            <div class="section-title">🍖 食物信息</div>
            <div class="info-line">• <b>类型：</b>食物</div>
            <div class="info-line">• <b>饥饿值恢复：</b>4点</div>
            """
        elif "生物" in category or "刷怪蛋" in category:
            detail += """
            <div class="section-title">🐾 生物信息</div>
            <div class="info-line">• <b>类型：</b>被动型生物</div>
            <div class="info-line">• <b>生命值：</b>❤️ 20</div>
            <div class="info-line">• <b>掉落物：</b>0-2 经验</div>
            """
        
        # 获取途径
        detail += f"""
        <div class="section-title">🎯 获取途径</div>
        <div class="info-line">• <b>合成：</b>可以使用工作台合成</div>
        <div class="info-line">• <b>挖掘：</b>破坏对应方块获得</div>
        <div class="info-line">• <b>生物掉落：</b>击杀生物概率掉落</div>
        <div class="info-line">• <b>指令：</b><code>/give @s {item_id}</code></div>
        
        <div class="section-title">📜 用途</div>
        <div class="info-line">• 可用于合成其他物品</div>
        <div class="info-line">• 可作为建筑材料</div>
        
        <div class="section-title">📅 版本历史</div>
        <div class="info-line">• <b>首次加入：</b>Java版 1.0.0</div>
        """
        return detail
    
    def update_item_list(self):
        self.item_list.clear()
        for item in self.filtered_items:
            list_item = QListWidgetItem(f"{item['name']}  ({item['id']})")
            list_item.setData(Qt.UserRole, item)
            self.item_list.addItem(list_item)
    
    def filter_items(self):
        text = self.search_box.text().strip().lower()
        if not text:
            self.filtered_items = self.all_items.copy()
        else:
            self.filtered_items = [
                item for item in self.all_items
                if text in item['name'].lower() or text in item['id'].lower()
            ]
        self.update_item_list()
        self.count_label.setText(f"共 {len(self.filtered_items)} 个物品")
        if self.filtered_items and self.item_list.count() > 0:
            self.item_list.setCurrentRow(0)
            self.on_item_selected(self.item_list.item(0))
    
    def on_item_selected(self, item):
        item_data = item.data(Qt.UserRole)
        if item_data:
            self.current_item = item_data
            self.detail_view.setHtml(item_data['detail'])
    
    def copy_give_command(self):
        if not self.current_item:
            QMessageBox.warning(self, "提示", "请先选择一个物品")
            return
        cmd = f"/give @s {self.current_item['id']}"
        QApplication.clipboard().setText(cmd)
        QMessageBox.information(self, "提示", f"已复制指令：{cmd}")
    
    def copy_item_id(self):
        if not self.current_item:
            QMessageBox.warning(self, "提示", "请先选择一个物品")
            return
        QApplication.clipboard().setText(self.current_item['id'])
        QMessageBox.information(self, "提示", f"已复制物品ID：{self.current_item['id']}")


def main():
    app = QApplication(sys.argv)
    
    # 设置图标
    icon_path = os.path.join(os.path.dirname(__file__), "data", "res", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    app.setFont(QFont("Microsoft YaHei", 9))
    window = ItemIDHelper()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()