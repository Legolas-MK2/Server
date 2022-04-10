import kivy
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

Window.size = (300, 500)

Produkt_widget = {}
ii = 0
def callback(instance):
    print('The button <%s> is being pressed' % instance.text)

class Manager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def new_element(self, count="", name=""):
        if count.strip() == "":
            return
        if name.strip() == "":
            return
        boxlayout = BoxLayout()
        boxlayout.height = 35
        boxlayout.orientation = 'horizontal'

        boxlayout.add_widget(CheckBox(size_hint=(0.35, 1)))

        boxlayout.add_widget(Label(markup=True, text="[color=ff3333]" + str(name) + "[/color]"))

        textinput = TextInput(multiline=False, input_filter="int", text=count)

        boxlayout.add_widget(textinput)
        self.ids.list_one.add_widget(boxlayout)


class ScreenApp(MDApp):
    def build(self):
        return Manager()


Builder.load_file("Einkaufen GUI.kv")
if __name__ == "__main__":
    ScreenApp().run()