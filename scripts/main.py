from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen


# Set the app size
Window.size = (800, 700)


# Define our different screens


class LoginScreen(Screen):
    # login = ObjectProperty(None)
    # password = ObjectProperty(None)
    pass


class MenuScreen(Screen):
    pass


class ScreenManager_(ScreenManager):
    def change_screen(self, screen):
        self.current = screen


# Now kivy knows what style we need for this app
kv = Builder.load_file('../kivy/hd.kv')


class HomeDoctor(App):

    def build(self):
        return kv


if __name__ == '__main__':
    HomeDoctor().run()
