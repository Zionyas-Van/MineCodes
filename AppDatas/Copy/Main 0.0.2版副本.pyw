import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QListWidget, QLabel,
                             QLineEdit, QTextEdit, QFrame, QSplitter,
                             QListWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon

# ===== 新增：隐藏控制台窗口（仅 Windows 下有效）=====
if sys.platform == 'win32':
    import ctypes
    # 获取控制台窗口句柄并隐藏
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
# ============================================

# 颜色定义
COLORS = {
    'bg': '#f5f5f7',           # 背景色
    'card': '#ffffff',          # 卡片背景
    'primary': '#1a73e8',       # 主色调（谷歌蓝）
    'primary_hover': '#1557b0', # 主色调悬停
    'text': '#202124',          # 文字颜色
    'text_secondary': '#5f6368',# 次要文字
    'border': '#dadce0',        # 边框颜色
    'success': '#34a853',       # 成功绿色
    'warning': '#f9ab00',       # 警告黄色
    'error': '#ea4335'          # 错误红色
}


class MinecraftCommandHelper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.all_commands = []  # 所有指令数据
        self.filtered_commands = []  # 过滤后的指令
        self.initUI()
        self.load_commands()
        
    def initUI(self):
        """初始化界面"""
        # ===== 修改：窗口标题改为 MineCodes =====
        self.setWindowTitle("MineCodes · 我的世界指令助手")
        # =====================================
        self.setMinimumSize(1000, 650)
        
        # 设置整体样式
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
                padding: 10px;
                border: 1px solid {COLORS['border']};
                border-radius: 20px;
                font-size: 14px;
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
        """)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ========== 顶部标题和搜索 ==========
        top_layout = QHBoxLayout()
        
        # 标题
        title = QLabel("⛏️ MineCodes")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 400;
            color: {COLORS['primary']};
        """)
        
        # 搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 搜索指令 (例如: give, tp, summon...)")
        self.search_box.textChanged.connect(self.filter_commands)
        
        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(self.search_box, 1)  # 搜索框占1份宽度
        
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
            
            # 默认选中"全部"
            if i == 0:
                btn.setChecked(True)
        
        categories_layout.addStretch()
        main_layout.addLayout(categories_layout)
        
        # ========== 主内容区（左右分栏） ==========
        content_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：指令列表
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
        
        # 列表标题
        list_header = QHBoxLayout()
        list_title = QLabel("📋 指令列表")
        list_title.setStyleSheet(f"font-size: 16px; font-weight: 500; color: {COLORS['text']};")
        self.count_label = QLabel("0 个指令")
        self.count_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        list_header.addWidget(list_title)
        list_header.addStretch()
        list_header.addWidget(self.count_label)
        left_layout.addLayout(list_header)
        
        # 指令列表
        self.command_list = QListWidget()
        self.command_list.itemClicked.connect(self.show_command_detail)
        left_layout.addWidget(self.command_list)
        
        # 右侧：指令详情
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
        
        # 详情标题
        detail_title = QLabel("📖 指令详情")
        detail_title.setStyleSheet(f"font-size: 16px; font-weight: 500; color: {COLORS['text']};")
        right_layout.addWidget(detail_title)
        
        # 详情内容
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        right_layout.addWidget(self.detail_text)
        
        # 添加到分割器
        content_splitter.addWidget(left_frame)
        content_splitter.addWidget(right_frame)
        content_splitter.setSizes([350, 650])  # 设置左右比例
        
        main_layout.addWidget(content_splitter)
        
        # 底部状态栏
        status_bar = self.statusBar()
        status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: white;
                border-top: 1px solid {COLORS['border']};
                color: {COLORS['text_secondary']};
            }}
        """)
        status_bar.showMessage("✨ 点击指令查看详细用法")
        
    def load_commands(self):
        """加载指令数据"""
        # Minecraft 指令数据 [command, description, usage, category]
        commands_data = [
            # 常用指令
            ["/give", "给予玩家物品", "/give <目标> <物品> [数量] [数据值] [NBT标签]\n\n示例：/give @p diamond 1 0 {display:{Name:'\"测试钻石\"'}}", "常用"],
            ["/tp", "传送实体", "/tp [目标玩家] <目标位置> 或 /tp <目标> <目的地>\n\n示例：/tp @p 100 64 100", "常用"],
            ["/summon", "召唤实体", "/summon <实体类型> [坐标] [NBT标签]\n\n示例：/summon creeper ~ ~ ~ {powered:1}", "常用"],
            ["/gamemode", "更改游戏模式", "/gamemode <模式> [玩家]\n模式：survival(生存), creative(创造), adventure(冒险), spectator(旁观)\n\n示例：/gamemode creative @p", "常用"],
            ["/time", "更改或查询时间", "/time set <时间值|day|night> 或 /time add <时间值>\n\n示例：/time set day", "常用"],
            ["/weather", "设置天气", "/weather <clear|rain|thunder> [持续时间]\n\n示例：/weather thunder 1000", "常用"],
            
            # 管理员指令
            ["/op", "授予管理员权限", "/op <玩家>\n\n示例：/op Steve", "管理员"],
            ["/deop", "撤销管理员权限", "/deop <玩家>\n\n示例：/deop Steve", "管理员"],
            ["/ban", "封禁玩家", "/ban <玩家> [原因]\n\n示例：/ban Steve 作弊", "管理员"],
            ["/pardon", "解封玩家", "/pardon <玩家>\n\n示例：/pardon Steve", "管理员"],
            ["/kick", "踢出玩家", "/kick <玩家> [原因]\n\n示例：/kick Steve 请遵守规则", "管理员"],
            ["/save-all", "保存世界", "/save-all\n\n保存所有世界数据到硬盘", "管理员"],
            ["/stop", "关闭服务器", "/stop\n\n安全关闭Minecraft服务器", "管理员"],
            
            # 世界指令
            ["/setworldspawn", "设置世界出生点", "/setworldspawn [坐标]\n\n示例：/setworldspawn 100 64 100", "世界"],
            ["/spawnpoint", "设置玩家出生点", "/spawnpoint [玩家] [坐标]\n\n示例：/spawnpoint @p 0 64 0", "世界"],
            ["/gamerule", "设置游戏规则", "/gamerule <规则> [值]\n\n常用规则：doDaylightCycle, keepInventory, mobGriefing\n\n示例：/gamerule keepInventory true", "世界"],
            ["/difficulty", "设置难度", "/difficulty <peaceful|easy|normal|hard>\n\n示例：/difficulty hard", "世界"],
            ["/seed", "查看世界种子", "/seed\n\n显示当前世界的种子码", "世界"],
            ["/locate", "查找结构", "/locate <结构>\n结构：village, temple, mansion, monument等\n\n示例：/locate village", "世界"],
            
            # 玩家指令
            ["/xp", "给予经验", "/xp <数量> [玩家] 或 /xp <数量>L [玩家]（等级）\n\n示例：/xp 100L @p", "玩家"],
            ["/effect", "添加状态效果", "/effect <玩家> <效果> [秒数] [倍数] [隐藏粒子]\n\n示例：/effect @p speed 60 2", "玩家"],
            ["/enchant", "附魔物品", "/enchant <玩家> <魔咒> [等级]\n\n示例：/enchant @p minecraft:sharpness 5", "玩家"],
            ["/clear", "清空物品栏", "/clear [玩家] [物品] [最大数量]\n\n示例：/clear @p minecraft:dirt", "玩家"],
            ["/say", "发送消息", "/say <消息>\n\n以服务器身份发送消息给所有人\n示例：/say 服务器即将重启", "玩家"],
            ["/me", "发送动作消息", "/me <动作>\n\n显示一个动作消息\n示例：/me 正在挖矿", "玩家"],
            ["/tell", "私聊消息", "/tell <玩家> <消息>\n\n向指定玩家发送私聊消息\n示例：/tell Steve 你好", "玩家"],
            
            # 战斗指令
            ["/kill", "杀死实体", "/kill [目标]\n\n杀死指定实体，不加目标杀死自己\n示例：/kill @e[type=minecraft:creeper]", "战斗"],
            ["/damage", "造成伤害", "/damage <目标> <伤害> [伤害类型]\n\n示例：/damage @p 10", "战斗"],
            ["/attribute", "修改属性", "/attribute <目标> <属性> <操作> [值]\n\n示例：/attribute @p minecraft:generic.max_health base set 40", "战斗"],
            
            # 物品指令
            ["/item", "修改物品", "/item <目标> <槽位> <物品>\n\n示例：/item @p weapon.mainhand minecraft:diamond_sword", "物品"],
            ["/replaceitem", "替换物品", "/replaceitem <目标> <槽位> <物品> [数量]\n\n示例：/replaceitem entity @p slot.hotbar.0 minecraft:apple 64", "物品"],
            ["/loot", "生成战利品", "/loot <目标> <来源>\n\n示例：/loot give @p loot minecraft:chests/simple_dungeon", "物品"],
        ]
        
        self.all_commands = []
        for cmd, desc, usage, cat in commands_data:
            self.all_commands.append({
                'command': cmd,
                'description': desc,
                'usage': usage,
                'category': cat
            })
        
        self.filtered_commands = self.all_commands.copy()
        self.update_command_list()
        
        # 默认选中第一个
        if self.command_list.count() > 0:
            self.command_list.setCurrentRow(0)
            self.show_command_detail(self.command_list.item(0))
    
    def update_command_list(self):
        """更新指令列表显示"""
        self.command_list.clear()
        for cmd in self.filtered_commands:
            item = QListWidgetItem(f"{cmd['command']} - {cmd['description']}")
            item.setData(Qt.UserRole, cmd)  # 存储完整数据
            self.command_list.addItem(item)
        
        # 更新计数
        self.count_label.setText(f"{len(self.filtered_commands)} 个指令")
    
    def filter_commands(self):
        """根据搜索框内容过滤指令"""
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
        
        # 重置分类按钮的选中状态
        for btn in self.category_btns:
            if btn.property("category") == "all":
                btn.setChecked(True)
            else:
                btn.setChecked(False)
    
    def filter_by_category(self, category):
        """根据分类过滤指令"""
        if category == "all":
            self.filtered_commands = self.all_commands.copy()
        else:
            self.filtered_commands = [
                cmd for cmd in self.all_commands 
                if cmd['category'] == category
            ]
        
        self.update_command_list()
        self.search_box.clear()  # 清空搜索框
        
        # 如果有指令，选中第一个
        if self.command_list.count() > 0:
            self.command_list.setCurrentRow(0)
            self.show_command_detail(self.command_list.item(0))
    
    def show_command_detail(self, item):
        """显示指令详情"""
        cmd_data = item.data(Qt.UserRole)
        
        # 格式化详情显示
        detail = f"""
        <style>
            .command {{
                font-size: 28px;
                font-weight: bold;
                color: {COLORS['primary']};
                margin-bottom: 10px;
            }}
            .description {{
                font-size: 16px;
                color: {COLORS['text']};
                margin-bottom: 20px;
            }}
            .usage-title {{
                font-size: 18px;
                font-weight: 500;
                color: {COLORS['text']};
                margin-top: 20px;
                margin-bottom: 10px;
            }}
            .usage {{
                background-color: {COLORS['bg']};
                padding: 15px;
                border-radius: 8px;
                font-family: monospace;
                font-size: 14px;
                color: {COLORS['text']};
                white-space: pre-wrap;
                line-height: 1.6;
            }}
            .category {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 16px;
                background-color: {COLORS['primary']}20;
                color: {COLORS['primary']};
                font-size: 12px;
                margin-top: 10px;
            }}
        </style>
        
        <div class="command">{cmd_data['command']}</div>
        <div class="description">{cmd_data['description']}</div>
        <div class="usage-title">📌 用法说明</div>
        <div class="usage">{cmd_data['usage'].replace(chr(10), '<br>')}</div>
        <div class="category">{cmd_data['category']}</div>
        """
        
        self.detail_text.setHtml(detail)


def main():
    app = QApplication(sys.argv)
    
    # 设置字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    window = MinecraftCommandHelper()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()