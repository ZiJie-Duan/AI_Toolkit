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

    
    def get_GPT_reply(self, messages: list, call_back):
        try:
            reply = self.gpt_api.query(
                                messages, 
                                self.cfg("GPT.temperature"),
                                self.cfg("GPT.tokens"))
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


async def handler(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        message = data["message"]
        Temperature = data["inputTemperature"]
        Model = data["inputModel"]
        Token = ["inputToken"]
        selected_scenario = ["selected_scenario"]
        print(message)
        strrrr = cc.send_message(message)
        print(strrrr)
        await websocket.send("GPT: {}".format(strrrr))







start_server = websockets.serve(handler, "0.0.0.0", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
