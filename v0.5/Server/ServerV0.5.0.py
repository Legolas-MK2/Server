import pickle
import socket
import threading
from time import sleep
import Cipher


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


def start(ID,sock,addr):
    global ID_list

    def bytes_to_int(xbytes: bytes) -> int:
        return int.from_bytes(xbytes, "little")

    def Read(key):
        recv = Client.Socket.recv(4096)
        if key != None:
            recv = Cipher.AES_decrypt_text(recv, key)
        recv = pickle.loads(recv)
        sleep(0.1)
        return recv

    def Send(author, receiver, type, message, key):
        msg = {
            "author": author,
            "receiver": receiver,
            "type": type,
            "message": message,
            "timestamp": "sec.min.h.d.m.y",
            "token": ""
        }
        msg = pickle.dumps(msg)
        if key != None:
            msg = Cipher.AES_encrypt_text(msg, key)
        print(f"@:{receiver}, von:{author}, msg:{msg}:msg")
        Client.Socket.send(msg)
        sleep(0.1)

    def set_key():
        recv = Read(None)
        if recv["type"] != "login": json_wrong(); return
        if recv["message"]["mode"] != "key": json_wrong(); return

        Client.pk = recv["message"]["key"]
        Client.key = Cipher.generate_key(20)
        msg = Cipher.RSA_encrypt(Client.pk, Client.key)

        Send(author="Server",
             receiver=Client.Name,
             type="login",
             message={
                 "mode": "key",
                 "key": msg
             },
             key=None)

    def get_name():
        Name = ""
        while len(Name) < 1:
            recv = Read(Client.key)
            if recv["type"] != "login": json_wrong(); return
            if recv["message"]["mode"] != "name": json_wrong(); return
            Name = recv["message"]["name"]

            if Name[:6] == "Server" or " " in Name or Name == "":
                print("name error")
                Send(author="Server",
                     receiver=Client.Name,
                     type="login",
                     message="retry",
                     key=Client.key)
                continue

            if len(ID_list) == 0:
                Send(author="Server",
                     receiver=Client.Name,
                     type="login",
                     message={
                         "mode": "name",
                         "name": Name
                     },
                     key=Client.key)
                print(f"{bcolors.OKGREEN}Der Nutzer {Name} hat sich eingeloggt und hat die ID {ID} bekommen{bcolors.END}")
                return Name
            for s in ID_list:
                if ID_list[s].Name == Name:

                    Send(author="Server",
                         receiver=Name,
                         type="login",
                         message="retry",
                         key=Client.key)

                    Name = ""
                    continue

            Send(author="Server",
                 receiver=Name,
                 type="login",
                 message={
                     "mode": "name",
                     "name": Name
                 },
                 key=Client.key)

            print(f"{bcolors.OKGREEN}Der Nutzer {Name} hat sich eingeloggt und hat die ID {ID} bekommen{bcolors.END}")
            return Name

    def connect_to_all():
        for client in ID_list:
            if ID_list[client].Name != Client.Name:
                while True:
                    pk = bytes_to_int(ID_list[client].pk)
                    pk = str(pk)

                    Send(author="Server",
                         receiver=Client.Name,
                         type="keys",
                         message={
                             "name": ID_list[client].Name,
                             "pk": pk
                         },
                         key=Client.key)

                    recv = Read(Client.key)
                    if recv['type'] != "keys": json_wrong(); continue
                    name = recv['message']['name']
                    key = recv['message']['key']

                    if ID_list[client].Name == name:
                        ID_list[client].Send(author="Server",
                                            receiver=Client.Name,
                                            type="online",
                                            message={
                                                "command": "#O",
                                                "name": Client.Name,
                                                "mode": "+",
                                                "key": key
                                            },
                                            key=Client.key)

                    else:
                        print(f"{bcolors.WARNING}Warning: in connect_to_all")
                        print(f"ID_list[client].Name ='{ID_list[client].Name}'")
                        print(f"name ='{name}'{bcolors.END}")
                    break
        Send(author="Server",
             receiver=Client.Name,
             type="keys",
             message="end",
             key=Client.key)

    def sub_from_onlinelist(name):
        global ID_list

        if len(name) < 1:
            return

        for s in ID_list:
            try:
                ID_list[s].Send(author="Server",
                                     receiver=Client.Name,
                                     type="online",
                                     message={
                                         "command": "#O",
                                         "name": name,
                                         "mode": "-",
                                     },
                                     key=Client.key)
            except:
                pass

    Client = client()
    def main():
        try:
            Client.Socket = sock
            Client.ID = ID
            Client.addr = addr
            set_key()

            Client.Name = get_name()
            connect_to_all()
            ID_list[ID] = Client
            ID_list[ID].start()
        except:
            print(f"{bcolors.FAIL}die Verbindung zu dem Client {Client.Name if len(Client.Name) > 0 else ID} wurde verloren{bcolors.END}")
            temp.pop(ID)
            sub_from_onlinelist(Client.Name)
    main()


