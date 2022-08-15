# public
import socket
import threading

# own
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


class client_handler(threading.Thread):
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
                recv = self.sock.read()
                #   if the message is addressed to the server
                if recv["receiver"] == "Server":
                    self.client2server(recv["message"])
                    continue

                #   Message forwarding
                self.forwarding(recv)

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

            self.running = False
            self.sub_from_onlinelist(self.Name)
            self.sock.send({"author": "Server",
                            "message": {
                                "command": "#C"
                            }})
            print(f"Der Client {self.Name} wurde geschlossen")
            client_list.pop(self.Name)
        elif parameter == "#O":
            pass
        else:
            print(f"{bcolors.WARNING}Der Client {self.Name} hat versucht an den Server "
                  f"die Nachricht '{parameter}' zusenden ohne das der Server eine Antwort hat{bcolors.END}")

    def forwarding(self, msg):
        if msg["receiver"] not in client_list:
            print(f"{bcolors.WARNING}Der Client {msg['receiver']} wurde nicht gefunden{bcolors.END}")
            return

        if msg.get("type") == "text":
            self.text_msg(msg)
        elif msg.get("type") == "file":
            self.file_msg(msg)

    def file_msg(self, msg):
        receiver = msg["receiver"]
        msg = msg["message"]
        packet_count = msg["packet_count"]

        if receiver not in client_list:
            return

        print(f"{self.Name} --> {receiver}")
        print("msg = file")
        print(f"filename = {msg['file_name']}")

        client_list[receiver].sock.send({
            "author": self.Name,
            "type": "file",
            "message": {
                "file_name": msg["file_name"],
                "packet_count": packet_count

            }
        })
        client_list[receiver].sock.file_stream(self.sock, int(packet_count))

    def text_msg(self, msg):
        name_receiver = msg["receiver"]
        receiver = client_list.get(name_receiver)

        print(f"{self.Name} --> {name_receiver}")
        print("msg ->", msg["message"])

        receiver.sock.send({"author": self.Name,
                            "message": msg["message"]
                            })

    @staticmethod
    def sub_from_onlinelist(name):
        global client_list

        if len(name) < 1:
            return

        for s in client_list:
            if not client_list[s].running:
                continue
            j = {"author": "Server",
                 "receiver": client_list[s].Name,
                 "message": {"command": "#O",
                             "mode": "-",
                             "name": name}}
            client_list[s].sock.send(j)

    @staticmethod
    def bytes_to_int(xbytes: bytes) -> int:
        return int.from_bytes(xbytes, "little")

    @staticmethod
    def int_to_bytes(x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, "little")


def main():
    max_user = 10
    ip = "192.168.178.75"
    port = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(max_user)

    for id in range(max_user):
        print("Warte auf neue Verbindung...")
        (socket_, addr) = server_socket.accept()
        client_list[str(id) + " "] = client_handler(id, socket_)
        client_list[str(id) + " "].start()
        print(bcolors.OKGREEN + "Ein neuer Client hat sich verbunden" + bcolors.END)

    print(bcolors.WARNING + "\n\n die maximale Anzahl an Clients haben sich verbunden" + bcolors.END)


client_list = {}

if __name__ == '__main__':
    main()
