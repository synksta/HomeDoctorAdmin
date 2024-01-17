import time
import re
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.screen import Screen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty
import dbcontrol


# Set the app size
Window.size = (800, 700)


# Define our different screens


class LoginScreen(Screen):
    def on_kv_post(self, base_widget):
        self.manager.screen_history.append(self.name)

    def on_enter(self):
        app.change_title('Вход')


class MenuScreen(Screen):
    def on_enter(self):
        app.change_title('Меню')


class FilterMenuHeader(MDBoxLayout):
    '''An instance of the class that will be added to the menu header.'''


symptoms_data = [
    ('0', "Кашель", "Антикашель", "ьлешаК", "1"),
    ('1', "Антикашель", "Антикашель", "ьлешаК", "2"),
    ('2', "ьлешаК", "Антикашель", "ьлешаК", "1"),
    ('3', "Кашель", "Антикашель", "ьлешаК", "1"),
    ('4', "Антикашель", "Антикашель", "ьлешаК", "2"),
    ('5', "ьлешаК", "Антикашель", "ьлешаК", "1"),
]


class SymptomsScreen(Screen):

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
        app.change_title('Добавление симптома')
        self.manager.current_screen.new_symptom()

        print("ADD")

    def edit_symptom(self, sid):
        self.manager.change_screen('symptomAddEditScreen')
        app.change_title('Редактирование симптома')
        self.manager.current_screen.load_symptom(symptoms_data[sid])
        print(self.manager.current_screen.symptom_id)
        print(self.manager.current_screen.symptom_name)
        print(self.manager.current_screen.symptom_yes)
        print(self.manager.current_screen.symptom_no)
        print(self.manager.current_screen.symptom_page)
        print("EDIT")

    def delete_symptom(self):
        # Удаление из БД
        # Обновление данных
        # Обновление таблицы
        print("DELETE")

    def on_check(self, instance_table, current_row):
        checks = instance_table.get_row_checks()
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
                    ['pencil', lambda x, sid=int(checks[0][0]): self.edit_symptom(sid),
                     'Редактировать']
                )

        # If more than one row are selected, then we can only delete these
        elif len(checks) > 1:
            if len(self.ids.topBar.right_action_items) > 3:
                self.ids.topBar.right_action_items.pop(0)
        else:
            while (len(self.ids.topBar.right_action_items) > 2):
                self.ids.topBar.right_action_items.pop(0)

        # print(instance_table.get_row_checks())

    def on_row_press(self, instance_table, instance_cell_row):
        row = int(instance_cell_row.index/len(instance_table.column_data))
        sid = int(instance_table.row_data[row][0])
        self.edit_symptom(sid)

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
                row_data=symptoms_data
                # for i in range(3)],
            )
            self.symptomsTable.bind(on_check_press=self.on_check)
            self.symptomsTable.bind(on_row_press=self.on_row_press)
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


class YesNoMenuHeader(MDBoxLayout):

    data = None

    def search(self, text):
        if (self.data == None):
            self.data = self.parent.parent.items.copy()

        if (len(text) > 0):
            res = list(
                filter(lambda x: text.lower() in x.get('text').lower(), self.data))
            self.parent.parent.items = res
        else:
            self.parent.parent.items = self.data
        self.parent.parent.set_menu_properties()
        # if (len(text) > 0):
        #     data = self.parent.parent.items
        #     print(text)
        #     res = list(
        #         filter(lambda x: text.lower() in x.get('text').lower(), data))
        #     self.parent.parent.items = res
        #     print(res)
        # self.symptomsTable.row_data = res
        # else:
        #     self.symptomsTable.row_data = self.table_data
        # print(text)


