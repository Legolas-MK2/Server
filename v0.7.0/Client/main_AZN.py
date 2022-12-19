from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.pickers import MDTimePicker
from kivy.core.window import Window
Window.size = (800, 190)
class Element(Screen):
    def time_picker(self):
        dialog = MDTimePicker(on_cancel=self.cancel, time=self.set_time)
        dialog.open()

    def cancel(self, a, time):
        print(str(time))
        self.ids.btn.text = str(time)

    def set_time(self, a, time):
        print(str(time))
        self.ids.btn.text = str(time)


class MainWindow(Screen):
    pass


class SecondWindow(Screen):
    pass


sm = ScreenManager()
Builder.load_file("main_AZN.kv")


class MyMainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        sm.add_widget(Element(name='e'))
        sm.add_widget(MainWindow(name='main'))
        sm.add_widget(SecondWindow(name='second'))
        return sm


if __name__ == "__main__":
    MyMainApp().run()