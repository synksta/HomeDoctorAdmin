import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_file('main.kv')  # Now kivy knows what style we need for this app


class MainGridLayout(Widget):  # Inheriting the GridLayout
    # Initialize infinite keywords
    # def __init__(self, **kwargs):
    # Call grid layout constructor
    # Calling __init__ method of inherited class
    # super MainGridLayout, self).__init__(**kwargs)

    # # Set columns
    # self.cols = 1

    # # Create a second gridlayout
    # self.top_grid = GridLayout(
    #     row_force_default=True,
    #     row_default_height=40,
    #     col_force_default=True,
    #     row_default_height=100,
    # )
    # self.top_grid.cols = 2

    # # Add widgets

    # # 1
    # # Add label
    # self.top_grid.add_widget(Label(text="Name: "))
    # # Add input box
    # self.name = TextInput(multiline=False)
    # self.top_grid.add_widget(self.name)

    # # 2
    # # Add label
    # self.top_grid.add_widget(Label(text="Midname: "))
    # # Add input box
    # self.midname = TextInput(multiline=False)
    # self.top_grid.add_widget(self.midname)

    # # 3
    # # Add label
    # self.top_grid.add_widget(Label(text="Surname: "))
    # # Add input box
    # self.surname = TextInput(multiline=False)
    # self.top_grid.add_widget(self.surname)

    # # Add the new top_grid to our app
    # self.add_widget(self.top_grid)

    # # Create a submit button
    # self.submit = Button(text="Submit",
    #                      font_size=32,
    #                      )
    # # Bind the button
    # self.submit.bind(on_press=self.press)
    # self.add_widget(self.submit)

    name = ObjectProperty(None)
    midname = ObjectProperty(None)
    surname = ObjectProperty(None)

    def press(self):
        name = self.name.text
        midname = self.midname.text
        surname = self.surname.text

        # print(f'Hello {name} {midname} {surname}!')
        # Create a result label
        # self.add_widget(Label(f'Hello {name} {midname} {surname}!'))

        # Clear the input boxes

        self.name.text = ''
        self.midname.text = ''
        self.surname.text = ''

        print(f'Hello {name} {midname} {surname}!')


class HomeDoctorApp(App):  # The design file name must contain the lowercased class name BUT it must not contain a word 'App' (in our case the design file will be named 'homedoctor.kv'). If we would name this class Mango or whatever the design file would be named as 'mango.kv'
    def build(self):
        return MainGridLayout()


if __name__ == '__main__':
    HomeDoctorApp().run()
