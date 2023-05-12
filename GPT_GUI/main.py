from module.TCP_Client import TCPClient
from module.GPT_API import GPT_API
from module.StoryBoard import Memo, StoryBoard
from module.Config import Config
from module.Exception_Handler import exception_handler
from chat_gui import CHAT_GUI
from pprint import pprint
import threading
import uuid

class Chat_StoryBoard(StoryBoard):

    def __init__(self, memo: Memo = None):
        super().__init__(memo)
        self.message_dic = {}
    
    def add_dialogue_pair(self, question: str, reply: str):
        self.add_dialogue("user", question)
        self.add_dialogue("assistant", reply)

    def prompt(self, prompt: str, question: str, event_id: str, 
               index=None, front=None, back=None):
        self.message_dic[event_id] = {"user": question}
        dialogue = self.get_dialogue_history(front, back)
        
        dialogue.append({"role": "user", "content": question})

        if index != None:
            dialogue.insert(index, {"role": "system", "content": prompt})
        else:
            dialogue.append({"role": "system", "content": prompt})

        return dialogue

    def insert_reply(self, event_id, reply: str):
        question = self.message_dic[event_id]["user"]
        del self.message_dic[event_id]
        self.add_dialogue_pair(question, reply)
    
    def abandon_event(self, event_id):
        del self.message_dic[event_id]

class GPT_TCPClient(TCPClient):

    def __init__(self, server_address=('localhost', 12345), buffer_size=4096):
        super().__init__(server_address, buffer_size)
    
    def request_GPT(self, data_dict: dict) -> dict:
        """
        a basic request function
        data_dict and the server_reply are both dict
        """
        server_reply = None
        sec_client_sock = self.connect_server(self)

        try:
            self.easy_send(sec_client_sock,data_dict)
            server_reply = self.easy_recv(sec_client_sock)

        except Exception as e:
            print("error from TCP_Client: ", e)
            return server_reply

        finally:
            sec_client_sock.close()

        return server_reply

    def request_stream_GPT(self,
                    message: dict,
                    stream_verify = None,
                    stream_update_call = None
                    ) -> dict:
        """
        this function have three methods to return data
        1. stream_verify
        2. stream_update_call # update the text chunk
        3. return reply_dict # return some detail info
        """

        sec_client_sock = self.connect_server()

        try:
            # 发送请求
            self.easy_send(sec_client_sock, message)
            reply_dict = self.easy_recv(sec_client_sock)
            
            full_text = ""
            # 判断是否通过验证
            if stream_verify(reply_dict):
                
                for text in self.recv_stream_chunk(sec_client_sock):
                    stream_update_call(text)
                    full_text += text

                reply_dict = self.easy_recv(sec_client_sock)

        finally:
            sec_client_sock.close()
        return reply_dict, full_text

class GPT_Client:

    def __init__(self, 
                host, port, 
                online = False, 
                key = "None"):
        
        self.tcp_client = GPT_TCPClient((host,port))
        self.gpt_api = GPT_API(key)
        self.online = online
    
    def set_arguments(self,
                    model: str,
                    stream: bool = False,
                    temperature: float = 0.5,
                    max_tokens: int = 200,
                    version_key: str = "None",
                    user_key: str = "None",
                    normal_call_back = None,
                    stream_state_callback = None,
                    stream_update_callback = None,
                    stream_end_callback = None
                    ):
        self.gpt_api.set_model(model)
        self.model = model
        self.stream = stream
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.version_key = version_key
        self.user_key = user_key

        # these three callbacks are used for stream mode only
        # stream_state_callback is used for online mode only
        # stream_state_callback 
        #   input: dict
        #   return: bool, True for continue, False for stop
        self.stream_state_callback = stream_state_callback
        # stream_update_callback
        #   input: str
        self.stream_update_callback = stream_update_callback
        # stream_end_callback
        #   input: dict {"state": str, "detail":{}, ...}
        self.stream_end_callback = stream_end_callback

        # this callback is used for normal mode only
        # input: dict {"state": str, "detail":{}, ...}
        self.normal_call_back = normal_call_back 

    @exception_handler
    def send_message(self, messages: list, event_id: str = "") -> None:
        """
        send message to the GPT-3 API and get the response
        """
        if self.online:
            task = threading.Thread(target=self.get_server_reply,args=(messages,event_id))
            task.start()
        else:
            task = threading.Thread(target=self.get_GPT_reply,args=(messages))
            task.start()

    def get_GPT_reply(self, messages: list):
        if self.stream:
            try:
                reply = self.gpt_api.query(
                            messages, 
                            self.temperature,
                            self.max_tokens,
                            stream = True)
                #self.stream_state_callback()
                full_text = ""
                chunk = None
                for chunk in reply:
                    text = chunk["choices"][0].get("delta", {}).get("content")
                    if text:
                        self.stream_update_callback(text)
                        full_text += text

                self.stream_end_callback({"state":"success" ,"detail": {}}, full_text)

            except:
                err_reply = "GPT API出现错误, 请检查网络并联系开发者"
                self.stream_end_callback({"state":err_reply ,"detail": {}}, None)
        else:
            try:
                reply = self.gpt_api.query(
                                    messages, 
                                    self.temperature,
                                    self.max_tokens)
                self.normal_call_back({"state": "success", "reply": reply, "detail": {}})
            
            except:
                reply = None
                err_reply = "GPT API出现错误, 请检查网络并联系开发者"
            self.normal_call_back({"state": err_reply, "reply": reply, "detail": {}})

    def get_server_reply(self, messages: str, event_id: str = "") -> None:

        if self.stream:
            reply = {}
            data = {"version_key": self.version_key,
                    "user_key": self.user_key,
                    "model": self.model,
                    "storyboard": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "event_id": event_id,
                    "stream": self.stream}
            reply, full_reply = self.tcp_client.request_stream_GPT(data,
                            self.stream_state_callback,
                            self.stream_update_callback)
            self.stream_end_callback(reply,full_reply)

        else:
            reply = {}
            data = {"version_key": self.version_key,
                    "user_key": self.user_key,
                    "model": self.model,
                    "storyboard": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "event_id": event_id,
                    "stream": self.stream}

            reply = self.tcp_client.request_GPT(data)
            self.normal_call_back(reply)

