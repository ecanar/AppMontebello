@echo off
echo ==========================================
echo Iniciando AppMontebello...
echo ==========================================

:: Verificar si el entorno virtual existe, si no, crearlo
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)

:: Activar el entorno virtual
call venv\Scripts\activate

:: Instalar o actualizar dependencias
echo Verificando dependencias...
pip install -r requirements.txt

:: Ejecutar la aplicación
echo Lanzando servidor de Flask...
python app.py

pause
