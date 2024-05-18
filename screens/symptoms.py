# from app import appInstance
from kivy.metrics import dp

from kivymd.uix.screen import Screen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDRectangleFlatButton

from kivy.clock import Clock

from utilities import database
from utilities.kivyutils import *


class SymptomsScreen(Screen):
    dialog = None

    def on_kv_post(self, base_widget):
        self.symptomsTable = None
        filters = ["ID", "Название", "Да", "Нет", "Страница"]
        self.filter = 1
        self.ids.filterButton.text = filters[self.filter][0]
        self.menu = MDDropdownMenu(
            header_cls=FilterMenuHeader(),
            caller=self.ids.filterButton,
            items=[
                {
                    "text": name,
                    "on_release": lambda x=(idx, name): self.menu_callback(x),
                }
                for idx, name in enumerate(filters)
            ],
        )

    def search(self, text):
        if len(text) > 0:
            print(text)
            res = list(
                filter(
                    lambda x: text.lower() in str(x[self.filter]).lower(),
                    self.symptomsTable.row_data,
                )
            )
            self.symptomsTable.row_data = sorted(res, key=lambda l: l[self.filter])
        else:
            self.symptomsTable.row_data = sorted(
                self.new_row_data, key=lambda l: l[self.filter]
            )
        # uncheck_all_rows(self.symptomsTable)

    def menu_callback(self, item):
        self.menu.dismiss()
        self.filter = int(item[0])
        self.ids.filterButton.text = item[1]
        self.symptomsTable.row_data = sorted(
            self.new_row_data, key=lambda l: l[self.filter]
        )
        print(self.filter)

    def dialog_help(self):
        if self.dialog:
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title="Помощь",
                text="Для изменения или удаления симптома нажмите на строку с нужным симптомом.\n\nДля фильтрации слов воспользуйтесь строкой поиска внизу экрана. Вы также можете выбрать фильтр кнопкой справа.",
                type="custom",
                buttons=[
                    MDRaisedButton(text="ОК", on_release=self.dialog_dismiss),
                ],
            )
            self.dialog.open()

    def add_symptom(self):
        # print(self.manager.screens)
        self.manager.change_screen("symptomAddEditScreen")
        # appInstance.change_title("Добавление симптома")
        self.manager.current_screen.new_symptom()

        print("ADD")

    def edit_symptom(self, id):
        self.manager.change_screen("symptomAddEditScreen")
        # appInstance.change_title("Редактирование симптома")
        self.manager.current_screen.load_symptom(id)
        print("EDIT")
        self.dialog.dismiss()
        self.dialog = None

    def dialog_dismiss(self, obj):
        self.dialog.dismiss()
        self.dialog = None

    def delete_symptom(self, id):
        with database.session_manager():
            database.delete_symptom(id=id)

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
                    title="Удаление",
                    text=f"Вы правда хотите удалить этот симптом?",
                    type="custom",
                    buttons=[
                        MDRaisedButton(text="ОТМЕНА", on_release=self.dialog_dismiss),
                        MDFlatButton(
                            text="УДАЛИТЬ", on_release=lambda x: self.delete_symptom(id)
                        ),
                    ],
                )
            else:
                self.dialog = MDDialog(
                    title="Воу воу, полегче",
                    text=f"Если в базе не останется как минимум три симптома, нужно будет вносить изменения через админку постгрес, мы этого не хотим.\nПросто отредактируйте симптомы.",
                    type="custom",
                    buttons=[
                        MDRaisedButton(text="ОК", on_release=self.dialog_dismiss),
                    ],
                )
            self.dialog.open()
        print("DELETE")

    def on_row_press(self, instance_table, instance_cell_row):
        index = instance_cell_row.index
        data = instance_table.table_data
        id = None
        cols_num = len(instance_table.column_data)
        if index % cols_num != 0:
            while index % cols_num:
                index -= 1
            row_obj = data.view_adapter.get_visible_view(index)
            if row_obj:
                id = int(row_obj.text)

        if self.dialog:
            self.dialog = None
        if not self.dialog and id:
            with database.session_manager():
                name = database.select_symptom(id=id).name
                self.dialog = MDDialog(
                    title=f'Выбран симптом "{name}"',
                    text=f"Выберите действие",
                    type="custom",
                    buttons=[
                        MDFlatButton(text="ОТМЕНА", on_release=self.dialog_dismiss),
                        MDRectangleFlatButton(
                            text="УДАЛИТЬ",
                            on_release=lambda x: self.dialog_delete_symptom(id),
                        ),
                        MDRaisedButton(
                            text="ИЗМЕНИТЬ", on_release=lambda x: self.edit_symptom(id)
                        ),
                    ],
                )
                self.dialog.open()

    def load_table(self):
        self.new_row_data = []
        with database.session_manager():
            for symptom in database.select_symptoms():
                self.new_row_data.append(symptom.tuple())

        if self.symptomsTable == None:
            self.symptomsTable = MDDataTable(
                pos_hint={"center_x": 0.5, "top": 1},
                size_hint=(1, 1),
                rows_num=10,
                # check=True,
                use_pagination=True,
                column_data=[
                    ("ID", dp(30)),
                    ("Название", dp(80)),
                    ("Да", dp(80)),
                    ("Нет", dp(80)),
                    ("Стр.", dp(30)),
                ],
            )
            # self.symptomsTable.bind(on_check_press=self.on_check)
            self.symptomsTable.bind(on_row_press=self.on_row_press)
            self.ids.table_place.add_widget(self.symptomsTable)
        self.symptomsTable.row_data = sorted(
            self.new_row_data, key=lambda l: l[self.filter]
        )
        uncheck_all_rows(self.symptomsTable)

    def on_enter(self):
        # appInstance.change_title("Симптомы")
        Clock.schedule_once(self.change_screen)

    def change_screen(self, dt):
        self.load_table()
