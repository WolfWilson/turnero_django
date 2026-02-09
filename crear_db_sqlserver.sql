-- ============================================================
-- Script de Creación de Base de Datos: Turnero
-- Servidor: web03
-- SQL Server 2012+
-- ============================================================

USE master;
GO

-- Crear la base de datos
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'Turnero')
BEGIN
    CREATE DATABASE Turnero;
    PRINT 'Base de datos Turnero creada exitosamente';
END
ELSE
BEGIN
    PRINT 'La base de datos Turnero ya existe';
END
GO

USE Turnero;
GO

-- Crear el usuario si no existe
IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = 'turnero_user')
BEGIN
    CREATE LOGIN turnero_user 
    WITH PASSWORD = 'Turnero_2026_Will@CPI',
    CHECK_POLICY = OFF,
    CHECK_EXPIRATION = OFF;
    PRINT 'Login turnero_user creado exitosamente';
END
ELSE
BEGIN
    PRINT 'El login turnero_user ya existe';
END
GO

-- Crear usuario en la base de datos
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'turnero_user')
BEGIN
    CREATE USER turnero_user FOR LOGIN turnero_user;
    PRINT 'Usuario turnero_user creado en la base de datos';
END
GO

-- Otorgar permisos
ALTER ROLE db_owner ADD MEMBER turnero_user;
GO

PRINT '==================================================';
PRINT 'Creando tablas del sistema Turnero...';
PRINT '==================================================';
GO

-- ============================================================
-- TABLA: SchemaVersion
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SchemaVersion')
BEGIN
    CREATE TABLE dbo.SchemaVersion (
        IdVersion INT IDENTITY(1,1) PRIMARY KEY,
        Version NVARCHAR(20) NOT NULL,
        Descripcion NVARCHAR(255) NOT NULL,
        FechaAplicacion DATETIME2 NOT NULL DEFAULT SYSDATETIME()
    );
    PRINT '✓ Tabla SchemaVersion creada';
END
GO

-- ============================================================
-- TABLA: Usuario
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Usuario')
BEGIN
    CREATE TABLE dbo.Usuario (
        IdUsuario INT IDENTITY(1,1) PRIMARY KEY,
        Username NVARCHAR(150) NOT NULL UNIQUE,
        DisplayName NVARCHAR(200) NOT NULL,
        Email NVARCHAR(254),
        IsActive BIT NOT NULL DEFAULT 1
    );
    PRINT '✓ Tabla Usuario creada';
END
GO

-- ============================================================
-- TABLA: Area
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Area')
BEGIN
    CREATE TABLE dbo.Area (
        IdArea INT IDENTITY(1,1) PRIMARY KEY,
        Nombre NVARCHAR(100) NOT NULL UNIQUE,
        Slug NVARCHAR(50) NOT NULL UNIQUE,
        Activa BIT NOT NULL DEFAULT 1
    );
    PRINT '✓ Tabla Area creada';
END
GO

-- ============================================================
-- TABLA: Persona
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Persona')
BEGIN
    CREATE TABLE dbo.Persona (
        IdPersona INT IDENTITY(1,1) PRIMARY KEY,
        Dni INT NOT NULL UNIQUE,
        Nombre NVARCHAR(120) NOT NULL,
        Apellido NVARCHAR(120) NOT NULL,
        FechaNacimiento DATE
    );
    PRINT '✓ Tabla Persona creada';
END
GO

-- ============================================================
-- TABLA: EstadoTicket
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'EstadoTicket')
BEGIN
    CREATE TABLE dbo.EstadoTicket (
        IdEstadoTicket TINYINT PRIMARY KEY,
        Nombre NVARCHAR(20) NOT NULL UNIQUE,
        Descripcion NVARCHAR(255) NOT NULL
    );
    PRINT '✓ Tabla EstadoTicket creada';
END
GO

