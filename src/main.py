from datetime import timedelta
import flet as ft
import constantes as cs


def main(page: ft.Page):

    for i in cs.horario:
        cs.columns.append(ft.DataColumn(label=i))

    for f in range(13):
        row_cells = []
        for c in range(7):
            if c == 0:
                new_hour = cs.object_hour + timedelta(minutes=cs.class_time)
                result = new_hour.strftime("%I:%M %p")
                row_cells.append(ft.DataCell(ft.Text(f"{cs.hour} - {result}")))
                cs.object_hour = new_hour
                cs.hour = result
            else:
                value = ((c - 1) * 13) + f
                row_cells.append(ft.DataCell(ft.Text(str(value))))
        cs.rows.append(ft.DataRow(cells=row_cells))

    horario = ft.DataTable(columns=cs.columns, rows=cs.rows)

    page.add(ft.Container(horario, alignment=ft.Alignment.CENTER))


ft.run(main)
