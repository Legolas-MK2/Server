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
        self.cipher.key = b'\x01\x88/\xca\xb9\x08\xbc\x10\x84\xe9\x97\x0bXs\x96\xaa'

    def Send(self,msg):
        if type(msg) != bytes:
            msg = bytes(msg, "utf-8")
        msg = self.cipher.AES_encrypt_text(msg)
        self.Socket.send(msg)

    def run(self):
        try:
            while len(self.Name) < 1:
                recv = self.Read()
                found_name = False
                if len(ID_list) > 0:
                    for s in ID_list:
                        if ID_list[s].Name == recv:
                            found_name = True
                    if found_name:
                        self.Send("e")
                        recv = ""
                    else:
                        self.Send(" ")
                else:
                    self.Send(" ")
                self.Name = recv
            print(f"Der Nutzer {self.Name} hat sich eingeloggt und hat die ID {self.ID} bekommen")
            self.add_to_onlinelist(self.Name)
            for s in ID_list:
                try:
                    self.Send("Server")
                    sleep(0.1)
                    self.Send("#O")
                    sleep(0.1)
                    self.Send("+ " + ID_list[s].Name)
                except:
                    pass

            while self.running:
                Empfänger_Name = self.Read()
                self.data_Transfer(Empfänger_Name)
            print(f"Der Client {self.Name} hat sich geschlossen")
        except:
            print(f"die Verbindung zu dem Client {self.Name if len(self.Name)> 0 else self.ID} wurde verloren")
            self.running = False
            self.sub_from_onlinelist(self.Name)
            ID_list.pop(self.ID)

    def Read(self):
        recv = self.Socket.recv(4096)
        recv = str(self.cipher.AES_decrypt_text(recv), "utf-8")
        return recv

    def ask_Server(self,parameter):
        if parameter == '#C':
            print(f"Der Client {self.Name} wird geschlossen")

            self.Send("Server")
            sleep(0.1)
            self.Send("#C")

            self.running = False
            self.sub_from_onlinelist(self.Name)
            ID_list.pop(self.ID)

        elif parameter == "#O":
            pass
        else:
            print(f"Der Client {self.Name} hat versucht an den Server die nachicht '{parameter}' zusenden ohne das der Server eine Antwort hat")

    def data_Transfer(self,Empfänger_Name):
        msg = self.Read()

        if Empfänger_Name == "Server":
            self.ask_Server(msg)
        else:
            if len(msg) > 0:
                user_exist = False

                for s in ID_list:
                    if ID_list[s].Name == Empfänger_Name:
                        Empfänger_ID = s
                        user_exist = True
                        break

                if user_exist:
                    print(f"{self.Name} --> {Empfänger_Name}")
                    print("msg -> " + msg)

                    ID_list[Empfänger_ID].Send(self.Name)
                    sleep(0.1)
                    ID_list[Empfänger_ID].Send(msg)
                else:
                    print(f"Der Client {Empfänger_Name} existiert nicht")

    def add_to_onlinelist(self, name):
        global ID_list
        for s in ID_list:
            try:
                ID_list[s].Send("Server")
                sleep(0.1)
                ID_list[s].Send("#O")
                sleep(0.1)
                ID_list[s].Send("+ " + name)
            except:
                pass

    def sub_from_onlinelist(self, name):
        global ID_list
        for s in ID_list:
            try:
                ID_list[s].Send("Server")
                sleep(0.1)
                ID_list[s].Send("#O")
                sleep(0.1)
                ID_list[s].Send("- " + name)
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