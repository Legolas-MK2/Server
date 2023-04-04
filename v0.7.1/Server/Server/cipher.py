import os

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from hashlib import md5


def rsa_generate_pk_sk():
    key = RSA.generate(1024)
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


def aes_encrypt_file(filename, key):
    global chunks
    out_file_name = "endcrypted-" + os.path.basename(filename)
    filesize = str(os.path.getsize(filename)).zfill(16)
    iv = Random.new().read(16)
    entcryptor = AES.new(key, AES.MODE_CFB, iv)
    with open(filename, "rb") as f_input:
        with open(out_file_name, "wb") as f_output:
            f_output.write(filesize.encode("utf-8"))
            f_output.write(iv)
            while True:
                chunk = f_input.read(chunks)
                if len(chunk) == 0:
                    break
                if len(chunk) % 16 != 0:
                    chunk += b' ' * (16 - (len(chunk) % 16))
                f_output.write(entcryptor.encrypt(chunk))


def aes_decrypt_file(filename, key):
    global chunks
    out_file_name = filename.split("-")[-1]
    with open(filename, "rb") as f_input:

        filesize = int(f_input.read(16))
        iv = f_input.read(16)
        decryptor = AES.new(key, AES.MODE_CFB, iv)

        with open(out_file_name, "wb") as f_output:
            while True:
                chunk = f_input.read(chunks)
                if len(chunk) == 0:
                    break

                f_output.write(decryptor.decrypt(chunk))
                f_output.truncate(filesize)


def aes_encrypt_text(data, key):
    vector = Random.get_random_bytes(AES.block_size)
    encryption_cipher = AES.new(key, AES.MODE_CBC, vector)
    return vector + encryption_cipher.encrypt(pad(data, AES.block_size))


def aes_decrypt_text(data, key):
    file_vector = data[:AES.block_size]
    decryption_cipher = AES.new(key, AES.MODE_CBC, file_vector)
    return unpad(decryption_cipher.decrypt(data[AES.block_size:]), AES.block_size)


def aes_get_key(passwort):
    hashing = SHA512.new(passwort.encode("utf-8"))
    return hashing.digest()


def hash(byte):
    h = SHA512.new()
    h.update(byte)
    return h.hexdigest()


def generate_key(size):
    return md5(Random.get_random_bytes(size)).digest()


chunks = 32 * 1024
if __name__ == "__main__":
    t = "a"
    for i in range(100000):
        t = hash(t.encode())
    print(t)
