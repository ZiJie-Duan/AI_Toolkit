import asyncio
import json
import websockets

import datetime
print("123123")

SECRET_KEY = "your_secret_key"

async def handle_message(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        username = data['username']
        password = data['password']
        # 处理数据
        print(username)
        print(password)
        
        token = "Mozhiao"
        
        response = {'status': 'success', "token": token}
        print(response)
        await websocket.send(json.dumps(response))



start_server = websockets.serve(handle_message, '0.0.0.0', 3000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
