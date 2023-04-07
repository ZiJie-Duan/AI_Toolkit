import socket
import json
import threading
import ssl

class TCPServer:
    def __init__(self, server_address=('localhost', 12345), buffer_size=4096):
        self.server_address = server_address
        self.buffer_size = buffer_size
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_process = None
        
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

    def start(self, lisent=5):
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(lisent)

         # 加载证书和私钥
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile='server.crt', keyfile='server.key')

        while True:
            print('等待客户端连接...')
            connection, client_address = self.server_socket.accept()
            # 将套接字包装为 SSL/TLS 套接字
            secure_sock = context.wrap_socket(connection, server_side=True)
            threading.Thread(target=self.handle, args=(secure_sock, client_address)).start()
            
    def handle(self, connection, client_address):
        try:
            print('连接来自:', client_address)
            # 接收数据长度
            data_len = connection.recv(self.buffer_size)
            connection.sendall(b'ok')

            # 接收数据
            data = self.recv_all(connection, data_len)
            received_dict = self.unpack_data(data)
            print('接收到的字典:', received_dict)

            # 处理数据
            reply_dict = self.data_process(received_dict)

            # 打包数据
            reply_len, reply_data = self.pack_data(reply_dict)

            # 发送数据长度
            connection.sendall(reply_len)
            _reply = connection.recv(self.buffer_size)
            # 发送数据
            connection.sendall(reply_data)

        except Exception as e:
            print(f'异常: {e}')

        finally:
            connection.close()

# if __name__ == '__main__':
#     data_processor = DataProcessor()
#     server = TCPServer(data_processor)
#     server.start()
