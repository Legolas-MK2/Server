# public module
import os
import socket
import json
import sys
import time
from time import sleep
from base64 import b64encode, b64decode
# own module
import Cipher


encoding = "utf-8"
buffer_recv = 1024


class My_Socket:
    def __init__(self, sock: socket.socket):
        self.socket = sock
        self.key = None

    def try_connect(self, ip, port):
        try:
            self.socket.connect((ip, port))
            return self.socket  # Server found
        except ConnectionRefusedError:
            return None         # no Server found

    def read(self, crypt=True) -> dict:
        recv = self.socket.recv(buffer_recv)
        print(sys.getsizeof(recv))
        if crypt:
            recv = Cipher.AES_decrypt_text(recv, self.key)
            recv = recv.decode("utf-8")
            recv = bytes2json(recv)

        sleep(0.1)
        return recv

    def read_file(self, filename):
        print("bekomme eine file")
        if not os.path.exists(r"temp"):
            os.mkdir("temp")

        with open(rf"temp\{filename}", "wb") as file:
            bytes_recv = self.socket.recv(buffer_recv)
            while bytes_recv:
                file.write(bytes_recv)
                print(bytes_recv)
                bytes_recv = self.socket.recv(buffer_recv)

    def send(self, msg: dict, crypt=True):
        if crypt:
            msg = json2bytes(msg)
            msg = Cipher.AES_encrypt_text(msg, self.key)

        sleep(0.1)
        self.socket.send(msg)

    def send_file(self, path):
        temp = 0
        temp2 = 0
        balken_size = 10
        with open(path, "rb") as file:
            while True:
                file_bytes = file.read(buffer_recv)
                print("-------------------------------")
                print(file_bytes)
                print("-------------------------------")
                self.socket.send(file_bytes)
                if not file_bytes:
                    time.sleep(0.5)
                    self.socket.send(b'a')
                    time.sleep(0.5)
                    send_empty(self.socket)
                    time.sleep(0.5)
                    self.socket.send(b'b')
                    print("break")
                    break
                else:
                    temp += sys.getsizeof(file_bytes)
                    load_value = round((temp / os.path.getsize(path)) * balken_size)
                    if load_value == temp2:
                        continue
                    temp2 = load_value
                    if load_value <= balken_size:
                        #sys.stdout.write('\r' + f"8{r'=' * load_value}D")
                        sys.stdout.write('\r' + f"[{r'#'*load_value}{' '*(load_value*-1+balken_size)}]")
            sys.stdout.write('\r')
        print("file zuende")

    def close(self):
        try:
            self.send({"receiver": "Server",
                       "message": {
                           "command": "#C"
                       }})
        except:
            pass

        self.socket.close()


def json2bytes(json_,recursive=False):
    for key in json_:
        if type(json_[key]) == dict:
            json_[key] = json2bytes(json_[key], True)
        else:
            temp = bytes(str(json_[key]), "utf-8")
            temp = b64encode(temp)
            json_[key] = str(temp, "utf-8")
    if recursive: return json_
    return bytes(json.dumps(json_), "utf-8")


def bytes2json(bytes_, recursive=False):
    if recursive:
        json_ = bytes_
    else:
        json_ = json.loads(bytes_)
    for key in json_:
        if type(json_[key]) == dict:
            json_[key] = bytes2json(json_[key], True)
        else:
            temp = bytes(json_[key], "utf-8")
            temp = b64decode(temp)
            json_[key] = str(temp, "utf-8")

    return json_


def send_empty(sock):
    print(type(sock))
    sock.send(b" ")
