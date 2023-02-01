# public
import json
import socket
import threading
import time

import Login
import Socket


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
    global list_client

    def __init__(self, id_, sock: Socket.My_Socket, pk):
        threading.Thread.__init__(self)
        self.id = id_
        self.sock = sock
        self.Name = ""
        self.running = False
        self.pk = pk
        self.filestream = {}
        self.channel = []

    def run(self):
        try:
            #   set AES key
            self.sock.key = Login.get_key(self.sock, self.pk)

            #   set Name
            self.Name = Login.get_name(self.sock, list_client)
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

            #   send all other clients keys
            Login.connect_to_all(self.sock, list_client, self.Name)

            #   client-main-loop
            self.running = True
            while self.running:
                recv = self.sock.read()
                #   if the message is addressed to the server
                if recv["receiver"] == "Server":
                    self.client2server(recv["message"])
                    continue

                #   Message forwarding
                self.forwarding(recv)

        except ConnectionError:
            self.error()
        except ValueError:
            self.error()

        print(f"Der Thread vom Client {self.Name if len(self.Name)> 0 else self.id} hat sich geschlossen")

    def error(self):
        self.running = False

        try:
            self.sub_from_onlinelist(self.Name)
        except ConnectionError:
            pass

        if self.Name == "":  # hat der Client schon ein Name
            print(f"{bcolors.FAIL}Die Verbindung vom Client mit der ID {self.id} ist abgestürzt {bcolors.END}")
            list_client.pop(f"{self.id} ")
        else:
            print(f"{bcolors.FAIL}Die Verbindung vom Client mit dem Namen {self.Name} ist abgestürzt {bcolors.END}")
            list_client.pop(self.Name)

    def client2server(self, parameter):
        if parameter["command"] == '#C':
            print(f"Der Client {self.Name} wird geschlossen")

            self.running = False
            self.sub_from_onlinelist(self.Name)
            self.sock.send({
                "author": "Server",
                "message": {
                    "command": "#C"
                }})

            print(f"Der Client {self.Name} wurde geschlossen")
            list_client.pop(self.Name)

        elif parameter == "#O":
            pass
        else:
            print(f"{bcolors.WARNING}Der Client {self.Name} hat versucht an den Server "
                  f"die Nachricht '{parameter}' zusenden ohne das der Server eine Antwort hat{bcolors.END}")

    def forwarding(self, msg):
        if msg["receiver"] not in list_client:
            print(f"{bcolors.WARNING}Der Client {msg['receiver']} wurde nicht gefunden{bcolors.END}")
            return

        if msg.get("type") == "text":
            self.text_msg(msg)
        elif msg.get("type") == "file":
            self.file_msg(msg)
        elif msg.get("type") == "save text":
            self.save_text_msg(msg)
        elif msg.get("type") == "save file":
            self.save_file_msg(msg)
        else:
            print("ungültiger type angegeben")

    def save_text_msg(self, msg):
        print("save text")

    def save_file_msg(self, msg):
        print("save file")

    def file_msg(self, msg):
        receiver = msg["receiver"]
        msg = msg["message"]
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

        threading.Thread(target=self.sock.file_stream,
                         args=[list_client[receiver].sock, int(packet_count), msg['file_name'], self.Name]).start()
        #while True:
        #    for thread in threading.enumerate():
        #        print(thread.name)
        #    time.sleep(1)


    def text_msg(self, msg):
        name_receiver = msg["receiver"]
        receiver = list_client.get(name_receiver)

        print(f"{self.Name} --> {name_receiver}")
        print("msg ->", msg["message"])

        receiver.sock.send(
            {
                "author": self.Name,
                "receiver": name_receiver,
                "type": "text",
                "message": msg["message"]}
        )

    @staticmethod
    def sub_from_onlinelist(name):
        global list_client

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
            self.sub_from_onlinelist(self.Name)
            self.sock.send({
                "author": "Server",
                "message": {
                    "command": "#C"
                }})
        except Exception as e:
            print(e)
        print(f"Der Client {self.Name} wurde geschlossen")
        list_client.pop(self.Name)


class Channel:
    def __init__(self, max_handler):
        self.max_handler = max_handler
        self.list_handler = []
        self.chat = []

    def add_handler(self, handler: Client_Handler):
        if len(self.list_handler) >= self.max_handler:
            return "max handler"

        self.list_handler.append(handler)


def main():
    ip = server_config["ip"]
    port = server_config["port"]

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen()

    current_id = server_config["current_id"]
    while True:
        print("Warte auf neue Verbindung...")
        (socket_, addr) = server_socket.accept()
        sock = Socket.My_Socket(socket_, ip, port)
        recv = sock.read_row()
        list_client[str(current_id) + " "] = Client_Handler(current_id, sock, recv)
        list_client[str(current_id) + " "].start()
        print(bcolors.OKGREEN + "Ein neuer Client hat sich verbunden" + bcolors.END)
        current_id += 1
        server_config["current_id"] = current_id
        with open("config.json", "w") as f:
            json.dump(server_config, f)


list_client = {}
server_config = {}

if __name__ == '__main__':
    h_name = socket.gethostname()
    IP_addres = socket.gethostbyname(h_name)
    print("Host Name is:" + h_name)
    print("Computer IP Address is:" + IP_addres)
    with open("config.json") as f:
        server_config = json.load(f)
    print(server_config)
    main()
