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


class DisconnectServerError(Exception):
    pass

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
            except ConnectionRefusedError:
                continue            # no Server found
            else:
                return self.socket  # Server found

    def read(self, crypt=True) -> dict:
        try:
            recv = self.socket.recv(buffer_recv)
        except ConnectionError:
            raise DisconnectServerError("Der Server wurde unerwatet Beendert")
        if recv == b'':
            raise DisconnectServerError("Der Server wurde unerwatet Beendert")
        if crypt:
            recv = cipher.AES_decrypt_text(recv, self.key)
            recv = recv.decode("utf-8")
            recv = bytes2json(recv)

        sleep(0.1)
        return recv

    def read_file(self, outfile, packet_count, key):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_temp:
            ex = 1
            while ex:
                time.sleep(0.1)

                ex = sock_temp.connect_ex((self.ip, self.port + 1))
            # recv data
            encrypted_data = b''
            chunk = sock_temp.recv(buffer_recv)
            while chunk:
                encrypted_data += chunk
                chunk = sock_temp.recv(buffer_recv)
        print(1)
        #  decrypt data
        cipher.AES_decrypt_file(encrypted_data, key, outfile=outfile)   #, outfile=f"file/{filename}"
        print(2)
        print(outfile)

    def send(self, msg: dict, crypt=True):
        if crypt:
            msg = json2bytes(msg)
            msg = cipher.AES_encrypt_text(msg, self.key)

        sleep(0.1)
        self.socket.send(msg)

    def send_file(self, path, packet_count, recver_key):
        ciphertext = cipher.AES_encrypt_file(path, recver_key)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_temp:

            while True:
                time.sleep(0.1)
                try:
                    sock_temp.connect((self.ip, self.port + 2))

                except ConnectionRefusedError:
                    pass
                else:
                    break

            sock_temp.sendall(ciphertext)

    def close(self):
        try:
            self.send({"receiver": "Server",
                       "message": {
                           "command": "#C"
                       }})
        except:
            pass

        self.socket.close()


def json2bytes(json_, recursive=False):
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
