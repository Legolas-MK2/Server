# public module
import json
import socket
from time import sleep
from base64 import b64encode, b64decode
import atexit

# own module
from . import cipher

encoding = "utf-8"
buffer_recv = 4096


class DisconnectClientError(Exception):
    pass


class My_Socket:
    def __init__(self, sock: socket.socket, file_recv: socket.socket, file_send: socket.socket):
        self.socket = sock
        self.key = None
        self.recv_sock = file_recv
        self.send_sock = file_send

    def read(self, crypt=True):
        try:
            recv = self.socket.recv(buffer_recv)
        except ConnectionError:
            raise DisconnectClientError

        if recv == b"":
            raise DisconnectClientError

        if crypt:
            recv = cipher.AES_decrypt_text(recv, self.key)
            recv = recv.decode("utf-8")
            recv = bytes2json(recv)

        sleep(0.1)
        return recv

    def send(self, msg: dict, crypt=True, key=None):
        if crypt:
            msg = json2bytes(msg)
            msg = cipher.AES_encrypt_text(msg, self.key)

        sleep(0.1)
        self.socket.send(msg)

    def read_row(self):
        recv = self.socket.recv(buffer_recv)
        return recv

    def send_row(self, row):
        self.socket.send(row)

    def __del__(self):
        print("clooose")
        try:
            self.socket.close()
            self.recv_sock.close()
            self.send_sock.close()
        except AttributeError:
            print("erroooor")

    def file_stream(self, sock_receiver, packet_count, filename, sender_name):
        conn_recv = None
        conn_send = None
        try:
            print("warte auf sender")
            conn_recv, _ = self.recv_sock.accept()
            print("warte auf Empfänger")
            conn_send, _ = self.send_sock.accept()
            print("start sending file")
            while True:
                data = conn_recv.recv(buffer_recv)
                if not data:
                    break
                conn_send.sendall(data)
            print("end sending file")
        except ConnectionResetError:
            print("filesending abbruch")
            print(conn_recv)

        if not conn_recv:
            conn_recv.shutdown(socket.SHUT_RD)
            conn_recv.close()

        if not conn_send:
            conn_send.shutdown(socket.SHUT_WR)
            conn_send.close()


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
