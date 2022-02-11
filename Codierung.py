import timeit
zeichen = ['','(', 'Ä', 'Q', 'v', ':', '/', 'x', "—", ';', 'k', 'I', 'ß', '2', 'J', '§', '7', 'C', '.', 'y', 'z', 'Z', '9', 'E', '!', 'X', '€', ']', 'c', 'F', 'd', '?', '#', 'Ö', "‘", 't', 'b', "'", '{', '3', 'n', 'Ü', 'U', 'O', 'G', 'H', 'V', 'p', 'g', 'D', 'K', '|', ' ', 'q', '%', '-', '}', '*', '-', '>', '"', 'N', '³', '´', '6', ')', 'ä', '^', 'Y', 'a', 'w', '_', 's', 'ü', '4', 'ö', 'M', 'R', 'f', 'L', 'u', '8', '²', '\\', 'e', '´', '+', 'B', 'l', 'm', '=', 'h', 'W', 'S', 'µ', 'j', '0', 'r', 'P', '1', '~', '5', '<', '[', 'T', ',', 'o', '$', 'i', 'A', '@', '&']
msg_entcode_list = list("Das ist eine testnachicht")
def decode(Input):# von zeichen zu bytes
    global zeichen
    msg = ""
    for char in Input:
        index = str(zeichen.index(char))
        while len(index) < 3:
            index = "0"+index
        msg = msg + index
    return int_to_bytes(int(msg))

def entcode(Input):#von bytes zu zeichen
    global zeichen
    Input = str(bytes_to_int(Input))
    output = ""
    while len(Input)%3 != 0:
        Input = "0" + Input

    for i in range(int(len(Input)/3)):
        char = Input[:3]
        Input = Input[3:]
        output = output + str(zeichen[int(char)])
    return output

def bytes_to_int(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')

def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')
t = timeit.timeit()
de = decode(msg_entcode_list)
print(timeit.timeit()-t)
print(de)
t = timeit.timeit()
en = entcode(de)
print(timeit.timeit()-t)
print(en)