-- ============================================================
-- TABLA: EstadoTurno
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'EstadoTurno')
BEGIN
    CREATE TABLE dbo.EstadoTurno (
        IdEstadoTurno TINYINT PRIMARY KEY,
        Nombre NVARCHAR(20) NOT NULL UNIQUE,
        Descripcion NVARCHAR(255) NOT NULL
    );
    PRINT '✓ Tabla EstadoTurno creada';
END
GO

-- ============================================================
-- TABLA: Mesa
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Mesa')
BEGIN
    CREATE TABLE dbo.Mesa (
        IdMesa INT IDENTITY(1,1) PRIMARY KEY,
        FkIdArea INT NOT NULL,
        Nombre NVARCHAR(20) NOT NULL,
        Activa BIT NOT NULL DEFAULT 1,
        CONSTRAINT FK_Mesa_Area FOREIGN KEY (FkIdArea) REFERENCES dbo.Area(IdArea),
        CONSTRAINT UQ_Mesa_Area_Nombre UNIQUE (FkIdArea, Nombre)
    );
    PRINT '✓ Tabla Mesa creada';
END
GO

-- ============================================================
-- TABLA: Tramite
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Tramite')
BEGIN
    CREATE TABLE dbo.Tramite (
        IdTramite INT IDENTITY(1,1) PRIMARY KEY,
        FkIdArea INT NOT NULL,
        Nombre NVARCHAR(100) NOT NULL,
        Activa BIT NOT NULL DEFAULT 1,
        CONSTRAINT FK_Tramite_Area FOREIGN KEY (FkIdArea) REFERENCES dbo.Area(IdArea),
        CONSTRAINT UQ_Tramite_Area_Nombre UNIQUE (FkIdArea, Nombre)
    );
    PRINT '✓ Tabla Tramite creada';
END
GO

-- ============================================================
-- TABLA: Rol
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Rol')
BEGIN
    CREATE TABLE dbo.Rol (
        IdRol TINYINT PRIMARY KEY,
        NombreRol NVARCHAR(50) NOT NULL UNIQUE,
        Descripcion NVARCHAR(255)
    );
    PRINT '✓ Tabla Rol creada';
END
GO

-- ============================================================
-- TABLA: Ticket
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Ticket')
BEGIN
    CREATE TABLE dbo.Ticket (
        IdTicket INT IDENTITY(1,1) PRIMARY KEY,
        FkIdPersona INT NOT NULL,
        FkIdArea INT NOT NULL,
        Prioridad INT NOT NULL DEFAULT 0,
        FechaCreacion DATE NOT NULL DEFAULT CAST(SYSDATETIME() AS DATE),
        FechaHoraCreacion DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        FkIdEstadoTicket TINYINT NOT NULL DEFAULT 0,
        CONSTRAINT FK_Ticket_Persona FOREIGN KEY (FkIdPersona) REFERENCES dbo.Persona(IdPersona) ON DELETE CASCADE,
        CONSTRAINT FK_Ticket_Area FOREIGN KEY (FkIdArea) REFERENCES dbo.Area(IdArea) ON DELETE CASCADE,
        CONSTRAINT FK_Ticket_Estado FOREIGN KEY (FkIdEstadoTicket) REFERENCES dbo.EstadoTicket(IdEstadoTicket),
        CONSTRAINT UQ_Ticket_IdTicket_FkIdArea UNIQUE (IdTicket, FkIdArea)
    );
    CREATE INDEX IX_Ticket_Cola ON dbo.Ticket(FkIdArea, FkIdEstadoTicket, Prioridad, FechaHoraCreacion);
    PRINT '✓ Tabla Ticket creada';
END
GO

