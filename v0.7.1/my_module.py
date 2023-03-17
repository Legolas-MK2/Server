import codetester

codetester.fall_in_exception = True


@codetester.debugging
def normale_verbindung():
    from Server.Server.server import Server_Handler, Client_Handler
    from Client.scit_client.client import Client as Cl

    class Client(Cl):
        def __init__(self):
            super().__init__()
            self.valid = self.set_name("a")

    class Server(Server_Handler):
        def __init__(self):
            super().__init__()
            self.connect_client()

    server = Server()
    client = Client()


#client sendet an sich selber
#client sendet an jemand anders
#client bricht ab ohne name anzugeben
#client sendet ohne name anzugeben
#client sendet keine file
#client sendet mittelgroße file
#client sendet große file
#client sendet file an sich und jamand anders
#client sendet zwei mal file
#client sendet file an jemandanders und bekommt eine file zurück
#client stürzt ab
#client stürzt ab beim file senden und verbindet sich wieder
#client sendet langen text
#client kreift mit injection an
#
#
#
#
#
#
#
#
#
#
