import os
import sys

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from hashlib import md5


def RSA_generate_pk_sk():
    key = RSA.generate(1024)
    return key.publickey().exportKey('PEM'), key.exportKey(format="PEM")


def RSA_encrypt(pk, msg):
    pk = RSA.importKey(pk)
    cipher = PKCS1_OAEP.new(pk)
    c = cipher.encrypt(msg)
    return c


def RSA_decrypt(sk, c):
    sk = RSA.importKey(sk)
    cipher = PKCS1_OAEP.new(sk)
    m = cipher.decrypt(c)
    return m


def AES_encrypt_file(filename, key):
    global chunks
    out_file_name = "endcrypted-" + os.path.basename(filename)
    filesize = str(os.path.getsize(filename)).zfill(16)
    IV = Random.new().read(16)
    entcryptor = AES.new(key, AES.MODE_CFB, IV)
    with open(filename, "rb") as f_input:
        with open(out_file_name, "wb") as f_output:
            f_output.write(filesize.encode("utf-8"))
            f_output.write(IV)
            while True:
                chunk = f_input.read(chunks)
                if len(chunk) == 0:
                    break
                if len(chunk) % 16 != 0:
                    chunk += b' ' * (16 - (len(chunk) % 16))
                f_output.write(entcryptor.encrypt(chunk))


def AES_decrypt_file(filename, key):
    global chunks
    out_file_name = filename.split("-")[-1]
    with open(filename, "rb") as f_input:
        filesize = int(f_input.read(16))
        IV = f_input.read(16)
        decryptor = AES.new(key, AES.MODE_CFB, IV)
        with open(out_file_name, "wb") as f_output:
            while True:
                chunk = f_input.read(chunks)
                if len(chunk) == 0:
                    break
                f_output.write(decryptor.decrypt(chunk))
                f_output.truncate(filesize)


def AES_encrypt_bytes(input, key):
    global chunks
    IV = Random.new().read(16)
    entcryptor = AES.new(key, AES.MODE_CFB, IV)
    return entcryptor.encrypt(IV + input)


def AES_decrypt_bytes(input, key):
    global chunks
    IV = input[:16]
    input = input[16:]
    decryptor = AES.new(key, AES.MODE_CFB, IV)
    return decryptor.decrypt(input)


def AES_encrypt_text(data, key):
    vector = Random.get_random_bytes(AES.block_size)
    encryption_cipher = AES.new(key, AES.MODE_CBC, vector)
    return vector + encryption_cipher.encrypt(pad(data, AES.block_size))


def AES_decrypt_text(data, key):
    file_vector = data[:AES.block_size]
    decryption_cipher = AES.new(key, AES.MODE_CBC, file_vector)
    return unpad(decryption_cipher.decrypt(data[AES.block_size:]), AES.block_size)


def AES_get_key(passwort):
    hashing = SHA512.new(passwort.encode("utf-8"))
    return hashing.digest()


def generate_key(size):
    return md5(Random.get_random_bytes(size)).digest()


chunks = 32 * 1024
if __name__ == "__main__":
    #AES
    key = b'r\xce\xdbP\xd4\xb7G\xfc\x04H82\x96\xd24\x17'
    print(sys.getsizeof())
    e = AES_encrypt_bytes(input, key)
    print(e)
    print(d)
    if d == input:
        print("jheasgdwiajkfdgUIKdgsauoidfgguiosedfiuswaeuhzijgu")
    """
    #RSA
    pk, sk = RSA_generate_pk_sk()
    c = RSA_encrypt(pk, b"a")
    print(c)
    m = RSA_decrypt(sk, c)
    print(m)"""