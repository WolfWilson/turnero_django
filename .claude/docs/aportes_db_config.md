# Configuración de Acceso a Base de Datos Aportes

## Estado Actual
- **Servidor**: sql01
- **Base de Datos**: Aportes
- **Autenticación**: Trusted Connection (Windows Authentication)
- **Stored Procedure**: `Will_Busca_Persona_Turnero`

## TODO: Crear Usuario Específico

### Script SQL para crear usuario (ejecutar en sql01)

```sql
USE [master]
GO

-- 1. Crear login SQL Server
CREATE LOGIN [turnero_consulta] 
WITH PASSWORD = 'GenerarPasswordSeguro_Aqui!', 
CHECK_POLICY = ON,
CHECK_EXPIRATION = OFF;
GO

-- 2. Crear usuario en BD Aportes
USE [Aportes]
GO

CREATE USER [turnero_consulta] FOR LOGIN [turnero_consulta];
GO

-- 3. Otorgar SOLO permiso de EXECUTE en el SP
GRANT EXECUTE ON [dbo].[Will_Busca_Persona_Turnero] TO [turnero_consulta];
GO

-- Verificar permisos
SELECT 
    dp.name AS UserName,
    o.name AS ObjectName,
    dp.permission_name,
    dp.state_desc
FROM sys.database_permissions dp
JOIN sys.objects o ON dp.major_id = o.object_id
WHERE dp.grantee_principal_id = USER_ID('turnero_consulta');
GO
```

### Actualizar .env

Una vez creadas las credenciales, descomentar y configurar en `.env`:

```dotenv
APORTES_DB_HOST=sql01
APORTES_SQL_USER=turnero_consulta
APORTES_SQL_PASS=password_generado_arriba
```

### Actualizar settings.py

En `turnero/settings.py`, cambiar la configuración de 'aportes':

```python
'aportes': {
    'ENGINE': 'mssql',
    'NAME': 'Aportes',
    'USER': env('APORTES_SQL_USER'),  # En lugar de Trusted_Connection
    'PASSWORD': env('APORTES_SQL_PASS'),
    'HOST': env('APORTES_DB_HOST', default='sql01'),
    'PORT': '',
    'OPTIONS': {
        'driver': env('DB_DRIVER'),
        'extra_params': 'TrustServerCertificate=yes',  # Sin Trusted_Connection
    },
}
```

## Archivos Relacionados

- **Servicio de búsqueda**: `apps/core/services_aportes.py`
- **Integración en emisión de turnos**: `apps/core/services.py` (función `buscar_persona_por_dni`)
- **API REST**: `api/views.py` (endpoint `/api/personas/buscar/`)
- **Test de conexión**: `test_aportes_connection.py`

## Uso desde código

```python
from apps.core.services_aportes import buscar_persona_por_dni

# Buscar por DNI
resultado = buscar_persona_por_dni('12345678')

if resultado:
    print(resultado['apeynom'])      # "APELLIDO, NOMBRE"
    print(resultado['fecha_nac'])    # datetime.date
    print(resultado['sexo'])         # 'M' o 'F'
```

## Uso desde API REST

```bash
POST /api/personas/buscar/
Content-Type: application/json

{
  "dni": 12345678
}
```

Respuesta exitosa:
```json
{
  "nombre": "JUAN",
  "apellido": "PÉREZ",
  "fecha_nacimiento": "1980-05-15",
  "sexo": "M"
}
```
