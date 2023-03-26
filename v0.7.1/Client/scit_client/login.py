# public module

# own module
from . import cipher
from .client import ClientConnection


def get_server_keys(sock):
    pk, sk = cipher.RSA_generate_pk_sk()
    sock.send(pk, False)
    key = sock.read(False)
    key_server = cipher.RSA_decrypt(sk, key)
    return pk, sk, key_server


def set_name(sock, name):
    if name[:6] == "Server" or " " in name or name == "":
        return None

    sock.send({"receiver": 0,
               "type": "name",
               "message": name})
    recv = sock.read()

    msg = recv.get("message")
    id = recv["receiver"]
    if msg == "OK":
        return name, id
    else:
        print(msg)
        return None, None


def get_clients_keys(sock) -> dict:
    users = {}
    while True:
        recv = sock.read()
        recv = recv["message"]

        if recv == "OK":

            return users

        name = recv["name"]
        pk = recv["key"]
        id_ = recv["id"]

        pk = int_to_bytes(int(pk))
        bkey = cipher.generate_key(20)
        key = cipher.RSA_encrypt(pk, bkey)
        key = str(bytes_to_int(key))
        users[id_] = ClientConnection(id_, bkey, name)

        sock.send({"author": 0,
                   "receiver": "name",
                   "message": {
                       "name": name,
                       "key": key
                   }})


def bytes_to_int(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, "little")


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, "little")
