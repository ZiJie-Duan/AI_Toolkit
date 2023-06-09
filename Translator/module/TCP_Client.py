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
        self.stream_end = "/<<--END-->>/"

    def recv_all(self, sock: object, data_len: bytes) -> bytes:
        """
        recv all the data from socket with the data_len
        """
        data = b''
        remaining = int(data_len.decode('utf-8'))
        while remaining > 0:
            recv_data = sock.recv(min(remaining, self.buffer_size))
            data += recv_data
            remaining -= len(recv_data)
        return data

    def pack_data(self, data: dict) -> tuple[bytes, bytes]:
        """
        pack data into bytes and calculate the length of the data
        """
        data = json.dumps(data).encode('utf-8')
        data_len = str(len(data)).encode('utf-8')
        return data_len, data
    
    def unpack_data(self, data: bytes) -> dict:
        """
        unpack data from bytes
        """
        return json.loads(data.decode('utf-8'))

    def recv_stream_chunk(self, sock: object) -> bytes:
        """
        a generator to recv flow data chunk from socket
        """
        while True:
            recv_data = sock.recv(self.buffer_size)
            decoded_data = recv_data.decode('utf-8')

            if self.stream_end in decoded_data:
                yield decoded_data[:decoded_data.index(self.stream_end)]
                break
                
            yield decoded_data

    def easy_send(self, sock: object, data: bytes) -> bytes:
        """
        send data to server
        """
        # pack data
        data_len, data_pack = self.pack_data(data)
        # --> 1. send data length
        sock.sendall(data_len)
        # <-- 2. recv reply
        _reply = sock.recv(self.buffer_size)
        # --> 3. send data
        sock.sendall(data_pack)
    
    def easy_recv(self, sock: object) -> bytes:
        """
        send data to server and recv reply
        """
        # <-- 1. recv data length
        reply_len = sock.recv(self.buffer_size)
        # --> 2. send reply
        sock.sendall(b'ok')
        # <-- 3. recv data data
        reply_data_pack = self.recv_all(sock, reply_len)
        # unpack data
        reply_data = self.unpack_data(reply_data_pack)
        return reply_data
    
    def connect_server(self):
        """
        start a socket and connect to server
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         # 创建 SSL/TLS 上下文
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # 将套接字包装为 SSL/TLS 套接字
        sec_client_sock = context.wrap_socket(client_socket)
        
        try:
            sec_client_sock.connect((self.host, self.port))
        except Exception as e:
            print("error from TCP_Client: ", e)
            return None

        return sec_client_sock
    
