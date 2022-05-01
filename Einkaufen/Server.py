import socket
import threading
from time import sleep
import Cipher

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

def start(ID,sock,addr):
    global ID_list

    def bytes_to_int(xbytes: bytes) -> int:
        return int.from_bytes(xbytes, "little")

    def Read(crypt=True):
        sleep(0.1)
        recv = Client.Socket.recv(4096)

        if crypt:
            recv = Cipher.AES_decrypt_text(recv, Client.key)
            recv = str(recv, "utf-8")
        return recv

    def Send(msg, crypt=True):
        sleep(0.1)
        if crypt:
            msg = bytes(msg, "utf-8")
            msg = Cipher.AES_encrypt_text(msg, Client.key)

        Client.Socket.send(msg)

    def set_key():
        Client.pk = Read(False)
        Client.key = Cipher.generate_key(20)
        msg = Cipher.RSA_encrypt(Client.pk, Client.key)
        Send(msg, False)


    Client = client()
    def main():
        try:
            Client.Socket = sock
            Client.ID = ID
            Client.addr = addr
            set_key()


            ID_list[ID] = Client
            ID_list[ID].start()
        except:
            print(f"{bcolors.FAIL}die Verbindung zu dem Client wurde verloren{bcolors.END}")
            temp.pop(ID)

    main()
class client(threading.Thread):
    global ID_list
    global temp
    def __init__(self):
        threading.Thread.__init__(self)

        self.ID = None
        self.Socket = None
        self.addr = None
        self.running = False
        self.key = None
        self.pk = None
        self.Kontakte = {} #[online] schreiben; [anstehent] anfrage annhemen
    def Read(self, crypt=True):

        recv = self.Socket.recv(4096)
        if crypt:
            recv = Cipher.AES_decrypt_text(recv, self.key)
            recv = str(recv, "utf-8")

        sleep(0.1)
        return recv

    def Send_von(self, Sender, msg):
        self.Send(Sender)
        self.Send(msg, False)

    def Send(self, msg, crypt=True):
        sleep(0.1)
        if crypt:
            msg = bytes(msg, "utf-8")
            msg = Cipher.AES_encrypt_text(msg, self.key)

        self.Socket.send(msg)

    def run(self):
        #try:
        self.running = True
        while self.running:
            recv = self.Read()
            self.data_Transfer(recv)
        #except:
        #    print(f"{bcolors.FAIL}die Verbindung zu dem Client wurde verloren{bcolors.END}")

        #    self.running = False
        #    ID_list.pop(self.ID)
        #    if temp[self.ID]:
        #        temp.pop(self.ID)

        print(f"Der Thread vom Client hat sich geschlossen")

    def ask_Server(self, parameter):
        if parameter == '#C':
            print(f"Der Client wird geschlossen")

            self.Send("Server")
            self.Send("#C")

            self.running = False

            print(f"Der Client wurde geschlossen")
            ID_list.pop(self.ID)
            temp.pop(self.ID)
        else:
            print(f"{bcolors.WARNING}Der Client hat versucht an den Server die Nachicht '{parameter}' zusenden ohne das der Server eine Antwort hat{bcolors.END}")

    def data_Transfer(self, recv):
        if recv == "Server":
            msg = self.Read()
            self.ask_Server(msg)
            return
        mode = recv
        msg = self.Read()
        msg = msg.split(" ")
        count = msg[0]
        msg.pop(0)
        Produkt = " ".join(msg)

        try:
            int(count)
        except:
            return
        print(f"{mode} {count} {Produkt}")
        for ID in ID_list:
            if ID_list[ID].ID == self.ID:
                return
            ID_list[ID].Send(mode)
            ID_list[ID].Send(count + " " + Produkt)

    def bytes_to_int(self, xbytes: bytes) -> int:
        return int.from_bytes(xbytes, "little")

    def int_to_bytes(self, x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, "little")

temp = {}
ID_list = {}

if __name__ == '__main__':
    Nutzer_max = 10
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5000))
    server_socket.listen(Nutzer_max)

    for i in range(0, Nutzer_max):
        try:
            print("Warte auf neue Verbindung...")
            (sock, addr) = server_socket.accept()
            temp[i] = threading.Thread(target=start, args=(i, sock, addr))
            temp[i].start()
            print(bcolors.OKGREEN + "Ein neuer Client hat sich verbunden" + bcolors.END)
        except:
            print(bcolors.WARNING + "ein Problem mit dem aktzeptieren" + bcolors.END)

    print(bcolors.WARNING + "\n\n die maximale Anzahl an Clients haben sich verbunden" + bcolors.END)