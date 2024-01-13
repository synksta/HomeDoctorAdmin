# from kivy.lang import Builder
# from kivymd.app import MDApp
# from kivy.core.window import Window
# from kivymd.uix.datatables import MDDataTable
# from kivymd.uix.screen import Screen
from kivy.clock import Clock
# from kivy.metrics import dp

# # Set the app size
# Window.size = (800, 700)


# class MyApp(MDApp):
#     def build(self):

#         self.theme_cls.theme_style = 'Dark'
#         self.theme_cls.primary_palette = 'Orange'
#         self.theme_cls.accent_palette = 'DeepPurple'

#         screen = Screen()

#         table = MDDataTable(
#             # Define Table
#             column_data=[
#                 ('First Name', dp(30)),
#                 ('Last Name', dp(30)),
#                 ('Email', dp(30)),
#                 ('Phone Number', dp(30))
#             ]
#         )

#         # return Builder.load_file('kv/datatables.kv')
#         return screen


# if __name__ == "__main__":
#     MyApp().run()


from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty


class ClientsTable(Screen):
    pass
    data_tables = ObjectProperty(None)

    def load_table(self):
        # layout = AnchorLayout()
        if self.data_tables == None:
            self.data_tables = MDDataTable(
                pos_hint={'center_y': 0.5, 'center_x': 0.5},
                size_hint=(0.9, 0.6),
                use_pagination=True,
                check=True,
                column_data=[
                    ("No.", dp(30)),
                    ("Head 1", dp(30)),
                    ("Head 2", dp(30)),
                    ("Head 3", dp(30)),
                    ("Head 4", dp(30)), ],
                row_data=[
                    (f"{i + 1}", "C", "C++", "JAVA", "Python")
                    for i in range(3)], )
            self.ids.bl.add_widget(self.data_tables)
        else:
            last_num_row = int(self.data_tables.row_data[-1][0])
            self.data_tables.add_row(
                (str(last_num_row + 1), "1", "2", "3", '4'))
        # return layout

    def on_enter(self):
        Clock.schedule_once(self.change_screen)

    def change_screen(self, dt):
        self.load_table()


class DemoPage(Screen):
    pass


class manager(ScreenManager):
    pass


class MainWindow(MDApp):
    def build(self):
        screen = Builder.load_file('kv/datatables.kv')
        return screen


if __name__ == "__main__":
    MainWindow().run()
