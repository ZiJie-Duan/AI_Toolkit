import threading
import asyncio
import websockets
from Config import Config
from TCP_Client import TCPClient
from TCP_Client import GPT_TCPClient
from GPT_API import GPT_API
from StoryBoard import Memo, StoryBoardx
from Exception_Handler import exception_handler

import json
print("123123")





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

class GPT_Client:

    def __init__(self, 
                host, port, 
                
                temperature: float = 0.5,
                max_tokens: int = 200,
                messageID = None,
                websocket = None,
                storyboard = None,
                online = False, 
                key = "None",):
        
        self.tcp_client = GPT_TCPClient((host,port))
        print(key)
        self.gpt_api = GPT_API(key)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.messageID = messageID
        self.websocket = websocket
        self.storyboard = storyboard

    async def get_GPT_reply(self, messages: list):
        """
        这个函数 用来从GPT服务器获取 回复并向前端发送

        """
        reply_user = {}
        try:
            reply = self.gpt_api.query(
                        messages, 
                        self.temperature,
                        self.max_tokens,
                        stream = True)
            #self.stream_state_callback()
            chunk = None
            messagecurren = []
            for chunk in reply:
                if chunk["choices"][0].get("delta", {}).get("content") is None:
                    continue
                reply_user["chatHistory"] = messages
                reply_user["message"] = chunk["choices"][0].get("delta", {}).get("content")
                reply_user["state"] = "not done"
                reply_user["messageID"] = self.messageID
                messagecurren.append(reply_user["message"])
                await self.websocket.send(json.dumps(reply_user))


            messagecurren = "".join(messagecurren)
            self.storyboard.ai_insert(messagecurren)
            dialog = self.storyboard.get_dialogue_history()

            reply_user["chatHistory"] = dialog
            reply_user["message"] = None
            reply_user["state"] = "done"
            reply_user["messageID"] = self.messageID
            await self.websocket.send(json.dumps(reply_user))

        except:
            err_reply = "GPT API出现错误, 请检查网络并联系开发者"
            reply_user["chatHistory"] = messages
            reply_user["message"] = err_reply
            reply_user["state"] = "done"
            reply_user["messageID"] = self.messageID
            await self.websocket.send(json.dumps(reply_user))
    




async def handler(websocket, path):
    async for message in websocket:
        cfg = Config() # cfg 是一个固定的配置文件，不需要每一次实例化

        reply = {}
        data = json.loads(message)
        print(data)
        Key = data["Key"]
        selected_scenario = data["selected_scenario"]
        storyBoard = data["chatHistory"]
        message = data["message"]
        Temperature = float(data["inputTemperature"])
        Model = data["inputModel"]
        Token = int(data["inputToken"])
        massageSendStr = data["massageSendStr"]
        #[{"role":"system", "content":"you are a helpful assistant"},.....]
        storyboard = StoryBoardx() #这个需要每一次都实例化 确保所有的 对话都是独立的


        storyboard.set_dialogue_history(storyBoard)
        storyboard.root_insert(get_promot(selected_scenario) , message)
        dialog = storyboard.get_dialogue_history()

        # 我懂了，我们可以在这个地方 加入很多和 UI 控件的交互，可以用于审核其参数是否正确等
        # 非常赞！！！

        cc = GPT_Client(cfg("SOCKET.host"),
                                   cfg("SOCKET.port"),
                                   Temperature,
                                   Token,
                                   massageSendStr,
                                   websocket,
                                   storyboard,
                                   online=cfg("SYSTEM.online"),
                                   key=cfg("GPT.api_key"),)
        
        await cc.get_GPT_reply(dialog)

        
        



        # storyboard.ai_insert(aireply)

        # dialog = storyboard.get_dialogue_history()

        # state = "done"

        # reply["chatHistory"] = dialog
        # reply["message"] = aireply
        # reply["state"] = state
        # reply["messageID"] = massageSendStr

        # print(reply)

        # await websocket.send(json.dumps(reply))


class GPT_WebServer:
    # 这个类可以用来　当作　前端和后端的传输接口，也就是　ｊａｃｋｙ　你的一部分的“GPT_Client”的作用
    # 如果Jacky你想的话，可以尝试将代码分层，或者将其结合到一起

    def __init__(self) -> None:
        self.data_process = None #使用回调函数的方式，导入我们的数据处理函数
        self.data_process_stream = None #以及流式数据处理函数

        # jakcy 推荐你阅读一下　data＿ｐｒｏｃｅｓｓ　的源码，这个函数是一个回调函数，你可以在这里加入你的数据处理函数
        #　而data_process_stream是一个流式数据处理函数，这两个函数会被调用，
        #　data_process会分辨　调用方是否为流传输，并且进行请求审查，如果是流传输，我们需要调用data_process_stream并传入相应的参数
    
    def run(self):
        # 这个函数用来启动我们的服务器,　
        start_server = websockets.serve(handler, "0.0.0.0", 8080)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()


