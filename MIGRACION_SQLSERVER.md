# Guía de Migración a SQL Server

## Pasos para Migrar de SQLite a SQL Server

### 1. Crear la Base de Datos en SQL Server

Ejecuta el script SQL en SQL Server Management Studio conectado a `web03`:

```bash
sqlcmd -S web03 -U sa -P <password_admin> -i crear_db_sqlserver.sql
```

O abre `crear_db_sqlserver.sql` en SSMS y ejecuta.

### 2. Verificar Conectividad

Prueba la conexión desde Python:

```bash
python test_sqlserver_connection.py
```

### 3. Aplicar Migraciones en SQL Server

```bash
python manage.py migrate
```

Esto creará todas las tablas en SQL Server.

### 4. Migrar los Datos

```bash
python migrar_datos.py
```

Esto creará:
- Grupos (Director, Operador)
- Usuarios (wbenitez, abouvier, wil_admin)
- Personas del fixture

### 5. Verificar

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
print(User.objects.count())  # Debe ser 3
```

### 6. Ejecutar el Servidor

```bash
python manage.py runserver
```

## Rollback a SQLite

Si necesitas volver a SQLite temporalmente:

1. Edita `turnero/settings.py`
2. Comenta la configuración de SQL Server
3. Descomenta DATABASES_SQLITE y renómbralo a DATABASES

## Troubleshooting

### Error: "Driver not found"

Instala el driver ODBC de SQL Server:
https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### Error: "Login failed"

Verifica las credenciales en `.env`:
- SQL_USER=turnero_user
- SQL_PASS=Turnero_2026_Will@CPI

### Error: "Cannot open database"

Ejecuta el script `crear_db_sqlserver.sql` como administrador.
