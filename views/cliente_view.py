import customtkinter as ctk
from controllers import cliente_controller as ctrl
from views.widgets import mostrar_mensaje, confirmar_accion, Tabla


class ClienteView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._clientes_lista = []      # cache de clientes mostrados
        self._cliente_seleccionado = None
        self._construir_ui()

    def _construir_ui(self):
        ctk.CTkLabel(
            self, text="Gestion de Clientes",
            font=ctk.CTkFont(size=22, weight="bold"), text_color="#2A9D8F"
        ).pack(anchor="w", padx=24, pady=(20, 4))

        ctk.CTkFrame(self, height=2, fg_color="#2A9D8F").pack(fill="x", padx=24, pady=(0, 12))

        # Layout: columna izquierda (formularios) | columna derecha (tabla)
        contenedor = ctk.CTkFrame(self, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        contenedor.columnconfigure(0, weight=1)
        contenedor.columnconfigure(1, weight=2)
        contenedor.rowconfigure(0, weight=1)

        self._construir_panel_izq(contenedor)
        self._construir_tabla(contenedor)

    # ── Panel izquierdo: tabs de Registrar / Editar ───────────────────────────
    def _construir_panel_izq(self, parent):
        panel = ctk.CTkFrame(parent, corner_radius=12)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self._tabs_form = ctk.CTkTabview(panel, anchor="nw", height=340)
        self._tabs_form.pack(fill="both", expand=True, padx=8, pady=8)
        self._tabs_form.add("Nuevo Cliente")
        self._tabs_form.add("Editar Cliente")

        self._construir_form_nuevo(self._tabs_form.tab("Nuevo Cliente"))
        self._construir_form_editar(self._tabs_form.tab("Editar Cliente"))

    # ── Formulario: Nuevo cliente ─────────────────────────────────────────────
    def _construir_form_nuevo(self, tab):
        self._entradas = {}
        for label, key in [("Nombre *", "nombre"), ("Telefono", "telefono"), ("Correo", "correo")]:
            ctk.CTkLabel(tab, text=label, font=ctk.CTkFont(size=12)).pack(
                anchor="w", padx=4, pady=(8, 2)
            )
            e = ctk.CTkEntry(tab, placeholder_text=label, height=36)
            e.pack(fill="x", padx=4, pady=(0, 2))
            self._entradas[key] = e

        ctk.CTkButton(
            tab, text="Registrar Cliente", height=40,
            fg_color="#2A9D8F", hover_color="#21867A",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._registrar
        ).pack(fill="x", padx=4, pady=(16, 4))

    def _registrar(self):
        nombre   = self._entradas["nombre"].get().strip()
        telefono = self._entradas["telefono"].get().strip()
        correo   = self._entradas["correo"].get().strip()

        ok, msg = ctrl.registrar(nombre, telefono, correo)
        if ok:
            def _post():
                for e in self._entradas.values():
                    e.delete(0, "end")
                self._cargar_tabla()
            mostrar_mensaje(self, "Cliente creado con exito",
                            "El cliente fue registrado correctamente.", "exito", callback=_post)
        else:
            mostrar_mensaje(self, "Error al registrar", msg, "error")

    # ── Formulario: Editar cliente ────────────────────────────────────────────
    def _construir_form_editar(self, tab):
        self._lbl_editando = ctk.CTkLabel(
            tab, text="Selecciona un cliente\nen la tabla para editarlo.",
            font=ctk.CTkFont(size=12), text_color="gray"
        )
        self._lbl_editando.pack(pady=(12, 8))

        self._entradas_edit = {}
        for label, key in [("Nombre *", "nombre"), ("Telefono", "telefono"), ("Correo", "correo")]:
            ctk.CTkLabel(tab, text=label, font=ctk.CTkFont(size=12)).pack(
                anchor="w", padx=4, pady=(6, 2)
            )
            e = ctk.CTkEntry(tab, placeholder_text=label, height=36)
            e.pack(fill="x", padx=4, pady=(0, 2))
            self._entradas_edit[key] = e

        # Botones Guardar + Eliminar
        fila_btns = ctk.CTkFrame(tab, fg_color="transparent")
        fila_btns.pack(fill="x", padx=4, pady=(14, 4))

        ctk.CTkButton(
            fila_btns, text="Guardar cambios", height=38,
            fg_color="#2A9D8F", hover_color="#21867A",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._guardar_edicion
        ).pack(side="left", expand=True, padx=(0, 4))

        ctk.CTkButton(
            fila_btns, text="Eliminar cliente", height=38,
            fg_color="#E63946", hover_color="#B02A33",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._eliminar_cliente
        ).pack(side="left", expand=True)

    def _cargar_edicion(self, cliente: dict):
        """Rellena el formulario de edición con los datos del cliente seleccionado."""
        self._cliente_seleccionado = cliente
        self._lbl_editando.configure(
            text=f"Editando: {cliente['nombre']}",
            text_color="#2A9D8F"
        )
        self._entradas_edit["nombre"].delete(0, "end")
        self._entradas_edit["nombre"].insert(0, cliente["nombre"])
        self._entradas_edit["telefono"].delete(0, "end")
        self._entradas_edit["telefono"].insert(0, cliente["telefono"] or "")
        self._entradas_edit["correo"].delete(0, "end")
        self._entradas_edit["correo"].insert(0, cliente["correo"] or "")
        # Cambiar automáticamente al tab de edición
        self._tabs_form.set("Editar Cliente")

    def _guardar_edicion(self):
        if not self._cliente_seleccionado:
            mostrar_mensaje(self, "Aviso",
                            "Selecciona un cliente en la tabla primero.", "error")
            return
        ok, msg = ctrl.actualizar(
            self._cliente_seleccionado["id"],
            self._entradas_edit["nombre"].get(),
            self._entradas_edit["telefono"].get(),
            self._entradas_edit["correo"].get(),
        )
        if ok:
            def _post():
                self._cliente_seleccionado = None
                self._lbl_editando.configure(
                    text="Selecciona un cliente\nen la tabla para editarlo.",
                    text_color="gray"
                )
                for e in self._entradas_edit.values():
                    e.delete(0, "end")
                self._cargar_tabla()
            mostrar_mensaje(self, "Cliente actualizado", msg, "exito", callback=_post)
        else:
            mostrar_mensaje(self, "Error", msg, "error")

    def _eliminar_cliente(self):
        if not self._cliente_seleccionado:
            mostrar_mensaje(self, "Aviso",
                            "Selecciona un cliente en la tabla primero.", "error")
            return
        nombre = self._cliente_seleccionado["nombre"]
        confirmado = confirmar_accion(
            self,
            "Eliminar Cliente",
            f"Estas a punto de eliminar a '{nombre}'.\n"
            f"Esta accion no se puede deshacer.\n\n"
            f"Las ventas asociadas a este cliente se mantendran en el historico."
        )
        if not confirmado:
            return

        ok, msg = ctrl.eliminar(self._cliente_seleccionado["id"])
        if ok:
            def _post():
                self._cliente_seleccionado = None
                self._lbl_editando.configure(
                    text="Selecciona un cliente\nen la tabla para editarlo.",
                    text_color="gray"
                )
                for e in self._entradas_edit.values():
                    e.delete(0, "end")
                self._cargar_tabla()
                self._tabs_form.set("Nuevo Cliente")
            mostrar_mensaje(self, "Cliente eliminado", msg, "exito", callback=_post)
        else:
            mostrar_mensaje(self, "Error", msg, "error")

    # ── Tabla de clientes ─────────────────────────────────────────────────────
    def _construir_tabla(self, parent):
        panel = ctk.CTkFrame(parent, corner_radius=12)
        panel.grid(row=0, column=1, sticky="nsew")

        enc = ctk.CTkFrame(panel, fg_color="transparent")
        enc.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(enc, text="Clientes Registrados",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")

        self._busqueda_var = ctk.StringVar()
        self._busqueda_var.trace_add("write", lambda *a: self._cargar_tabla())
        ctk.CTkEntry(enc, placeholder_text="Buscar...",
                     textvariable=self._busqueda_var, width=180, height=32).pack(side="right")

        # Instrucción de selección
        ctk.CTkLabel(panel,
                     text="Haz clic en un cliente para editarlo o eliminarlo.",
                     font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w", padx=16)

        self._tabla = Tabla(
            panel,
            columnas=[("Nombre", 3), ("Telefono", 2), ("Correo", 3), ("Fecha", 2)],
            callback_seleccion=self._on_seleccionar,
            height=400
        )
        self._tabla.pack(fill="both", expand=True, padx=12, pady=(4, 12))
        self._cargar_tabla()

    def _on_seleccionar(self, fila_data):
        idx = self._tabla._fila_seleccionada
        if idx is not None and idx < len(self._clientes_lista):
            self._cargar_edicion(self._clientes_lista[idx])

    def _cargar_tabla(self):
        self._clientes_lista = ctrl.listar(self._busqueda_var.get())
        filas = [
            [c["nombre"],
             c["telefono"] if c["telefono"] else "-",
             c["correo"]   if c["correo"]   else "-",
             c["created_at"][:16]]
            for c in self._clientes_lista
        ]
        self._tabla.cargar(filas)
