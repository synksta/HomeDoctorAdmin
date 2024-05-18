# from app import appInstance

from kivymd.uix.screen import Screen
from kivy.properties import StringProperty

from utilities import database
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

        if not (name and password):
            if not name:
                self.ids.nameField.hint_text_color_normal = "red"
            if not password:
                self.ids.passwordField.hint_text_color_normal = "red"
            return

        with database.session_manager():
            user = database.select_user(name=name)

            if user and user.password == password:
                self.manager.change_screen("menuScreen")
            else:
                CustomSnackbar(
                    text="Неверный логин или пароль!",
                    icon="alert-box",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                ).open()
