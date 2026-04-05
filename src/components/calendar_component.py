import flet as ft
import constantes as cs
from datetime import datetime, timedelta
from typing import Callable, Optional
import os
import json


# CalendarContainer
@ft.control
class CalendarContainer(ft.Container):
    def __init__(self, on_accept: Optional[Callable[[set], None]] = None):
        super().__init__()
        self._on_accept_callback = on_accept
        self._page: Optional[ft.Page] = None
        self.availabity = set()
        self._dialog_content = ft.Container(
            content=self._build_calendar(),
            width=980,
            height=640,
            border_radius=10,
            padding=5,
            alignment=ft.Alignment.CENTER,
        )
        self._popup = ft.AlertDialog(
            content=self._dialog_content,
            actions=[
                ft.TextButton("Cancelar", on_click=self._cancel_dialog),
                ft.ElevatedButton("Aceptar", on_click=self._accept_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def open_dialog(self, page: ft.Page):
        self._page = page
        if self._popup not in page.overlay:
            page.overlay.append(self._popup)
        self._popup.open = True
        page.update()

    def close_dialog(self):
        if self._page is None:
            return
        self._popup.open = False
        self._page.update()

    def _rec_set(self, period_name: str):
        origin_path = os.getcwd()
        period_path = os.path.normpath(
            os.path.join(origin_path, "..", "CRONO", "data", "periodos", period_name)
        )
        availabity_path = os.path.join(period_path, "availability.json")
        with open(availabity_path, "w") as file:
            json.dump(list(self.availabity), file)

    def _accept_dialog(self, _):
        if self._on_accept_callback:
            self._on_accept_callback(set(self.availabity))

        self.close_dialog()

    def _cancel_dialog(self, _):
        self.close_dialog()

    def _checkbox_changed(self, e: ft.Event[ft.Checkbox]):
        id_celda = e.control.data
        if e.control.value:
            self.availabity.add(id_celda)
        else:
            self.availabity.discard(id_celda)
        print("Disponibilidad actual:", self.availabity)

    def _build_calendar(self):
        hour_col_width = 180
        day_col_width = 125

        columns = []
        for index, day in enumerate(cs.horario):
            col_width = hour_col_width if index == 0 else day_col_width
            columns.append(
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(day, weight=ft.FontWeight.W_600),
                        width=col_width,
                        alignment=ft.Alignment.CENTER,
                    )
                )
            )

        rows = []
        current_hour = datetime.strptime(cs.hour, "%I:%M %p")

        hours_blocks = 13
        week_days = 7
        for hours in range(hours_blocks):
            row_cells = []
            for c in range(week_days):
                if c == 0:
                    new_hour = current_hour + timedelta(minutes=cs.class_time)
                    start_time = current_hour.strftime("%I:%M %p")
                    finist_time = new_hour.strftime("%I:%M %p")
                    row_cells.append(
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    f"{start_time} - {finist_time}",
                                    size=12,
                                ),
                                width=hour_col_width,
                                alignment=ft.Alignment.CENTER,
                            ),
                        )
                    )
                    current_hour = new_hour

                else:
                    value = ((c - 1) * hours_blocks) + hours
                    row_cells.append(
                        ft.DataCell(
                            ft.Container(
                                content=ft.Checkbox(
                                    data=value, on_change=self._checkbox_changed
                                ),
                                width=day_col_width,
                                alignment=ft.Alignment.CENTER,
                            )
                        )
                    )
            rows.append(ft.DataRow(cells=row_cells))

        calendar = ft.DataTable(
            columns=columns,
            rows=rows,
            horizontal_lines=ft.border.BorderSide(0.5, "grey"),
            column_spacing=0,
        )

        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Disponibilidad Docente", size=20),
                ft.Divider(),
                ft.Container(
                    content=calendar,
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                ),
            ],
            expand=True,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
