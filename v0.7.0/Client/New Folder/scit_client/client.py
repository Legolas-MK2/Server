import os
import sys
import threading
import types
import asyncio

from . import cipher
from . import login
from .socket import My_Socket
from .socket import buffer_recv


class Client:
    running = False

    def __init__(self, async_=False):
        self.__name: str = ""  # username

        self.dict_clients = {}  # dict with all other clients

        self.filepath = "files/"  # the downloaded files are stored under the path

        # bind() function
        self._on_message = self.empty
        self._on_close = self.empty
        self._on_connected = self.empty

        # make Socket
        self.__socket = My_Socket()
        if async_:
            asyncio.run(self._async_start_connection())
        else:
            self._start_connection()

    async def _async_start_connection(self):
        # connect to Server
        self.__socket.try_connect("192.168.178.75", 5000)   #  "5.230.75.187", 5000

        try:
            # set public-key private-key AES-key for Client Server communication
            self.pk, self.sk, self.__socket.key = login.get_server_keys(self.__socket)
        except ConnectionError:
            self.close()

        self.running = True
        self._on_connected()

    def _start_connection(self):
        # connect to Server
        self.__socket.try_connect("192.168.178.75", 5000)

        try:
            # set public-key private-key AES-key for Client Server communication
            self.pk, self.sk, self.__socket.key = login.get_server_keys(self.__socket)
        except ConnectionError:
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
                print(recv)
            except OSError:
                self.running = False
                break
            if recv.get("author") == "Server":
                self.__Server(recv["message"])
            else:
                self._on_message(recv)
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
            threading.Thread(target=self.__socket.read_file, args= (msg["file_name"], int(msg["packet_count"]), self.dict_clients[recv['author']])).start()
        except ConnectionError:
            os.remove(rf"temp\recv-crypted-{msg['file_name']}")
            self.close()



    def __text_msg(self, recv):
        #  decrypt message
        msg = int(recv["message"])
        msg = login.int_to_bytes(msg)
        msg = cipher.AES_decrypt_text(msg, self.dict_clients[recv['author']])
        msg = str(msg, "utf-8")
        recv["message"] = msg

        self.read(recv)

    def close(self):
        if self.running and self.__socket:
            self.__socket.close()
            self.dict_clients = {}
        self.running = False


