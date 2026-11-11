"""Genera el informe IEEE del segundo avance de Huellitas."""

from pathlib import Path
from shutil import copyfile

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


RAIZ = Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "tmp" / "plantilla_ieee_convertida.docx"
SALIDA = RAIZ / "documentacion" / "Michelle_Fernandez_Segundo_Avance_Huellitas.docx"
EVIDENCIAS = RAIZ / "evidencias"


def configurar_fuente(run, tamano=9, negrita=False, cursiva=False):
    run.font.name = "Times New Roman"
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Times New Roman")
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Times New Roman")
    run.font.size = Pt(tamano)
    run.bold = negrita
    run.italic = cursiva


def columnas(seccion, cantidad):
    sect_pr = seccion._sectPr
    cols = sect_pr.xpath("./w:cols")
    elemento = cols[0] if cols else OxmlElement("w:cols")
    if not cols:
        sect_pr.append(elemento)
    elemento.set(qn("w:num"), str(cantidad))
    elemento.set(qn("w:space"), "360")


def limpiar_documento(doc):
    cuerpo = doc._element.body
    for elemento in list(cuerpo):
        if elemento.tag != qn("w:sectPr"):
            cuerpo.remove(elemento)
    seccion = doc.sections[0]
    seccion.page_width = Inches(8.5)
    seccion.page_height = Inches(11)
    seccion.top_margin = Inches(0.75)
    seccion.bottom_margin = Inches(1.0)
    seccion.left_margin = Inches(0.62)
    seccion.right_margin = Inches(0.62)
    columnas(seccion, 1)


def parrafo(doc, texto="", alineacion=WD_ALIGN_PARAGRAPH.JUSTIFY, espacio=3, tamano=9,
            negrita=False, cursiva=False):
    p = doc.add_paragraph()
    p.alignment = alineacion
    p.paragraph_format.space_after = Pt(espacio)
    p.paragraph_format.line_spacing = 1.0
    configurar_fuente(p.add_run(texto), tamano, negrita, cursiva)
    return p


def encabezado(doc, numero, titulo):
    p = parrafo(doc, f"{numero}.  {titulo.upper()}", WD_ALIGN_PARAGRAPH.CENTER, 4, 10)
    p.paragraph_format.keep_with_next = True


def subtitulo(doc, letra, titulo):
    p = parrafo(doc, f"{letra}. {titulo}", WD_ALIGN_PARAGRAPH.LEFT, 2, 10, cursiva=True)
    p.paragraph_format.keep_with_next = True


def vineta(doc, texto):
    p = parrafo(doc, espacio=1)
    p.paragraph_format.left_indent = Inches(0.18)
    p.paragraph_format.first_line_indent = Inches(-0.12)
    configurar_fuente(p.add_run("• "), 9)
    configurar_fuente(p.add_run(texto), 9)


def seccion_columnas(doc, cantidad):
    seccion = doc.add_section(WD_SECTION.CONTINUOUS)
    seccion.page_width = Inches(8.5)
    seccion.page_height = Inches(11)
    seccion.top_margin = Inches(0.75)
    seccion.bottom_margin = Inches(1.0)
    seccion.left_margin = Inches(0.62)
    seccion.right_margin = Inches(0.62)
    columnas(seccion, cantidad)
    return seccion


def bordes_tabla(tabla):
    tbl_pr = tabla._tbl.tblPr
    bordes = tbl_pr.first_child_found_in("w:tblBorders")
    if bordes is None:
        bordes = OxmlElement("w:tblBorders")
        tbl_pr.append(bordes)
    for nombre in ("top", "left", "bottom", "right", "insideH", "insideV"):
        borde = OxmlElement(f"w:{nombre}")
        borde.set(qn("w:val"), "single")
        borde.set(qn("w:sz"), "4")
        borde.set(qn("w:color"), "808080")
        bordes.append(borde)


