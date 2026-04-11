# App Montebello - Sistema de Gestión de Compras de Mercado

Aplicación web para gestionar compras de mercado con control de productos, proveedores e histórico de compras.

## Características

- **Gestión de Productos**: CRUD completo para productos con diferentes medidas (saco, libras, atado, racimo, cartón, unidad, cubeta)
- **Gestión de Proveedores**: CRUD para proveedores con información de cédula, andén y puesto
- **Compras del Día**: Registro diario de compras con cantidades pedidas, en bodega y compradas
- **Histórico de Compras**: Almacenamiento permanente de todas las transacciones

## Estructura de la Base de Datos

### Tabla de Productos
- `id_Prod`: Código del Producto (Primary Key)
- `Nom_Prod`: Nombre Producto
- `Medida`: (sac, lbs, ata, rac, cart, uni, cub)
- `Id_Prov`: Código del Proveedor (Foreign Key)

### Tabla de Proveedores
- `Id_Prov`: Código del Proveedor (Primary Key)
- `Nom_Prov`: Nombre del Proveedor
- `Num_Ced`: Número Cédula
- `Num_Anden`: Número Andén
- `Num_Puesto`: Número Puesto

### Tabla Compras del Día
- `Id_Lin_Comp`: Id Linea Compra (Primary Key)
- `Id_Comp`: Id de la Lista de Compra
- `Fec_Comp`: Fecha en que se realizó la Compra
- `Id_Prod`: Código del Producto (Foreign Key)
- `Cant_Ped`: Cantidad Pedida de Producto
- `Cant_Bod`: Cantidad en Bodega
- `Cant_Comp`: Cantidad Comprada Producto
- `Val_Pag`: Valor Pagado por el Producto
- `Id_Prov`: Código del Proveedor (Foreign Key)

### Tabla Histórico Compras
- `Id_Lin_Comp`: Id Linea Compra (Primary Key)
- `Id_Comp`: Id de la Lista de Compra
- `Fec_Comp`: Fecha en que se realizó la Compra
- `Id_Prod`: Código del Producto (Foreign Key)
- `Cant_Ped`: Cantidad Pedida de Producto
- `Cant_Comp`: Cantidad Comprada Producto
- `Cant_Bod`: Cantidad en Bodega
- `Val_Pag`: Valor Pagado por el Producto
- `Id_Prov`: Código del Proveedor (Foreign Key)

## Instalación

1. Clonar o descargar el proyecto
2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # En Windows
   ```
3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecutar la aplicación:
   ```bash
   python app.py
   ```

## Uso

1. Abre tu navegador y ve a `http://127.0.0.1:5000`
2. Comienza agregando proveedores en la sección "Proveedores"
3. Luego agrega productos en la sección "Productos"
4. Registra tus compras diarias en "Compras del Día"
5. Cuando termines el día, mueve las compras al histórico para mantener limpio el registro diario

## Tecnologías

- **Backend**: Flask con SQLAlchemy
- **Frontend**: Bootstrap 5
- **Base de Datos**: SQLite (para desarrollo, fácil de migrar a PostgreSQL/MySQL)
