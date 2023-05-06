import socket
import json
import threading
import ssl
from pprint import pprint

class TCPServer:
    def __init__(self, server_address=('localhost', 12345), buffer_size=4096):
        self.server_address = server_address
        self.buffer_size = buffer_size
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_socket.bind(self.server_address)
        self.server_socket.listen(5)

         # 加载证书和私钥
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(certfile='server.crt', keyfile='server.key')


    def recv_all(self, sock: object, data_len: bytes) -> bytes:
        data = b''
        remaining = int(data_len.decode('utf-8'))
        while remaining > 0:
            recv_data = sock.recv(min(remaining, self.buffer_size))
            data += recv_data
            remaining -= len(recv_data)
        return data

    def pack_data(self, data: dict) -> tuple[bytes, bytes]:
        data = json.dumps(data).encode('utf-8')
        data_len = str(len(data)).encode('utf-8')
        return data_len, data
    
    def unpack_data(self, data: bytes) -> dict:
        return json.loads(data.decode('utf-8'))
    
    def esay_send(self, sock: object, data: dict) -> dict:
        data_len, data_pack = self.pack_data(data)
        # --> 1. send data length
        sock.sendall(data_len)
        # <-- 2. recv reply
        _reply = sock.recv(self.buffer_size)
        # --> 3. send data
        sock.sendall(data_pack)

    def esay_recv(self, sock: object) -> dict:
        # <-- 1. recv data length
        data_len = sock.recv(self.buffer_size)
        # --> 2. send reply
        sock.sendall(b'ok')
        # <-- 3. recv data
        user_original_data = self.recv_all(sock, data_len)
        user_data = self.unpack_data(user_original_data)
        return user_data
    

class GPT_TCPServer(TCPServer):

    def __init__(self, server_address=('localhost', 12345), buffer_size=4096):
        super().__init__(server_address, buffer_size)
        self.data_process = None
        self.data_process_stream = None

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

# if __name__ == '__main__':
#     data_processor = DataProcessor()
#     server = TCPServer(data_processor)
#     server.start()
