import datetime
import logging
from .abstract import ISetting

class Setting(ISetting):

    def __init__(self, setting:dict = None) -> None:
        if setting:
            self._encoding = setting["encoding"]
            self._level = self._log_level(setting["level"])
            self._location =\
                F"{setting["location"]}\\{datetime.datetime.today().strftime('%Y-%m-%d')}.log"
        else:
            self._encoding = "utf-8"
            self._level = logging.INFO
            self._location = F"{datetime.datetime.today().strftime('%Y-%m-%d')}.log"

        self._configure_logging()

    def _configure_logging(self):
        logging.basicConfig(
            filename=self._location,
            encoding=self._encoding,
            level=self._level,
            datefmt='%Y/%m/%d|%H:%M:%S',
            format='[%(asctime)s][%(levelname)s]:%(message)s'
        )

    def _log_level(self, level_str:str):
        levels = {
            "DEBUG":logging.DEBUG,
            "INFO":logging.INFO,
            "WARNING":logging.WARNING,
            "ERROR":logging.ERROR,
            "CRITICAL":logging.CRITICAL
        }
        return levels.get(level_str,logging.INFO)

    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def level(self) -> str:
        levels = {
            logging.DEBUG: "DEBUG",
            logging.INFO: "INFO",
            logging.WARNING: "WARNING",
            logging.ERROR: "ERROR",
            logging.CRITICAL: "CRITICAL"
        }
        return levels.get(self._level, self._level)

    @property
    def location(self) -> str:
        return self._location
