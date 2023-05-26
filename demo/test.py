from Client.scit_client.socket import json2bytes
from Client.scit_client.cipher import aes_decrypt_text, aes_encrypt_text
# Convert an integer to a 2-byte representation
number = 65535


def data2bytes(receiver: int, _type: int, message: str, *, group=None):

    # check if id over 2 bytes is
    if receiver > 65535:
        raise OverflowError(f"the receiver_id ({receiver}) is to big")
    if _type > 65535:
        raise OverflowError(f"the type_id ({_type}) is to big")

    msg = receiver.to_bytes(2, 'big')
    msg += _type.to_bytes(2, 'big')
    msg += bytes(message, "utf-8")

    return msg


def bytes2data(data: bytes):
    receiver = int.from_bytes(data[:2], 'big')
    _type = int.from_bytes(data[2:4], 'big')
    message = data[4:].decode('utf-8')

    return receiver, _type, message


def main():
    receiver = 3
    _type = 459
    message = "fsekjhwkkjggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggfh"*1000
    print(f"{receiver = } ||  {_type = } || {message = }")
    b = data2bytes(receiver, _type, message)
    print(b)
    receiver, _type, message = bytes2data(b)
    print(f"{receiver = } ||  {_type = } || {message = }\n")
    print(len(aes_encrypt_text(json2bytes({"receiver": receiver, "type": _type, "message": message}), b"aaaaaaaaaaaaaaaa")) / 100 * len(aes_encrypt_text(b, b"aaaaaaaaaaaaaaaa")), end="% \n")
    print(len(aes_encrypt_text(b, b"aaaaaaaaaaaaaaaa")))
    print(len(aes_encrypt_text(json2bytes({"receiver": receiver, "type": _type, "message": message}), b"aaaaaaaaaaaaaaaa")))


if __name__ == '__main__':
    main()

