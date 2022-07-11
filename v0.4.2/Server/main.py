import socket
import threading

import Login
import Socket


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


class client_händler(threading.Thread):
    global client_list

    def __init__(self, id_, sock):
        threading.Thread.__init__(self)
        self.id = id_
        self.sock = Socket.My_Socket(sock)
        self.Name = ""
        self.running = False
        self.key = None
        self.pk = None

    def run(self):
        try:
            #   set AES key
            self.pk, self.key = Login.get_key(self.sock)
            self.sock.key = self.key

            #   set Name
            self.Name = Login.get_name(self.sock, client_list)
            print(f"{bcolors.OKGREEN}Der Nutzer {self.Name} hat sich eingeloggt "
                  f"und hat die ID {self.id} bekommen{bcolors.END}")
            client_list[self.Name] = client_list.pop(str(self.id)+" ")

            #   send all other clients keys
            Login.connect_to_all(self.sock, client_list, self.Name)

            #   client-main-loop
            self.running = True
            while self.running:
                author = self.sock.read()

                #   if the message is addressed to the server
                if author == "Server":
                    msg = self.sock.read()
                    self.client2server(msg)
                    continue

                #   Message forwarding
                self.forwarding(author)

        except ConnectionResetError:
            self.running = False
            self.sub_from_onlinelist(self.Name)

            if self.Name == "":    # hat der Client schon ein Name
                print(f"{bcolors.FAIL}Die Verbindung vom Client mit der ID {self.id} ist abgestürzt {bcolors.END}")
                client_list.pop(f"{self.id} ")
            else:
                print(f"{bcolors.FAIL}Die Verbindung vom Client mit dem Namen {self.Name} ist abgestürzt {bcolors.END}")
                client_list.pop(self.Name)

        print(f"Der Thread vom Client {self.Name if len(self.Name)> 0 else self.id} hat sich geschlossen")

    def client2server(self, parameter):
        if parameter == '#C':
            print(f"Der Client {self.Name} wird geschlossen")

            self.sock.send("Server")
            self.sock.send("#C")

            self.running = False
            self.sub_from_onlinelist(self.Name)

            print(f"Der Client {self.Name} wurde geschlossen")
            client_list.pop(self.Name)

        elif parameter == "#O":
            pass
        else:
            print(f"{bcolors.WARNING}Der Client {self.Name} hat versucht an den Server "
                  f"die Nachricht '{parameter}' zusenden ohne das der Server eine Antwort hat{bcolors.END}")

    def forwarding(self, name_receiver):
        msg = self.sock.read(False)

        if len(msg) == 0:
            print(f"{bcolors.WARNING}die Nachricht hat kein inhalt{bcolors.END}")
            return

        receiver = client_list.get(name_receiver)
        if not receiver:
            print(f"{bcolors.WARNING}Der Client {name_receiver} wurde nicht gefunden{bcolors.END}")
            return

        print(f"{self.Name} --> {name_receiver}")
        print("msg ->", msg)
        receiver.sock.send_c2c(self.Name, msg)

    def add_to_onlinelist(self, name):
        global client_list

        if len(name) < 1:
            return

        for s in client_list:
            if not client_list[s].running:
                continue
            key = str(self.bytes_to_int(self.pk))
            client_list[s].sock.send("Server")
            client_list[s].sock.send("#O + " + name + " " + key)

    @staticmethod
    def sub_from_onlinelist(name):
        global client_list

        if len(name) < 1:
            return

        for s in client_list:
            if not client_list[s].running:
                continue
            client_list[s].sock.send("Server")
            client_list[s].sock.send("#O - " + name)

    @staticmethod
    def bytes_to_int(xbytes: bytes) -> int:
        return int.from_bytes(xbytes, "little")

    @staticmethod
    def int_to_bytes(x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, "little")


def main():
    max_user = 10
    ip = "127.0.0.1"
    port = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(max_user)

    for id in range(max_user):
        print("Warte auf neue Verbindung...")
        (socket_, addr) = server_socket.accept()
        client_list[str(id) + " "] = client_händler(id, socket_)
        client_list[str(id) + " "].start()
        print(bcolors.OKGREEN + "Ein neuer Client hat sich verbunden" + bcolors.END)

    print(bcolors.WARNING + "\n\n die maximale Anzahl an Clients haben sich verbunden" + bcolors.END)


client_list = {}

if __name__ == '__main__':
    main()
