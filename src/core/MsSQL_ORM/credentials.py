"""_summary_
"""
from dataclasses import dataclass

@dataclass
class DBUser():
    """用戶資訊"""
    account:str
    password:str

@dataclass
class DBServer():
    """資料庫資訊"""
    host:str
    database:str = None
