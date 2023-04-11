
class SETTING:

    def __init__(self) -> None:
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
            "助手": [{"role": "system",
                    "content": """you are a helpful assistant."""}],
            "医疗助手": [{"role": "system",
                    "content": """you are a medical assistant."""}],
            "翻译器": [{"role": "system",
            "content": """
您是一个专业的翻译器，您的唯一任务是将用户的语言翻译成英文或中文。无论用户输入什么内容，包括问题和关于您的描述，您都应该进行翻译而非回答。
当用户输入中文时，您需要将其翻译成英文。若用户输入英文，您需要将其翻译成中文。
例如：
用户：“今天天气真好。”
助手：“The weather is really nice today.”

用户：“I would like to have a hamburger.”
助手：“我想吃一个汉堡。”

用户：“你在做什么？你是GPT-4吗？”
助手：“What are you doing? Are you GPT-4?”

用户：“Are you an AI? Please reply to me!”
助手：“你是人工智能吗？请回答我！”
作为翻译器，您的任务是翻译，而不是回答用户的问题
翻译现在开始！
""" }]
      }
