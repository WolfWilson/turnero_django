-- ============================================================
-- Script: Crear usuario SQL Server para la aplicación Turnero
-- Servidor: web03
-- Base de datos: Turnero
-- Ejecutar con: sqlcmd -S web03 -E -i crear_usuario_sqlserver.sql
-- ============================================================

USE [master]
GO

-- 1) Crear Login a nivel de servidor (si no existe)
IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'turnero_user')
BEGIN
    CREATE LOGIN [turnero_user]
        WITH PASSWORD = N'Turnero_2026_Will@CPI',
             DEFAULT_DATABASE = [Turnero],
             CHECK_POLICY = OFF,
             CHECK_EXPIRATION = OFF;
    PRINT '✓ Login [turnero_user] creado en master';
END
ELSE
    PRINT '○ Login [turnero_user] ya existe';
GO

-- 2) Crear Usuario en la base de datos Turnero
USE [Turnero]
GO

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'turnero_user')
BEGIN
    CREATE USER [turnero_user] FOR LOGIN [turnero_user];
    PRINT '✓ Usuario [turnero_user] creado en Turnero';
END
ELSE
    PRINT '○ Usuario [turnero_user] ya existe en Turnero';
GO

-- ============================================================
-- 3) Permisos sobre tablas propias de la aplicación (dbo.*)
--    Solo SELECT, INSERT, UPDATE, DELETE sobre las tablas que
--    la app necesita. NO se otorga db_owner ni DDL.
-- ============================================================

-- Tablas de solo lectura (catálogos)
GRANT SELECT ON dbo.Rol                TO [turnero_user];
GRANT SELECT ON dbo.EstadoTicket       TO [turnero_user];
GRANT SELECT ON dbo.EstadoTurno        TO [turnero_user];
GRANT SELECT ON dbo.SchemaVersion      TO [turnero_user];
PRINT '✓ Permisos SELECT en catálogos';
GO

-- Tablas de lectura/escritura (entidades principales)
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Usuario                     TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.UsuarioRol                  TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Area                        TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.AreaAdministrador           TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.AreaUsuario                 TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Persona                     TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Mesa                        TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Tramite                     TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.TramiteOperador             TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Ticket                      TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Turno                       TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.TurnoHistorialDerivacion    TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.ConfiguracionArea           TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.ConfiguracionAreaHistorial  TO [turnero_user];
PRINT '✓ Permisos CRUD en tablas principales';
GO

-- ============================================================
-- 4) Permisos sobre tablas de Django (auth, sessions, admin, etc.)
--    Necesarias para login, sesiones y el admin de Django.
-- ============================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.auth_user              TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.auth_group             TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.auth_permission        TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.auth_user_groups       TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.auth_user_user_permissions  TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.auth_group_permissions TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.django_session         TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.django_admin_log       TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.django_content_type    TO [turnero_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.django_migrations      TO [turnero_user];
PRINT '✓ Permisos CRUD en tablas Django';
GO

-- ============================================================
-- 5) Verificación
-- ============================================================
PRINT '';
PRINT '============================================================';
PRINT '  RESUMEN DE PERMISOS OTORGADOS A [turnero_user]';
PRINT '============================================================';

SELECT 
    dp.permission_name  AS Permiso,
    o.name              AS Tabla,
    dp.state_desc       AS Estado
FROM sys.database_permissions dp
JOIN sys.objects o ON dp.major_id = o.object_id
JOIN sys.database_principals pr ON dp.grantee_principal_id = pr.principal_id
WHERE pr.name = 'turnero_user'
ORDER BY o.name, dp.permission_name;
GO

PRINT '';
PRINT '✓ Script completado. El usuario [turnero_user] tiene permisos';
PRINT '  mínimos (solo CRUD en tablas necesarias, sin DDL ni db_owner).';
GO
