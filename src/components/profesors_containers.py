from constantes import MATERIAS_DATA
import flet as ft
from .calendar_component import CalendarContainer


class _Profesors:
    def __init__(self, name: str, assigment: str):
        self.name = name
        self.assigment = assigment
        self.blocks = set()

    def set_blocks(self, calendar_blocks: set):
        self.blocks = calendar_blocks


class _Semester(ft.Container):
    def __init__(self, number: int, assignments: dict):
        super().__init__()
        self.number = number
        self.assignments = assignments

        self.padding = 10
        self.border_radius = 10
        self.border = ft.border.all(1, "blue")

        self.layout = ft.Column(spacing=15)
        self.layout.controls.append(
            ft.Text(f"SEMESTRE {self.number}", size=16, weight=ft.FontWeight.BOLD)
        )

        for code, value in self.assignments.items():
            self.layout.controls.append(self._build_assigment(code, value))

        self.content = self.layout

    def _build_assigment(self, code, name):
        row_prof = ft.Column(spacing=5)

        def add_prof_to_mat(e):
            name_input = ft.TextField(
                label="Nombre del _Profesors",
                autofocus=True,
                on_submit=lambda _: confirm_add(None),
            )

            def confirm_add(_):
                if name_input.value:
                    new_prof = _Profesors(name_input.value, assigment=code)

                    row_prof.controls.append(self._build_prof_row(new_prof, row_prof))
                    dlg.open = False
                    e.page.update()

            dlg = ft.AlertDialog(
                title=ft.Text(f"Agregar _Profesors a {name}"),
                content=name_input,
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=lambda _: (
                            setattr(dlg, "open", False) or e.page.update()
                        ),
                    ),
                    ft.TextButton("Agregar", on_click=confirm_add),
                ],
            )
            e.page.overlay.append(dlg)
            dlg.open = True
            e.page.update()

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            f"{name} ({code})",
                            weight=ft.FontWeight.W_500,
                            expand=True,
                        ),
                        ft.IconButton(ft.Icons.PERSON_ADD, on_click=add_prof_to_mat),
                    ]
                ),
                row_prof,
            ]
        )

    def _build_prof_row(self, prof: _Profesors, parent_container):
        calendar = CalendarContainer(on_accept=prof.set_blocks)

        def delete_prof(e):
            parent_container.controls.remove(row)
            e.page.update()

        def open_calendar(e):
            calendar.open_dialog(e.page)

        row = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ARROW_RIGHT, size=16),
                    ft.Text(prof.name, size=14, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.DATE_RANGE, icon_size=18, on_click=open_calendar
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=18,
                        icon_color=ft.Colors.RED,
                        on_click=delete_prof,
                    ),
                ]
            ),
            padding=ft.Padding.only(left=20),
        )
        return row


class professorsContainer(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 20
        self.expand = True

        self.professors_data = []

        self.main_list = ft.ListView(expand=True, spacing=10)
        semesters = 10

        for i in range(1, semesters + 1):
            prefix = f"{i:02d}"
            semester_assignmets = {
                k: v for k, v in MATERIAS_DATA.items() if k[3:5] == prefix
            }

            if semester_assignmets:
                self.main_list.controls.append(
                    _Semester(number=i, assignments=semester_assignmets)
                )

        self.content = ft.Column(
            [
                ft.Text(
                    "Asignación de Docentes por Materia",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Divider(),
                self.main_list,
            ],
            expand=True,
        )
