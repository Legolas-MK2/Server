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

    def Read(crypt=True):
        sleep(0.1)
        recv = Client.Socket.recv(4096)

        if crypt:
            recv = Cipher.AES_decrypt_text(recv, Client.key)
            recv = str(recv, "utf-8")
        return recv

    def Send(msg, crypt=True):
        sleep(0.1)
        if crypt:
            msg = bytes(msg, "utf-8")
            msg = Cipher.AES_encrypt_text(msg, Client.key)

        Client.Socket.send(msg)

    def set_key():
        Client.pk = Read(False)
        Client.key = Cipher.generate_key(20)
        msg = Cipher.RSA_encrypt(Client.pk, Client.key)
        Send(msg, False)

    def get_name():
        Name = ""
        while len(Name) < 1:
            Name = Read()
            if len(ID_list) == 0:
                Send(" ")
                print(f"{bcolors.OKGREEN}Der Nutzer {Client.Name} hat sich eingeloggt und hat die ID {ID} bekommen{bcolors.END}")
                return Name
            continue_ = False
            for s in ID_list:
                if ID_list[s].Name == Name:
                    Send("e")
                    continue_ = True
            if continue_:
                Name = ""
                continue
            Send(" ")
            print(f"{bcolors.OKGREEN}Der Nutzer {Client.Name} hat sich eingeloggt und hat die ID {ID} bekommen{bcolors.END}")
            return Name

    def connect_to_all():
        for client in ID_list:
            if ID_list[client].Name != Client.Name:

                pk = bytes_to_int(ID_list[client].pk)
                pk = str(pk)

                Client.Send(ID_list[client].Name + " " + pk)
                recv = Read().split(" ")
                if ID_list[client].Name == recv[0]:
                    ID_list[client].Send("Server")
                    ID_list[client].Send("#O + " + Client.Name + " " + recv[1])
                else:
                    print(f"{bcolors.WARNING}Warning: in connect_to_all")
                    print(f"ID_list[client].Name ='{ID_list[client].Name}'")
                    print(f"recv[0] ='{recv[0]}'{bcolors.END}")
        Send("e")

    def sub_from_onlinelist(name):
        global ID_list

        if len(name) < 1:
            return

        for s in ID_list:
            try:
                ID_list[s].Send("Server")
                ID_list[s].Send("#O - " + name)
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
            self.running = True
            while self.running:
                recv = self.Read()
                self.data_Transfer(recv)
        except:
            print(f"{bcolors.FAIL}die Verbindung zu dem Client {self.Name if len(self.Name)> 0 else self.ID} wurde verloren{bcolors.END}")

            self.running = False
            self.sub_from_onlinelist(self.Name)
            ID_list.pop(self.ID)
            if temp[self.ID]:
                temp.pop(self.ID)

        print(f"Der Thread vom Client {self.Name if len(self.Name)> 0 else self.ID} hat sich geschlossen")

    def ask_Server(self, parameter):
        if parameter == '#C':
            print(f"Der Client {self.Name} wird geschlossen")

            self.Send("Server")
            self.Send("#C")

            self.running = False
            self.sub_from_onlinelist(self.Name)

            print(f"Der Client {self.Name} wurde geschlossen")
            ID_list.pop(self.ID)
            temp.pop(self.ID)

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
        exist = False

        if len(msg) == 0:
            return

        for s in ID_list:
            if ID_list[s].Name == Empfänger_Name:
                Empfänger_ID = s
                exist = True
                break

        if not exist:
            print(f"{bcolors.WARNING}Der Client {Empfänger_Name} existiert nicht{bcolors.END}")
            return

        print(f"{self.Name} --> {Empfänger_Name}")
        print("msg ->", msg)
        ID_list[Empfänger_ID].Send_von(self.Name, msg)

    def add_to_onlinelist(self, name):
        global ID_list

        if len(name) < 1:
            return

        for s in ID_list:
            try:
                key = str(self.bytes_to_int(self.pk))
                ID_list[s].Send("Server")
                ID_list[s].Send("#O + " + name + " " + key)
            except:
                pass

    def sub_from_onlinelist(self, name):
        global ID_list

        if len(name) < 1:
            return

        for s in ID_list:
            try:
                ID_list[s].Send("Server")
                ID_list[s].Send("#O - " + name)
            except:
                pass

    def bytes_to_int(self, xbytes: bytes) -> int:
        return int.from_bytes(xbytes, "little")

    def int_to_bytes(self, x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, "little")

temp = {}
ID_list = {}
#TODO name_list = {}

if __name__ == '__main__':
    Nutzer_max = 10
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5000))
    server_socket.listen(Nutzer_max)

    for i in range(0, Nutzer_max):
        try:
            print("Warte auf neue Verbindung...")
            (sock, addr) = server_socket.accept()
            temp[i] = threading.Thread(target=start, args=(i, sock, addr))
            temp[i].start()
            print(bcolors.OKGREEN, "Ein neuer Client hat sich verbunden", bcolors.END)
        except:
            print(bcolors.WARNING + "ein Problem mit dem aktzeptieren" + bcolors.END)

    print(bcolors.WARNING + "\n\n die maximale Anzahl an Clients haben sich verbunden" + bcolors.END)