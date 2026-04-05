import flet as ft
from components.profesors_containers import professorsContainer


def main(page: ft.Page):
    professors = professorsContainer()
    page.add(professors)


ft.run(main)
