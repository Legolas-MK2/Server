# public module
import socket
from time import sleep
# own module
import Cipher


encoding = "utf-8"
buffer_recv = 4096


class My_Socket:
    def __init__(self, sock):
        self.socket = sock
        self.key = None

    def try_connect(self, ip, port):
        try:
            self.socket.connect((ip, port))
            return self.socket  # Server found
        except ConnectionRefusedError:
            return None         # no Server found

    def read(self, crypt=True):
        recv = self.socket.recv(buffer_recv)
        if crypt:
            recv = Cipher.AES_decrypt_text(recv, self.key)
            recv = str(recv, "utf-8")

        sleep(0.1)
        return recv

    def send(self, msg, crypt=True):
        if crypt:
            msg = bytes(msg, "utf-8")
            msg = Cipher.AES_encrypt_text(msg, self.key)

        sleep(0.1)
        self.socket.send(msg)

    def close(self):
        try:
            self.send("Server")
            self.send("#C")
        except:
            pass

        self.socket.close()