class SymptomAddEditScreen(Screen):
    symptom = None
    symptom_id = ObjectProperty('')
    symptom_name = ObjectProperty('')
    symptom_yes = ObjectProperty('')
    symptom_no = ObjectProperty('')
    symptom_page = ObjectProperty('')

    def new_symptom(self):
        self.symptom_id = ''
        self.symptom_name = ''
        self.symptom_yes = 'Выбрать'
        self.symptom_no = 'Выбрать'
        self.symptom_page = ''

    def load_symptom(self, symptom):
        self.symptom_id = symptom[0]
        self.symptom_name = symptom[1]
        self.symptom_yes = symptom[2]
        self.symptom_no = symptom[3]
        self.symptom_page = symptom[4]

    def save(self):
        print('SAVE')
        pass

    def save_then_quit(self):
        self.save()
        self.manager.change_screen('symptomsScreen')
        pass

    def save_then_add(self):
        self.save()
        app.change_title('Добавление симптома')
        self.new_symptom()
        print("ADD")
        pass

    def on_enter(self):
        self.yes_menu_items = [
            {
                "text": 'ID',
                "on_release": lambda x=['0', 'ID']: self.yesMenu_callback(x),
            },
            {
                "text": 'Название',
                "on_release": lambda x=['1', 'Название']: self.yesMenu_callback(x),
            },
            {
                "text": 'Да',
                "on_release": lambda x=['2', 'Да']: self.yesMenu_callback(x),
            },
            {
                "text": 'Нет',
                "on_release": lambda x=['3', 'Нет']: self.yesMenu_callback(x),
            },
            {
                "text": 'Страница',
                "on_release": lambda x=['4', 'Страница']: self.yesMenu_callback(x),
            },


        ]

        self.no_menu_items = [
            {
                "text": 'Ключевые слова',
                "on_release": lambda x=['5', 'Ключевые слова']: self.noMenu_callback(x),
            },
            {
                "text": 'Ключевые слова',
                "on_release": lambda x=['5', 'Ключевые слова']: self.noMenu_callback(x),
            },
            {
                "text": 'Ключевые слова',
                "on_release": lambda x=['5', 'Ключевые слова']: self.noMenu_callback(x),
            },
            {
                "text": 'Ключевые слова',
                "on_release": lambda x=['5', 'Ключевые слова']: self.noMenu_callback(x),
            },

        ]

        self.yesMenu = MDDropdownMenu(
            caller=self.ids.yesButton,
            header_cls=MDBoxLayout()
        )

        self.noMenu = MDDropdownMenu(
            caller=self.ids.noButton,
            header_cls=MDBoxLayout()
        )

    def menu_set_header(self, menu):
        if len(menu.items) > 4:
            if menu.header_cls.__class__.__name__ != 'YesNoMenuHeader':
                menu.header_cls = YesNoMenuHeader()
        else:
            menu.header_cls = MDBoxLayout()

    def prepare_menu_yes(self):
        self.yesMenu.items = self.yes_menu_items.copy()
        self.yesMenu.set_menu_properties()
        self.menu_set_header(self.yesMenu)
        self.set_focus_yes()

    def prepare_menu_no(self):
        self.noMenu.items = self.no_menu_items.copy()
        self.noMenu.set_menu_properties()
        self.menu_set_header(self.noMenu)
        self.set_focus_no()

    def set_focus_yes(self):
        if (self.yesMenu.header_cls.__class__.__name__ == 'YesNoMenuHeader'):
            if len(self.yesMenu.header_cls.ids) > 0:
                self.yesMenu.header_cls.ids.searchField.focus = True
                self.yesMenu.header_cls.ids.searchField.text = ''
            else:
                self.yesMenu.dismiss()

    def set_focus_no(self):
        if (self.noMenu.header_cls.__class__.__name__ == 'YesNoMenuHeader'):
            if len(self.noMenu.header_cls.ids) > 0:
                self.noMenu.header_cls.ids.searchField.focus = True
                self.noMenu.header_cls.ids.searchField.text = ''
            else:
                self.noMenu.dismiss()

    def yesMenu_callback(self, item):
        self.yesMenu.dismiss()
        self.ids.yesButton.text = item[1]

    def noMenu_callback(self, item):
        self.noMenu.dismiss()
        self.ids.noButton.text = item[1]

    # KEYWORDS

    keywords_list = [
        'внимание',
        'ребята',
        'домашнее',
        'задание',
    ]

    def keywords_enter(self, text):
        def find_common(list1, list2): return sum(
            map(lambda x: x in list1 and x in list2, list1))

        if (len(text) > 0):
            parsed_list = re.split('\,* \\s*', re.sub('\,*$', '', text))
            common = find_common(parsed_list, self.keywords_list)
            self.ids.keywordsInput.helper_text = f'В базе есть {
                common} введенных слов, {len(parsed_list) - common} будет добавлено'
        else:
            self.ids.keywordsInput.helper_text = "Вводите через запятую (Можно с пробелами)"


