-- Crear tabla LlamadaTurno para registro de llamadas y re-llamadas
USE Turnero;
GO

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[LlamadaTurno]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[LlamadaTurno] (
        [IdLlamadaTurno] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [FkIdTurno] INT NOT NULL,
        [FechaHoraLlamada] DATETIME2 NOT NULL,
        [FkIdOperador] INT NULL,
        [TipoLlamada] NVARCHAR(20) NOT NULL DEFAULT 'LLAMADA',
        CONSTRAINT [FK_LlamadaTurno_Turno] FOREIGN KEY ([FkIdTurno]) REFERENCES [dbo].[Turno]([IdTurno]) ON DELETE CASCADE,
        CONSTRAINT [FK_LlamadaTurno_Usuario] FOREIGN KEY ([FkIdOperador]) REFERENCES [dbo].[Usuario]([IdUsuario]) ON DELETE SET NULL,
        CONSTRAINT [CK_LlamadaTurno_Tipo] CHECK ([TipoLlamada] IN ('LLAMADA', 'RELLAMADA'))
    );
    
    -- Índices para optimizar consultas
    CREATE NONCLUSTERED INDEX [idx_llamada_turno_fecha] ON [dbo].[LlamadaTurno]([FkIdTurno], [FechaHoraLlamada] DESC);
    CREATE NONCLUSTERED INDEX [idx_llamada_fecha] ON [dbo].[LlamadaTurno]([FechaHoraLlamada] DESC);
    
    PRINT 'Tabla LlamadaTurno creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla LlamadaTurno ya existe';
END
GO
