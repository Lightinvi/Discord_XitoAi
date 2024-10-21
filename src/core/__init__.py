# pylint: disable=missing-docstring
import pandas as pd
from .cog_ex import CogExtension,Bot,Slash
from .logger import Logger
from .MsSQL_ORM import *
from .error import OutOfLevelRange
from .type import *

#db_account = DBUser('sa','test123')
#db_server = DBServer('127.0.0.1:52938','XitoAi')

db_account = DBUser('Lightinvi','ej; up30627')
db_server = DBServer('server.lightinvi.idv','XitoAi')
