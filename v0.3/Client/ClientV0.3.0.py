from time import sleep
import threading
import Cipher
import socket
import os
#trest
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

        while running:
            #try:
            Sender = self.Read(key_server)
            if len(Sender) == 0:
                continue

            if Sender == "Server":
                recv = self.Read(key_server).split(" ")
                self.Server(recv)
                continue
            if Sender in user_online:
                recv = self.Read(key_client).split(" ")
                msg = " ".join(recv)
                nachrichten.append(f"von {Sender}: " + msg)
                list_log.append(f"von {Sender}: " + msg)

            #except Exception as e:
            #    running = False
            #    print("\n\nThread wurde Abgebrochen\nexcept: "+str(e))

    def Server(self, command):
        global running
        global user_online
        if command[0] == "#C" and running == False:
            client_socket.close()
            print("die Verbindung wurde geschlossen", end="")
            exit(0)

        elif command[0] == "#O":
            recv = command[1]
            user = command[2]
            pk = command[3]
            pk = self.int_to_bytes(int(pk))

            if recv == "-" and user in user_online:
                user_online.remove(user)
            elif recv == "+" and user not in user_online:
                user_online.append(user)
                user_pk[user] = pk

        else:
            print("ein nicht gültiger Befehl vom Server ist gekommen")

    def Read(self, key):
        recv = client_socket.recv(4096)
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


    print(len(nachrichten), "neue Nachrichten")
    for msg in nachrichten:
        print(msg)

    nachrichten = []

def Send_to_client(Empfänger, msg):
    global client_socket
    global key_server
    global key_client

    msg = msg.strip()

    if len(msg) < 1:
        print("Die Nachicht hat kein Inhalt")
        return

    if Empfänger not in user_online:
        print(f"Der Nutzer '{Empfänger}' existiert nicht")
        return

    Send(Empfänger, key_server)
    Send(msg, key_client)
    print("Nachicht wurde gesendet")

def close():
    global running
    global client_socket

    print("die Verbindung wird geschlossen")
    Send("Server", key_server)
    Send("#C", key_server)
    running = False

def online():
    #
    l = ""
    for user in user_online:
        l += user+", "
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


def switch(Befehl, parameter1 = "", parameter2 = ""):
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
    else:
        print(f"Der Befehl {Befehl} ist entweder falsch geschrieben oder konnte nicht gefunden werden.")

#Global Variable
key_client = b'\x9c\x98l0\xe4\xddPJ\xd5\x96\xfb\x83\xb9\x08\xb4\x1e'
key_server = None
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
running = True
nachrichten = []
user_online = []
list_log = []
user_pk = {}

if __name__ == "__main__":

    #connect
    try_connect = True
    while try_connect:
        try:
            client_socket.connect(("192.168.178.140", 5000))
            try_connect = False
        except:
            print("Kein Server gefunden")
            pass

    # RSA
    pk, sk = Cipher.RSA_generate_pk_sk()
    Send(pk, None)
    key = Read(None)
    key_server = Cipher.RSA_decrypt(sk, key)

    #set name
    Name = ""
    while True:
        try:
            clear()
            Name = input("Name: ")
        except:
            continue
            pass
        if Name == "Server" or " " in Name:
            Name = ""
            continue

        Send(Name, key_server)
        recv = Read(key_server)

        if recv == " ":
            break

    t = Read_Thread(client_socket)
    t.start()

    # Main loop
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
            print("Es gab ein Fehler bei dem Input")
