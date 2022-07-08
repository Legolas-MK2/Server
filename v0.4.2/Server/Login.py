
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def set_key(self):
    self.pk = self.Read(False)
    self.key = Cipher.generate_key(20)
    msg = Cipher.RSA_encrypt(self.pk, self.key)
    self.Send(msg, False)


def get_name(self):
    Name = ""
    while len(Name) < 1:
        Name = self.Read()
        print(f"Name = {Name}")
        if Name[:6] == "Server" or " " in Name or Name == "":
            print("name error")
            self.Send("e")
            continue
        elif len(client_list) == 0:
            self.Send(" ")
            print(
                f"{bcolors.OKGREEN}Der Nutzer {self.Name} hat sich eingeloggt und hat die ID {self.ID} bekommen{bcolors.END}")
            return Name
        continue_ = False
        for s in client_list:
            if client_list[s].Name == Name:
                self.Send("e")
                continue_ = True
        if continue_:
            Name = ""
            continue
        self.Send(" ")
        print(
            f"{bcolors.OKGREEN}Der Nutzer {self.Name} hat sich eingeloggt und hat die ID {self.ID} bekommen{bcolors.END}")
        return Name


def connect_to_all(self):
    for c in client_list:
        if client_list[c].Name != self.Name \
                and c[-1] != " ":
            pk = self.bytes_to_int(client_list[c].pk)
            pk = str(pk)

            self.Send(client_list[c].Name + " " + pk)
            recv = self.Read().split(" ")
            if client_list[c].Name == recv[0]:
                client_list[c].Send("Server")
                client_list[c].Send("#O + " + self.Name + " " + recv[1])
            else:
                print(f"{bcolors.WARNING}Warning: in connect_to_all")
                print(f"client_list[c].Name ='{client_list[c].Name}'")
                print(f"recv[0] ='{recv[0]}'{bcolors.END}")
    self.Send("e")