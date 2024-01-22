import time
import re
from kivy.config import Config
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.screen import Screen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import MDSnackbar
from kivy.metrics import dp
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
import dbcontrol


# Set the app size
Window.size = (800, 700)


# Define our different screens

class CustomSnackbar(MDSnackbar):
    text = StringProperty(None)
    icon = StringProperty(None)
    font_size = NumericProperty("15sp")


class LoginScreen(Screen):
    name = StringProperty('')
    password = StringProperty('')

    def on_kv_post(self, base_widget):
        self.manager.screen_history.append(self.name)

    def on_enter(self):
        # print(self.ids.nameField.text)  # = ''
        # self.ids.passwordField.text = ''
        app.change_title('Вход')

    def login(self):
        name = self.ids.nameField.text.strip()
        password = self.ids.passwordField.text.strip()

        if len(name) > 0 and len(password) > 0:

            dbcontrol.open_session()
            current_user = None
            for user in dbcontrol.read_users():
                if name == user.name:
                    current_user = user
                    break
            if current_user:
                if password == current_user.password:
                    self.manager.change_screen('menuScreen')
                else:
                    CustomSnackbar(
                        text="Пароль не подходит!",
                        icon="alert-box",
                        snackbar_x="10dp",
                        snackbar_y="10dp",
                    ).open()
            else:
                CustomSnackbar(
                    text="Такого пользователя нет!",
                    icon="alert-box",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                ).open()
        else:
            if len(name) == 0:
                self.ids.nameField.hint_text_color_normal = 'red'
            if len(password) == 0:
                self.ids.passwordField.hint_text_color_normal = 'red'


class MenuScreen(Screen):
    def on_enter(self):
        app.change_title('Меню')


