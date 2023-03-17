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
    def __init__(self, sock: socket.socket, ip: str, port: int):
        self.socket = sock
        self.key = None
        self.ip = ip
        self.port = port

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

    def read_row(self):
        recv = self.socket.recv(buffer_recv)
        return recv

    def send_row(self, row):
        self.socket.send(row)

    def file_stream(self, sock_receiver, packet_count, filename, sender_name):                             #
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as recv_sock_temp:   # build a extra socket
            recv_sock_temp.bind((self.ip, self.port + 1))                           # for the receiving Client
            recv_sock_temp.listen(1)                                                #
            recv_sock, _ = recv_sock_temp.accept()                                          #

            sock_receiver.send({
                "author": sender_name,
                "type": "file",
                "message": {
                    "file_name": filename,
                    "packet_count": packet_count

                }
            })
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as send_sock_temp:   #
                send_sock_temp.bind((self.ip, self.port + 2))                           # build a extra socket
                send_sock_temp.listen(1)                                                # for the sending Client
                send_sock, _ = send_sock_temp.accept()                                  #

                with send_sock:
                    for _ in range(packet_count):              #
                        recv = recv_sock.recv(buffer_recv)     # send file
                        send_sock.send(recv)                   #
                    print("\n\n\n")
                    print("stream ende")


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
