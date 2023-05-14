from module.GPT_API import GPT_API
from module.Config import Config
from module.TCP_Server import TCPServer
from module.Key_Manager import KeyManager
from module.token_tool import TokenCounter
from web_main import GPT_WebServer # 导入我们的web_main.py，GPT_WebServer类是我们和主程序衔接的接口
from threading import Thread
import socket
import ssl
from pprint import pprint
from functools import partial
from time import sleep
import datetime

CONFIG_FILE = "/www/GPT_python_v3/server_config.ini"
#CONFIG_FILE = "server_config.ini"

class GPT_TCP_Server(TCPServer):

    def __init__(self, server_address=('localhost', 12345), 
                 buffer_size=4096, ssl_files=('server.crt','server.key')):
        super().__init__(server_address, buffer_size, ssl_files)
        self.data_process = None
        self.stream_feedback = None

    def start(self):

        while True:
            print('\n[gpt_tcp_server]: 等待用户连接...')
            orig_connection, client_address = self.server_socket.accept()
            try:
                new_thread = Thread(target=self.handle, args=(orig_connection, client_address))
                new_thread.start()
            except ssl.SSLError as e:
                print(f'[gpt_tcp_server]: SSL 错误 {e}')
                orig_connection.close()
            except socket.timeout as e:
                print(f"[gpt_tcp_server]: 握手超时 {e}")
                orig_connection.close()


    def handle(self, orig_connection, client_address):
        connection = None
        # try:
        connection = self.context.wrap_socket(orig_connection, server_side=True)

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print('[gpt_tcp_server]: {} 连接来自 {}'.format(current_time, client_address))
        user_data = self.esay_recv(connection)
        
        print("[gpt_tcp_server]: 用户数据(debug)")
        pprint(user_data)

        # 处理数据 判断是否为流式数据
        # 如果请求失败，则使用非流式传输错误反馈
        result_dict, stream = self.data_process(user_data)
        if stream:
            print("[gpt_tcp_server]: 允许流式数据传输\n")

            self.esay_send(connection, result_dict)

            # sent stream
            ai_reply = ""
            chunk = None
            stream_flow = stream()
            print("\nAI: ",end="")
            for chunk in stream_flow:
                word = chunk["choices"][0].get("delta", {}).get("content")
                if word:
                    print(word,end="")
                    ai_reply += word
                    # --> 8. 流式发送数据
                    connection.sendall(word.encode('utf-8'))
            # --> 9. 流式发送结束标志
            connection.sendall(self.stream_end.encode("utf-8"))
            print("\n[gpt_tcp_server]: 流式数据发送完毕\n")

            # 生成反馈
            reply_dict = self.stream_feedback(user_data,ai_reply,chunk)
            
            self.esay_send(connection, reply_dict)

        else:
            self.esay_send(connection, result_dict)

        # except Exception as e:
        #     print(f'异常 来自handle函数: {e}')

        # finally:
        #     if connection:
        #         connection.close()

