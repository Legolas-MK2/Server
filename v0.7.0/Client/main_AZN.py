import threading

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivymd.uix.card import MDCard, MDSeparator
from kivy.core.window import Window
import datetime

from scit_client.client import Client

#Window.size = (800, 240)


class Element(MDCard):
    def __init__(self, **kwargs):
        super(Element, self).__init__(**kwargs)

    def delete_element(self):
        l = [["as", "Arbeitszeit Start"], ["ae", "Arbeitszeit Ende"]]

        msg = ""
        for feld in l:
            if not self.ids[feld[0]].text.strip():
                msg += "    " + feld[1] + "\n"

        if not msg:
            self.parent.remove_widget(self)
        else:
            Popup(title='Warnung', content=Label(text=f"fülle noch folgende felder aus:\n{msg}"), size_hint=(None, None), size=(400, 200)).open()


class MainWindow(Screen):
    pass


class SecondWindow(Screen):
    def __init__(self, **kwargs):
        self.overtime = 20
        super(SecondWindow, self).__init__(**kwargs)

        for d in range(5):
            da = (datetime.date.today() + datetime.timedelta(days=d)).__format__("%A %d-%b-%Y")
            self.spawn(da)

    def spawn(self, date):
        e = Element()
        e.ids["date"].text = str(date)
        self.ids.list.add_widget(e)

    @staticmethod
    def set_screen(screen_name):
        sm.transition.direction = "right"
        sm.current = screen_name


sm = ScreenManager()


class MyMainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.material_style = "M3"

        sm.add_widget(SecondWindow(name='second'))
        sm.add_widget(MainWindow(name='main'))
        self.title = 'Arbeitszeitnachweis'
        return sm

    def on_stop(self):
        if client:
            client.close()


def strat_client():
    global client

    client = Client(async_=True)
    print(1)
    client.set_name("a")


client: Client = None

if __name__ == "__main__":
    threading.Thread(target=strat_client).start()
    Builder.load_file("main_AZN.kv")
    MyMainApp().run()
    print("§")
    print(client)
    #t.daemon = False
    client.close()
