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

        ex = 111
        while ex == 111:
            time.sleep(0.1)
            ex = self.socket.connect_ex((self.ip, self.port))

    def read(self, crypt=True) -> dict:
        try:
            recv = self.socket.recv(buffer_recv)
        except ConnectionError:
            raise DisconnectServerError("Der Server wurde unerwatet Beendert")

        # Empty bytestring = server connection broken.
        if recv == b'':
            raise DisconnectServerError("Der Server wurde unerwatet Beendert")
        if crypt:
            recv = cipher.aes_decrypt_text(recv, self.key)
            recv = recv.decode("utf-8")
            recv = bytes2json(recv)

        # Prevents server overload and network issues with delay between packets.
        sleep(0.2)
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

        #  decrypt data
        cipher.aes_decrypt_file(encrypted_data, key, outfile=outfile)   #, outfile=f"file/{filename}"

    def send_row(self, packet: bytes):
        sleep(0.2)

        try:
            self.socket.send(packet)
        except ConnectionError:
            raise DisconnectServerError("Der Server wurde unerwatet Beendert")

    def send(self, receiver: int, message, _type: str, *, group=None):
        packet = {
            "receiver": receiver,
            "type": _type,
            "message": message
        }
        if group:
            packet["group"] = group

        packet = json2bytes(packet)
        packet = cipher.aes_encrypt_text(packet, self.key)

        # Prevents server overload and network issues with delay between packets.
        sleep(0.2)

        try:
            self.socket.send(packet)
        except ConnectionError:
            raise DisconnectServerError("Der Server wurde unerwatet Beendert")
        except OSError:
            raise DisconnectServerError("Der Server wurde unerwatet Beendert")

    def send_file(self, path, packet_count, recver_key):
        ciphertext = cipher.aes_encrypt_file(path, recver_key)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_temp:
            ex = 1
            while ex:
                time.sleep(0.1)

                ex = sock_temp.connect_ex((self.ip, self.port + 2))

            sock_temp.sendall(ciphertext)

    def close(self):
        try:
            self.send(0, {"command": "#C"}, "Server")
        except DisconnectServerError:
            pass

        self.socket.close()


def build_message(receiver: int, message, _type: str, *, group=None):
    packet = {
        "receiver": receiver,
        "type": _type,
        "message": message
    }
    if group:
        packet["group"] = group

    return packet


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