class KeywordsScreen(Screen):

    table_data = [
        ('0', "кхе кхе"),
        ('1', "ай больно в ноге"),
        ('2', "ломает, соли - срочно соли"),
    ]

    def on_kv_post(self, base_widget):
        self.wordsTable = None

    def search(self, text):
        if (len(text) > 0):
            print(text)
            res = list(
                filter(lambda x: text in x[1], self.table_data))
            self.wordsTable.row_data = res
        else:
            self.wordsTable.row_data = self.table_data

    def help_popup(self):
        print("HELP")

    def add_user(self):
        print("ADD")

    def delete_user(self):
        print("DELETE")

    def edit_user(self):
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
                    ['delete', lambda x: self.delete_user(), 'Удалить']
                )
            if len(self.ids.topBar.right_action_items) < 4:
                self.ids.topBar.right_action_items.insert(
                    0,
                    ['pencil', lambda x: self.edit_user(), 'Редактировать']
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
        if self.wordsTable == None:
            self.wordsTable = MDDataTable(
                pos_hint={'center_x': 0.5, 'top': 1},
                size_hint=(1, 1),
                use_pagination=True,
                check=True,
                column_data=[
                    ("ID", dp(50)),
                    ("Слово", dp(50)),
                ],
                row_data=self.table_data
            )
            self.wordsTable.bind(on_check_press=self.on_check)

            self.ids.table_place.add_widget(self.wordsTable)

    def on_enter(self):
        app.change_title('Ключевые слова')
        Clock.schedule_once(self.change_screen)

    def change_screen(self, dt):
        self.load_table()


class AddEditUserDialog_Content(MDBoxLayout):
    pass


class UsersScreen(Screen):
    dialog = None

    table_data = [
        ('user0', "qwerty"),
        ('user1', "qwerty123"),
        ('user2', "qwerty123456"),
    ]

    def on_kv_post(self, base_widget):
        self.usersTable = None

    def search(self, text):
        if (len(text) > 0):
            print(text)
            res = list(
                filter(lambda x: text in x[0], self.table_data))
            self.usersTable.row_data = res
        else:
            self.usersTable.row_data = self.table_data

    def on_row_press(self, instance_table, instance_cell_row):
        row = int(instance_cell_row.index/len(instance_table.column_data))
        # uid = int(instance_table.row_data[row][0])
        self.edit_user(row)

    def help_popup(self):
        print("HELP")

    def delete_user(self):
        print("DELETE")

    def on_check(self, instance_table, current_row):
        checks = instance_table.get_row_checks()
        # print(len(self.ids.topBar.right_action_items))
        print(checks)

        # If one row is selected, then we can edit or delete it
        if len(checks) == 1:
            if len(self.ids.topBar.right_action_items) < 3:
                self.ids.topBar.right_action_items.insert(
                    0,
                    ['delete', lambda x: self.delete_user(), 'Удалить']
                )
            if len(self.ids.topBar.right_action_items) < 4:
                self.ids.topBar.right_action_items.insert(
                    0,
                    ['pencil', lambda x: self.edit_user(), 'Редактировать']
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
        if self.usersTable == None:
            self.usersTable = MDDataTable(
                pos_hint={'center_x': 0.5, 'top': 1},
                size_hint=(1, 1),
                use_pagination=True,
                check=True,
                column_data=[
                    ("Логин", dp(50)),
                    ("Пароль", dp(50)),
                ],
                row_data=self.table_data
            )
            self.usersTable.bind(on_check_press=self.on_check)
            self.usersTable.bind(on_row_press=self.on_row_press)
            self.ids.table_place.add_widget(self.usersTable)

    def add_user(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title='Добавление пользователя',
                type="custom",
                content_cls=AddEditUserDialog_Content(),
                buttons=[
                    MDFlatButton(
                        text="ОТМЕНИТЬ",
                        on_release=self.dialog_dismiss
                    ),
                    MDRaisedButton(
                        text="ДОБАВИТЬ",
                        on_release=self.dialog_add_user
                    )
                ]
            )
        self.dialog.open()

    def dialog_add_user(self, obj):
        print(self.dialog.content_cls.ids.loginField.text)
        print(self.dialog.content_cls.ids.passwordField.text)
        self.dialog.dismiss()
        self.dialog = None

    def edit_user(self, uid):
        if not self.dialog:
            self.dialog = MDDialog(
                title='Изменение пользователя',
                type="custom",
                content_cls=AddEditUserDialog_Content(),
                buttons=[
                    MDFlatButton(
                        text="ОТМЕНИТЬ",
                        on_release=self.dialog_dismiss
                    ),
                    MDRaisedButton(
                        text="CОХРАНИТЬ",
                        on_release=self.dialog_edit_user
                    )
                ]
            )
        self.dialog.content_cls.ids.loginField.text = self.table_data[uid][0]
        self.dialog.content_cls.ids.passwordField.text = self.table_data[uid][1]
        self.dialog.open()

    def dialog_edit_user(self, obj):
        print(self.dialog.content_cls.ids.loginField.text)
        print(self.dialog.content_cls.ids.passwordField.text)
        self.dialog.dismiss()
        self.dialog = None

    def dialog_dismiss(self, obj):
        self.dialog.dismiss()
        self.dialog = None

    def on_enter(self):
        app.change_title('Пользователи')
        Clock.schedule_once(self.change_screen)

    def change_screen(self, dt):
        self.load_table()


class Manager(ScreenManager):

    screen_history = []

    def change_screen(self, new):
        # if (self.screen_names.index(self.current) < self.screen_names.index(new)):
        self.transition.direction = 'left'
        self.screen_history.append(new)
        # else:
        #     self.transition.direction = 'right'
        # self.prev = self.current
        self.current = new

    def change_screen_to_prev(self):
        if len(self.screen_history) > 0:
            self.transition.direction = 'right'
            self.screen_history.pop(-1)
            self.current = self.screen_history[-1]


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
