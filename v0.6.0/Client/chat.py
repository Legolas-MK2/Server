import os
import threading

from scit_client.client import Client as Cl


class Client(Cl):
    def __init__(self):
        Cl.__init__(self)
        self.list_message = []

        valid = False
        while not valid:
            name = input("Name:")
            valid = self.set_name(name)
        self.run()

    def run(self):
        while self.running:
            command = input(">>")
            command = command.lower()

            if " " in command:
                command = command.split(" ")
            else:
                command = [command]

            self.swich(command)

    def swich(self, command: list):
        keywords_send = ["send", "an", "to", "#s"]
        keywords_help = ["help", "hilfe", "bitte_helfen_sie_mir_ich_bin_in_gefahr_bitte_helfen_sie_mir"]
        keywords_update = ["update", "reload", "msg", "#u"]
        keywords_close = ["close", "exit", "taskkill", "#c"]
        keywords_clear = ["cls", "clear"]
        keywords_online = ["online", "online_list"]
        keywords_send_file = ["send_file", "file"]

        if command[0] in keywords_send:
            if len(command) < 3:
                return
            receiver = command[1]
            msg = " ".join(command[2:])
            self.send(receiver, msg)

        elif command[0] in keywords_help:
            print("""Vielen Dank dass sie sich für den Hilfecommand Entschieden haben. Wir wünschen ihnen einen schönen Tag noch mit den folgenden Commands :)
                    Nachrichten senden           --> send [Empfänger] [Nachricht]
                    Nachrichten anschauen        --> update, msg
                    Löschende Nachrichten an/aus --> log
                    Erreichbare Clients sehen    --> online
                    Bildschirm säubern           --> cls
                    Client schließen             --> close
                    Hilfe (das hier) anzeigen    --> help """)

        elif command[0] in keywords_update:
            print("\n".join(self.list_message))
            self.list_message = []

        elif command[0] in keywords_close:
            self.close()

        elif command[0] in keywords_clear:
            os.system('cls' if os.name == 'nt' else 'clear')

        elif command[0] in keywords_online:
            print(", ".join(list(self.dict_clients.keys())))

        elif command[0] in keywords_send_file:
            if len(command) < 3:
                return
            receiver = command[1]
            msg = " ".join(command[2:])

            threading.Thread(target=self.send_file, args=(receiver, msg)).start()

        else:
            print(f"Command {command[0]} nicht gefunden")

    def read(self, recv: dict):
        self.list_message.append(f"von {recv['author']}: {recv['message']}")


if __name__ == "__main__":
    client = Client()


