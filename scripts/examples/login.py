from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window

# Set the app size
Window.size = (800, 700)


class MyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Orange'
        self.theme_cls.accent_palette = 'DeepPurple'
        return Builder.load_file('../kivy/examples/login.kv')


if __name__ == "__main__":
    MyApp().run()
