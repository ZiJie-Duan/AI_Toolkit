import json
from typing import List, Dict

class Memo:
    def __init__(self, filename: str):
        self.filename = filename

    def read_from_file(self) -> List[Dict[str, str]]:
        try:
            with open(self.filename, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []
        return data

    def write_to_file(self, dialogue_history: List[Dict[str, str]]):
        with open(self.filename, "w") as file:
            json.dump(dialogue_history, file, indent=2)

class StoryBoard:
    def __init__(self, memo: Memo, back_ground: list[Dict]):
        self.memo = memo
        self.dialogue_history = self.memo.read_from_file()
        self.back_ground_insert(back_ground=back_ground["助手"])

    def add_dialogue_entry(self, user_input: str, ai_response: str):
        self.dialogue_history.append(
            {"role": "user", "content": user_input},
        )
        self.dialogue_history.append(
            {"role": "assistant", "content": ai_response},
        )
        self.memo.write_to_file(self.dialogue_history)

    def get_dialogue_history(self) -> List[Dict[str, str]]:
        return self.dialogue_history[:]

    def back_ground_insert(self,back_ground: list[Dict]) -> None: 
        if self.dialogue_history == []:
            print(back_ground)
            self.dialogue_history = back_ground[:]
            

# # 创建一个Memo对象，设置文件名为"dialogue_history.json"
# memo = Memo("dialogue_history.json")

# # 创建一个StoryBoard对象，将memo传入初始化
# storyboard = StoryBoard(memo)

# # 添加一些对话条目
# storyboard.add_dialogue_entry("What's the weather like today?", "The weather is sunny today.")
# storyboard.add_dialogue_entry("What is the capital of France?", "The capital of France is Paris.")

# # 获取对话历史并打印
# dialogue_history = storyboard.get_dialogue_history()
# for entry in dialogue_history:
#     print(f"{entry['role'].capitalize()}: {entry['content']}")

# 输出:
# System: You are a helpful assistant.
# User: What's the weather like today?
# Assistant: The weather is sunny today.
# User: What is the capital of France?
# Assistant: The capital of France is Paris.
