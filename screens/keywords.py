# from app import appInstance

from kivy.metrics import dp
from kivy.clock import Clock

from kivymd.uix.screen import Screen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog

from utilities import dbcontrol
from utilities.kivyutils import *


class KeywordsScreen(Screen):
    dialog = None
    checks = []

    def on_kv_post(self, base_widget):
        self.wordsTable = None

    # def on_leave(self):
    # uncheck_all_rows(self.wordsTable)

    def search(self, text):
        if len(text) > 0:
            res = list(
                filter(lambda x: text.lower() in x[1].lower(), self.new_row_data)
            )
            self.wordsTable.row_data = sorted(res, key=lambda l: l[0])
        else:
            self.wordsTable.row_data = sorted(self.new_row_data, key=lambda l: l[0])

        # update_checks(self.wordsTable, self.checks, self)
        # uncheck_all_rows(self.wordsTable)
        # self.wordsTable.table_data.select_all('normal')

    def dialog_add_keyword(self):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title="Добавление ключевого слова",
                type="custom",
                content_cls=AddEditKeywordDialog_Content(),
                buttons=[
                    MDFlatButton(text="ОТМЕНИТЬ", on_release=self.dialog_dismiss),
                    MDRaisedButton(text="ДОБАВИТЬ", on_release=self.add_keyword),
                ],
            )
        self.dialog.open()

    def add_keyword(self, obj):
        new_word = self.dialog.content_cls.ids.wordField.text.strip()
        if len(new_word) > 0:
            dbcontrol.open_session()
            dbcontrol.insert_keyword(new_word)
            dbcontrol.close_session()
            self.dialog.dismiss()
            self.dialog = None
            self.load_table()
        else:
            self.dialog.content_cls.ids.wordField.hint_text = (
                "Поле не может быть пустым"
            )
            self.dialog.content_cls.ids.wordField.hint_text_color_normal = "red"

    def on_row_press(self, instance_table, instance_cell_row):
        index = instance_cell_row.index
        data = instance_table.table_data
        cols_num = len(instance_table.column_data)
        id = None
        if index % cols_num != 0:
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
                text=f"Выберите действие",
                type="custom",
                buttons=[
                    MDFlatButton(text="ОТМЕНА", on_release=self.dialog_dismiss),
                    MDRectangleFlatButton(
                        text="УДАЛИТЬ",
                        on_release=lambda x: self.dialog_delete_keyword(id),
                    ),
                    MDRaisedButton(
                        text="ИЗМЕНИТЬ",
                        on_release=lambda x: self.dialog_edit_keyword(id),
                    ),
                ],
            )
            self.dialog.open()

    def dialog_edit_keyword(self, id):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title="Изменение ключевого слова",
                type="custom",
                content_cls=AddEditKeywordDialog_Content(),
                buttons=[
                    MDFlatButton(text="ОТМЕНИТЬ", on_release=self.dialog_dismiss),
                    MDRaisedButton(
                        text="CОХРАНИТЬ", on_release=lambda x: self.edit_keyword(id)
                    ),
                ],
            )
        dbcontrol.open_session()
        self.dialog.content_cls.ids.wordField.text = dbcontrol.get_keyword(id).word
        dbcontrol.close_session()
        self.dialog.open()

    def edit_keyword(self, id):
        new_word = self.dialog.content_cls.ids.wordField.text.strip()
        if len(new_word) > 0:
            dbcontrol.open_session()
            dbcontrol.update_keyword(id, new_word)
            dbcontrol.close_session()
            self.dialog.dismiss()
            self.dialog = None
            self.load_table()
        else:
            self.dialog.content_cls.ids.wordField.hint_text = (
                "Поле не может быть пустым"
            )
            self.dialog.content_cls.ids.wordField.hint_text_color_normal = "red"

    def dialog_delete_keyword(self, id):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not self.dialog:
            self.dialog = MDDialog(
                title="Удаление",
                text=f"Вы правда хотите удалить это ключевое слово?",
                type="custom",
                buttons=[
                    MDRaisedButton(text="ОТМЕНА", on_release=self.dialog_dismiss),
                    MDFlatButton(
                        text="УДАЛИТЬ", on_release=lambda x: self.delete_keyword(id)
                    ),
                ],
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
                title="Помощь",
                text="Для изменения или удаления ключевого слова нажмите на строку с нужным словом.\n\nДля фильтрации слов воспользуйтесь строкой поиска внизу экрана.",
                type="custom",
                buttons=[
                    MDRaisedButton(text="ОК", on_release=self.dialog_dismiss),
                ],
            )
            self.dialog.open()

    def load_table(self):
        self.new_row_data = []
        dbcontrol.open_session()
        for keyword in dbcontrol.read_keywords():
            self.new_row_data.append(keyword.tuple())
        dbcontrol.close_session()

        if self.wordsTable == None:
            self.wordsTable = MDDataTable(
                pos_hint={"center_x": 0.5, "top": 1},
                size_hint=(1, 1),
                rows_num=10,
                use_pagination=True,
                column_data=[
                    ("ID", dp(50)),
                    ("Слово", dp(50)),
                ],
            )
            self.wordsTable.bind(on_row_press=self.on_row_press)
            self.ids.table_place.add_widget(self.wordsTable)

        self.wordsTable.row_data = sorted(self.new_row_data, key=lambda l: l[0])

    def on_enter(self):
        # appInstance.change_title("Ключевые слова")
        if self.wordsTable:
            uncheck_all_rows(self.wordsTable)
        Clock.schedule_once(self.change_screen)

    def change_screen(self, dt):
        self.load_table()
