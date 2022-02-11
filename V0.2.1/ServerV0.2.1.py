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

            while self.running:
                Empfänger_Name = self.Read()
                self.data_Transfer(Empfänger_Name)
            print(f"Der Client {self.Name} hat sich geschlossen")
        except:
            print(f"die Verbindung zu dem Client {self.Name if len(self.Name)> 0 else self.ID} wurde verloren")
            self.running = False
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
            ID_list.pop(self.ID)

        elif parameter == "#O":
            names = ""
            for s in ID_list:
                names += ID_list[s].Name + ", "

            names = names[:-2]
            self.Send("Server")
            sleep(0.1)
            self.Send("#O")
            self.Send(names)
        else:
            print(f"Der Client {self.Name} hat versucht an den Server die nachicht '{parameter}' zusenden ohne das der Server eine Antwort hat")

    def data_Transfer(self,Empfänger_Name):
        msg = self.Read()

        if Empfänger_Name == "Server":
            self.ask_Server(msg)
        else:
            if len(msg) > 0:
                nutzer_exist = False

                for s in ID_list:
                    if ID_list[s].Name == Empfänger_Name:
                        Empfänger_ID = s
                        nutzer_exist = True
                        break

                if nutzer_exist:
                    print(f"{self.Name} --> {Empfänger_Name}")
                    print("msg -> " + msg)

                    ID_list[Empfänger_ID].Send(bytes(self.Name,"utf-8"))
                    sleep(0.1)
                    ID_list[Empfänger_ID].Send(bytes(msg,"utf-8"))
                else:
                    print(f"Der Client {Empfänger_Name} existiert nicht")

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
    print("\n\n die maximale anzahl an Clients haben sich verbunden")