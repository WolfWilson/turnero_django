import pyodbc
import os
from pathlib import Path

# Cargar variables de entorno
import environ
BASE_DIR = Path(__file__).resolve().parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

print("=" * 60)
print("TEST DE CONEXIÓN A SQL SERVER")
print("=" * 60)

# Configuración
DB_HOST = env('DB_HOST')
DB_NAME = env('DB_NAME')
DB_USER = env('SQL_USER')
DB_PASS = env('SQL_PASS')
DB_DRIVER = env('DB_DRIVER')

print(f"\nParámetros de conexión:")
print(f"  Host: {DB_HOST}")
print(f"  Database: {DB_NAME}")
print(f"  User: {DB_USER}")
print(f"  Driver: {DB_DRIVER}")

# String de conexión
conn_str = (
    f"DRIVER={{{DB_DRIVER}}};"
    f"SERVER={DB_HOST};"
    f"DATABASE={DB_NAME};"
    f"UID={DB_USER};"
    f"PWD={DB_PASS};"
    f"TrustServerCertificate=yes;"
)

print(f"\nIntentando conectar...")

try:
    # Intentar conexión
    conn = pyodbc.connect(conn_str, timeout=5)
    cursor = conn.cursor()
    
    # Ejecutar query de prueba
    cursor.execute("SELECT @@VERSION")
    row = cursor.fetchone()
    version = row[0] if row else "Desconocida"
    
    print("\n✅ CONEXIÓN EXITOSA")
    print(f"\nVersión del servidor:")
    print(f"  {version.split('\\n')[0]}")
    
    # Listar tablas existentes
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)
    
    tablas = cursor.fetchall()
    if tablas:
        print(f"\nTablas encontradas ({len(tablas)}):")
        for tabla in tablas:
            print(f"  - {tabla[0]}")
    else:
        print("\n⚠️  No hay tablas en la base de datos (esto es normal antes de migrate)")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("Puedes proceder con: python manage.py migrate")
    print("=" * 60)

except pyodbc.Error as e:
    print("\n❌ ERROR DE CONEXIÓN")
    print(f"\nDetalles del error:")
    print(f"  {e}")
    print("\n💡 Verifica:")
    print("  1. El servidor web03 está accesible")
    print("  2. SQL Server está ejecutándose")
    print("  3. La base de datos 'Turnero' existe")
    print("  4. Las credenciales son correctas")
    print("  5. El driver ODBC está instalado")
    
except Exception as e:
    print(f"\n❌ ERROR INESPERADO: {e}")
