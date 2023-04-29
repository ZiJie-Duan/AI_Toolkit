
from GPT_API import GPT_API
from Config import Config
from TCP_Server import TCPServer
from Key_Manager import KeyManager

class GPT_Server:
    def __init__(self):
        self.cfg = Config()
        self.gpt_api = GPT_API(self.cfg("GPT.api_key"))
        self.TCP_server = TCPServer((self.cfg("SOCKET.host"), 
                                     self.cfg("SOCKET.port")))
        self.TCP_server.data_process = self.socket_data_process
        self.version_key = self.cfg("SOCKET.version_key")
        self.keymanager = KeyManager(self.cfg("USERKEY.file_path"))

        self.model_list = self.cfg("GPT.models").split(',')

    def data_structure(self, data: dict):
        """
        check the data structure
        """
        if "version_key" not in data or \
            "user_key" not in data or \
            "model" not in data or \
            "storyboard" not in data or \
            "temperature" not in data or \
            "max_tokens" not in data:
            return False
        return True

    def argument_check(self, data: dict) -> bool:
        """
        check the argument of the data
        """
        if data["max_tokens"] > self.cfg("GPT.max_tokens") or \
            data["max_tokens"] < self.cfg("GPT.min_tokens"):
            return True
        if data["temperature"] > self.cfg("GPT.max_temperature") or \
            data["temperature"] < self.cfg("GPT.min_temperature"):
            return True
        if data["model"] not in self.model_list:
            return True
        return False


    def socket_data_process(self, data: dict) -> dict:
        """
        example data structure

        data = {
            "version_key" : "12kiw....",
            "user_key" : "df3pt....",
            "model" : "gpt-3.5-turbo",
            "storyboard" : [{...},{...},...],
            "temperature" : 1.5,
            "max_tokens" : 200,
        }

        reply = {
            "state" : "success", 
            # "success" or "user_key_error" or "version_key_error"
            # "argument_error"
            "message" : "None", # server feedback message
            "reply" : "None",
            "detail" : {
                'id': 'chatcmpl-6p9XYPYSTTRi0xEviKjjilqrWU2Ve',
                "model" : "gpt-3.5-turbo",
                'usage': {'prompt_tokens': 56, 'completion_tokens': 31, 'total_tokens': 87},
                'finish_reason': 'stop',
                } # API return detail
        }

        """
        reply = {
            "state" : "None", 
            "message" : "None", # "max_tokens不能超过2000"
            "reply" : "None",
            "detail" : {}
        }

        if not self.data_structure(data):
            return reply

        elif data["version_key"] != self.version_key:
            reply["state"] = "version_key_error"
            reply["message"] = "程序版本密钥错误，请联系开发者，更新程序"
        
        elif not self.keymanager.check_key(data["user_key"]):
            reply["state"] = "user_key_error"
            reply["message"] = "用户密钥不存在 或已过期，请重新获取密钥"
        
        elif self.argument_check(data):
            reply["state"] = "argument_error"
            reply["message"] = "参数错误, 请检查各项参数是否超出范围"
        
        else:
            ai_reply = self.gpt_api.query_full(data["storyboard"],
                                       float(data["temperature"]),
                                       int(data["max_tokens"]))
            reply["state"] = "success"
            reply["message"] = "success"
            reply["reply"] = ai_reply["choices"][0]["message"]["content"]
            reply["detail"]["id"] = ai_reply["id"]
            reply["detail"]["model"] = ai_reply["model"]
            reply["detail"]["usage"] = ai_reply["usage"]
            reply["detail"]["finish_reason"] = ai_reply["choices"][0]["finish_reason"]

            self.keymanager.decrease_value(data["user_key"], 
                            ai_reply["usage"]["total_tokens"])
        
        return reply
            
    def start(self):
        self.TCP_server.start()
    

def main():
    gpt_server = GPT_Server()

    while True:
        gpt_server.start()

if __name__ == '__main__':
    main()
