import flet as ft
from .profesors_containers import professorsContainer


class PeriodContainer(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 8
        self.period_input = ft.TextField(
            label="Nombre del periodo",
            hint_text="Ej: 2026-1CR",
            expand=True,
        )
        self.periods_column = ft.Column()

        self.add_button = ft.ElevatedButton(
            "Agregar Periodo",
            on_click=self._add_period,
        )
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self.period_input,
                        self.add_button,
                    ]
                ),
                self.periods_column,
            ]
        )

        self.periods_column.controls.append(self._build_period_title("2026-1CR"))

    def _build_period_title(self, period_name: str) -> ft.ExpansionTile:
        return ft.ExpansionTile(
            title=ft.Text(period_name),
            controls=[
                professorsContainer(),
            ],
        )

    def _add_period(self, e):
        name = (self.period_input.value or "").strip()
        if not name:
            return

        self.periods_column.controls.append(self._build_period_title(name))
        self.period_input.value = ""
        self.update()
