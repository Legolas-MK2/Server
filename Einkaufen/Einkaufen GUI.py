from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.checkbox import CheckBox

Window.size = (300, 500)

kv = """
WindowManager:
    FirstWindow:
        name: 'firstwindow'
    SecondWindow:
        name: 'secondwindow'


<FirstWindow>:
    BoxLayout:
        orientation: 'vertical'

        MDToolbar:
            title: 'SCREEN 1'

        Button:
            size_hint: 1,0.1
            on_release: root.new_element(6,"Nudeln")

        ScrollView:
            MDList:
                id: list_one

        MDFloatingActionButton:
            elevation: 8
            icon: 'plus'
            pos_hint: {'center_x': .5}
            on_press:
                app.root.current = 'secondwindow'
                root.manager.transition.direction = 'up'

<SecondWindow>:
    BoxLayout:
        orientation: 'vertical'

        MDToolbar:
            title: 'Neues Element'

        BoxLayout:
            orientation: 'vertical'
            Label:
                text: "Menge"
                color: 0,0,0,1
                size_hint: 1,0.1
            
            TextInput:
                pos_hint: {"center_x": .5, "center_y": .5}
                multiline: False
                size_hint: 0.9,0.15
                
            BoxLayout:
                size_hint: 1,0.15
                orientation: "horizontal"
                Button:
                    text: "1"
                Button:
                    text: "2"
                Button:
                    text: "3"
                Button:
                    text: "4"
                Button:
                    text: "5"
                Button:
                    text: "6"
                Button:
                    text: "7"
            Label:
                size_hint: 1,0.1
            Label:
                text: "Produkt"
                color: 0,0,0,1
                size_hint: 1,0.1
            TextInput:
                pos_hint: {"center_x": .5, "center_y": .5}
                multiline: False
                size_hint: 0.9,0.15
            MDList:
                id: list_Produkt
            Label:
        
        
        MDFloatingActionButton:
            icon: "android"
            md_bg_color: app.theme_cls.primary_color
            pos_hint: {"center_x": .1, "center_y": .5}
            on_release:
                app.root.current = 'firstwindow'
                root.manager.transition.direction = 'down'
                
        MDFloatingActionButton:
            icon: "plus"
            pos_hint: {"center_x": .5, "center_y": .5}
            md_bg_color: app.theme_cls.primary_color
            on_release:
                root.add()
                app.root.current = 'firstwindow'
                root.manager.transition.direction = 'down'
"""

Itemlist = {}

class FirstWindow(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("aaaaaaaaaaaaaaaa")
    def build(self):
        print("build")

    def new_element(self, menge=5, name="Bananne"):
        boxlayout = BoxLayout()
        boxlayout.height = 35
        boxlayout.orientation = 'horizontal'

        boxlayout.add_widget(CheckBox(size_hint=(0.35, 1)))

        boxlayout.add_widget(Label(markup=True, text="[color=ff3333]"+str(name)+"[/color]"))

        boxlayout.add_widget(Button(text=str(menge)))

        self.ids.list_one.add_widget(boxlayout)
FirstWindowi = FirstWindow()
class SecondWindow(Screen):
    def add(self):
        print("add")



class WindowManager(ScreenManager):
    pass


class MultiscreenApp(MDApp):
    def build(self):
        return Builder.load_string(kv)

    def app(self):
        print("Edbhugiotga937")
        pass


if __name__ == '__main__':
    MultiscreenApp().run()
