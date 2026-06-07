from models import producto_model as model


def crear(nombre: str, descripcion: str, precio_str: str, stock_str: str) -> tuple[bool, str]:
    try:
        precio = float(precio_str.replace(",", "."))
        stock = int(stock_str)
    except ValueError:
        return False, "Precio y stock deben ser números válidos."
    return model.crear_producto(nombre, descripcion, precio, stock)


def listar(busqueda: str = "") -> list:
    return model.obtener_todos(busqueda)


def agregar_stock(producto_id: int, cantidad_str: str) -> tuple[bool, str]:
    try:
        cantidad = int(cantidad_str)
    except ValueError:
        return False, "La cantidad debe ser un número entero."
    return model.ingresar_stock(producto_id, cantidad)


def actualizar(producto_id: int, nombre: str, descripcion: str, precio_str: str) -> tuple[bool, str]:
    try:
        precio = float(precio_str.replace(",", "."))
    except ValueError:
        return False, "El precio debe ser un número válido."
    return model.actualizar_producto(producto_id, nombre, descripcion, precio)


def obtener(producto_id: int) -> dict | None:
    return model.obtener_por_id(producto_id)
