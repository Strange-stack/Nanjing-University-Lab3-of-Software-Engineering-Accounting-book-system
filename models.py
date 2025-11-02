from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"

class Category(Enum):
    TRANSFER = "transfer"
    PAYMENT = "payment"
    RED_PACKET = "red_packet"
    SALARY = "salary"
    FOOD = "food"
    TRANSPORT = "transport"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    OTHER = "other"

@dataclass
class User:
    id: int
    username: str
    email: str
    created_at: datetime
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at
        }

@dataclass
class Transaction:
    id: int
    user_id: int
    from_user: str
    to_user: str
    amount: float
    transaction_type: TransactionType
    category: Category
    description: str
    transaction_time: datetime
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'from_user': self.from_user,
            'to_user': self.to_user,
            'amount': self.amount,
            'transaction_type': self.transaction_type.value,
            'category': self.category.value,
            'description': self.description,
            'transaction_time': self.transaction_time
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            from_user=data['from_user'],
            to_user=data['to_user'],
            amount=data['amount'],
            transaction_type=TransactionType(data['transaction_type']),
            category=Category(data['category']),
            description=data['description'],
            transaction_time=datetime.fromisoformat(data['transaction_time'])
        )