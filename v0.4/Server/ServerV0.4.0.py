import socket
import threading
from time import sleep
import Cipher
#dawdwadawda
def start():
    global ID_list

    def __init__(ID,sock):

        ID = ID
        (Socket, addr ) = sock
        Name = ""
        key = b''
        pk = b''

    def run(self):
        self.set_key()
        self.set_name()
        self.connect_to_all()

    def Read(self, crypt=True):
        recv = self.Socket.recv(4096)

        if crypt:
            recv = Cipher.AES_decrypt_text(recv, self.key)
            recv = str(recv, "utf-8")
        sleep(0.1)
        return recv

    def Send(self, msg, crypt=True):
        sleep(0.1)
        if crypt:
            msg = bytes(msg, "utf-8")
            msg = Cipher.AES_encrypt_text(msg, self.key)

        self.Socket.send(msg)

    def set_key(self):
        self.pk = self.Read(False)
        self.key = Cipher.generate_key(20)
        msg = Cipher.RSA_encrypt(self.pk, self.key)
        self.pk = str(self.bytes_to_int(self.pk))
        self.Send(msg, False)

    def set_name(self):
        while len(self.Name) < 1:
            self.Name = self.Read()

            if len(ID_list) == 1:
                break

            for s in ID_list:
                if ID_list[s].Name == self.Name and ID_list[s].ID != self.ID:
                    self.Send("e")
                    self.Name = ""
                    continue

        self.Send(" ")

        print(f"Der Nutzer {self.Name} hat sich eingeloggt und hat die ID {self.ID} bekommen")

    def connect_to_all(self):
        for client in ID_list:
            if ID_list[client].Name != self.Name:
                self.Send(ID_list[client].Name + " " + ID_list[client].pk)
                recv = self.Read().split(" ")

                if ID_list[client].Name == recv[0]:
                    ID_list[client].Send("Server")
                    ID_list[client].Send("#O + " + self.Name + " " + recv[1])
                else:
                    print("Error: in connect_to_all\nID_list[client].Name =", ID_list[client].Name, "\nrecv[0] =",
                          recv[0])
        self.Send("e")


class client(threading.Thread):
    global ID_list

    def __init__(self, ID,sock):
        threading.Thread.__init__(self)

        self.ID = ID
        (self.Socket, self.addr) = sock
        self.Name = ""
        self.running = False
        self.key = b''
        self.pk = b''

    def Read(self, crypt = True):
        recv = self.Socket.recv(4096)

        if crypt:
            recv = Cipher.AES_decrypt_text(recv, self.key)
            recv = str(recv, "utf-8")

        sleep(0.1)

        return recv

    def Send(self, msg, crypt=True):
        sleep(0.1)
        if crypt:
            msg = bytes(msg, "utf-8")
            msg = Cipher.AES_encrypt_text(msg, self.key)

        self.Socket.send(msg)
    def run(self):
        try:
            self.set_key()
            self.set_name()
            self.connect_to_all()

            self.running = True
            while self.running:
                recv = self.Read()
                self.data_Transfer(recv)
        except:
            print(f"die Verbindung zu dem Client {self.Name if len(self.Name)> 0 else self.ID} wurde verloren")

            self.running = False
            self.sub_from_onlinelist(self.Name)
            ID_list.pop(self.ID)

        print(f"Der Thread vom Client {self.Name if len(self.Name)> 0 else self.ID} hat sich geschlossen")

    def Read(self, crypt = True):
        recv = self.Socket.recv(4096)

        if crypt:
            recv = Cipher.AES_decrypt_text(recv, self.key)
            recv = str(recv, "utf-8")

        sleep(0.1)

        return recv

    def ask_Server(self, parameter):
        if parameter == '#C':
            print(f"Der Client {self.Name} wird geschlossen")

            self.Send("Server")
            self.Send("#C")

            self.running = False
            self.sub_from_onlinelist(self.Name)

            print(f"Der Client {self.Name} wurde geschlossen")
            ID_list.pop(self.ID)

        elif parameter == "#O":
            pass
        elif parameter == "#K":
            pass
        else:
            print(f"Der Client {self.Name} hat versucht an den Server die Nachicht '{parameter}' zusenden ohne das der Server eine Antwort hat")

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
            print(f"Der Client {Empfänger_Name} existiert nicht")
            return

        print(f"{self.Name} --> {Empfänger_Name}")
        print("msg ->", msg)
        ID_list[Empfänger_ID].Send(self.Name)
        ID_list[Empfänger_ID].Send(msg, False)

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

ID_list = {}

if __name__ == '__main__':
    Nutzer_max = 10
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5001))
    server_socket.listen(Nutzer_max)

    for i in range(0, Nutzer_max):
        try:
            print("Warte auf neue Verbindung...")

            ID_list[i] = client(i, server_socket.accept())
            ID_list[i].start()
        except:
            print("ein Problem mit dem aktzeptieren")

    print("\n\n die maximale Anzahl an Clients haben sich verbunden")
