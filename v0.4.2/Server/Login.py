import Cipher
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


def bytes_to_int(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, "little")


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, "little")


def get_key(sock: Socket.My_Socket) -> bytes:
    pk = sock.read(False)
    key = Cipher.generate_key(20)
    msg = Cipher.RSA_encrypt(pk, key)
    sock.send(msg, False)
    return key


def get_name(sock: Socket.My_Socket, client_list) -> str:
    Name = ""
    while len(Name) < 1:
        print("\/key\/")
        print(sock.key)
        Name = sock.read()

        if Name[:6] == "Server" or " " in Name or Name == "":
            print("name error")
            sock.send("e")
            continue
        elif len(client_list) == 0:
            sock.send(" ")
            break

        continue_ = False
        for s in client_list:
            if client_list[s].Name == Name:
                sock.send("e")
                continue_ = True

        if continue_:
            Name = ""
            continue

        sock.send(" ")
        break
    return Name


def connect_to_all(sock: Socket.My_Socket, client_list, Name):
    for c in client_list:
        if client_list[c].Name != Name and c[-1] != " ":
            pk = bytes_to_int(client_list[c].pk)
            pk = str(pk)

            sock.send(client_list[c].Name + " " + pk)
            recv = sock.read().split(" ")
            if client_list[c].Name == recv[0]:
                client_list[c].sock.send("Server")
                client_list[c].sock.send("#O + " + Name + " " + recv[1])
            else:
                print(f"{bcolors.WARNING}Warning: in connect_to_all")
                print(f"client_list[c].Name ='{client_list[c].Name}'")
                print(f"recv[0] ='{recv[0]}'{bcolors.END}")
    sock.send("e")
