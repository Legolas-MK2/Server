import socket
import threading
from time import sleep
import Cipher

class client(threading.Thread):
    global ID_list

    def __init__(self, ID,sock):
        threading.Thread.__init__(self)

        self.ID = ID
        (self.Socket, self.addr) = sock
        self.Name = ""
        self.running = True
        self.key = b''
        self.pk = b''

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

            while self.running:
                recv = self.Read()
                self.data_Transfer(recv)
        except:
            print(f"die Verbindung zu dem Client {self.Name if len(self.Name)> 0 else self.ID} wurde verloren")

            self.running = False
            self.sub_from_onlinelist(self.Name)
            ID_list.pop(self.ID)

        print(f"Der Thread vom Client {self.Name if len(self.Name)> 0 else self.ID} hat sich geschlossen")

    def set_key(self):
        self.pk = self.Read(False)
        self.key = Cipher.generate_key(20)
        msg = Cipher.RSA_encrypt(self.pk, self.key)
        self.Send(msg, False)

    def set_name(self):
        while len(self.Name) < 1:
            print(1)
            recv = self.Read()
            print(2)
            found_name = False
            print(3)
            if len(ID_list) == 1:
                print(4)
                self.Send(" ")
                print(5)
                print(recv)
                self.Name = recv
                print(len(self.Name))
                print(len(self.Name) < 1)
                print(6)
                print(f"Der Nutzer {self.Name} hat sich eingeloggt und hat die ID {self.ID} bekommen")
                self.add_to_onlinelist(self.Name)
                return
            print(7)
            for s in ID_list:
                print(8)
                if ID_list[s].Name == recv:
                    print(9)
                    found_name = True
            print(10)
            if found_name:
                print(11)
                self.Send("e")
                print(12)
                recv = ""
            else:
                print(13)
                self.Send(" ")
            print(14)
        print(15)


        for s in ID_list:
            try:
                self.Send("Server")
                self.Send("#O + " + ID_list[s].Name)
            except:
                pass

    def Read(self,crypt = True):
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
        else:
            print(f"Der Client {self.Name} hat versucht an den Server die Nachicht '{parameter}' zusenden ohne das der Server eine Antwort hat")

    def data_Transfer(self, Empfänger_name):
        if Empfänger_name == "Server":
            msg = self.Read()
            self.ask_Server(msg)
<<<<<<< HEAD
            return

        msg = self.Read(False)
        exist = False
=======
        else:
            msg = self.Read(False)
>>>>>>> 23f6a5146c0235f6afb2b4b030db15347d5d2201

        if len(msg) == 0:
            return

        for s in ID_list:
            if ID_list[s].Name == Empfänger_name:
                Empfänger_ID = s
                exist = True
                break

        if not exist:
            print(f"Der Client {Empfänger_name} existiert nicht")
            return

        print(f"{self.Name} --> {Empfänger_name}")
        print("msg ->", msg)
        ID_list[Empfänger_ID].Send(self.Name)
        ID_list[Empfänger_ID].Send(msg, False)

    def add_to_onlinelist(self, name):
        global ID_list

        for s in ID_list:
            try:
                if name != ID_list[s]:
                    key = str(self.bytes_to_int(self.pk))
                    ID_list[s].Send("Server")
                    ID_list[s].Send("#O + "+ name + " " + key)
            except:
                pass

    def sub_from_onlinelist(self, name):
        global ID_list

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
    server_socket.bind(("192.168.178.140", 5000))
    server_socket.listen(Nutzer_max)

    for i in range(0, Nutzer_max):
        try:
            print("Warte auf neue Verbindung...")

            ID_list[i] = client(i, server_socket.accept())
            ID_list[i].start()
        except:
            print("ein Problem mit dem aktzeptieren")

    print("\n\n die maximale Anzahl an Clients haben sich verbunden")