@echo off
echo ========================================
echo   App Montebello - Instalador Automatico
echo ========================================
echo.

echo [1/4] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado.
    echo Por favor instala Python desde https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)
echo Python encontrado: 
python --version

echo.
echo [2/4] Instalando dependencias...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias.
    pause
    exit /b 1
)
echo Dependencias instaladas correctamente.

echo.
echo [3/4] Creando base de datos...
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Base de datos creada correctamente')"
if %errorlevel% neq 0 (
    echo ERROR: No se pudo crear la base de datos.
    pause
    exit /b 1
)

echo.
echo [4/4] Iniciando aplicacion...
echo.
echo La aplicacion se iniciara en tu navegador.
echo Si no se abre automaticamente, visita: http://127.0.0.1:5000
echo.
echo Para detener la aplicacion, cierra esta ventana o presiona Ctrl+C.
echo.

start http://127.0.0.1:5000
python app.py

pause
