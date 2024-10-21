"""profile 錯誤類別"""

class OutOfLevelRange(Exception):
    """超出等級搜索"""
    def __init__(self, num) -> None:
        super().__init__(F"超出等級範圍\n當前範圍:0~{num}")
