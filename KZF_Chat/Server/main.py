
from GPT_API import GPT_API
from setting import SETTING
from TCP_Server import TCPServer
from threading import Thread

class GPT3Server:
    def __init__(self):
        self.set = SETTING()
        self.gpt_api = GPT_API(self.set.GPT_API_KEY)
        self.TCP_server = TCPServer((self.set.host, self.set.port))
        self.TCP_server.data_process = self.socket_data_process

    def socket_data_process(self, data: dict) -> dict:
        if data["key"] != self.set.kzf_key:
            return {"error": "Key Error"}
        else:
            reply = self.gpt_api.query(data["storyboard"],
                                       float(data["temperature"]),
                                       int(data["max_tokens"]))
            return {"reply": reply}

    def start(self):
        self.TCP_server.start(5)
    

def main():
    gpt3_server = GPT3Server()
    gpt3_server.start()

if __name__ == '__main__':
    main()