class FilterMenuHeader(MDBoxLayout):
    '''An instance of the class that will be added to the menu header.'''


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
                filter(lambda x: text.lower() in str(x[self.filter]).lower(), self.symptomsTable.row_data))
            self.symptomsTable.row_data = sorted(
                res, key=lambda l: l[self.filter])
        else:
            self.symptomsTable.row_data = sorted(
                self.new_row_data, key=lambda l: l[self.filter])
        # uncheck_all_rows(self.symptomsTable)

    def menu_callback(self, item):
        self.menu.dismiss()
        self.filter = int(item[0])
        self.ids.filterButton.text = item[1]
        self.symptomsTable.row_data = sorted(
            self.new_row_data, key=lambda l: l[self.filter])
        print(self.filter)

    def dialog_help(self):
        if self.dialog:
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title='Помощь',
                text='Для изменения или удаления симптома нажмите на строку с нужным симптомом.\n\nДля фильтрации слов воспользуйтесь строкой поиска внизу экрана. Вы также можете выбрать фильтр кнопкой справа.',
                type="custom",
                buttons=[
                    MDRaisedButton(
                        text="ОК",
                        on_release=self.dialog_dismiss
                    ),
                ]
            )
            self.dialog.open()

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
        self.dialog.dismiss()
        self.dialog = None

    def dialog_dismiss(self, obj):
        self.dialog.dismiss()
        self.dialog = None

    def delete_symptom(self, id):
        dbcontrol.open_session()
        dbcontrol.delete_symptom(id)
        dbcontrol.close_session()
        self.load_table()
        self.dialog.dismiss()
        self.dialog = None

    def dialog_delete_symptom(self, id):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog:
            if len(self.new_row_data) > 3:
                self.dialog = MDDialog(
                    title='Удаление',
                    text=f'Вы правда хотите удалить этот симптом?',
                    type="custom",
                    buttons=[
                        MDRaisedButton(
                            text="ОТМЕНА",
                            on_release=self.dialog_dismiss
                        ),
                        MDFlatButton(
                            text="УДАЛИТЬ",
                            on_release=lambda x: self.delete_symptom(id)
                        )
                    ]
                )
            else:
                self.dialog = MDDialog(
                    title='Воу воу, полегче',
                    text=f'Если в базе не останется как минимум три симптома, нужно будет вносить изменения через админку постгрес, мы этого не хотим.\nПросто отредактируйте симптомы.',
                    type="custom",
                    buttons=[
                        MDRaisedButton(
                            text="ОК",
                            on_release=self.dialog_dismiss
                        ),
                    ]
                )
            self.dialog.open()
        print("DELETE")

    # def on_check(self, instance_table, current_row):
    #     self.checks = instance_table.get_row_checks()
    #     print(self.checks)

    #     # If one row is selected, then we can edit or delete it
    #     if len(self.checks) == 1:
    #         if len(self.ids.topBar.right_action_items) < 3:
    #             self.ids.topBar.right_action_items.insert(
    #                 0,
    #                 ['delete', lambda x: self.dialog_delete_symptom(), 'Удалить']
    #             )
    #         if len(self.ids.topBar.right_action_items) < 4:
    #             self.ids.topBar.right_action_items.insert(
    #                 0,
    #                 ['pencil', lambda x: self.edit_symptom(int(self.checks[0][0])),
    #                  'Редактировать']
    #             )

    #     # If more than one row are selected, then we can only delete these
    #     elif len(self.checks) > 1:
    #         if len(self.ids.topBar.right_action_items) > 3:
    #             self.ids.topBar.right_action_items.pop(0)
    #     else:
    #         while (len(self.ids.topBar.right_action_items) > 2):
    #             self.ids.topBar.right_action_items.pop(0)

    def on_row_press(self, instance_table, instance_cell_row):
        index = instance_cell_row.index
        data = instance_table.table_data
        id = None
        cols_num = len(instance_table.column_data)
        if (index % cols_num != 0):
            while index % cols_num:
                index -= 1
            row_obj = data.view_adapter.get_visible_view(index)
            if row_obj:
                id = int(row_obj.text)

        if self.dialog:
            self.dialog = None
        if not self.dialog and id:

            dbcontrol.open_session()
            name = dbcontrol.get_symptom(id).name
            dbcontrol.close_session()

            self.dialog = MDDialog(
                title=f'Выбран симптом "{name}"',
                text=f'Выберите действие',
                type="custom",
                buttons=[
                    MDFlatButton(
                        text="ОТМЕНА",
                        on_release=self.dialog_dismiss
                    ),
                    MDRectangleFlatButton(
                        text="УДАЛИТЬ",
                        on_release=lambda x: self.dialog_delete_symptom(id)
                    ),
                    MDRaisedButton(
                        text="ИЗМЕНИТЬ",
                        on_release=lambda x: self.edit_symptom(id)
                    ),
                ]
            )
            self.dialog.open()

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
                rows_num=10,
                # check=True,
                use_pagination=True,
                column_data=[
                    ("ID", dp(30)),
                    ("Название", dp(80)),
                    ("Да", dp(80)),
                    ("Нет", dp(80)),
                    ("Стр.", dp(30)), ],
            )
            # self.symptomsTable.bind(on_check_press=self.on_check)
            self.symptomsTable.bind(on_row_press=self.on_row_press)
            self.ids.table_place.add_widget(self.symptomsTable)
        self.symptomsTable.row_data = sorted(
            self.new_row_data, key=lambda l: l[self.filter])
        uncheck_all_rows(self.symptomsTable)

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

    def on_pre_enter(self):
        dbcontrol.open_session()
        self.all_keywords = []
        for keyword in dbcontrol.read_keywords():
            self.all_keywords.append(keyword.word)
        dbcontrol.close_session()

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
        self.yes_menu_items = self.symptoms_yes_menu_gen()
        self.no_menu_items = self.symptoms_no_menu_gen()

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
            self.symptom_keywords.append(keyword.word)

    def save(self):
        if not (('' or None in [
                self.symptom_name,
                self.symptom_description,
                self.symptom_page,
                # self.symptom_no_obj,
                # self.symptom_yes_obj
        ])) and self.symptom_page.isdigit():
            dbcontrol.open_session()

            if (self.symptom_id == 0):
                print('save new')
                dbcontrol.insert_symptom(
                    self.symptom_name.strip(),
                    self.symptom_description.strip(),
                    int(self.symptom_page.strip()),
                )

                if self.symptom_no_obj:
                    dbcontrol.get_symptom_by_name(
                        self.symptom_name).no = self.symptom_no_obj.id
                    dbcontrol.session.commit()

                if self.symptom_yes_obj:
                    dbcontrol.get_symptom_by_name(
                        self.symptom_name).yes = self.symptom_yes_obj.id
                    dbcontrol.session.commit()

                new_keywords = [
                    x for x in self.symptom_keywords if x not in self.all_keywords]

                for keyword in new_keywords:
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
                    # self.symptom_yes_obj.id,
                    # self.symptom_no_obj.id
                )

                if self.symptom_no_obj:
                    dbcontrol.get_symptom_by_name(
                        self.symptom_name).no = self.symptom_no_obj.id
                    dbcontrol.session.commit()

                if self.symptom_yes_obj:
                    dbcontrol.get_symptom_by_name(
                        self.symptom_name).yes = self.symptom_yes_obj.id
                    dbcontrol.session.commit()

                print(f'Введенные ключи:\n{self.symptom_keywords}')
                actual_keywords = []
                for keyword in dbcontrol.get_symptom(self.symptom_id).keywords:
                    actual_keywords.append(keyword.word)

                print(f'Прошлые ключи:\n{actual_keywords}')

                keywords_to_delete = [
                    x for x in actual_keywords if x not in self.symptom_keywords]

                print(f'Отвязанные ключи:\n{keywords_to_delete}')

                new_keywords = [
                    x for x in self.symptom_keywords if x not in self.all_keywords]

                for keyword in new_keywords:
                    dbcontrol.insert_keyword(keyword)

                print(f'Новые ключи:\n{new_keywords}')

                new_to_symptom_keywords = [
                    x for x in self.symptom_keywords if x not in actual_keywords]

                for keyword in new_to_symptom_keywords:
                    dbcontrol.insert_ref_keyword(
                        self.symptom_id,
                        dbcontrol.get_keyword_by_word(keyword).id
                    )

                print(f'Новые ключи для сипмтома:\n{new_to_symptom_keywords}')

                if len(keywords_to_delete) > 0:
                    for keyword in keywords_to_delete:
                        dbcontrol.delete_ref_keyword(
                            self.symptom_id, dbcontrol.get_keyword_by_word(keyword).id)

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
        if self.save():
            app.change_title('Добавление симптома')
            self.new_symptom()

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
    def keywords_enter(self, text):
        def find_common(list1, list2):
            res = 0
            for item in list1:
                if item in list2:
                    res += 1
            return res
            # return sum(map(lambda x: x in list1 and x in list2, list1))
        if (len(text) > 0):
            parsed_list = list(set(re.split(
                '\\s*,+\\s*', re.sub(',*$', '', text).lower().strip())))
            if '' in parsed_list:
                parsed_list.remove('')
            if ',' in parsed_list:
                parsed_list.remove(',')
            common = find_common(parsed_list, self.all_keywords)
            self.ids.keywordsInput.helper_text = f'В базе есть {
                common} введенных слов, {len(parsed_list) - common} будет добавлено'
            self.symptom_keywords = parsed_list
        else:
            self.ids.keywordsInput.helper_text = "Вводите через запятую (Можно с пробелами)"


