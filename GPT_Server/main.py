
from ..Module.GPT_API import GPT_API
from ..Module.Config import Config
from ..Module.TCP_Server import TCPServer
from ..Module.Key_Manager import KeyManager
from ..Module.token_tool import TokenCounter
#from web_main import GPT_WebServer # 导入我们的web_main.py，GPT_WebServer类是我们和主程序衔接的接口
from threading import Thread
from pprint import pprint
import functools
import click
import time


class GPT_Server(TCPServer):
    """
    a connection between GPT_API and TCP_Server
    """
    def __init__(self, server_address=('localhost', 12345), buffer_size=4096):
        super().__init__(server_address, buffer_size)
        self.data_process = None
        self.data_process_stream = None

        self.cfg = Config()
        self.gpt_api = GPT_API(self.cfg("GPT.api_key"))
        self.TCP_server = GPT_TCPServer((self.cfg("SOCKET.host"),  #######重构哈！别忘记了~~~~~~~~~~ 段子杰自己要重构哈！！！！！！！！！
                                     self.cfg("SOCKET.port")))
        
        # self.GPT_WebServer = GPT_WebServer() #实例化我们的 服务器类
        # self.GPT_WebServer.data_process = self.socket_data_process #使用回调函数的方式，导入我们的数据处理函数
        # self.GPT_WebServer.data_process_stream = self.socket_data_process_stream #以及流式数据处理函数

        self.TCP_server.data_process = self.socket_data_process
        self.TCP_server.data_process_stream = self.socket_data_process_stream
        self.version_key = self.cfg("SOCKET.version_key")
        self.keymanager = KeyManager(self.cfg("USERKEY.file_path"))

        self.model_list = self.cfg("GPT.models").split(',')
        self.token = TokenCounter()
    
    def start(self):

        while True:
            print('\n等待客户端连接...')
            orig_connection, client_address = self.server_socket.accept()
            try:
                new_thread = threading.Thread(target=self.handle, args=(orig_connection, client_address))
                new_thread.start()
            except ssl.SSLError as e:
                print(f'SSL 错误: {e}')
                orig_connection.close()
            except socket.timeout as e:
                print(f"握手超时: {e}")
                orig_connection.close()


    def handle(self, orig_connection, client_address):
        connection = None
        # try:
        connection = self.context.wrap_socket(orig_connection, server_side=True)

        print('连接来自:', client_address)
        user_data = self.esay_recv(connection)
        pprint(user_data)
        # 处理数据 判断是否为流式数据
        result_dict, stream = self.data_process(user_data)
        if stream:

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
            connection.sendall("/<<--END-->>/".encode("utf-8"))
            print()
            # 生成反馈
            reply_dict = self.data_process_stream(user_data,ai_reply,chunk)
            
            self.esay_send(connection, reply_dict)

        else:
            self.esay_send(connection, result_dict)

        # except Exception as e:
        #     print(f'异常 来自handle函数: {e}')

        # finally:
        #     if connection:
        #         connection.close()

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
    
    def socket_data_process_stream(self, user_data: dict,
                                   ai_reply: str,
                                   details: dict) -> dict:

        token_promote = self.token.get_token(user_data["model"],
                             user_data["storyboard"],
                             self.cfg("USERKEY.user_choice"))
        token_complete = self.token.get_token(user_data["model"],
                             [{"role":"assistant", "content":ai_reply}],
                             self.cfg("USERKEY.user_choice"))
        total_token_used = token_promote + token_complete
        self.keymanager.decrease_value(user_data["user_key"], 
                                        total_token_used)
        reply = {"details":{}}
        reply["details"]["event_id"] = user_data["event_id"]
        reply["details"]["model"] = details["model"]
        reply["details"]["usage"] = total_token_used
        reply["details"]["finish_reason"] = details["choices"][0]["finish_reason"]
        return reply

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
            "event_id" : "12kiw....",
            "stream" : "False"
        }

        reply = {
            "state" : "success", 
            # "success" or "user_key_error" or "version_key_error"
            # "argument_error"
            "message" : "None", # server feedback message
            "reply" : "None",
            "details" : {
                "event_id" : "12kiw....",
                "model" : "gpt-3.5-turbo",
                'usage': {'prompt_tokens': 56, 'completion_tokens': 31, 'total_tokens': 87},
                'finish_reason': 'stop',
                } # API return detail
        }

        """
        reply = {
            "state" : "None", 
            "message" : "None",
            "reply" : "None",
            "details" : {}
        }
        if not self.data_structure(data):
            return reply, False

        elif data["version_key"] != self.version_key:
            reply["state"] = "version_key_error"
            reply["message"] = "程序版本密钥错误，请联系开发者，更新程序"
            return reply, False

        elif not self.keymanager.check_key(data["user_key"]):
            reply["state"] = "user_key_error"
            reply["message"] = "用户密钥不存在 或已过期，请重新获取密钥"
            return reply, False
        
        elif self.argument_check(data):
            reply["state"] = "argument_error"
            reply["message"] = "参数错误, 请检查各项参数是否超出范围"
            return reply, False
        
        else:
            if data["stream"]:
                reply["state"] = "success"
                reply["message"] = "success"
                
                ai_generator = functools.partial(
                                self.gpt_api.query,
                                data["storyboard"],
                                float(data["temperature"]),
                                int(data["max_tokens"]),
                                data["model"],
                                stream=True,
                                full=True)
                return reply, ai_generator
            
            else:
                ai_reply = self.gpt_api.query(data["storyboard"],
                                        float(data["temperature"]),
                                        int(data["max_tokens"]),
                                        data["model"],
                                        full=True)
                
                token_promote = self.token.get_token(data["model"],
                            data["storyboard"],
                            self.cfg("USERKEY.user_choice"))
                token_complete = self.token.get_token(data["model"],
                            [{"role":"assistant", "content":ai_reply}],
                            self.cfg("USERKEY.user_choice"))
                total_token_used = token_promote + token_complete
                
                reply["state"] = "success"
                reply["message"] = "success"
                reply["reply"] = ai_reply["choices"][0]["message"]["content"]
                reply["details"]["event_id"] = data["event_id"]
                reply["details"]["model"] = ai_reply["model"]
                reply["details"]["usage"] = total_token_used
                reply["details"]["finish_reason"] = ai_reply["choices"][0]["finish_reason"]

                self.keymanager.decrease_value(data["user_key"], 
                                ai_reply["usage"]["total_tokens"])
                return reply, False

    def start(self):
        # 这里改用了多线程　同时启动我们的TCP服务器和Web服务器
        tcp_server = Thread(target=self.TCP_server.start)
        # web_server = Thread(target=self.GPT_WebServer.start).start() 
        tcp_server.start()
        # web_server.start() # 启动我们的GPT　Web服务器　

        # here to wait the tcp server to stop
        tcp_server.join()
    

@click.group()
def cli():
    pass

@click.command(help='run gpt server')
def run():
    server = GPT_Server()
    while True:
        server.start()
        time.sleep(3)
        print("restart server")
    

@click.command(help='key manager')
@click.option('--add', '-a', help='add a new key', is_flag=True)
@click.option('--delete', '-d', help='delete a key', is_flag=True)
@click.option('--ls', '-l', help='list all keys', is_flag=True)
@click.argument('key', type=str, required=False) # n is None
@click.argument('value', type=int, required=False)
def key(add, delete, ls, key=None, value=2000):
    cfg = Config()
    keymanager = KeyManager(cfg("USERKEY.file_path"))
    if add:
        if key == 'n':
            key = None
        keymanager.add_key_value(key=key, value=value)
        print("add key-value")
        print(key, value)
    elif delete:
        if key is None or key == 'n':
            print("Please enter the correct arguments")
            return
        keymanager.remove_key(key)
        print("delete key")
        print(key)
    elif ls:
        print("list all keys\n")
        kv = keymanager.get_all_keys_value()
        print("-"*50)
        for k, v in kv:
            print(f"{k:<40s} : {v:<10d}")
        print("-"*50)
    else:
        print("Please enter the correct command")

cli.add_command(key)
cli.add_command(run)

if __name__ == '__main__':
    #cli()
    run()
