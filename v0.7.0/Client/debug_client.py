import hashlib
import os
import subprocess
import time

from scit_client.client import Client


class client(Client):
    def __init__(self):
        self.messages = []

    def init(self):
        Client.__init__(self)

    def read(self, recv):
        self.messages.append(recv)


vulnerabilitys = []

"""
def test():
    c = client()

    print("Test 0: try to set name bevor init")
    try:
        c.init()
        c.set_name("a")
        print("Successfully")
    except Exception as e:
        print("Fail")
        vulnerabilitys.append("Test 1: try to set name bevor init")
    c.close()
"""


def test1():
    c = client()

    print("Test 1: try to set name bevor init")
    try:
        c.set_name("a")
        print("Successfully")
    except Exception as e:
        print("Fail")
        vulnerabilitys.append("Test 1: try to set name bevor init")
    c.close()


def test2():
    c1 = client()
    c2 = client()
    print("Test 2: same name")
    try:
        c1.init()
        tmp = c1.set_name("a")
        if not tmp:
            raise Exception
        c2.init()
        tmp = c2.set_name("a")
        if tmp:
            raise Exception

        print("Successfully")
    except Exception as e:
        print("Fail")
        vulnerabilitys.append("Test 2: same name")

    c1.close()
    c2.close()


def test3():
    c = client()

    print("Test 3: injection")
    try:
        c.init()
        c.set_name("a\"\'{,\"\',,")

        if c.send("a\"\'{,\"\',,", "b\"\'{}[]"):
            time.sleep(3)
            if c.messages[0]["message"] == "b\"\'{}[]" or c.messages[0]["message"] == r"b\"\'{}[]":
                pass
            else:
                raise Exception
        else:
            print("erste Nachricht hatte Probleme beim senden")
            raise Exception

        print("Successfully")
    except Exception as e:
        print("Fail")
        vulnerabilitys.append("Test 3: injection")

    c.close()


def test4():
    c1 = client()
    c2 = client()
    print("Test 4: send a file")
    try:
        c1.init()
        c1.set_name("a")

        c2.init()
        c2.set_name("b")

        c2.send_file("a", "debug/file")
        time.sleep(5)

        with open("debug/file", 'rb') as file_to_check:
            data = file_to_check.read()
            file_hash = hashlib.md5(data).hexdigest()

        with open("files/file", 'rb') as file_to_check:
            data = file_to_check.read()
            if file_hash != hashlib.md5(data).hexdigest():
                raise Exception

        print("Successfully")
    except Exception as e:
        print("Fail")
        vulnerabilitys.append("Test 4: send a file")
    c1.close()
    c2.close()


def test5():
    c1 = client()
    c2 = client()

    print("Test 5: send message")
    try:
        c1.init()
        c1.set_name("a")

        c2.init()
        c2.set_name("b")

        c1.send("b", "test")
        time.sleep(1)
        if c2.messages[0]["message"] == "test" and c2.messages[0]["author"] == "a":
            pass
        else:
            raise Exception

        print("Successfully")
    except Exception as e:
        print("Fail")
        vulnerabilitys.append("Test 5: send message")
    c1.close()
    c2.close()


def main():
    all_tests = [test1, test2, test3, test4, test5]

    for test in all_tests:
        #p = subprocess.Popen(["python", r"C:\Coden\py_projekte\Server\git Server\Server\v0.5.2\Server\main.py"], stdout=subprocess.PIPE)
        #input("---")
        test()
        print("ende vom test")
        #p.kill()

    print("\n")
    print("Fails in:")
    if not vulnerabilitys:
        print("----")
    for v in vulnerabilitys:
        print(f"{v}")


if __name__ == '__main__':
    main()
