from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import StringProperty, NumericProperty

from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.button import MDRectangleFlatIconButton

from scit_client.client import Client as Cl


Window.size = (300, 500)


class Client(Cl):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager: Manager = None
        self.set_name("a")
        if not self.get_name():
            print("name already used")
            exit()
        self.group_create("t")

    def inc_element(self, name, count):
        self.group_send("t", {"name": name, "mode": "inc", "count": count})

    def dec_element(self, name, count):
        self.group_send("t", {"name": name, "mode": "dec", "count": count})

    def read(self, recv: dict):
        print(f"{recv = }")


class Main_Element(TwoLineAvatarIconListItem):
    adaptive_width = True
    name = StringProperty('')
    count = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = self.name
        self.secondary_text = str(int(self.count))

    def del_element(self, instance=None):
        self.parent.remove_widget(self)
        client.inc_element(self.name, 999)

    def sub_element(self, instance=None):
        self.count -= 1
        self.secondary_text = str(int(self.count))
        if self.count == 0:
            client.inc_element(self.name, 999)
        else:
            client.inc_element(self.name, 1)

    def add_element(self, instance=None, count=1):
        if self.count + count >= 999:
            return
        self.count += count
        self.secondary_text = str(int(self.count))
        client.dec_element(self.name, 1)


class Manager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.first_refresh = True
        client.manager = Manager

    def show_popup(self, msg):
        popup = Popup(
            title="Warnung",
            content=Label(text=msg),
            size_hint=(None, None),
            size=(200, 100))
        popup.open()

    def refresh(self):
        Window.size = (300, 500)

    def add_list(self, a, b):
        self.ids.Produkt.text = a.text

    def new_element(self, count=0, name=""):
        name = name.strip()
        try:
            count = int(count)
        except ValueError:
            return

        if any([not name, not count, count >= 1000, len(name) > 15, count < 1]):
            return
        for child in self.ids.list_Produkt.children:
            if child.text == name:
                break
        else:
            button = MDRectangleFlatIconButton(text=name, size_hint=(1, 1))
            button.bind(on_touch_down=self.add_list)
            self.ids.list_Produkt.add_widget(button)

        client.dec_element(name, count)
        for child in self.ids.list_one.children:
            if child.text == name:
                child.add_element(count=count)
                break
        else:
            element = Main_Element(name=name, count=count)
            self.ids.list_one.add_widget(element)

    def __del__(self):
        client.close()


class ScreenApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.accent_palette = "Red"
        return Manager()

    def __del__(self):
        client.close()


client = Client()
Builder.load_file("Einkaufen GUI.kv")

if __name__ == "__main__":
    ScreenApp().run()
    client.close()