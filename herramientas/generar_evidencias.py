"""Genera imágenes de evidencia a partir de resultados reales del proyecto."""

import sqlite3
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


RAIZ = Path(__file__).resolve().parent.parent
EVIDENCIAS = RAIZ / "evidencias"


def fuente(tamano: int, negrita: bool = False) -> ImageFont.FreeTypeFont:
    nombre = "segoeuib.ttf" if negrita else "segoeui.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / nombre), tamano)


def crear_imagen(titulo: str, lineas: list[str], destino: Path) -> None:
    ancho = 1400
    alto = max(520, 150 + len(lineas) * 29)
    imagen = Image.new("RGB", (ancho, alto), "#F7F9F8")
    dibujo = ImageDraw.Draw(imagen)
    dibujo.rectangle((0, 0, ancho, 92), fill="#4F8A6B")
    dibujo.text((42, 25), titulo, font=fuente(30, True), fill="white")
    y = 125
    for linea in lineas:
        color = "#35664D" if linea.startswith(("OK", "Ran ", "TABLA", "ÍNDICE")) else "#26332D"
        dibujo.text((42, y), linea, font=fuente(18), fill=color)
        y += 29
    imagen.save(destino)


def evidencia_pruebas() -> None:
    resultado = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "pruebas", "-v"],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        check=False,
    )
    salida = (resultado.stdout + resultado.stderr).strip()
    (EVIDENCIAS / "resultado_pruebas.txt").write_text(salida + "\n", encoding="utf-8")
    lineas = [linea for linea in salida.splitlines() if linea.strip()]
    crear_imagen("Resultado real de las pruebas automatizadas", lineas,
                 EVIDENCIAS / "05_resultado_pruebas.png")
    if resultado.returncode != 0:
        raise SystemExit("Las pruebas fallaron; no se puede generar evidencia de aprobación.")


def evidencia_base_datos() -> None:
    conexion = sqlite3.connect(RAIZ / "huellitas.db")
    try:
        tablas = conexion.execute(
            "SELECT name, sql FROM sqlite_master WHERE type = 'table' AND name IN ('mascotas', 'cuidados') ORDER BY name"
        ).fetchall()
        indices = conexion.execute(
            "SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND name LIKE 'idx_%' ORDER BY name"
        ).fetchall()
        foraneas = conexion.execute("PRAGMA foreign_key_list(cuidados)").fetchall()
        conteos = {
            "mascotas": conexion.execute("SELECT COUNT(*) FROM mascotas").fetchone()[0],
            "cuidados": conexion.execute("SELECT COUNT(*) FROM cuidados").fetchone()[0],
        }
    finally:
        conexion.close()

    lineas = ["Archivo inspeccionado: huellitas.db", ""]
    for nombre, definicion in tablas:
        lineas.append(f"TABLA {nombre} - {conteos[nombre]} registros")
        lineas.extend(f"  {parte.strip()}" for parte in definicion.replace("\n", " ").split(","))
        lineas.append("")
    for nombre, tabla in indices:
        lineas.append(f"ÍNDICE {nombre} sobre {tabla}")
    for clave in foraneas:
        lineas.append(f"CLAVE FORÁNEA cuidados.{clave[3]} -> {clave[2]}.{clave[4]} | ON DELETE {clave[6]}")
    crear_imagen("Inspección real de la base de datos SQLite", lineas,
                 EVIDENCIAS / "06_base_datos_tablas.png")


if __name__ == "__main__":
    EVIDENCIAS.mkdir(exist_ok=True)
    evidencia_pruebas()
    evidencia_base_datos()
    print("Evidencias de pruebas y base de datos generadas correctamente.")
