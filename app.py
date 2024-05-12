from screens.keywords import *
from screens.login import *
from screens.menu import *
from screens.symptomform import *
from screens.symptoms import *
from screens.users import *

from utilities.kivyutils import *

from kivy.core.window import Window
from kivy.lang import Builder

from kivymd.app import MDApp


class App(MDApp):
    appname = "ДД Админ"

    Window.size = (800, 700)

    def change_title(self, new):
        self.title = f"{self.appname} - {new}"

    def build(self):
        self.icon = "../data/images/medical-bag.png"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.accent_palette = "DeepPurple"
        return Builder.load_file("app.kv")


appInstance = App()


def main():
    appInstance.run()


if __name__ == "__main__":
    main()
