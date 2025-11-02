import sqlite3
import hashlib
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)# 第一次调用时创建实例
        return cls._instance# 后续调用都返回同一个实例
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.db_path = "finance_manager.db"
            self.initialized = True
            self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()#创建游标对象；游标用于执行SQL语句和获取结果
        
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 交易表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                from_user VARCHAR(100) NOT NULL,
                to_user VARCHAR(100) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                transaction_type VARCHAR(20) NOT NULL,
                category VARCHAR(50) NOT NULL,
                description TEXT,
                transaction_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_time ON transactions(transaction_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type)')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()