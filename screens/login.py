# from app import appInstance

from kivymd.uix.screen import Screen
from kivy.properties import StringProperty

from utilities import dbcontrol
from utilities.kivyutils import CustomSnackbar


class LoginScreen(Screen):
    name = StringProperty("")
    password = StringProperty("")

    def on_kv_post(self, base_widget):
        self.manager.screen_history.append(self.name)

    # def on_enter(self):
    # appInstance.change_title("Вход")

    # print(self.ids.nameField.text)  # = ''
    # self.ids.passwordField.text = ''

    def login(self):
        name = self.ids.nameField.text.strip()
        password = self.ids.passwordField.text.strip()

        if len(name) > 0 and len(password) > 0:

            dbcontrol.open_session()
            current_user = None
            for user in dbcontrol.read_users():
                if name == user.name:
                    current_user = user
                    break
            if current_user:
                if password == current_user.password:
                    self.manager.change_screen("menuScreen")
                else:
                    CustomSnackbar(
                        text="Пароль не подходит!",
                        icon="alert-box",
                        snackbar_x="10dp",
                        snackbar_y="10dp",
                    ).open()
            else:
                CustomSnackbar(
                    text="Такого пользователя нет!",
                    icon="alert-box",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                ).open()
        else:
            if len(name) == 0:
                self.ids.nameField.hint_text_color_normal = "red"
            if len(password) == 0:
                self.ids.passwordField.hint_text_color_normal = "red"
