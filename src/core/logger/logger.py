import json

from .decorator import single_create
from .setting import Setting
from .write import Write
from .abstract import ILoggerUI

@single_create
class Logger(ILoggerUI):

    def __init__(self, setting:str = None) -> None:
        if setting:
            with open(setting, "r", encoding="utf-8") as js_setting:
                setting = json.load(js_setting)
        self._setting = Setting(setting)
        self._write = Write()

    @property
    def setting(self) -> Setting:
        return self._setting

    @property
    def write(self) -> Write:
        return self._write
