import socket
import threading
from time import sleep
from Verschlüsselung import Cipher

class client(threading.Thread):
    global ID_list

    def __init__(self, ID,sock):
        threading.Thread.__init__(self)
        self.cipher = Cipher()
        self.ID = ID
        (self.Socket, self.addr) = sock
        self.Name = ""
        self.running = True
        self.key_server = b'\x02\x88/\xca\xb9\x08\xbc\x10\x84\xf9\x97\x0bXs\x96\xaa'
        self.key_client = b'\x9c\x98l0\xe4\xddPJ\xd5\x96\xfb\x83\xb9\x08\xb4\x1e'

    def Send(self,msg,key):
        sleep(0.1)
        msg = bytes(msg, "utf-8")
        msg = self.cipher.AES_encrypt_text(msg,key)
        self.Socket.send(msg)

    def run(self):
        try:
            self.set_name()

            while self.running:
                recv = self.Read(self.key_server)
                self.data_Transfer(recv)

            print(f"Der Client {self.Name} hat sich geschlossen")
        except:
            print(f"die Verbindung zu dem Client {self.Name if len(self.Name)> 0 else self.ID} wurde verloren")

            self.running = False
            self.sub_from_onlinelist(self.Name)
            ID_list.pop(self.ID)

    def set_name(self):
        while len(self.Name) < 1:
            recv = self.Read(self.key_server)
            found_name = False

            if len(ID_list) > 0:
                for s in ID_list:
                    if ID_list[s].Name == recv:
                        found_name = True
                if found_name:
                    self.Send("e", self.key_server)
                    recv = ""
                else:
                    self.Send(" ", self.key_server)
            else:
                self.Send(" ", self.key_server)
            self.Name = recv

        print(f"Der Nutzer {self.Name} hat sich eingeloggt und hat die ID {self.ID} bekommen")
        self.add_to_onlinelist(self.Name)

        for s in ID_list:
            try:
                self.Send("Server", self.key_server)
                self.Send("#O + " + ID_list[s].Name, self.key_server)
            except:
                pass
    def Read(self,key):
        recv = self.Socket.recv(4096)
        recv = self.cipher.AES_decrypt_text(recv, key)
        recv = str(recv, "utf-8")
        sleep(0.1)
        return recv

    def ask_Server(self, parameter):
        if parameter == '#C':
            print(f"Der Client {self.Name} wird geschlossen")

            self.Send("Server",self.key_server)
            self.Send("#C",self.key_server)

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
            msg = self.Read(self.key_server)
            self.ask_Server(msg)
        else:
            msg = self.Read(self.key_client)
            if len(msg) > 0:
                user_exist = False

                for s in ID_list:
                    if ID_list[s].Name == Empfänger_name:
                        Empfänger_ID = s
                        user_exist = True
                        break

                if user_exist:
                    print(f"{self.Name} --> {Empfänger_name}")
                    print("msg -> " + msg)

                    ID_list[Empfänger_ID].Send(self.Name, self.key_server)
                    ID_list[Empfänger_ID].Send(msg, self.key_client)
                else:
                    print(f"Der Client {Empfänger_name} existiert nicht")

    def add_to_onlinelist(self, name):
        global ID_list

        for s in ID_list:
            try:
                if name != ID_list[s]:
                    ID_list[s].Send("Server", self.key_server)
                    ID_list[s].Send("#O + " + name, self.key_server)
            except:
                pass

    def sub_from_onlinelist(self, name):
        global ID_list

        for s in ID_list:
            try:
                ID_list[s].Send("Server", self.key_server)
                ID_list[s].Send("#O - " + name, self.key_server)
            except:
                pass

ID_list = {}
Nutzer_max = 10
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("127.0.0.1", 5000))
server_socket.listen(Nutzer_max)

if __name__ == '__main__':
    for i in range(0, Nutzer_max):
        try:
            print("Warte auf neue Verbindung...")
            ID_list[i] = client(i, server_socket.accept())
            ID_list[i].start()
        except:
            print("ein Problem mit dem aktzeptieren")
    print("\n\n die maximale Anzahl an Clients haben sich verbunden")