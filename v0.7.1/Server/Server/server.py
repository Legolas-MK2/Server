# public
import json
import socket
import threading
from typing import List
from multiprocessing import Process
from typing import Dict

from . import login
from .socket import My_Socket
from .socket import DisconnectClientError


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Client_Handler(threading.Thread):
    def __init__(self, id_, sock: My_Socket):
        threading.Thread.__init__(self)
        self.id = id_
        self.sock = sock
        self.Name = ""
        self.running = False
        self.pk = b""
        self.filestreams = []
        self.channel = []
        self.list_groups: Dict[str, Group_Handler] = {}

    def run(self):

        self.pk = self.sock.read_row()
        if self.pk == b'':
            self.error()
            return
        #   set AES key
        self.sock.key = login.get_key(self.sock, self.pk)

        #   set Name
        self.Name = login.get_name(self.sock, list_client)
        if self.Name == "":
            self.error()
            return

        with open("config.json") as f:
            server_config = json.load(f)

        if not server_config.get("names"):
            server_config["names"] = []

        if self.Name in server_config["names"]:
            print("erneutes anmelden")
        else:
            server_config["names"].append(self.Name)
            with open("config.json", "w") as f:
                json.dump(server_config, f)

        print(f"{bcolors.OKGREEN}Der Nutzer {self.Name} hat sich eingeloggt "
              f"und hat die ID {self.id} bekommen{bcolors.END}")
        list_client[self.Name] = list_client.pop(str(self.id) + " ")

        try:
            #   send all other clients keys
            login.connect_to_all(self.sock, list_client, self.Name)

            #   client-main-loop
            self.running = True
            while self.running:
                data = self.sock.read()
                #   if the message is addressed to the server
                if data["receiver"] == "Server":
                    self.__client2server(data["message"])
                    continue

                #   Message forwarding
                self.__forwarding(data)
        except DisconnectClientError:
            self.error()

        for stream in self.filestreams:
            stream.terminate()
            stream.join()

        print(f"Der Thread vom Client {self.Name if len(self.Name)> 0 else self.id} hat sich geschlossen")

    def error(self):
        self.running = False
        try:
            self.__sub_from_onlinelist(self.Name)
        except ConnectionError:
            pass

        if self.Name == "":  # hat der Client schon ein Name
            print(f"{bcolors.FAIL}Die Verbindung vom Client mit der ID {self.id} ist abgestürzt {bcolors.END}")
            print(list_client)
            list_client.pop(f"{self.id} ")
        else:
            print(f"{bcolors.FAIL}Die Verbindung vom Client mit dem Namen {self.Name} ist abgestürzt {bcolors.END}")
            list_client.pop(self.Name)

    def on_finnish_filestream(self):
        pass

    def __client2server(self, data: dict):
        if data["command"] == '#C':
            print(f"Der Client {self.Name} wird geschlossen")

            self.running = False
            self.__sub_from_onlinelist(self.Name)
            self.sock.send({
                "author": "Server",
                "message": {
                    "command": "#C"
                }})

            print(f"Der Client {self.Name} wurde geschlossen")
            list_client.pop(self.Name)
        elif data["command"] == "#O":
            pass
        elif data["command"] == "#G":
            if not data.get("name"):
                print("Group konnte nicht erstellt werden")
                return

            print("Erstelle Group")
            group = Group_Handler(data["name"], self)
            self.list_groups[data["name"]] = group
        elif data["command"] == "#GA":
            if data.get("group") not in self.list_groups:
                print(f"die gruppe {data.get('group')} wurde nicht gefunden")
                return
            if data.get("client") not in list_client:
                print(f"der client {data.get('client')} wurde nicht gefunden")
                return

            print(f"der client {data.get('client')} wird zu der gruppe {data.get('group')} hinzugefügt")
            self.list_groups[data["group"]].add_client(list_client[data["client"]])
        elif self.on_server_message(data):
            pass
        else:
            print(f"{bcolors.WARNING}Der Client {self.Name} hat versucht an den Server "
                  f"die Nachricht '{data}' zusenden ohne das der Server eine Antwort hat{bcolors.END}")

    def on_server_message(self, data):
        pass

    def __forwarding(self, data):
        if data.get("type") == "text":
            if data["receiver"] not in list_client:
                print(f"{bcolors.WARNING}Der Client {data['receiver']} wurde nicht gefunden{bcolors.END}")
                return

            self.on_text_message(data)
        elif data.get("type") == "file":
            if data["receiver"] not in list_client:
                print(f"{bcolors.WARNING}Der Client {data['receiver']} wurde nicht gefunden{bcolors.END}")
                return

            self.on_file_message(data)
        elif data.get("type") == "text_group":
            if data["receiver"] not in self.list_groups:
                print(f"die group {data['receiver']} wurde nicht gefunden")
                return
            self.list_groups[data["receiver"]].send_text(self.Name, data["message"])
        else:
            print("ungültiger type angegeben")

    def on_file_message(self, data):
        self.send_file(data)

    def on_text_message(self, data):
        self.send(data)

    def send(self, data):
        name_receiver = data["receiver"]
        receiver = list_client.get(name_receiver)

        print(f"{self.Name} --> {name_receiver}")
        print("msg ->", data["message"])

        receiver.sock.send(
            {
                "author": self.Name,
                "receiver": name_receiver,
                "type": "text",
                "message": data["message"]}
        )

    def send_file(self, data):
        receiver = data["receiver"]
        msg = data["message"]
        packet_count = msg["packet_count"]

        if receiver not in list_client:
            return

        list_client[receiver].sock.send({
            "author": self.Name,
            "type": "file",
            "message": {
                "file_name": msg['file_name'],
                "packet_count": packet_count

            }
        })

        print(f"{self.Name} --> {receiver}")
        print("msg = file")
        print(f"filename = {msg['file_name']}")

        stream = Process(
            target=self.sock.file_stream,
            args=[list_client[receiver].sock,
                  int(packet_count),
                  msg['file_name'],
                  self.Name])
        stream.start()

        self.filestreams.append(stream)

    def on_close(self):
        pass

    def __del__(self):
        self.error()

    @staticmethod
    def __sub_from_onlinelist(name):

        if len(name) < 1:
            return

        for s in list_client:
            if not list_client[s].running:
                continue
            j = {"author": "Server",
                 "receiver": list_client[s].Name,
                 "message": {"command": "#O",
                             "mode": "-",
                             "name": name}}
            list_client[s].sock.send(j)

    @staticmethod
    def bytes_to_int(xbytes: bytes) -> int:
        return int.from_bytes(xbytes, "little")

    @staticmethod
    def int_to_bytes(x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, "little")

    def force_close(self):
        self.running = False
        try:
            self.__sub_from_onlinelist(self.Name)
            self.sock.send({
                "author": "Server",
                "message": {
                    "command": "#C"
                }})
        except Exception as e:
            print(e)
        print(f"Der Client {self.Name} wurde geschlossen")
        list_client.pop(self.Name)


