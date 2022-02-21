import socket
import threading
import os
from time import sleep
from Verschlüsselung import Cipher

class Read_Thread(threading.Thread):
    global nachrichten,running, key

    def __init__(self,socket):
        threading.Thread.__init__(self)
        self.socket = socket

    def run(self):
        global running, cipher

        while running:
            try:
                Sender = self.Read()
                if len(Sender) > 0:
                    if Sender == "Server":
                        self.Server()
                    else:
                        msg = self.Read()
                        nachrichten.append(f"von {Sender}: " + msg)
            except Exception as e:
                running = False
                print("Thread wurde geschlossen \n except: "+str(e))

    def Read(self):
        global cipher
        recv = self.socket.recv(4096)
        recv = cipher.AES_decrypt_text(recv)
        return str(recv, "utf-8")

    def Server(self):
        global running, cipher, key, user_online
        sleep(0.1)
        command = self.Read()
        print("command:",command)
        if command == "#C" and running == False:
            client_socket.close()
            print("die Verbindung wurde geschlossen",end="")
            exit()
        elif command == "#O":
            sleep(0.1)
            recv = self.Read().split(" ")
            user = recv[1]
            if recv[0] == "-" and recv[1] in user_online:
                user_online.remove(user)
            elif recv[0] == "+" and recv[1] not in user_online:
                user_online.append(user)
        else:
            print("ein nicht gültiger Befehl vom Server ist gekommen")

def Send(msg):
    global client_socket, cipher
    msg = bytes(msg, "utf-8")
    msg = cipher.AES_encrypt_text(msg)
    client_socket.send(msg)

def Update():
    global nachrichten
    print(str(len(nachrichten)),"neue Nachrichten")

    if len(nachrichten) > 0:
        for msg in nachrichten:
            print(msg)
        nachrichten = []
    else:
        print("Keine neuen Nachichten bekommen")

def Send_to_client(Empfänger,msg):
    global client_socket, cipher
    msg = msg.strip()
    if len(msg) > 0:
        Send(Empfänger)
        sleep(0.1)
        Send(msg)
        print("Nachicht wurde gesendet")
    else:
        print("Die Nachicht hat kein Inhalt")

def close():
    global running, client_socket, cipher
    print("der Client wird geschlossen")
    Send("Server")
    sleep(0.1)
    Send("#C")
    running = False

def online():
    print(user_online)

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
key = b'\x01\x88/\xca\xb9\x08\xbc\x10\x84\xe9\x97\x0bXs\x96\xaa' #Key für Client und Client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
running = True
nachrichten = []
cipher = Cipher()
cipher.key = key
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
            Send(Name)
            recv = client_socket.recv(4096)
            recv = str(cipher.AES_decrypt_text(recv),"utf-8")
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