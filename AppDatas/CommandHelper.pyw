#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
指令助手 - MineCodes 配套程序
升级版：增加更多常用指令，采用标签页分类，界面更友好
"""

import sys
import traceback
from PyQt5.QtGui import QIcon
import os

# 错误日志文件
log_file = "command_helper_error.log"

def handle_exception(exc_type, exc_value, exc_traceback):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    # 仍然调用默认的异常处理（可能不会显示）
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = handle_exception

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTabWidget,
                             QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
                             QComboBox, QGridLayout, QTextEdit, QMessageBox,
                             QGroupBox, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QClipboard

# ===== 隐藏控制台窗口 =====
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# 颜色定义（与主程序保持一致）
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


class CommandCard(QWidget):
    """指令卡片 - 每个指令一个独立卡片"""
    def __init__(self, title, description, build_func):
        super().__init__()
        self.build_func = build_func  # 构建指令的函数
        self.params = {}  # 存储参数控件
        
        # 卡片样式
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }}
            QLabel.title {{
                font-size: 16px;
                font-weight: bold;
                color: {COLORS['primary']};
            }}
            QLabel.desc {{
                color: {COLORS['text_secondary']};
                font-size: 12px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # 标题行
        title_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setProperty("class", "title")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a73e8;")
        desc_label = QLabel(description)
        desc_label.setProperty("class", "desc")
        desc_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(desc_label)
        layout.addLayout(title_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px;")
        layout.addWidget(line)
        
        # 参数区域
        self.param_widget = QWidget()
        self.param_layout = QGridLayout(self.param_widget)
        self.param_layout.setVerticalSpacing(8)
        self.param_layout.setHorizontalSpacing(10)
        layout.addWidget(self.param_widget)
        
        # 预览区域（放在卡片底部）
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("预览:"))
        self.preview_label = QLineEdit()
        self.preview_label.setReadOnly(True)
        self.preview_label.setStyleSheet(f"""
            background-color: {COLORS['bg']};
            border: 1px solid {COLORS['border']};
            border-radius: 4px;
            padding: 5px;
            font-family: monospace;
        """)
        preview_layout.addWidget(self.preview_label)
        
        self.copy_btn = QPushButton("📋 复制")
        self.copy_btn.setFixedWidth(60)
        self.copy_btn.clicked.connect(self.copy_command)
        preview_layout.addWidget(self.copy_btn)
        
        layout.addLayout(preview_layout)
        
        # 调用构建函数生成参数控件
        if build_func:
            build_func(self)
        
        # 初始更新预览
        self.update_preview()
    
    def add_param(self, label, control, row, col=0, colspan=1):
        """添加参数控件"""
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: {COLORS['text']};")
        self.param_layout.addWidget(label_widget, row, col*2)
        self.param_layout.addWidget(control, row, col*2+1, 1, colspan)
        
        # 连接信号
        if isinstance(control, (QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox)):
            if isinstance(control, QLineEdit):
                control.textChanged.connect(self.update_preview)
            elif isinstance(control, (QSpinBox, QDoubleSpinBox)):
                control.valueChanged.connect(self.update_preview)
            elif isinstance(control, QComboBox):
                control.currentIndexChanged.connect(self.update_preview)
            elif isinstance(control, QCheckBox):
                control.stateChanged.connect(self.update_preview)
        
        return control
    
    def update_preview(self):
        """更新预览（由子类实现或通过build_func设置）"""
        pass
    
    def copy_command(self):
        """复制指令"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.preview_label.text())
        QMessageBox.information(self, "提示", "指令已复制到剪贴板")


