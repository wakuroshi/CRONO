import flet as ft
from components.period_conteniner import PeriodContainer


def main(page: ft.Page):
    page.title = "C.R.O.N.O"
    page.add(PeriodContainer())


ft.run(main)
