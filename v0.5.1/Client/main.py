import json
import time
from time import sleep
import threading
import Cipher
import socket
import os
import sys

import Login
from Socket import My_Socket


class bcolors:
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    """
    HEADER = ''
    OKBLUE = ''
    OKCYAN = ''
    OKGREEN = ''
    WARNING = ''
    FAIL = ''
    END = ''
    BOLD = ''
    UNDERLINE = ''


class Read_Thread(threading.Thread):
    global nachrichten
    global running
    global key_server
    global sock

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global running
        global start
        self.set_keys()

        start = True
        while running:
            #try:
                recv = sock.read()

                if recv["author"] == "Server":
                    self.Server(recv["message"])
                    continue
                for user in users.items():
                    if recv["author"] in user[0]:
                        msg = int(recv["message"])
                        msg = self.int_to_bytes(msg)
                        msg = Cipher.AES_decrypt_text(msg, users[recv['author']])
                        msg = str(msg, "utf-8")
                        nachrichten.append(f"von {recv['author']}: " + msg)
                        logs.append(f"von {recv['author']}: " + msg)
            #except Exception as e:
            #    if running:
            #        running = False
            #        print(bcolors.FAIL + "\n\nThread wurde Abgebrochen\nexcept: " + str(e) + bcolors.END)

    def set_keys(self):
        users[username] = Cipher.generate_key(20)
        while True:
            recv = sock.read()
            recv = recv["message"]

            if recv == "OK": return

            name = recv["name"]
            pk = recv["key"]

            pk = self.int_to_bytes(int(pk))
            bkey = Cipher.generate_key(20)
            key = Cipher.RSA_encrypt(pk, bkey)
            key = str(self.bytes_to_int(key))
            users[name] = bkey

            sock.send({"author": "Server",
                       "receiver": name,
                       "message":{
                           "name": name,
                           "key": key
                       }}, key_server)

    def Server(self, msg):
        global running
        if msg["command"] == "#C" and not running:
            sock.close()
            print("Die Verbindung wurde geschlossen")
            sys.exit()
        elif msg["command"] == "#O":
            global sk
            mode = msg["mode"]
            user_name = msg["name"]

            if mode == "-":
                for user in users.items():
                    if user[0] == user_name:
                        users.pop(user_name)
                        return

            elif mode == "+":
                key = msg["key"]
                key = self.int_to_bytes(int(key))
                key = Cipher.RSA_decrypt(sk, key)
                users[user_name] = key
            else:
                print(bcolors.WARNING + msg + " Wurde vom Server gesendet ohne es zu verarbeiten" + bcolors.END)

    @staticmethod
    def bytes_to_int(xbytes: bytes) -> int:
        return int.from_bytes(xbytes, "little")

    @staticmethod
    def int_to_bytes(x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, "little")


def Update():
    global nachrichten

    if len(nachrichten) == 0:
        print("Keine neuen Nachrichten bekommen")
        return

    print(len(nachrichten), "neue Nachrichten")
    for msg in nachrichten:
        print(msg)

    nachrichten = []


def Send_to_client(Empfänger, msg):
    global key_server
    global logs
    msg = msg.strip()
    if len(msg) < 1:
        print("Die Nachricht hat kein Inhalt")
        return

    for a, b in users.items():
        if a == Empfänger:
            logs.append(f"an {Empfänger}: {msg}")

            msg = bytes(msg, "utf-8")
            msg = Cipher.AES_encrypt_text(msg, users[Empfänger])
            msg = Read_Thread.bytes_to_int(msg)

            sock.send({"author": username,
                       "receiver": Empfänger,
                       "message": msg})

            print("Nachricht wurde gesendet")
            return

    print(bcolors.WARNING + "Client nicht gefunden die verfügbaren sind" + bcolors.END)


def close():
    global running
    sock.send({"author": username,
               "receiver": "Server",
               "message": "#C"})
    print("Verbindung wird geschlossen")
    running = False


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
        print("Keine Nachricht bekommen")
        return

    print(len(logs), "Nachrichten")
    for msg in logs:
        print(msg)


def send_file(reciver, file_path):
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        print("problem mit der file")
        return
    sock.send({"author": username,
               "receiver": "Server",
               "message": {
                   "command": "#F",
                   "receiver": reciver,
                   "filename": os.path.basename(file_path)
               }})

    with open(file_path, "rb") as file:
        pass



def help():
    print("""Vielen Dank dass sie sich für den Hilfecommand Entschieden haben. Wir wünschen ihnen einen schönen Tag noch mit den folgenden Commands :)
        Nachrichten senden           --> send [Empfänger] Nachricht
        Nachrichten anschauen        --> update, msg
        Löschende Nachrichten an/aus --> log
        Erreichbare Clients sehen    --> online
        Bildschirm säubern           --> cls
        Client schließen             --> close
        Hilfe (das hier) anzeigen    --> help """)


def switch(Befehl, parameter1="", parameter2=""):
    Befehl_help = ["help", "hilfe", "bitte_helfen_sie_mir_ich_bin_in_gefahr_bitte_helfen_sie_mir"]
    Befehl_update = ["update", "reload", "msg", "#u"]
    Befehl_send = ["send", "an", "to", "#s"]
    Befehl_close = ["close", "exit", "taskkill", "#c"]
    Befehl_clear = ["cls", "clear"]
    Befehl_online = ["online", "online_list"]
    Befehl_log = ["log"]
    Befehl_send_file = ["send_file", "file"]

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
    elif Befehl in Befehl_send_file:
        send_file(parameter1, parameter2)
    elif Befehl == "":
        return
    else:
        print(f"{bcolors.WARNING}Der Befehl {Befehl} ist entweder falsch geschrieben oder konnte nicht gefunden werden.{bcolors.END}")


def main():
    while running:
        try:
            msg = input(">>> ")
        except KeyboardInterrupt:
            pass
        except EOFError:
            continue

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

        #except:
        #    if running == True:
        #        print(bcolors.WARNING + "Es gab ein Fehler bei dem Input" + bcolors.END)



# Global Variable
key_server = None
running = True
nachrichten = []
logs = []
users = {}
pk = b""
sk = b""
max_user_parameter = 2
username = ""
start = False
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if __name__ == "__main__":
    sock = My_Socket(sock)
    Login.connect(sock)
    pk, sk, key_server = Login.get_key_server(sock)
    sock.key = key_server
    username = Login.get_name(sock)
    t = Read_Thread()
    t.start()

    while not start:
        pass
    main()
