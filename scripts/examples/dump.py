# # мусорка для примеров

# from kivy.app import App
# from kivy.uix.widget import Widget
# from kivy.properties import ObjectProperty
# from kivy.lang import Builder

# # Now kivy knows what style we need for this app
# Builder.load_file('../kivy/update_label.kv')


# class MainLayout(Widget):  # Inheriting the GridLayout
#     # Initialize infinite keywords
#     # def __init__(self, **kwargs):
#     # Call grid layout constructor
#     # Calling __init__ method of inherited class
#     # super MainLayout, self).__init__(**kwargs)

#     # # Set columns
#     # self.cols = 1

#     # # Create a second gridlayout
#     # self.top_grid = GridLayout(
#     #     row_force_default=True,
#     #     row_default_height=40,
#     #     col_force_default=True,
#     #     row_default_height=100,
#     # )
#     # self.top_grid.cols = 2

#     # # Add widgets

#     # # 1
#     # # Add label
#     # self.top_grid.add_widget(Label(text="Name: "))
#     # # Add input box
#     # self.name = TextInput(multiline=False)
#     # self.top_grid.add_widget(self.name)

#     # # 2
#     # # Add label
#     # self.top_grid.add_widget(Label(text="Midname: "))
#     # # Add input box
#     # self.midname = TextInput(multiline=False)
#     # self.top_grid.add_widget(self.midname)

#     # # 3
#     # # Add label
#     # self.top_grid.add_widget(Label(text="Surname: "))
#     # # Add input box
#     # self.surname = TextInput(multiline=False)
#     # self.top_grid.add_widget(self.surname)

#     # # Add the new top_grid to our app
#     # self.add_widget(self.top_grid)

#     # # Create a submit button
#     # self.submit = Button(text="Submit",
#     #                      font_size=32,
#     #                      )
#     # # Bind the button
#     # self.submit.bind(on_press=self.press)
#     # self.add_widget(self.submit)

#     name = ObjectProperty(None)
#     midname = ObjectProperty(None)
#     surname = ObjectProperty(None)

#     def press(self):
#         # Widget variables
#         name = self.ids.name_input

#         # Update the label
#         if name != '':
#             self.ids.name_label.text = f'Hello {name.text}!'
#         else:
#             self.ids.name_label.text = 'What\'s your name?'

#         # print(f'Hello {name} {midname} {surname}!')
#         # Create a result label
#         # self.add_widget(Label(f'Hello {name} {midname} {surname}!'))

#         # Clear the input boxes

#         self.ids.name_input.text = ''


# class HomeDoctorApp(App):  # The design file name must contain the lowercased class name BUT it must not contain a word 'App' (in our case the design file will be named 'homedoctor.kv'). If we would name this class Mango or whatever the design file would be named as 'mango.kv'
#     def build(self):
#         return MainLayout()


# if __name__ == '__main__':
#     HomeDoctorApp().run()
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

Builder.load_string('''\
<LoginScreen>:
    orientation: "horizontal"
    TextInput:
        text: "500"
        on_text: root.calc(self.text)
''')


class LoginScreen(BoxLayout):
    # def __init__(self, **kwargs):
    #     super(LoginScreen, self).__init__(**kwargs)

    def calc(self, text):
        print(text)


class MyApp(App):

    def build(self):
        return LoginScreen()


if __name__ == '__main__':
    MyApp().run()
