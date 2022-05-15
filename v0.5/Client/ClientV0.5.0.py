import pickle
import time
from time import sleep
import threading
import Cipher
import socket
import os
import sys


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


class Read_Thread(threading.Thread):
    global nachrichten
    global running
    global key_server

    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket

    def run(self):
        global running
        self.set_client_keys()
        running = True
        while running:
            #try:
            jsonn = self.Read(key_server)
            if jsonn['author'] == "Server":
                self.Server(jsonn['message'])
                continue

            if jsonn['receiver'] in users:
                nachrichten.append(f"von {jsonn['receiver']}: {jsonn['message']}")
                logs.append(f"von {jsonn['receiver']}: {jsonn['message']}")
            """except Exception as e:
                running = False
                print(bcolors.FAIL + "\n\nThread wurde Abgebrochen\nexcept: " + str(e) + bcolors.END)"""

    def set_client_keys(self):
        users[Name] = Cipher.generate_key(20)

        while True:
            jsonn = self.Read(key_server)
            if jsonn["message"] == "end": break
            if jsonn["type"] != "keys": json_wrong(); continue
            if jsonn["type"] != "keys": json_wrong(); continue
            name = jsonn['message']['name']
            pk = jsonn['message']['pk']
            pk = self.int_to_bytes(int(pk))
            bkey = Cipher.generate_key(20)
            key = Cipher.RSA_encrypt(pk, bkey)
            key = str(self.bytes_to_int(key))

            users[name] = bkey

            Send(receiver=jsonn['message']['name'],
                 type="keys",
                 message={"name": name,
                          "key": key},
                 key=key_server)

    def Server(self, list_command):
        global running

        command = list_command["command"]
        if command == "#C" and running == False:
            client_socket.close()
            print("Die Verbindung wurde geschlossen")
            sys.exit()
        elif command == "#O":
            global sk
            name = list_command["name"]
            mode = list_command["mode"]
            if mode == "-":
                for user in users.items():
                    if user[0] == name:
                        users.pop(name)
                        return
            elif mode == "+":
                key = list_command["key"]
                key = self.int_to_bytes(int(key))
                key = Cipher.RSA_decrypt(sk, key)
                users[name] = key
            else:
                print(bcolors.WARNING + command + " wurde vom Server gesendet ohne es zuverarbeiten" + bcolors.END)
        else:
            print(bcolors.WARNING + command + " wurde vom Server gesendet ohne es zuverarbeiten" + bcolors.END)

    def Read(self, key):
        print(key)
        recv = client_socket.recv(4096)
        print("recv:", recv)
        recv = Cipher.AES_decrypt_text(recv, key)
        recv = pickle.loads(recv)
        return recv

    @staticmethod
    def bytes_to_int(xbytes: bytes) -> int:
        return int.from_bytes(xbytes, "little")

    @staticmethod
    def int_to_bytes(x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, "little")


def json_wrong():
    print("json fehler gefunden")
    pass


def Read(key):
    recv = client_socket.recv(4096)
    if key != None:
        recv = Cipher.AES_decrypt_text(recv, key)
    recv = pickle.loads(recv)
    sleep(0.1)

    return recv


def Send(receiver, type, message, key):
    global client_socket

    msg = {
        "author": Name,
        "receiver": receiver,
        "type": type,
        "message": message,
        "timestamp": "sec.min.h.d.m.y",
        "token": ""
    }

    msg = pickle.dumps(msg)
    if key != None:
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
    global logs

    msg = msg.strip()
    if len(msg) < 1:
        print("Die Nachicht hat kein Inhalt")
        return

    for a, b in users.items():
        if a == Empfänger:
            Send(receiver=Empfänger,
                 type="message",
                 message=msg,
                 key=key_server)
            print("Nachicht wurde gesendet")
            logs.append(f"an {Empfänger}: {msg}")
            return

    print(bcolors.WARNING + "Client nicht gefunden" + bcolors.END)


def close():
    global running

    print("Verbindung wird geschlossen")
    running = False
    Send(receiver="Server",
         type="metadata",
         message={"command": "#C"},
         key=key_server)
    sys.exit()


def online():
    l = ""
    for user in users.items():
        l += user[0] + ", "
    print(l[:-2])


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def log():
    global logs

    if len(logs) < 1:
        print("Keine Nachichten bekommen")
        return

    print(len(logs), "Nachrichten")
    for msg in logs:
        print(msg)


def help():
    print("""Vielen Dank dass sie sich für den Hilfecommand Entschieden haben. Wir wünschen ihnen einen schönen Tag noch mit den folgenden Commands :)
        Nachrichten senden          --> send [Empfänger] [Nachricht]
        Nachrichten anschauen       --> update, msg
        Löschende Nachriten an/aus  --> log
        Erreichbare Clients sehen   --> online

        Bildschirm säubern          --> cls
        Client schließen            --> close

        Hilfe (das hier) anzeigen   --> help """)


def switch(Befehl, parameter1="", parameter2=""):
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
        if Befehl == "":
            return
        print(f"{bcolors.WARNING}Der Befehl {Befehl} ist entweder falsch geschrieben oder konnte nicht gefunden werden.{bcolors.END}")


def connect():
    try_connect = True
    while try_connect:
        try:
            client_socket.connect(("127.0.0.1", 5000))
            try_connect = False
        except:
            print(bcolors.WARNING + "Kein Server gefunden" + bcolors.END)


def set_server_key():
    global key_server
    global pk
    global sk

    pk, sk = Cipher.RSA_generate_pk_sk()
    while True:
        Send(receiver="Server",
             type="login",
             message={
                 "mode": "key",
                 "key": pk
             },
             key=None)

        recv = Read(None)
        if recv["type"] != "login": json_wrong(); continue
        if recv["message"]["mode"] != "key": json_wrong(); continue
        key = recv["message"]["key"]
        key_server = Cipher.RSA_decrypt(sk, key)
        break


def get_name():
    global Name

    while True:
        try:
            clear()
            name = input("Name: ")
        except:
            continue

        if name[:6] == "Server" or " " in name or name == "":
            name = ""
            continue

        Send(receiver="Server",
             type="login",
             message={
                "mode": "name",
                "name": name
             },
             key=key_server)

        recv = Read(key_server)
        if recv["type"] != "login": json_wrong(); continue
        if recv["message"] == "retry": continue
        if recv["message"]["mode"] != "name": json_wrong(); continue
        if recv["message"]["name"] == name: break

    return name


def main():
    while running:
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
        except:
            if running == True:
                print(bcolors.WARNING + "Es gab ein Fehler bei dem Input" + bcolors.END)


# Global Variable
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
users = {}
nachrichten = []
logs = []
ziel_port = 5000
running = True
ziel_ip = "127.0.0.1"
Name = ""
key_server = b""
pk = b""
sk = b""


if __name__ == "__main__":
    running = True

    connect()
    set_server_key()
    Name = get_name()

    t = Read_Thread(client_socket)
    t.start()

    main()