def tabla(doc, titulo, encabezados, filas, anchos=None):
    parrafo(doc, titulo, WD_ALIGN_PARAGRAPH.CENTER, 2, 8, negrita=True)
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    bordes_tabla(t)
    for i, texto in enumerate(encabezados):
        celda = t.rows[0].cells[i]
        celda.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        if anchos: celda.width = Inches(anchos[i])
        p = celda.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        configurar_fuente(p.add_run(texto), 7.5, negrita=True)
        sombreado = OxmlElement("w:shd"); sombreado.set(qn("w:fill"), "D9E8DF")
        celda._tc.get_or_add_tcPr().append(sombreado)
    for fila in filas:
        celdas = t.add_row().cells
        for i, texto in enumerate(fila):
            celdas[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if anchos: celdas[i].width = Inches(anchos[i])
            p = celdas[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i in (0, len(fila)-1) else WD_ALIGN_PARAGRAPH.LEFT
            configurar_fuente(p.add_run(str(texto)), 7.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def figura(doc, archivo, numero, pie, ancho=6.6):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(EVIDENCIAS / archivo), width=Inches(ancho))
    cap = parrafo(doc, f"Fig. {numero}. {pie}", WD_ALIGN_PARAGRAPH.CENTER, 5, 8)
    cap.paragraph_format.keep_together = True


def construir():
    SALIDA.parent.mkdir(exist_ok=True)
    copyfile(PLANTILLA, SALIDA)
    doc = Document(SALIDA)
    limpiar_documento(doc)

    p = parrafo(doc, "Huellitas: aplicación para organizar el cuidado de las mascotas",
                WD_ALIGN_PARAGRAPH.CENTER, 8, 24)
    p.paragraph_format.keep_with_next = True
    parrafo(doc, "Michelle Fernández", WD_ALIGN_PARAGRAPH.CENTER, 0, 11)
    parrafo(doc, "Universidad Fidélitas", WD_ALIGN_PARAGRAPH.CENTER, 0, 10)
    parrafo(doc, "Paradigmas de Programación", WD_ALIGN_PARAGRAPH.CENTER, 0, 10)
    parrafo(doc, "Costa Rica", WD_ALIGN_PARAGRAPH.CENTER, 10, 10)

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    configurar_fuente(p.add_run("Resumen—"), 9, negrita=True)
    configurar_fuente(p.add_run(
        "Este segundo avance presenta la implementación funcional de Huellitas, una aplicación de escritorio "
        "para registrar perros y gatos y organizar vacunas, baños, desparasitaciones y citas veterinarias. "
        "La solución utiliza Python, Tkinter y SQLite, conserva los objetivos aprobados en el primer avance "
        "y separa los modelos, la persistencia y la interfaz. Se incorporan validaciones, operaciones de "
        "registro, consulta, modificación y eliminación, claves foráneas e índices. Doce pruebas automatizadas "
        "verificaron las operaciones principales, la relación entre tablas, la eliminación en cascada y la persistencia."), 9)
    p.paragraph_format.space_after = Pt(3)
    p = doc.add_paragraph()
    configurar_fuente(p.add_run("Palabras clave—"), 9, negrita=True)
    configurar_fuente(p.add_run("mascotas, aplicación, registro, estructuras de datos, Python, SQLite."), 9)

    seccion_columnas(doc, 2)
    encabezado(doc, "I", "Introducción")
    parrafo(doc, "Actualmente, muchas familias tienen mascotas que necesitan cuidados constantes, como vacunas, desparasitación, baños y visitas al veterinario. Cuando estas fechas se anotan en distintos lugares o solo se intentan recordar, puede ser difícil mantener toda la información organizada.")
    parrafo(doc, "Por esta razón se desarrolló Huellitas, una aplicación sencilla para registrar perros y gatos y consultar sus cuidados. El proyecto es una utilidad de uso personal para reunir los datos básicos y las fechas de atención en un solo lugar.")
    subtitulo(doc, "A", "Problema de investigación")
    parrafo(doc, "El Instituto Nacional de Estadística y Censos (INEC) informó que, en 2024, el 62,2 % de los hogares de Costa Rica tenía al menos un perro o gato como mascota [1]. Cuando una persona cuida más de un animal, puede necesitar recordar fechas diferentes para cada uno. La pregunta conservada del primer avance es: ¿cómo ayudar a organizar, mediante una aplicación sencilla, los datos y las fechas de cuidado de las mascotas?")
    subtitulo(doc, "B", "Justificación")
    parrafo(doc, "La Encuesta Nacional de Hogares 2024 estimó 1 133 257 hogares con al menos un perro o gato [1]. Además, el INEC reportó que el 76,5 % de los perros de los hogares estaba vacunado [2]. Huellitas reúne la información para facilitar su consulta; no sustituye la atención ni las recomendaciones de un profesional veterinario.")
    subtitulo(doc, "C", "Objetivo general")
    parrafo(doc, "Diseñar una aplicación sencilla que permita registrar mascotas y organizar sus fechas de cuidado mediante el uso de estructuras de datos dinámicas.")
    subtitulo(doc, "D", "Objetivos específicos")
    vineta(doc, "Identificar la información básica que se necesita guardar de cada mascota, como nombre, especie y cuidados.")
    vineta(doc, "Proponer una interfaz clara para agregar, consultar, modificar y eliminar los registros de las mascotas.")
    vineta(doc, "Organizar una lista dinámica de mascotas y sus próximas actividades para facilitar la consulta de fechas.")

    encabezado(doc, "II", "Marco teórico")
    subtitulo(doc, "A", "Aplicación informática")
    parrafo(doc, "Una aplicación es un programa que permite realizar una tarea específica. En Huellitas, esa tarea consiste en guardar información de mascotas y mostrar las fechas de sus cuidados. La utilidad se mantuvo pequeña para que sus funciones fueran fáciles de comprender y desarrollar.")
    subtitulo(doc, "B", "Lenguajes y paradigmas de programación")
    parrafo(doc, "Un lenguaje de programación utiliza instrucciones, reglas y símbolos para indicarle a una computadora qué debe hacer [3]. Un paradigma es una manera de organizar el código y resolver problemas [4]. Huellitas combina programación imperativa, orientación a objetos y un ejemplo funcional sencillo, sin forzar paradigmas que no aportan a la solución.")
    subtitulo(doc, "C", "Conceptos aplicados")
    vineta(doc, "Variables y tipos: cadenas para nombres, números enteros para edades y condiciones booleanas en las decisiones del programa.")
    vineta(doc, "Condicionales y lógica: validación de campos, especies, edades, fechas, estados y selección de registros.")
    vineta(doc, "Funciones: operaciones pequeñas para convertir fechas, actualizar listas y ejecutar cada acción CRUD.")
    vineta(doc, "Listas dinámicas: los resultados de SQLite se convierten en listas de diccionarios que crecen o disminuyen según los registros.")
    vineta(doc, "Orientación a objetos: las clases Mascota, Cuidado, BaseDatos y AplicacionHuellitas encapsulan datos y responsabilidades.")
    vineta(doc, "Programación funcional: obtener_pendientes crea una nueva lista filtrada y ordenada sin modificar la lista recibida.")

    encabezado(doc, "III", "Desarrollo técnico")
    subtitulo(doc, "A", "Organización modular")
    parrafo(doc, "main.py inicia la aplicación; modelos.py define los datos y validaciones; base_datos.py concentra las consultas parametrizadas; interfaz.py contiene las ventanas y controles; y pruebas/test_huellitas.py verifica el comportamiento. Esta separación permite explicar y modificar cada parte sin mezclar la interfaz con SQL.")
    subtitulo(doc, "B", "Interfaz y operaciones")
    parrafo(doc, "La ventana principal tiene las secciones Mis mascotas y Próximos cuidados. Los formularios permiten agregar y editar. Las tablas permiten consultar, seleccionar y eliminar, y en cuidados también se puede marcar un registro como realizado. Antes de eliminar una mascota se solicita confirmación y se advierte que sus cuidados asociados también se eliminarán.")
    subtitulo(doc, "C", "Diseño y justificación de la base de datos")
    parrafo(doc, "SQLite se eligió porque guarda datos localmente, no requiere servidor y está incluido con Python. La normalización en dos tablas evita repetir los datos de la mascota en cada cuidado. La clave foránea asegura que todo cuidado pertenezca a una mascota existente. ON DELETE CASCADE mantiene la integridad cuando se confirma la eliminación. Las restricciones CHECK protegen especie, edad, tipo y estado, y los índices agilizan las consultas por mascota, fecha y estado.")

    seccion_columnas(doc, 1)
    tabla(doc, "TABLA I. DISEÑO DE LA BASE DE DATOS",
          ["Tabla", "Campo", "Tipo y restricción", "Justificación"], [
        ("mascotas", "id", "INTEGER, PK, AUTOINCREMENT", "Identificador único"),
        ("mascotas", "nombre", "TEXT, NOT NULL, CHECK", "Nombre obligatorio"),
        ("mascotas", "especie", "TEXT, CHECK Perro/Gato", "Valores controlados"),
        ("mascotas", "edad", "INTEGER, CHECK >= 0", "Edad válida"),
        ("mascotas", "observaciones", "TEXT, DEFAULT ''", "Dato opcional"),
        ("cuidados", "id", "INTEGER, PK, AUTOINCREMENT", "Identificador único"),
        ("cuidados", "mascota_id", "INTEGER, FK, NOT NULL", "Relación con mascotas"),
        ("cuidados", "tipo", "TEXT, CHECK", "Tipo permitido"),
        ("cuidados", "fecha", "TEXT AAAA-MM-DD, CHECK", "Orden y formato estable"),
        ("cuidados", "estado", "TEXT, CHECK", "Pendiente o Realizado"),
        ("cuidados", "observaciones", "TEXT, DEFAULT ''", "Dato opcional"),
    ], [0.75, 1.05, 2.25, 2.85])

    seccion_columnas(doc, 2)
    subtitulo(doc, "D", "Validación y seguridad de datos")
    parrafo(doc, "Todas las instrucciones SQL reciben parámetros mediante signos de interrogación. Esto evita formar consultas con texto del usuario. Las claves foráneas se activan en cada conexión y cada conexión se confirma, revierte ante un error y se cierra. Las fechas se validan con datetime y se almacenan como AAAA-MM-DD, aunque la interfaz las muestra como DD/MM/AAAA.")
    subtitulo(doc, "E", "Pruebas automatizadas")
    parrafo(doc, "Se ejecutó unittest con bases temporales independientes. La ejecución real del 9 de noviembre de 2026 completó 12 pruebas en menos de un segundo con resultado OK. Se verificaron registro, validaciones, consulta, actualización, eliminación, cuidados, relación entre tablas, cambio de estado, cascada, fechas, transformación funcional y persistencia al reabrir la base.")

    encabezado(doc, "IV", "Evidencia y cumplimiento")
    seccion_columnas(doc, 1)
    figura(doc, "01_pantalla_principal_mascotas.png", 1, "Pantalla principal con mascotas recuperadas de SQLite.")
    figura(doc, "03_formulario_mascota.png", 2, "Formulario real para agregar una mascota.", 4.6)
    figura(doc, "02_proximos_cuidados.png", 3, "Consulta de próximos cuidados con fechas presentadas en DD/MM/AAAA.")
    figura(doc, "04_formulario_cuidado.png", 4, "Formulario real para registrar un cuidado asociado a una mascota.", 4.8)
    figura(doc, "05_resultado_pruebas.png", 5, "Resultado real de las doce pruebas automatizadas.")
    figura(doc, "06_base_datos_tablas.png", 6, "Inspección real de tablas, índices y clave foránea en huellitas.db.")

    tabla(doc, "TABLA II. MATRIZ DE REQUERIMIENTOS Y CUMPLIMIENTO",
          ["ID", "Requerimiento", "Evidencia", "Estado"], [
        ("R1", "Registrar, consultar, editar y eliminar mascotas", "Fig. 1 y Fig. 2; pruebas CRUD", "Cumplido"),
        ("R2", "Validar nombre, especie y edad", "Prueba de campos obligatorios", "Cumplido"),
        ("R3", "Registrar, consultar, editar y eliminar cuidados", "Fig. 3 y Fig. 4; pruebas CRUD", "Cumplido"),
        ("R4", "Marcar un cuidado como realizado", "Prueba de cambio de estado", "Cumplido"),
        ("R5", "Validar y convertir fechas", "Prueba de fechas; DD/MM/AAAA en Fig. 3", "Cumplido"),
        ("R6", "Relacionar todo cuidado con una mascota", "FK y prueba de mascota inexistente", "Cumplido"),
        ("R7", "Eliminar cuidados al eliminar una mascota", "ON DELETE CASCADE y prueba de cascada", "Cumplido"),
        ("R8", "Persistir datos entre ejecuciones", "SQLite y prueba de reapertura", "Cumplido"),
        ("R9", "Crear tablas automáticamente", "BaseDatos.crear_tablas", "Cumplido"),
        ("R10", "Interfaz sencilla en español", "Fig. 1 a Fig. 4", "Cumplido"),
        ("R11", "Publicar enlace del repositorio", "Requiere publicación por la autora", "Pendiente"),
    ], [0.42, 2.55, 2.65, 0.9])

    seccion_columnas(doc, 2)
    encabezado(doc, "V", "Conclusiones")
    parrafo(doc, "Huellitas alcanzó un avance funcional coherente con el objetivo y los requerimientos aprobados. La aplicación permite administrar mascotas y cuidados con una interfaz sencilla, datos persistentes y validaciones claras. La estructura modular y las clases utilizadas permiten explicar los conceptos del curso con ejemplos concretos.", tamano=8.5)
    parrafo(doc, "Las pruebas automatizadas y las capturas demuestran el comportamiento implementado. La base de datos aplica claves primarias, clave foránea, restricciones, consultas parametrizadas, índices y eliminación en cascada. El único elemento pendiente es publicar el repositorio y sustituir en la entrega final la indicación correspondiente por el enlace real, acción que requiere la cuenta de GitHub de la autora.", tamano=8.5)

    p = parrafo(doc, "REFERENCIAS", WD_ALIGN_PARAGRAPH.CENTER, 4, 10)
    p.paragraph_format.keep_with_next = True
    referencias = [
        "[1] Instituto Nacional de Estadística y Censos (INEC), “El 62,2 % de los hogares de Costa Rica tienen al menos un perro o un gato como mascota,” 24 oct. 2024. [En línea]. Disponible: https://new.sen.inec.cr/noticias/el-622-los-hogares-costa-rica-tienen-al-menos-un-perro-o-un-gato-como-mascota",
        "[2] Instituto Nacional de Estadística y Censos (INEC), “Infografía Día del Perro 2025,” datos de la Encuesta Nacional de Hogares 2024. [En línea]. Disponible: https://admin.inec.cr/sites/default/files/2025-07/INFOGRAFIA_DIA_DEL_PERRO_2025.pdf",
        "[3] Universidad Fidélitas, “Elementos fundamentales de un lenguaje de programación,” Paradigmas de Programación, semana 2, material del curso, 2026.",
        "[4] Universidad Fidélitas, “Introducción a los paradigmas de programación,” Paradigmas de Programación, semana 1, material del curso, 2026.",
        "[5] Universidad Fidélitas, “Criterios de diseño y eficiencia de un lenguaje de programación,” Paradigmas de Programación, semana 2, material del curso, 2026.",
    ]
    for referencia in referencias:
        p = parrafo(doc, referencia, WD_ALIGN_PARAGRAPH.LEFT, 1, 7)
        p.paragraph_format.left_indent = Inches(0.18)
        p.paragraph_format.first_line_indent = Inches(-0.18)
        p.paragraph_format.keep_together = True

    doc.core_properties.title = "Huellitas Segundo avance"
    doc.core_properties.author = "Michelle Fernández"
    doc.core_properties.subject = "Paradigmas de Programación"
    doc.save(SALIDA)
    print(SALIDA)


if __name__ == "__main__":
    construir()
