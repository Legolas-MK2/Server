# public module

# own module
from . import cipher
from .client import ClientConnection
from .socket import My_Socket


def get_server_keys(sock:My_Socket):
    pk, sk = cipher.rsa_generate_pk_sk()
    sock.send_row(pk)
    key = sock.read(False)
    key_server = cipher.rsa_decrypt(sk, key)
    return pk, sk, key_server


def set_name(sock, name) -> tuple:
    if name[:6] == "Server" or " " in name or name == "":
        return None, None

    sock.send(0, name, "name")
    recv = sock.read()

    # if the Server sends the id then everything is successful
    msg: str = recv.get("message")
    if msg.isnumeric():
        return name, int(msg)
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
        key = cipher.rsa_encrypt(pk, bkey)
        key = str(bytes_to_int(key))
        users[id_] = ClientConnection(id_, bkey, name)

        sock.send(
            0,
            {
                "name": name,
                "key": key
            },
            "Server"
        )


def bytes_to_int(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, "little")


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, "little")
