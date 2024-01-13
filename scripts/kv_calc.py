from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window

# Set the app size
Window.size = (500, 700)

# Now kivy knows what style we need for this app
Builder.load_file('../kivy/examples/calc.kv')


class MainLayout(Widget):  # Inheriting the GridLayout
    temp = None

    def calc_add(self, text):
        if self.temp is None:
            temp = int(text)

    def calc_erase(self):
        if len(self.ids.calc_input.text) > 1:
            self.ids.calc_input.text = self.ids.calc_input.text[:-1]
        else:
            self.ids.calc_input.text = '0'

    def calc_clear(self):
        self.ids.calc_input.text = '0'

    def calc_print(self, text):
        if self.ids.calc_input.text == '0':
            self.ids.calc_input.text = text
        else:
            self.ids.calc_input.text += text


class Calculator(App):  # The design file name must contain the lowercased class name BUT it must not contain a word 'App' (in our case the design file will be named 'homedoctor.kv'). If we would name this class Mango or whatever the design file would be named as 'mango.kv'
    def build(self):
        return MainLayout()


if __name__ == '__main__':
    Calculator().run()
