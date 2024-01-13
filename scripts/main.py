from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.screen import Screen
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty


# Set the app size
Window.size = (800, 700)


# Define our different screens


class LoginScreen(Screen):
    # login = ObjectProperty(None)
    # password = ObjectProperty(None)
    pass


class MenuScreen(Screen):
    pass


class SymptomsScreen(Screen):
    pass
    symptomsDT = ObjectProperty(None)

    def load_table(self):
        if self.symptomsDT == None:
            self.symptomsDT = MDDataTable(
                pos_hint={'center_x': 0.5, 'top': 1},
                size_hint=(1, 1),
                use_pagination=True,
                check=True,
                column_data=[
                    ("Название", dp(30)),
                    ("Да", dp(30)),
                    ("Нет", dp(30)),
                    ("Стр.", dp(30)), ],
                row_data=[
                    ("Кашель", "Антикашель", "ьлешаК", "1")
                    for i in range(3)], )
            self.ids.table_place.add_widget(self.symptomsDT)
        # else:
        #     last_num_row = int(self.symptomsDT.row_data[-1][0])
        #     self.symptomsDT.add_row(
        #         (str(last_num_row + 1), "1", "2", "3", '4'))

    def on_enter(self):
        Clock.schedule_once(self.change_screen)

    def change_screen(self, dt):
        self.load_table()


class Manager(ScreenManager):
    def change_screen(self, screen):
        self.current = screen


class HomeDoctor(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Orange'
        self.theme_cls.accent_palette = 'DeepPurple'
        return Builder.load_file('../kivy/main.kv')


if __name__ == '__main__':
    HomeDoctor().run()
