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

thisScreen = None


class LinksMenuHeader(MDBoxLayout):
    def search(self, text):
        global thisScreen
        if not thisScreen:
            return
        thisScreen.set_link_menu_items(filter_string=text)


class SymptomAddEditScreen(Screen):
    dialog = None

    symptom: database.Symptom = None
    yes: database.Symptom = None
    no: database.Symptom = None

    id = 0

    f_name = ObjectProperty("")
    f_description = ObjectProperty("")
    f_yes_name = ObjectProperty("")
    f_no_name = ObjectProperty("")
    f_page = ObjectProperty("")
    f_keywords = ObjectProperty("")

    f_link_clean = "Выбрать"

    keywords = []
    new_keywords = []
    all_keywords = []

    def on_pre_enter(self):
        global thisScreen
        thisScreen = self
        with database.session_manager():
            self.all_keywords = []
            for keyword in database.select_keywords():
                self.all_keywords.append(keyword.word)

    def new_symptom(self):
        self.id = 0
        self.f_name = ""
        self.f_description = ""
        self.yes = None
        self.f_yes_name = self.f_link_clean
        self.no = None
        self.f_no_name = self.f_link_clean
        self.f_page = ""
        self.keywords = []
        self.f_keywords = ""
        self.ids.keywordsInput.text = ""
        self.new_keywords = []

    def load_symptom(self, id):
        with database.session_manager():
            self.symptom = database.select_symptom(id=id)

            self.yes = self.symptom.yes
            self.no = self.symptom.no

            self.id = self.symptom.id
            self.f_name = self.symptom.name
            self.f_description = self.symptom.description or ""
            self.f_yes_name = self.yes.name if self.yes else self.f_link_clean
            self.f_no_name = self.no.name if self.no else self.f_link_clean
            self.f_page = str(self.symptom.page) if self.symptom.page else ""
            self.f_keywords = database.keywords_string(self.symptom.keywords)
            self.ids.keywordsInput.text = self.f_keywords or ""
            self.keywords = [
                keyword.word for keyword in database.select_symptom(id=self.id).keywords
            ]

    def save(self):
        if (
            not (
                (
                    ""
                    or None
                    in [
                        self.f_name,
                        self.f_description,
                        self.f_page,
                    ]
                )
            )
            and self.f_page.isdigit()
        ):
            with database.session_manager():

                if self.id == 0:
                    print("save new")
                    database.insert_symptom(
                        name=self.f_name.strip(),
                        description=self.f_description.strip(),
                        page=int(self.f_page.strip()),
                    )

                    if self.no:
                        database.select_symptom(name=self.f_name).no_id = self.no.id

                    if self.yes:
                        database.select_symptom(name=self.f_name).yes_id = self.yes.id

                    new_keywords = [
                        x for x in self.keywords if x not in self.all_keywords
                    ]

                    for keyword in new_keywords:
                        database.insert_keyword(word=keyword)

                    for keyword in self.keywords:
                        database.insert_symptom_keyword_mapping(
                            symptom_id=database.select_symptom(name=self.f_name).id,
                            keyword_id=database.select_keyword(word=keyword).id,
                        )

                else:
                    database.update_symptom(
                        id=self.id,
                        new_name=self.f_name,
                        new_description=self.f_description,
                        new_page=int(self.f_page),
                        new_yes_id=self.yes.id if self.yes else None,
                        new_no_id=self.no.id if self.no else None,
                    )

                    print(f"Введенные ключи:\n{self.keywords}")

                    actual_keywords = []
                    for keyword in database.select_symptom(id=self.id).keywords:
                        actual_keywords.append(keyword.word)

                    print(f"Прошлые ключи:\n{actual_keywords}")

                    keywords_to_delete = [
                        x for x in actual_keywords if x not in self.keywords
                    ]

                    print(f"Отвязанные ключи:\n{keywords_to_delete}")

                    new_keywords = [
                        x for x in self.keywords if x not in self.all_keywords
                    ]

                    for keyword in new_keywords:
                        database.insert_keyword(word=keyword)

                    print(f"Новые ключи:\n{new_keywords}")

                    new_to_symptom_keywords = [
                        x for x in self.keywords if x not in actual_keywords
                    ]

                    for keyword in new_to_symptom_keywords:
                        database.insert_symptom_keyword_mapping(
                            symptom_id=self.id,
                            keyword_id=database.select_keyword(word=keyword).id,
                        )

                    print(f"Новые ключи для сипмтома:\n{new_to_symptom_keywords}")

                    if len(keywords_to_delete) > 0:
                        for keyword in keywords_to_delete:
                            database.delete_symptom_keyword_mapping(
                                symptom_id=self.id,
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
                if not text:
                    return

                symptom_data = parser.parse_symptom_data(text)
                if not symptom_data:
                    return

                print(symptom_data)

                self.f_name = (
                    f"{symptom_data['name'].capitalize()}"
                    if symptom_data["name"]
                    else self.f_name
                )

                self.f_page = (
                    f"{symptom_data['page']}" if symptom_data["page"] else self.f_page
                )

                self.f_description = (
                    f"{symptom_data['description'].capitalize()}"
                    if symptom_data["description"]
                    else self.f_description
                )

                if symptom_data["yes_name"]:
                    with database.session_manager():
                        potential_yes = database.select_symptoms(
                            name=symptom_data["yes_name"]
                        )
                        symptom = potential_yes[0] if potential_yes else None
                    if (
                        symptom
                        and ((symptom.id != self.symptom.id) if self.symptom else True)
                        and ((symptom.id != self.yes.id) if self.yes else True)
                        and ((symptom.id != self.no.id) if self.no else True)
                    ):
                        self.yes = symptom
                        self.f_yes_name = symptom.name

                if symptom_data["no_name"]:
                    with database.session_manager():
                        potential_no = database.select_symptoms(
                            name=symptom_data["no_name"]
                        )
                        symptom = potential_no[0] if potential_no else None
                    if (
                        symptom
                        and ((symptom.id != self.symptom.id) if self.symptom else True)
                        and ((symptom.id != self.yes.id) if self.yes else True)
                        and ((symptom.id != self.no.id) if self.no else True)
                    ):
                        self.no = symptom
                        self.f_no_name = symptom.name

                self.f_keywords = (
                    f"{symptom_data['keywords']}"
                    if symptom_data["keywords"]
                    else self.f_keywords
                )

    def save_then_quit(self):
        if self.save():
            self.manager.change_screen("symptomsScreen")

    def save_then_add(self):
        if self.save():
            # appInstance.change_title("Добавление симптома")
            self.new_symptom()

    def clear_yes(self):
        self.f_yes_name = self.f_link_clean
        self.yes = None

    def clear_no(self):
        self.f_no_name = self.f_link_clean
        self.no = None

    def set_yes(self, symptom):
        self.f_yes_name = symptom.name
        self.yes = symptom

    def set_no(self, symptom):
        self.f_no_name = symptom.name
        self.no = symptom

    def set_link_menu_items(self, filter_string=None):
        if not self.link_menu:
            return
        self.link_menu.items = [
            {
                "viewclass": "IconListItem",
                "icon": "broom",
                "text": "Очистить",
                "on_release": lambda: (
                    self.link_menu.dismiss(),
                    (
                        self.clear_yes()
                        if self.link_menu_caller == self.ids.yesLinkMenuButton
                        else (
                            self.clear_no()
                            if self.link_menu_caller == self.ids.noLinkMenuButton
                            else None
                        )
                    ),
                ),
            }
        ]
        with database.session_manager():
            for symptom in list(
                filter(
                    lambda s: (
                        s.id != self.id
                        and ((s.id != self.yes.id) if self.yes else True)
                        and ((s.id != self.no.id) if self.no else True)
                    ),
                    database.select_symptoms(name=filter_string),
                )
            ):
                self.link_menu.items.append(
                    {
                        "text": symptom.name,
                        "on_release": lambda s=symptom: (
                            self.link_menu.dismiss(),
                            (
                                self.set_yes(s)
                                if self.link_menu_caller == self.ids.yesLinkMenuButton
                                else (
                                    self.set_no(s)
                                    if self.link_menu_caller
                                    == self.ids.noLinkMenuButton
                                    else None
                                )
                            ),
                        ),
                    }
                )
        self.link_menu.set_menu_properties()

    def init_link_menu(self, caller):

        self.link_menu = MDDropdownMenu(caller=caller, header_cls=MDBoxLayout())

        self.link_menu_caller = caller

        self.set_link_menu_items()

        if len(self.link_menu.items) > 4:
            if self.link_menu.header_cls.__class__.__name__ != "LinksMenuHeader":
                self.link_menu.header_cls = LinksMenuHeader()
        else:
            self.link_menu.header_cls = MDBoxLayout()

        if self.link_menu.header_cls.__class__.__name__ == "LinksMenuHeader":
            if len(self.link_menu.header_cls.ids) > 0:
                self.link_menu.header_cls.ids.searchField.focus = True
                self.link_menu.header_cls.ids.searchField.text = ""
            else:
                self.link_menu.dismiss()

        self.link_menu.open()

    def menu_set_header(self, menu):
        if len(menu.items) > 4:
            if menu.header_cls.__class__.__name__ != "LinksMenuHeader":
                menu.header_cls = LinksMenuHeader()
        else:
            menu.header_cls = MDBoxLayout()

    def keywords_enter(self, text):
        def find_common(list1, list2):
            res = 0
            for item in list1:
                if item in list2:
                    res += 1
            return res

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
            self.keywords = parsed_list
        else:
            self.ids.keywordsInput.helper_text = (
                "Вводите через запятую (Можно с пробелами)"
            )
