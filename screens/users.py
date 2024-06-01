# from app import appInstance


from kivy.metrics import dp
from kivy.clock import Clock

from kivymd.uix.screen import Screen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog

from utilities import database
from utilities.kivyutils import *


class AddEditUserDialog_Content(MDBoxLayout):
    pass


class UsersScreen(Screen):
    new_row_data = []

    dialog = None

    def on_kv_post(self, base_widget):
        self.usersTable = None

    def search(self, text):
        if len(text) > 0:
            # print(text)
            res = list(
                filter(lambda x: text.lower() in x[0].lower(), self.new_row_data)
            )
            self.usersTable.row_data = res
        else:
            self.usersTable.row_data = self.new_row_data

    def dialog_add_user(self):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title="Добавление пользователя",
                type="custom",
                content_cls=AddEditUserDialog_Content(),
                buttons=[
                    MDFlatButton(text="ОТМЕНИТЬ", on_release=self.dialog_dismiss),
                    MDRaisedButton(text="ДОБАВИТЬ", on_release=self.add_user),
                ],
            )
        self.dialog.open()

    def add_user(self, obj):
        name = self.dialog.content_cls.ids.loginField.text.strip()
        password = self.dialog.content_cls.ids.passwordField.text.strip()
        if len(name) > 0 and len(password) > 0:
            with database.session_manager():
                database.insert_user(name=name, password=password)
            self.dialog.dismiss()
            self.dialog = None
            self.load_table()
        else:
            if len(name) == 0:
                self.dialog.content_cls.ids.loginField.hint_text = (
                    "Поле не может быть пустым"
                )
                self.dialog.content_cls.ids.loginField.hint_text_color_normal = "red"
            if len(password) == 0:
                self.dialog.content_cls.ids.passwordField.hint_text = (
                    "Поле не может быть пустым"
                )
                self.dialog.content_cls.ids.passwordField.hint_text_color_normal = "red"

    def on_row_press(self, instance_table, instance_cell_row):
        index = instance_cell_row.index
        data = instance_table.table_data
        cols_num = len(instance_table.column_data)
        name = None
        if index % cols_num != 0:
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
                text=f"Выберите действие",
                type="custom",
                buttons=[
                    MDFlatButton(text="ОТМЕНА", on_release=self.dialog_dismiss),
                    MDRectangleFlatButton(
                        text="УДАЛИТЬ",
                        on_release=lambda x: self.dialog_delete_user(name),
                    ),
                    MDRaisedButton(
                        text="ИЗМЕНИТЬ",
                        on_release=lambda x: self.dialog_edit_user(name),
                    ),
                ],
            )
            self.dialog.open()

    def dialog_edit_user(self, name):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title="Изменение пользователя",
                type="custom",
                content_cls=EditDialog_Content(),
                buttons=[
                    MDFlatButton(text="ОТМЕНИТЬ", on_release=self.dialog_dismiss),
                    MDRaisedButton(
                        text="CОХРАНИТЬ", on_release=lambda x: self.edit_user(name)
                    ),
                ],
            )
        self.dialog.content_cls.ids.wordField.hint_text = "Пароль"
        with database.session_manager():
            self.dialog.content_cls.ids.wordField.text = database.get_user_by_name(
                name
            ).password
        self.dialog.open()

    def edit_user(self, name):

        new_password = self.dialog.content_cls.ids.wordField.text.strip()
        # print(self.dialog.content_cls.ids.wordField.text)
        if new_password:
            with database.session_manager():
                database.update_user(name=name, new_password=new_password)
            self.dialog.dismiss()
            self.dialog = None
            self.load_table()
        else:
            self.dialog.content_cls.ids.wordField.hint_text = (
                "Поле не может быть пустым"
            )
            self.dialog.content_cls.ids.wordField.hint_text_color_normal = "red"

    def dialog_delete_user(self, name):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title="Удаление",
                text=f"Вы правда хотите удалить этого пользователя?",
                type="custom",
                buttons=[
                    MDRaisedButton(text="ОТМЕНА", on_release=self.dialog_dismiss),
                    MDFlatButton(
                        text="УДАЛИТЬ", on_release=lambda x: self.delete_user(name)
                    ),
                ],
            )
            self.dialog.open()

    def delete_user(self, name):
        with database.session_manager():
            database.delete_user(name)
        self.load_table()
        self.dialog.dismiss()
        self.dialog = None

    def dialog_help(self):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title="Помощь",
                text="Для изменения или удаления данных пользователя нажмите на строку с нужным пользователем.\n\nДля фильтрации пользователей воспользуйтесь строкой поиска внизу экрана.",
                type="custom",
                buttons=[
                    MDRaisedButton(text="ОК", on_release=self.dialog_dismiss),
                ],
            )
            self.dialog.open()

    def load_table(self):

        self.new_row_data = []
        with database.session_manager():
            for user in database.select_users():
                self.new_row_data.append(user.tuple())

        if self.usersTable == None:
            self.usersTable = MDDataTable(
                pos_hint={"center_x": 0.5, "top": 1},
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

        self.usersTable.row_data = sorted(self.new_row_data, key=lambda l: l[0])

    def dialog_dismiss(self, obj):
        self.dialog.dismiss()
        self.dialog = None

    def on_enter(self):
        # appInstance.change_title("Пользователи")
        Clock.schedule_once(self.change_screen)

    def change_screen(self, dt):
        self.load_table()