class AddEditKeywordDialog_Content(MDBoxLayout):
    pass


def list_of_unique(l):
    n = []
    for i in l:
        if i not in n:
            n.append(i)
    return n


def uncheck_all_rows(table: MDDataTable):
    def deselect_rows(*args):
        table.table_data.select_all('normal')
    Clock.schedule_once(deselect_rows)


def update_checks(table: MDDataTable, checked_collection, obj=None):

    if (checked_collection):
        uncheck_all_rows(table)

        def action(*args):
            data = table.table_data
            for i in range(0, len(data.recycle_data), data.total_col_headings):
                row_obj = data.view_adapter.get_visible_view(i)
                if row_obj:
                    data.on_mouse_select(row_obj)
                    if list(table.row_data[row_obj.index//data.total_col_headings]) in checked_collection:
                        row_obj.ids.check.state = 'down'
                        # print('\n')
                        # print(f'{row_obj.index//2}:')
                        # print(table.row_data[row_obj.index//2])
                    else:
                        row_obj.ids.check.state = 'normal'

                # Clock.schedule_once(update_row)

        Clock.schedule_once(action)

        # def get_checks(*args):
        #     # obj.checks = list(set(checked_collection + table.get_row_checks()))
        #     new_checked_collection = table.get_row_checks()
        #     print('\n\n\nBEFORE:')
        #     print(checked_collection)
        #     print('\nAFTER:')
        #     print(new_checked_collection)
        #     global checks
        #     checks = list_of_unique(
        #         checked_collection + new_checked_collection)

        # Clock.schedule_once(get_checks)


class KeywordsScreen(Screen):
    dialog = None
    checks = []

    def on_kv_post(self, base_widget):
        self.wordsTable = None

    # def on_leave(self):
        # uncheck_all_rows(self.wordsTable)

    def search(self, text):
        if (len(text) > 0):
            res = list(
                filter(lambda x: text.lower() in x[1].lower(), self.new_row_data))
            self.wordsTable.row_data = sorted(
                res, key=lambda l: l[0])
        else:
            self.wordsTable.row_data = sorted(
                self.new_row_data, key=lambda l: l[0])

        # update_checks(self.wordsTable, self.checks, self)
        # uncheck_all_rows(self.wordsTable)
        # self.wordsTable.table_data.select_all('normal')

    def dialog_add_keyword(self):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title='Добавление ключевого слова',
                type="custom",
                content_cls=AddEditKeywordDialog_Content(),
                buttons=[
                    MDFlatButton(
                        text="ОТМЕНИТЬ",
                        on_release=self.dialog_dismiss
                    ),
                    MDRaisedButton(
                        text="ДОБАВИТЬ",
                        on_release=self.add_keyword
                    )
                ]
            )
        self.dialog.open()

    def add_keyword(self, obj):
        new_word = self.dialog.content_cls.ids.wordField.text.strip()
        if (len(new_word) > 0):
            dbcontrol.open_session()
            dbcontrol.insert_keyword(new_word)
            dbcontrol.close_session()
            self.dialog.dismiss()
            self.dialog = None
            self.load_table()
        else:
            self.dialog.content_cls.ids.wordField.hint_text = "Поле не может быть пустым"
            self.dialog.content_cls.ids.wordField.hint_text_color_normal = "red"

    def on_row_press(self, instance_table, instance_cell_row):
        index = instance_cell_row.index
        data = instance_table.table_data
        cols_num = len(instance_table.column_data)
        id = None
        if (index % cols_num != 0):
            while index % cols_num:
                index -= 1
            row_obj = data.view_adapter.get_visible_view(index)
            if row_obj:
                id = int(row_obj.text)

        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog and id:
            dbcontrol.open_session()
            word = dbcontrol.get_keyword(id).word
            dbcontrol.close_session()
            self.dialog = MDDialog(
                title=f'Выбрано слово "{word}"',
                text=f'Выберите действие',
                type="custom",
                buttons=[
                    MDFlatButton(
                        text="ОТМЕНА",
                        on_release=self.dialog_dismiss
                    ),
                    MDRectangleFlatButton(
                        text="УДАЛИТЬ",
                        on_release=lambda x: self.dialog_delete_keyword(id)
                    ),
                    MDRaisedButton(
                        text="ИЗМЕНИТЬ",
                        on_release=lambda x: self.dialog_edit_keyword(id)
                    ),
                ]
            )
            self.dialog.open()

    def dialog_edit_keyword(self, id):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title='Изменение ключевого слова',
                type="custom",
                content_cls=AddEditKeywordDialog_Content(),
                buttons=[
                    MDFlatButton(
                        text="ОТМЕНИТЬ",
                        on_release=self.dialog_dismiss
                    ),
                    MDRaisedButton(
                        text="CОХРАНИТЬ",
                        on_release=lambda x: self.edit_keyword(id)
                    )
                ]
            )
        dbcontrol.open_session()
        self.dialog.content_cls.ids.wordField.text = dbcontrol.get_keyword(
            id).word
        dbcontrol.close_session()
        self.dialog.open()

    def edit_keyword(self, id):
        new_word = self.dialog.content_cls.ids.wordField.text.strip()
        # print(self.dialog.content_cls.ids.wordField.text)
        if (len(new_word) > 0):
            dbcontrol.open_session()
            dbcontrol.update_keyword(id, new_word)
            dbcontrol.close_session()
            self.dialog.dismiss()
            self.dialog = None
            self.load_table()
        else:
            self.dialog.content_cls.ids.wordField.hint_text = "Поле не может быть пустым"
            self.dialog.content_cls.ids.wordField.hint_text_color_normal = "red"

    def dialog_delete_keyword(self, id):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title='Удаление',
                text=f'Вы правда хотите удалить это ключевое слово?',
                type="custom",
                buttons=[
                    MDRaisedButton(
                        text="ОТМЕНА",
                        on_release=self.dialog_dismiss
                    ),
                    MDFlatButton(
                        text="УДАЛИТЬ",
                        on_release=lambda x: self.delete_keyword(id)
                    )
                ]
            )
            self.dialog.open()

    def delete_keyword(self, id):
        dbcontrol.open_session()
        dbcontrol.delete_keyword(id)
        dbcontrol.close_session()
        # uncheck_all_rows(self.wordsTable)
        self.load_table()
        self.dialog.dismiss()
        self.dialog = None

    def dialog_dismiss(self, obj):
        self.dialog.dismiss()
        self.dialog = None

    def dialog_help(self):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title='Помощь',
                text='Для изменения или удаления ключевого слова нажмите на строку с нужным словом.\n\nДля фильтрации слов воспользуйтесь строкой поиска внизу экрана.',
                type="custom",
                buttons=[
                    MDRaisedButton(
                        text="ОК",
                        on_release=self.dialog_dismiss
                    ),
                ]
            )
            self.dialog.open()

    # def on_check(self, instance_table, current_row):
    #     def update(*args):
    #         # if len(instance_table.row_data) < len(self.new_row_data):
    #         for row in instance_table.row_data:
    #             row = list(row)
    #             if row in instance_table.get_row_checks():
    #                 if row not in self.checks:
    #                     self.checks.append(row)
    #             elif row in self.checks:
    #                 print('гуй')
    #                 self.checks.remove(row)
    #         # else:
    #         #     self.checks = instance_table.get_row_checks()
    #         print('\nТЫК')
    #         print(self.checks)

    #     def update_menu(*args):
    #         # If one row is selected, then we can edit or delete it
    #         if len(self.checks) == 1:
    #             if len(self.ids.topBar.right_action_items) < 3:
    #                 self.ids.topBar.right_action_items.insert(
    #                     0,
    #                     ['delete', lambda x: self.dialog_delete_keyword(),
    #                         'Удалить']
    #                 )
    #             if len(self.ids.topBar.right_action_items) < 4:
    #                 self.ids.topBar.right_action_items.insert(
    #                     0,
    #                     ['pencil', lambda x: self.dialog_edit_keyword(
    #                         int(self.checks[0][0])), 'Редактировать']
    #                 )

    #         # If more than one row are selected, then we can only delete these
    #         elif len(self.checks) > 1:
    #             if len(self.ids.topBar.right_action_items) > 3:
    #                 self.ids.topBar.right_action_items.pop(0)
    #         else:
    #             while (len(self.ids.topBar.right_action_items) > 2):
    #                 self.ids.topBar.right_action_items.pop(0)

    #     Clock.schedule_once(update)
    #     Clock.schedule_once(update_menu)

    def load_table(self):
        self.new_row_data = []
        dbcontrol.open_session()
        for keyword in dbcontrol.read_keywords():
            self.new_row_data.append(keyword.tuple())
        dbcontrol.close_session()

        # print(self.new_row_data)

        if self.wordsTable == None:
            self.wordsTable = MDDataTable(
                pos_hint={'center_x': 0.5, 'top': 1},
                size_hint=(1, 1),
                rows_num=10,
                # check=True,
                use_pagination=True,
                column_data=[
                    ("ID", dp(50)),
                    ("Слово", dp(50)),
                ],
            )
            # self.wordsTable.bind(on_check_press=self.on_check)
            self.wordsTable.bind(on_row_press=self.on_row_press)
            self.ids.table_place.add_widget(self.wordsTable)

        self.wordsTable.row_data = sorted(
            self.new_row_data, key=lambda l: l[0])

        # self.wordsTable.table_data.select_all('normal')

    def on_enter(self):
        app.change_title('Ключевые слова')
        if self.wordsTable:
            uncheck_all_rows(self.wordsTable)
        Clock.schedule_once(self.change_screen)

    def change_screen(self, dt):
        self.load_table()


