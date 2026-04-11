import sqlite3
import os

db_path = 'instance/montebello.db'
if not os.path.exists(db_path):
    db_path = 'montebello.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("\nTABLA: compras_dia")
    cursor.execute("SELECT Id_Lin_Comp, Id_Comp, Id_Prod, Cant_Ped, Cant_Bod, Cant_Comp, Val_Pag FROM compras_dia")
    rows = cursor.fetchall()
    
    print(f"{'Id_Lin_Comp':<12} | {'Id_Comp':<8} | {'Id_Prod':<8} | {'Cant_Ped':<10} | {'Cant_Bod':<10} | {'Cant_Comp':<10} | {'Val_Pag':<10}")
    print("-" * 85)
    for row in rows:
        print(f"{row[0]:<12} | {row[1]:<8} | {row[2]:<8} | {row[3]:<10} | {row[4]:<10} | {row[5]:<10} | {row[6]:<10}")

    print("\nTABLA: historico_compras")
    cursor.execute("SELECT Id_Lin_Comp, Id_Comp, Fec_Comp, Id_Prod, Cant_Ped, Cant_Comp, Cant_Bod, Val_Pag FROM historico_compras")
    rows = cursor.fetchall()
    
    print(f"{'Id_Lin_Comp':<12} | {'Id_Comp':<8} | {'Fec_Comp':<12} | {'Id_Prod':<8} | {'Cant_Ped':<10} | {'Cant_Comp':<10} | {'Cant_Bod':<10} | {'Val_Pag':<10}")
    print("-" * 110)
    for row in rows:
        print(f"{row[0]:<12} | {row[1]:<8} | {str(row[2]):<12} | {row[3]:<8} | {row[4]:<10} | {row[5]:<10} | {row[6]:<10} | {row[7]:<10}")
    
    conn.close()
else:
    print(f"No se encontró la base de datos en {db_path}")
