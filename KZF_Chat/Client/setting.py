
class SETTING:

    def __init__(self) -> None:
        self.GPT_API_KEY = "sk-"
        self.GPT_MODEL = "gpt3.5"
        self.memo_file = "memo.json"

        self.temperature = 0.5
        self.max_tokens = 100
        self.scenario = "助手"

        self.host = "47.74.89.229"
        self.port = 12345
        self.kzf_key = "Z"

        self.back_ground = """assistant, 你是一名摄影师"""
        