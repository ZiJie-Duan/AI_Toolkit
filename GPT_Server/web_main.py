import json
import websockets
import asyncio
import ssl
import threading
from module.Config import Config
from module.StoryBoard import Memo, StoryBoard
from module.TCP_Client import TCPClient
from module.GPT_API import GPT_API


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



class GPT_WebServer:
    
    def __init__(self) -> None:
        self.data_process = None
        self.stream_feedback = None

    async def handler(self, websocket, path):
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
            model = data["inputmodel"]
            Token = int(data["inputToken"])
            massageSendStr = data["massageSendStr"]

            data = {
                "version_key" : "GPT_SERVER_KEY_TEST",
                "user_key" : Key,
                "model" : model,
                "storyboard" : None,
                "temperature" : Temperature,
                "max_tokens" : Token,
                "event_id" : massageSendStr,
                "stream" : True
            }

            #[{"role":"system", "content":"you are a helpful assistant"},.....]
            storybd = Chat_StoryBoard()


            storybd.set_dialogue_history(storyBoard)
            dialog = storybd.prompt(selected_scenario,message,
                                       data["event_id"],0)
            data["storyboard"] = dialog
            
            reply, ai_generator = self.data_process(data)
            print(ai_generator)


        
            


            if reply["state"] != "success":
                reply_user = {
                    "chatHistory" : None,
                    "message" : None,
                    "messageSYS" : reply["message"],
                    "messageID" : massageSendStr,
                    "state" : "false",
                    'usage' : None,
                }

                await websocket.send(json.dumps(reply_user))
                break
                
            stream = ai_generator()
            stenRecv = ""
            chunk = None
            for chunk in stream:
                word = chunk["choices"][0].get("delta", {}).get("content")
                if word:
                    stenRecv += word

                    reply_user = {
                        "chatHistory" : None,
                        "message" : word,
                        "messageSYS" : None,
                        "messageID" : massageSendStr,
                        "state" : "not done",
                        'usage' : None,
                    }

                    await websocket.send(json.dumps(reply_user))
            
            feedback = self.stream_feedback(data,stenRecv,chunk)

            storybd.insert_reply(data["event_id"],stenRecv)
            dialog = storybd.get_dialogue_history()

            reply_user = {
                "chatHistory" : dialog,
                "message" : None,
                "messageSYS" : None,
                "messageID" : feedback["details"]["event_id"],
                "state" : "done",
                'usage' : feedback["details"]["usage"]
            }
            await websocket.send(json.dumps(reply_user))
            
    def start(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain('/www/GPT_python_v3/asjdaskdk/server.crt', '/www/GPT_python_v3/asjdaskdk/server.key')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(websockets.serve(self.handler, "0.0.0.0", 8080))
        loop.run_forever()

            



    # def handle(self):
        
    #     # recv 自己客户端的请求

    #     # 拼凑出 data数据结构
    #     # 将data数据结构传入 
    #     reply, ai_generator = self.data_process(data)
    #     if reply +? success
        
    #     stream = ai_generator()
    #     assss = ""
    #     chunk = None
    #     for chunk in stream:
    #         word = chunk["choices"][0].get("delta", {}).get("content")
    #         if word:
    #             assss += word
    #             send.....

    #     feedback = self.stream_feedback(data,assss,chunk)
    #     sendfjajndaligh

        

    