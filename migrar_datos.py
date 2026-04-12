"""
SCRIPT DE MIGRACIÓN: SQLite local → PostgreSQL Railway
=======================================================
Este script lee los datos de tu base de datos local (montebello.db)
y los inserta en la base de datos PostgreSQL de Railway.

CÓMO USARLO:
1. Asegúrate de tener el archivo .env con la variable DATABASE_URL
   apuntando a tu PostgreSQL de Railway. Puedes copiarla desde:
   Railway → tu proyecto → Postgres → Variables → DATABASE_URL
   
   Ejemplo de .env:
   DATABASE_URL=postgresql://postgres:xxxx@roundhouse.proxy.rlwy.net:PORT/railway

2. Instala dependencias si no las tienes:
   pip install psycopg2-binary python-dotenv

3. Ejecuta el script:
   python migrar_datos.py
"""

import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# ── Conexión a SQLite local ────────────────────────────────────────────────────
SQLITE_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'montebello.db')

# ── Conexión a PostgreSQL Railway ─────────────────────────────────────────────
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: No se encontró la variable DATABASE_URL en el archivo .env")
    exit(1)

# Railway puede devolver "postgres://" pero psycopg2 necesita "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ── Funciones de ayuda ────────────────────────────────────────────────────────

def conectar_sqlite():
    if not os.path.exists(SQLITE_PATH):
        print(f"ERROR: No se encontró el archivo SQLite en: {SQLITE_PATH}")
        exit(1)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
    print(f"✔ Conectado a SQLite: {SQLITE_PATH}")
    return conn

def conectar_postgres():
    conn = psycopg2.connect(DATABASE_URL)
    print("✔ Conectado a PostgreSQL Railway")
    return conn

def migrar_proveedores(sqlite_cur, pg_cur):
    print("\n── Migrando Proveedores ──")
    sqlite_cur.execute("SELECT * FROM proveedores")
    filas = sqlite_cur.fetchall()
    
    if not filas:
        print("   No hay proveedores para migrar.")
        return

    for fila in filas:
        pg_cur.execute("""
            INSERT INTO proveedores ("Id_Prov", "Nom_Prov", "Num_Ced", "Num_Anden", "Num_Puesto")
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT ("Id_Prov") DO NOTHING
        """, (fila['Id_Prov'], fila['Nom_Prov'], fila['Num_Ced'], fila['Num_Anden'], fila['Num_Puesto']))
    
    print(f"   ✔ {len(filas)} proveedor(es) migrado(s).")

def migrar_productos(sqlite_cur, pg_cur):
    print("\n── Migrando Productos ──")
    sqlite_cur.execute("SELECT * FROM productos")
    filas = sqlite_cur.fetchall()

    if not filas:
        print("   No hay productos para migrar.")
        return

    for fila in filas:
        pg_cur.execute("""
            INSERT INTO productos ("id_Prod", "Nom_Prod", "Medida", "Id_Prov")
            VALUES (%s, %s, %s, %s)
            ON CONFLICT ("id_Prod") DO NOTHING
        """, (fila['id_Prod'], fila['Nom_Prod'], fila['Medida'], fila['Id_Prov']))

    print(f"   ✔ {len(filas)} producto(s) migrado(s).")

def migrar_compras_dia(sqlite_cur, pg_cur):
    print("\n── Migrando Compras del Día ──")
    sqlite_cur.execute("SELECT * FROM compras_dia")
    filas = sqlite_cur.fetchall()

    if not filas:
        print("   No hay compras del día para migrar.")
        return

    for fila in filas:
        pg_cur.execute("""
            INSERT INTO compras_dia ("Id_Lin_Comp", "Id_Comp", "Fec_Comp", "Id_Prod", "Cant_Ped", "Cant_Bod", "Cant_Comp", "Val_Pag", "Id_Prov")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT ("Id_Lin_Comp") DO NOTHING
        """, (fila['Id_Lin_Comp'], fila['Id_Comp'], fila['Fec_Comp'], fila['Id_Prod'],
              fila['Cant_Ped'], fila['Cant_Bod'], fila['Cant_Comp'], fila['Val_Pag'], fila['Id_Prov']))

    print(f"   ✔ {len(filas)} compra(s) del día migrada(s).")

def migrar_historico(sqlite_cur, pg_cur):
    print("\n── Migrando Histórico de Compras ──")
    sqlite_cur.execute("SELECT * FROM historico_compras")
    filas = sqlite_cur.fetchall()

    if not filas:
        print("   No hay histórico para migrar.")
        return

    for fila in filas:
        pg_cur.execute("""
            INSERT INTO historico_compras ("Id_Lin_Comp", "Id_Comp", "Fec_Comp", "Id_Prod", "Cant_Ped", "Cant_Comp", "Cant_Bod", "Val_Pag", "Id_Prov")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT ("Id_Lin_Comp") DO NOTHING
        """, (fila['Id_Lin_Comp'], fila['Id_Comp'], fila['Fec_Comp'], fila['Id_Prod'],
              fila['Cant_Ped'], fila['Cant_Comp'], fila['Cant_Bod'], fila['Val_Pag'], fila['Id_Prov']))

    print(f"   ✔ {len(filas)} registro(s) histórico(s) migrado(s).")

def migrar_pedidos(sqlite_cur, pg_cur):
    print("\n── Migrando Pedidos de Compra ──")
    sqlite_cur.execute("SELECT * FROM pedidos_compra")
    filas = sqlite_cur.fetchall()

    if not filas:
        print("   No hay pedidos para migrar.")
        return

    for fila in filas:
        pg_cur.execute("""
            INSERT INTO pedidos_compra ("Id_Lin_Ped", "Id_Lista", "Id_Prod", "Cant_Ped", "Cant_Bod", "Fec_Ped")
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT ("Id_Lin_Ped") DO NOTHING
        """, (fila['Id_Lin_Ped'], fila['Id_Lista'], fila['Id_Prod'],
              fila['Cant_Ped'], fila['Cant_Bod'], fila['Fec_Ped']))

    print(f"   ✔ {len(filas)} pedido(s) migrado(s).")

# ── Ejecución principal ───────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 55)
    print("   MIGRACIÓN SQLite → PostgreSQL Railway")
    print("=" * 55)

    sqlite_conn = conectar_sqlite()
    pg_conn = conectar_postgres()

    sqlite_cur = sqlite_conn.cursor()
    pg_cur = pg_conn.cursor()

    try:
        # El orden importa: primero tablas sin dependencias (proveedores),
        # luego las que dependen de ellas (productos), y así sucesivamente.
        migrar_proveedores(sqlite_cur, pg_cur)
        migrar_productos(sqlite_cur, pg_cur)
        migrar_compras_dia(sqlite_cur, pg_cur)
        migrar_historico(sqlite_cur, pg_cur)
        migrar_pedidos(sqlite_cur, pg_cur)

        pg_conn.commit()  # Confirmar todos los cambios en PostgreSQL
        print("\n✅ Migración completada exitosamente.")

    except Exception as e:
        pg_conn.rollback()  # Si algo falla, deshacer TODO para no dejar datos a medias
        print(f"\n❌ Error durante la migración: {e}")
        print("   Se deshicieron todos los cambios (rollback).")

    finally:
        sqlite_cur.close()
        pg_cur.close()
        sqlite_conn.close()
        pg_conn.close()
        print("   Conexiones cerradas.")
