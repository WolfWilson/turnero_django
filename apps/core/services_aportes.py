# apps/core/services_aportes.py
"""
Servicios para consultar la base de datos Aportes (SQL Server sql01)
Utiliza Trusted Connection por ahora, en el futuro usará credenciales del .env
"""
from django.db import connections
from typing import Optional, Dict, Any


def buscar_persona_por_dni(dni: str) -> Optional[Dict[str, Any]]:
    """
    Busca una persona en la base de datos Aportes por DNI.
    Llama al SP: Will_Busca_Persona_Turnero
    
    Args:
        dni: DNI de la persona (8 dígitos)
    
    Returns:
        Dict con: {
            'apeynom': str,
            'fecha_nac': date,
            'sexo': str
        } o None si no encuentra
    """
    # Normalizar DNI (8 dígitos sin puntos)
    dni_limpio = dni.strip().replace('.', '').replace(',', '').zfill(8)
    
    if len(dni_limpio) > 8:
        dni_limpio = dni_limpio[:8]
    
    with connections['aportes'].cursor() as cursor:
        # Ejecutar SP
        cursor.execute(
            "EXEC Will_Busca_Persona_Turnero @dni = %s",
            [dni_limpio]
        )
        
        row = cursor.fetchone()
        
        if row:
            return {
                'apeynom': row[0],
                'fecha_nac': row[1],
                'sexo': row[2],
            }
        
        return None


def verificar_conexion_aportes() -> bool:
    """
    Verifica si la conexión a la base de datos Aportes está disponible.
    
    Returns:
        True si la conexión es exitosa, False en caso contrario
    """
    try:
        with connections['aportes'].cursor() as cursor:
            cursor.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"Error conectando a Aportes: {e}")
        return False