-- ============================================================
-- TABLA: Turno
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Turno')
BEGIN
    CREATE TABLE dbo.Turno (
        IdTurno INT IDENTITY(1,1) PRIMARY KEY,
        FkIdTicket INT NOT NULL,
        FkIdTramite INT NOT NULL,
        Orden INT NOT NULL DEFAULT 1,
        FkIdArea INT NOT NULL,
        NumeroVisible INT NOT NULL DEFAULT 0,
        FkIdMesaAsignada INT,
        FkIdEstadoTurno TINYINT NOT NULL DEFAULT 0,
        FechaTurno DATE NOT NULL DEFAULT CAST(SYSDATETIME() AS DATE),
        FechaHoraCreacion DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        FkIdOperador INT,
        MotivoReal NVARCHAR(2000),
        FechaHoraInicioAtencion DATETIME2,
        FechaHoraFinAtencion DATETIME2,
        CONSTRAINT FK_Turno_Ticket FOREIGN KEY (FkIdTicket) REFERENCES dbo.Ticket(IdTicket) ON DELETE CASCADE,
        CONSTRAINT FK_Turno_Tramite FOREIGN KEY (FkIdTramite) REFERENCES dbo.Tramite(IdTramite),
        CONSTRAINT FK_Turno_Estado FOREIGN KEY (FkIdEstadoTurno) REFERENCES dbo.EstadoTurno(IdEstadoTurno),
        CONSTRAINT FK_Turno_MesaAsignada FOREIGN KEY (FkIdMesaAsignada) REFERENCES dbo.Mesa(IdMesa) ON DELETE SET NULL,
        CONSTRAINT FK_Turno_Operador FOREIGN KEY (FkIdOperador) REFERENCES dbo.Usuario(IdUsuario),
        CONSTRAINT FK_Turno_Ticket_Area_Coherencia FOREIGN KEY (FkIdTicket, FkIdArea) REFERENCES dbo.Ticket(IdTicket, FkIdArea)
    );
    CREATE INDEX IX_Turno_Monitor ON dbo.Turno(FkIdMesaAsignada, FkIdEstadoTurno);
    CREATE INDEX IX_Turno_Cola ON dbo.Turno(FkIdArea, FkIdEstadoTurno);
    PRINT '✓ Tabla Turno creada';
END
GO

-- ============================================================
-- TABLA: TurnoHistorialDerivacion
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TurnoHistorialDerivacion')
BEGIN
    CREATE TABLE dbo.TurnoHistorialDerivacion (
        IdTurnoHistorialDerivacion INT IDENTITY(1,1) PRIMARY KEY,
        FkIdTurno INT NOT NULL,
        FkIdOperadorOrigen INT NOT NULL,
        FkIdOperadorDestino INT NOT NULL,
        FechaHoraDerivacion DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        Motivo NVARCHAR(500),
        CONSTRAINT FK_Historial_Turno FOREIGN KEY (FkIdTurno) REFERENCES dbo.Turno(IdTurno) ON DELETE CASCADE,
        CONSTRAINT FK_Historial_OperadorOrigen FOREIGN KEY (FkIdOperadorOrigen) REFERENCES dbo.Usuario(IdUsuario),
        CONSTRAINT FK_Historial_OperadorDestino FOREIGN KEY (FkIdOperadorDestino) REFERENCES dbo.Usuario(IdUsuario)
    );
    PRINT '✓ Tabla TurnoHistorialDerivacion creada';
END
GO

-- ============================================================
-- TABLA: UsuarioRol
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'UsuarioRol')
BEGIN
    CREATE TABLE dbo.UsuarioRol (
        FkIdUsuario INT NOT NULL,
        FkIdRol TINYINT NOT NULL,
        CONSTRAINT PK_UsuarioRol PRIMARY KEY (FkIdUsuario, FkIdRol),
        CONSTRAINT FK_UsuarioRol_Usuario FOREIGN KEY (FkIdUsuario) REFERENCES dbo.Usuario(IdUsuario) ON DELETE CASCADE,
        CONSTRAINT FK_UsuarioRol_Rol FOREIGN KEY (FkIdRol) REFERENCES dbo.Rol(IdRol) ON DELETE CASCADE
    );
    PRINT '✓ Tabla UsuarioRol creada';
