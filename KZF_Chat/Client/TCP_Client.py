import socket
import json
import ssl

class TCPClient:
    """
    this is a TCP client class
    all the data will be packed into a dict
    """
    def __init__(self, server_address=('localhost', 12345), buffer_size=4096):
        self.host, self.port = server_address
        self.buffer_size = buffer_size
        self.client_socket = None

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

    def start(self, data_dict: dict):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         # 创建 SSL/TLS 上下文
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # 将套接字包装为 SSL/TLS 套接字
        self.client_socket = context.wrap_socket(client_socket)

        self.client_socket.connect((self.host, self.port))

        try:
            data_len, data = self.pack_data(data_dict)

            # send the length of data to remind the server
            self.client_socket.sendall(data_len)
            _reply = self.client_socket.recv(self.buffer_size)

            # send the data
            self.client_socket.sendall(data)
            # reveive the length of reply
            reply_len = self.client_socket.recv(self.buffer_size)

            self.client_socket.sendall(b'ok')
            # receive the reply
            reply_data = self.recv_all(self.client_socket, reply_len)
            
            reply_dict = self.unpack_data(reply_data)
        finally:
            self.client_socket.close()
        
        return reply_dict


# if __name__ == '__main__':
#     client = TCPClient()
#     client.start({"this":"是个测试"})
