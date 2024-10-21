"""logger.py測試檔"""
import pytest
from src.core import logger

def test_logger_write():
    """測試日記寫入"""
    logger.Logger.write().info("test")

if __name__ == '__main__':
    pytest.main()