END
GO

-- ============================================================
-- TABLA: AreaAdministrador
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AreaAdministrador')
BEGIN
    CREATE TABLE dbo.AreaAdministrador (
        IdAreaAdministrador INT IDENTITY(1,1) PRIMARY KEY,
        FkIdUsuario INT NOT NULL,
        FkIdArea INT NOT NULL,
        CONSTRAINT FK_AreaAdministrador_Usuario FOREIGN KEY (FkIdUsuario) REFERENCES dbo.Usuario(IdUsuario) ON DELETE CASCADE,
        CONSTRAINT FK_AreaAdministrador_Area FOREIGN KEY (FkIdArea) REFERENCES dbo.Area(IdArea) ON DELETE CASCADE,
        CONSTRAINT UQ_AreaAdministrador_Usuario_Area UNIQUE (FkIdUsuario, FkIdArea)
    );
    PRINT '✓ Tabla AreaAdministrador creada';
END
GO

-- ============================================================
-- TABLA: AreaUsuario
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AreaUsuario')
BEGIN
    CREATE TABLE dbo.AreaUsuario (
        IdAreaUsuario INT IDENTITY(1,1) PRIMARY KEY,
        FkIdArea INT NOT NULL,
        FkIdUsuario INT NOT NULL,
        CONSTRAINT FK_AreaUsuario_Area FOREIGN KEY (FkIdArea) REFERENCES dbo.Area(IdArea) ON DELETE CASCADE,
        CONSTRAINT FK_AreaUsuario_Usuario FOREIGN KEY (FkIdUsuario) REFERENCES dbo.Usuario(IdUsuario) ON DELETE CASCADE,
        CONSTRAINT UQ_Area_Usuario UNIQUE (FkIdArea, FkIdUsuario)
    );
    PRINT '✓ Tabla AreaUsuario creada';
END
GO

-- ============================================================
-- TABLA: TramiteOperador
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TramiteOperador')
BEGIN
    CREATE TABLE dbo.TramiteOperador (
        IdTramiteOperador INT IDENTITY(1,1) PRIMARY KEY,
        FkIdOperador INT NOT NULL,
        FkIdTramite INT NOT NULL,
        Habilitada BIT NOT NULL DEFAULT 1,
        PrioridadAtencion TINYINT NOT NULL DEFAULT 1,
        CONSTRAINT FK_TramiteOperador_Operador FOREIGN KEY (FkIdOperador) REFERENCES dbo.Usuario(IdUsuario) ON DELETE CASCADE,
        CONSTRAINT FK_TramiteOperador_Tramite FOREIGN KEY (FkIdTramite) REFERENCES dbo.Tramite(IdTramite) ON DELETE CASCADE,
        CONSTRAINT UQ_TramiteOperador_Operador_Tramite UNIQUE (FkIdOperador, FkIdTramite)
    );
    PRINT '✓ Tabla TramiteOperador creada';
END
GO

-- ============================================================
-- TABLA: ConfiguracionArea
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ConfiguracionArea')
BEGIN
    CREATE TABLE dbo.ConfiguracionArea (
        IdConfiguracionArea INT IDENTITY(1,1) PRIMARY KEY,
        FkIdArea INT NOT NULL,
        Clave NVARCHAR(100) NOT NULL,
        Valor NVARCHAR(2000) NOT NULL,
        Descripcion NVARCHAR(255),
        CONSTRAINT FK_Configuracion_Area FOREIGN KEY (FkIdArea) REFERENCES dbo.Area(IdArea) ON DELETE CASCADE,
        CONSTRAINT UQ_Configuracion_Area_Clave UNIQUE (FkIdArea, Clave)
    );
    PRINT '✓ Tabla ConfiguracionArea creada';
END
GO

