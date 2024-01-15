from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivymd.uix.list import OneLineListItem

# Builder String
helper_string = '''
ScreenManager:
    Hello:
    Bye:
<Hello>:
    name: 'hello'
    ScrollView:
        MDList:
            id: list
            
<Bye>:
    name: 'bye'
    MDLabel:
        id: target        
        text:'Good Bye'
    MDLabel:
        id:'aaa'
        text:""

'''


class Hello(Screen):
    pass


class Bye(Screen):
    pass


class DemoApp(MDApp):
    def build(self):
        screen = Screen()

        self.help_str = Builder.load_string(helper_string)

        screen.add_widget(self.help_str)
        return screen

    def on_start(self):
        for i in range(50):
            item = OneLineListItem(text='Item ' + str(i),
                                   on_release=lambda x, value_for_pass={
                                       i}: self.passValue(value_for_pass)
                                   )
            self.help_str.get_screen('hello').ids.list.add_widget(item)

    def passValue(self, *args):
        args_str = ','.join(map(str, args))
        print(args_str)
        bye_screen = self.help_str.get_screen('bye')
        bye_screen.manager.current = 'bye'
        bye_screen.ids.target.text = args_str


DemoApp().run()
