import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

class MyGridLayout(GridLayout):
  # Initialize infinite keywords
  def __init__(self, **kwargs):
    # Call grid layout constructor
    super(MyGridLayout, self).__init__(**kwargs)

    # Set columns
    self.cols = 2

    # Add widgets

    # 1
    # Add label
    self.add_widget(Label(text="Name: "))
    # Add input box
    self.name = TextInput(multiline = False)
    self.add_widget(self.name)
    
    # 2
    # Add label
    self.add_widget(Label(text="Midname: "))
    # Add input box
    self.midname = TextInput(multiline = False)
    self.add_widget(self.midname)

    # 3
    # Add label
    self.add_widget(Label(text="Surname: "))
    # Add input box
    self.surname = TextInput(multiline = False)
    self.add_widget(self.surname)

    # Create a submit button
    self.submit = Button(text="Submit", font_size= 32)
    self.add_widget(self.submit)

class MyApp(App):
  def build(self):
    return MyGridLayout()
  
if __name__ == '__main__':
  MyApp().run()