class CHAT_CORE:

    def __init__(self):
        self.cfg = Config()

        self.memo = Memo(self.cfg("MEMO.file_path"))
        self.storyboard = Chat_StoryBoard(self.memo)

        self.chat_gui = CHAT_GUI(
            title = self.cfg("GUI.title"),
            geometry = self.cfg("GUI.geometry"),
            selected_scenario = self.cfg("PROMPT.selected_scenario"),
            selected_model = self.cfg("GPT.model"),
            scenario = self.cfg("PROMPT.scenario").split(","),
            models = self.cfg("GPT.models").split(","),
            temperature = self.cfg("GPT.temperature"),
            max_tokens = self.cfg("GPT.tokens"),
            user_key = self.cfg("SOCKET.user_key"),
            settings_callback = self.settings,
            send_message_callback = self.send_mesag,
            refresh_dialogue_callback = self.refresh_dialogue,
            restart_dialogue_callback = self.restart_dialogue
        )
        self.gpt_core = GPT_Client(self.cfg("SOCKET.host"),
                                   self.cfg("SOCKET.port"),
                                   online=self.cfg("SYSTEM.online"),
                                   key=self.cfg("GPT.api_key"))
                                   
        self.message_temp = ""
    
    def set_gpt_arguments(self):
        self.gpt_core.set_arguments(
            model = self.cfg("GPT.model"),
            temperature = self.cfg("GPT.temperature"),
            max_tokens = self.cfg("GPT.tokens"),
            stream = self.cfg("GPT.stream"),
            version_key = self.cfg("SOCKET.version_key"),
            user_key = self.cfg("SOCKET.user_key"),
            stream_state_callback = self.stream_verify,
            stream_update_callback = self.stream_update,
            stream_end_callback = self.stream_end
        )
    
    def info_analyze(self,state):
        if state == "user_key_error":
            self.print_info("用户密钥错误或过期, 请重新获取","系统")
        elif state == "version_key_error":
            self.print_info("软件版本过期, 请联系开发者更新","系统")
        elif state == "argument_error":
            self.print_info("参数错误, 请检查设置","系统")
 
    def stream_verify(self,reply):
        print("stream_verify:")
        pprint(reply)
        if reply["state"] == "success":
            self.chat_gui.insert_message(self.cfg("prompt.selected_scenario")+": ",False)
            return True
        else:
            self.info_analyze(reply["state"])
            return False
        
    def stream_update(self,text):
        self.chat_gui.insert_message(text, enter = False)
        self.message_temp += text

    def stream_end(self,reply,full_reply):
        pprint(reply)

        self.chat_gui.insert_message("")
        event_id = reply["details"]["event_id"]

        if "usage" in reply["details"]:
            usage = reply["details"]["usage"]
        if "finish_reason" in reply["details"]:
            # if details donot have finish_reason
            # it means the event is abandoned
            finish_reason = reply["details"]["finish_reason"]
            self.storyboard.insert_reply(event_id,full_reply)

        else:
            self.storyboard.abandon_event(event_id)

        self.message_temp = ""
        self.update_dialogue_counter()

    def send_mesag(self,message):
        event_id = str(uuid.uuid4())

        if len(message) > 500:
            self.print_info("输入过长, 请重新输入","系统")
            self.print_info(message,"系统")
            return

        self.chat_gui.insert_message("\n用户: " + message)
        if self.cfg("prompt.selected_scenario") == "assistant":
            promot = "you are a helpful assistant"
            dialog = self.storyboard.prompt(promot,message,event_id,0)

        if self.cfg("prompt.selected_scenario") == "teacher":
            promot = "you are a teacher"
            dialog = self.storyboard.prompt(promot,message,event_id,0)

        self.gpt_core.send_message(dialog,event_id)

    def settings(self, model: str, temperature: float, 
                 max_tokens: int, scenario: str, 
                 user_key: str, hidden: bool = False) -> bool:
        """
        set the temperature, max_tokens and scenario
        return True if the settings are valid
        """
        # scenario_chanege = False
        # if self.cfg("prompt.selected_scenario") != scenario:
        #     scenario_chanege = True

        # if temperature < self.cfg("GPT.min_temperature")\
        #     or temperature > self.cfg("GPT.max_temperature"):
        #     self.print_info("温度值错误, 请重新设置", "系统")
        #     return False
        
        # if max_tokens < self.cfg("GPT.min_tokens")\
        #     or max_tokens > self.cfg("GPT.max_tokens"):
        #     self.print_info("Max_Tokens数错误, 请重新设置", "系统")
        #     return False
        
        self.cfg.set("GPT","model",model)
        self.cfg.set("GPT","temperature",temperature)
        self.cfg.set("GPT","tokens",max_tokens)
        self.cfg.set("prompt","selected_scenario",scenario)
        self.cfg.set("SOCKET","user_key",user_key)

        self.set_gpt_arguments()
        if not hidden:
            self.print_info("设置已保存", "系统")
        return True
        # if scenario_chanege:
        #     self.print_info("情景已切换, 正在 '重启对话' ", "系统")
        #     self.restart_dialogue()
        
        # the change of scenario will apply after restart dialogue
    
    def update_dialogue_counter(self) -> None:
        num_of_dialogue = len(self.storyboard.get_dialogue_history())//2
        if num_of_dialogue\
              >= self.cfg("SOTRYBOARD.max_dialogue")\
                    - num_of_dialogue:
            info = "对话次数已达推荐上限 \n您可以继续进行对话 \n但为了程序稳定 \n推荐您尽快结束对话 \n并点击重启对话按钮"
            self.chat_gui.update_dialogue_counter_text(info, color="red")
        else:
            info = "建议对话次数 剩余：" \
                + str(self.cfg("SOTRYBOARD.max_dialogue")\
                    - num_of_dialogue)
            self.chat_gui.update_dialogue_counter_text(info)
    
    def restart_dialogue(self) -> None:
        """
        clean the dialogue history and restart the dialogue
        """
        self.storyboard.set_dialogue_history([])
        self.refresh_dialogue()
        self.print_info("对话已重启", "系统")
        self.print_info("对话开启", "系统")
        self.update_dialogue_counter()
    
    def refresh_dialogue(self) -> None:
        """refresh the dialogue history
         when the dialogue history be mess up or destoryed,
         this function can recover it via the storyboard
        """
        self.chat_gui.clear_dialogue()
        messages = self.storyboard.get_dialogue_history()
        for message in messages:
            if message["role"] == "user":
                self.chat_gui.insert_message("用户: " + message["content"])
            elif message["role"] == "system":
                self.chat_gui.insert_message("[系统]: " + message["content"])
            else:
                self.chat_gui.insert_message(
            self.cfg("prompt.selected_scenario")+": "+message["content"])

    def print_info(self, info: str, role: str) -> None:
        self.chat_gui.insert_message("[{}]: {}".format(role, info))

    def help(self):
        self.print_info("欢迎使用 GPT_GUI_v2.1 Alpha", "系统")
        self.print_info("请遵循OpenAI使用条例", "系统")
        self.print_info(
        """
保护隐私：请勿在请求中包含您自己、他人或任何个人的敏感信息，如姓名、地址、电话号码、身份证号等。

合法使用：确保您的请求和用途符合您所在国家/地区的法律法规，遵守知识产权、隐私权以及其他相关法律法规。

遵守道德规范: 不要使用API来制作、传播或推广仇恨言论、歧视、暴力、欺凌, 犯罪行为或不道德内容。

使用限制: 遵循OpenAI API使用限制, 不要通过过高频率的请求或自动化程序滥用服务，以避免对系统造成过大负荷。

信息安全: 在分享或公开API的结果时,确保不泄露您的API密钥或包含敏感信息的请求。
        """, "系统")
        self.print_info("此程序将对话记录存储至软件根目录下的memo.json文件", "系统")
        self.print_info("使用方法：", "系统")
        self.print_info("'Temperature', 'Max_Tokens' 修改后需要点击设置进行保存", "系统")
        self.print_info("'情景选择' 修改后将自动 '重启对话' 进行应用", "系统")
        self.print_info("'刷新' 将去除所有的系统提示, 仅保留对话信息", "系统")
        self.print_info("'重启对话' 将清空对话记录, 并重新开始对话", "系统")
        self.print_info("'Temperature' 范围 0.1 - 2.0 ", "系统警告")
        self.print_info("'Max_Tokens' 范围 10 - 2000 ", "系统警告")
    
def main():

    #try:
    chat_core = CHAT_CORE()
    chat_core.help()
    chat_core.chat_gui.mainloop()
    # except Exception as e:
    #     try:
    #         chat_core.print_info("错误信息: " + str(e), "系统错误")
    #         chat_core.print_info("程序出现错误, 请联系开发者", "系统错误")
    #     except:
    #         pass
    #     print(e)
    #     print("程序出现错误, 请联系开发者")
    # return 0
        
if __name__ == "__main__":
    main()
