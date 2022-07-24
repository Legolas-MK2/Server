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


def get_key(sock: Socket.My_Socket) -> (bytes, bytes):
    pk = sock.read(False)
    key = Cipher.generate_key(20)
    msg = Cipher.RSA_encrypt(pk, key)
    sock.send(msg, False)
    return pk, key


def get_name(sock: Socket.My_Socket, client_list) -> str:
    name = ""
    while len(name) < 1:
        recv = sock.read()
        name = recv["message"]

        if name[:6] == "Server" or " " in name or name == "":
            print("name error")
            sock.send({"author": "Server",
                       "receiver": name,
                       "message": "Check the name-rules"})
            continue
        elif len(client_list) == 0:
            sock.send({"author": "Server",
                       "receiver": name,
                       "message": "OK"})
            break

        continue_ = False
        for s in client_list:
            if client_list[s].Name == name:
                sock.send({"author": "Server",
                           "receiver": name,
                           "message": "This name already exists"})
                continue_ = True

        if continue_:
            name = ""
            continue

        sock.send({"author": "Server",
                   "receiver": name,
                   "message": "OK"})
        break
    return name


def connect_to_all(sock: Socket.My_Socket, client_list, name):
    for c in client_list:
        if client_list[c].Name != name and c[-1] != " ":
            pk = bytes_to_int(client_list[c].pk)

            sock.send({"author": "Server",
                       "receiver": name,
                       "message": {
                           "name": client_list[c].Name,
                           "key": str(pk)
                       }})
            recv = sock.read()["message"]
            if client_list[c].Name == recv["name"]:
                client_list[c].sock.send({"author": "Server",
                                          "receiver": client_list[c].Name,
                                          "message": {"command": "#O",
                                                      "mode": "+",
                                                      "name": name,
                                                      "key": recv["key"]}})
            else:
                print(f"{bcolors.WARNING}Warning: in connect_to_all")
                print(f"client_list[c].Name ='{client_list[c].Name}'")
                print(f"recv[0] ='{recv[0]}'{bcolors.END}")
    sock.send({"author": "Server",
               "receiver": name,
               "message": "OK"})
