import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class MyGridLayout(GridLayout): # Inheritiёng the GridLayout
  # Initialize infinite keywords
  def __init__(self, **kwargs):
    # Call grid layout constructor
    super(MyGridLayout, self).__init__(**kwargs) # Calling __init__ method of inherited class

    # Set columns
    self.cols = 1

    # Create a second gridlayout
    self.top_grid = GridLayout
    self.top_grid.cols = 2

    # Add widgets

    # 1
    # Add label
    self.top_grid.add_widget(Label(text="Name: "))
    # Add input box
    self.name = TextInput(multiline = False)
    self.top_grid.add_widget(self.name)
    
    # 2
    # Add label
    self.top_grid.add_widget(Label(text="Midname: "))
    # Add input box
    self.midname = TextInput(multiline = False)
    self.top_grid.add_widget(self.midname)

    # 3
    # Add label
    self.top_grid.add_widget(Label(text="Surname: "))
    # Add input box
    self.surname = TextInput(multiline = False)
    self.top_grid.add_widget(self.surname)

    # Add the new top_grid to our app
    self.add_widget(self.top_grid)


    # Create a submit button
    self.submit = Button(text="Submit", font_size= 32)
    # Bind the button 
    self.submit.bind(on_press=self.press)
    self.add_widget(self.submit)

  def press(self, instance):
    name =  self.name.text
    midname = self.midname.text
    surname = self.surname.text

    # print(f'Hello {name} {midname} {surname}!')
    # Create a result label
    self.add_widget(Label(f'Hello {name} {midname} {surname}!'))

    # Clear the input boxes

    self.name.text = ''
    self.midname.text = ''
    self.surname.text = ''

class MyApp(App):
  def build(self):
    return MyGridLayout()
  
if __name__ == '__main__':
  MyApp().run()