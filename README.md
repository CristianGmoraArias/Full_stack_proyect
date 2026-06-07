#  Sistema de Inventarios Local

Aplicación de escritorio para gestión de inventarios, clientes y ventas.
Construida con **Python + CustomTkinter + SQLite**.

---

##  Instalación

### Requisitos
- Python 3.11 o superior
- pip

### Pasos

```bash
# 1. Instalar dependencias (solo CustomTkinter; sqlite3 ya viene con Python)
pip install -r requirements.txt

# 2. Ejecutar la aplicación
python main.py
```

La primera vez que se ejecuta, se crea automáticamente el archivo `inventario.db`
en la misma carpeta. Ese archivo ES tu base de datos — guárdalo como backup.

---

##  Estructura del proyecto

```
inventario_app/
├── main.py              ← Punto de entrada
├── database.py          ← Inicialización de SQLite
├── requirements.txt
├── inventario.db        ← Se genera automáticamente
│
├── models/              ← Comunicación con la base de datos
│   ├── cliente_model.py
│   ├── producto_model.py
│   └── venta_model.py
│
├── views/               ← Interfaz gráfica (CustomTkinter)
│   ├── main_window.py
│   ├── cliente_view.py
│   ├── producto_view.py
│   ├── venta_view.py
│   └── widgets.py
│
└── controllers/         ← Lógica de negocio
    ├── cliente_controller.py
    ├── producto_controller.py
    └── venta_controller.py
```

---

##  Uso básico

### Flujo recomendado al iniciar
1. **Clientes** → Registra tus clientes.
2. **Productos** → Crea los productos con precio y stock inicial.
3. **Ventas** → Selecciona cliente + productos → Confirmar Venta.

### Generar una venta
1. Ve a la sección **Ventas → Nueva Venta**.
2. Busca y selecciona el producto en la lista izquierda.
3. Ingresa la cantidad y haz clic en **Agregar al carrito**.
4. Repite para más productos.
5. Selecciona el cliente (o deja "Cliente Genérico").
6. Haz clic en **Confirmar Venta**.

El stock se descuenta automáticamente. Si no hay existencias suficientes,
la venta **no se registra** y se muestra un mensaje de error.

---

##  Empaquetar como .exe (opcional)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Inventarios" main.py
```

El ejecutable quedará en la carpeta `dist/`.

---

##  Backup de datos

El archivo `inventario.db` contiene **toda** tu información.
Para hacer un respaldo, simplemente cópialo a otro lugar.
