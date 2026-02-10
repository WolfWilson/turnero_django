# test_aportes_connection.py
"""
Script para probar la conexión a la BD Aportes y el SP Will_Busca_Persona_Turnero
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'turnero.settings')
django.setup()

from apps.core.services_aportes import verificar_conexion_aportes, buscar_persona_por_dni

print("=" * 60)
print("TEST: Conexión a Base de Datos Aportes (sql01)")
print("=" * 60)

# 1. Verificar conexión
print("\n1. Verificando conexión...")
if verificar_conexion_aportes():
    print("   ✓ Conexión exitosa a Aportes")
else:
    print("   ✗ Error al conectar a Aportes")
    exit(1)

# 2. Probar búsqueda por DNI
print("\n2. Probando búsqueda por DNI...")
dni_test = "32746256"  # DNI de ejemplo del comentario del SP
print(f"   Buscando DNI: {dni_test}")

resultado = buscar_persona_por_dni(dni_test)

if resultado:
    print(f"\n   ✓ Persona encontrada:")
    print(f"      Nombre completo: {resultado['apeynom']}")
    print(f"      Fecha Nac: {resultado['fecha_nac']}")
    print(f"      Sexo: {resultado['sexo']}")
else:
    print(f"   ✗ DNI {dni_test} no encontrado")

# 3. Probar con DNI que no existe
print("\n3. Probando con DNI inexistente...")
dni_fake = "00000001"
resultado_fake = buscar_persona_por_dni(dni_fake)

if resultado_fake:
    print(f"   ✗ Inesperado: encontró resultado para DNI fake")
else:
    print(f"   ✓ Correctamente retorna None para DNI inexistente")

print("\n" + "=" * 60)
print("FIN DEL TEST")
print("=" * 60)
