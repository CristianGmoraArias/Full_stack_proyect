import customtkinter as ctk
from controllers import producto_controller as ctrl
from views.widgets import mostrar_mensaje, Tabla


class ProductoView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._productos_lista = []
        self._producto_seleccionado = None
        self._construir_ui()

    def on_tab_activado(self):
        self._recargar_todo()

    def _construir_ui(self):
        ctk.CTkLabel(
            self, text="Gestion de Productos e Inventario",
            font=ctk.CTkFont(size=22, weight="bold"), text_color="#E76F51"
        ).pack(anchor="w", padx=24, pady=(20, 4))

        ctk.CTkFrame(self, height=2, fg_color="#E76F51").pack(fill="x", padx=24, pady=(0, 10))

        self._tabs = ctk.CTkTabview(self, anchor="nw")
        self._tabs.pack(fill="both", expand=True, padx=24)

        for nombre in ["Inventario General", "Nuevo Producto", "Ingresar Stock", "Editar Producto"]:
            self._tabs.add(nombre)

        self._construir_inventario(self._tabs.tab("Inventario General"))
        self._construir_nuevo(self._tabs.tab("Nuevo Producto"))
        self._construir_stock(self._tabs.tab("Ingresar Stock"))
        self._construir_editar(self._tabs.tab("Editar Producto"))

        # Carga inicial
        self.after(100, self._recargar_todo)

    # ── Inventario general ────────────────────────────────────────────────────
    def _construir_inventario(self, tab):
        barra = ctk.CTkFrame(tab, fg_color="transparent")
        barra.pack(fill="x", pady=(12, 6), padx=8)

        ctk.CTkLabel(barra, text="Todos los productos",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        self._busq_inv = ctk.StringVar()
        self._busq_inv.trace_add("write", lambda *a: self._recargar_tabla())
        ctk.CTkEntry(barra, placeholder_text="Buscar...",
                     textvariable=self._busq_inv, width=200, height=32).pack(side="right")

        self._tabla_inv = Tabla(
            tab,
            columnas=[("Producto", 3), ("Descripcion", 3), ("Precio", 2), ("Stock", 1)],
            height=400
        )
        self._tabla_inv.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _recargar_todo(self):
        busqueda = self._busq_inv.get() if hasattr(self, "_busq_inv") else ""
        self._productos_lista = ctrl.listar(busqueda)
        self._recargar_tabla()
        self._sync_combo_stock()
        self._sync_combo_editar()

    def _recargar_tabla(self):
        busqueda = self._busq_inv.get() if hasattr(self, "_busq_inv") else ""
        self._productos_lista = ctrl.listar(busqueda)
        filas = [
            [p["nombre"],
             p["descripcion"] if p["descripcion"] else "-",
             f"${p['precio']:,.0f}",
             f"{p['stock']}  !!BAJO!!" if p["stock"] <= 5 else str(p["stock"])]
            for p in self._productos_lista
        ]
        self._tabla_inv.cargar(filas)

    # ── Nuevo producto ────────────────────────────────────────────────────────
    def _construir_nuevo(self, tab):
        frame = ctk.CTkFrame(tab, fg_color="transparent")
        frame.pack(expand=True, pady=20, padx=60)

        ctk.CTkLabel(frame, text="Crear Nuevo Producto",
                     font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 16), sticky="w"
        )

        self._ent_nuevo = {}
        campos = [
            ("Nombre del producto *", "n_nombre"),
            ("Descripcion",           "n_desc"),
            ("Precio de venta *",     "n_precio"),
            ("Stock inicial *",       "n_stock"),
        ]
        for i, (label, key) in enumerate(campos, start=1):
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12)).grid(
                row=i, column=0, sticky="w", padx=(0, 20), pady=6
            )
            e = ctk.CTkEntry(frame, width=300, height=36)
            e.grid(row=i, column=1, pady=6)
            self._ent_nuevo[key] = e

        ctk.CTkButton(
            frame, text="Crear Producto", height=40,
            fg_color="#E76F51", hover_color="#C85A3A",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._crear_producto
        ).grid(row=len(campos)+1, column=0, columnspan=2, pady=20, sticky="ew")

    def _crear_producto(self):
        ok, msg = ctrl.crear(
            self._ent_nuevo["n_nombre"].get(),
            self._ent_nuevo["n_desc"].get(),
            self._ent_nuevo["n_precio"].get(),
            self._ent_nuevo["n_stock"].get(),
        )

        if ok:
            def _post():
                for e in self._ent_nuevo.values():
                    e.delete(0, "end")
                self._recargar_todo()

            mostrar_mensaje(self,
                            titulo="Producto creado con exito",
                            mensaje=msg,
                            tipo="exito",
                            callback=_post)
        else:
            mostrar_mensaje(self,
                            titulo="Error al crear producto",
                            mensaje=msg,
                            tipo="error")

    # ── Ingresar stock ────────────────────────────────────────────────────────
    def _construir_stock(self, tab):
        frame = ctk.CTkFrame(tab, fg_color="transparent")
        frame.pack(expand=True, pady=30, padx=60)

        ctk.CTkLabel(frame, text="Selecciona el producto:",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 6))

        self._combo_stock_var = ctk.StringVar(value="-- Selecciona --")
        self._combo_stock = ctk.CTkComboBox(
            frame, variable=self._combo_stock_var,
            values=["-- Selecciona --"],
            width=360, height=36, state="readonly"
        )
        self._combo_stock.pack(pady=(0, 20))

        ctk.CTkLabel(frame, text="Cantidad a ingresar:",
                     font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 4))
        self._ent_cant_stock = ctk.CTkEntry(frame, width=180, height=36, placeholder_text="ej. 50")
        self._ent_cant_stock.pack(pady=(0, 24))

        ctk.CTkButton(
            frame, text="Ingresar Stock", height=40,
            fg_color="#E76F51", hover_color="#C85A3A",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._ingresar_stock
        ).pack()

    def _sync_combo_stock(self):
        nombres = [p["nombre"] for p in self._productos_lista]
        self._combo_stock.configure(values=nombres if nombres else ["-- Sin productos --"])
        self._combo_stock_var.set("-- Selecciona --")

    def _ingresar_stock(self):
        nombre = self._combo_stock_var.get()
        nombres = [p["nombre"] for p in self._productos_lista]
        if nombre not in nombres:
            mostrar_mensaje(self, "Aviso", "Selecciona un producto de la lista.", "error")
            return

        producto_id = self._productos_lista[nombres.index(nombre)]["id"]
        ok, msg = ctrl.agregar_stock(producto_id, self._ent_cant_stock.get())

        if ok:
            def _post():
                self._ent_cant_stock.delete(0, "end")
                self._recargar_todo()
            mostrar_mensaje(self, "Stock actualizado", msg, "exito", callback=_post)
        else:
            mostrar_mensaje(self, "Error", msg, "error")

    # ── Editar producto ───────────────────────────────────────────────────────
    def _construir_editar(self, tab):
        frame = ctk.CTkFrame(tab, fg_color="transparent")
        frame.pack(expand=True, pady=20, padx=60)

        ctk.CTkLabel(frame, text="Selecciona el producto a editar:",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 6))

        self._combo_editar_var = ctk.StringVar(value="-- Selecciona --")
        self._combo_editar = ctk.CTkComboBox(
            frame, variable=self._combo_editar_var,
            values=["-- Selecciona --"],
            width=360, height=36, state="readonly",
            command=self._on_cambio_editar
        )
        self._combo_editar.pack(pady=(0, 16))

        self._ent_editar = {}
        for label, key in [("Nombre *", "e_nombre"), ("Descripcion", "e_desc"), ("Precio *", "e_precio")]:
            fila = ctk.CTkFrame(frame, fg_color="transparent")
            fila.pack(fill="x", pady=4)
            ctk.CTkLabel(fila, text=label, width=110,
                         anchor="w", font=ctk.CTkFont(size=12)).pack(side="left")
            e = ctk.CTkEntry(fila, width=280, height=36)
            e.pack(side="left")
            self._ent_editar[key] = e

        ctk.CTkButton(
            frame, text="Guardar Cambios", height=40,
            fg_color="#E76F51", hover_color="#C85A3A",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._guardar_edicion
        ).pack(pady=20)

    def _sync_combo_editar(self):
        nombres = [p["nombre"] for p in self._productos_lista]
        self._combo_editar.configure(values=nombres if nombres else ["-- Sin productos --"])
        self._combo_editar_var.set("-- Selecciona --")
        for e in self._ent_editar.values():
            e.delete(0, "end")
        self._producto_seleccionado = None

    def _on_cambio_editar(self, nombre):
        nombres = [p["nombre"] for p in self._productos_lista]
        if nombre not in nombres:
            return
        p = self._productos_lista[nombres.index(nombre)]
        self._producto_seleccionado = p
        self._ent_editar["e_nombre"].delete(0, "end")
        self._ent_editar["e_nombre"].insert(0, p["nombre"])
        self._ent_editar["e_desc"].delete(0, "end")
        self._ent_editar["e_desc"].insert(0, p["descripcion"] or "")
        self._ent_editar["e_precio"].delete(0, "end")
        self._ent_editar["e_precio"].insert(0, str(p["precio"]))

    def _guardar_edicion(self):
        if not self._producto_seleccionado:
            mostrar_mensaje(self, "Aviso", "Selecciona un producto primero.", "error")
            return

        ok, msg = ctrl.actualizar(
            self._producto_seleccionado["id"],
            self._ent_editar["e_nombre"].get(),
            self._ent_editar["e_desc"].get(),
            self._ent_editar["e_precio"].get(),
        )

        if ok:
            def _post():
                self._recargar_todo()
            mostrar_mensaje(self, "Producto actualizado", msg, "exito", callback=_post)
        else:
            mostrar_mensaje(self, "Error", msg, "error")
