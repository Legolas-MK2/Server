import os.path

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivymd.uix.button import MDIconButton
from kivymd.uix.list.list import OneLineListItem
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty
from kivymd.uix.list import TwoLineAvatarIconListItem
Window.size = (300, 500)


def callback(instance):
    pass
    #print('The button <%s> is being pressed' % instance.text)


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

    def sub_element(self, instance=None):
        self.count -= 1
        self.secondary_text = str(int(self.count))
        if self.count == 0:
            self.del_element()

    def add_element(self, instance=None):
        if self.count >= 999:
            return
        self.count += 1
        self.secondary_text = str(int(self.count))


class Manager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.first_refresh = True

    def show_popup(self, msg):
        popup = Popup(
            title="Warnung",
            content=Label(text=msg),
            size_hint=(None, None),
            size=(200, 100))
        popup.open()

    def refresh(self):
        if self.first_refresh:
            self.first_refresh = False
            if not os.path.exists("db.txt"):
                with open("db.txt", "wb"):
                    pass
            with open("db.txt", "r", encoding='utf-8') as f:
                for produkt in f.readlines():
                    if "#SEP#" not in produkt:
                        continue
                    name, count = produkt.split("#SEP#")
                    count = count[:-1]
                    if not count.isnumeric():
                        continue
                    self.new_element(count, name)

        if not os.path.exists("db.txt"):
            with open("db.txt", "wb"):
                pass
        with open("db.txt", "w") as f:
            for i in self.ids:
                if i[:12] == "label_count_":
                    f.writelines(f"{i[12:]}#SEP#{self.ids[i].text[14:-8]}\n")

    def add_list(self, a):
        self.ids.Produkt.text = a.text

    def new_element(self, count=0, name=""):
        name = name.strip()
        count = int(count)

        if any([not name, not count, count >= 1000]):
            return
        element = Main_Element(name=name, count=count)
        self.ids.list_one.add_widget(element)


class ScreenApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        return Manager()


Builder.load_file("guitest.kv")

if __name__ == "__main__":
    ScreenApp().run()