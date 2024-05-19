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
    appname = "Home Doctor - Admin"

    Window.size = (800, 700)

    def change_title(self, new):
        self.title = f"{self.appname} - {new}"

    def build(self):
        self.icon = "../data/images/medical-bag.png"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.accent_palette = "DeepPurple"
        #
        # Commented the build thing because it's not needed
        # in case of kv file has the same name as the class
        #
        # return Builder.load_file("app.kv")


def main():
    appInstance = App()
    appInstance.run()


if __name__ == "__main__":
    main()
