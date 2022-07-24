# public module
import json
import socket
from time import sleep
from base64 import b64encode, b64decode

# own module
import Cipher


encoding = "utf-8"
buffer_recv = 4096


class My_Socket:
    def __init__(self, sock: socket.socket):
        self.socket = sock
        self.key = None

    def read(self, crypt=True):
        recv = self.socket.recv(buffer_recv)
        if crypt:
            recv = Cipher.AES_decrypt_text(recv, self.key)
            recv = recv.decode("utf-8")
            recv = bytes2json(recv)


        sleep(0.1)
        return recv

    def send(self, msg: dict, crypt=True):
        if crypt:
            msg = json2bytes(msg)
            msg = Cipher.AES_encrypt_text(msg, self.key)

        sleep(0.1)
        self.socket.send(msg)


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