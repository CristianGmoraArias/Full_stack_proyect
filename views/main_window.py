import tkinter as tk
import customtkinter as ctk
from views.cliente_view import ClienteView
from views.producto_view import ProductoView
from views.venta_view import VentaView


def _dibujar_icono_caja(parent, size=48):
    """
    Dibuja una caja/paquete usando Canvas con líneas blancas,
    visible tanto en modo oscuro como claro.
    """
    canvas = tk.Canvas(parent, width=size, height=size,
                       bg="#0F1923", highlightthickness=0)

    s = size
    m = int(s * 0.12)   # margen
    # Cara frontal del cubo
    # Base inferior
    canvas.create_rectangle(m, int(s*0.45), s-m, s-m,
                            outline="white", fill="", width=2)
    # Tapa superior (trapecio simulado con líneas)
    cx = s // 2
    top_y = int(s * 0.12)
    canvas.create_line(m,   int(s*0.45), cx,  top_y,    fill="white", width=2)
    canvas.create_line(s-m, int(s*0.45), s-cx, top_y,   fill="white", width=2)
    canvas.create_line(cx,  top_y,       s-cx, top_y,   fill="white", width=2)
    # Línea central de la tapa (lacito)
    canvas.create_line(cx, top_y, cx, int(s*0.45), fill="white", width=2)
    # Línea horizontal del lazo en la caja
    mid_y = int(s * 0.62)
    canvas.create_line(m, mid_y, s-m, mid_y, fill="white", width=2)

    return canvas


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Inventarios")
        self.geometry("1100x680")
        self.minsize(900, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._modo_oscuro = True
        self._construir_ui()

    def _construir_ui(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # ── Barra lateral ─────────────────────────────────────────────────────
        self._sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#0F1923")
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)

        # Ícono de caja dibujado con Canvas (siempre blanco, visible en ambos modos)
        self._canvas_icono = _dibujar_icono_caja(self._sidebar, size=52)
        self._canvas_icono.pack(pady=(28, 4))

        ctk.CTkLabel(
            self._sidebar,
            text="Sistema de\nInventarios",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(pady=(4, 24))

        ctk.CTkFrame(self._sidebar, height=1, fg_color="#2A3A4A").pack(
            fill="x", padx=20, pady=(0, 16)
        )

        # Botones de navegación
        nav_items = [
            ("  Clientes",  "clientes",  "#2A9D8F"),
            ("  Productos", "productos", "#E76F51"),
            ("  Ventas",    "ventas",    "#6A0572"),
        ]
        self._btn_nav = {}
        for texto, clave, color in nav_items:
            btn = ctk.CTkButton(
                self._sidebar,
                text=texto, anchor="w", height=46,
                font=ctk.CTkFont(size=14),
                fg_color="transparent", hover_color=color,
                text_color="white", corner_radius=8,
                command=lambda c=clave: self._navegar(c)
            )
            btn.pack(fill="x", padx=12, pady=4)
            self._btn_nav[clave] = (btn, color)

        # Switch modo oscuro/claro al fondo
        ctk.CTkFrame(self._sidebar, height=1, fg_color="#2A3A4A").pack(
            fill="x", padx=20, pady=16, side="bottom"
        )
        self._switch_modo = ctk.CTkSwitch(
            self._sidebar, text="Modo oscuro",
            font=ctk.CTkFont(size=12), text_color="white",
            command=self._toggle_modo
        )
        self._switch_modo.pack(pady=12, side="bottom")
        self._switch_modo.select()

        # ── Área de contenido ─────────────────────────────────────────────────
        self._contenido = ctk.CTkFrame(self, corner_radius=0,
                                       fg_color=("gray95", "#141B22"))
        self._contenido.grid(row=0, column=1, sticky="nsew")
        self._contenido.rowconfigure(0, weight=1)
        self._contenido.columnconfigure(0, weight=1)

        self._vistas = {
            "clientes":  ClienteView(self._contenido),
            "productos": ProductoView(self._contenido),
            "ventas":    VentaView(self._contenido),
        }
        for vista in self._vistas.values():
            vista.grid(row=0, column=0, sticky="nsew")

        self._navegar("clientes")

    def _navegar(self, seccion: str):
        for clave, (btn, color) in self._btn_nav.items():
            btn.configure(fg_color=color if clave == seccion else "transparent")
        for clave, vista in self._vistas.items():
            if clave == seccion:
                vista.tkraise()
                if hasattr(vista, "on_tab_activado"):
                    vista.on_tab_activado()

    def _toggle_modo(self):
        self._modo_oscuro = self._switch_modo.get() == 1
        if self._modo_oscuro:
            ctk.set_appearance_mode("dark")
            self._switch_modo.configure(text="Modo oscuro")
            color_sidebar = "#0F1923"
        else:
            ctk.set_appearance_mode("light")
            self._switch_modo.configure(text="Modo claro")
            color_sidebar = "#1A2B3C"

        self._sidebar.configure(fg_color=color_sidebar)
        # Actualizar fondo del canvas del ícono
        self._canvas_icono.configure(bg=color_sidebar)
