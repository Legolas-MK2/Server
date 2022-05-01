from time import sleep
import threading
import Cipher
import socket
import os
import sys

list_add = [["6", "Bannane"], ["5", "Apfel"]]  # [[Count, "Name"], [Count, "Name"]]
list_sub = [["2", "Birne"]]  # [[Count, "Name"], [Count, "Name"]]"""

class bcolors():
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Client(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.key_server = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.nachrichten = []
        self.logs = []
        self.users = {}
        self.pk = b""
        self.sk = b""
        self.Name = ""
        self.start_ = False
        self.list_add = [["6", "Bannane"], ["5", "Apfel"]]  # [[Count, "Name"], [Count, "Name"]]
        self.list_sub = [["2", "a"]]  # [[Count, "Name"], [Count, "Name"]]"""
    def run(self):
        try:
            self.connect()
            self.RSA_Server()
            self.set_name()
            t = threading.Thread(target=self.Read_th)
            t.start()
        except:
            sys.exit(0)
        while self.start_ == False:
            sleep(1)
            pass
        self.main()

    def Read_th(self):
        def set_keys():
            self.users[self.Name] = Cipher.generate_key(20)
            while True:
                recv = self.Read(self.key_server)
                if recv == "e":
                    return
                recv = recv.split(" ")
                name = recv[0]
                self.pk = recv[1]
                self.pk = self.int_to_bytes(int(self.pk))
                bkey = Cipher.generate_key(20)
                key = Cipher.RSA_encrypt(self.pk, bkey)
                key = str(self.bytes_to_int(key))
                self.users[name] = bkey
    
                self.Send(f"{name} {key}", self.key_server)
    
        def Server(command):
            if command[0] == "#C" and self.running == False:
                self.socket.close()
                print("Die Verbindung wurde geschlossen")
                sys.exit()
            elif command[0] == "#O":
                mode = command[1]
                user_name = command[2]

                if mode == "-":
                    for user in self.users.items():
                        if user[0] == user_name:
                            self.users.pop(user_name)
                            return
    
                elif mode == "+":
                    key = command[3]
                    key = self.int_to_bytes(int(key))
                    key = Cipher.RSA_decrypt(self.sk, key)
                    self.users[user_name] = key
                elif mode == "add":
    
                    pass
                else:
                    print(bcolors.WARNING + command + " Wurde vom Server gesendet ohne es zuverarbeiten" + bcolors.END)

        set_keys()

        self.start_ = True
        while self.running:
            try:
                Sender = self.Read(self.key_server)
                if len(Sender) == 0:
                    continue

                if Sender == "Server":
                    recv = self.Read(self.key_server).split(" ")
                    Server(recv)
                    continue

                for user in self.users.items():
                    if Sender in user[0]:
                        recv = self.Read(self.users[Sender])
                        msg = recv.split(" ")
                        mode = msg[0]
                        msg.pop(0)
                        count = msg[0]
                        msg.pop(0)
                        Produkt = " ".join(msg)

                        try:
                            int(count)
                        except:
                            continue

                        if mode == "add":
                            self.list_add.extend([[count, Produkt]])
                            pass
                        elif mode == "sub":
                            self.list_sub.extend([[count, Produkt]])

            except Exception as e:
                self.running = False
                print(bcolors.FAIL + "\n\nThread wurde Abgebrochen\nexcept: " + str(e) + bcolors.END)

    def bytes_to_int(self, xbytes: bytes) -> int:
        return int.from_bytes(xbytes, "little")

    def int_to_bytes(self, x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, "little")
    
    def Read(self, key):
        recv = self.socket.recv(4096)
    
        if key != None:
            recv = Cipher.AES_decrypt_text(recv, key)
            recv = str(recv, "utf-8")
        sleep(0.1)
    
        return recv
    
    def Send(self, msg, key):
    
        if key != None:
            msg = bytes(msg, "utf-8")
            msg = Cipher.AES_encrypt_text(msg, key)
    
        self.socket.send(msg)
        sleep(0.1)
    
    def Update(self):
    
        if len(self.nachrichten) == 0:
            print("Keine neuen Nachichten bekommen")
            return
    
        print(len(self.nachrichten), "neue self.nachrichten")
        for msg in self.nachrichten:
            print(msg)
    
        self.nachrichten = []
    
    def Send_to_client(self, Empfänger, msg):
        msg = msg.strip()
        if len(msg) < 1:
            print("Die Nachicht hat kein Inhalt")
            return
    
        for a, b in self.users.items():
            if a == Empfänger:
                self.Send(Empfänger, self.key_server)
                self.Send(msg, self.users[Empfänger])
                print("Nachicht wurde gesendet")
                self.logs.append(f"an {Empfänger}: {msg}")
                return
    
        print(bcolors.WARNING + "Client nicht gefunden" + bcolors.END)
    
    def close(self):
    
        print("Verbindung wird geschlossen")
        self.running = False
        self.Send("Server", self.key_server)
        self.Send("#C", self.key_server)
        sys.exit()
    
    def online(self):
        l = ""
        for user in self.users.items():
            l += user[0] + ", "
        print(l[:-2])
    
    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def log(self):
    
        if len(self.logs) < 1:
            print("Keine Nachichten bekommen")
            return
    
        print(len(self.logs), "self.nachrichten")
        for msg in self.logs:
            print(msg)
    
    
    def help(self):
        print("""Vielen Dank dass sie sich für den Hilfecommand Entschieden haben. Wir wünschen ihnen einen schönen Tag noch mit den folgenden Commands :)
            self.nachrichten senden          --> send [Empfänger] Nachricht
            self.nachrichten anschauen       --> update, msg
            Löschende Nachriten an/aus  --> log
            Erreichbare Clients sehen   --> online
    
            Bildschirm säubern          --> cls
            Client schließen            --> close
    
            Hilfe (das hier) anzeigen   --> help """)
    
    
    def switch(self, Befehl, parameter1="", parameter2=""):
        Befehl_help = ["help", "hilfe", "bitte_helfen_sie_mir_ich_bin_in_gefahr_bitte_helfen_sie_mir"]
        Befehl_update = ["update", "reload", "msg", "#u"]
        Befehl_send = ["send", "an", "to", "#s"]
        Befehl_close = ["close", "exit", "taself.skkill", "#c"]
        Befehl_clear = ["cls", "clear"]
        Befehl_online = ["online", "online_list"]
        Befehl_log = ["log"]
    
        if Befehl in Befehl_update:
            self.Update()
        elif Befehl in Befehl_send:
            self.Send_to_client(parameter1, parameter2)
        elif Befehl in Befehl_close:
            self.close()
        elif Befehl in Befehl_clear:
            self.clear()
        elif Befehl in Befehl_online:
            self.online()
        elif Befehl in Befehl_log:
            self.log()
        elif Befehl in Befehl_help:
            self.help()
        elif Befehl == ".":
            print(self.list_add)
            print(self.list_sub)
        else:
            print(f"{bcolors.WARNING}Der Befehl {Befehl} ist entweder falsch geschrieben oder konnte nicht gefunden werden.{bcolors.END}")
    
    def connect(self):
        try_connect = True
        while try_connect:
            try:
                self.socket.connect(("127.0.0.1", 5000))
                try_connect = False
            except:
                print(bcolors.WARNING + "Kein Server gefunden" + bcolors.END)
    
    
    def RSA_Server(self):
        pk, sk = Cipher.RSA_generate_pk_sk()
        self.pk, self.sk = pk, sk
        self.Send(self.pk, None)
        key = self.Read(None)
        self.key_server = Cipher.RSA_decrypt(self.sk, key)
    
    
    def set_name(self):

        while True:
            try:
                self.clear()
                print(1)

                self.Name = input("Name: ")
            except:
                continue
            if self.Name[:6] == "Server" or " " in self.Name or self.Name == "":
                self.Name = ""
                continue
            else:
                self.Send(self.Name, self.key_server)
                print(self.key_server)
                print(1)
                recv = self.Read(self.key_server)
                print(2)
                if recv == " ":
                    break
                else:
                    print("Der Name ist schon belegt")
    
    def main(self):
        while self.running == True:
            try:
                msg = input(">>> ")
    
                if " " not in msg:
                    self.switch(Befehl=msg.lower().strip())
                    continue
    
                msg = msg.split(" ")
                Befehl = msg[0]
                msg.pop(0)
                Empfänger = msg[0]
                msg.pop(0)
                msg = " ".join(msg)
                self.switch(Befehl=Befehl.lower(), parameter1=Empfänger, parameter2=msg)
    
            except:
                if self.running == True:
                    print(bcolors.WARNING + "Es gab ein Fehler bei dem Input" + bcolors.END)

