-- =====================================================
-- Actualización de Mesa para configuración avanzada
-- Fecha: 2026-02-10
-- =====================================================
USE Turnero;
GO

-- 1. Agregar campos a tabla Mesa
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Mesa') AND name = 'FkIdOperadorAsignado')
BEGIN
    ALTER TABLE dbo.Mesa
    ADD FkIdOperadorAsignado INT NULL
        CONSTRAINT FK_Mesa_OperadorAsignado FOREIGN KEY REFERENCES dbo.Usuario(IdUsuario);
END;
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Mesa') AND name = 'Color')
BEGIN
    ALTER TABLE dbo.Mesa
    ADD Color VARCHAR(7) NOT NULL DEFAULT '#FFFFFF';
END;
GO

-- 2. Crear tabla MesaTramite (relación many-to-many)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID('dbo.MesaTramite') AND type = 'U')
BEGIN
    CREATE TABLE dbo.MesaTramite (
        IdMesaTramite INT IDENTITY(1,1) NOT NULL,
        FkIdMesa      INT NOT NULL,
        FkIdTramite   INT NOT NULL,
        
        CONSTRAINT PK_MesaTramite PRIMARY KEY (IdMesaTramite),
        CONSTRAINT FK_MesaTramite_Mesa FOREIGN KEY (FkIdMesa) REFERENCES dbo.Mesa(IdMesa) ON DELETE CASCADE,
        CONSTRAINT FK_MesaTramite_Tramite FOREIGN KEY (FkIdTramite) REFERENCES dbo.Tramite(IdTramite) ON DELETE CASCADE,
        CONSTRAINT UQ_MesaTramite UNIQUE (FkIdMesa, FkIdTramite)
    );
END;
GO

PRINT 'Tablas actualizadas correctamente';
PRINT '- Mesa: agregados campos FkIdOperadorAsignado y Color';
PRINT '- MesaTramite: tabla creada para relación Mesa-Tramite';
GO
