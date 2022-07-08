# > TODO ID system löschen
# > TODO def start löscchen
# X TODO multi dateien

import socket
import threading
from time import sleep

import Login
import Cipher
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


class client(threading.Thread):
    global client_list
    global temp

    def __init__(self, ID, socket_):
        threading.Thread.__init__(self)

        self.ID = ID
        #self.Socket = Socket
        self.sock = Socket.My_Socket(socket_)
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
            self.set_key()
            self.Name = self.get_name()
            client_list[self.Name] = client_list.pop(str(self.ID)+" ")
            self.connect_to_all()

            self.running = True
            while self.running:
                recv = self.sock.read()
                self.data_Transfer(recv)
        except ConnectionResetError:
            print(f"{bcolors.FAIL}Der Client mit {(f'dem Namen{self.Name}') if len(self.Name)> 0 else (f'{self.ID}')}{bcolors.END}")

            self.running = False
            self.sub_from_onlinelist(self.Name)
            client_list.pop(self.Name) #TODO if self.Name not found

        print(f"Der Thread vom Client {self.Name if len(self.Name)> 0 else self.ID} hat sich geschlossen")

    def set_key(self):
        self.pk = self.sock.read(False)
        self.sock.key = Cipher.generate_key(20)
        msg = Cipher.RSA_encrypt(self.pk, self.sock.key)
        self.sock.send(msg, False)

    def get_name(self):
        Name = ""
        while len(Name) < 1:
            Name = self.sock.read()
            print(f"Name = {Name}")
            if Name[:6] == "Server" or " " in Name or Name == "":
                print("name error")
                self.sock.send("e")
                continue
            elif len(client_list) == 0:
                self.sock.send(" ")
                print(f"{bcolors.OKGREEN}Der Nutzer {Name} hat sich eingeloggt und hat die ID {self.ID} bekommen{bcolors.END}")
                return Name
            continue_ = False
            for s in client_list:
                if client_list[s].Name == Name:
                    self.sock.send("e")
                    continue_ = True
            if continue_:
                Name = ""
                continue
            self.sock.send(" ")
            print(f"{bcolors.OKGREEN}Der Nutzer {Name} hat sich eingeloggt und hat die ID {self.ID} bekommen{bcolors.END}")
            return Name

    def connect_to_all(self):
        for c in client_list:
            if client_list[c].Name != self.Name and c[-1] != " ":
                pk = self.bytes_to_int(client_list[c].pk)
                pk = str(pk)

                self.sock.send(client_list[c].Name + " " + pk)
                recv = self.sock.read().split(" ")
                if client_list[c].Name == recv[0]:
                    client_list[c].sock.send("Server")
                    client_list[c].sock.send("#O + " + self.Name + " " + recv[1])
                else:
                    print(f"{bcolors.WARNING}Warning: in connect_to_all")
                    print(f"client_list[c].Name ='{client_list[c].Name}'")
                    print(f"recv[0] ='{recv[0]}'{bcolors.END}")
        self.sock.send("e")

    def ask_Server(self, parameter):
        if parameter == '#C':
            print(f"Der Client {self.Name} wird geschlossen")

            self.sock.send("Server")
            self.sock.send("#C")

            self.running = False
            self.sub_from_onlinelist(self.Name)

            print(f"Der Client {self.Name} wurde geschlossen")
            client_list.pop(self.Name)

        elif parameter == "#O":
            pass
        else:
            print(f"{bcolors.WARNING}Der Client {self.Name} hat versucht an den Server die Nachicht '{parameter}' zusenden ohne das der Server eine Antwort hat{bcolors.END}")

    def data_Transfer(self, Empfänger_Name):
        if Empfänger_Name == "Server":
            msg = self.sock.read()
            self.ask_Server(msg)
            return

        msg = self.sock.read(False)

        if len(msg) == 0:
            print(f"{bcolors.WARNING}die Nachricht hat kein inhalt{bcolors.END}")
            return

        if Empfänger_Name not in client_list.keys():
            print(f"{bcolors.WARNING}Der Client {Empfänger_Name} existiert nicht{bcolors.END}");
            return

        print(f"{self.Name} --> {Empfänger_Name}")
        print("msg ->", msg)
        client_list[Empfänger_Name].sock.send_c2c(self.Name, msg)

    def add_to_onlinelist(self, name):
        global client_list

        if len(name) < 1:
            return

        for s in client_list:
            if not client_list[s].running:
                continue
            try:
                key = str(self.bytes_to_int(self.pk))
                client_list[s].sock.send("Server")
                client_list[s].sock.send("#O + " + name + " " + key)
            except:
                pass

    def sub_from_onlinelist(self, name):
        global client_list

        if len(name) < 1:
            return

        for s in client_list:
            if not client_list[s].running:
                continue
            try:
                client_list[s].sock.send("Server")
                client_list[s].sock.send("#O - " + name)
            except:
                pass

    def bytes_to_int(self, xbytes: bytes) -> int:
        return int.from_bytes(xbytes, "little")

    def int_to_bytes(self, x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, "little")

temp = {}
client_list = {}

if __name__ == '__main__':
    Nutzer_max = 10
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5000))
    server_socket.listen(Nutzer_max)

    for i in range(0, Nutzer_max):
        try:
            print("Warte auf neue Verbindung...")
            (socket_, addr) = server_socket.accept()
            client_list[str(i)+" "] = client(i, socket_)
            client_list[str(i)+" "].start()
            print(bcolors.OKGREEN + "Ein neuer Client hat sich verbunden" + bcolors.END)
        except:
            print(bcolors.WARNING + "ein Problem mit dem aktzeptieren" + bcolors.END)

    print(bcolors.WARNING + "\n\n die maximale Anzahl an Clients haben sich verbunden" + bcolors.END)
