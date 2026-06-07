import sqlite3
from database import DB_PATH, get_connection


def registrar_venta(cliente_id: int, items: list[dict]) -> tuple[bool, str]:
    """
    Registra una venta de forma atómica.
    items: [{"producto_id": int, "cantidad": int, "precio_unitario": float}, ...]
    Retorna (True, mensaje) o (False, error).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.isolation_level = None  # control manual de transacciones

    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN")

        # 1. Verificar stock suficiente para cada ítem
        for item in items:
            row = cursor.execute(
                "SELECT nombre, stock FROM productos WHERE id = ?",
                (item["producto_id"],)
            ).fetchone()

            if row is None:
                raise ValueError(f"Producto ID {item['producto_id']} no existe.")

            if row["stock"] < item["cantidad"]:
                raise ValueError(
                    f"Stock insuficiente para '{row['nombre']}'. "
                    f"Disponible: {row['stock']}, solicitado: {item['cantidad']}."
                )

        # 2. Calcular total
        total = sum(i["cantidad"] * i["precio_unitario"] for i in items)

        # 3. Insertar cabecera de venta
        cursor.execute(
            "INSERT INTO ventas (cliente_id, total) VALUES (?, ?)",
            (cliente_id, total)
        )
        venta_id = cursor.lastrowid

        # 4. Insertar detalles y descontar stock
        for item in items:
            cursor.execute(
                """INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario)
                   VALUES (?, ?, ?, ?)""",
                (venta_id, item["producto_id"], item["cantidad"], item["precio_unitario"])
            )
            cursor.execute(
                "UPDATE productos SET stock = stock - ? WHERE id = ?",
                (item["cantidad"], item["producto_id"])
            )

        cursor.execute("COMMIT")
        return True, f"Venta #{venta_id} registrada. Total: ${total:,.0f}"

    except ValueError as e:
        cursor.execute("ROLLBACK")
        return False, str(e)
    except sqlite3.Error as e:
        cursor.execute("ROLLBACK")
        return False, f"Error de base de datos: {e}"
    finally:
        conn.close()


def obtener_historico(busqueda: str = "") -> list:
    conn = get_connection()
    query = """
        SELECT
            v.id,
            COALESCE(c.nombre, 'Cliente Genérico') AS cliente,
            v.total,
            v.created_at,
            COUNT(d.id) AS num_items
        FROM ventas v
        LEFT JOIN clientes c ON v.cliente_id = c.id
        LEFT JOIN detalle_ventas d ON v.id = d.venta_id
        WHERE c.nombre LIKE ? OR v.id LIKE ?
        GROUP BY v.id
        ORDER BY v.created_at DESC
    """
    patron = f"%{busqueda}%" if busqueda.strip() else "%"
    rows = conn.execute(query, (patron, patron)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtener_detalle_venta(venta_id: int) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            p.nombre AS producto,
            d.cantidad,
            d.precio_unitario,
            (d.cantidad * d.precio_unitario) AS subtotal
        FROM detalle_ventas d
        JOIN productos p ON d.producto_id = p.id
        WHERE d.venta_id = ?
    """, (venta_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
