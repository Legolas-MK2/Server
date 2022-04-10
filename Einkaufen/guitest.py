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

Window.size = (300, 500)

Produkt_widget = []
ii = 3
def callback(instance):
    print('The button <%s> is being pressed' % instance.text)

class Manager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def delete_produkt(self, instance):

        pass

    def new_element(self, count="", name=""):
        def del_element(instance):
            self.ids.list_one.remove_widget(self.ids[("boxlayout_" + name)])

        def sub_element(instance):
            self.ids[("label_count_" + name)].text = "[color=000000]" + str(int(self.ids[("label_count_" + name)].text[14:-8]) - 1) + "[/color]"
            if self.ids[("label_count_" + name)].text == "[color=000000]" + str(0) + "[/color]":
                del_element(1)

        def add_element(instance):
            self.ids[("label_count_" + name)].text = "[color=000000]" + str(int(self.ids[("label_count_" + name)].text[14:-8]) + 1) + "[/color]"
        if count.strip() == "":
            return
        if name.strip() == "":
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