from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog

KV = '''
<AddUserDialog_Content>
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "120dp"

    MDTextField:
        id: loginField
        hint_text: "Логин"

    MDTextField:
        id: passwordField
        hint_text: "Пароль"
                    


MDFloatLayout:

    MDFlatButton:
        text: "ALERT DIALOG"
        pos_hint: {'center_x': .5, 'center_y': .5}
        on_release: app.show_add_user_dialog()
'''


class AddUserDialog_Content(BoxLayout):
    pass


class Example(MDApp):
    dialog = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        return Builder.load_string(KV)

    def show_add_user_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Address:",
                type="custom",
                content_cls=AddUserDialog_Content(),
                buttons=[
                    MDFlatButton(
                        text="ОТМЕНИТЬ",
                        on_release=self.cancel
                    ),
                    MDRaisedButton(
                        text="ДОБАВИТЬ",
                        on_release=self.add_user


                    )
                ]
            )

        self.dialog.open()

    def cancel(self, obj):
        self.dialog.dismiss()

    def add_user(self, obj):
        self.dialog.dismiss()
        print(self.dialog.content_cls.ids.loginField.text)
        print(self.dialog.content_cls.ids.passwordField.text)


Example().run()
