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
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivy.metrics import sp
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
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
    dialog = None

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
                filter(lambda x: text.lower() in x[self.filter].lower(), self.symptomsTable.row_data))
            self.symptomsTable.row_data = res
        else:
            self.symptomsTable.row_data = self.new_row_data

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

    def edit_symptom(self, id):
        self.manager.change_screen('symptomAddEditScreen')
        app.change_title('Редактирование симптома')
        self.manager.current_screen.load_symptom(id)
        print("EDIT")

    def dialog_delete_symptom(self, obj):
        dbcontrol.open_session()
        for row in self.checks:
            dbcontrol.delete_symptom(int(row[0]))
        dbcontrol.close_session()

        self.load_table()

        self.dialog.dismiss()
        self.dialog = None

        self.checks = []

    def dialog_dismiss(self, obj):
        self.dialog.dismiss()
        self.dialog = None

    def delete_symptom_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title='Удаление',
                text=f'Вы правда хотите удалить {len(self.checks)} симптомов?',
                type="custom",
                buttons=[
                    MDRaisedButton(
                        text="ОТМЕНА",
                        on_release=self.dialog_dismiss
                    ),
                    MDFlatButton(
                        text="УДАЛИТЬ",
                        on_release=self.dialog_delete_symptom
                    )
                ]
            )
            self.dialog.open()
        # dbcontrol.open_session()
        # for row in checked_rows:
        #     dbcontrol.delete_symptom(int(row[0]))

        # dbcontrol.close_session()

        # Удаление из БД
        # Обновление данных
        # Обновление таблицы
        print("DELETE")

    def on_check(self, instance_table, current_row):
        self.checks = instance_table.get_row_checks()
        print(self.checks)

        # If one row is selected, then we can edit or delete it
        if len(self.checks) == 1:
            if len(self.ids.topBar.right_action_items) < 3:
                self.ids.topBar.right_action_items.insert(
                    0,
                    ['delete', lambda x: self.delete_symptom_dialog(), 'Удалить']
                )
            if len(self.ids.topBar.right_action_items) < 4:
                self.ids.topBar.right_action_items.insert(
                    0,
                    ['pencil', lambda x, sid=int(self.checks[0][0]): self.edit_symptom(sid),
                     'Редактировать']
                )

        # If more than one row are selected, then we can only delete these
        elif len(self.checks) > 1:
            if len(self.ids.topBar.right_action_items) > 3:
                self.ids.topBar.right_action_items.pop(0)
        else:
            while (len(self.ids.topBar.right_action_items) > 2):
                self.ids.topBar.right_action_items.pop(0)

    def on_row_press(self, instance_table, instance_cell_row):
        if (instance_cell_row.index % len(instance_table.column_data) != 0):
            row = int(instance_cell_row.index/len(instance_table.column_data))
            id = int(instance_table.row_data[row][0])
            self.edit_symptom(id)

    def load_table(self):
        self.new_row_data = []
        dbcontrol.open_session()
        for symptom in dbcontrol.read_symptoms():
            self.new_row_data.append(symptom.tuple())
        dbcontrol.close_session()

        if self.symptomsTable == None:
            self.symptomsTable = MDDataTable(
                pos_hint={'center_x': 0.5, 'top': 1},
                size_hint=(1, 1),
                rows_num=len(self.new_row_data)*2,
                check=True,
                column_data=[
                    ("ID", dp(30)),
                    ("Название", dp(80)),
                    ("Да", dp(80)),
                    ("Нет", dp(80)),
                    ("Стр.", dp(30)), ],
            )
            self.symptomsTable.bind(on_check_press=self.on_check)
            self.symptomsTable.bind(on_row_press=self.on_row_press)
            self.ids.table_place.add_widget(self.symptomsTable)
        self.symptomsTable.row_data = self.new_row_data

    def on_enter(self):
        app.change_title('Симптомы')
        Clock.schedule_once(self.change_screen)

    def change_screen(self, dt):
        self.load_table()


class IconListItem(OneLineIconListItem):
    icon = StringProperty()


class YesNoMenuHeader(MDBoxLayout):

    data = None

    def search(self, text):
        if (self.data == None):
            self.data = self.parent.parent.items.copy()

        if (len(text) > 0):
            res = list(
                filter(lambda x: text.lower() in x.get('text').lower() or x.get('text') == 'Очистить', self.data))
            self.parent.parent.items = res
        else:
            self.parent.parent.items = self.data
        self.parent.parent.set_menu_properties()


