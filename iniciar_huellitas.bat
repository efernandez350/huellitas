@echo off
set "PYTHON_HUELLITAS=%LocalAppData%\Programs\Python\Python313\python.exe"

if not exist "%PYTHON_HUELLITAS%" (
    echo No se encontro Python en la ruta esperada.
    echo Instale Python 3 desde https://www.python.org/downloads/
    pause
    exit /b 1
)

cd /d "%~dp0"
"%PYTHON_HUELLITAS%" main.py

if errorlevel 1 (
    echo.
    echo Huellitas termino con un error.
    pause
)