-- ============================================================
-- TABLA: ConfiguracionAreaHistorial
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ConfiguracionAreaHistorial')
BEGIN
    CREATE TABLE dbo.ConfiguracionAreaHistorial (
        IdConfiguracionAreaHistorial INT IDENTITY(1,1) PRIMARY KEY,
        FkIdConfiguracionArea INT NOT NULL,
        ValorAnterior NVARCHAR(2000),
        ValorNuevo NVARCHAR(2000) NOT NULL,
        FkIdUsuarioModifico INT NOT NULL,
        FechaHoraModificacion DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT FK_Historial_Configuracion FOREIGN KEY (FkIdConfiguracionArea) REFERENCES dbo.ConfiguracionArea(IdConfiguracionArea) ON DELETE CASCADE,
        CONSTRAINT FK_Historial_Usuario FOREIGN KEY (FkIdUsuarioModifico) REFERENCES dbo.Usuario(IdUsuario)
    );
    PRINT '✓ Tabla ConfiguracionAreaHistorial creada';
END
GO

PRINT '';
PRINT '==================================================';
PRINT 'Insertando datos maestros...';
PRINT '==================================================';
GO

-- ============================================================
-- DATOS MAESTROS: EstadoTicket
-- ============================================================
IF NOT EXISTS (SELECT * FROM dbo.EstadoTicket)
BEGIN
    INSERT INTO dbo.EstadoTicket (IdEstadoTicket, Nombre, Descripcion) VALUES
    (0, 'Pendiente', 'Ticket creado, esperando asignación a turno'),
    (1, 'EnProceso', 'Ticket tiene turnos en proceso'),
    (2, 'Completado', 'Todos los turnos del ticket fueron atendidos'),
    (3, 'Cancelado', 'Ticket cancelado');
    PRINT '✓ Estados de Ticket insertados';
END
GO

-- ============================================================
-- DATOS MAESTROS: EstadoTurno
-- ============================================================
IF NOT EXISTS (SELECT * FROM dbo.EstadoTurno)
BEGIN
    INSERT INTO dbo.EstadoTurno (IdEstadoTurno, Nombre, Descripcion) VALUES
    (0, 'Pendiente', 'Turno en cola, esperando ser llamado'),
    (1, 'Llamando', 'Turno está siendo llamado en el monitor'),
    (2, 'EnAtencion', 'Turno siendo atendido por operador'),
    (3, 'Finalizado', 'Atención completada'),
    (4, 'NoPresento', 'Cliente no se presentó al llamado'),
    (5, 'Derivado', 'Turno derivado a otro operador');
    PRINT '✓ Estados de Turno insertados';
END
GO

-- ============================================================
-- DATOS MAESTROS: Rol
-- ============================================================
IF NOT EXISTS (SELECT * FROM dbo.Rol)
BEGIN
    INSERT INTO dbo.Rol (IdRol, NombreRol, Descripcion) VALUES
    (1, 'Administrador', 'Administrador del sistema con acceso completo'),
    (2, 'Director', 'Director de área con acceso a dashboard y configuración'),
    (3, 'Operador', 'Operador de mesa de atención'),
    (4, 'Supervisor', 'Supervisor de área');
    PRINT '✓ Roles insertados';
END
GO

-- ============================================================
-- VERSIÓN DEL ESQUEMA
-- ============================================================
IF NOT EXISTS (SELECT * FROM dbo.SchemaVersion WHERE Version = '1.0.0')
BEGIN
    INSERT INTO dbo.SchemaVersion (Version, Descripcion) 
    VALUES ('1.0.0', 'Esquema inicial del sistema de turnos');
    PRINT '✓ Versión de esquema registrada: 1.0.0';
END
GO

PRINT '';
PRINT '==================================================';
PRINT '✅ BASE DE DATOS CONFIGURADA EXITOSAMENTE';
PRINT '==================================================';
PRINT '';
PRINT 'Siguiente paso: python manage.py runserver';
PRINT '';
GO
