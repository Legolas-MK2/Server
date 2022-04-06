from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.uix.screen import Screen
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp

Window.size = (300, 500)

kv = """
<Tabelle>:
    MDDataTable:
        pos_hint:{'center_x': 0.5, 'center_y': 0.5}
        size_hint:(0.9, 0.6)
        check:True
        # rows_num:10
        column_data:[("No.", dp(18)), ("Food", dp(20)), ("Calories", dp(20))]
        row_data:[("1", "Burger", "300"), ("2", "Oats", "200"), ("3", "Oats", "200"), ("4", "Oats", "200")]

Screen:
    BoxLayout:
        orientation: "vertical"
        MDToolbar:
            title: "Einkaufapp"
            #left_action_items: [["coffee", lambda x: app.navigation_draw()]]
            #right_action_items: [["clock", lambda x: app.navigation_draw()]]
            elevation: 15
        MDLabel:
            text: "test text"
            halign: "center"
            
        MDDataTable:
            #check:True
            #rows_num:10
            column_data:[("No.", dp(18)), ("Food", dp(20)), ("Calories", dp(20))]
            row_data:[("1", "Burger", "300"), ("2", "Oats", "200"), ("3", "Oats", "200"), ("4", "Oats", "200")]
        
        MDBottomAppBar:
            MDToolbar:
                title: "Demo2"
                mode : "center"
                type: 'bottom'
                icon: "plus"
                on_action_button: app.add_element()
"""

class Tabelle(MDApp):
    def build(self):
        self.theme_cls.primary_palette = 'Teal'
        screen = Screen()
        self.data_table = MDDataTable(pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                      size_hint=(0.9, 0.6),
                                      check=True,
                                      # rows_num=10,
                                      column_data=[
                                          ("No.", dp(18)),
                                          ("Food", dp(20)),
                                          ("Calories", dp(20))
                                      ],
                                      row_data=[
                                          ("1", "Burger", "300"),
                                          ("2", "Oats", "200"),
                                          ("3", "Oats", "200"),
                                          ("4", "Oats", "200"),
                                          ("5", "Oats", "200"),
                                          ("6", "Oats", "200"),
                                          ("7", "Oats", "200"),
                                          ("8", "Oats", "200")

                                      ]
                                      )
        self.data_table.bind(on_row_press=self.on_row_press)
        self.data_table.bind(on_check_press=self.on_check_press)
        screen.add_widget(self.data_table)
        return screen

    def on_row_press(self, instance_table, instance_row):
        print(instance_table, instance_row, "on_row_press")

    def on_check_press(self, instance_table, current_row):
        print(instance_table, current_row, "on_check_press")
        self.data_tables.remove_row(instance_table)

    def navigation_draw(self):
        print("test")
        pass

    def add_element(self):
        print("Es wird was zur liste hinzugefügt")
        pass


class App(MDApp):
    def build(self):
        self.theme_cls.primary_palette = 'Teal'
        screen = Builder.load_string(kv)

        return screen

    def on_row_press(self, instance_table, instance_row):
        print(instance_table, instance_row, "on_row_press")

    def on_check_press(self, instance_table, current_row):
        print(instance_table, current_row, "on_check_press")
        self.data_tables.remove_row(instance_table)

    def navigation_draw(self):
        print("test")
        pass

    def add_element(self):
        print("Es wird was zur liste hinzugefügt")
        pass

App().run()