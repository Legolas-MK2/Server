# public module

# own module
import Cipher
import Socket


ip = "127.0.0.1"
port = 5000


def connect(objekt_socket):
    sock = None
    while not sock:
        sock = objekt_socket.try_connect(ip, port)
    return sock


def get_key_server(sock):
    pk, sk = Cipher.RSA_generate_pk_sk()

    sock.send(pk, False)
    key = sock.read(False)

    key_server = Cipher.RSA_decrypt(sk, key)
    return pk, sk, key_server


def get_name(sock):
    recv = ""
    while recv != " ":
        name = input("Name: ")
        if name[:6] == "Server" or " " in name or name == "":
            continue

        sock.send(name)
        recv = sock.read()

    return name
