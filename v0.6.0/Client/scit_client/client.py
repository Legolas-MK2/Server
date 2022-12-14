import os
import sys
import threading

from . import cipher
from . import login
from .socket import My_Socket
from .socket import buffer_recv


class Client:
    running = False

    def __init__(self):
        self.__name = ""  # username

        self.dict_clients = {}  # dict with all other clients

        self.filepath = "files/"  # the downloaded files are stored under the path

        # make Socket
        self.__socket = My_Socket()

        # connect to Server
        self.__socket.try_connect("127.0.0.1", 5000)

        try:
            # set public-key private-key AES-key for Client Server communication
            self.pk, self.sk, self.__socket.key = login.get_server_keys(self.__socket)
            self.running = True
        except ConnectionError:
            pass

    def get_name(self):
        return self.__name

    def set_name(self, name: str):  # set name and returns None for an invalid name or if the name has already been set
        if not self.running:
            print("running")
            return

        if self.__name:
            print("name (set_name)")
            print(self.__name)
            return

        self.__name = login.set_name(self.__socket, name)

        if self.__name:  # if the name is valid the AES keys are set for the other clients
            self.dict_clients = login.get_clients_keys(self.__socket, self.__name)
            threading.Thread(target=self.__recv).start()

        return self.__name

    def send(self, name: str, msg: str):
        if not self.running:
            print("send ohne running")
            return
        if not self.__name:
            print("name (send)")
            print(self.__name)
            return

        if not self.dict_clients.get(name):
            print("Empfänger nicht in der liste gefunden")
            return

        msg = bytes(msg, "utf-8")
        msg = cipher.AES_encrypt_text(msg, self.dict_clients[name])
        msg = login.bytes_to_int(msg)

        self.__socket.send({
            "author": self.__name,
            "receiver": name,
            "type": "text",
            "message": msg})
        return "OK"

    def read(self, recv: dict):
        pass

    def __recv(self):   # this method runs in the extra thread and waits for a message
        while self.running:
            try:
                recv = self.__socket.read()
            except OSError:
                self.running = False
                break
            if recv.get("author") == "Server":
                self.__Server(recv["message"])
            else:
                if recv.get("type") == "file":
                    self.__file_msg(recv)
                elif recv.get("type") == "text":
                    self.__text_msg(recv)

    def __Server(self, msg):
        if msg["command"] == "#C" and not self.running:
            self.__socket.close()
            sys.exit()

        elif msg["command"] == "#O":
            global sk
            mode = msg["mode"]
            user_name = msg["name"]

            if mode == "-":
                for user in self.dict_clients.items():
                    if user[0] == user_name:
                        self.dict_clients.pop(user_name)
                        return

            elif mode == "+":
                key = msg["key"]
                key = login.int_to_bytes(int(key))
                key = cipher.RSA_decrypt(self.sk, key)
                self.dict_clients[user_name] = key

    def send_file(self, receiver, file_path):
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return

        basename = os.path.basename(file_path)
        cipher.AES_encrypt_file(file_path, self.dict_clients[receiver])
        file_path = "temp/send-crypted-" + basename

        packet_count = round((os.path.getsize(file_path) / buffer_recv) + .5)
        send_packet_count = packet_count

        if float(packet_count) == float(os.path.getsize(file_path) / buffer_recv) + 1:
            send_packet_count -= 1

        self.__socket.send({
            "author": self.__name,
            "receiver": receiver,
            "type": "file",
            "message": {
                "receiver": receiver,
                "file_name": basename,
                "packet_count": send_packet_count
            }})

        self.__socket.send_file(file_path, packet_count)
        #os.remove(file_path)
        return "ok"

    def __file_msg(self, recv):
        msg = recv["message"]

        #   get file
        try:
            self.__socket.read_file(msg["file_name"], int(msg["packet_count"]))
        except ConnectionError:
            os.remove(rf"temp\recv-crypted-{msg['file_name']}")
            self.close()
        #  decrypt file
        cipher.AES_decrypt_file(self.filepath, msg["file_name"], self.dict_clients[recv['author']])

    def __text_msg(self, recv):
        #  decrypt message
        msg = int(recv["message"])
        msg = login.int_to_bytes(msg)
        msg = cipher.AES_decrypt_text(msg, self.dict_clients[recv['author']])
        msg = str(msg, "utf-8")
        recv["message"] = msg

        #  execute read-methode
        self.read(recv)

    def close(self):
        if self.running and self.__socket:
            self.__socket.close()
            self.dict_clients = {}
        self.running = False
