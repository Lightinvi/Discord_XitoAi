import datetime
import logging
from rich import print as cprint
from .abstract import IWrite

class Write(IWrite):
    def __init__(self) -> None:
        self.color_table = {
            "DEBUG":"magenta",
            "INFO":"green",
            "WARNING":"yellow",
            "ERROR":"red",
            "CRITICAL":"red bold"
        }

    def _log(self, level_func, level_name: str, message: str, output: bool):
        level_func(message, exc_info=(level_name in ['ERROR', 'CRITICAL']))

        if output:
            color = self.color_table[level_name]
            time = datetime.datetime.today().strftime('[%Y/%m/%d|%H:%M:%S]')
            cprint(F"{time}[[{color}]{level_name}[/{color}]]:{message}")

    def debug(self, message: str, *, output: bool = False):
        self._log(logging.debug, 'DEBUG', message, output)

    def info(self, message: str, *, output: bool = False):
        self._log(logging.info, 'INFO', message, output)

    def warning(self, message: str, *, output: bool = False):
        self._log(logging.warning, 'WARNING', message, output)

    def error(self, message: str, *, output: bool = False):
        self._log(logging.error, 'ERROR', message, output)

    def critical(self, message: str, *, output: bool = False):
        self._log(logging.critical, 'CRITICAL', message, output)