class GPT_Server():
    """
    a connection between GPT_API and TCP_Server
    """
    def __init__(self):
        self.cfg = Config(path = CONFIG_FILE)
        self.gpt_api = GPT_API(self.cfg("GPT.api_key"))
        self.TCP_server = GPT_TCP_Server((self.cfg("SOCKET.host"), 
                                     self.cfg("SOCKET.port")),
                        ssl_files=(self.cfg("SOCKET.cert_file"),
                                   self.cfg("SOCKET.key_file")))

        self.GPT_WebServer = GPT_WebServer(
                ssl_files=(self.cfg("WEB.cert_file"),
                            self.cfg("WEB.key_file")),
                server_address=(self.cfg("WEB.host"),
                                self.cfg("WEB.port")))
        
        self.GPT_WebServer.data_process = self.data_process #使用回调函数的方式，导入我们的数据处理函数
        self.GPT_WebServer.stream_feedback = self.stream_feedback #以及流式数据处理函数

        self.TCP_server.data_process = self.data_process
        self.TCP_server.stream_feedback = self.stream_feedback
        self.version_key = self.cfg("SOCKET.version_key")
        self.keymanager = KeyManager(self.cfg("USERKEY.file_path"))

        self.model_list = self.cfg("GPT.models").split(',')
        self.token = TokenCounter()
    
    def story_board_check(self, storyboard: list) -> bool:
        for item in storyboard:
            if item["role"] not in ["user", "assistant", "system"]:
                return False
        return True

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

    def data_check(self, data: dict) -> dict:
        reply = {
            "state" : "None", 
            "message" : "None",
            "details" : {"event_id" : data["event_id"]}
        }
        if not self.data_structure(data):
            print("[data_process]: 特殊异常 数据结构错误")
            return reply, False

        elif data["version_key"] != self.version_key:
            reply["state"] = "version_key_error"
            reply["message"] = "程序版本密钥错误，请联系开发者，更新程序"
            print("[data_process]: 程序版本密钥错误")
            return reply, False

        elif not self.keymanager.check_key(data["user_key"]):
            reply["state"] = "user_key_error"
            reply["message"] = "用户密钥不存在 或已过期，请重新获取密钥"
            print("[data_process]: 用户密钥错误")
            return reply, False
        
        elif self.argument_check(data):
            reply["state"] = "argument_error"
            reply["message"] = "参数错误, 请检查各项参数是否超出范围"
            print("[data_process]: 参数错误")
            return reply, False
        
        elif not self.story_board_check(data["storyboard"]):
            reply["state"] = "argument_error"
            reply["message"] = "故事板角色设定错误, 请检查故事板参数是否正确"
            print("[data_process]: 故事板角色设定错误")
            return reply, False
        
        else:
            reply["state"] = "success"
            reply["message"] = "success"
            return reply, True

    
    def stream_feedback(self, user_data: dict,
                                   ai_reply: str,
                                   details: dict) -> dict:

        token_promote = self.token.get_token(user_data["model"],
                             user_data["storyboard"],
                             process="Prompt")
        token_complete = self.token.get_token(user_data["model"],
                             [{"role":"assistant", "content":ai_reply}],
                             process="Completion")
        
        total_token_used = token_promote + token_complete
        _, token_remain = self.keymanager.decrease_value(
                                        user_data["user_key"], 
                                        total_token_used)
        reply = {"details":{}}
        reply["details"]["event_id"] = user_data["event_id"]
        reply["details"]["model"] = details["model"]
        reply["details"]["token_remain"] = token_remain
        reply["details"]["finish_reason"] = details["choices"][0]["finish_reason"]
        return reply

    def data_process(self, data: dict) -> dict:
        """
        data process function only has two return value
        1. reply: dict
        2. ai_generator: generator or False
        ai_generator is used for stream transmission
        False is used for normal transmission
        """

        reply, check = self.data_check(data)

        if not check:
            return reply, False
        
        if data["stream"]:
            
            reply["state"] = "success"
            reply["message"] = "success"
            
            ai_generator = partial(
                            self.gpt_api.query_stream,
                            data["storyboard"],
                            float(data["temperature"]),
                            int(data["max_tokens"]),
                            data["model"],
                            full=True)
            return reply, ai_generator
        
        else:
            ai_reply = self.gpt_api.query(data["storyboard"],
                                    float(data["temperature"]),
                                    int(data["max_tokens"]),
                                    data["model"],
                                    full=True)
            
            token_promote = self.token.get_token(data["model"],
                        data["storyboard"])
            
            token_complete = self.token.get_token(data["model"],
                    [{"role":"assistant", "content":ai_reply}])
            
            total_token_used = token_promote + token_complete
            _, token_remain = self.keymanager.decrease_value(
                            data["user_key"], 
                            total_token_used)
            
            reply["state"] = "success"
            reply["message"] = "success"
            reply["reply"] = ai_reply["choices"][0]["message"]["content"]
            reply["details"]["event_id"] = data["event_id"]
            reply["details"]["model"] = ai_reply["model"]
            reply["details"]["token_remain"] = token_remain
            reply["details"]["finish_reason"] = ai_reply["choices"][0]["finish_reason"]

            return reply, False

    def start(self):
        
        # 这里改用了多线程　同时启动我们的TCP服务器和Web服务器
        tcp_server = Thread(target=self.TCP_server.start)
        web_server = Thread(target=self.GPT_WebServer.start)

        tcp_server.start()
        web_server.start() # 启动我们的GPT　Web服务器　

        # here to wait the tcp server to stop
        tcp_server.join()
        web_server.join()
    

def main():
    print("[main] 初始化服务器...")
    server = GPT_Server()
    while True:
        print("[main] 进入服务器主循环...\n")
        server.start()
        sleep(3)
        print("[main] 重启服务器...\n")
    

if __name__ == '__main__':
    main()



# example data structure

# data = {
#     "version_key" : "12kiw....",
#     "user_key" : "df3pt....",
#     "model" : "gpt-3.5-turbo",
#     "storyboard" : [{...},{...},...],
#     "temperature" : 1.5,
#     "max_tokens" : 200,
#     "event_id" : "12kiw....",
#     "stream" : "False"
# }

# reply = {
#     "state" : "success", 
#     # "success" or "user_key_error" or "version_key_error"
#     # "argument_error"
#     "message" : "None", # server feedback message
#     "reply" : "None",
#     "details" : {
#         "event_id" : "12kiw....",
#         "model" : "gpt-3.5-turbo",
#         "token_remain": "2330",
#         'finish_reason': 'stop',
#         } # API return detail
# }
