from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import OneLineListItem
from kivy.clock import Clock
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
            text: 'List maker button'
            on_release: root.new_element()

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

        ScrollView:
            MDList:
                id: list_two

        MDRaisedButton:
            text: 'Go Back'
            on_release:
                app.root.current = 'firstwindow'
                root.manager.transition.direction = 'down'
"""




class FirstWindow(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.create_list)

    def create_list(self, *args):
        for i in range(20):
            pass
            #self.ids.list_one.add_widget(OneLineListItem(text=f'List Item {i}'))

    # But adding widgets doesn't happen automatically
    # I tried variations but the variable is always not defined
    # self.ids.list_one.add_widget(OneLineListItem(text='List Item 1'))
    # root.ids.list_one.add_widget(OneLineListItem(text='List Item 1'))
    # ids.list_one.add_widget(OneLineListItem(text='List Item 1'))

    # This function works when called from a button
    def new_element(self,menge = 3466):
        #for i in range(0, 41, 2):
        boxlayout = BoxLayout()
        boxlayout.height = 35
        boxlayout.orientation = 'horizontal'
        checkbox = CheckBox()
        button = Button(text=str(menge))
        boxlayout.add_widget(button)
        button = Button(text=str(menge*4763))
        boxlayout.add_widget(button)
        self.ids.list_one.add_widget(boxlayout)

class SecondWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class MultiscreenApp(MDApp):
    def build(self):
        return Builder.load_string(kv)


if __name__ == '__main__':
    MultiscreenApp().run()
