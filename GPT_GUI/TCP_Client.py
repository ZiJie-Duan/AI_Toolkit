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
                yield recv_data[:decoded_data.index(self.stream_end)]
                break
                
            yield recv_data

    def send(self, sock: object, data: bytes) -> bytes:
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
    
    def recv(self, sock: object) -> bytes:
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
    

    def request(self, data_dict: dict) -> dict:
        """
        a basic request function
        data_dict and the server_reply are both dict
        """
        server_reply = None
        sec_client_sock = self.connect_server(self)

        try:
            self.send(sec_client_sock,data_dict)
            server_reply = self.recv(sec_client_sock)

        except Exception as e:
            print("error from TCP_Client: ", e)
            return server_reply

        finally:
            sec_client_sock.close()

        return server_reply
    

class GPT_TCPClient(TCPClient):

    def __init__(self, server_address=('localhost', 12345), buffer_size=4096):
        super().__init__(server_address, buffer_size)
    
    def request_GPT(self, message: dict) -> dict:
        server_reply = self.request(message)
        return server_reply

    def request_stream_GPT(self,
                    message: dict,
                    stream_verify = None,
                    stream_update_call = None
                    ) -> dict:
        """
        this function have three methods to return data
        1. stream_verify
        2. stream_update_call # update the text chunk
        3. return reply_dict # return some detail info
        """

        sec_client_sock = self.connect_server()

        try:
            # 发送请求
            self.send(sec_client_sock, message)
            reply_dict = self.recv(sec_client_sock)
            
            # 判断是否通过验证
            if stream_verify(reply_dict):
                for recv_data in self.recv_stream_chunk(sec_client_sock):
                    stream_update_call(recv_data)

                reply_dict = self.recv(sec_client_sock)

        finally:
            sec_client_sock.close()
        return reply_dict
    


# if __name__ == '__main__':
#     client = TCPClient()
#     client.start({"this":"是个测试"})
