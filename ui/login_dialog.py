from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class LoginDialog(QDialog):
    login_success = pyqtSignal(object)  # 发射User对象
    
    def __init__(self, user_service, parent=None):
        super().__init__(parent)
        self.user_service = user_service
        self.is_register_mode = False
        self.user = None # 存储登录成功的用户
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("记账本系统 - 登录")
        self.setFixedSize(450, 600)  # 调整尺寸
        """
        对话框的背景为渐变颜色
        统一所有标签的样式
        美化输入框
        输入框获得焦点时改变边框颜色
        基础按钮样式
        提供按钮交互反馈（不透明度）
        美化框架容器
        """
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #667eea, stop: 1 #764ba2);
            }
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                background: white;
                min-height: 25px;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
            QPushButton {
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                color: white;
                min-width: 100px;
                min-height: 40px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:pressed {
                opacity: 0.8;
            }
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 顶部标题区域
        header_frame = QFrame()
        header_frame.setFixedHeight(120)
        header_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-bottom: 1px solid rgba(255,255,255,0.2);
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel("记账本系统")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        
        subtitle_label = QLabel("个人财务管理")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont("Microsoft YaHei", 12))
        subtitle_label.setStyleSheet("color: rgba(255,255,255,0.8); margin-top: 5px;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        # 表单区域
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(40, 40, 40, 40)
        
        # 模式标题
        self.mode_title = QLabel("用户登录")
        self.mode_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mode_title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        self.mode_title.setStyleSheet("color: white; margin-bottom: 10px;")
        form_layout.addWidget(self.mode_title)
        
        # 用户名输入
        username_layout = QVBoxLayout()
        username_layout.setSpacing(8)
        
        username_label = QLabel("用户名")
        username_label.setStyleSheet("color: white;")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        self.username_edit.setMinimumHeight(45)
        
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        form_layout.addLayout(username_layout)
        
        # 密码输入
        password_layout = QVBoxLayout()
        password_layout.setSpacing(8)
        
        password_label = QLabel("密码")
        password_label.setStyleSheet("color: white;")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setMinimumHeight(45)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        form_layout.addLayout(password_layout)
        
        # 邮箱输入（注册时显示）
        self.email_layout = QVBoxLayout()
        self.email_layout.setSpacing(8)
        
        self.email_label = QLabel("邮箱（可选）")
        self.email_label.setStyleSheet("color: white;")
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("请输入邮箱地址")
        self.email_edit.setMinimumHeight(45)
        
        self.email_layout.addWidget(self.email_label)
        self.email_layout.addWidget(self.email_edit)
        form_layout.addLayout(self.email_layout)
        
        # 操作按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.login_btn = QPushButton("登录")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        
        self.register_btn = QPushButton("注册")
        self.register_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)
        self.register_btn.clicked.connect(self.handle_register)
        
        buttons_layout.addWidget(self.login_btn)
        buttons_layout.addWidget(self.register_btn)
        form_layout.addLayout(buttons_layout)
        
        # 切换模式按钮
        self.toggle_btn = QPushButton("切换到注册模式")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                text-decoration: underline;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_mode)
        form_layout.addWidget(self.toggle_btn)
        
        # 组装主布局
        main_layout.addWidget(header_frame)
        main_layout.addWidget(form_frame)
        
        # 初始隐藏邮箱字段
        self.hide_email_fields()
    
    def hide_email_fields(self):
        """隐藏邮箱字段"""
        self.email_label.hide()
        self.email_edit.hide()
    
    def show_email_fields(self):
        """显示邮箱字段"""
        self.email_label.show()
        self.email_edit.show()
    
    def toggle_mode(self):
        """切换登录/注册模式"""
        self.is_register_mode = not self.is_register_mode
        
        if self.is_register_mode:
            self.mode_title.setText("用户注册")
            self.toggle_btn.setText("切换到登录模式")
            self.login_btn.setText("注册并登录")
            self.show_email_fields()
            self.setFixedSize(450, 660)  # 调整高度以适应邮箱字段
        else:
            self.mode_title.setText("用户登录")
            self.toggle_btn.setText("切换到注册模式")
            self.login_btn.setText("登录")
            self.hide_email_fields()
            self.setFixedSize(450, 600)
    
    def handle_login(self):
        """处理登录"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        if not username:
            QMessageBox.warning(self, "输入错误", "请输入用户名")
            self.username_edit.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "输入错误", "请输入密码")
            self.password_edit.setFocus()
            return
        
        user = self.user_service.login_user(username, password)
        if user:
            self.user = user
            self.login_success.emit(user)
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误")
            self.password_edit.clear()
            self.password_edit.setFocus()
    
    def handle_register(self):
        """处理注册"""
        if not self.is_register_mode:
            self.toggle_mode()
            return
        
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        email = self.email_edit.text().strip()
        
        if not username:
            QMessageBox.warning(self, "输入错误", "请输入用户名")
            self.username_edit.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "输入错误", "请输入密码")
            self.password_edit.setFocus()
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "输入错误", "密码长度至少6位")
            self.password_edit.setFocus()
            return
        
        if self.user_service.user_exists(username):
            QMessageBox.warning(self, "注册失败", "用户名已存在")
            self.username_edit.clear()
            self.username_edit.setFocus()
            return
        
        user = self.user_service.register_user(username, password, email)
        if user:
            QMessageBox.information(self, "注册成功", "用户注册成功！")
            # 自动切换到登录模式
            self.toggle_mode()
            # 清空密码字段
            self.password_edit.clear()
            self.email_edit.clear()
        else:
            QMessageBox.warning(self, "注册失败", "注册失败，请重试")