class AddEditUserDialog_Content(MDBoxLayout):
    pass


class UsersScreen(Screen):
    new_row_data = []

    dialog = None

    def on_kv_post(self, base_widget):
        self.usersTable = None

    def search(self, text):
        if (len(text) > 0):
            # print(text)
            res = list(
                filter(lambda x: text.lower() in x[0].lower(), self.new_row_data))
            self.usersTable.row_data = res
        else:
            self.usersTable.row_data = self.new_row_data

    def dialog_add_user(self):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
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
                        on_release=self.add_user
                    )
                ]
            )
        self.dialog.open()

    def add_user(self, obj):
        name = self.dialog.content_cls.ids.loginField.text.strip()
        password = self.dialog.content_cls.ids.passwordField.text.strip()
        if (len(name) > 0 and len(password) > 0):
            dbcontrol.open_session()
            dbcontrol.insert_user(name, password)
            dbcontrol.close_session()
            self.dialog.dismiss()
            self.dialog = None
            self.load_table()
        else:
            if len(name) == 0:
                self.dialog.content_cls.ids.loginField.hint_text = "Поле не может быть пустым"
                self.dialog.content_cls.ids.loginField.hint_text_color_normal = "red"
            if len(password) == 0:
                self.dialog.content_cls.ids.passwordField.hint_text = "Поле не может быть пустым"
                self.dialog.content_cls.ids.passwordField.hint_text_color_normal = "red"

    def on_row_press(self, instance_table, instance_cell_row):
        index = instance_cell_row.index
        data = instance_table.table_data
        cols_num = len(instance_table.column_data)
        name = None
        if (index % cols_num != 0):
            while index % cols_num:
                index -= 1
            row_obj = data.view_adapter.get_visible_view(index)
            if row_obj:
                name = row_obj.text

        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog and name:
            self.dialog = MDDialog(
                title=f'Выбран пользователь "{name}"',
                text=f'Выберите действие',
                type="custom",
                buttons=[
                    MDFlatButton(
                        text="ОТМЕНА",
                        on_release=self.dialog_dismiss
                    ),
                    MDRectangleFlatButton(
                        text="УДАЛИТЬ",
                        on_release=lambda x: self.dialog_delete_user(name)
                    ),
                    MDRaisedButton(
                        text="ИЗМЕНИТЬ",
                        on_release=lambda x: self.dialog_edit_user(name)
                    ),
                ]
            )
            self.dialog.open()

    def dialog_edit_user(self, name):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title='Изменение пользователя',
                type="custom",
                content_cls=AddEditKeywordDialog_Content(),
                buttons=[
                    MDFlatButton(
                        text="ОТМЕНИТЬ",
                        on_release=self.dialog_dismiss
                    ),
                    MDRaisedButton(
                        text="CОХРАНИТЬ",
                        on_release=lambda x: self.edit_user(name)
                    )
                ]
            )
        self.dialog.content_cls.ids.wordField.hint_text = "Пароль"
        dbcontrol.open_session()
        self.dialog.content_cls.ids.wordField.text = dbcontrol.get_user(
            name).password
        dbcontrol.close_session()
        self.dialog.open()

    def edit_user(self, name):

        new_password = self.dialog.content_cls.ids.wordField.text.strip()
        # print(self.dialog.content_cls.ids.wordField.text)
        if (len(new_password) > 0):
            dbcontrol.open_session()
            dbcontrol.update_user_password(name, new_password)
            dbcontrol.close_session()
            self.dialog.dismiss()
            self.dialog = None
            self.load_table()
        else:
            self.dialog.content_cls.ids.wordField.hint_text = "Поле не может быть пустым"
            self.dialog.content_cls.ids.wordField.hint_text_color_normal = "red"

    def dialog_delete_user(self, name):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title='Удаление',
                text=f'Вы правда хотите удалить этого пользователя?',
                type="custom",
                buttons=[
                    MDRaisedButton(
                        text="ОТМЕНА",
                        on_release=self.dialog_dismiss
                    ),
                    MDFlatButton(
                        text="УДАЛИТЬ",
                        on_release=lambda x: self.delete_user(name)
                    )
                ]
            )
            self.dialog.open()

    def delete_user(self, name):
        dbcontrol.open_session()
        dbcontrol.delete_user(name)
        dbcontrol.close_session()
        # uncheck_all_rows(self.wordsTable)
        self.load_table()
        self.dialog.dismiss()
        self.dialog = None

    def dialog_help(self):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title='Помощь',
                text='Для изменения или удаления данных пользователя нажмите на строку с нужным пользователем.\n\nДля фильтрации пользователей воспользуйтесь строкой поиска внизу экрана.',
                type="custom",
                buttons=[
                    MDRaisedButton(
                        text="ОК",
                        on_release=self.dialog_dismiss
                    ),
                ]
            )
            self.dialog.open()

    # def on_check(self, instance_table, current_row):
    #     checks = instance_table.get_row_checks()
    #     # print(len(self.ids.topBar.right_action_items))
    #     print(checks)

    #     # If one row is selected, then we can edit or delete it
    #     if len(checks) == 1:
    #         if len(self.ids.topBar.right_action_items) < 3:
    #             self.ids.topBar.right_action_items.insert(
    #                 0,
    #                 ['delete', lambda x: self.delete_user(), 'Удалить']
    #             )
    #         if len(self.ids.topBar.right_action_items) < 4:
    #             self.ids.topBar.right_action_items.insert(
    #                 0,
    #                 ['pencil', lambda x: self.edit_user(), 'Редактировать']
    #             )

    #     # If more than one row are selected, then we can only delete these
    #     elif len(checks) > 1:
    #         if len(self.ids.topBar.right_action_items) > 3:
    #             self.ids.topBar.right_action_items.pop(0)
    #     else:
    #         while (len(self.ids.topBar.right_action_items) > 2):
    #             self.ids.topBar.right_action_items.pop(0)

    #     # print(instance_table.get_row_checks())

    def load_table(self):

        self.new_row_data = []
        dbcontrol.open_session()
        for user in dbcontrol.read_users():
            self.new_row_data.append(user.tuple())
        dbcontrol.close_session()

        if self.usersTable == None:
            self.usersTable = MDDataTable(
                pos_hint={'center_x': 0.5, 'top': 1},
                size_hint=(1, 1),
                use_pagination=True,
                rows_num=10,
                column_data=[
                    ("Логин", dp(50)),
                    ("Пароль", dp(50)),
                ],

            )
            # self.usersTable.bind(on_check_press=self.on_check)
            self.usersTable.bind(on_row_press=self.on_row_press)
            self.ids.table_place.add_widget(self.usersTable)

        self.usersTable.row_data = sorted(
            self.new_row_data, key=lambda l: l[0])

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
        self.icon = '../data/images/medical-bag.png'
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Orange'
        self.theme_cls.accent_palette = 'DeepPurple'
        return Builder.load_file('../kivy/main.kv')


app = HomeDoctor()

if __name__ == '__main__':
    app.run()
