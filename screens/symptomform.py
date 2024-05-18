# from app import appInstance
import re

from kivymd.uix.screen import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.properties import ObjectProperty

from utilities import database

from voicerecognition import recorder, speechtotext, parser


class YesNoMenuHeader(MDBoxLayout):
    data = None

    def search(self, text):
        if self.data == None:
            self.data = self.parent.parent.items.copy()

        if len(text) > 0:
            res = list(
                filter(
                    lambda x: text.lower() in x.get("text").lower()
                    or x.get("text") == "Очистить",
                    self.data,
                )
            )
            self.parent.parent.items = res
        else:
            self.parent.parent.items = self.data
        self.parent.parent.set_menu_properties()


class SymptomAddEditScreen(Screen):
    dialog = None

    symptom_id = 0
    symptom_name = ObjectProperty("")
    symptom_description = ObjectProperty("")
    symptom_yes = None
    symptom_yes_name = ObjectProperty("Выбрать")
    symptom_no = None
    symptom_no_name = ObjectProperty("Выбрать")
    symptom_page = ObjectProperty("")
    symptom_keywords_string = ObjectProperty("")
    symptom_keywords = []

    new_keywords = []
    all_keywords = []

    def on_pre_enter(self):
        with database.session_manager():
            self.all_keywords = []
            for keyword in database.select_keywords():
                self.all_keywords.append(keyword.word)

    def new_symptom(self):
        self.symptom_id = 0
        self.symptom_name = ""
        self.symptom_description = ""
        self.symptom_yes = None
        self.symptom_yes_name = "Выбрать"
        self.symptom_no = None
        self.symptom_no_name = "Выбрать"
        self.symptom_page = ""
        self.symptom_keywords = []
        self.symptom_keywords_string = ""
        self.ids.keywordsInput.text = ""
        self.new_keywords = []
        self.yes_menu_items = self.symptoms_yes_menu_gen()
        self.no_menu_items = self.symptoms_no_menu_gen()

    def load_symptom(self, id):
        database.session_open()
        symptom = database.get_symptom_by_id(id)

        self.symptom_id = symptom.id

        self.symptom_name = symptom.name

        if symptom.description:
            self.symptom_description = symptom.description
        else:
            self.symptom_description = ""

        if symptom.yes_obj:
            self.symptom_yes = symptom.yes_obj
            self.symptom_yes_name = symptom.yes_obj.name
        else:
            self.symptom_yes = None
            self.symptom_yes_name = "Выбрать"

        if symptom.no_obj:
            self.symptom_no = symptom.no_obj
            self.symptom_no_name = symptom.no_obj.name
        else:
            self.symptom_no = None
            self.symptom_no_name = "Выбрать"

        if symptom.page:
            self.symptom_page = str(symptom.page)
        else:
            self.symptom_page = ""

        self.symptom_keywords_string = database.keywords_string(symptom.keywords)
        if self.symptom_keywords_string == "":
            self.ids.keywordsInput.text = ""

        self.symptom_keywords = []
        for keyword in database.get_symptom_by_id(self.symptom_id).keywords:
            self.symptom_keywords.append(keyword.word)

    def save(self):
        if (
            not (
                (
                    ""
                    or None
                    in [
                        self.symptom_name,
                        self.symptom_description,
                        self.symptom_page,
                        # self.symptom_no_obj,
                        # self.symptom_yes_obj
                    ]
                )
            )
            and self.symptom_page.isdigit()
        ):
            with database.session_manager():

                if self.symptom_id == 0:
                    print("save new")
                    database.insert_symptom(
                        name=self.symptom_name.strip(),
                        description=self.symptom_description.strip(),
                        page=int(self.symptom_page.strip()),
                    )

                    if self.symptom_no:
                        database.select_symptom(name=self.symptom_name).no_id = (
                            self.symptom_no.id
                        )

                    if self.symptom_yes:
                        database.select_symptom(name=self.symptom_name).yes_id = (
                            self.symptom_yes.id
                        )

                    new_keywords = [
                        x for x in self.symptom_keywords if x not in self.all_keywords
                    ]

                    for keyword in new_keywords:
                        database.insert_keyword(keyword)

                    for keyword in self.symptom_keywords:
                        database.insert_symptom_keyword_mapping(
                            database.select_symptom(name=self.symptom_name).id,
                            database.select_keyword(word=keyword).id,
                        )

                else:
                    database.update_symptom(
                        self.symptom_id,
                        self.symptom_name,
                        self.symptom_description,
                        int(self.symptom_page),
                    )

                    if self.symptom_no:
                        database.select_symptom(name=self.symptom_name).no = (
                            self.symptom_no.id
                        )

                    if self.symptom_yes:
                        database.select_symptom(name=self.symptom_name).yes = (
                            self.symptom_yes.id
                        )

                    print(f"Введенные ключи:\n{self.symptom_keywords}")

                    actual_keywords = []
                    for keyword in database.select_symptom(id=self.symptom_id).keywords:
                        actual_keywords.append(keyword.word)

                    print(f"Прошлые ключи:\n{actual_keywords}")

                    keywords_to_delete = [
                        x for x in actual_keywords if x not in self.symptom_keywords
                    ]

                    print(f"Отвязанные ключи:\n{keywords_to_delete}")

                    new_keywords = [
                        x for x in self.symptom_keywords if x not in self.all_keywords
                    ]

                    for keyword in new_keywords:
                        database.insert_keyword(word=keyword)

                    print(f"Новые ключи:\n{new_keywords}")

                    new_to_symptom_keywords = [
                        x for x in self.symptom_keywords if x not in actual_keywords
                    ]

                    for keyword in new_to_symptom_keywords:
                        database.insert_symptom_keyword_mapping(
                            symptom_id=self.symptom_id,
                            keyword_id=database.select_keyword(word=keyword).id,
                        )

                    print(f"Новые ключи для сипмтома:\n{new_to_symptom_keywords}")

                    if len(keywords_to_delete) > 0:
                        for keyword in keywords_to_delete:
                            database.delete_symptom_keyword_mapping(
                                symptom_id=self.symptom_id,
                                keyword_id=database.select_keyword(word=keyword).id,
                            )
            return True
        else:
            if not self.dialog:
                self.dialog = MDDialog(
                    title="Ошибка",
                    text="Вы допустили ошибку при заполнении формы",
                    type="custom",
                    buttons=[MDFlatButton(text="ОК", on_release=self.dialog_dismiss)],
                )
            self.dialog.open()
            return False

    def dialog_dismiss(self, obj):
        self.dialog.dismiss()
        self.dialog = None

    ready_to_record_audio = None

    def voice_input(self):

        self.ready_to_record_audio = (
            not (self.ready_to_record_audio)
            if self.ready_to_record_audio is not None
            else True
        )

        path = None

        if self.ready_to_record_audio:
            recorder.start()
        else:
            path = recorder.stop_and_get_path()
            if path is not None:
                text = speechtotext.get_text_from_speech(path=path)
                print(text)
                if text is not "":
                    f = parser.get_symptom_data(text)
                    if f:
                        print(f)
                        # data = json.load(f)
                        # if data:
                        #     self.symptom_name = (f"{data['name']}").capitalize()
                        #     self.symptom_page = f"{data['page']}"
                        #     self.symptom_description = (
                        #         f"{data['description']}"
                        #     ).capitalize()
                        #     self.symptom_keywords_string = f"{data['keywords']}"
                        #     if data["yes"]:
                        #         database.session_open()
                        #         symptom = database.get_symptom_by_name(data["yes"])
                        #         database.session_close()
                        #         if symptom:
                        #             self.symptom_yes_obj = symptom
                        #             self.symptom_yes_name = symptom.name
                        #     if data["no"]:
                        #         database.session_open()
                        #         symptom = database.get_symptom_by_name(data["no"])
                        #         database.session_close()
                        #         if symptom:
                        #             self.symptom_no_obj = symptom
                        # self.symptom_no_name = symptom.name

    #     global ready

    #     result = None

    #     if ready:
    #         start()
    #     else:
    #         result = stop_and_get_wav()

    #     return result

    def save_then_quit(self):
        if self.save():
            self.manager.change_screen("symptomsScreen")

    def save_then_add(self):
        if self.save():
            # appInstance.change_title("Добавление симптома")
            self.new_symptom()

    def symptoms_yes_menu_gen(self):
        res = [
            {
                "viewclass": "IconListItem",
                "icon": "broom",
                "text": "Очистить",
                "on_release": self.clear_yes_symptom,
            }
        ]

        database.session_open()

        for symptom in list(
            filter(lambda x: x.id != self.symptom_id, database.select_symptoms())
        ):
            res.append(
                {
                    "text": symptom.name,
                    "on_release": lambda x=symptom: self.yes_select_callback(x),
                }
            )

        database.session_close()

        return res

    def clear_yes_symptom(self):
        self.yes_menu.dismiss()
        self.symptom_yes_name = "Выбрать"
        self.symptom_yes = None

    def symptoms_no_menu_gen(self):
        res = [
            {
                "viewclass": "IconListItem",
                "icon": "broom",
                "text": "Очистить",
                "on_release": self.clear_no_symptom,
            }
        ]

        database.session_open()

        for symptom in list(
            filter(lambda x: x.id != self.symptom_id, database.select_symptoms())
        ):
            res.append(
                {
                    "text": symptom.name,
                    "on_release": lambda x=symptom: self.no_menu_callback(x),
                }
            )

        database.session_close()

        return res

    def clear_no_symptom(self):
        self.no_menu.dismiss()
        self.symptom_no_name = "Выбрать"
        self.symptom_no = None

    def on_enter(self):
        self.yes_menu_items = self.symptoms_yes_menu_gen()
        self.no_menu_items = self.symptoms_no_menu_gen()

        self.yes_menu = MDDropdownMenu(
            caller=self.ids.yesButton, header_cls=MDBoxLayout()
        )

        self.no_menu = MDDropdownMenu(
            caller=self.ids.noButton, header_cls=MDBoxLayout()
        )

    def menu_set_header(self, menu):
        if len(menu.items) > 4:
            if menu.header_cls.__class__.__name__ != "YesNoMenuHeader":
                menu.header_cls = YesNoMenuHeader()
        else:
            menu.header_cls = MDBoxLayout()

    def prepare_menu_yes(self):
        self.yes_menu.items = list(
            filter(
                lambda x: x.get("text")
                not in (self.symptom_yes_name, self.symptom_no_name),
                self.yes_menu_items.copy(),
            )
        )

        self.yes_menu.set_menu_properties()
        self.menu_set_header(self.yes_menu)
        self.set_focus_yes()

    def prepare_menu_no(self):

        self.no_menu.items = list(
            filter(
                lambda x: x.get("text")
                not in (self.symptom_yes_name, self.symptom_no_name),
                self.no_menu_items.copy(),
            )
        )

        self.no_menu.set_menu_properties()
        self.menu_set_header(self.no_menu)
        self.set_focus_no()

    def set_focus_yes(self):
        if self.yes_menu.header_cls.__class__.__name__ == "YesNoMenuHeader":
            if len(self.yes_menu.header_cls.ids) > 0:
                self.yes_menu.header_cls.ids.searchField.focus = True
                self.yes_menu.header_cls.ids.searchField.text = ""
            else:
                self.yes_menu.dismiss()

    def set_focus_no(self):
        if self.no_menu.header_cls.__class__.__name__ == "YesNoMenuHeader":
            if len(self.no_menu.header_cls.ids) > 0:
                self.no_menu.header_cls.ids.searchField.focus = True
                self.no_menu.header_cls.ids.searchField.text = ""
            else:
                self.no_menu.dismiss()

    def yes_select_callback(self, x):

        self.yes_menu.dismiss()
        self.symptom_yes_name = x.name
        self.symptom_yes = x

    def no_menu_callback(self, x):
        self.no_menu.dismiss()
        self.symptom_no_name = x.name
        self.symptom_no = x

    def keywords_enter(self, text):
        def find_common(list1, list2):
            res = 0
            for item in list1:
                if item in list2:
                    res += 1
            return res
            # return sum(map(lambda x: x in list1 and x in list2, list1))

        if len(text) > 0:
            parsed_list = list(
                set(re.split("\\s*,+\\s*", re.sub(",*$", "", text).lower().strip()))
            )
            if "" in parsed_list:
                parsed_list.remove("")
            if "," in parsed_list:
                parsed_list.remove(",")
            common = find_common(parsed_list, self.all_keywords)
            self.ids.keywordsInput.helper_text = f"В базе есть {common} введенных слов, {len(parsed_list) - common} будет добавлено"
            self.symptom_keywords = parsed_list
        else:
            self.ids.keywordsInput.helper_text = (
                "Вводите через запятую (Можно с пробелами)"
            )