class SymptomAddEditScreen(Screen):
    dialog = None

    symptom_id = 0
    symptom_name = ObjectProperty('')
    symptom_description = ObjectProperty('')
    symptom_yes_obj = None
    symptom_yes_name = ObjectProperty('Выбрать')
    symptom_no_obj = None
    symptom_no_name = ObjectProperty('Выбрать')
    symptom_page = ObjectProperty('')
    symptom_keywords_string = ObjectProperty('')
    symptom_keywords = []

    new_keywords = []

    all_keywords = []

    def new_symptom(self):
        self.symptom_id = 0
        self.symptom_name = ''
        self.symptom_description = ''
        self.symptom_yes_obj = None
        self.symptom_yes_name = 'Выбрать'
        self.symptom_no_obj = None
        self.symptom_no_name = 'Выбрать'
        self.symptom_page = ''
        self.symptom_keywords = []
        self.symptom_keywords_string = ""
        self.ids.keywordsInput.text = ""
        self.new_keywords = []
        dbcontrol.open_session()
        self.all_keywords = []
        for keyword in dbcontrol.read_keywords():
            self.all_keywords.append(keyword.word)
        dbcontrol.close_session()

    def load_symptom(self, id):
        dbcontrol.open_session()
        symptom = dbcontrol.get_symptom(id)

        self.symptom_id = symptom.id

        self.symptom_name = symptom.name

        if (symptom.description):
            self.symptom_description = symptom.description
        else:
            self.symptom_description = ''

        if (symptom.yes_obj):
            self.symptom_yes_obj = symptom.yes_obj
            self.symptom_yes_name = symptom.yes_obj.name
        else:
            self.symptom_yes_obj = None
            self.symptom_yes_name = 'Выбрать'

        if (symptom.no_obj):
            self.symptom_no_obj = symptom.no_obj
            self.symptom_no_name = symptom.no_obj.name
        else:
            self.symptom_no_obj = None
            self.symptom_no_name = 'Выбрать'

        if (symptom.page):
            self.symptom_page = str(symptom.page)
        else:
            self.symptom_page = ''

        self.symptom_keywords_string = dbcontrol.keywords_string(
            symptom.keywords)
        if self.symptom_keywords_string == "":
            self.ids.keywordsInput.text = ""

        self.symptom_keywords = []
        for keyword in dbcontrol.get_symptom(self.symptom_id).keywords:
            self.symptom_keywords.append(keyword)
        self.new_keywords = []
        self.all_keywords = []
        for keyword in dbcontrol.read_keywords():
            self.all_keywords.append(keyword.word)
        dbcontrol.close_session()

    def save(self):
        if not (('' or None in [
                self.symptom_name,
                self.symptom_description,
                self.symptom_page,
                self.symptom_no_obj,
                self.symptom_yes_obj
        ])) and self.symptom_page.isdigit():
            dbcontrol.open_session()

            if (self.symptom_id == 0):
                print('save new')
                dbcontrol.insert_symptom(
                    self.symptom_name,
                    self.symptom_description,
                    int(self.symptom_page),
                    self.symptom_yes_obj.id,
                    self.symptom_no_obj.id
                )

                self.new_keywords = [
                    x for x in self.symptom_keywords if x not in self.all_keywords]

                for keyword in self.new_keywords:
                    dbcontrol.insert_keyword(keyword)

                for keyword in self.symptom_keywords:
                    dbcontrol.insert_ref_keyword(
                        dbcontrol.get_symptom_by_name(
                            self.symptom_name).id,
                        dbcontrol.get_keyword_by_word(keyword).id
                    )

            else:
                dbcontrol.update_symptom(
                    self.symptom_id,
                    self.symptom_name,
                    self.symptom_description,
                    int(self.symptom_page),
                    self.symptom_yes_obj.id,
                    self.symptom_no_obj.id
                )

                actual_symptom_keywords = []
                for keyword in dbcontrol.get_symptom(self.symptom_id).keywords:
                    actual_symptom_keywords.append(keyword)

                keywords_to_delete = [
                    x for x in actual_symptom_keywords if x not in self.symptom_keywords]

                if len(keywords_to_delete) > 0:
                    for keyword in keywords_to_delete:
                        dbcontrol.delete_ref_keyword(
                            self.symptom_id, dbcontrol.get_keyword_by_word(keyword))

                actual_symptom_keywords = []
                for keyword in dbcontrol.get_symptom(self.symptom_id).keywords:
                    actual_symptom_keywords.append(keyword)

                self.symptom_keywords = [
                    x for x in self.symptom_keywords if x not in actual_symptom_keywords]

                self.new_keywords = [
                    x for x in self.symptom_keywords if x not in self.all_keywords]

                for keyword in self.new_keywords:
                    dbcontrol.insert_keyword(keyword)
                    dbcontrol.insert_ref_keyword(
                        self.symptom_id,
                        dbcontrol.get_keyword_by_word(keyword).id
                    )

            dbcontrol.session.commit()
            dbcontrol.close_session()
            return True
        else:
            if not self.dialog:
                self.dialog = MDDialog(
                    title='Ошибка',
                    text='Вы допустили ошибку при заполнении формы',
                    type="custom",
                    buttons=[
                        MDFlatButton(
                            text="ОК",
                            on_release=self.dialog_dismiss
                        )
                    ]
                )
            self.dialog.open()
            return False

    def dialog_dismiss(self, obj):
        self.dialog.dismiss()
        self.dialog = None

    def save_then_quit(self):
        if self.save():
            self.manager.change_screen('symptomsScreen')

    def save_then_add(self):
        self.save()
        app.change_title('Добавление симптома')
        self.new_symptom()
        print("ADD")
        pass

    def symptoms_yes_menu_gen(self):
        res = [
            {
                "viewclass": "IconListItem",
                "icon": "broom",
                'text': 'Очистить',
                'on_release': self.clear_yes_symptom
            }
        ]

        dbcontrol.open_session()

        for symptom in list(filter(lambda x: x.id != self.symptom_id, dbcontrol.read_symptoms())):
            res.append(
                {
                    'text': symptom.name,
                    "on_release": lambda x=symptom: self.yesMenu_callback(x),
                }
            )

        dbcontrol.close_session()

        return res

    def clear_yes_symptom(self):
        print('пылесос')
        self.yesMenu.dismiss()
        self.symptom_yes_name = 'Выбрать'
        self.symptom_yes_obj = None

    def symptoms_no_menu_gen(self):
        res = [
            {
                "viewclass": "IconListItem",
                "icon": "broom",
                'text': 'Очистить',
                'on_release': self.clear_no_symptom
            }
        ]

        dbcontrol.open_session()

        for symptom in list(filter(lambda x: x.id != self.symptom_id, dbcontrol.read_symptoms())):
            res.append(
                {
                    'text': symptom.name,
                    'on_release': lambda x=symptom: self.noMenu_callback(x),
                }
            )

        dbcontrol.close_session()

        return res

    def clear_no_symptom(self):
        self.noMenu.dismiss()
        self.symptom_no_name = 'Выбрать'
        self.symptom_no_obj = None

    def on_enter(self):
        self.yes_menu_items = self.symptoms_yes_menu_gen()

        self.no_menu_items = self.symptoms_no_menu_gen()

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
        self.yesMenu.items = list(
            filter(lambda x: x.get('text') not in (self.symptom_yes_name, self.symptom_no_name), self.yes_menu_items.copy()))

        self.yesMenu.set_menu_properties()
        self.menu_set_header(self.yesMenu)
        self.set_focus_yes()

    def prepare_menu_no(self):

        self.noMenu.items = list(
            filter(lambda x: x.get('text') not in (self.symptom_yes_name, self.symptom_no_name), self.no_menu_items.copy()))

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

    def yesMenu_callback(self, x):

        self.yesMenu.dismiss()
        self.symptom_yes_name = x.name
        self.symptom_yes_obj = x

    def noMenu_callback(self, x):
        self.noMenu.dismiss()
        self.symptom_no_name = x.name
        self.symptom_no_obj = x

    # KEYWORDS
    flag = False

    def keywords_enter(self, text):
        def find_common(list1, list2):
            return sum(map(lambda x: x in list1 and x in list2, list1))
        if (len(text) > 0):
            flag = True
            if (flag):
                parsed_list = list(set(re.split(
                    '\\s*\,+\\s*', re.sub('\,*$', '', text).lower().strip())))
                if '' in parsed_list:
                    parsed_list.remove('')
                if ',' in parsed_list:
                    parsed_list.remove(',')

                print(parsed_list)
                common = find_common(parsed_list, self.all_keywords)
                # print(self.all_keywords)
                self.ids.keywordsInput.helper_text = f'В базе есть {
                    common} введенных слов, {len(parsed_list) - common} будет добавлено'
                self.symptom_keywords = parsed_list
        else:
            self.symptom_keywords = []
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
        if not (new in self.screen_history):
            self.transition.direction = 'left'
            self.screen_history.append(new)
        else:
            self.transition.direction = 'right'
            for screen in reversed(self.screen_history):
                if screen != new:
                    print(self.screen_history)
                    self.screen_history.remove(screen)
                else:
                    break
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
