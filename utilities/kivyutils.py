from kivymd.uix.datatables import MDDataTable
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.list import OneLineIconListItem

from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.properties import NumericProperty


class FilterMenuHeader(MDBoxLayout):
    """An instance of the class that will be added to the menu header."""


class CustomSnackbar(MDSnackbar):
    text = StringProperty(None)
    icon = StringProperty(None)
    font_size = NumericProperty("15sp")


class EditDialog_Content(MDBoxLayout):
    pass


class IconListItem(OneLineIconListItem):
    icon = StringProperty()


class Manager(ScreenManager):

    screen_history = []

    def change_screen(self, new):

        if not (new in self.screen_history):
            self.transition.direction = "left"
            self.screen_history.append(new)
        else:
            self.transition.direction = "right"
            for screen in reversed(self.screen_history):
                if screen != new:
                    print(self.screen_history)
                    self.screen_history.remove(screen)
                else:
                    break
        self.current = new

    def change_screen_to_prev(self):
        if len(self.screen_history) > 1:
            self.transition.direction = "right"
            self.screen_history.pop(-1)
            self.current = self.screen_history[-1]


def list_of_unique(l):
    n = []
    for i in l:
        if i not in n:
            n.append(i)
    return n


def uncheck_all_rows(table: MDDataTable):
    def deselect_rows(*args):
        table.table_data.select_all("normal")

    Clock.schedule_once(deselect_rows)
