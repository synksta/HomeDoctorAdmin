# from app import appInstance
import re

from kivymd.uix.screen import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.properties import ObjectProperty

from utilities import dbcontrol

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
    symptom_yes_obj = None
    symptom_yes_name = ObjectProperty("Выбрать")
    symptom_no_obj = None
    symptom_no_name = ObjectProperty("Выбрать")
    symptom_page = ObjectProperty("")
    symptom_keywords_string = ObjectProperty("")
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
        self.symptom_name = ""
        self.symptom_description = ""
        self.symptom_yes_obj = None
        self.symptom_yes_name = "Выбрать"
        self.symptom_no_obj = None
        self.symptom_no_name = "Выбрать"
        self.symptom_page = ""
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

        if symptom.description:
            self.symptom_description = symptom.description
        else:
            self.symptom_description = ""

        if symptom.yes_obj:
            self.symptom_yes_obj = symptom.yes_obj
            self.symptom_yes_name = symptom.yes_obj.name
        else:
            self.symptom_yes_obj = None
            self.symptom_yes_name = "Выбрать"

        if symptom.no_obj:
            self.symptom_no_obj = symptom.no_obj
            self.symptom_no_name = symptom.no_obj.name
        else:
            self.symptom_no_obj = None
            self.symptom_no_name = "Выбрать"

        if symptom.page:
            self.symptom_page = str(symptom.page)
        else:
            self.symptom_page = ""

        self.symptom_keywords_string = dbcontrol.keywords_string(symptom.keywords)
        if self.symptom_keywords_string == "":
            self.ids.keywordsInput.text = ""

        self.symptom_keywords = []
        for keyword in dbcontrol.get_symptom(self.symptom_id).keywords:
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
            dbcontrol.open_session()

            if self.symptom_id == 0:
                print("save new")
                dbcontrol.insert_symptom(
                    self.symptom_name.strip(),
                    self.symptom_description.strip(),
                    int(self.symptom_page.strip()),
                )

                if self.symptom_no_obj:
                    dbcontrol.get_symptom_by_name(self.symptom_name).no = (
                        self.symptom_no_obj.id
                    )
                    dbcontrol.session.commit()

                if self.symptom_yes_obj:
                    dbcontrol.get_symptom_by_name(self.symptom_name).yes = (
                        self.symptom_yes_obj.id
                    )
                    dbcontrol.session.commit()

                new_keywords = [
                    x for x in self.symptom_keywords if x not in self.all_keywords
                ]

                for keyword in new_keywords:
                    dbcontrol.insert_keyword(keyword)

                for keyword in self.symptom_keywords:
                    dbcontrol.insert_ref_keyword(
                        dbcontrol.get_symptom_by_name(self.symptom_name).id,
                        dbcontrol.get_keyword_by_word(keyword).id,
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
                    dbcontrol.get_symptom_by_name(self.symptom_name).no = (
                        self.symptom_no_obj.id
                    )
                    dbcontrol.session.commit()

                if self.symptom_yes_obj:
                    dbcontrol.get_symptom_by_name(self.symptom_name).yes = (
                        self.symptom_yes_obj.id
                    )
                    dbcontrol.session.commit()

                print(f"Введенные ключи:\n{self.symptom_keywords}")
                actual_keywords = []
                for keyword in dbcontrol.get_symptom(self.symptom_id).keywords:
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
                    dbcontrol.insert_keyword(keyword)

                print(f"Новые ключи:\n{new_keywords}")

                new_to_symptom_keywords = [
                    x for x in self.symptom_keywords if x not in actual_keywords
                ]

                for keyword in new_to_symptom_keywords:
                    dbcontrol.insert_ref_keyword(
                        self.symptom_id, dbcontrol.get_keyword_by_word(keyword).id
                    )

                print(f"Новые ключи для сипмтома:\n{new_to_symptom_keywords}")

                if len(keywords_to_delete) > 0:
                    for keyword in keywords_to_delete:
                        dbcontrol.delete_ref_keyword(
                            self.symptom_id, dbcontrol.get_keyword_by_word(keyword).id
                        )

            dbcontrol.session.commit()
            dbcontrol.close_session()
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
                        #         dbcontrol.open_session()
                        #         symptom = dbcontrol.get_symptom_by_name(data["yes"])
                        #         dbcontrol.close_session()
                        #         if symptom:
                        #             self.symptom_yes_obj = symptom
                        #             self.symptom_yes_name = symptom.name
                        #     if data["no"]:
                        #         dbcontrol.open_session()
                        #         symptom = dbcontrol.get_symptom_by_name(data["no"])
                        #         dbcontrol.close_session()
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

        dbcontrol.open_session()

        for symptom in list(
            filter(lambda x: x.id != self.symptom_id, dbcontrol.read_symptoms())
        ):
            res.append(
                {
                    "text": symptom.name,
                    "on_release": lambda x=symptom: self.yesMenu_callback(x),
                }
            )

        dbcontrol.close_session()

        return res

    def clear_yes_symptom(self):
        self.yesMenu.dismiss()
        self.symptom_yes_name = "Выбрать"
        self.symptom_yes_obj = None

    def symptoms_no_menu_gen(self):
        res = [
            {
                "viewclass": "IconListItem",
                "icon": "broom",
                "text": "Очистить",
                "on_release": self.clear_no_symptom,
            }
        ]

        dbcontrol.open_session()

        for symptom in list(
            filter(lambda x: x.id != self.symptom_id, dbcontrol.read_symptoms())
        ):
            res.append(
                {
                    "text": symptom.name,
                    "on_release": lambda x=symptom: self.noMenu_callback(x),
                }
            )

        dbcontrol.close_session()

        return res

    def clear_no_symptom(self):
        self.noMenu.dismiss()
        self.symptom_no_name = "Выбрать"
        self.symptom_no_obj = None

    def on_enter(self):
        self.yes_menu_items = self.symptoms_yes_menu_gen()
        self.no_menu_items = self.symptoms_no_menu_gen()

        self.yesMenu = MDDropdownMenu(
            caller=self.ids.yesButton, header_cls=MDBoxLayout()
        )

        self.noMenu = MDDropdownMenu(caller=self.ids.noButton, header_cls=MDBoxLayout())

    def menu_set_header(self, menu):
        if len(menu.items) > 4:
            if menu.header_cls.__class__.__name__ != "YesNoMenuHeader":
                menu.header_cls = YesNoMenuHeader()
        else:
            menu.header_cls = MDBoxLayout()

    def prepare_menu_yes(self):
        self.yesMenu.items = list(
            filter(
                lambda x: x.get("text")
                not in (self.symptom_yes_name, self.symptom_no_name),
                self.yes_menu_items.copy(),
            )
        )

        self.yesMenu.set_menu_properties()
        self.menu_set_header(self.yesMenu)
        self.set_focus_yes()

    def prepare_menu_no(self):

        self.noMenu.items = list(
            filter(
                lambda x: x.get("text")
                not in (self.symptom_yes_name, self.symptom_no_name),
                self.no_menu_items.copy(),
            )
        )

        self.noMenu.set_menu_properties()
        self.menu_set_header(self.noMenu)
        self.set_focus_no()

    def set_focus_yes(self):
        if self.yesMenu.header_cls.__class__.__name__ == "YesNoMenuHeader":
            if len(self.yesMenu.header_cls.ids) > 0:
                self.yesMenu.header_cls.ids.searchField.focus = True
                self.yesMenu.header_cls.ids.searchField.text = ""
            else:
                self.yesMenu.dismiss()

    def set_focus_no(self):
        if self.noMenu.header_cls.__class__.__name__ == "YesNoMenuHeader":
            if len(self.noMenu.header_cls.ids) > 0:
                self.noMenu.header_cls.ids.searchField.focus = True
                self.noMenu.header_cls.ids.searchField.text = ""
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
