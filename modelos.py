"""Modelos y validaciones sencillas de Huellitas."""

from dataclasses import dataclass
from datetime import datetime


ESPECIES = ("Perro", "Gato")
TIPOS_CUIDADO = ("Vacuna", "Baño", "Desparasitación", "Cita veterinaria", "Otro")
ESTADOS = ("Pendiente", "Realizado")


def fecha_a_iso(fecha: str) -> str:
    """Convierte DD/MM/AAAA a AAAA-MM-DD y rechaza fechas inválidas."""
    try:
        return datetime.strptime(fecha.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError as error:
        raise ValueError("La fecha debe ser válida y tener el formato DD/MM/AAAA.") from error


def fecha_para_mostrar(fecha_iso: str) -> str:
    """Convierte una fecha almacenada como AAAA-MM-DD a DD/MM/AAAA."""
    return datetime.strptime(fecha_iso, "%Y-%m-%d").strftime("%d/%m/%Y")


@dataclass
class Mascota:
    nombre: str
    especie: str
    edad: int
    observaciones: str = ""
    id: int | None = None

    def validar(self) -> None:
        self.nombre = self.nombre.strip()
        self.especie = self.especie.strip().title()
        self.observaciones = self.observaciones.strip()
        if not self.nombre:
            raise ValueError("El nombre de la mascota es obligatorio.")
        if self.especie not in ESPECIES:
            raise ValueError("La especie debe ser Perro o Gato.")
        if isinstance(self.edad, bool) or not isinstance(self.edad, int) or self.edad < 0:
            raise ValueError("La edad debe ser un número entero mayor o igual a cero.")


@dataclass
class Cuidado:
    mascota_id: int
    tipo: str
    fecha: str
    estado: str = "Pendiente"
    observaciones: str = ""
    id: int | None = None

    def validar(self) -> None:
        self.tipo = self.tipo.strip()
        self.estado = self.estado.strip().title()
        self.observaciones = self.observaciones.strip()
        if isinstance(self.mascota_id, bool) or not isinstance(self.mascota_id, int) or self.mascota_id <= 0:
            raise ValueError("Debe seleccionar una mascota válida.")
        if self.tipo not in TIPOS_CUIDADO:
            raise ValueError("Seleccione un tipo de cuidado válido.")
        datetime.strptime(self.fecha, "%Y-%m-%d")
        if self.estado not in ESTADOS:
            raise ValueError("El estado debe ser Pendiente o Realizado.")


def obtener_pendientes(cuidados: list[dict]) -> list[dict]:
    """Ejemplo funcional: crea otra lista sin modificar la lista original."""
    return sorted(
        [cuidado.copy() for cuidado in cuidados if cuidado["estado"] == "Pendiente"],
        key=lambda cuidado: cuidado["fecha"],
    )
