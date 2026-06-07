from models import cliente_model as model


def registrar(nombre: str, telefono: str, correo: str) -> tuple[bool, str]:
    return model.crear_cliente(nombre, telefono, correo)


def listar(busqueda: str = "") -> list:
    return model.obtener_todos(busqueda)


def listar_para_venta() -> list:
    return model.obtener_todos_con_generico()


def actualizar(cliente_id: int, nombre: str, telefono: str, correo: str) -> tuple:
    from models import cliente_model as model
    return model.actualizar_cliente(cliente_id, nombre, telefono, correo)


def eliminar(cliente_id: int) -> tuple:
    from models import cliente_model as model
    return model.eliminar_cliente(cliente_id)
