"""Punto de entrada de la aplicación Huellitas."""

from base_datos import BaseDatos
from interfaz import AplicacionHuellitas


def main() -> None:
    """Prepara la base de datos y abre la ventana principal."""
    base_datos = BaseDatos("huellitas.db")
    base_datos.crear_tablas()
    aplicacion = AplicacionHuellitas(base_datos)
    aplicacion.mainloop()


if __name__ == "__main__":
    main()
