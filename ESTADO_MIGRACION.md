# ✅ Migración Completada a SQL Server

## Estado Actual

### Base de Datos
- **Servidor**: web03
- **Base de Datos**: Turnero
- **Usuario**: turnero_user
- **Engine**: SQL Server 2014 Standard Edition

### Tablas Creadas (18)

| Tabla | Descripción |
|-------|-------------|
| **SchemaVersion** | Control de versiones del esquema |
| **Usuario** | Usuarios del sistema (no usa Django Auth) |
| **Area** | Áreas/sectores de atención |
| **Persona** | Datos de personas (con DNI y fecha nacimiento) |
| **EstadoTicket** | Catálogo de estados de tickets |
| **EstadoTurno** | Catálogo de estados de turnos |
| **Mesa** | Mesas de atención por área |
| **Tramite** | Tipos de trámites por área |
| **Rol** | Roles del sistema |
| **Ticket** | Tickets de solicitud (contenedor de turnos) |
| **Turno** | Turnos individuales dentro de tickets |
| **TurnoHistorialDerivacion** | Historial de derivaciones |
| **UsuarioRol** | Relación usuarios-roles |
| **AreaAdministrador** | Administradores por área |
| **AreaUsuario** | Usuarios asignados a áreas |
| **TramiteOperador** | Trámites habilitados por operador |
| **ConfiguracionArea** | Configuraciones por área |
| **ConfiguracionAreaHistorial** | Auditoría de cambios |

### Datos Maestros Insertados

#### EstadoTicket
- 0: Pendiente
- 1: EnProceso
- 2: Completado
- 3: Cancelado

#### EstadoTurno
- 0: Pendiente
- 1: Llamando
- 2: EnAtencion
- 3: Finalizado
- 4: NoPresento
- 5: Derivado

#### Roles
- 1: Administrador
- 2: Director
- 3: Operador
- 4: Supervisor

## Próximos Pasos

### 1. Actualizar Modelos Django

Los modelos en `apps/core/models.py` necesitan actualizarse para reflejar el nuevo esquema SQL Server. El sistema actual usa `django.contrib.auth.User`, pero el nuevo esquema tiene tabla `Usuario` personalizada.

### 2. Configurar Managed=False

Para usar las tablas existentes sin que Django intente crearlas:

```python
class Meta:
    managed = False
    db_table = 'Usuario'
```

### 3. Datos Iniciales

Necesitas crear:
- Áreas de atención
- Usuarios del sistema
- Trámites por área
- Mesas por área

### 4. Migrar Lógica de Autenticación

El sistema actual usa Django Auth. Opciones:
- **A)** Mantener Django Auth y crear puente con tabla Usuario
- **B)** Implementar autenticación custom basada en tabla Usuario
- **C)** Usar LDAP (ya está configurado en .env)

## Archivos Importantes

- [crear_db_sqlserver.sql](crear_db_sqlserver.sql) - Script ejecutado
- [test_sqlserver_connection.py](test_sqlserver_connection.py) - Test de conectividad
- [.env](.env) - Credenciales de conexión

## Comandos Útiles

```bash
# Verificar conexión
python test_sqlserver_connection.py

# Ver tablas en SQL Server
sqlcmd -S web03 -E -d Turnero -Q "SELECT name FROM sys.tables ORDER BY name"

# Consultar datos maestros
sqlcmd -S web03 -E -d Turnero -Q "SELECT * FROM EstadoTurno"
```
