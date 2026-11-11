"""Pruebas automatizadas de modelos, persistencia y operaciones CRUD."""

import tempfile
import unittest
from pathlib import Path

from base_datos import BaseDatos
from modelos import Cuidado, Mascota, fecha_a_iso, fecha_para_mostrar, obtener_pendientes


class PruebasHuellitas(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory()
        self.ruta = Path(self.temporal.name) / "prueba.db"
        self.base = BaseDatos(self.ruta)
        self.base.crear_tablas()

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def crear_mascota(self, nombre: str = "Luna") -> int:
        return self.base.agregar_mascota(Mascota(nombre, "Perro", 3, "Juguetona"))

    def test_registro_y_consulta_de_mascota(self) -> None:
        identificador = self.crear_mascota()
        mascotas = self.base.listar_mascotas()
        self.assertEqual(1, len(mascotas))
        self.assertEqual(identificador, mascotas[0]["id"])
        self.assertEqual("Luna", mascotas[0]["nombre"])

    def test_validacion_de_campos_obligatorios(self) -> None:
        with self.assertRaisesRegex(ValueError, "nombre"):
            self.base.agregar_mascota(Mascota("  ", "Perro", 2))
        with self.assertRaisesRegex(ValueError, "especie"):
            self.base.agregar_mascota(Mascota("Milo", "Ave", 2))
        with self.assertRaisesRegex(ValueError, "edad"):
            self.base.agregar_mascota(Mascota("Milo", "Gato", -1))

    def test_modificacion_de_mascota(self) -> None:
        identificador = self.crear_mascota()
        resultado = self.base.actualizar_mascota(Mascota("Luna", "Perro", 4, "Vacunada", identificador))
        self.assertTrue(resultado)
        self.assertEqual(4, self.base.obtener_mascota(identificador)["edad"])

    def test_eliminacion_de_mascota(self) -> None:
        identificador = self.crear_mascota()
        self.assertTrue(self.base.eliminar_mascota(identificador))
        self.assertEqual([], self.base.listar_mascotas())

    def test_registro_y_relacion_de_cuidado(self) -> None:
        mascota_id = self.crear_mascota()
        cuidado_id = self.base.agregar_cuidado(Cuidado(mascota_id, "Vacuna", "2026-11-15"))
        cuidado = self.base.obtener_cuidado(cuidado_id)
        self.assertEqual(mascota_id, cuidado["mascota_id"])
        self.assertEqual("Pendiente", cuidado["estado"])

    def test_cuidado_requiere_mascota_existente(self) -> None:
        with self.assertRaisesRegex(ValueError, "no existe"):
            self.base.agregar_cuidado(Cuidado(999, "Baño", "2026-12-01"))

    def test_modificacion_y_cambio_de_estado(self) -> None:
        mascota_id = self.crear_mascota()
        cuidado_id = self.base.agregar_cuidado(Cuidado(mascota_id, "Vacuna", "2026-11-15"))
        self.assertTrue(self.base.actualizar_cuidado(
            Cuidado(mascota_id, "Cita veterinaria", "2026-11-20", "Pendiente", "Control", cuidado_id)))
        self.assertTrue(self.base.marcar_realizado(cuidado_id))
        self.assertEqual("Realizado", self.base.obtener_cuidado(cuidado_id)["estado"])

    def test_eliminacion_en_cascada_controlada(self) -> None:
        mascota_id = self.crear_mascota()
        self.base.agregar_cuidado(Cuidado(mascota_id, "Baño", "2026-11-25"))
        self.base.eliminar_mascota(mascota_id)
        self.assertEqual([], self.base.listar_cuidados())

    def test_eliminacion_de_cuidado(self) -> None:
        mascota_id = self.crear_mascota()
        cuidado_id = self.base.agregar_cuidado(Cuidado(mascota_id, "Otro", "2026-12-01"))
        self.assertTrue(self.base.eliminar_cuidado(cuidado_id))
        self.assertIsNone(self.base.obtener_cuidado(cuidado_id))

    def test_persistencia_al_reabrir_la_base(self) -> None:
        self.crear_mascota("Max")
        otra_instancia = BaseDatos(self.ruta)
        otra_instancia.crear_tablas()
        self.assertEqual("Max", otra_instancia.listar_mascotas()[0]["nombre"])

    def test_conversion_y_validacion_de_fechas(self) -> None:
        self.assertEqual("2026-11-15", fecha_a_iso("15/11/2026"))
        self.assertEqual("15/11/2026", fecha_para_mostrar("2026-11-15"))
        with self.assertRaisesRegex(ValueError, "formato"):
            fecha_a_iso("31/02/2026")

    def test_transformacion_funcional_no_modifica_lista(self) -> None:
        originales = [
            {"id": 1, "fecha": "2026-12-10", "estado": "Pendiente"},
            {"id": 2, "fecha": "2026-11-10", "estado": "Realizado"},
            {"id": 3, "fecha": "2026-11-20", "estado": "Pendiente"},
        ]
        copia = [elemento.copy() for elemento in originales]
        pendientes = obtener_pendientes(originales)
        self.assertEqual([3, 1], [elemento["id"] for elemento in pendientes])
        self.assertEqual(copia, originales)


if __name__ == "__main__":
    unittest.main()
