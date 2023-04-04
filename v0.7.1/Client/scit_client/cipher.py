import os
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from hashlib import md5


def rsa_generate_pk_sk(key_size: int = 1204) -> tuple[bytes, bytes]:
    key = RSA.generate(key_size)
    return key.publickey().exportKey('PEM'), key.exportKey(format="PEM")


def rsa_encrypt(pk, msg):
    pk = RSA.importKey(pk)
    cipher = PKCS1_OAEP.new(pk)
    c = cipher.encrypt(msg)
    return c


def rsa_decrypt(sk, c):
    sk = RSA.importKey(sk)
    cipher = PKCS1_OAEP.new(sk)
    m = cipher.decrypt(c)
    return m


def aes_encrypt_file(file_path, key):
    with open(file_path, 'rb') as file:
        file_bytes = file.read()
    iv = Random.new().read(16)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    encrypted_bytes = iv + cipher.encrypt(file_bytes)

    return encrypted_bytes


def aes_decrypt_file(file_bytes, key, outfile=None):
    cipher = AES.new(key, AES.MODE_CFB, file_bytes[:16])
    decrypted_bytes = cipher.decrypt(file_bytes[16:])
    if outfile:
        if not os.path.isdir(os.path.dirname(outfile)):
            os.mkdir(os.path.dirname(outfile))
        with open(outfile, "wb") as f:
            f.write(decrypted_bytes)
    else:
        return decrypted_bytes


def aes_encrypt_text(data, key):
    vector = Random.get_random_bytes(AES.block_size)
    print(f"{key = }")
    print(f"{data = }")
    print(f"{vector = }")

    encryption_cipher = AES.new(key, AES.MODE_CBC, vector)
    return vector + encryption_cipher.encrypt(pad(data, AES.block_size))


def aes_decrypt_text(data, key):
    file_vector = data[:AES.block_size]
    decryption_cipher = AES.new(key, AES.MODE_CBC, file_vector)
    return unpad(decryption_cipher.decrypt(data[AES.block_size:]), AES.block_size)


def aes_get_key(passwort):
    hashing = SHA512.new(passwort.encode("utf-8"))
    return hashing.digest()


def generate_key(size):
    return md5(Random.get_random_bytes(size)).digest()


chunks = 32 * 1024
