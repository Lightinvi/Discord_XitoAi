import json

from typing import Optional,List,Type
from dataclasses import dataclass,field

from .error import OutOfLevelRange

@dataclass(frozen=True)
class StarLevel:
    level:int = field(default=None)
    convert:str = field(default=None)
    need_for:int = field(default=None)
    next_need:int = field(default=None)

    @classmethod
    def level_list(cls, search_level:Optional[int] = None) -> List['StarLevel'] | Type['StarLevel']:
        with open("systemDocumentation\\starLevel.json", 'r', encoding="utf-8") as file:
            data = json.load(file)

        result_list: List[cls] = []
        for level, requirements in dict(data['list']).items():
            result_list.append(
                cls(
                    int(level),
                    str(data['convert'][level]),
                    int(requirements),
                    dict(data['list']).get(str(int(level) + 1), None)
                )
            )

        if search_level is None:
            return result_list
        if search_level > len(result_list)-1 or search_level < 0:
            raise OutOfLevelRange(len(result_list)-1)
        return result_list[search_level]

class LevelMethod():
    """星級輸出轉換方法"""
    @staticmethod
    def convert(member_level:str | int) -> str:
        """轉換字型輸出

        Args:
            user_level (str | int): 成員等級(原始型態)

        Returns:
            MemberLevel (str): 轉換視覺化輸出
        """
        member_level = int(member_level)
        return StarLevel.level_list(member_level).convert

    @classmethod
    def level_check(cls, member_online_time:int, convert:bool = False) -> str:
        """等級對應

        Args:
            member_online_time (int): 成員總在線時數
            convert (bool, optional): 預設輸出原始型態,當為True時轉換為視覺化輸出. Defaults to False.

        Returns:
            MemberLevel (str): 回傳對應結果
        """

        for level in StarLevel.level_list():
            level:StarLevel
            if level.next_need is None:
                member_level = str(len(StarLevel.level_list())-1)
                break
            if level.need_for <= member_online_time < level.next_need:
                member_level = str(level.level)
                break

        if convert is True:
            return cls.convert(member_level)
        return member_level
