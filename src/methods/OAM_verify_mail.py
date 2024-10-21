# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=E1101
from email.mime.text import MIMEText
from email.utils import formataddr
from string import Template
from pathlib import Path
import smtplib
import random
import string
from dataclasses import field,dataclass
from src.core import SQL,db_account,db_server
#smtp.office365.com 587
#smtp.gmail.com 587

async def send_verify_mail(username:str, user_mail:str, verify_code):
    smtp=smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(
        'lightinvipeng@gmail.com',
        'tlkd ptdd psmd nkiy'
        )

    template = Template(Path("systemDocumentation\\verify_mail.html").read_text(encoding='utf-8'))
    content = template.substitute({"username":username,"verify_code":verify_code})

    msg = MIMEText(content,'html')   #目前最後一行會傳遞錯誤資訊
    msg['Subject'] = "XitoAi電子郵件驗證碼"         #主旨
    msg['From'] = formataddr(("XitoAi Developer",'lightinvipeng@gmail.com'))

    msg['To'] = user_mail                     #收信者

    smtp.sendmail('lightinvipeng@gmail.com', user_mail, msg.as_string())

def generate_verify_code():
    confusing_letters = '0oOiIlLzsQe'
    valid_characters = ''.join(set(string.ascii_letters + string.digits) - set(confusing_letters))
    return ''.join(random.SystemRandom().choice(valid_characters) for _ in range(6))
