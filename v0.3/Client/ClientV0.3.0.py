import socket
import threading
import os
from time import sleep
import Cipher

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
            try:
                Sender = self.Read(key_server)

                if len(Sender) > 0:
                    if Sender == "Server":
                        recv = self.Read(key_server).split(" ")
                        self.Server(recv)
                    else:
                        recv = self.Read(key_client).split(" ")
                        msg = " ".join(recv)
                        nachrichten.append(f"von {Sender}: " + msg)

            except Exception as e:
                running = False
                print("\n\nThread wurde Abgebrochen\nexcept: "+str(e))

    def Server(self, command):
        global running
        global user_online

        if command[0] == "#C" and running == False:
            client_socket.close()
            print("die Verbindung wurde geschlossen",end="")
            exit()

        elif command[0] == "#O":
            recv = command[1]
            user = command[2]

            if recv == "-" and user in user_online:
                user_online.remove(user)
            elif recv == "+" and user not in user_online:
                user_online.append(user)

        else:
            print("ein nicht gültiger Befehl vom Server ist gekommen")

    def Read(self, key):
        recv = client_socket.recv(4096)
        recv = Cipher.AES_decrypt_text(recv, key)
        recv = str(recv, "utf-8")
        sleep(0.1)

        return recv

def Read(key):
    recv = client_socket.recv(4096)

    if key != None:
        recv = Cipher.AES_decrypt_text(recv, key)
        recv = str(recv, "utf-8")
    sleep(0.1)

    return recv

def Send(msg,key):
    global client_socket
    if key != None:
        msg = bytes(msg, "utf-8")
        msg = Cipher.AES_encrypt_text(msg, key)
    client_socket.send(msg)
    sleep(0.1)

def Update():
    global nachrichten

    print(len(nachrichten), "neue Nachrichten")

    if len(nachrichten) > 0:
        for msg in nachrichten:
            print(msg)

        nachrichten = []
    else:
        print("Keine neuen Nachichten bekommen")

def Send_to_client(Empfänger,msg):
    global client_socket
    global key_server
    global key_client

    msg = msg.strip()

    if len(msg) > 0:
        Send(Empfänger, key_server)
        Send(msg, key_client)
        print("Nachicht wurde gesendet")
    else:
        print("Die Nachicht hat kein Inhalt")

def close():
    global running
    global client_socket

    print("die Verbindung wird geschlossen")
    Send("Server", key_server)
    Send("#C", key_server)
    running = False

def online():
    #tes
    l = ""
    for user in user_online:
        l += user+", "
    print(l[:-2])

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def switch(Befehl,parameter1 = "", parameter2 = ""):
    Befehl_update = ["update", "reload", "msg", "#u"]
    Befehl_send = ["send", "an", "to", "#s"]
    Befehl_close = ["close", "exit", "taskkill", "#c"]
    Befehl_clear = ["cls", "clear"]
    Befehl_online = ["online", "online_list"]

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
    else:
        print(f"Der Befehl {Befehl} ist entweder falsch geschrieben oder konnte nicht gefunden werden.")

#Global Variable
key_client = b'\x9c\x98l0\xe4\xddPJ\xd5\x96\xfb\x83\xb9\x08\xb4\x1e'
key_server = None
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
running = True
nachrichten = []
user_online = []

if __name__ == "__main__":

    #connect
    try_connect = True
    while try_connect:
        try:
            client_socket.connect(("127.0.0.1", 5000))
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
    while len(Name) < 1:
        try:
            clear()
            Name = input("Name: ")
        except:
            pass
        if Name == "Server" or " " in Name:
            Name = ""
        else:
            Send(Name, key_server)
            recv = Read(key_server)
            if recv != " ":
                Name = ""

    t = Read_Thread(client_socket)
    t.start()
    running = True

    # Main loop
    while running == True:
        try:
            msg = input(">>> ")
            if " " in msg:
                msg = msg.split(" ")
                Befehl = msg[0]
                msg.pop(0)
                Empfänger = msg[0]
                msg.pop(0)
                msg = " ".join(msg)
                switch(Befehl=Befehl.lower(), parameter1=Empfänger, parameter2=msg)
            else:
                switch(Befehl=msg.lower().strip())
        except :
            print("Es gab ein Fehler bei dem Input")
