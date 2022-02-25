import os
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from hashlib import md5

class Cipher:

    def __init__(self,e = ""):
        pass
    def RSA_generate_sk(self):
        key = RSA.generate(4096)
        with open("secret_key.pem", "wb") as f_out:
            f_out.write(key.exportKey(format="PEM"))

    def RSA_import_key(self,file_name):
        with open(file_name, "rb") as f_in:
            key = RSA.importKey(f_in.read())
        return key

    def RSA_generate_pk(self,sk):
        pk = sk.public_key()
        with open("public_key.pem", "wb") as f_out:
            f_out.write(pk.exportKey(format="PEM"))
        return pk

    def RSA_encrypt(self,pk, msg):
        cipher = PKCS1_OAEP.new(pk)
        c = cipher.encrypt(msg)
        return c

    def RSA_decrypt(self,sk, c):
        cipher = PKCS1_OAEP.new(sk)
        m = cipher.decrypt(c)
        return m

    def AES_encrypt_file(self, filename, key):
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

    def AES_decrypt_file(self, filename,key):
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

    def AES_encrypt_text(self, data,key):
        vector = Random.get_random_bytes(AES.block_size)
        encryption_cipher = AES.new(key, AES.MODE_CBC, vector)
        return vector + encryption_cipher.encrypt(pad(data, AES.block_size))

    def AES_decrypt_text(self, data,key):
        file_vector = data[:AES.block_size]
        decryption_cipher = AES.new(key, AES.MODE_CBC, file_vector)
        return unpad(decryption_cipher.decrypt(data[AES.block_size:]), AES.block_size)

    def AES_get_key(passwort):
        hashing = SHA512.new(passwort.encode("utf-8"))
        return hashing.digest()

    def generate_key(self,size):
        return md5(Random.get_random_bytes(size)).digest()

chunks = 32 * 1024
if __name__ == "__main__":
    cipher = Cipher()
    key = cipher.generate_key(20)
    crypt_text = cipher.AES_encrypt_text(data=b"das ist eine nachicht",key=key)
    print(crypt_text)
    print(cipher.AES_decrypt_text(crypt_text,key = key))

    cipher.RSA_generate_sk()
    key = cipher.RSA_import_key("secret_key.pem")
    pk = cipher.RSA_generate_pk(key)
    c = cipher.RSA_encrypt(pk, b"das ist eine nachicht")
    print(c)
    m = cipher.RSA_decrypt(key, c)