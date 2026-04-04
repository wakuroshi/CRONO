import flet as ft
from components.calendar_component import CalendarContainer


def main(page: ft.Page):
    calendar = ft.AlertDialog(CalendarContainer())
    page.add(
        ft.SafeArea(
            content=ft.Column(
                controls=[
                    ft.Button(
                        content="Open dialog",
                        on_click=lambda: page.show_dialog(calendar),
                    )
                ]
            )
        )
    )


ft.run(main)
