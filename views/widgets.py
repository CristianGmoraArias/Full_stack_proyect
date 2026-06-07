"""Widgets y helpers reutilizables en toda la aplicación."""
import customtkinter as ctk


def _crear_dialogo_base(parent, titulo: str, ancho: int = 420, alto: int = 210):
    """
    Crea un CTkToplevel correctamente en Ubuntu/Linux.
    El truco: withdraw → construir contenido → deiconify → after() para grab_set.
    """
    root = parent.winfo_toplevel()
    d = ctk.CTkToplevel(root)
    d.withdraw()          # ocultarlo mientras se construye
    d.title(titulo)
    d.geometry(f"{ancho}x{alto}")
    d.resizable(False, False)

    # Centrar sobre la ventana padre
    root.update_idletasks()
    rx = root.winfo_x() + root.winfo_width() // 2 - ancho // 2
    ry = root.winfo_y() + root.winfo_height() // 2 - alto // 2
    d.geometry(f"{ancho}x{alto}+{rx}+{ry}")

    return d


def _mostrar_dialogo(d):
    """Muestra el diálogo y aplica grab_set con retardo para que Linux lo dibuje bien."""
    d.deiconify()
    d.lift()
    d.focus_force()
    d.after(50, d.grab_set)   # <-- el retardo es la clave en Ubuntu


def mostrar_mensaje(parent, titulo: str, mensaje: str, tipo: str = "info", callback=None):
    """
    Ventana de diálogo con mensaje y botón Aceptar.
    callback: función que se ejecuta al presionar Aceptar (para recargar vistas).
    """
    color = "#2A9D8F" if tipo == "exito" else "#E63946" if tipo == "error" else "#457B9D"
    icono = "✓" if tipo == "exito" else "✗" if tipo == "error" else "i"

    d = _crear_dialogo_base(parent, titulo, 440, 220)

    # Contenido
    ctk.CTkLabel(
        d,
        text=f"  {icono}  {titulo}",
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color=color,
        anchor="w"
    ).pack(fill="x", pady=(28, 6), padx=24)

    ctk.CTkLabel(
        d,
        text=mensaje,
        font=ctk.CTkFont(size=13),
        wraplength=390,
        justify="left",
        anchor="w"
    ).pack(fill="x", padx=24, pady=(0, 16))

    def _cerrar():
        d.destroy()
        if callback:
            callback()

    ctk.CTkButton(
        d,
        text="Aceptar",
        width=130, height=38,
        fg_color=color,
        font=ctk.CTkFont(size=13, weight="bold"),
        command=_cerrar
    ).pack(pady=(0, 20))

    _mostrar_dialogo(d)


def confirmar_accion(parent, titulo: str, mensaje: str) -> bool:
    """Diálogo Sí / Cancelar. Bloquea hasta que el usuario responda."""
    resultado = [False]

    d = _crear_dialogo_base(parent, titulo, 460, 230)

    ctk.CTkLabel(
        d,
        text=f"  !  {titulo}",
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color="#E76F51",
        anchor="w"
    ).pack(fill="x", pady=(28, 6), padx=24)

    ctk.CTkLabel(
        d,
        text=mensaje,
        font=ctk.CTkFont(size=13),
        wraplength=410,
        justify="left",
        anchor="w"
    ).pack(fill="x", padx=24, pady=(0, 20))

    frame_btns = ctk.CTkFrame(d, fg_color="transparent")
    frame_btns.pack()

    def _confirmar():
        resultado[0] = True
        d.destroy()

    ctk.CTkButton(
        frame_btns, text="Si, confirmar",
        fg_color="#2A9D8F", width=150, height=38,
        font=ctk.CTkFont(size=13, weight="bold"),
        command=_confirmar
    ).pack(side="left", padx=8)

    ctk.CTkButton(
        frame_btns, text="Cancelar",
        fg_color="#E63946", width=150, height=38,
        font=ctk.CTkFont(size=13, weight="bold"),
        command=d.destroy
    ).pack(side="left", padx=8)

    _mostrar_dialogo(d)
    d.wait_window()
    return resultado[0]


class Tabla(ctk.CTkScrollableFrame):
    """Tabla genérica con encabezados, filas alternadas y selección."""

    def __init__(self, parent, columnas: list, callback_seleccion=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.columnas = columnas
        self.callback_seleccion = callback_seleccion
        self._filas_widgets = []
        self._datos = []
        self._fila_seleccionada = None
        self._construir_encabezado()

    def _construir_encabezado(self):
        frame = ctk.CTkFrame(self, fg_color="#1F3A5F", corner_radius=6)
        frame.pack(fill="x", padx=2, pady=(2, 0))
        for titulo, _ in self.columnas:
            ctk.CTkLabel(
                frame, text=titulo,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white", anchor="w"
            ).pack(side="left", expand=True, fill="x", padx=8, pady=6)

    def cargar(self, datos: list):
        for w in self._filas_widgets:
            try:
                w.destroy()
            except Exception:
                pass
        self._filas_widgets.clear()
        self._datos = datos
        self._fila_seleccionada = None

        if not datos:
            lbl = ctk.CTkLabel(self, text="Sin resultados.",
                               font=ctk.CTkFont(size=12), text_color="gray")
            lbl.pack(pady=20)
            self._filas_widgets.append(lbl)
            return

        for i, fila in enumerate(datos):
            color_bg = "#2B2D42" if i % 2 == 0 else "#1E1E2E"
            fr = ctk.CTkFrame(self, fg_color=color_bg, corner_radius=4)
            fr.pack(fill="x", padx=2, pady=1)

            for valor in fila:
                lbl = ctk.CTkLabel(
                    fr, text=str(valor),
                    font=ctk.CTkFont(size=12), anchor="w", text_color="#E0E0E0"
                )
                lbl.pack(side="left", expand=True, fill="x", padx=8, pady=5)
                lbl.bind("<Button-1>", lambda e, idx=i: self._on_click(idx))

            fr.bind("<Button-1>", lambda e, idx=i: self._on_click(idx))
            self._filas_widgets.append(fr)

    def _on_click(self, idx: int):
        if self._fila_seleccionada is not None:
            try:
                old = self._filas_widgets[self._fila_seleccionada]
                color = "#2B2D42" if self._fila_seleccionada % 2 == 0 else "#1E1E2E"
                old.configure(fg_color=color)
            except Exception:
                pass

        self._fila_seleccionada = idx
        try:
            self._filas_widgets[idx].configure(fg_color="#2A9D8F")
        except Exception:
            pass

        if self.callback_seleccion and idx < len(self._datos):
            self.callback_seleccion(self._datos[idx])
