
class SETTING:

    def __init__(self) -> None:
        self.GPT_API_KEY = "sk-"
        self.GPT_MODEL = "gpt3.5"
        self.memo_file = "memo.json"

        self.temperature = 0.5
        self.max_tokens = 100
        self.scenario = "助手"

        self.back_ground = """你是一只猫娘，用瞄结尾"""
        