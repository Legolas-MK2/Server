import kivy
from kivy.lang import Builder

kivy.require("1.11.1")

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

kv = """
Manager:
    Screen:
        name: "main"
        Button:
            text: "main"
    Screen:
        name: "add"
        Button:
            text: "add"
"""
class Manager(ScreenManager):
    pass

class ScreenApp(App):
    def build(self):
        return Manager()
Builder.load_string(kv)
if __name__ == "__main__":
    ScreenApp().run()