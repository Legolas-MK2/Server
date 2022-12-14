# > TODO ID system löschen
# > TODO def start löscchen
# X TODO multi dateien

import socket
import threading
from time import sleep

import Login
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


class client(threading.Thread):
    global list_client
    global temp

    def __init__(self, ID, Socket):
        threading.Thread.__init__(self)

        self.ID = ID
        self.Socket = Socket
        self.addr = None
        self.Name = ""
        self.running = False
        self.key = None
        self.pk = None

    def Read(self, crypt=True):

        recv = self.Socket.recv(4096)
        if crypt:
            recv = Cipher.AES_decrypt_text(recv, self.key)
            recv = str(recv, "utf-8")

        sleep(0.1)
        return recv

    def Send_von(self, Sender, msg):
        self.Send(Sender)
        self.Send(msg, False)

    def Send(self, msg, crypt=True):
        sleep(0.1)
        if crypt:
            msg = bytes(msg, "utf-8")
            msg = Cipher.AES_encrypt_text(msg, self.key)

        self.Socket.send(msg)

    def run(self):
        try:
            self.addr = addr
            self.set_key()

            self.Name = self.get_name()
            list_client[self.Name] = list_client.pop(str(self.ID) + " ")
            self.connect_to_all()

            self.running = True
            while self.running:
                recv = self.Read()
                self.data_Transfer(recv)
        except:
            print(f"{bcolors.FAIL}die Verbindung zu dem Client {self.Name if len(self.Name)> 0 else self.ID} wurde verloren{bcolors.END}")

            self.running = False
            self.sub_from_onlinelist(self.Name)
            list_client.pop(self.Name)

        print(f"Der Thread vom Client {self.Name if len(self.Name)> 0 else self.ID} hat sich geschlossen")

    def set_key(self):
        self.pk = self.Read(False)
        self.key = Cipher.generate_key(20)
        msg = Cipher.RSA_encrypt(self.pk, self.key)
        self.Send(msg, False)

    def get_name(self):
        Name = ""
        while len(Name) < 1:
            Name = self.Read()
            print(f"Name = {Name}")
            if Name[:6] == "Server" or " " in Name or Name == "":
                print("name error")
                self.Send("e")
                continue
            elif len(list_client) == 0:
                self.Send(" ")
                print(f"{bcolors.OKGREEN}Der Nutzer {self.Name} hat sich eingeloggt und hat die ID {self.ID} bekommen{bcolors.END}")
                return Name
            continue_ = False
            for s in list_client:
                if list_client[s].Name == Name:
                    self.Send("e")
                    continue_ = True
            if continue_:
                Name = ""
                continue
            self.Send(" ")
            print(f"{bcolors.OKGREEN}Der Nutzer {self.Name} hat sich eingeloggt und hat die ID {self.ID} bekommen{bcolors.END}")
            return Name

    def connect_to_all(self):
        for c in list_client:
            if list_client[c].Name != self.Name \
                    and c[-1] != " ":
                pk = self.bytes_to_int(list_client[c].pk)
                pk = str(pk)

                self.Send(list_client[c].Name + " " + pk)
                recv = self.Read().split(" ")
                if list_client[c].Name == recv[0]:
                    list_client[c].Send("Server")
                    list_client[c].Send("#O + " + self.Name + " " + recv[1])
                else:
                    print(f"{bcolors.WARNING}Warning: in connect_to_all")
                    print(f"client_list[c].Name ='{list_client[c].Name}'")
                    print(f"recv[0] ='{recv[0]}'{bcolors.END}")
        self.Send("e")

    def ask_Server(self, parameter):
        if parameter == '#C':
            print(f"Der Client {self.Name} wird geschlossen")

            self.Send("Server")
            self.Send("#C")

            self.running = False
            self.sub_from_onlinelist(self.Name)

            print(f"Der Client {self.Name} wurde geschlossen")
            list_client.pop(self.Name)

        elif parameter == "#O":
            pass
        else:
            print(f"{bcolors.WARNING}Der Client {self.Name} hat versucht an den Server die Nachicht '{parameter}' zusenden ohne das der Server eine Antwort hat{bcolors.END}")

    def data_Transfer(self, Empfänger_Name):
        if Empfänger_Name == "Server":
            msg = self.Read()
            self.ask_Server(msg)
            return

        msg = self.Read(False)

        if len(msg) == 0:
            print(f"{bcolors.WARNING}die Nachricht hat kein inhalt{bcolors.END}")
            return

        if Empfänger_Name not in list_client.keys():
            print(f"{bcolors.WARNING}Der Client {Empfänger_Name} existiert nicht{bcolors.END}");
            return

        print(f"{self.Name} --> {Empfänger_Name}")
        print("msg ->", msg)
        list_client[Empfänger_Name].Send_von(self.Name, msg)

    def add_to_onlinelist(self, name):
        global list_client

        if len(name) < 1:
            return

        for s in client_list:
            if not client_list[s].running:
                continue
            try:
                key = str(self.bytes_to_int(self.pk))
                client_list[s].Send("Server")
                client_list[s].Send("#O + " + name + " " + key)
            except:
                pass

    def sub_from_onlinelist(self, name):
        global list_client

        if len(name) < 1:
            return

        for s in client_list:
            if not client_list[s].running:
                continue
            try:
                client_list[s].Send("Server")
                client_list[s].Send("#O - " + name)
            except:
                pass

    def bytes_to_int(self, xbytes: bytes) -> int:
        return int.from_bytes(xbytes, "little")

    def int_to_bytes(self, x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, "little")

temp = {}
list_client = {}

if __name__ == '__main__':
    Nutzer_max = 10
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5000))
    server_socket.listen(Nutzer_max)

    for i in range(0, Nutzer_max):
        try:
            print("Warte auf neue Verbindung...")
            (sock, addr) = server_socket.accept()
            list_client[str(i) + " "] = client(i, sock)
            list_client[str(i) + " "].start()
            print(bcolors.OKGREEN + "Ein neuer Client hat sich verbunden" + bcolors.END)
        except:
            print(bcolors.WARNING + "ein Problem mit dem aktzeptieren" + bcolors.END)

    print(bcolors.WARNING + "\n\n die maximale Anzahl an Clients haben sich verbunden" + bcolors.END)
