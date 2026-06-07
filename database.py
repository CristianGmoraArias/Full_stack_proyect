import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventario.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acceder a columnas por nombre
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS clientes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre     TEXT    NOT NULL,
            telefono   TEXT    DEFAULT '',
            correo     TEXT    DEFAULT '',
            created_at TEXT    DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS productos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT    NOT NULL,
            descripcion TEXT    DEFAULT '',
            precio      REAL    NOT NULL CHECK (precio >= 0),
            stock       INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
            created_at  TEXT    DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS ventas (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER REFERENCES clientes(id),
            total      REAL    NOT NULL DEFAULT 0,
            created_at TEXT    DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id        INTEGER NOT NULL REFERENCES ventas(id),
            producto_id     INTEGER NOT NULL REFERENCES productos(id),
            cantidad        INTEGER NOT NULL CHECK (cantidad > 0),
            precio_unitario REAL    NOT NULL
        );

        -- Cliente genérico para ventas sin cliente identificado
        INSERT OR IGNORE INTO clientes (id, nombre, telefono, correo)
        VALUES (1, 'Cliente Genérico', '', '');
    """)

    conn.commit()
    conn.close()
