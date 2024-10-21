# pylint: disable=invalid-name
# pylint: disable=missing-docstring
import random
from dataclasses import dataclass
from src.core import Optional
from src.methods import DiscordMember

@dataclass
class ErrorMsgBox:
    msg:str

@dataclass
class LotteryBox:
    """bonus獲得獎金,probability此獎機率,magnification:此獎倍率
    """
    bonus:int
    probability:str
    magnification:str

class LotteryMethod():

    @staticmethod
    def is_in_range(member:DiscordMember,broken_star:int) -> Optional[ErrorMsgBox]:

        if not 0 < broken_star <= 10000:
            return ErrorMsgBox("rangeout")
        if member.broken_star - broken_star < 0:
            return ErrorMsgBox("insufficient")
        return None

    @staticmethod
    def lottery_machine(broken_star: int) -> LotteryBox:
        """
        無 (0): 40% 的機率
        五 (金額*1.5): 25% 的機率
        四 (金額*2): 15% 的機率
        三 (金額*3.5): 10% 的機率
        二 (金額*5): 8% 的機率
        一 (金額*10): 2% 的機率
        """

        outcomes = [
            (0, 0.4, "0"),
            (broken_star * 1.5, 0.25, "1.5"),
            (broken_star * 2, 0.15, "2"),
            (broken_star * 3.5, 0.1, "3.5"),
            (broken_star * 5, 0.08, "5"),
            (broken_star * 10, 0.02, "10")
        ]

        bonus, probability, magnification = random.choices(
            outcomes, weights=[prob for _, prob, _ in outcomes]
            )[0]

        return LotteryBox(bonus, probability, magnification)
