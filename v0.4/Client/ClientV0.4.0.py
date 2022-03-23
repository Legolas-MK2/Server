from time import sleep
import threading
import Cipher
import socket
import os

class Read_Thread(threading.Thread):
    global nachrichten
    global running
    global key_server
    global key_client

    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket


    def run(self):
        global running
        global start

        self.set_keys()

        start = True
        while running:
            try:
                Sender = self.Read(key_server)

                if len(Sender) == 0:
                    continue

                if Sender == "Server":
                    recv = self.Read(key_server).split(" ")
                    self.Server(recv)
                    continue

                for user in users.items():
                    if Sender in user[0]:
                        recv = self.Read(key_client).split(" ")
                        msg = " ".join(recv)

                        nachrichten.append(f"von {Sender}: " + msg)
                        list_log.append(f"von {Sender}: " + msg)

            except Exception as e:
                running = False
                print("\n\nThread wurde Abgebrochen\nexcept: "+str(e))

    def set_keys(self):
        users[Name] = Cipher.generate_key(20)
        while True:
            recv = self.Read(key_server)
            if recv == "Server":
                self.Read(key_server)
                recv = self.Read(key_server)
            if recv == "e":
                return
            recv = recv.split(" ")
            name = recv[0]
            pk = recv[1]
            pk = self.int_to_bytes(int(pk))
            key = Cipher.generate_key(20)
            key = Cipher.RSA_encrypt(pk, key)
            key = str(self.bytes_to_int(key))

            users[name] = key

            Send(f"{name} {key}", key_server)


    def Server(self, command):
        global running
        if command[0] == "#C" and running == False:
            client_socket.close()
            print("Die Verbindung wurde geschlossen")
            exit()

        elif command[0] == "#O":
            mode = command[1]
            user_name = command[2]

            if mode == "-":
                for user in users.items():
                    if user[0] == user_name:
                        users.pop(user_name)
                        return

            elif mode == "+":
                key = command[3]
                key = self.int_to_bytes(int(key))
                users[user_name] = key
            else:
                print(command)

    def Read(self, key):
        recv = client_socket.recv(4096)
        if recv == b"":
            print("Error: kein inhalt")
        if key != "":
            recv = Cipher.AES_decrypt_text(recv, key)
            recv = str(recv, "utf-8")
        sleep(0.1)
        return recv

    def bytes_to_int(self, xbytes: bytes) -> int:
        return int.from_bytes(xbytes, "little")

    def int_to_bytes(self, x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, "little")

def Read(key):
    recv = client_socket.recv(4096)
    if key != None:
        recv = Cipher.AES_decrypt_text(recv, key)
        recv = str(recv, "utf-8")
    sleep(0.1)
    return recv

def Send(msg, key):
    global client_socket

    if key != None:
        msg = bytes(msg, "utf-8")
        msg = Cipher.AES_encrypt_text(msg, key)

    client_socket.send(msg)
    sleep(0.1)

def Update():
    global nachrichten

    if len(nachrichten) == 0:
        print("Keine neuen Nachichten bekommen")
        return

    print(len(nachrichten), "neue Nachrichten")
    for msg in nachrichten:
        print(msg)

    nachrichten = []

def Send_to_client(Empfänger, msg):
    global client_socket
    global key_server

    msg = msg.strip()
    if len(msg) < 1:
        print("Die Nachicht hat kein Inhalt")
        return

    for a, b in users.items():
        if a == Empfänger:
            Send(Empfänger, key_server)
            Send(msg, key_client)
            print("Nachicht wurde gesendet")
            return
    print("Client nicht gefunden")

def close():
    global running
    global client_socket

    print("Die Verbindung wird geschlossen")
    running = False
    Send("Server", key_server)
    Send("#C", key_server)
    sleep(5)
    exit()

def online():
    l = ""
    for user in users.items():
        l += user[0]+", "
    print(l[:-2])

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def log():
    global list_log

    if len(list_log) < 1:
        print("Keine Nachichten bekommen")
        return

    print(len(list_log), "Nachrichten")
    for msg in list_log:
        print(msg)

def help():
    print("""Vielen Dank dass sie sich für den Hilfecommand Entschieden haben. Wir wünschen ihnen einen schönen Tag noch mit den folgenden Commands :)
        Nachrichten senden          --> send [Empfänger] Nachricht
        Nachrichten anschauen       --> update, msg
        Löschende Nachriten an/aus  --> log
        Erreichbare Clients sehen   --> online
        
        Bildschirm säubern          --> cls
        Client schließen            --> close
        
        Hilfe (das hier) anzeigen   --> help """)

def switch(Befehl, parameter1 = "", parameter2 = ""):
    Befehl_help = ["help", "hilfe", "bitte_helfen_sie_mir_ich_bin_in_gefahr_bitte_helfen_sie_mir"]
    Befehl_update = ["update", "reload", "msg", "#u"]
    Befehl_send = ["send", "an", "to", "#s"]
    Befehl_close = ["close", "exit", "taskkill", "#c"]
    Befehl_clear = ["cls", "clear"]
    Befehl_online = ["online", "online_list"]
    Befehl_log = ["log"]

    if Befehl in Befehl_update:
        Update()
    elif Befehl in Befehl_send:
        Send_to_client(parameter1, parameter2)
    elif Befehl in Befehl_close:
        close()
    elif Befehl in Befehl_clear:
        clear()
    elif Befehl in Befehl_online:
        online()
    elif Befehl in Befehl_log:
        log()
    elif Befehl in Befehl_help:
        help()
    else:
        print(f"Der Befehl {Befehl} ist entweder falsch geschrieben oder konnte nicht gefunden werden.")

def connect():
    try_connect = True
    while try_connect:
        try:
            client_socket.connect(("127.0.0.1", 5001))
            try_connect = False
        except:
            print("Kein Server gefunden")

def RSA_Server():
    global key_server
    global pk
    global sk
    pk, sk = Cipher.RSA_generate_pk_sk()
    Send(pk, None)
    key = Read(None)
    key_server = Cipher.RSA_decrypt(sk, key)

def set_name():
    global Name
    while True:
        try:
            clear()
            Name = input("Name: ")
        except:
            continue
        if Name[:6] == "Server" or " " in Name or Name == "":
            Name = ""
            continue
        Send(Name, key_server)
        recv = Read(key_server)
        if recv == " ":
            break


def main():
    while running == True:
        try:
            msg = input(">>> ")

            if " " not in msg:
                switch(Befehl=msg.lower().strip())
                continue

            msg = msg.split(" ")
            Befehl = msg[0]
            msg.pop(0)
            Empfänger = msg[0]
            msg.pop(0)
            msg = " ".join(msg)
            switch(Befehl=Befehl.lower(), parameter1=Empfänger, parameter2=msg)

        except :
            if running == True:
                print("Es gab ein Fehler bei dem Input")

#Global Variable
key_client = b'\x9c\x98l0\xe4\xddPJ\xd5\x96\xfb\x83\xb9\x08\xb4\x1e'
key_server = None
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
running = True
nachrichten = []
list_log = []
users = {}
pk = b""
sk = b""
max_user_parameter = 2
Name = ""
start = False

if __name__ == "__main__":

    connect()
    RSA_Server()
    set_name()
    t = Read_Thread(client_socket)
    t.start()

    while start == False:
        pass
    main()
