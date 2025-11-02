import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QLineEdit, QComboBox, QDateEdit, 
    QMessageBox, QHeaderView, QFrame, QGroupBox,
    QFormLayout, QDoubleSpinBox, QTextEdit, QDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

from models import User, Transaction, TransactionType, Category
from services import TransactionService, QueryService, StatisticsService

class MainWindow(QMainWindow):
    def __init__(self, user: User):
        super().__init__()
        self.user = user # 当前登录用户
        self.transaction_service = TransactionService()
        self.query_service = QueryService()
        self.stats_service = StatisticsService()
        
        self.setup_ui()
        self.load_transactions()
        self.update_stats()
        
    def setup_ui(self):
        self.setWindowTitle(f"记账本系统 - {self.user.username}")
        self.setGeometry(200, 100, 1400, 1000)# 窗口左上角距离屏幕左边的像素数，上，窗口宽度，高度
        self.setMinimumSize(1200, 800) # 设置窗口的最小尺寸限制
        self.setStyleSheet(self.get_stylesheet())# 调用 get_stylesheet() 方法获取样式字符串，将样式应用到当前窗口及其子部件
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题栏
        title_layout = QHBoxLayout()
        title_label = QLabel(f"欢迎，{self.user.username}！")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 快速操作按钮
        quick_btn_layout = QHBoxLayout()
        quick_btn_layout.setSpacing(10)
        
        self.add_income_btn = QPushButton("+ 添加收入")
        self.add_expense_btn = QPushButton("- 添加支出")
        self.refresh_btn = QPushButton("🔄 刷新")

        # 基础样式模板
        button_style_template = """
            QPushButton {{
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
            min-height: 35px;
            min-width: 100px;
            background: {bg_color};
            color: white;
        }}
        QPushButton:hover {{
            opacity: 0.9;
            background: {hover_color};
        }}
        QPushButton:pressed {{
            background: {pressed_color};
        }}
    """

        # 应用样式
        self.add_income_btn.setStyleSheet(button_style_template.format(
            bg_color="#27ae60", hover_color="#219652", pressed_color="#1e8449"
        ))

        self.add_expense_btn.setStyleSheet(button_style_template.format(
            bg_color="#e74c3c", hover_color="#d34536", pressed_color="#ba3f31"
        ))

        self.refresh_btn.setStyleSheet(button_style_template.format(
            bg_color="#3498db", hover_color="#2980b9", pressed_color="#2472a4"
        ))
        
        self.add_income_btn.clicked.connect(lambda: self.show_add_transaction_dialog(TransactionType.INCOME))
        self.add_expense_btn.clicked.connect(lambda: self.show_add_transaction_dialog(TransactionType.EXPENSE))
        self.refresh_btn.clicked.connect(self.refresh_data)
        
        quick_btn_layout.addWidget(self.add_income_btn)
        quick_btn_layout.addWidget(self.add_expense_btn)
        quick_btn_layout.addWidget(self.refresh_btn)
        quick_btn_layout.addStretch()
        
        title_layout.addLayout(quick_btn_layout)
        layout.addLayout(title_layout)
        
        # 统计信息卡片
        self.setup_stats_cards(layout)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                padding: 12px 24px;
                margin-right: 2px;
                border: 1px solid #bdc3c7;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: white;
                border-color: #3498db;
                color: #3498db;
            }
            QTabBar::tab:hover {
                background: #d5dbdb;
            }
        """)
        
        self.setup_transactions_tab()
        self.setup_query_tab()
        self.setup_stats_tab()
        
        layout.addWidget(self.tab_widget)
    
    def setup_stats_cards(self, layout):
        """设置统计信息卡片"""
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        # 总收入卡片
        self.income_card = self.create_stat_card("总收入", "¥0.00", "#27ae60", "💰")
        # 总支出卡片
        self.expense_card = self.create_stat_card("总支出", "¥0.00", "#e74c3c", "💸")
        # 净收入卡片
        self.net_card = self.create_stat_card("净收入", "¥0.00", "#3498db", "📊")
        # 交易笔数卡片
        self.count_card = self.create_stat_card("交易笔数", "0", "#f39c12", "📝")
        
        cards_layout.addWidget(self.income_card)
        cards_layout.addWidget(self.expense_card)
        cards_layout.addWidget(self.net_card)
        cards_layout.addWidget(self.count_card)
        
        layout.addLayout(cards_layout)
    
    def create_stat_card(self, title: str, value: str, color: str, icon: str) -> QFrame:
        """创建统计卡片"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-radius: 10px;
            }}
        """)
        card.setFixedHeight(100)
        card.setFixedWidth(250)  # 设置固定宽度
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题行
        title_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 16))
        icon_label.setStyleSheet("color: white; background: transparent;")
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; background: transparent;")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 数值
        value_label = QLabel(value)
        value_label.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        value_label.setStyleSheet("color: white; background: transparent;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setObjectName("value_label")  # 设置对象名称用于后续更新
        
        card_layout.addLayout(title_layout)
        card_layout.addWidget(value_label)
        
        return card

    def setup_transactions_tab(self):
        """设置交易记录选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 说明标签
        info_label = QLabel("最近交易记录")
        info_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        info_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # 交易表格
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(7)
        self.transaction_table.setHorizontalHeaderLabels([
            "ID", "交易方", "金额", "类型", "分类", "描述", "时间"
        ])
        
        # 设置表格属性
        self.transaction_table.setAlternatingRowColors(True)

        # 设置行高 - 解决行间距问题
        self.transaction_table.verticalHeader().setDefaultSectionSize(40)  # 设置默认行高
        self.transaction_table.verticalHeader().setMinimumSectionSize(35)  # 最小行高

        header = self.transaction_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID列
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 交易方列自适应
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # 金额列
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # 类型列
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # 分类列
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # 描述列自适应
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # 时间列
        
        self.transaction_table.setSortingEnabled(True)
        self.transaction_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.transaction_table)
        
        self.tab_widget.addTab(tab, "📋 交易记录")

    def setup_query_tab(self):
        """设置查询选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 查询条件组
        query_group = QGroupBox("查询条件")
        query_layout = QFormLayout(query_group)
        query_layout.setSpacing(12)
        
        self.query_target_edit = QLineEdit()
        self.query_target_edit.setPlaceholderText("输入交易方名称")
        self.query_target_edit.setMinimumHeight(35)
        
        self.query_type_combo = QComboBox()
        self.query_type_combo.addItem("所有类型", None)
        self.query_type_combo.addItem("收入", TransactionType.INCOME)
        self.query_type_combo.addItem("支出", TransactionType.EXPENSE)
        self.query_type_combo.setMinimumHeight(35)
        
        self.query_category_combo = QComboBox()
        self.query_category_combo.addItem("所有分类", None)
        for category in Category:
            self.query_category_combo.addItem(category.value, category)
        self.query_category_combo.setMinimumHeight(35)
        
        self.query_start_date = QDateEdit()
        self.query_start_date.setDate(QDate.currentDate().addMonths(-1))
        self.query_start_date.setCalendarPopup(True)
        self.query_start_date.setMinimumHeight(35)
        
        self.query_end_date = QDateEdit()
        self.query_end_date.setDate(QDate.currentDate())
        self.query_end_date.setCalendarPopup(True)
        self.query_end_date.setMinimumHeight(35)
        
        query_layout.addRow("交易方:", self.query_target_edit)
        query_layout.addRow("类型:", self.query_type_combo)
        query_layout.addRow("分类:", self.query_category_combo)
        query_layout.addRow("开始时间:", self.query_start_date)
        query_layout.addRow("结束时间:", self.query_end_date)
        
        # 查询按钮
        query_btn_layout = QHBoxLayout()
        self.search_btn = QPushButton("🔍 搜索")
        self.reset_btn = QPushButton("🔄 重置")
        
        self.search_btn.setStyleSheet("background: #3498db; color: white; padding: 10px 20px;")
        self.reset_btn.setStyleSheet("background: #95a5a6; color: white; padding: 10px 20px;")
        
        self.search_btn.clicked.connect(self.perform_search)
        self.reset_btn.clicked.connect(self.reset_search)
        
        query_btn_layout.addWidget(self.search_btn)
        query_btn_layout.addWidget(self.reset_btn)
        query_btn_layout.addStretch()
        
        query_layout.addRow(query_btn_layout)
        
        layout.addWidget(query_group)
        
        # 查询结果表格
        self.query_table = QTableWidget()
        self.query_table.setColumnCount(7)
        self.query_table.setHorizontalHeaderLabels([
            "ID", "交易方", "金额", "类型", "分类", "描述", "时间"
        ])

        # 设置行高 - 解决行间距问题
        self.query_table.verticalHeader().setDefaultSectionSize(40)  # 设置默认行高
        self.query_table.verticalHeader().setMinimumSectionSize(35)  # 最小行高
        
        header = self.query_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.query_table)
        
        self.tab_widget.addTab(tab, "🔍 交易查询")

    def setup_stats_tab(self):
        """设置统计选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 统计控制
        stats_control_layout = QHBoxLayout()
        stats_control_layout.addWidget(QLabel("统计时间段:"))
        
        self.stats_start_date = QDateEdit()
        self.stats_start_date.setDate(QDate.currentDate().addMonths(-1))
        self.stats_start_date.setCalendarPopup(True)
        self.stats_start_date.setMinimumHeight(35)
        
        self.stats_end_date = QDateEdit()
        self.stats_end_date.setDate(QDate.currentDate())
        self.stats_end_date.setCalendarPopup(True)
        self.stats_end_date.setMinimumHeight(35)
        
        self.stats_btn = QPushButton("📊 生成统计")
        self.stats_btn.setStyleSheet("background: #9b59b6; color: white; padding: 10px 20px;")
        self.stats_btn.clicked.connect(self.generate_stats)
        
        stats_control_layout.addWidget(self.stats_start_date)
        stats_control_layout.addWidget(QLabel("到"))
        stats_control_layout.addWidget(self.stats_end_date)
        stats_control_layout.addWidget(self.stats_btn)
        stats_control_layout.addStretch()
        
        layout.addLayout(stats_control_layout)
        
        # 统计结果显示区域
        stats_display_layout = QHBoxLayout()
        
        # 左侧：统计数字
        stats_numbers_frame = QFrame()
        stats_numbers_frame.setStyleSheet("background: white; border-radius: 8px; padding: 15px;")
        stats_numbers_layout = QVBoxLayout(stats_numbers_frame)
        
        self.stats_income_label = QLabel("总收入: ¥0.00")
        self.stats_expense_label = QLabel("总支出: ¥0.00")
        self.stats_net_label = QLabel("净收入: ¥0.00")
        self.stats_count_label = QLabel("交易笔数: 0")
        
        for label in [self.stats_income_label, self.stats_expense_label, 
                     self.stats_net_label, self.stats_count_label]:
            label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
            label.setStyleSheet("""
                padding: 15px;
                background: #f8f9fa;
                border-radius: 6px;
                margin: 5px;
                color: #2c3e50;
                border-left: 4px solid #3498db;
            """)
            stats_numbers_layout.addWidget(label)
        
        stats_numbers_layout.addStretch()
        
        # 右侧：图表区域
        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
            }
        """)
        chart_layout = QVBoxLayout(chart_frame)
        
        self.chart_area = QLabel("统计图表区域\n\n点击\"生成统计\"按钮查看数据分析")
        self.chart_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_area.setFont(QFont("Microsoft YaHei", 14))
        self.chart_area.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                padding: 40px;
            }
        """)
        
        chart_layout.addWidget(self.chart_area)
        
        stats_display_layout.addWidget(stats_numbers_frame, 1)
        stats_display_layout.addWidget(chart_frame, 2)
        
        layout.addLayout(stats_display_layout)
        
        self.tab_widget.addTab(tab, "📊 数据统计")

    # ========== 核心功能方法 ==========

    def load_transactions(self):
        """加载交易记录"""
        try:
            transactions = self.transaction_service.get_user_transactions(self.user.id)
            self.populate_table(self.transaction_table, transactions)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载交易记录失败: {str(e)}")

    def populate_table(self, table: QTableWidget, transactions: list):
        """填充表格数据"""
        table.setRowCount(len(transactions))
        
        for row, transaction in enumerate(transactions):
            table.setItem(row, 0, QTableWidgetItem(str(transaction.id)))
            table.setItem(row, 1, QTableWidgetItem(
                f"{transaction.from_user} → {transaction.to_user}"
            ))
            
            amount_item = QTableWidgetItem(f"¥{transaction.amount:.2f}")
            if transaction.transaction_type == TransactionType.INCOME:
                amount_item.setForeground(QColor(39, 174, 96))  # 绿色
            else:
                amount_item.setForeground(QColor(231, 76, 60))  # 红色
            table.setItem(row, 2, amount_item)
            
            type_text = "收入" if transaction.transaction_type == TransactionType.INCOME else "支出"
            table.setItem(row, 3, QTableWidgetItem(type_text))
            table.setItem(row, 4, QTableWidgetItem(transaction.category.value))
            table.setItem(row, 5, QTableWidgetItem(transaction.description))
            table.setItem(row, 6, QTableWidgetItem(
                transaction.transaction_time.strftime("%Y-%m-%d %H:%M:%S")
            ))

    def refresh_data(self):
        """刷新数据"""
        self.load_transactions()
        self.update_stats()
        QMessageBox.information(self, "刷新", "数据已刷新！")

    def update_stats(self):
        """更新统计信息"""
        try:
            # 获取最近30天的统计数据
            end_time = datetime.now()
            start_time = end_time - timedelta(days=30)
            
            stats = self.stats_service.get_time_range_stats(self.user.id, start_time, end_time)
            
            # 更新统计卡片
            self.update_stat_card(self.income_card, f"¥{stats['total_income']:.2f}")
            self.update_stat_card(self.expense_card, f"¥{stats['total_expense']:.2f}")
            self.update_stat_card(self.net_card, f"¥{stats['net_amount']:.2f}")
            self.update_stat_card(self.count_card, str(stats['transaction_count']))
            
            # 更新统计选项卡中的数字
            self.stats_income_label.setText(f"总收入: ¥{stats['total_income']:.2f}")
            self.stats_expense_label.setText(f"总支出: ¥{stats['total_expense']:.2f}")
            self.stats_net_label.setText(f"净收入: ¥{stats['net_amount']:.2f}")
            self.stats_count_label.setText(f"交易笔数: {stats['transaction_count']}")
            
        except Exception as e:
            print(f"更新统计信息失败: {e}")

    def update_stat_card(self, card: QFrame, value: str):
        """更新统计卡片的值"""
        # 查找卡片中的所有QLabel组件
        for widget in card.findChildren(QLabel):
            if widget.objectName() == "value_label":
                widget.setText(value)
                break

    def perform_search(self):
        """执行搜索"""
        try:
            conditions = {}
            
            target_user = self.query_target_edit.text().strip()
            if target_user:
                conditions['target_user'] = target_user
            
            transaction_type = self.query_type_combo.currentData()
            if transaction_type:
                conditions['transaction_type'] = transaction_type
            
            category = self.query_category_combo.currentData()
            if category:
                conditions['category'] = category
            
            start_time = self.query_start_date.date().toPyDate()
            end_time = self.query_end_date.date().toPyDate()
            conditions['start_time'] = datetime.combine(start_time, datetime.min.time())
            conditions['end_time'] = datetime.combine(end_time, datetime.max.time())
            
            transactions = self.query_service.query_transactions(self.user.id, **conditions)
            self.populate_table(self.query_table, transactions)
            
            QMessageBox.information(self, "搜索完成", f"找到 {len(transactions)} 条记录")
            
        except Exception as e:
            QMessageBox.warning(self, "搜索错误", f"搜索失败: {str(e)}")

    def reset_search(self):
        """重置搜索条件"""
        self.query_target_edit.clear()
        self.query_type_combo.setCurrentIndex(0)
        self.query_category_combo.setCurrentIndex(0)
        self.query_start_date.setDate(QDate.currentDate().addMonths(-1))
        self.query_end_date.setDate(QDate.currentDate())
        self.query_table.setRowCount(0)

    def generate_stats(self):
        """生成统计"""
        try:
            start_time = datetime.combine(
                self.stats_start_date.date().toPyDate(), 
                datetime.min.time()
            )
            end_time = datetime.combine(
                self.stats_end_date.date().toPyDate(), 
                datetime.max.time()
            )
            
            stats = self.stats_service.get_time_range_stats(self.user.id, start_time, end_time)
            
            # 更新统计显示
            self.stats_income_label.setText(f"总收入: ¥{stats['total_income']:.2f}")
            self.stats_expense_label.setText(f"总支出: ¥{stats['total_expense']:.2f}")
            self.stats_net_label.setText(f"净收入: ¥{stats['net_amount']:.2f}")
            self.stats_count_label.setText(f"交易笔数: {stats['transaction_count']}")
            
            # 显示分类统计
            category_text = "📊 分类统计\n\n"
            total_amount = stats['total_income'] + stats['total_expense']
            
            for category in stats['category_breakdown']:
                percentage = (category['amount'] / total_amount * 100) if total_amount > 0 else 0
                category_text += f"• {category['category']}: ¥{category['amount']:.2f} ({percentage:.1f}%)\n"
            
            self.chart_area.setText(category_text)
            
            QMessageBox.information(self, "统计完成", "统计数据已生成！")
            
        except Exception as e:
            QMessageBox.warning(self, "统计错误", f"生成统计失败: {str(e)}")

    def show_add_transaction_dialog(self, transaction_type: TransactionType):
        """显示添加交易对话框"""
        dialog = AddTransactionDialog(self.user, transaction_type, self)
        if dialog.exec():
            transaction = dialog.get_transaction()
            if self.transaction_service.add_transaction(transaction):
                QMessageBox.information(self, "成功", "交易添加成功！")
                self.refresh_data()
            else:
                QMessageBox.warning(self, "错误", "交易添加失败！")

    def get_stylesheet(self):
        """获取样式表"""
        return """
            QMainWindow {
                background: #ecf0f1;
                font-family: "Microsoft YaHei";
            }
            QTableWidget {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background: white;
                gridline-color: #ecf0f1;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background: #3498db;
                color: white;
            }
            QHeaderView::section {
                background: #34495e;
                color: white;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
            QGroupBox {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 13px;
                color: #2c3e50;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background: white;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                min-height: 35px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QTextEdit {
                padding: 10px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background: white;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, 
            QDoubleSpinBox:focus, QTextEdit:focus {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #7f8c8d;
                width: 0px;
                height: 0px;
            }
        """

