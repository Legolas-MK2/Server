from . import cipher
from . import socket
from .socket import DisconnectClientError

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


def get_key(sock: socket.My_Socket, pk) -> bytes:
    key = cipher.generate_key(20)
    print(f"{key = }")
    msg = cipher.RSA_encrypt(pk, key)
    sock.send(msg, False)
    return key


def get_name(sock: socket.My_Socket, client_list, id_) -> str:
    name = ""
    while len(name) < 1:
        try:
            recv: dict = sock.read()
        except DisconnectClientError:
            return ""

        if recv.get("type") != "name":
            return ""

        name = recv["message"]
        if name[:6] == "Server" or " " in name or name == "":
            print("name error")
            sock.send({"author": 0,
                       "receiver": id_,
                       "message": "Check the name-rules"})
            continue
        elif len(client_list) == 0:
            sock.send({"author": 0,
                       "receiver": id_,
                       "message": "OK"})
            break

        continue_ = False
        for s in client_list:
            if client_list[s].Name == name:
                sock.send({"author": 0,
                           "receiver": id_,
                           "message": "This name already exists"})
                print("This name already exists")
                break
        else:
            sock.send(
                {"author": 0,
                 "receiver": id_,
                 "message": "OK"})
            break
    return name


def connect_to_all(sock: socket.My_Socket, list_client, name, id_):
    for c in list_client:
        if list_client[c].Name != name:
            pk = bytes_to_int(list_client[c].pk)

            sock.send({"author": 0,
                       "receiver": name,
                       "message": {
                           "name": list_client[c].Name,
                           "key": str(pk),
                           "id": list_client[c].id
                       }})

            recv = sock.read()["message"]

            if list_client[c].Name == recv["name"]:
                list_client[c].sock.send({"author": 0,
                                          "receiver": list_client[c],
                                          "message": {"command": "#O",
                                                      "mode": "+",
                                                      "name": name,
                                                      "key": recv["key"]}})
            else:
                print(f"{bcolors.WARNING}Warning: in connect_to_all")
                print(f"client_list[c].Name ='{list_client[c].Name}'")
                print(f"recv[0] ='{recv[0]}'{bcolors.END}")

    sock.send({"author": 0,
               "receiver": name,
               "message": "OK"})
