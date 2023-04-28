
class SETTING:

    def __init__(self) -> None:
        self.GPT_API_KEY = "sk-"
        self.GPT_MODEL = "gpt3.5"
        self.memo_file = "memo.json"
        
        self.temperature = 0.5
        self.max_tokens = 100
        self.scenario = "助手"
        self.record = True # used to record the dialogue history

        self.host = ""
        self.port = 12345
        self.kzf_key = ""

        self.max_dialogue = 10

        # back ground is a list of dict
        # back ground is a part of the dialogue history
        # each dict has two keys: role and content
        self.back_ground = {
            "助手2": [{"role": "system",
                    "content": """你是一个信息提取机器人，请你提取文本中的关键信息（论点，论证，举例，规则，要求等），转为一整段陈述性文字，不需要介绍和补充任何信息。用中文回答"""}],
            "助手": [{"role": "system",
                    "content": """你是一个信息提取机器人，列出文本中的关键信息并加以总结"""}]}
