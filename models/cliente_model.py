from database import get_connection


def crear_cliente(nombre: str, telefono: str = "", correo: str = "") -> tuple[bool, str]:
    if not nombre.strip():
        return False, "El nombre del cliente es obligatorio."
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO clientes (nombre, telefono, correo) VALUES (?, ?, ?)",
            (nombre.strip(), telefono.strip(), correo.strip())
        )
        conn.commit()
        conn.close()
        return True, "Cliente registrado con éxito."
    except Exception as e:
        return False, f"Error al registrar cliente: {e}"


def obtener_todos(busqueda: str = "") -> list:
    conn = get_connection()
    if busqueda.strip():
        rows = conn.execute(
            "SELECT * FROM clientes WHERE nombre LIKE ? AND id != 1 ORDER BY nombre",
            (f"%{busqueda}%",)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM clientes WHERE id != 1 ORDER BY nombre"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtener_por_id(cliente_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def obtener_todos_con_generico() -> list:
    """Para el selector de ventas: incluye Cliente Genérico."""
    conn = get_connection()
    rows = conn.execute("SELECT id, nombre FROM clientes ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def actualizar_cliente(cliente_id: int, nombre: str, telefono: str, correo: str) -> tuple:
    if not nombre.strip():
        return False, "El nombre del cliente es obligatorio."
    try:
        conn = get_connection()
        res = conn.execute(
            "UPDATE clientes SET nombre = ?, telefono = ?, correo = ? WHERE id = ?",
            (nombre.strip(), telefono.strip(), correo.strip(), cliente_id)
        )
        if res.rowcount == 0:
            conn.close()
            return False, "Cliente no encontrado."
        conn.commit()
        conn.close()
        return True, "Cliente actualizado con exito."
    except Exception as e:
        return False, f"Error al actualizar: {e}"


def eliminar_cliente(cliente_id: int) -> tuple:
    if cliente_id == 1:
        return False, "No se puede eliminar el Cliente Generico."
    try:
        conn = get_connection()
        conn.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()
        conn.close()
        return True, "Cliente eliminado correctamente."
    except Exception as e:
        return False, f"Error al eliminar: {e}"
