import kivy
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivymd.uix.button import MDIconButton
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivy.graphics import Color, Rectangle
import time
from Einkaufen_Client import list_add
from Einkaufen_Client import list_sub

Window.size = (300, 500)

def callback(instance):
    print('The button <%s> is being pressed' % instance.text)

class Manager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def refresh(self):
        global list_add
        global list_sub

        #add
        if len(list_add) != 0:
            for element in list_add:
                count, name = element
                self.new_element(count, name)
            list_add = []

        #sub
        if len(list_sub) == 0:
            return

        for element in list_sub:
            count, name = element
            if ("boxlayout_" + name) not in self.ids:
                break

            for i in range(int(count)):
                id_label = "label_count_" + name
                self.ids[id_label].text = "[color=000000]" + str(int(self.ids[id_label].text[14:-8]) - 1) + "[/color]"

                if self.ids[id_label].text == "[color=000000]" + str(0) + "[/color]":
                    self.ids.list_one.remove_widget(self.ids[("boxlayout_" + name)])

        list_sub = []

    def new_element(self, count="", name=""):
        name = name.strip()
        count = count.strip()
        def del_element(instance):
            self.ids.list_one.remove_widget(self.ids[("boxlayout_" + name)])

        def sub_element(instance):
            id_label = "label_count_" + name
            new_count = int(self.ids[id_label].text[14:-8]) - 1
            self.ids[id_label].text = "[color=000000]" + str(new_count) + "[/color]"
            if new_count == 0:
                del_element(1)

        def add_element(instance):
            id_label = "label_count_" + name
            if int(self.ids[id_label].text[14:-8]) > 998:
                return
            self.ids[id_label].text = "[color=000000]" + str(int(self.ids[id_label].text[14:-8]) + 1) + "[/color]"


        if count == "":
            return
        if name == "":
            return
        if 1 < int(count) > 999:
            return
        if ("boxlayout_"+name) in self.ids:
            for _ in range(int(count)):
                add_element(1)
            return

        boxlayout = BoxLayout()
        boxlayout.height = 40
        boxlayout.orientation = 'horizontal'

        boxlayout2 = BoxLayout()
        boxlayout2.height = 40
        boxlayout2.orientation = 'horizontal'
        self.ids[("boxlayout_"+name)] = boxlayout
        Button_del = MDIconButton(icon="delete", on_press=del_element)

        label_name = Label(markup=True, text="[color=000000]" + str(name) + "[/color]")

        Button_sub = Button(text="-", on_press=sub_element)
        label_count = Label(markup=True, text="[color=000000]" + str(count) + "[/color]")
        self.ids[("label_count_" + name)] = label_count
        Button_add = Button(text="+", on_press=add_element)

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