import flet as ft
import constantes as cs
from datetime import timedelta


@ft.control
class CalendarContainer(ft.Container):
    def __init__(self):
        super().__init__()
        self.title = ft.Text("Disponibilidad Docente")
        self.padding = 10
        self.border_radius = 10
        self.content = self._build_calendar()
        self.width = 600
        self.height = 500

    def _build_calendar(self):
        for cells in cs.horario:
            cs.columns.append(ft.DataColumn(label=cells))

        hours_blocks = 13
        week_days = 7
        for hours in range(hours_blocks):
            row_cells = []
            for c in range(week_days):
                if c == 0:
                    new_hour = cs.object_hour + timedelta(minutes=cs.class_time)
                    result = new_hour.strftime("%I:%M %p")
                    row_cells.append(
                        ft.DataCell(
                            ft.Text(f"{cs.hour}\n{result}", size=12),
                        )
                    )
                    cs.object_hour = new_hour
                    cs.hour = result

                else:
                    value = ((c - 1) * hours_blocks) + hours
                    row_cells.append(ft.DataCell(ft.Text(str(value))))
            cs.rows.append(ft.DataRow(cells=row_cells))

        calendar = ft.DataTable(
            columns=cs.columns,
            rows=cs.rows,
            column_spacing=20,
            horizontal_lines=ft.border.BorderSide(0.5, "grey"),
        )

        return ft.Column(
            controls=[
                ft.Text("Disponibilidad Docente", size=20),
                ft.Divider(),
                ft.Column(
                    controls=[calendar], scroll=ft.ScrollMode.ADAPTIVE, expand=True
                ),
            ],
            tight=True,
        )
