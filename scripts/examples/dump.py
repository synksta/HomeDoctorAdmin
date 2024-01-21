from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout

from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable


class Example(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"

        layout = AnchorLayout()
        data_tables = MDDataTable(
            size_hint=(0.9, 0.6),
            check=True,
            rows_num=30,
            column_data=[
                ("Column 1", dp(50)),
                ("Column 2", dp(30), self.sort_on_col_0),
                ("Column 3", dp(50)),
                ("Column 4", dp(30)),
                ("Column 5", dp(30)),
                ("Column 6", dp(30)),
            ],
            row_data=[
                ("1", f"{i + 1}", "2", "3", "4", "5") for i in range(30)
            ],
        )
        layout.add_widget(data_tables)
        return layout

    def sort_on_col_0(self, data):
        for d in data:
            print(d)

        return zip(
            *sorted(
                enumerate(data),
                key=lambda l: l[1][1]
            )
        )

    def sort_on_col_2(self, data):
        return zip(
            *sorted(
                enumerate(data),
                key=lambda l: l[1][-1]
            )
        )


Example().run()
