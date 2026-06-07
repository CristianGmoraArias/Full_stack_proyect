"""
Sistema de Inventarios Local
Punto de entrada principal.
"""
import sys
import os

# Asegurar que el directorio del proyecto esté en el path
# para que los imports relativos funcionen correctamente
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import inicializar_db
from views.main_window import MainWindow


def main():
    # 1. Crear/verificar la base de datos y sus tablas
    inicializar_db()

    # 2. Lanzar la ventana principal
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
