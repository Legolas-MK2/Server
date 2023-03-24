from Server.server import Server_Handler, Client_Handler, Group_Handler


class Client(Client_Handler):
    def on_text_message(self, data):
        self.send(data)

    def on_file_message(self, data):
        self.send_file(data)
        return

    def on_server_message(self, data):
        print(data)

    def on_close(self):
        pass


class Server(Server_Handler):
    def __init__(self, class_client):
        super().__init__()
        while True:
            self.connect_client(class_client)


class Group(Group_Handler):
    def add(self, a):
        print("djkghafeaukuf")


if __name__ == "__main__":
    Group_Handler = Group
    Server(Client)