# 添加交易对话框类（保持不变）
class AddTransactionDialog(QDialog):
    def __init__(self, user: User, transaction_type: TransactionType, parent=None):
        super().__init__(parent)
        self.user = user
        self.transaction_type = transaction_type
        self.setup_ui()
    
    def setup_ui(self):
        type_text = "收入" if self.transaction_type == TransactionType.INCOME else "支出"
        self.setWindowTitle(f"添加{type_text}记录")
        self.setFixedSize(500, 600)
        self.setStyleSheet("""
            QDialog {
                background: white;
            }
            QLabel {
                font-weight: bold;
                color: #2c3e50;
                font-size: 13px;
            }
            QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit {
                padding: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 13px;
                min-height: 25px;
            }
            QPushButton {
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                min-height: 40px;
                min-width: 80px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = QLabel(f"添加{type_text}记录")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 表单
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.from_user_edit = QLineEdit()
        self.from_user_edit.setPlaceholderText("输入付款方名称")
        self.from_user_edit.setMinimumHeight(35)
        form_layout.addRow("付款方:", self.from_user_edit)
        
        self.to_user_edit = QLineEdit()
        self.to_user_edit.setPlaceholderText("输入收款方名称")
        self.to_user_edit.setMinimumHeight(35)
        form_layout.addRow("收款方:", self.to_user_edit)
        
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0.01, 1000000.00)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("¥ ")
        self.amount_spin.setMinimumHeight(35)
        form_layout.addRow("金额:", self.amount_spin)
        
        self.category_combo = QComboBox()
        for category in Category:
            self.category_combo.addItem(category.value, category)
        self.category_combo.setMinimumHeight(35)
        form_layout.addRow("分类:", self.category_combo)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(120)
        self.description_edit.setPlaceholderText("输入交易描述（可选）")
        form_layout.addRow("描述:", self.description_edit)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        
        self.ok_btn.setStyleSheet("background: #27ae60; color: white;")
        self.cancel_btn.setStyleSheet("background: #95a5a6; color: white;")
        
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def get_transaction(self) -> Transaction:
        """获取交易对象"""
        return Transaction(
            id=0,
            user_id=self.user.id,
            from_user=self.from_user_edit.text().strip(),
            to_user=self.to_user_edit.text().strip(),
            amount=self.amount_spin.value(),
            transaction_type=self.transaction_type,
            category=self.category_combo.currentData(),
            description=self.description_edit.toPlainText().strip(),
            transaction_time=datetime.now()
        )