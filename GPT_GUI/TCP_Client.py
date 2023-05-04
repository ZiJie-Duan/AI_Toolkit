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

    def recv_all(self, sock: object, data_len: bytes) -> bytes:
        data = b''
        remaining = int(data_len.decode('utf-8'))
        while remaining > 0:
            recv_data = sock.recv(min(remaining, self.buffer_size))
            data += recv_data
            remaining -= len(recv_data)
        return data
    
    def recv_stream(self, sock: object) -> bytes:
        recv_data = sock.recv().encode('utf-8')
        return recv_data

    def pack_data(self, data: dict) -> tuple[bytes, bytes]:
        data = json.dumps(data).encode('utf-8')
        data_len = str(len(data)).encode('utf-8')
        return data_len, data
    
    def unpack_data(self, data: bytes) -> dict:
        return json.loads(data.decode('utf-8'))

    def start(self, 
              data_dict: dict, 
              stream = False,
              stream_state_call = None,
              stream_update_call = None,
              stream_final_call = None
              ) -> dict:
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         # 创建 SSL/TLS 上下文
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # 将套接字包装为 SSL/TLS 套接字
        security_client_socket = context.wrap_socket(client_socket)

        security_client_socket.connect((self.host, self.port))

        if stream:
            try:
                data_len, data = self.pack_data(data_dict)

                # send the length of data to remind the server
                security_client_socket.sendall(data_len)
                _reply = security_client_socket.recv(self.buffer_size)

                # send the data
                security_client_socket.sendall(data)
                # reveive the length of reply
                reply_len = security_client_socket.recv(self.buffer_size)
                
                security_client_socket.sendall(b'ok')
                # receive the reply
                reply_data = self.recv_all(security_client_socket, reply_len)
                
                reply_dict = self.unpack_data(reply_data)

                if stream_state_call(reply_dict):
                    while True:
                        recv_data = self.recv_stream()
                        if "/<<--END-->>/" not in recv_data:
                            stream_update_call(recv_data)
                        else:
                            break
                    
                    # send the data
                    security_client_socket.sendall(b'ok')
                    # reveive the length of reply
                    reply_len = security_client_socket.recv(self.buffer_size)

                    security_client_socket.sendall(b'ok')
                    # receive the reply
                    reply_data = self.recv_all(security_client_socket, reply_len)
                    stream_final_call(reply_data)

            finally:
                security_client_socket.close()
        
            return reply_dict

        else:
            try:
                data_len, data = self.pack_data(data_dict)

                # send the length of data to remind the server
                security_client_socket.sendall(data_len)
                _reply = security_client_socket.recv(self.buffer_size)

                # send the data
                security_client_socket.sendall(data)
                # reveive the length of reply
                reply_len = security_client_socket.recv(self.buffer_size)

                security_client_socket.sendall(b'ok')
                # receive the reply
                reply_data = self.recv_all(security_client_socket, reply_len)
                
                reply_dict = self.unpack_data(reply_data)
            finally:
                security_client_socket.close()
        
            return reply_dict


# if __name__ == '__main__':
#     client = TCPClient()
#     client.start({"this":"是个测试"})
