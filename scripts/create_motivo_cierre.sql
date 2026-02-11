-- =====================================================================
-- Script: Crear tabla MotivoCierre y actualizar Turno
-- Fecha: 2026-02-11
-- Descripción: Motivos de cierre configurables + prioridad + observaciones
-- =====================================================================

USE Turnero;
GO

-- Crear tabla MotivoCierre si no existe
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[MotivoCierre]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[MotivoCierre] (
        [IdMotivoCierre] INT IDENTITY(1,1) NOT NULL,
        [Nombre] NVARCHAR(100) NOT NULL,
        [Descripcion] NVARCHAR(255) NOT NULL DEFAULT '',
        [Activo] BIT NOT NULL DEFAULT 1,
        [Orden] SMALLINT NOT NULL DEFAULT 0,
        CONSTRAINT [PK_MotivoCierre] PRIMARY KEY CLUSTERED ([IdMotivoCierre] ASC),
        CONSTRAINT [UQ_MotivoCierre_Nombre] UNIQUE ([Nombre])
    );
    
    CREATE NONCLUSTERED INDEX [IX_MotivoCierre_Activo_Orden] 
    ON [dbo].[MotivoCierre] ([Activo], [Orden]) INCLUDE ([Nombre]);
    
    PRINT '✓ Tabla MotivoCierre creada';
END
ELSE
    PRINT '⚠ Tabla MotivoCierre ya existe';
GO

-- Agregar columnas a Turno si no existen
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[Turno]') AND name = 'FkIdMotivoCierre')
BEGIN
    ALTER TABLE [dbo].[Turno]
    ADD [FkIdMotivoCierre] INT NULL;
    
    ALTER TABLE [dbo].[Turno]
    ADD CONSTRAINT [FK_Turno_MotivoCierre] 
    FOREIGN KEY ([FkIdMotivoCierre]) REFERENCES [dbo].[MotivoCierre] ([IdMotivoCierre])
    ON DELETE SET NULL;
    
    PRINT '✓ Columna FkIdMotivoCierre agregada a Turno';
END
ELSE
    PRINT '⚠ Columna FkIdMotivoCierre ya existe en Turno';
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[Turno]') AND name = 'PrioridadConsulta')
BEGIN
    ALTER TABLE [dbo].[Turno]
    ADD [PrioridadConsulta] SMALLINT NOT NULL DEFAULT 0;
    
    PRINT '✓ Columna PrioridadConsulta agregada a Turno';
END
ELSE
    PRINT '⚠ Columna PrioridadConsulta ya existe en Turno';
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[Turno]') AND name = 'Observaciones')
BEGIN
    ALTER TABLE [dbo].[Turno]
    ADD [Observaciones] NVARCHAR(MAX) NULL;
    
    PRINT '✓ Columna Observaciones agregada a Turno';
END
ELSE
    PRINT '⚠ Columna Observaciones ya existe en Turno';
GO

-- Insertar motivos de cierre por defecto
IF NOT EXISTS (SELECT * FROM [dbo].[MotivoCierre] WHERE [Nombre] = 'Consulta informativa')
BEGIN
    INSERT INTO [dbo].[MotivoCierre] ([Nombre], [Descripcion], [Activo], [Orden])
    VALUES 
        ('Consulta informativa', 'Solicitud de información general', 1, 1),
        ('Trámite completado', 'Trámite realizado exitosamente', 1, 2),
        ('Documentación pendiente', 'Requiere documentación adicional', 1, 3),
        ('Derivado a otra área', 'Turno derivado para continuar atención', 1, 4),
        ('No corresponde', 'El trámite no corresponde al área', 1, 5),
        ('Otro', 'Otro motivo no especificado', 1, 99);
    
    PRINT '✓ Motivos de cierre por defecto insertados';
END
ELSE
    PRINT '⚠ Motivos de cierre ya existen';
GO

PRINT '========================================';
PRINT 'Script completado exitosamente';
PRINT '========================================';
GO
