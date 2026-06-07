import sqlite3
from database import get_connection


def crear_producto(nombre: str, descripcion: str, precio: float, stock: int) -> tuple:
    if not nombre.strip():
        return False, "El nombre del producto es obligatorio."
    if precio < 0:
        return False, "El precio no puede ser negativo."
    if stock < 0:
        return False, "El stock inicial no puede ser negativo."

    conn = get_connection()
    # Verificar nombre duplicado
    existe = conn.execute(
        "SELECT id FROM productos WHERE LOWER(nombre) = LOWER(?)", (nombre.strip(),)
    ).fetchone()
    if existe:
        conn.close()
        return False, f"Ya existe un producto con el nombre '{nombre.strip()}'. Usa un nombre diferente."

    try:
        conn.execute(
            "INSERT INTO productos (nombre, descripcion, precio, stock) VALUES (?, ?, ?, ?)",
            (nombre.strip(), descripcion.strip(), precio, stock)
        )
        conn.commit()
        conn.close()
        return True, f"Producto '{nombre.strip()}' creado con exito."
    except Exception as e:
        conn.close()
        return False, f"Error al crear producto: {e}"


def obtener_todos(busqueda: str = "") -> list:
    conn = get_connection()
    if busqueda.strip():
        rows = conn.execute(
            "SELECT * FROM productos WHERE nombre LIKE ? ORDER BY nombre",
            (f"%{busqueda}%",)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM productos ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtener_por_id(producto_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM productos WHERE id = ?", (producto_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def ingresar_stock(producto_id: int, cantidad: int) -> tuple:
    if cantidad <= 0:
        return False, "La cantidad a ingresar debe ser mayor a cero."
    try:
        conn = get_connection()
        res = conn.execute(
            "UPDATE productos SET stock = stock + ? WHERE id = ?", (cantidad, producto_id)
        )
        if res.rowcount == 0:
            conn.close()
            return False, "Producto no encontrado."
        conn.commit()
        conn.close()
        return True, f"Stock actualizado: +{cantidad} unidades agregadas."
    except Exception as e:
        return False, f"Error al actualizar stock: {e}"


def actualizar_producto(producto_id: int, nombre: str, descripcion: str, precio: float) -> tuple:
    if not nombre.strip():
        return False, "El nombre del producto es obligatorio."
    if precio < 0:
        return False, "El precio no puede ser negativo."

    conn = get_connection()
    # Verificar nombre duplicado (excluyendo el mismo producto)
    existe = conn.execute(
        "SELECT id FROM productos WHERE LOWER(nombre) = LOWER(?) AND id != ?",
        (nombre.strip(), producto_id)
    ).fetchone()
    if existe:
        conn.close()
        return False, f"Ya existe otro producto con el nombre '{nombre.strip()}'."

    try:
        conn.execute(
            "UPDATE productos SET nombre = ?, descripcion = ?, precio = ? WHERE id = ?",
            (nombre.strip(), descripcion.strip(), precio, producto_id)
        )
        conn.commit()
        conn.close()
        return True, "Producto actualizado con exito."
    except Exception as e:
        conn.close()
        return False, f"Error al actualizar producto: {e}"
