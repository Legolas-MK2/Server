from sys import getsizeof

zeichen = ['','(', 'Ä', 'Q', 'v', ':', '/', 'x', "—", ';', 'k', 'I', 'ß', '2', 'J', '§', '7', 'C', '.', 'y', 'z', 'Z', '9', 'E', '!', 'X', '€', ']', 'c', 'F', 'd', '?', '#', 'Ö', "‘", 't', 'b', "'", '{', '3', 'n', 'Ü', 'U', 'O', 'G', 'H', 'V', 'p', 'g', 'D', 'K', '|', ' ', 'q', '%', '-', '}', '*', '-', '>', '"', 'N', '³', '´', '6', ')', 'ä', '^', 'Y', 'a', 'w', '_', 's', 'ü', '4', 'ö', 'M', 'R', 'f', 'L', 'u', '8', '²', '\\', 'e', '´', '+', 'B', 'l', 'm', '=', 'h', 'W', 'S', 'µ', 'j', '0', 'r', 'P', '1', '~', '5', '<', '[', 'T', ',', 'o', '$', 'i', 'A', '@', '&']
msg_entcode_list = "Dhd90b3 vz2z327ftr37rb(/(IHDDLIZ/(H)L§$/FGw"
def decode(Input):# von zeichen zu bytes
    global zeichen
    msg = ""
    i2 = ""
    for char in Input:
        index = zeichen.index(char)
        i2 += str(index) + " "
        index = hex(index).split("0x")[1]
        while len(index) < 2:
            index = "0"+index
        print("index:",index)
        msg = msg + index
        print("msg:",msg)
    print("i2:",i2)
    return bytes.fromhex(msg)

def entcode(Input):#von bytes zu zeichen
    global zeichen
    Input = Input.hex()
    print(Input)
    Input = str(int(Input, 16))
    print("Input",Input)
    output = ""
    while len(Input)%2 != 0:
        Input = "0" + Input
    print(Input)
    for i in range(int(len(Input)/2)):
        char = Input[:2]
        Input = Input[2:]
        print(char)
        output = output + str(zeichen[int(char)])
    return output

def bytes_to_int(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, "little")

def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, "little")

de = decode(msg_entcode_list)
en = entcode(de)
print("größe:",getsizeof(de))
print(de)
print(en)

