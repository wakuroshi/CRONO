import customtkinter as ctk
import mod_json


class CronoFrame(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.horario = None

        ctk.set_default_color_theme("dark-blue")
        self.title("CRONO")
        self.minsize(800, 600)
        self.grid_columnconfigure((0, 1), weight=1)

        self.button = ctk.CTkButton(self, text="Añadir Horario", command=self.get_txth)
        self.button.grid(row=1, column=1, padx=20, pady=10, sticky="nsew", columnspan=1)

        self.txth = ctk.CTkEntry(self, placeholder_text="Ingresa un Horario", width=320)
        self.txth.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.IdCatedra = ctk.CTkLabel(self, text="IdCatedra")
        self.IdCatedra.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")

    def get_txth(self):
        self.horario = self.txth.get()
        self.txth.delete(0, "end")

    def modificar_json(self):
        mod_json.Mod_Json(self.horario)


window = CronoFrame()

window.mainloop()
