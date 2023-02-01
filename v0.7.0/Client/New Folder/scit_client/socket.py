# public module
import os
import socket
import json
import sys
import time
from time import sleep
from base64 import b64encode, b64decode
# own module
from . import cipher


encoding = "utf-8"
buffer_recv = 4096
balken_size = 10


class My_Socket:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.key = None
        self.ip = ""
        self.port = 5000

    def try_connect(self, ip, port):
        self.ip = ip
        self.port = port
        while True:
            try:
                t = self.socket.connect((ip, port))
                print(t)
            except ConnectionRefusedError:
                continue            # no Server found
            else:
                return self.socket  # Server found

    def read(self, crypt=True) -> dict:
        recv = self.socket.recv(buffer_recv)
        if crypt:
            recv = cipher.AES_decrypt_text(recv, self.key)
            recv = recv.decode("utf-8")
            recv = bytes2json(recv)

        sleep(0.1)
        return recv

    def read_file(self, filename, packet_count, key):
        if not os.path.exists(r"temp"):
            os.mkdir("temp")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_temp:
            ex = 0
            print("test")
            while not ex:
                time.sleep(0.1)
                print(ex)
                ex = sock_temp.connect_ex((self.ip, self.port + 1))  # Fileport is Textport + 1
            with open(rf"temp\recv-crypted-{filename}", "wb") as file:
                for i in range(packet_count):
                    print(f"{i}")
                    bytes_recv = sock_temp.recv(buffer_recv)
                    file.write(bytes_recv)
        #  decrypt file
        cipher.AES_decrypt_file(rf"file\\", filename, key)
        print("fertig")


    def send(self, msg: dict, crypt=True):
        if crypt:
            msg = json2bytes(msg)
            msg = cipher.AES_encrypt_text(msg, self.key)

        sleep(0.1)
        self.socket.send(msg)

    def send_file(self, path, packet_count):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_temp:

            while True:
                time.sleep(0.1)
                try:
                    sock_temp.connect((self.ip, 5002))
                except ConnectionRefusedError:
                    pass
                else:
                    break
            with open(path, "rb") as file:
                temp = 0
                time.sleep(2)
                for packet_counter in range(packet_count):
                    print(f"{packet_counter}")
                    file_bytes = file.read(buffer_recv)
                    sock_temp.send(file_bytes)

                    load_value = round((packet_counter / packet_count) * balken_size)
                    if load_value == temp:
                        continue
                    temp = load_value

                    if load_value <= balken_size:
                        #sys.stdout.write('\r' + f"8{r'=' * load_value}D")
                        sys.stdout.write('\r' + f"[{r'#'*load_value}{'-'*(load_value*-1+balken_size)}]")
                sys.stdout.write('\r                ')
        print("fertig")

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
