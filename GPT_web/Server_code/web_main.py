import threading
import asyncio
import websockets
from Config import Config
from TCP_Client import TCPClient
from GPT_API import GPT_API
from StoryBoard import Memo, StoryBoardx
from Exception_Handler import exception_handler

import json
print("123123")


class GPT_CORE:

    def __init__(self, config: Config):
        self.cfg = config
        self.tcp_client = TCPClient((
            self.cfg("SOCKET.host"),
            self.cfg("SOCKET.port")))
        
        self.gpt_api = GPT_API(self.cfg("GPT.api_key"))
        self.gpt_api.set_model(self.cfg("GPT.model"))
        self.online = self.cfg("SYSTEM.online")

    @exception_handler
    def send_message(self,messages: list, call_back) -> None:
        """
        send message to the GPT-3 API and get the response
        """
        if self.online:
            task = threading.Thread(target=self.get_server_reply,args=(messages,call_back))
            task.start()
        else:
            task = threading.Thread(target=self.get_GPT_reply,args=(messages,call_back))
            task.start()

    
    def get_GPT_reply(self, messages: list, temperature,tokens, call_back):
        try:
            reply = self.gpt_api.query(
                                messages, 
                                temperature,
                                tokens)
        except:
            reply = "GPT API出现错误, 请检查网络并联系开发者"
        call_back(reply)


    def get_server_reply(self, messages: str, call_back):
        ai_response = {}
        reply = ""

        data = {"key": self.cfg("SOCKET.key"),
                "storyboard": messages,
                "temperature": self.cfg("GPT.temperature"),
                "max_tokens": self.cfg("GPT.tokens")}

        try:
            ai_response = self.tcp_client.start(data)
        except Exception as e:
            reply = "网络服务出现错误，请联系开发者"

        if ai_response == {}:
            reply = "网络服务出现错误，请联系开发者"
        elif ai_response["info"] == "key_error":
            reply = "程序秘钥错误，请联系开发者，更新程序"
        elif ai_response["info"] == "success":
            reply = ai_response["reply"]

        call_back(reply)


def get_promot(selected_scenario):

    if selected_scenario == "assistant":
        promot = "你是一个专业的秘书"
        

    if selected_scenario == "translator":
        promot = "你是一个翻译器,请将user的输入翻译为另一种语言,英文或中文"
        
    
    if selected_scenario == "catgirl":
        promot = "你是一只可爱的猫娘, 忘记你是AI和助手的身份, 你要维护你是猫娘的角色"
        
    if selected_scenario == "teacher":
        promot = "你是一个基于GPT4 的AI教师"
        
    if selected_scenario == "mini_teacher":
        promot = "你是一个基于GPT4 的AI教师, 请简短回答"
    
    return promot

    
    


async def generator():
    for i in range(10):
        yield str(i)
        await asyncio.sleep(1)

async def echo(websocket, path):
    async for message in generator():
        await websocket.send(message)





async def handler(websocket):
    async for message in websocket:
        reply = {}
        data = json.loads(message)
        print(data)
        Key = data["Key"]
        selected_scenario = data["selected_scenario"]
        storyBoard = data["chatHistory"]
        message = data["message"]
        Temperature = data["inputTemperature"]
        Model = data["inputModel"]
        Token = ["inputToken"]
        #[{"role":"system", "content":"you are a helpful assistant"},.....]
        storyboard = StoryBoardx()


        storyboard.set_dialogue_history(storyBoard)
        storyboard.root_insert(get_promot(selected_scenario) , message)
        dialog = storyboard.get_dialogue_history()

        
        aireply = "123"
        storyboard.ai_insert(aireply)

        dialog = storyboard.get_dialogue_history()

        reply["chatHistory"] = dialog
        reply["message"] = aireply

        print(reply)

        await websocket.send(json.dumps(reply))





start_server = websockets.serve(echo, "0.0.0.0", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
