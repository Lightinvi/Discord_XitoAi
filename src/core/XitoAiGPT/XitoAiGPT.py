import threading
from typing import Optional
from gpt4all import GPT4All

from .decorator import single_create

@single_create
class XitoAiGPT():
    """XitoAi聊天生成器(測試)
    """
    def __init__(self) -> None:
        with open("systemDocumentation\\system_prompt.txt","r",encoding="utf-8") as text:
            system_prompt = text.read()
        self._model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf",device="cuda")
        self._context_manager = self._model.chat_session(
                system_prompt=system_prompt
            )
        self._chat:Optional[GPT4All] = None
        self._task = None

    def create_chat(self):
        """創建聊天上下文管理器
        """
        self._chat = self._context_manager.__enter__()

    def start(self):
        """啟動GPT
        """
        self._task = threading.Thread(target=self.create_chat)
        self._task.start()

    def restart(self):
        """重啟GPT
        """
        del self._task
        self._task = threading.Thread(target=self.create_chat)
        self._task.start()

    def generate(self, content:str, max_token:int = 500):
        """生成回應
        """
        if self._chat is None:

            return "生成模型未加載,請聯繫開發者"
        return self._chat.generate(prompt=content, max_tokens=max_token)
