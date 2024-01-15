from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.screen import Screen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty


# Set the app size
Window.size = (800, 700)


# Define our different screens


class LoginScreen(Screen):

    def on_enter(self):
        app.change_title('Вход')


class MenuScreen(Screen):

    def on_enter(self):
        app.change_title('Меню')


class FilterMenuHeader(MDBoxLayout):
    '''An instance of the class that will be added to the menu header.'''


class SymptomsScreen(Screen):
    table_data = [
        ('0', "Кашель", "Антикашель", "ьлешаК", "1"),
        ('1', "Антикашель", "Антикашель", "ьлешаК", "2"),
        ('2', "ьлешаК", "Антикашель", "ьлешаК", "1"),
        ('3', "Кашель", "Антикашель", "ьлешаК", "1"),
        ('4', "Антикашель", "Антикашель", "ьлешаК", "2"),
        ('5', "ьлешаК", "Антикашель", "ьлешаК", "1"),
    ]

    def on_kv_post(self, base_widget):

        self.symptomsTable = None
        filter_menu_items = [
            {
                "text": 'ID',
                "on_release": lambda x=['0', 'ID']: self.menu_callback(x),
            },
            {
                "text": 'Название',
                "on_release": lambda x=['1', 'Название']: self.menu_callback(x),
            },
            {
                "text": 'Да',
                "on_release": lambda x=['2', 'Да']: self.menu_callback(x),
            },
            {
                "text": 'Нет',
                "on_release": lambda x=['3', 'Нет']: self.menu_callback(x),
            },
            {
                "text": 'Страница',
                "on_release": lambda x=['4', 'Страница']: self.menu_callback(x),
            },
            {
                "text": 'Ключевые слова',
                "on_release": lambda x=['5', 'Ключевые слова']: self.menu_callback(x),
            },
        ]

        self.filter = 1
        self.ids.filterButton.text = 'Название'

        self.menu = MDDropdownMenu(
            header_cls=FilterMenuHeader(),
            caller=self.ids.filterButton,
            items=filter_menu_items,
        )

    def search(self, text):
        if (len(text) > 0):
            print(text)
            res = list(
                filter(lambda x: text in x[self.filter], self.table_data))
            self.symptomsTable.row_data = res
        else:
            self.symptomsTable.row_data = self.table_data

    def menu_callback(self, item):
        self.menu.dismiss()
        self.filter = int(item[0])
        self.ids.filterButton.text = item[1]
        print(self.filter)

    def help_popup(self):
        print("HELP")

    def add_symptom(self):
        # print(self.manager.screens)
        self.manager.change_screen('symptomAddEditScreen')
        self.manager.current_screen.symptom = 'watafaks'
        app.change_title('Добавление симптома')
        print(self.manager.current_screen.symptom)
        print("ADD")

    def delete_symptom(self):
        print("DELETE")

    def edit_symptom(self):
        print("EDIT")

    def on_check(self, instance_table, current_row):
        checks = instance_table.get_row_checks()

        # print(len(self.ids.topBar.right_action_items))
        print(checks)

        # If one row is selected, then we can edit or delete it
        if len(checks) == 1:
            if len(self.ids.topBar.right_action_items) < 3:
                self.ids.topBar.right_action_items.insert(
                    0,
                    ['delete', lambda x: self.delete_symptom(), 'Удалить']
                )
            if len(self.ids.topBar.right_action_items) < 4:
                self.ids.topBar.right_action_items.insert(
                    0,
                    ['pencil', lambda x: self.edit_symptom(), 'Редактировать']
                )

        # If more than one row are selected, then we can only delete these
        elif len(checks) > 1:
            if len(self.ids.topBar.right_action_items) > 3:
                self.ids.topBar.right_action_items.pop(0)
        else:
            while (len(self.ids.topBar.right_action_items) > 2):
                self.ids.topBar.right_action_items.pop(0)

        # print(instance_table.get_row_checks())

    def load_table(self):
        if self.symptomsTable == None:
            self.symptomsTable = MDDataTable(
                pos_hint={'center_x': 0.5, 'top': 1},
                size_hint=(1, 1),
                use_pagination=True,
                check=True,
                column_data=[
                    ("ID", dp(30)),
                    ("Название", dp(30)),
                    ("Да", dp(30)),
                    ("Нет", dp(30)),
                    ("Стр.", dp(30)), ],
                row_data=self.table_data
                # for i in range(3)],
            )
            self.symptomsTable.bind(on_check_press=self.on_check)
            self.ids.table_place.add_widget(self.symptomsTable)
        # else:
        #     last_num_row = int(self.symptomsTable.row_data[-1][0])
        #     self.symptomsTable.add_row(
        #         (str(last_num_row + 1), "1", "2", "3", '4'))

    def on_enter(self):
        app.change_title('Симптомы')
        Clock.schedule_once(self.change_screen)

    def change_screen(self, dt):
        self.load_table()


class SymptomAddEditScreen(Screen):
    symptom = ObjectProperty('')
    title = ObjectProperty('')


class Manager(ScreenManager):

    def change_screen(self, new):
        self.transition.direction = 'left'
        self.prev = self.current
        self.current = new

    def change_screen_to_prev(self):
        self.transition.direction = 'right'
        self.current = self.previous()


class HomeDoctor(MDApp):
    appname = 'ДД Админ'

    def change_title(self, new):
        self.title = f'{self.appname} - {new}'

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Orange'
        self.theme_cls.accent_palette = 'DeepPurple'
        return Builder.load_file('../kivy/main.kv')


app = HomeDoctor()
if __name__ == '__main__':
    app.run()