class CommandHelper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MineCodes · 指令助手 Pro")
        self.setMinimumSize(900, 700)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['bg']};
            }}
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background-color: {COLORS['card']};
            }}
            QTabBar::tab {{
                background-color: transparent;
                color: {COLORS['text']};
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {COLORS['primary']}20;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("🎮 指令助手 Pro")
        title.setStyleSheet(f"font-size: 24px; font-weight: 400; color: {COLORS['primary']};")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # 说明文字
        desc = QLabel("选择指令类型，填写参数即可生成完整的Minecraft指令")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(f"color: {COLORS['text_secondary']}; margin-bottom: 10px;")
        main_layout.addWidget(desc)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 添加各个分类的标签页
        self.setup_basic_tab()      # 基础指令
        self.setup_teleport_tab()    # 传送与位置
        self.setup_world_tab()       # 世界与时间
        self.setup_item_tab()        # 物品与装备
        self.setup_mob_tab()         # 生物与效果
        self.setup_admin_tab()       # 管理员指令
        self.setup_adv_tab()         # 高级指令
    
    def setup_basic_tab(self):
        """基础指令标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 使用滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 游戏模式指令
        gamemode_card = CommandCard("/gamemode", "切换游戏模式", self.build_gamemode)
        scroll_layout.addWidget(gamemode_card)
        
        # 难度指令
        difficulty_card = CommandCard("/difficulty", "设置游戏难度", self.build_difficulty)
        scroll_layout.addWidget(difficulty_card)
        
        # 击杀指令
        kill_card = CommandCard("/kill", "杀死实体", self.build_kill)
        scroll_layout.addWidget(kill_card)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "⭐ 基础")
    
    def setup_teleport_tab(self):
        """传送与位置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 传送指令
        tp_card = CommandCard("/tp", "传送实体", self.build_tp)
        scroll_layout.addWidget(tp_card)
        
        # 传送指定玩家
        tp_other_card = CommandCard("/tp (玩家间传送)", "将玩家传送到另一个玩家", self.build_tp_other)
        scroll_layout.addWidget(tp_other_card)
        
        # 生成点设置
        spawnpoint_card = CommandCard("/spawnpoint", "设置玩家出生点", self.build_spawnpoint)
        scroll_layout.addWidget(spawnpoint_card)
        
        # 世界出生点
        setworldspawn_card = CommandCard("/setworldspawn", "设置世界出生点", self.build_setworldspawn)
        scroll_layout.addWidget(setworldspawn_card)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "📍 传送")
    
    def setup_world_tab(self):
        """世界与时间标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 时间指令
        time_card = CommandCard("/time", "调整游戏时间", self.build_time)
        scroll_layout.addWidget(time_card)
        
        # 天气指令
        weather_card = CommandCard("/weather", "改变天气", self.build_weather)
        scroll_layout.addWidget(weather_card)
        
        # 游戏规则
        gamerule_card = CommandCard("/gamerule", "修改游戏规则", self.build_gamerule)
        scroll_layout.addWidget(gamerule_card)
        
        # 查找结构
        locate_card = CommandCard("/locate", "查找附近结构", self.build_locate)
        scroll_layout.addWidget(locate_card)
        
        # 世界种子
        seed_card = CommandCard("/seed", "查看世界种子", self.build_seed)
        scroll_layout.addWidget(seed_card)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "🌍 世界")
    
    def setup_item_tab(self):
        """物品与装备标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 给予物品
        give_card = CommandCard("/give", "给予玩家物品", self.build_give)
        scroll_layout.addWidget(give_card)
        
        # 附魔
        enchant_card = CommandCard("/enchant", "附魔手中物品", self.build_enchant)
        scroll_layout.addWidget(enchant_card)
        
        # 经验
        xp_card = CommandCard("/xp", "给予经验", self.build_xp)
        scroll_layout.addWidget(xp_card)
        
        # 清空物品栏
        clear_card = CommandCard("/clear", "清空物品栏", self.build_clear)
        scroll_layout.addWidget(clear_card)
        
        # 替换物品
        replaceitem_card = CommandCard("/replaceitem", "替换物品栏物品", self.build_replaceitem)
        scroll_layout.addWidget(replaceitem_card)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "📦 物品")
    
    def setup_mob_tab(self):
        """生物与效果标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 召唤生物
        summon_card = CommandCard("/summon", "召唤生物或实体", self.build_summon)
        scroll_layout.addWidget(summon_card)
        
        # 状态效果
        effect_card = CommandCard("/effect", "添加或移除状态效果", self.build_effect)
        scroll_layout.addWidget(effect_card)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "👾 生物")
    
    def setup_admin_tab(self):
        """管理员指令标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 给予OP
        op_card = CommandCard("/op", "给予管理员权限", self.build_op)
        scroll_layout.addWidget(op_card)
        
        # 踢出玩家
        kick_card = CommandCard("/kick", "踢出玩家", self.build_kick)
        scroll_layout.addWidget(kick_card)
        
        # 封禁玩家
        ban_card = CommandCard("/ban", "封禁玩家", self.build_ban)
        scroll_layout.addWidget(ban_card)
        
        # 白名单
        whitelist_card = CommandCard("/whitelist", "管理白名单", self.build_whitelist)
        scroll_layout.addWidget(whitelist_card)
        
        # 保存世界
        saveall_card = CommandCard("/save-all", "保存世界", self.build_saveall)
        scroll_layout.addWidget(saveall_card)
        
        # 停止服务器
        stop_card = CommandCard("/stop", "关闭服务器", self.build_stop)
        scroll_layout.addWidget(stop_card)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "👑 管理员")
    
    def setup_adv_tab(self):
        """高级指令标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 填充方块
        fill_card = CommandCard("/fill", "填充方块区域", self.build_fill)
        scroll_layout.addWidget(fill_card)
        
        # 克隆区域
        clone_card = CommandCard("/clone", "复制方块区域", self.build_clone)
        scroll_layout.addWidget(clone_card)
        
        # 设置方块
        setblock_card = CommandCard("/setblock", "放置单个方块", self.build_setblock)
        scroll_layout.addWidget(setblock_card)
        
        # 执行指令
        execute_card = CommandCard("/execute", "以其他实体身份执行指令", self.build_execute)
        scroll_layout.addWidget(execute_card)
        
        # 标题显示
        title_card = CommandCard("/title", "显示屏幕标题", self.build_title)
        scroll_layout.addWidget(title_card)
        
        # 粒子效果
        particle_card = CommandCard("/particle", "生成粒子效果", self.build_particle)
        scroll_layout.addWidget(particle_card)
        
        # 播放音效
        playsound_card = CommandCard("/playsound", "播放音效", self.build_playsound)
        scroll_layout.addWidget(playsound_card)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "⚡ 高级")
    
    # ========== 各个指令的构建函数 ==========
    
    def build_gamemode(self, card):
        """构建游戏模式指令"""
        card.params['target'] = card.add_param("目标玩家:", QLineEdit("@p"), 0)
        card.params['mode'] = card.add_param("游戏模式:", QComboBox(), 1)
        mode_combo = card.params['mode']
        mode_combo.addItems(["survival (生存)", "creative (创造)", "adventure (冒险)", "spectator (旁观)"])
        
        def update():
            mode_map = {
                "survival (生存)": "survival",
                "creative (创造)": "creative",
                "adventure (冒险)": "adventure",
                "spectator (旁观)": "spectator"
            }
            mode = mode_map[mode_combo.currentText()]
            target = card.params['target'].text()
            card.preview_label.setText(f"/gamemode {mode} {target}")
        
        card.update_preview = update
        mode_combo.currentIndexChanged.connect(update)
        card.params['target'].textChanged.connect(update)
        update()
    
    def build_difficulty(self, card):
        """构建难度指令"""
        card.params['difficulty'] = card.add_param("难度:", QComboBox(), 0)
        diff_combo = card.params['difficulty']
        diff_combo.addItems(["peaceful (和平)", "easy (简单)", "normal (普通)", "hard (困难)"])
        
        def update():
            diff_map = {
                "peaceful (和平)": "peaceful",
                "easy (简单)": "easy",
                "normal (普通)": "normal",
                "hard (困难)": "hard"
            }
            diff = diff_map[diff_combo.currentText()]
            card.preview_label.setText(f"/difficulty {diff}")
        
        card.update_preview = update
        diff_combo.currentIndexChanged.connect(update)
        update()
    
    def build_kill(self, card):
        """构建击杀指令"""
        card.params['target'] = card.add_param("目标实体:", QLineEdit("@p"), 0)
        card.add_param("(留空杀死自己)", QLabel(""), 1)
        
        def update():
            target = card.params['target'].text().strip()
            if target:
                card.preview_label.setText(f"/kill {target}")
            else:
                card.preview_label.setText("/kill")
        
        card.update_preview = update
        card.params['target'].textChanged.connect(update)
        update()
    
    def build_tp(self, card):
        """构建传送指令"""
        card.params['target'] = card.add_param("目标玩家:", QLineEdit("@p"), 0)
        card.params['x'] = card.add_param("X坐标:", QLineEdit("~"), 1, 0)
        card.params['y'] = card.add_param("Y坐标:", QLineEdit("~"), 1, 1)
        card.params['z'] = card.add_param("Z坐标:", QLineEdit("~"), 1, 2)
        
        def update():
            target = card.params['target'].text()
            x = card.params['x'].text()
            y = card.params['y'].text()
            z = card.params['z'].text()
            card.preview_label.setText(f"/tp {target} {x} {y} {z}")
        
        card.update_preview = update
        for w in [card.params['target'], card.params['x'], card.params['y'], card.params['z']]:
            w.textChanged.connect(update)
        update()
    
    def build_tp_other(self, card):
        """构建玩家间传送指令"""
        card.params['target1'] = card.add_param("被传送的玩家:", QLineEdit("@p"), 0)
        card.params['target2'] = card.add_param("传送目的地玩家:", QLineEdit("Steve"), 1)
        
        def update():
            t1 = card.params['target1'].text()
            t2 = card.params['target2'].text()
            card.preview_label.setText(f"/tp {t1} {t2}")
        
        card.update_preview = update
        card.params['target1'].textChanged.connect(update)
        card.params['target2'].textChanged.connect(update)
        update()
    
    def build_spawnpoint(self, card):
        """设置玩家出生点"""
        card.params['target'] = card.add_param("目标玩家:", QLineEdit("@p"), 0)
        card.params['x'] = card.add_param("X坐标(可选):", QLineEdit("~"), 1, 0)
        card.params['y'] = card.add_param("Y坐标(可选):", QLineEdit("~"), 1, 1)
        card.params['z'] = card.add_param("Z坐标(可选):", QLineEdit("~"), 1, 2)
        
        def update():
            target = card.params['target'].text()
            x = card.params['x'].text()
            y = card.params['y'].text()
            z = card.params['z'].text()
            # 如果坐标都是"~"，可以省略坐标
            if x == "~" and y == "~" and z == "~":
                card.preview_label.setText(f"/spawnpoint {target}")
            else:
                card.preview_label.setText(f"/spawnpoint {target} {x} {y} {z}")
        
        card.update_preview = update
        for w in [card.params['target'], card.params['x'], card.params['y'], card.params['z']]:
            w.textChanged.connect(update)
        update()
    
    def build_setworldspawn(self, card):
        """设置世界出生点"""
        card.params['x'] = card.add_param("X坐标(可选):", QLineEdit("~"), 0, 0)
        card.params['y'] = card.add_param("Y坐标(可选):", QLineEdit("~"), 0, 1)
        card.params['z'] = card.add_param("Z坐标(可选):", QLineEdit("~"), 0, 2)
        
        def update():
            x = card.params['x'].text()
            y = card.params['y'].text()
            z = card.params['z'].text()
            # 如果都是"~"，直接/setworldspawn
            if x == "~" and y == "~" and z == "~":
                card.preview_label.setText("/setworldspawn")
            else:
                card.preview_label.setText(f"/setworldspawn {x} {y} {z}")
        
        card.update_preview = update
        for w in [card.params['x'], card.params['y'], card.params['z']]:
            w.textChanged.connect(update)
        update()
    
    def build_time(self, card):
        """构建时间指令"""
        card.params['operation'] = card.add_param("操作:", QComboBox(), 0)
        op_combo = card.params['operation']
        op_combo.addItems(["set (设置为)", "add (增加)"])
    
        card.params['value'] = card.add_param("时间值:", QComboBox(), 1)
        value_combo = card.params['value']
        value_combo.setEditable(True)
        value_combo.addItems(["day (白天)", "night (晚上)", "noon (正午)", "midnight (午夜)", "1000", "6000", "13000"])

        def update():
            op = "set" if "set" in op_combo.currentText() else "add"
            val_text = value_combo.currentText()
            if " " in val_text:
                val = val_text.split()[0]
            else:
                val = val_text
            card.preview_label.setText(f"/time {op} {val}")

        card.update_preview = update
        op_combo.currentIndexChanged.connect(update)
        value_combo.currentIndexChanged.connect(update)
        value_combo.lineEdit().textChanged.connect(update)
        update()
    
    def build_weather(self, card):
        """构建天气指令"""
        card.params['type'] = card.add_param("天气类型:", QComboBox(), 0)
        weather_combo = card.params['type']
        weather_combo.addItems(["clear (晴天)", "rain (雨天)", "thunder (雷雨)"])
        
        card.params['duration'] = card.add_param("持续时间(秒，可选):", QSpinBox(), 1)
        duration_spin = card.params['duration']
        duration_spin.setRange(1, 1000000)
        duration_spin.setSpecialValueText("默认")
        duration_spin.setValue(1)
        
        def update():
            w_map = {
                "clear (晴天)": "clear",
                "rain (雨天)": "rain",
                "thunder (雷雨)": "thunder"
            }
            weather = w_map[weather_combo.currentText()]
            duration = duration_spin.value()
            if duration == 1 and duration_spin.specialValueText() == "默认":
                card.preview_label.setText(f"/weather {weather}")
            else:
                card.preview_label.setText(f"/weather {weather} {duration}")
        
        card.update_preview = update
        weather_combo.currentIndexChanged.connect(update)
        duration_spin.valueChanged.connect(update)
        update()
    
    def build_gamerule(self, card):
        """构建游戏规则指令"""
        # 常用规则列表
        rules = [
            "keepInventory (死亡不掉落)",
            "doDaylightCycle (日夜循环)",
            "doMobSpawning (生物生成)",
            "doWeatherCycle (天气变化)",
            "pvp (玩家伤害)",
            "commandBlockOutput (命令方块输出)",
            "sendCommandFeedback (命令反馈)",
            "randomTickSpeed (随机刻速度)",
            "maxEntityCramming (实体挤压)",
            "doFireTick (火焰蔓延)",
            "doMobLoot (生物掉落)",
            "doTileDrops (方块掉落)"
        ]
        
        card.params['rule'] = card.add_param("游戏规则:", QComboBox(), 0)
        rule_combo = card.params['rule']
        rule_combo.addItems(rules)
        
        card.params['value'] = card.add_param("值:", QComboBox(), 1)
        value_combo = card.params['value']
        value_combo.addItems(["true (开启)", "false (关闭)"])
        value_combo.setEditable(True)
        
        def update():
            rule_text = rule_combo.currentText()
            rule = rule_text.split()[0] if " " in rule_text else rule_text
            val_text = value_combo.currentText()
            val = val_text.split()[0] if " " in val_text else val_text
            card.preview_label.setText(f"/gamerule {rule} {val}")
        
        card.update_preview = update
        rule_combo.currentIndexChanged.connect(update)
        value_combo.currentIndexChanged.connect(update)
        value_combo.lineEdit().textChanged.connect(update)
        update()
    
    def build_locate(self, card):
        """查找结构指令"""
        structures = [
            "village (村庄)",
            "temple (神庙)",
            "mansion (林地府邸)",
            "monument (海底神殿)",
            "stronghold (要塞)",
            "endcity (末地城)",
            "fortress (下界要塞)",
            "bastion (堡垒遗迹)",
            "ruined_portal (废弃传送门)",
            "shipwreck (沉船)",
            "ocean_ruin (海底废墟)"
        ]
        
        card.params['structure'] = card.add_param("结构类型:", QComboBox(), 0)
        struct_combo = card.params['structure']
        struct_combo.addItems(structures)
        
        def update():
            struct_text = struct_combo.currentText()
            struct = struct_text.split()[0]
            card.preview_label.setText(f"/locate {struct}")
        
        card.update_preview = update
        struct_combo.currentIndexChanged.connect(update)
        update()
    
    def build_seed(self, card):
        """查看世界种子"""
        def update():
            card.preview_label.setText("/seed")
        card.update_preview = update
        update()
    
    def build_give(self, card):
        """给予物品指令"""
        card.params['target'] = card.add_param("目标玩家:", QLineEdit("@p"), 0)
        card.params['item'] = card.add_param("物品ID:", QLineEdit("minecraft:diamond"), 1)
        card.params['count'] = card.add_param("数量:", QSpinBox(), 2)
        count_spin = card.params['count']
        count_spin.setRange(1, 64)
        count_spin.setValue(1)
        
        def update():
            target = card.params['target'].text()
            item = card.params['item'].text()
            count = card.params['count'].value()
            card.preview_label.setText(f"/give {target} {item} {count}")
        
        card.update_preview = update
        card.params['target'].textChanged.connect(update)
        card.params['item'].textChanged.connect(update)
        card.params['count'].valueChanged.connect(update)
        update()
    
    def build_enchant(self, card):
        """附魔指令"""
        card.params['target'] = card.add_param("目标玩家:", QLineEdit("@p"), 0)
        
        enchants = [
            "sharpness (锋利)",
            "protection (保护)",
            "unbreaking (耐久)",
            "fortune (时运)",
            "silk_touch (精准采集)",
            "power (力量)",
            "flame (火矢)",
            "infinity (无限)",
            "mending (经验修补)",
            "looting (抢夺)",
            "fire_aspect (火焰附加)",
            "knockback (击退)"
        ]
        
        card.params['enchant'] = card.add_param("魔咒:", QComboBox(), 1)
        enchant_combo = card.params['enchant']
        enchant_combo.addItems(enchants)
        
        card.params['level'] = card.add_param("等级:", QSpinBox(), 2)
        level_spin = card.params['level']
        level_spin.setRange(1, 5)
        level_spin.setValue(1)
        
        def update():
            target = card.params['target'].text()
            enchant_text = enchant_combo.currentText()
            enchant = enchant_text.split()[0]
            level = card.params['level'].value()
            card.preview_label.setText(f"/enchant {target} {enchant} {level}")
        
        card.update_preview = update
        card.params['target'].textChanged.connect(update)
        enchant_combo.currentIndexChanged.connect(update)
        card.params['level'].valueChanged.connect(update)
        update()
    
    def build_xp(self, card):
        """经验指令"""
        card.params['operation'] = card.add_param("操作类型:", QComboBox(), 0)
        op_combo = card.params['operation']
        op_combo.addItems(["增加经验值", "增加经验等级", "扣除经验值", "扣除经验等级"])
        
        card.params['amount'] = card.add_param("数量:", QSpinBox(), 1)
        amount_spin = card.params['amount']
        amount_spin.setRange(1, 10000)
        amount_spin.setValue(100)
        
        card.params['target'] = card.add_param("目标玩家:", QLineEdit("@p"), 2)
        
        def update():
            op = op_combo.currentIndex()
            amount = card.params['amount'].value()
            target = card.params['target'].text()
            
            if op == 0:  # 增加经验值
                card.preview_label.setText(f"/xp {amount} {target}")
            elif op == 1:  # 增加经验等级
                card.preview_label.setText(f"/xp {amount}L {target}")
            elif op == 2:  # 扣除经验值
                card.preview_label.setText(f"/xp -{amount} {target}")
            else:  # 扣除经验等级
                card.preview_label.setText(f"/xp -{amount}L {target}")
        
        card.update_preview = update
        op_combo.currentIndexChanged.connect(update)
        card.params['amount'].valueChanged.connect(update)
        card.params['target'].textChanged.connect(update)
        update()
    
    def build_clear(self, card):
        """清空物品栏"""
        card.params['target'] = card.add_param("目标玩家(可选):", QLineEdit("@p"), 0)
        card.params['item'] = card.add_param("特定物品(可选):", QLineEdit(), 1)
        card.params['max_count'] = card.add_param("最大数量(可选):", QSpinBox(), 2)
        count_spin = card.params['max_count']
        count_spin.setRange(1, 64)
        count_spin.setSpecialValueText("全部")
        count_spin.setValue(1)
        
        def update():
            target = card.params['target'].text()
            item = card.params['item'].text().strip()
            max_count = card.params['max_count'].value()
            
            if not item:
                card.preview_label.setText(f"/clear {target}")
            elif max_count == 1 and count_spin.specialValueText() == "全部":
                card.preview_label.setText(f"/clear {target} {item}")
            else:
                card.preview_label.setText(f"/clear {target} {item} {max_count}")
        
        card.update_preview = update
        card.params['target'].textChanged.connect(update)
        card.params['item'].textChanged.connect(update)
        count_spin.valueChanged.connect(update)
        update()
    
    def build_replaceitem(self, card):
        """替换物品栏物品"""
        card.params['target'] = card.add_param("目标玩家:", QLineEdit("@p"), 0)
        
        slots = [
            "slot.hotbar.0 (快捷栏1)",
            "slot.hotbar.1 (快捷栏2)",
            "slot.hotbar.2 (快捷栏3)",
            "slot.hotbar.3 (快捷栏4)",
            "slot.hotbar.4 (快捷栏5)",
            "slot.hotbar.5 (快捷栏6)",
            "slot.hotbar.6 (快捷栏7)",
            "slot.hotbar.7 (快捷栏8)",
            "slot.hotbar.8 (快捷栏9)",
            "slot.inventory.0 (背包1)",
            "slot.armor.head (头盔)",
            "slot.armor.chest (胸甲)",
            "slot.armor.legs (护腿)",
            "slot.armor.feet (靴子)",
            "slot.weapon.mainhand (主手)",
            "slot.weapon.offhand (副手)"
        ]
        
        card.params['slot'] = card.add_param("物品栏位置:", QComboBox(), 1)
        slot_combo = card.params['slot']
        slot_combo.addItems(slots)
        
        card.params['item'] = card.add_param("物品ID:", QLineEdit("minecraft:diamond"), 2)
        card.params['count'] = card.add_param("数量:", QSpinBox(), 3)
        count_spin = card.params['count']
        count_spin.setRange(1, 64)
        count_spin.setValue(1)
        
        def update():
            target = card.params['target'].text()
            slot_text = slot_combo.currentText()
            slot = slot_text.split()[0]
            item = card.params['item'].text()
            count = card.params['count'].value()
            card.preview_label.setText(f"/replaceitem entity {target} {slot} {item} {count}")
        
        card.update_preview = update
        card.params['target'].textChanged.connect(update)
        slot_combo.currentIndexChanged.connect(update)
        card.params['item'].textChanged.connect(update)
        card.params['count'].valueChanged.connect(update)
        update()
    
    def build_summon(self, card):
        """召唤生物指令"""
        entities = [
            "creeper (苦力怕)",
            "zombie (僵尸)",
            "skeleton (骷髅)",
            "spider (蜘蛛)",
            "enderman (末影人)",
            "witch (女巫)",
            "villager (村民)",
            "sheep (羊)",
            "cow (牛)",
            "pig (猪)",
            "chicken (鸡)",
            "horse (马)",
            "wolf (狼)",
            "cat (猫)",
            "iron_golem (铁傀儡)",
            "ender_dragon (末影龙)",
            "wither (凋灵)"
        ]
        
        card.params['entity'] = card.add_param("实体类型:", QComboBox(), 0)
        entity_combo = card.params['entity']
        entity_combo.addItems(entities)
        
        card.params['x'] = card.add_param("X坐标(可选):", QLineEdit("~"), 1, 0)
        card.params['y'] = card.add_param("Y坐标(可选):", QLineEdit("~"), 1, 1)
        card.params['z'] = card.add_param("Z坐标(可选):", QLineEdit("~"), 1, 2)
        
        def update():
            entity_text = entity_combo.currentText()
            entity = entity_text.split()[0]
            x = card.params['x'].text()
            y = card.params['y'].text()
            z = card.params['z'].text()
            # 如果坐标都是"~"，可以省略坐标
            if x == "~" and y == "~" and z == "~":
                card.preview_label.setText(f"/summon {entity}")
            else:
                card.preview_label.setText(f"/summon {entity} {x} {y} {z}")
        
        card.update_preview = update
        entity_combo.currentIndexChanged.connect(update)
        for w in [card.params['x'], card.params['y'], card.params['z']]:
            w.textChanged.connect(update)
        update()
    
    def build_effect(self, card):
        """状态效果指令"""
        card.params['operation'] = card.add_param("操作:", QComboBox(), 0)
        op_combo = card.params['operation']
        op_combo.addItems(["give (添加效果)", "clear (移除效果)"])
        
        effects = [
            "speed (速度)",
            "slowness (缓慢)",
            "haste (急迫)",
            "mining_fatigue (挖掘疲劳)",
            "strength (力量)",
            "instant_health (瞬间治疗)",
            "instant_damage (瞬间伤害)",
            "jump_boost (跳跃提升)",
            "nausea (反胃)",
            "regeneration (生命恢复)",
            "resistance (抗性提升)",
            "fire_resistance (抗火)",
            "water_breathing (水下呼吸)",
            "invisibility (隐身)",
            "blindness (失明)",
            "night_vision (夜视)",
            "hunger (饥饿)",
            "weakness (虚弱)",
            "poison (中毒)",
            "wither (凋零)",
            "health_boost (生命提升)",
            "absorption (伤害吸收)",
            "saturation (饱和)",
            "glowing (发光)",
            "levitation (飘浮)",
            "luck (幸运)",
            "unluck (霉运)"
        ]
        
        card.params['effect'] = card.add_param("效果类型:", QComboBox(), 1)
        effect_combo = card.params['effect']
        effect_combo.addItems(effects)
        
        card.params['target'] = card.add_param("目标玩家:", QLineEdit("@p"), 2)
        card.params['duration'] = card.add_param("持续时间(秒):", QSpinBox(), 3)
        duration_spin = card.params['duration']
        duration_spin.setRange(1, 1000000)
        duration_spin.setValue(60)
        
        card.params['amplifier'] = card.add_param("倍率(0-255):", QSpinBox(), 4)
        amp_spin = card.params['amplifier']
        amp_spin.setRange(0, 255)
        amp_spin.setValue(1)
        
        card.params['hide'] = card.add_param("隐藏粒子:", QCheckBox(), 5)
        
        def update():
            op = op_combo.currentText()
            target = card.params['target'].text()
            
            if "clear" in op:
                effect_text = effect_combo.currentText()
                effect = effect_text.split()[0]
                card.preview_label.setText(f"/effect clear {target} {effect}")
            else:
                effect_text = effect_combo.currentText()
                effect = effect_text.split()[0]
                duration = card.params['duration'].value()
                amp = card.params['amplifier'].value()
                hide = card.params['hide'].isChecked()
                hide_str = "true" if hide else "false"
                card.preview_label.setText(f"/effect give {target} {effect} {duration} {amp} {hide_str}")
        
        card.update_preview = update
        op_combo.currentIndexChanged.connect(update)
        effect_combo.currentIndexChanged.connect(update)
        card.params['target'].textChanged.connect(update)
        card.params['duration'].valueChanged.connect(update)
        card.params['amplifier'].valueChanged.connect(update)
        card.params['hide'].stateChanged.connect(update)
        update()
    
    def build_op(self, card):
        """给予OP指令"""
        card.params['target'] = card.add_param("玩家名:", QLineEdit("Steve"), 0)
        
        def update():
            target = card.params['target'].text()
            card.preview_label.setText(f"/op {target}")
        
        card.update_preview = update
        card.params['target'].textChanged.connect(update)
        update()
    
    def build_kick(self, card):
        """踢出玩家"""
        card.params['target'] = card.add_param("玩家名:", QLineEdit("Steve"), 0)
        card.params['reason'] = card.add_param("原因(可选):", QLineEdit(), 1)
        
        def update():
            target = card.params['target'].text()
            reason = card.params['reason'].text().strip()
            if reason:
                card.preview_label.setText(f"/kick {target} {reason}")
            else:
                card.preview_label.setText(f"/kick {target}")
        
        card.update_preview = update
        card.params['target'].textChanged.connect(update)
        card.params['reason'].textChanged.connect(update)
        update()
    
    def build_ban(self, card):
        """封禁玩家"""
        card.params['target'] = card.add_param("玩家名:", QLineEdit("Steve"), 0)
        card.params['reason'] = card.add_param("原因(可选):", QLineEdit(), 1)
        
        def update():
            target = card.params['target'].text()
            reason = card.params['reason'].text().strip()
            if reason:
                card.preview_label.setText(f"/ban {target} {reason}")
            else:
                card.preview_label.setText(f"/ban {target}")
        
        card.update_preview = update
        card.params['target'].textChanged.connect(update)
        card.params['reason'].textChanged.connect(update)
        update()
    
    def build_whitelist(self, card):
        """白名单管理"""
        ops = [
            "on (开启)",
            "off (关闭)",
            "list (列表)",
            "add (添加)",
            "remove (移除)",
            "reload (重载)"
        ]
        
        card.params['operation'] = card.add_param("操作:", QComboBox(), 0)
        op_combo = card.params['operation']
        op_combo.addItems(ops)
        
        card.params['target'] = card.add_param("玩家名(添加/移除时):", QLineEdit(), 1)
        
        def update():
            op_text = op_combo.currentText()
            op = op_text.split()[0]
            target = card.params['target'].text().strip()
            
            if op in ["add", "remove"] and target:
                card.preview_label.setText(f"/whitelist {op} {target}")
            else:
                card.preview_label.setText(f"/whitelist {op}")
        
        card.update_preview = update
        op_combo.currentIndexChanged.connect(update)
        card.params['target'].textChanged.connect(update)
        update()
    
    def build_saveall(self, card):
        """保存世界"""
        def update():
            card.preview_label.setText("/save-all")
        card.update_preview = update
        update()
    
    def build_stop(self, card):
        """停止服务器"""
        def update():
            card.preview_label.setText("/stop")
        card.update_preview = update
        update()
    
    def build_fill(self, card):
        """填充方块"""
        card.params['from_x'] = card.add_param("起点 X:", QLineEdit("~"), 0, 0)
        card.params['from_y'] = card.add_param("起点 Y:", QLineEdit("~"), 0, 1)
        card.params['from_z'] = card.add_param("起点 Z:", QLineEdit("~"), 0, 2)
        
        card.params['to_x'] = card.add_param("终点 X:", QLineEdit("~10"), 1, 0)
        card.params['to_y'] = card.add_param("终点 Y:", QLineEdit("~10"), 1, 1)
        card.params['to_z'] = card.add_param("终点 Z:", QLineEdit("~10"), 1, 2)
        
        card.params['block'] = card.add_param("方块ID:", QLineEdit("minecraft:stone"), 2)
        
        modes = ["replace (替换)", "destroy (破坏)", "hollow (空心)", "outline (轮廓)", "keep (保留)"]
        card.params['mode'] = card.add_param("模式:", QComboBox(), 3)
        mode_combo = card.params['mode']
        mode_combo.addItems(modes)
        
        def update():
            from_x = card.params['from_x'].text()
            from_y = card.params['from_y'].text()
            from_z = card.params['from_z'].text()
            to_x = card.params['to_x'].text()
            to_y = card.params['to_y'].text()
            to_z = card.params['to_z'].text()
            block = card.params['block'].text()
            mode_text = mode_combo.currentText()
            mode = mode_text.split()[0]
            
            card.preview_label.setText(f"/fill {from_x} {from_y} {from_z} {to_x} {to_y} {to_z} {block} 0 {mode}")
        
        card.update_preview = update
        for w in [card.params['from_x'], card.params['from_y'], card.params['from_z'],
                  card.params['to_x'], card.params['to_y'], card.params['to_z'],
                  card.params['block']]:
            w.textChanged.connect(update)
        mode_combo.currentIndexChanged.connect(update)
        update()
    
    def build_clone(self, card):
        """克隆区域"""
        card.params['from_x1'] = card.add_param("源起点 X1:", QLineEdit("100"), 0, 0)
        card.params['from_y1'] = card.add_param("起点 Y1:", QLineEdit("64"), 0, 1)
        card.params['from_z1'] = card.add_param("起点 Z1:", QLineEdit("100"), 0, 2)
        
        card.params['from_x2'] = card.add_param("源终点 X2:", QLineEdit("110"), 1, 0)
        card.params['from_y2'] = card.add_param("终点 Y2:", QLineEdit("74"), 1, 1)
        card.params['from_z2'] = card.add_param("终点 Z2:", QLineEdit("110"), 1, 2)
        
        card.params['to_x'] = card.add_param("目标 X:", QLineEdit("200"), 2, 0)
        card.params['to_y'] = card.add_param("目标 Y:", QLineEdit("64"), 2, 1)
        card.params['to_z'] = card.add_param("目标 Z:", QLineEdit("200"), 2, 2)
        
        def update():
            x1 = card.params['from_x1'].text()
            y1 = card.params['from_y1'].text()
            z1 = card.params['from_z1'].text()
            x2 = card.params['from_x2'].text()
            y2 = card.params['from_y2'].text()
            z2 = card.params['from_z2'].text()
            tx = card.params['to_x'].text()
            ty = card.params['to_y'].text()
            tz = card.params['to_z'].text()
            
            card.preview_label.setText(f"/clone {x1} {y1} {z1} {x2} {y2} {z2} {tx} {ty} {tz}")
        
        card.update_preview = update
        for w in [card.params['from_x1'], card.params['from_y1'], card.params['from_z1'],
                  card.params['from_x2'], card.params['from_y2'], card.params['from_z2'],
                  card.params['to_x'], card.params['to_y'], card.params['to_z']]:
            w.textChanged.connect(update)
        update()
    
    def build_setblock(self, card):
        """设置单个方块"""
        card.params['x'] = card.add_param("X坐标:", QLineEdit("~"), 0, 0)
        card.params['y'] = card.add_param("Y坐标:", QLineEdit("~1"), 0, 1)
        card.params['z'] = card.add_param("Z坐标:", QLineEdit("~"), 0, 2)
        
        card.params['block'] = card.add_param("方块ID:", QLineEdit("minecraft:diamond_block"), 1)
        
        modes = ["replace (替换)", "keep (仅替换空气)", "destroy (破坏并掉落)"]
        card.params['mode'] = card.add_param("模式:", QComboBox(), 2)
        mode_combo = card.params['mode']
        mode_combo.addItems(modes)
        
        def update():
            x = card.params['x'].text()
            y = card.params['y'].text()
            z = card.params['z'].text()
            block = card.params['block'].text()
            mode_text = mode_combo.currentText()
            mode = mode_text.split()[0]
            
            card.preview_label.setText(f"/setblock {x} {y} {z} {block} 0 {mode}")
        
        card.update_preview = update
        for w in [card.params['x'], card.params['y'], card.params['z'], card.params['block']]:
            w.textChanged.connect(update)
        mode_combo.currentIndexChanged.connect(update)
        update()
    
    def build_execute(self, card):
        """执行指令"""
        exec_types = [
            "as (作为实体)",
            "at (在实体的位置)",
            "as at (作为实体并在其位置)",
            "positioned (在指定坐标)",
            "if (条件执行)"
        ]
        
        card.params['type'] = card.add_param("执行类型:", QComboBox(), 0)
        type_combo = card.params['type']
        type_combo.addItems(exec_types)
        
        card.params['entity'] = card.add_param("目标实体:", QLineEdit("@p"), 1)
        card.params['x'] = card.add_param("X坐标(可选):", QLineEdit("~"), 2, 0)
        card.params['y'] = card.add_param("Y坐标(可选):", QLineEdit("~"), 2, 1)
        card.params['z'] = card.add_param("Z坐标(可选):", QLineEdit("~"), 2, 2)
        
        card.params['command'] = card.add_param("要执行的指令:", QLineEdit("say Hello"), 3)
        
        def update():
            type_idx = type_combo.currentIndex()
            entity = card.params['entity'].text()
            x = card.params['x'].text()
            y = card.params['y'].text()
            z = card.params['z'].text()
            cmd = card.params['command'].text()
            
            if type_idx == 0:  # as
                card.preview_label.setText(f"/execute as {entity} run {cmd}")
            elif type_idx == 1:  # at
                card.preview_label.setText(f"/execute at {entity} run {cmd}")
            elif type_idx == 2:  # as at
                card.preview_label.setText(f"/execute as {entity} at {entity} run {cmd}")
            elif type_idx == 3:  # positioned
                card.preview_label.setText(f"/execute positioned {x} {y} {z} run {cmd}")
            else:  # if
                card.preview_label.setText(f"/execute if entity {entity} run {cmd}")
        
        card.update_preview = update
        type_combo.currentIndexChanged.connect(update)
        for w in [card.params['entity'], card.params['x'], card.params['y'], card.params['z'], card.params['command']]:
            w.textChanged.connect(update)
        update()
    
    def build_title(self, card):
        """标题显示指令"""
        title_types = [
            "title (主标题)",
            "subtitle (副标题)",
            "actionbar (物品栏上方)"
        ]
        
        card.params['type'] = card.add_param("标题类型:", QComboBox(), 0)
        type_combo = card.params['type']
        type_combo.addItems(title_types)
        
        card.params['target'] = card.add_param("目标玩家:", QLineEdit("@p"), 1)
        card.params['text'] = card.add_param("标题文字:", QLineEdit("Hello World"), 2)
        
        def update():
            type_idx = type_combo.currentIndex()
            title_map = {0: "title", 1: "subtitle", 2: "actionbar"}
            title_type = title_map[type_idx]
            target = card.params['target'].text()
            text = card.params['text'].text()
            card.preview_label.setText(f"/title {target} {title_type} {text}")
        
        card.update_preview = update
        type_combo.currentIndexChanged.connect(update)
        card.params['target'].textChanged.connect(update)
        card.params['text'].textChanged.connect(update)
        update()
    
    def build_particle(self, card):
        """粒子效果指令"""
        particles = [
            "heart (爱心)",
            "note (音符)",
            "portal (传送门)",
            "flame (火焰)",
            "lava (熔岩)",
            "water (水)",
            "splash (水花)",
            "crit (暴击)",
            "magic_crit (魔法暴击)",
            "smoke (烟雾)",
            "large_smoke (浓烟)",
            "redstone (红石)",
            "drip_water (水滴)",
            "drip_lava (岩浆滴)",
            "enchant (附魔)",
            "angry_villager (愤怒村民)",
            "happy_villager (开心村民)",
            "end_rod (末地烛)",
            "dragon_breath (龙息)"
        ]
        
        card.params['particle'] = card.add_param("粒子类型:", QComboBox(), 0)
        particle_combo = card.params['particle']
        particle_combo.addItems(particles)
        
        card.params['x'] = card.add_param("X坐标:", QLineEdit("~"), 1, 0)
        card.params['y'] = card.add_param("Y坐标:", QLineEdit("~2"), 1, 1)
        card.params['z'] = card.add_param("Z坐标:", QLineEdit("~"), 1, 2)
        
        card.params['dx'] = card.add_param("扩散范围 X:", QLineEdit("0.5"), 2, 0)
        card.params['dy'] = card.add_param("扩散范围 Y:", QLineEdit("0.5"), 2, 1)
        card.params['dz'] = card.add_param("扩散范围 Z:", QLineEdit("0.5"), 2, 2)
        
        card.params['speed'] = card.add_param("速度:", QDoubleSpinBox(), 3)
        speed_spin = card.params['speed']
        speed_spin.setRange(0, 10)
        speed_spin.setSingleStep(0.1)
        speed_spin.setValue(0.1)
        
        card.params['count'] = card.add_param("数量:", QSpinBox(), 4)
        count_spin = card.params['count']
        count_spin.setRange(1, 1000)
        count_spin.setValue(50)
        
        def update():
            particle_text = particle_combo.currentText()
            particle = particle_text.split()[0]
            x = card.params['x'].text()
            y = card.params['y'].text()
            z = card.params['z'].text()
            dx = card.params['dx'].text()
            dy = card.params['dy'].text()
            dz = card.params['dz'].text()
            speed = card.params['speed'].value()
            count = card.params['count'].value()
            
            card.preview_label.setText(f"/particle {particle} {x} {y} {z} {dx} {dy} {dz} {speed} {count}")
        
        card.update_preview = update
        particle_combo.currentIndexChanged.connect(update)
        for w in [card.params['x'], card.params['y'], card.params['z'],
                  card.params['dx'], card.params['dy'], card.params['dz']]:
            w.textChanged.connect(update)
        speed_spin.valueChanged.connect(update)
        count_spin.valueChanged.connect(update)
        update()
    
    def build_playsound(self, card):
        """播放音效指令"""
        sounds = [
            "entity.player.levelup (升级)",
            "entity.experience_orb.pickup (捡经验)",
            "entity.arrow.shoot (射箭)",
            "entity.creeper.primed (苦力怕点燃)",
            "entity.ender_dragon.death (末影龙死亡)",
            "entity.lightning_bolt.thunder (打雷)",
            "entity.wither.spawn (凋灵生成)",
            "block.note_block.pling (音符盒)",
            "block.anvil.place (放置铁砧)",
            "block.chest.open (打开箱子)",
            "block.portal.travel (传送门)",
            "item.trident.riptide (三叉戟激流)",
            "music_disc.13 (唱片13)",
            "music_disc.cat (唱片cat)"
        ]
        
        card.params['sound'] = card.add_param("音效:", QComboBox(), 0)
        sound_combo = card.params['sound']
        sound_combo.setEditable(True)
        sound_combo.addItems(sounds)
        
        card.params['source'] = card.add_param("来源:", QComboBox(), 1)
        source_combo = card.params['source']
        source_combo.addItems(["master (主音量)", "music (音乐)", "record (唱片)", "weather (天气)", "block (方块)", "hostile (敌对)", "neutral (中立)", "player (玩家)", "ambient (环境)", "voice (语音)"])
        
        card.params['target'] = card.add_param("目标玩家:", QLineEdit("@p"), 2)
        card.params['x'] = card.add_param("X坐标(可选):", QLineEdit("~"), 3, 0)
        card.params['y'] = card.add_param("Y坐标(可选):", QLineEdit("~"), 3, 1)
        card.params['z'] = card.add_param("Z坐标(可选):", QLineEdit("~"), 3, 2)
        
        card.params['volume'] = card.add_param("音量(0-1):", QDoubleSpinBox(), 4)
        volume_spin = card.params['volume']
        volume_spin.setRange(0, 1)
        volume_spin.setSingleStep(0.1)
        volume_spin.setValue(1.0)
        
        card.params['pitch'] = card.add_param("音调(0-2):", QDoubleSpinBox(), 5)
        pitch_spin = card.params['pitch']
        pitch_spin.setRange(0, 2)
        pitch_spin.setSingleStep(0.1)
        pitch_spin.setValue(1.0)
        
        def update():
            sound_text = sound_combo.currentText()
            sound = sound_text.split()[0] if " " in sound_text else sound_text
            source_text = source_combo.currentText()
            source = source_text.split()[0]
            target = card.params['target'].text()
            x = card.params['x'].text()
            y = card.params['y'].text()
            z = card.params['z'].text()
            volume = card.params['volume'].value()
            pitch = card.params['pitch'].value()
            
            # 如果坐标都是"~"，可以省略坐标
            if x == "~" and y == "~" and z == "~":
                card.preview_label.setText(f"/playsound {sound} {source} {target} {volume} {pitch}")
            else:
                card.preview_label.setText(f"/playsound {sound} {source} {target} {x} {y} {z} {volume} {pitch}")
        
        card.update_preview = update
        sound_combo.currentIndexChanged.connect(update)
        sound_combo.lineEdit().textChanged.connect(update)
        source_combo.currentIndexChanged.connect(update)
        card.params['target'].textChanged.connect(update)
        for w in [card.params['x'], card.params['y'], card.params['z']]:
            w.textChanged.connect(update)
        volume_spin.valueChanged.connect(update)
        pitch_spin.valueChanged.connect(update)
        update()


def main():
    app = QApplication(sys.argv)
    
    # 设置图标
    icon_path = os.path.join(os.path.dirname(__file__), "data", "res", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    app.setFont(QFont("Microsoft YaHei", 9))
    window = CommandHelper()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()