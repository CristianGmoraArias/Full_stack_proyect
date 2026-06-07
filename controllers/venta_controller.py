from models import venta_model as model


def confirmar_venta(cliente_id: int, carrito: list[dict]) -> tuple[bool, str]:
    if not carrito:
        return False, "El carrito está vacío. Agrega productos antes de confirmar."
    return model.registrar_venta(cliente_id, carrito)


def historico(busqueda: str = "") -> list:
    return model.obtener_historico(busqueda)


def detalle(venta_id: int) -> list:
    return model.obtener_detalle_venta(venta_id)
