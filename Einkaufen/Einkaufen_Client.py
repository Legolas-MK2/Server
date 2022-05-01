from time import sleep
import threading
import Cipher
import socket
import sys

list_add = [["6", "Bannane"], ["5", "Apfel"]]  # [[Count, "Name"], [Count, "Name"]]
list_sub = [["2", "Birne"]]  # [[Count, "Name"], [Count, "Name"]]"""

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

class Client(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.key_server = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.nachrichten = []
        self.logs = []
        self.pk = b""
        self.sk = b""
        self.start_ = False
        self.list = []

    def run(self):
        try:
            self.connect()
            self.RSA_Server()
            t = threading.Thread(target=self.Read_th)
            t.start()
        except:
            sys.exit(0)

        while self.start_ == False:
            sleep(1)
            pass
        self.main()

    def Read_th(self):
        def Server(command):
            if command[0] == "#C" and self.running == False:
                self.socket.close()
                print("Die Verbindung wurde geschlossen")
                sys.exit()
            else:
                print(bcolors.WARNING + command + " Wurde vom Server gesendet ohne es zuverarbeiten" + bcolors.END)

        self.start_ = True
        while self.running:
            try:
                recv = self.Read(self.key_server)
                print(recv)
                if len(recv) == 0:
                    continue

                if recv == "Server":
                    recv = self.Read(self.key_server).split(" ")
                    Server(recv)
                    continue

                mode = recv
                msg = self.Read(self.key_server)
                msg = msg.split(" ")
                count = msg[0]
                msg.pop(0)
                Produkt = " ".join(msg)

                try:
                    int(count)
                except:
                    continue
                print(mode, count, Produkt)
                self.list.extend([[mode, count, Produkt]])
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
    
    def send_new_produkt(self, mode, count, produkt):
        list_mode = ["add", "sub", "set"]
        mode = mode.strip()
        count = str(count).strip()
        produkt = produkt.strip()

        if len(mode) < 1:
            print("Die mode hat kein Inhalt")
            return
        if len(count) < 1:
            print("Die count hat kein Inhalt")
            return
        if len(produkt) < 1:
            print("Die produkt hat kein Inhalt")
            return
        if mode not in list_mode:
            print("ungültiger modus")
            return

        self.Send(mode, self.key_server)
        self.Send(count + " " + produkt, self.key_server)
        print("Nachicht wurde gesendet")

    def close(self):
        print("Verbindung wird geschlossen")
        self.running = False
        self.Send("Server", self.key_server)
        self.Send("#C", self.key_server)
        sys.exit()

    def switch(self, Befehl, parameter1="", parameter2="",parameter3=""):
        Befehl_send = ["send", "an", "to", "#s"]
        Befehl_close = ["close", "exit", "taself.skkill", "#c"]

        if Befehl in Befehl_send:
            self.send_new_produkt(parameter1, parameter2, parameter3)
        elif Befehl in Befehl_close:
            self.close()
        elif Befehl == ".":
            print(self.list)
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
        self.Send(self.pk,  None)
        key = self.Read(None)
        self.key_server = Cipher.RSA_decrypt(self.sk, key)
    
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
                parameter1 = msg[0]
                msg.pop(0)
                parameter2 = msg[0]
                msg.pop(0)
                parameter3 = " ".join(msg)

                self.switch(Befehl=Befehl.lower(), parameter1=parameter1, parameter2=parameter2,parameter3=parameter3)
    
            except:
                if self.running == True:
                    print(bcolors.WARNING + "Es gab ein Fehler bei dem Input" + bcolors.END)