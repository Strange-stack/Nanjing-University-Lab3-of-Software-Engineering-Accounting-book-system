from database import DatabaseManager
from models import User, Transaction, TransactionType, Category
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import sqlite3

class UserService:
    def __init__(self):
        self.db = DatabaseManager()
    
    def register_user(self, username: str, password: str, email: str = "") -> Optional[User]:
        """用户注册"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = self.db.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password_hash, email)
            )
            user_id = cursor.lastrowid#获取刚刚插入记录的自增ID（获取新用户ID）
            conn.commit()
            
            return User(
                id=user_id,
                username=username,
                email=email,
                created_at=datetime.now()
            )#返回User对象
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def login_user(self, username: str, password: str) -> Optional[User]:
        """用户登录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.db.hash_password(password)
        cursor.execute(
            "SELECT id, username, email, created_at FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        
        result = cursor.fetchone()#查询结果处理
        conn.close()
        
        if result:
            return User(
                id=result[0],
                username=result[1],
                email=result[2],
                created_at=datetime.fromisoformat(result[3])
            )
        return None
    
    def user_exists(self, username: str) -> bool:
        """检查用户是否存在"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

class TransactionService:
    def __init__(self):
        self.db = DatabaseManager()
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """添加交易"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO transactions 
                (user_id, from_user, to_user, amount, transaction_type, category, description, transaction_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction.user_id,
                transaction.from_user,
                transaction.to_user,
                transaction.amount,
                transaction.transaction_type.value,
                transaction.category.value,
                transaction.description,
                transaction.transaction_time.isoformat()
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_transactions(self, user_id: int, limit: int = 100) -> List[Transaction]:
        """获取用户交易记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, from_user, to_user, amount, transaction_type, category, description, transaction_time
            FROM transactions 
            WHERE user_id = ? 
            ORDER BY transaction_time DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        transactions = []
        for row in cursor.fetchall():
            transactions.append(Transaction(
                id=row[0],
                user_id=row[1],
                from_user=row[2],
                to_user=row[3],
                amount=row[4],
                transaction_type=TransactionType(row[5]),
                category=Category(row[6]),
                description=row[7],
                transaction_time=datetime.fromisoformat(row[8])
            ))
        
        conn.close()
        return transactions
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """删除交易"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            return False
        finally:
            conn.close()

class QueryService:
    def __init__(self):
        self.db = DatabaseManager()
    
    def query_transactions(self, user_id: int, **conditions) -> List[Transaction]:
        """通用交易查询"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, user_id, from_user, to_user, amount, transaction_type, category, description, transaction_time
            FROM transactions 
            WHERE user_id = ?
        '''
        params = [user_id]
        
        # 构建查询条件
        if 'target_user' in conditions and conditions['target_user']:
            query += " AND (from_user LIKE ? OR to_user LIKE ?)"
            params.extend([f"%{conditions['target_user']}%", f"%{conditions['target_user']}%"])
        
        if 'start_time' in conditions and conditions['start_time']:
            query += " AND transaction_time >= ?"
            params.append(conditions['start_time'].isoformat())
        
        if 'end_time' in conditions and conditions['end_time']:
            query += " AND transaction_time <= ?"
            params.append(conditions['end_time'].isoformat())
        
        if 'transaction_type' in conditions and conditions['transaction_type']:
            query += " AND transaction_type = ?"
            params.append(conditions['transaction_type'].value)
        
        if 'category' in conditions and conditions['category']:
            query += " AND category = ?"
            params.append(conditions['category'].value)
        
        query += " ORDER BY transaction_time DESC"
        
        cursor.execute(query, params)
        
        transactions = []
        for row in cursor.fetchall():
            transactions.append(Transaction(
                id=row[0],
                user_id=row[1],
                from_user=row[2],
                to_user=row[3],
                amount=row[4],
                transaction_type=TransactionType(row[5]),
                category=Category(row[6]),
                description=row[7],
                transaction_time=datetime.fromisoformat(row[8])
            ))
        
        conn.close()
        return transactions

class StatisticsService:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_time_range_stats(self, user_id: int, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """获取时间段统计"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # 总收入、总支出
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END) as total_expense,
                COUNT(*) as transaction_count
            FROM transactions 
            WHERE user_id = ? AND transaction_time BETWEEN ? AND ?
        ''', (user_id, start_time.isoformat(), end_time.isoformat()))
        
        result = cursor.fetchone()
        total_income = result[0] or 0
        total_expense = result[1] or 0
        transaction_count = result[2] or 0
        
        # 分类统计
        cursor.execute('''
            SELECT category, SUM(amount) as category_amount
            FROM transactions 
            WHERE user_id = ? AND transaction_time BETWEEN ? AND ?
            GROUP BY category
            ORDER BY category_amount DESC
        ''', (user_id, start_time.isoformat(), end_time.isoformat()))
        
        category_breakdown = []
        for row in cursor.fetchall():
            category_breakdown.append({
                'category': row[0],
                'amount': row[1]
            })
        
        conn.close()
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'net_amount': total_income - total_expense,
            'transaction_count': transaction_count,
            'category_breakdown': category_breakdown
        }
    
    def get_top_categories(self, user_id: int, limit: int = 10, 
                          start_time: datetime = None, end_time: datetime = None) -> List[Dict[str, Any]]:
        """获取顶级分类"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT category, SUM(amount) as total_amount, COUNT(*) as count
            FROM transactions 
            WHERE user_id = ? AND transaction_type = 'expense'
        '''
        params = [user_id]
        
        if start_time and end_time:
            query += " AND transaction_time BETWEEN ? AND ?"
            params.extend([start_time.isoformat(), end_time.isoformat()])
        
        query += " GROUP BY category ORDER BY total_amount DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        top_categories = []
        for row in cursor.fetchall():
            top_categories.append({
                'category': row[0],
                'amount': row[1],
                'count': row[2]
            })
        
        conn.close()
        return top_categories