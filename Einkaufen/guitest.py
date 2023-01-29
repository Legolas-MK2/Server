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
Window.size = (300, 500)


def callback(instance):
    print('The button <%s> is being pressed' % instance.text)


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

    def new_element(self, count="", name=""):
        name = name.strip()
        count = count.strip()

        def del_element(instance=None):
            print(f"remove label_count_{name}")
            self.ids.list_one.remove_widget(self.ids[("boxlayout_" + name)])
            del self.ids[("label_count_" + name)]
            del self.ids[("boxlayout_" + name)]

        def sub_element(instance=None):
            id_label = "label_count_" + name
            new_count = int(self.ids[id_label].text[14:-8]) - 1
            self.ids[id_label].text = "[color=000000]" + str(new_count) + "[/color]"
            if new_count == 0:
                del_element()

        def add_element(instance=None):
            id_label = "label_count_" + name
            if int(self.ids[id_label].text[14:-8]) > 998:
                return

            self.ids[id_label].text = "[color=000000]" + str(int(self.ids[id_label].text[14:-8]) + 1) + "[/color]"

        if count == "":
            self.show_popup("Die Mengenangabe\nwurde nicht angegeben")
            return
        if name == "":
            self.show_popup("Der Name\nwurde nicht angegeben")
            return
        if int(count) > 999 or int(count) < 1:
            self.show_popup("Die Mengenangabe muss\nzwischen 1 und 999 liegen")
            return
        if len(name) > 17:
            self.show_popup("Der Name\nist zu lang")
            return
        if "#SEP#" in name:
            self.show_popup("Der Name\nist ungültig")
            return
        if ("boxlayout_" + name) in self.ids:
            for _ in range(int(count)):
                add_element()
            return

        for i in self.ids["list_Produkt"].children:
            if i.text == name:
                break
        else:
            item = OneLineListItem()
            item.text = name
            item.bind(on_press=self.add_list)
            self.ids["list_Produkt"].add_widget(item)

        boxlayout = BoxLayout()
        boxlayout.height = 40
        boxlayout.orientation = 'horizontal'

        boxlayout2 = BoxLayout()
        boxlayout2.height = 40
        boxlayout2.orientation = 'horizontal'
        self.ids[("boxlayout_" + name)] = boxlayout
        Button_del = MDIconButton(icon="delete-outline", on_press=del_element)

        label_name = Label(markup=True, text="[color=000000]" + str(name) + "[/color]")

        Button_sub = MDIconButton(icon="minus-box-outline", on_press=sub_element)
        label_count = Label(markup=True, text="[color=000000]" + str(count) + "[/color]")
        self.ids[("label_count_" + name)] = label_count
        Button_add = MDIconButton(icon="plus-box-outline", on_press=add_element)

        boxlayout.add_widget(Button_del)
        boxlayout2.add_widget(Button_sub)
        boxlayout2.add_widget(label_count)
        boxlayout2.add_widget(Button_add)

        boxlayout.add_widget(label_name)
        boxlayout.add_widget(boxlayout2)

        self.ids.list_one.add_widget(boxlayout)


class ScreenApp(MDApp):
    def build(self):
        return Manager()


Builder.load_file("guitest.kv")

if __name__ == "__main__":
    ScreenApp().run()