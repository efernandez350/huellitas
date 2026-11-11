# Huellitas

Huellitas es una aplicación de escritorio sencilla para registrar perros y gatos y organizar sus vacunas, baños, desparasitaciones y citas veterinarias. Fue desarrollada como proyecto del curso Paradigmas de Programación de la Universidad Fidélitas.

## Tecnologías

- Python 3.13
- Tkinter para la interfaz gráfica
- SQLite para la persistencia local
- `unittest` para las pruebas automatizadas

Todas forman parte de la biblioteca estándar de Python; la aplicación no necesita paquetes externos.

## Cómo ejecutar la aplicación

1. Abra esta carpeta en Visual Studio Code.
2. Abra una terminal integrada desde **Terminal > Nueva terminal**.
3. Ejecute:

```powershell
python main.py
```

Si Windows todavía no reconoce `python`, use la ruta instalada:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" main.py
```

También puede hacer doble clic en `iniciar_huellitas.bat`. Este iniciador utiliza directamente la instalación de Python y no depende de la configuración de `PATH` de la terminal.

La primera ejecución crea automáticamente `huellitas.db` en la carpeta del proyecto.

## Funciones principales

- Agregar, consultar, editar y eliminar mascotas.
- Validar nombre, especie y edad.
- Agregar, consultar, editar y eliminar cuidados.
- Marcar cuidados como realizados.
- Validar fechas en formato DD/MM/AAAA y guardarlas como AAAA-MM-DD.
- Eliminar en cascada los cuidados cuando se elimina una mascota, después de pedir confirmación.
- Mantener la información entre ejecuciones mediante SQLite.

## Cómo ejecutar las pruebas

```powershell
python -m unittest discover -s pruebas -v
```

Las pruebas usan bases de datos temporales; no modifican `huellitas.db`.

## Organización

- `main.py`: inicia la base de datos y la ventana principal.
- `modelos.py`: define las clases `Mascota` y `Cuidado`, sus validaciones y las fechas.
- `base_datos.py`: crea las tablas y contiene las operaciones CRUD parametrizadas.
- `interfaz.py`: contiene la interfaz Tkinter y los formularios.
- `pruebas/test_huellitas.py`: contiene las pruebas automatizadas.
- `evidencias/`: contiene capturas reales del funcionamiento y las pruebas.
- `documentacion/`: contiene el informe académico del segundo avance.

## Base de datos

La tabla `mascotas` almacena el identificador, nombre, especie, edad y observaciones. La tabla `cuidados` almacena el identificador, la mascota relacionada, tipo, fecha, estado y observaciones. `cuidados.mascota_id` es una clave foránea hacia `mascotas.id` con eliminación en cascada. Las claves foráneas se activan en cada conexión y se usan índices para consultar con eficiencia por mascota, fecha y estado.

## Subir a GitHub

Después de crear un repositorio vacío en GitHub, ejecute desde esta carpeta:

```powershell
git init
git add .
git commit -m "Segundo avance de Huellitas"
git branch -M main
git remote add origin URL_DEL_REPOSITORIO
git push -u origin main
```

Sustituya `URL_DEL_REPOSITORIO` por la dirección de su repositorio. Compruebe antes de subir que `huellitas.db` no aparece entre los archivos preparados; está excluido por `.gitignore`.