class Group_Handler:
    def __init__(self, name: str, admin: Client_Handler, size=None):
        # static count of max members
        self.__size = size

        self.name = name

        # dict of all members
        self.__list_members: List[Client_Handler] = [admin]

    def get_size(self):
        return self.__size

    def add_client(self, client: Client_Handler):
        if not self.__size or len(self.__list_members) <= self.__size:
            self.on_add(client)
        else:
            print(f"{client.Name} konnte nicht gespeichert werden")

    def on_add(self, client: Client_Handler):
        self.add(client)

    def add(self, client: Client_Handler):
        self.__list_members.append(client)
        client.sock.send({
            "author": "Server",
            "message": {
                "command": "#GA",
                "name": self.name,
                "clients": self.__list_members
            }})
        client.list_groups[self.name] = self

    def send_text(self, author, message):
        print(f"msg = {message}")
        print(self.__list_members)
        for member in self.__list_members:
            member.sock.send({
                    "author": author,
                    "group": self.name,
                    "type": "text_group",
                    "message": message
                })


# Global Variable
list_client: Dict[str, Client_Handler] = {}
file_request = {}


class Server_Handler:
    def __init__(self):
        self.server_config = {}
        try:
            with open("config.json") as f:
                self.server_config = json.load(f)
        except FileNotFoundError:
            self.server_config = {'current_id': 0, 'ip': '0.0.0.0', 'port': 5000, 'names': ['a']}
        print(self.server_config)
        self.ip = self.server_config["ip"]
        self.port = self.server_config["port"]
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.ip, self.port))
            self.server_socket.listen()

            self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.send_sock.bind((self.ip, self.port + 1))
            self.send_sock.listen(1)

            self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.recv_sock.bind((self.ip, self.port + 2))
            self.recv_sock.listen(1)

        except OSError:
            print("port ist belegt")
            exit()
        self.current_id = self.server_config["current_id"]

    def connect_client(self, class_client=Client_Handler):
        print("Warte auf neue Verbindung...")
        try:
            (socket_, addr) = self.server_socket.accept()
        except KeyboardInterrupt:
            exit()
        sock = My_Socket(socket_, self.recv_sock, self.send_sock)
        list_client[str(self.current_id) + " "] = class_client(self.current_id, sock)
        list_client[str(self.current_id) + " "].start()
        print(bcolors.OKGREEN + "Ein neuer Client hat sich verbunden" + bcolors.END)
        self.current_id += 1
        self.server_config["current_id"] = self.current_id
        with open("config.json", "w") as f:
            json.dump(self.server_config, f)

    def __del__(self):
        global list_client

        del list_client
        try:
            if not self.server_socket:
                self.server_socket.shutdown(socket.SHUT_RD)
                self.server_socket.close()
        except AttributeError:
            pass

        try:
            if not self.recv_sock:
                self.recv_sock.shutdown(socket.SHUT_RD)
                self.recv_sock.close()
        except AttributeError:
            pass

        try:
            if not self.send_sock:
                self.send_sock.shutdown(socket.SHUT_WR)
                self.send_sock.close()
        except AttributeError:
            pass
