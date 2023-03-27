import os
import sys
import threading
import types
import asyncio
from typing import Dict


from . import cipher
from . import login
from .socket import My_Socket
from .socket import buffer_recv
from .socket import DisconnectServerError


class ClientConnection:
    def __init__(self, _id: int, key: bytes, name: str = None):
        self.id = _id
        self.name = name
        self.key = key

    def send_text(self, msg):
        pass

    def send_file(self, filepath):
        pass


class Client:
    running = False

    def __init__(self, start_async=False):

        self.__name: str = ""  # username

        self.dict_clients: Dict[int, ClientConnection] = {}  # dict with all other clients
        self.list_groups = []
        self.config = {
            "filepath": "file/"  # the downloaded files are stored under the path
        }

        # bind() function
        self._on_message = self.empty
        self._on_close = self.empty
        self._on_connected = self.empty
        # make Socket
        self.__socket = My_Socket()
        if start_async:
            self._async_start_connection()
        else:
            self._start_connection()

    async def _async_start_connection(self):
        threading.Thread(target=self._start_connection).start()

    def _start_connection(self):
        # connect to Server
        #self.__socket.try_connect("5.230.75.187", 5000)
        self.__socket.try_connect("127.0.0.1", 5000)
        try:
            # set public-key private-key AES-key for Client Server communication
            self.pk, self.sk, self.__socket.key = login.get_server_keys(self.__socket)
        except DisconnectServerError:
            self.close()
        self.running = True
        self._on_connected()

    def empty(self, *args, **kwargs): pass

    def get_name(self):
        return self.__name

    def set_name(self, name: str):  # set name and returns None for an invalid name or if the name has already been set
        if not self.running:
            print("running")
            return

        if self.__name:
            print(self.__name)
            return

        try:
            self.__name, id_ = login.set_name(self.__socket, name)
        except DisconnectServerError:
            print("Server Disconnectet")
            self.close()
            return

        if self.__name:  # if the name is valid --> the AES keys are set for the other clients
            try:
                self.dict_clients[id_] = ClientConnection(id_, cipher.generate_key(20), self.__name)
                clients_keys = login.get_clients_keys(self.__socket)
                self.dict_clients.update(clients_keys)
            except DisconnectServerError:
                self.close()
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

        for client in self.dict_clients.values():
            if client.name == name or client.id == name:
                key = client.key
                id_ = client.id
                break
        else:
            print("Empfänger nicht in der liste gefunden")
            return

        msg = bytes(msg, "utf-8")
        msg = cipher.AES_encrypt_text(msg, key)
        msg = login.bytes_to_int(msg)

        self.__socket.send({
            "receiver": self.dict_clients[id_].id,
            "type": "text",
            "message": msg})

        return "OK"

    def read(self, recv: dict):
        pass

    def bind(self, on_message=None, on_close=None, on_connected=None):
        if on_message and isinstance(on_message, types.MethodType):
            self._on_message = on_message

        if on_close and isinstance(on_close, types.MethodType):
            self._on_close = on_close

        if on_connected and isinstance(on_connected, types.MethodType):
            self._on_connected = on_connected

    def __recv(self):   # this method runs in the extra thread and waits for a message
        while self.running:
            try:
                recv = self.__socket.read()
            except DisconnectServerError:
                self.running = False
                break

            if recv.get("author") == "0":
                self.__server(recv["message"])
            else:
                self._on_message(recv)
                if recv.get("type") == "file":
                    self.__file_msg(recv)
                elif recv.get("type") == "text":
                    self.__text_msg(recv)
                elif recv.get("type") == "file_group":
                    self.__file_msg_group(recv)
                elif recv.get("type") == "text_group":
                    self.__text_msg_group(recv)

    def __server(self, msg):
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
                con = ClientConnection(msg["id"], key, user_name)
                self.dict_clients[msg["id"]] = con
        elif msg["command"] == "#GA":
            self.list_groups.append(msg["name"])

    def send_file(self, receiver, file_path):
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            print(f"path '{file_path}' not found")
            return

        basename = os.path.basename(file_path)

        packet_count = round((os.path.getsize(file_path) / buffer_recv) + .5)
        send_packet_count = packet_count
        if float(packet_count) == float(os.path.getsize(file_path) / buffer_recv) + 1:
            send_packet_count -= 1

        for client in self.dict_clients.values():
            if client.name == receiver or client.id == receiver:
                key = client.key
                id_ = client.id
                break
        else:
            print("Empfänger nicht in der liste gefunden")
            return

        self.__socket.send({
            "receiver": id_,
            "type": "file",
            "message": {
                "receiver": id_,
                "file_name": basename,
                "packet_count": send_packet_count
            }})
        self.__socket.send_file(file_path, packet_count, self.dict_clients[id_].key)
        return "ok"

    def group_create(self, name):
        self.__socket.send({
            "receiver": 0,
            "message": {
                "command": "#G",
                "name": name
            }})

    def group_send(self, group, msg):
        self.__socket.send({
            "receiver": group,
            "type": "text_group",
            "message": msg})

    def group_add(self, group, client):
        self.__socket.send({
            "receiver": 0,
            "message": {
                "command": "#GA",
                "client": client,
                "group": group
            }})

    def __file_msg_group(self, recv):
        print("file group")
        return

    def __text_msg_group(self, recv: dict):
        #  decrypt message
        self.read(recv)

    def __file_msg(self, recv):
        msg = recv["message"]
        for client in self.dict_clients.values():
            if client.name == recv["author"] or client.id == recv["author"]:
                key = client.key
                id_ = client.id
                break
        else:
            print("Empfänger nicht in der liste gefunden")
            return

        t = threading.Thread(target=self.__socket.read_file, args=(self.config["filepath"]+msg["file_name"], int(msg["packet_count"]), self.dict_clients[id_].key))
        t.start()

    def __text_msg(self, recv: dict):
        #  decrypt message
        msg = int(recv["message"])
        msg = login.int_to_bytes(msg)
        print(f"{self.dict_clients = }")
        print(f"{recv = }")
        msg = cipher.AES_decrypt_text(msg, self.dict_clients[recv['author']].key)
        msg = str(msg, "utf-8")
        recv["message"] = msg

        self.read(recv)

    def close(self):
        if self.running and self.__socket:
            self.__socket.close()
            self.dict_clients = {}
        self.running = False
