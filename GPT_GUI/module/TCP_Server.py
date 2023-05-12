import socket
import json
import ssl

class TCPServer:
    def __init__(self, server_address=('localhost', 12345), buffer_size=4096):
        self.server_address = server_address
        self.buffer_size = buffer_size
        self.stream_end = "/<<--END-->>/"

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
    
    def start(self):
        pass

    def handle(self, sock: object, addr: tuple):
        pass
    


