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
    def __init__(self, memo: Memo = None):
        self.memo = memo
        self.dialogue_history = self.init_dialogue_history()
    
    def init_dialogue_history(self):
        if self.memo:
            return self.memo.read_from_file()
        else:
            return []

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
        if self.memo:
            self.memo.write_to_file(self.dialogue_history)

