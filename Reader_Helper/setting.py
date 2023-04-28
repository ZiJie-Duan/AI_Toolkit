
class SETTING:

    def __init__(self) -> None:
        self.GPT_API_KEY = ""
        self.GPT_MODEL = "gpt3.5"
        self.memo_file = "memo.json"

        self.back_ground = """请将user发送的文本翻译为中文"""
        #self.back_ground = """请用书面的英文表达user发送的中文文本,如果user发送的是英文,请你优化user发送的英文"""
        
        self.host = ""
        self.port = 12345
        self.kzf_key = ""

