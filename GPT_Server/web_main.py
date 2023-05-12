import json
import websockets
import asyncio
import threading
from module.Config import Config
from module.StoryBoard import Memo, StoryBoardx
from module.TCP_Client import TCPClient
from module.TCP_Client import GPT_TCPClient
from module.GPT_API import GPT_API

class Web_Client:

    def __init__(self, 
                host, port, 
                
                temperature: float = 0.5,
                max_tokens: int = 200,
                messageID = None,
                websocket = None,
                storyboard = None,
                online = False, 
                key = "None",):
        
        
        print(key)
        self.gpt_api = GPT_API(key)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.messageID = messageID
        self.websocket = websocket
        self.storyboard = storyboard

    async def get_GPT_reply(self, messages: list):
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
        cfg = Config()

        reply = {}
        data = json.loads(message)
        print(data)
        Key = data["Key"]
        
        selected_scenario = data["selected_scenario"]
        storyBoard = data["chatHistory"]
        message = data["message"]
        Temperature = float(data["inputTemperature"])
        
        Token = int(data["inputToken"])
        massageSendStr = data["massageSendStr"]
        #[{"role":"system", "content":"you are a helpful assistant"},.....]
        storyboard = StoryBoardx()


        storyboard.set_dialogue_history(storyBoard)
        storyboard.root_insert(selected_scenario, message)
        dialog = storyboard.get_dialogue_history()

        cc = Web_Client(cfg("SOCKET.host"),
                                   cfg("SOCKET.port"),
                                   Temperature,
                                   Token,
                                   massageSendStr,
                                   websocket,
                                   storyboard,
                                   online=cfg("SYSTEM.online"),
                                   key=cfg("GPT.api_key"),)
        
        await cc.get_GPT_reply(dialog)


start_server = websockets.serve(handler, "0.0.0.0", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()