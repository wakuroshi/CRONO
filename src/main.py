import flet as ft


def main(page: ft.Page):
    counter = ft.Text("0", size=50, data=0)

    def increment_click(e):
        counter.data += 1
        counter.value = str(counter.data)

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD, on_click=increment_click
    )

    semesterbar = ft.MenuBar(
        controls=[
            ft.SubmenuButton(
                content=ft.Text("Submenu"),
                controls=[
                    ft.MenuItemButton(content=ft.Text("Item 1")),
                    ft.MenuItemButton(content=ft.Text("Item 2")),
                    ft.MenuItemButton(content=ft.Text("Item 3")),
                ],
            ),
        ],
    )

    page.add(
        semesterbar,
        ft.SafeArea(
            expand=True,
            content=ft.Container(
                content=counter,
                alignment=ft.Alignment.CENTER,
            ),
        ),
    )


ft.run(main)
