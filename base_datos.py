"""Acceso a SQLite y operaciones CRUD de Huellitas."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from modelos import Cuidado, Mascota


class BaseDatos:
    def __init__(self, ruta: str | Path = "huellitas.db") -> None:
        self.ruta = str(ruta)

    @contextmanager
    def conectar(self) -> Iterator[sqlite3.Connection]:
        conexion = sqlite3.connect(self.ruta)
        conexion.row_factory = sqlite3.Row
        conexion.execute("PRAGMA foreign_keys = ON")
        try:
            yield conexion
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

    def crear_tablas(self) -> None:
        with self.conectar() as conexion:
            conexion.executescript(
                """
                CREATE TABLE IF NOT EXISTS mascotas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
                    especie TEXT NOT NULL CHECK (especie IN ('Perro', 'Gato')),
                    edad INTEGER NOT NULL CHECK (edad >= 0),
                    observaciones TEXT NOT NULL DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS cuidados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mascota_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL CHECK (tipo IN
                        ('Vacuna', 'Baño', 'Desparasitación', 'Cita veterinaria', 'Otro')),
                    fecha TEXT NOT NULL CHECK (
                        length(fecha) = 10 AND
                        substr(fecha, 5, 1) = '-' AND
                        substr(fecha, 8, 1) = '-'
                    ),
                    estado TEXT NOT NULL DEFAULT 'Pendiente'
                        CHECK (estado IN ('Pendiente', 'Realizado')),
                    observaciones TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY (mascota_id) REFERENCES mascotas(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_cuidados_mascota ON cuidados(mascota_id);
                CREATE INDEX IF NOT EXISTS idx_cuidados_fecha_estado ON cuidados(estado, fecha);
                """
            )

    def agregar_mascota(self, mascota: Mascota) -> int:
        mascota.validar()
        with self.conectar() as conexion:
            cursor = conexion.execute(
                "INSERT INTO mascotas (nombre, especie, edad, observaciones) VALUES (?, ?, ?, ?)",
                (mascota.nombre, mascota.especie, mascota.edad, mascota.observaciones),
            )
            return int(cursor.lastrowid)

    def listar_mascotas(self) -> list[dict]:
        with self.conectar() as conexion:
            filas = conexion.execute(
                "SELECT id, nombre, especie, edad, observaciones FROM mascotas ORDER BY nombre COLLATE NOCASE"
            ).fetchall()
        return [dict(fila) for fila in filas]

    def obtener_mascota(self, mascota_id: int) -> dict | None:
        with self.conectar() as conexion:
            fila = conexion.execute(
                "SELECT id, nombre, especie, edad, observaciones FROM mascotas WHERE id = ?",
                (mascota_id,),
            ).fetchone()
        return dict(fila) if fila else None

    def actualizar_mascota(self, mascota: Mascota) -> bool:
        mascota.validar()
        if mascota.id is None:
            raise ValueError("La mascota necesita un identificador para actualizarse.")
        with self.conectar() as conexion:
            cursor = conexion.execute(
                "UPDATE mascotas SET nombre = ?, especie = ?, edad = ?, observaciones = ? WHERE id = ?",
                (mascota.nombre, mascota.especie, mascota.edad, mascota.observaciones, mascota.id),
            )
            return cursor.rowcount == 1

    def eliminar_mascota(self, mascota_id: int) -> bool:
        with self.conectar() as conexion:
            cursor = conexion.execute("DELETE FROM mascotas WHERE id = ?", (mascota_id,))
            return cursor.rowcount == 1

    def agregar_cuidado(self, cuidado: Cuidado) -> int:
        cuidado.validar()
        with self.conectar() as conexion:
            if not conexion.execute("SELECT 1 FROM mascotas WHERE id = ?", (cuidado.mascota_id,)).fetchone():
                raise ValueError("La mascota seleccionada ya no existe.")
            cursor = conexion.execute(
                """INSERT INTO cuidados (mascota_id, tipo, fecha, estado, observaciones)
                   VALUES (?, ?, ?, ?, ?)""",
                (cuidado.mascota_id, cuidado.tipo, cuidado.fecha, cuidado.estado, cuidado.observaciones),
            )
            return int(cursor.lastrowid)

    def listar_cuidados(self) -> list[dict]:
        with self.conectar() as conexion:
            filas = conexion.execute(
                """SELECT c.id, c.mascota_id, m.nombre AS mascota, c.tipo,
                          c.fecha, c.estado, c.observaciones
                   FROM cuidados AS c
                   JOIN mascotas AS m ON m.id = c.mascota_id
                   ORDER BY CASE c.estado WHEN 'Pendiente' THEN 0 ELSE 1 END,
                            c.fecha, m.nombre COLLATE NOCASE"""
            ).fetchall()
        return [dict(fila) for fila in filas]

    def obtener_cuidado(self, cuidado_id: int) -> dict | None:
        with self.conectar() as conexion:
            fila = conexion.execute(
                "SELECT id, mascota_id, tipo, fecha, estado, observaciones FROM cuidados WHERE id = ?",
                (cuidado_id,),
            ).fetchone()
        return dict(fila) if fila else None

    def actualizar_cuidado(self, cuidado: Cuidado) -> bool:
        cuidado.validar()
        if cuidado.id is None:
            raise ValueError("El cuidado necesita un identificador para actualizarse.")
        with self.conectar() as conexion:
            cursor = conexion.execute(
                """UPDATE cuidados SET mascota_id = ?, tipo = ?, fecha = ?, estado = ?, observaciones = ?
                   WHERE id = ?""",
                (cuidado.mascota_id, cuidado.tipo, cuidado.fecha, cuidado.estado,
                 cuidado.observaciones, cuidado.id),
            )
            return cursor.rowcount == 1

    def marcar_realizado(self, cuidado_id: int) -> bool:
        with self.conectar() as conexion:
            cursor = conexion.execute(
                "UPDATE cuidados SET estado = 'Realizado' WHERE id = ?", (cuidado_id,)
            )
            return cursor.rowcount == 1

    def eliminar_cuidado(self, cuidado_id: int) -> bool:
        with self.conectar() as conexion:
            cursor = conexion.execute("DELETE FROM cuidados WHERE id = ?", (cuidado_id,))
            return cursor.rowcount == 1

    def esquema(self) -> list[dict]:
        """Devuelve la definición de las tablas para documentación o diagnóstico."""
        with self.conectar() as conexion:
            filas = conexion.execute(
                """SELECT name, sql FROM sqlite_master
                   WHERE type = 'table' AND name IN ('mascotas', 'cuidados') ORDER BY name"""
            ).fetchall()
        return [dict(fila) for fila in filas]