class client(threading.Thread):
    global ID_list
    global temp
    def __init__(self):
        threading.Thread.__init__(self)

        self.ID = None
        self.Socket = None
        self.addr = None
        self.Name = ""
        self.running = False
        self.key = None
        self.pk = None
        self.Kontakte = {} #[online] schreiben; [anstehent] anfrage annhemen

    def Read(self, key):
        recv = self.Socket.recv(4096)
        if key != None:
            recv = Cipher.AES_decrypt_text(recv, key)
        recv = pickle.loads(recv)
        sleep(0.1)
        return recv

    def Send(self, author, receiver, type, message, key):
        msg = {
            "author": author,
            "receiver": receiver,
            "type": type,
            "message": message,
            "timestamp": "sec.min.h.d.m.y",
            "token": ""
        }
        print(f"@:{receiver}, von:{author},key{key}, msg:{msg}:msg")
        msg = pickle.dumps(msg)
        if key != None:
            msg = Cipher.AES_encrypt_text(msg, key)
            print("crypt")
        else:
            print("no crypt")
        print(f"@:{receiver}, von:{author}, msg:{msg}:msg")

        self.Socket.send(msg)
        sleep(0.1)

    def run(self):
        try:
            self.running = True
            while self.running:
                recv = self.Read(self.key)
                self.data_Transfer(recv)
        except:
            print(f"{bcolors.FAIL}die Verbindung zu dem Client {self.Name if len(self.Name)> 0 else self.ID} wurde verloren{bcolors.END}")

            self.running = False
            self.sub_from_onlinelist(self.Name)
            ID_list.pop(self.ID)
            if temp[self.ID]:
                temp.pop(self.ID)

        print(f"Der Thread vom Client {self.Name if len(self.Name)> 0 else self.ID} hat sich geschlossen")

    def ask_Server(self, list_command):
        command = list_command["command"]
        if command == '#C':
            print(f"Der Client {self.Name} wird geschlossen")

            self.Send(author="Server",
                 receiver=self.Name,
                 type="metadata",
                 message={"command": "#C"},
                 key=self.key)

            self.running = False
            self.sub_from_onlinelist(self.Name)

            print(f"Der Client {self.Name} wurde geschlossen")
            ID_list.pop(self.ID)
            temp.pop(self.ID)

        elif command == "#O":
            pass
        else:
            print(f"{bcolors.WARNING}Der Client {self.Name} hat versucht an den Server die Nachicht '{command}' zusenden ohne das der Server eine Antwort hat{bcolors.END}")

    def data_Transfer(self, msg):
        if msg['receiver'] == "Server":
            self.ask_Server(msg['message'])
            return

        exist = False

        if len(msg) == 0:
            return

        for s in ID_list:
            if ID_list[s].Name == msg['receiver']:
                Empfänger_ID = s
                exist = True
                break

        if not exist:
            print(f"{bcolors.WARNING}Der Client {msg['receiver']} existiert nicht{bcolors.END}")
            return

        print(f"{self.Name} --> {msg['receiver']}")
        print("msg ->", msg)
        ID_list[Empfänger_ID].Send(author=self.Name,
                                receiver=msg['receiver'],
                                type="message",
                                message=msg["message"],
                                key=self.key)

    def sub_from_onlinelist(self, name):
        global ID_list

        if len(name) < 1:
            return

        for s in ID_list:
            try:
                ID_list[s].Send(author="Server",
                                receiver=name,
                                type="online",
                                message={
                                    "command": "#O",
                                    "name": name,
                                    "mode": "-",
                                },
                                key=self.key)
            except:
                pass

    def bytes_to_int(self, xbytes: bytes) -> int:
        return int.from_bytes(xbytes, "little")

    def int_to_bytes(self, x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, "little")

def json_wrong():
    pass

temp = {}
ID_list = {}
ip = "127.0.0.1"
port = 5000

if __name__ == '__main__':
    Nutzer_max = 10
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(Nutzer_max)

    for i in range(0, Nutzer_max):
        try:
            print("Warte auf neue Verbindung...")
            (sock, addr) = server_socket.accept()
            temp[i] = threading.Thread(target=start, args=(i, sock, addr))
            temp[i].start()
            print(bcolors.OKGREEN+ "Ein neuer Client hat sich verbunden"+ bcolors.END)
        except:
            print(bcolors.WARNING + "ein Problem mit dem aktzeptieren" + bcolors.END)

    print(bcolors.WARNING + "\n\n die maximale Anzahl an Clients haben sich verbunden" + bcolors.END)