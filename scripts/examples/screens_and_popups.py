from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen


# Set the app size
Window.size = (800, 700)


# Define our different screens


class FirstScreen(Screen):
    pass


class SecondScreen(Screen):
    pass


class ScreenManager_(ScreenManager):
    def change_screen(self, screen):
        self.current = screen


# Now kivy knows what style we need for this app
kv = Builder.load_file('../kivy/examples/screens_and_popups.kv')


class Multiscreen(App):

    def build(self):
        return kv


if __name__ == '__main__':
    Multiscreen().run()
