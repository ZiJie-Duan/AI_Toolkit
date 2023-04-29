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
    def __init__(self, memo: Memo):
        self.memo = memo
        self.dialogue_history = self.memo.read_from_file()
    
    def add_dialogue(self, role: str, content: str, index=None):
        if index:
            self.dialogue_history.insert(index,
                {"role": role, "content": content})
        else:
            self.dialogue_history.append(
                {"role": role, "content": content},
            )

    def get_dialogue_history(self,front=None,back=None) -> List[Dict[str, str]]:
        return self.dialogue_history[front:back]

    def set_dialogue_history(self, dialogue_history: List[Dict[str, str]]):
        self.dialogue_history = dialogue_history[:]
    
    def save(self):
        self.memo.write_to_file(self.dialogue_history)


class StoryBoardx(StoryBoard):

    def __init__(self, memo: Memo):
        super().__init__(memo)
    
    def root_insert(self,promote,message):
        self.add_dialogue_role("sys",promote,0)
        self.add_dialogue_role("user",message)
        return self.get_dialogue_history()
    
    def single_message_front_insert(self,promote,message):
        self.add_dialogue_role("sys",promote)
        self.add_dialogue_role("user",message)
        return self.get_dialogue_history(front=-2)
    
    def ai_insert(self,reply):
        self.add_dialogue_role("ai",reply)

    def add_dialogue_role(self, role: str, content: str, index=None):
        # auto match the role. role: user, ai, sys
        if role == "user":
            self.add_dialogue("user",content,index)
        elif role == "ai":
            self.add_dialogue("assistant",content,index)
        elif role == "sys":
            self.add_dialogue("system",content,index)

    def remove_sys(self):
        dialog = self.get_dialogue_history()
        dialog = [log for log in dialog if log["role"] != "system"]
        self.set_dialogue_history(dialog)




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
