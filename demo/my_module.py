import codetester

codetester.fall_in_exception = True


@codetester.debugging
def nur_verbinden():
    from Server.Server.server import Server_Handler
    from Client.scit_client.client import Client as Cl

    server = Server_Handler()
    server.async_connect_client()
    client = Cl()
    client.close()



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
