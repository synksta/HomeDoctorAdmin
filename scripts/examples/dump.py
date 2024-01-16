from kivy.lang import Builder
from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout

KV = '''

<YesNoMenuHeader> 
    padding: "10dp", "10dp", "0dp", "-8dp"
    adaptive_height: True
    MDTextField:
        id: searchField
        text: ''
        on_text: app.search(self.text)
        # adaptive_size: True
        size_hint: None, 0
        width: '184dp'
    MDIconButton:
        icon: "magnify"
        pos_hint: {'x': 1, "top": 1}

MDScreen:

    MDRaisedButton:
        id: button
        text: "PRESS ME"
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: 
            app.menu.open()
            app.set_focus()
'''


class YesNoMenuHeader(MDBoxLayout):
    '''An instance of the class that will be added to the menu header.'''


class Test(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = Builder.load_string(KV)
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
        self.menu = MDDropdownMenu(
            header_cls=YesNoMenuHeader(),
            caller=self.screen.ids.button,
            items=filter_menu_items,
        )

    def set_focus(self):
        self.menu.ids.content_header.children[0].ids.searchField.focus = True
        self.menu.ids.content_header.children[0].ids.searchField.text = ''
        # print(self.menu.ids.content_header.children[0].ids)

    def menu_callback(self, text_item):

        print(text_item)

    def build(self):
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.theme_style = "Dark"
        return self.screen

    def search(self, text):
        # self.menu.ids.content_header.children[0].ids.searchField.text = 'Поиск'
        # self.menu.ids.content_header.children[0].ids.searchLabel.text = text
        print(text)


Test().run()
