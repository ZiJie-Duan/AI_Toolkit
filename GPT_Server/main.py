
from GPT_API import GPT_API
from Config import Config
from TCP_Server import GPT_TCPServer
from Key_Manager import KeyManager
from token_tool import TokenCounter
import functools
import click
import time

class GPT_Server:
    def __init__(self):
        self.cfg = Config()
        self.gpt_api = GPT_API(self.cfg("GPT.api_key"))
        self.TCP_server = GPT_TCPServer((self.cfg("SOCKET.host"), 
                                     self.cfg("SOCKET.port")))
        self.TCP_server.data_process = self.socket_data_process
        self.TCP_server.data_process_stream = self.socket_data_process_stream
        self.version_key = self.cfg("SOCKET.version_key")
        self.keymanager = KeyManager(self.cfg("USERKEY.file_path"))

        self.model_list = self.cfg("GPT.models").split(',')
        self.token = TokenCounter()

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
        self.TCP_server.start()
    

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
