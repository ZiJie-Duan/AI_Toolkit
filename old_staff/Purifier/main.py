# -*- coding: utf-8 -*-
from module.GPT_API import GPT_API
from module.Config import Config
from module.StoryBoard import StoryBoard
import time

class Purifier:

    def __init__(self) -> None:
        self.cfg = Config()
        self.gpt = GPT_API(self.cfg("GPT.api_key"))
        self.gpt.set_model(self.cfg("GPT.model"))
        self.storyboard = StoryBoard()

        self.outPutFile = self.cfg("Purifier.OutPut")
        self.inPutFile = self.cfg("Purifier.InPut")
        self.text_lenth = self.cfg("Purifier.text_lenth")

    def write_text(self,text) -> None:
        # 将文本写入文件
        with open(self.outPutFile, "a", encoding="utf-8") as file:
            file.write(text)


    def get_text(self) -> str:
        # 从文件中获取文本
        text = None
        with open(self.inPutFile, "r", encoding="utf-8") as file:
            text = file.read()

        for i in range(0, len(text), self.text_lenth):
            yield text[i : i + self.text_lenth]
        yield text[i + self.text_lenth :]


    def prompt(self, text) -> None:
        self.storyboard.add_dialogue("system", 
                    self.cfg(self.cfg("PROMPTS.prompt")))
        text += self.cfg("PROMPTS.prompt_text")
        self.storyboard.add_dialogue("user", text)
        result = self.storyboard.get_dialogue_history()
        self.storyboard.set_dialogue_history([])
        return result
    

    def start(self):

        for text in self.get_text():

            print(text)
            print("开始查询。。。\n\n")

            dialog = self.prompt(text)

            for i in range(10):
                try:
                    # 使用GPT_API进行查询
                    ai_response = \
                        self.gpt.query(dialog,
                                        self.cfg("GPT.temperature"),
                                        self.cfg("GPT.max_tokens"))
                    
                    self.write_text(ai_response)
                    print(ai_response)
                    print("AI回复...\n\n")
                    break
                except Exception as e:
                    print(e)
                    print("正在重试...\n\n")
                    time.sleep(10)


if __name__ == "__main__":
    purifier = Purifier()
    purifier.start()

