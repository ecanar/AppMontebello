# App Montebello - Guía de Instalación

## Método 1: Instalación Automática (Recomendado)

### Pasos:
1. **Descarga los archivos** de la App Montebello en una carpeta
2. **Doble clic** en el archivo `instalar.bat`
3. **Espera** a que termine la instalación
4. **Listo** - La aplicación se abrirá automáticamente en tu navegador

### Si falla la instalación automática:
- Sigue los pasos del Método 2 manualmente

---

## Método 2: Instalación Manual

### Requisitos:
- Windows 10 o superior
- Python 3.8 o superior

### Paso 1: Instalar Python
1. Ve a https://www.python.org/downloads/
2. Descarga la versión más reciente
3. **IMPORTANTE**: Durante la instalación, marca la casilla "Add Python to PATH"
4. Completa la instalación

### Paso 2: Verificar instalación
1. Abre la terminal (Windows + R, escribe `cmd`, presiona Enter)
2. Escribe: `python --version`
3. Deberías ver algo como: `Python 3.12.x`

### Paso 3: Descargar la aplicación
1. Copia todos los archivos de App Montebello a una carpeta
2. Asegúrate de tener estos archivos:
   - `app.py`
   - `requirements.txt`
   - `instalar.bat`
   - Carpeta `templates/`

### Paso 4: Instalar dependencias
1. Abre terminal en la carpeta de la aplicación
2. Ejecuta: `python -m pip install -r requirements.txt`

### Paso 5: Ejecutar la aplicación
1. En la misma terminal, ejecuta: `python app.py`
2. Abre tu navegador y ve a: `http://127.0.0.1:5000`

---

## Método 3: Instalación Portátil (Sin instalar Python)

### Pasos:
1. **Descarga Python Portable** desde https://www.python.org/downloads/windows/
2. **Extrae** Python Portable en una carpeta
3. **Copia** la App Montebello en la misma carpeta
4. **Ejecuta** el script `instalar.bat`

---

## Archivos Necesarios

La carpeta completa debe contener:

```
AppMontebello/
    app.py                    # Aplicación principal
    requirements.txt          # Dependencias
    instalar.bat             # Instalador automático
    INSTALACION.md           # Esta guía
    templates/               # Plantillas HTML
        base.html
        index.html
        productos.html
        proveedores.html
        pedidos.html
        compras.html
        historico.html
        edit_producto.html
        edit_proveedor.html
```

---

## Solución de Problemas

### Error: "python no se reconoce"
**Solución**: Reinstala Python asegurándote de marcar "Add Python to PATH"

### Error: "pip no se reconoce"
**Solución**: Usa `python -m pip` en lugar de `pip`

### Error: "No se puede conectar a localhost:5000"
**Solución**: Asegúrate de que `python app.py` esté corriendo

### Error: "Template not found"
**Solución**: Verifica que la carpeta `templates/` esté junto a `app.py`

---

## Uso Básico

1. **Agregar Proveedores** primero
2. **Agregar Productos** después
3. **Crear Pedidos** para planificar compras
4. **Transferir Pedidos** a Compras del Día
5. **Actualizar Compras** con cantidades reales
6. **Mover a Histórico** al finalizar el día

---

## Soporte

Si tienes problemas:
1. Revisa esta guía
2. Ejecuta `instalar.bat` para diagnóstico
3. Verifica que todos los archivos estén presentes

---

## Características

- **5 Módulos**: Productos, Proveedores, Pedidos, Compras, Histórico
- **IDs Secuenciales**: Para pedidos anuales
- **Transferencia Automática**: De pedidos a compras
- **Base de Datos Local**: SQLite (sin configuración requerida)
- **Interfaz Web**: Bootstrap 5, moderna y responsiva
