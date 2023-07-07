from TCP_Client import TCPClient
import threading
import asyncio
import websockets
import json
print("123123")


class CHAT_CORE:

    def __init__(self):
        self.tcp_client = TCPClient(("47.74.85.241", 12345))
        

    def send_message(self,message: str) -> None:

        messages = [{"role": "system", "content": "you are a helpful assistant."}]
        messages.append({"role": "user", "content": message})

        data = {"key": "KZF_KEY_FIRST_VERSION",
                "storyboard": messages,
                "temperature": 0.5,
                "max_tokens": 200}
        
        try:
            ai_response = self.tcp_client.start(data)
        except Exception as e:
            self.print_info("错误信息: " + str(e), "系统错误")
            self.print_info("程序网络模块出现错误,检查网络并请联系开发者", "系统错误")

        if ai_response["info"] == "success":
            reply = ai_response["reply"]
        elif ai_response["info"] == "key_error":
            reply = "程序秘钥错误，请联系开发者，更新程序"

        return reply
    


cc = CHAT_CORE()


async def handler(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        message = data["message"]
        Temperature = data["inputTemperature"]
        Model = data["inputModel"]
        Token = ["inputToken"]
        print(message)
        strrrr = cc.send_message(message)
        print(strrrr)
        await websocket.send("GPT: {}".format(strrrr))


start_server = websockets.serve(handler, "0.0.0.0", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
