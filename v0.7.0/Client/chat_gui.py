from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import TwoLineListItem


class test(Screen):
    pass


class MainWindow(Screen):
    def __init__(self, chat, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        for i in range(31):
            element = TwoLineListItem()
            element.text = f"Der Name {i}"
            element.secondary_text = f"Message {i}"
            element.bind(on_release=self.open_chat)
            self.ids.main_contact.add_widget(element)

    @staticmethod
    def open_chat(_):
        sm.transition.direction = "left"
        sm.current = "chat"


class Chat(Screen):
    @staticmethod
    def set_screen(screen_name):
        sm.transition.direction = "right"
        sm.current = screen_name

    @staticmethod
    def me2():
        print(2)


sm = ScreenManager()
Builder.load_file("chat_gui.kv")


class MyMainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        #sm.add_widget(test(name="defsd"))
        sm.add_widget(Chat(name='chat'))
        sm.add_widget(MainWindow(test=" aljk", name='main'))

        return sm


if __name__ == "__main__":
    MyMainApp().run()