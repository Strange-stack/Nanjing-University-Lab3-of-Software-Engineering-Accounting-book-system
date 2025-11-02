import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from database import DatabaseManager
from services import UserService
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow

def main():
    # 初始化数据库
    db_manager = DatabaseManager()
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 高DPI缩放设置（PyQt6中的正确属性名）
    try:
        # 方法1：使用新的属性名
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    except AttributeError:
        try:
            # 方法2：如果上面的属性不存在，尝试旧属性名
            app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        except AttributeError:
            # 方法3：如果都不存在，跳过这个设置
            print("高DPI缩放属性不可用，跳过设置")
    
    try:
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        try:
            app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            print("高DPI图片属性不可用，跳过设置")
    
    # 创建用户服务
    user_service = UserService()
    
    # 显示登录对话框
    login_dialog = LoginDialog(user_service)
    
    if login_dialog.exec():
        user = login_dialog.user
        main_window = MainWindow(user)
        main_window.show()
        
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()