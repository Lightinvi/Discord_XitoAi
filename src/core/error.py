"""錯誤類別"""

class UnknownConditional(Exception):
    """未知條件符號"""
    def __init__(self) -> None:
        super().__init__("錯誤的條件符號")

class OutOfLevelRange(Exception):
    """超出等級搜索"""
    def __init__(self, num) -> None:
        super().__init__(F"超出等級範圍\n當前範圍:0~{num}")
