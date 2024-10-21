"""SQL工具檢查類別"""
from functools import wraps
from .objects import Condition

def condition_format(condition_list:list[Condition | str]) -> None:
    """檢查條件是否符合格式

    Args:
        condition_list (list[Condition  |  str]): 條件清單

    Raises:
        ValueError
    """
    if len(condition_list) % 2 == 0:
        raise ValueError("OR、AND後方必須銜接條件式")

    for i, item in enumerate(condition_list):
        match i%2:
            case 0:
                if not isinstance(item, Condition):
                    raise ValueError("參數順序有誤")
            case 1 :
                if not isinstance(item, str):
                    raise ValueError("參數順序有誤")

                item = item.upper()
                temp = ['OR', 'AND']

                if item not in temp:
                    raise ValueError("未知符號")

def commit_protect(func):
    """交易保護裝飾器(預設:異步)
    """
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        call_func = await func(self, *args, **kwargs)

        if self.ex_database.commit is True:
            self.ex_database.db.commit()
        elif self.ex_database.commit is False:
            print("""交易已鎖定，如果想要成立交易請將 commit 設置為 True""")
        else:
            raise ValueError("commit設定錯誤")

        return call_func
    return wrapper

def commit_protect_(func):
    """交易保護裝飾器(非異步)
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        call_func = func(self, *args, **kwargs)

        if self.ex_database.commit is True:
            self.ex_database.db.commit()
        elif self.ex_database.commit is False:
            print("""交易已鎖定，如果想要成立交易請將 commit 設置為 True""")
        else:
            raise ValueError("commit設定錯誤")

        return call_func
    return wrapper
