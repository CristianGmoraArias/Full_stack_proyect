import customtkinter as ctk
from controllers import venta_controller as vctrl
from controllers import cliente_controller as cctrl
from controllers import producto_controller as pctrl
from views.widgets import mostrar_mensaje, confirmar_accion, Tabla


class VentaView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._carrito = []
        self._productos_cache = []
        self._clientes_cache = []
        self._prod_seleccionado = None
        self._btn_productos = {}   # producto_id -> (CTkButton, color_original)
        self._construir_ui()

    def on_tab_activado(self):
        self._cargar_productos()
        self._recargar_clientes()
        self._recargar_historico()

    def _construir_ui(self):
        ctk.CTkLabel(
            self, text="Gestion de Ventas",
            font=ctk.CTkFont(size=22, weight="bold"), text_color="#6A0572"
        ).pack(anchor="w", padx=24, pady=(20, 4))

        ctk.CTkFrame(self, height=2, fg_color="#6A0572").pack(fill="x", padx=24, pady=(0, 10))

        self._tabs = ctk.CTkTabview(self, anchor="nw")
        self._tabs.pack(fill="both", expand=True, padx=24)
        self._tabs.add("Nueva Venta")
        self._tabs.add("Historico de Ventas")

        self._construir_nueva_venta(self._tabs.tab("Nueva Venta"))
        self._construir_historico(self._tabs.tab("Historico de Ventas"))

        self.after(150, self._cargar_productos)
        self.after(150, self._recargar_clientes)

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB: Nueva Venta
    # ═══════════════════════════════════════════════════════════════════════════
    def _construir_nueva_venta(self, tab):
        tab.columnconfigure(0, weight=2)
        tab.columnconfigure(1, weight=3)
        tab.rowconfigure(0, weight=1)

        # ── Catálogo izquierdo ────────────────────────────────────────────────
        panel_izq = ctk.CTkFrame(tab, corner_radius=12)
        panel_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=8)
        panel_izq.rowconfigure(2, weight=1)
        panel_izq.columnconfigure(0, weight=1)

        ctk.CTkLabel(panel_izq, text="Catalogo",
                     font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(14, 4)
        )

        self._busq_prod = ctk.StringVar()
        self._busq_prod.trace_add("write", lambda *a: self._filtrar_productos())
        ctk.CTkEntry(panel_izq, placeholder_text="Buscar...",
                     textvariable=self._busq_prod, height=32).grid(
            row=1, column=0, sticky="ew", padx=14, pady=(0, 6)
        )

        self._scroll_prods = ctk.CTkScrollableFrame(panel_izq, height=280)
        self._scroll_prods.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 8))

        # Controles de cantidad + agregar
        ctrl_frame = ctk.CTkFrame(panel_izq, fg_color="transparent")
        ctrl_frame.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 14))

        fila_cant = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        fila_cant.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(fila_cant, text="Cantidad:", font=ctk.CTkFont(size=12)).pack(side="left")
        self._ent_cantidad = ctk.CTkEntry(fila_cant, width=80, height=34)
        self._ent_cantidad.insert(0, "1")
        self._ent_cantidad.pack(side="right")

        ctk.CTkButton(
            ctrl_frame, text="Agregar al carrito", height=38,
            fg_color="#6A0572", hover_color="#4E0558",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._agregar_al_carrito
        ).pack(fill="x")

        # ── Carrito derecho ───────────────────────────────────────────────────
        panel_der = ctk.CTkFrame(tab, corner_radius=12)
        panel_der.grid(row=0, column=1, sticky="nsew", pady=8)

        ctk.CTkLabel(panel_der, text="Carrito de Venta",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=14, pady=(14, 6)
        )

        # Selector cliente
        fila_cli = ctk.CTkFrame(panel_der, fg_color="transparent")
        fila_cli.pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkLabel(fila_cli, text="Cliente:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 8))
        self._cliente_var = ctk.StringVar(value="Cliente Generico")
        self._combo_cliente = ctk.CTkComboBox(
            fila_cli, variable=self._cliente_var,
            values=["Cliente Generico"], width=260, height=34, state="readonly"
        )
        self._combo_cliente.pack(side="left")

        # Tabla carrito
        self._tabla_carrito = Tabla(
            panel_der,
            columnas=[("Producto", 3), ("Cant.", 1), ("Precio unit.", 2), ("Subtotal", 2)],
            height=230
        )
        self._tabla_carrito.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        # Total
        self._lbl_total = ctk.CTkLabel(
            panel_der, text="Total: $0",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#6A0572"
        )
        self._lbl_total.pack(anchor="e", padx=14, pady=4)

        # Botones
        fila_btns = ctk.CTkFrame(panel_der, fg_color="transparent")
        fila_btns.pack(fill="x", padx=14, pady=(0, 14))

        ctk.CTkButton(
            fila_btns, text="Limpiar carrito", height=38,
            fg_color="#E63946", hover_color="#B02A33",
            command=self._limpiar_carrito
        ).pack(side="left", expand=True, padx=(0, 6))

        ctk.CTkButton(
            fila_btns, text="Confirmar Venta", height=38,
            fg_color="#2A9D8F", hover_color="#21867A",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._confirmar_venta
        ).pack(side="left", expand=True)

    # ── Catálogo ──────────────────────────────────────────────────────────────
    def _cargar_productos(self):
        self._productos_cache = pctrl.listar()
        self._prod_seleccionado = None
        self._filtrar_productos()

    def _filtrar_productos(self):
        busqueda = self._busq_prod.get().lower() if hasattr(self, "_busq_prod") else ""
        filtrados = [p for p in self._productos_cache
                     if busqueda in p["nombre"].lower()] if busqueda else self._productos_cache

        for w in self._scroll_prods.winfo_children():
            w.destroy()
        self._btn_productos.clear()

        for p in filtrados:
            # Color del borde según stock
            if p["stock"] == 0:
                color_borde = "#E63946"
                stock_txt   = "Sin stock"
            elif p["stock"] <= 5:
                color_borde = "#E76F51"
                stock_txt   = f"Stock: {p['stock']}"
            else:
                color_borde = "#2A9D8F"
                stock_txt   = f"Stock: {p['stock']}"

            texto = f"{p['nombre']}   ${p['precio']:,.0f}   {stock_txt}"
            btn = ctk.CTkButton(
                self._scroll_prods,
                text=texto, anchor="w", height=38,
                fg_color="transparent",
                border_width=2, border_color=color_borde,
                hover_color=("#DDDDDD", "#2A2A3A"),   # claro / oscuro
                text_color=("#111111", "#EEEEEE"),     # negro en claro, blanco en oscuro
                font=ctk.CTkFont(size=12),
                command=lambda prod=p: self._seleccionar_producto(prod)
            )
            btn.pack(fill="x", pady=2)
            self._btn_productos[p["id"]] = (btn, color_borde)

    def _seleccionar_producto(self, producto):
        # Quitar resaltado del anterior
        if self._prod_seleccionado and self._prod_seleccionado["id"] in self._btn_productos:
            btn, color_orig = self._btn_productos[self._prod_seleccionado["id"]]
            try:
                btn.configure(fg_color="transparent", border_color=color_orig)
            except Exception:
                pass

        self._prod_seleccionado = producto

        # Resaltar el nuevo
        if producto["id"] in self._btn_productos:
            btn, _ = self._btn_productos[producto["id"]]
            try:
                btn.configure(fg_color="#6A0572", border_color="#6A0572")
            except Exception:
                pass

        self._ent_cantidad.delete(0, "end")
        self._ent_cantidad.insert(0, "1")

    def _agregar_al_carrito(self):
        if not self._prod_seleccionado:
            mostrar_mensaje(self, "Aviso", "Selecciona un producto del catalogo primero.", "error")
            return

        try:
            cantidad = int(self._ent_cantidad.get() or "1")
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            mostrar_mensaje(self, "Error", "La cantidad debe ser un numero entero positivo.", "error")
            return

        prod = self._prod_seleccionado

        if prod["stock"] == 0:
            mostrar_mensaje(self, "Sin stock",
                            f"'{prod['nombre']}' no tiene stock disponible.", "error")
            return

        ya_en_carrito = sum(i["cantidad"] for i in self._carrito if i["producto_id"] == prod["id"])
        disponible = prod["stock"] - ya_en_carrito

        if cantidad > disponible:
            mostrar_mensaje(self, "Stock insuficiente",
                            f"Solo puedes agregar {disponible} unidad(es) mas de '{prod['nombre']}'.\n"
                            f"Stock total: {prod['stock']}  |  Ya en carrito: {ya_en_carrito}", "error")
            return

        # Agregar o sumar
        for item in self._carrito:
            if item["producto_id"] == prod["id"]:
                item["cantidad"] += cantidad
                self._refrescar_carrito()
                return

        self._carrito.append({
            "producto_id":    prod["id"],
            "nombre":         prod["nombre"],
            "cantidad":       cantidad,
            "precio_unitario": prod["precio"],
        })
        self._refrescar_carrito()

    def _refrescar_carrito(self):
        filas = [
            [i["nombre"], i["cantidad"],
             f"${i['precio_unitario']:,.0f}",
             f"${i['cantidad'] * i['precio_unitario']:,.0f}"]
            for i in self._carrito
        ]
        self._tabla_carrito.cargar(filas)
        total = sum(i["cantidad"] * i["precio_unitario"] for i in self._carrito)
        self._lbl_total.configure(text=f"Total: ${total:,.0f}")

    def _limpiar_carrito(self):
        self._carrito.clear()
        self._refrescar_carrito()

    def _recargar_clientes(self):
        self._clientes_cache = cctrl.listar_para_venta()
        nombres = [c["nombre"] for c in self._clientes_cache]
        self._combo_cliente.configure(values=nombres if nombres else ["Cliente Generico"])
        self._cliente_var.set("Cliente Generico")

    def _confirmar_venta(self):
        if not self._carrito:
            mostrar_mensaje(self, "Carrito vacio",
                            "Agrega al menos un producto antes de confirmar.", "error")
            return

        nombre_cliente = self._cliente_var.get()
        cliente_id = 1
        for c in self._clientes_cache:
            if c["nombre"] == nombre_cliente:
                cliente_id = c["id"]
                break

        total      = sum(i["cantidad"] * i["precio_unitario"] for i in self._carrito)
        n_productos = len(self._carrito)
        n_unidades  = sum(i["cantidad"] for i in self._carrito)

        confirmado = confirmar_accion(
            self,
            "Confirmar Venta",
            f"Cliente: {nombre_cliente}\n"
            f"{n_productos} producto(s)  |  {n_unidades} unidad(es)\n"
            f"Total a cobrar: ${total:,.0f}"
        )
        if not confirmado:
            return

        items = [
            {"producto_id":    i["producto_id"],
             "cantidad":       i["cantidad"],
             "precio_unitario": i["precio_unitario"]}
            for i in self._carrito
        ]

        ok, msg = vctrl.confirmar_venta(cliente_id, items)

        if ok:
            def _post_venta():
                self._limpiar_carrito()
                self._cargar_productos()
                self._recargar_historico()
                self._prod_seleccionado = None

            mostrar_mensaje(self,
                            titulo="Venta Exitosa",
                            mensaje=msg,
                            tipo="exito",
                            callback=_post_venta)
        else:
            mostrar_mensaje(self, "Error en la venta", msg, "error")

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB: Histórico
    # ═══════════════════════════════════════════════════════════════════════════
    def _construir_historico(self, tab):
        barra = ctk.CTkFrame(tab, fg_color="transparent")
        barra.pack(fill="x", padx=8, pady=(12, 6))

        ctk.CTkLabel(barra, text="Historial de Ventas",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        self._busq_hist = ctk.StringVar()
        self._busq_hist.trace_add("write", lambda *a: self._recargar_historico())
        ctk.CTkEntry(barra, placeholder_text="Buscar por cliente o # venta...",
                     textvariable=self._busq_hist, width=260, height=32).pack(side="right")

        self._tabla_hist = Tabla(
            tab,
            columnas=[("# Venta", 1), ("Cliente", 3), ("Items", 1), ("Total", 2), ("Fecha", 3)],
            callback_seleccion=self._on_seleccionar_venta,
            height=220
        )
        self._tabla_hist.pack(fill="x", padx=8, pady=(0, 8))

        ctk.CTkLabel(tab, text="Detalle de la venta seleccionada:",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=8, pady=(4, 2))

        self._tabla_detalle = Tabla(
            tab,
            columnas=[("Producto", 4), ("Cantidad", 1), ("Precio unit.", 2), ("Subtotal", 2)],
            height=160
        )
        self._tabla_detalle.pack(fill="x", padx=8, pady=(0, 8))
        self._ventas_cache = []

    def _recargar_historico(self):
        busqueda = self._busq_hist.get() if hasattr(self, "_busq_hist") else ""
        self._ventas_cache = vctrl.historico(busqueda)
        filas = [
            [f"#{v['id']}", v["cliente"], v["num_items"],
             f"${v['total']:,.0f}", v["created_at"][:16]]
            for v in self._ventas_cache
        ]
        self._tabla_hist.cargar(filas)
        self._tabla_detalle.cargar([])

    def _on_seleccionar_venta(self, fila_data):
        idx = self._tabla_hist._fila_seleccionada
        if idx is None or idx >= len(self._ventas_cache):
            return
        detalles = vctrl.detalle(self._ventas_cache[idx]["id"])
        filas = [
            [d["producto"], d["cantidad"],
             f"${d['precio_unitario']:,.0f}", f"${d['subtotal']:,.0f}"]
            for d in detalles
        ]
        self._tabla_detalle.cargar(filas)
