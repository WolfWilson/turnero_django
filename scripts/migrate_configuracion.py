"""
Script para migrar la tabla ConfiguracionArea de clave/valor a campos estructurados.
Ejecutar: python scripts/migrate_configuracion.py
"""
import os, sys, django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'turnero.settings')
django.setup()

from django.db import connections

SQL_STATEMENTS = [
    # 1. Borrar historial que referencia la tabla vieja
    "IF OBJECT_ID('ConfiguracionAreaHistorial', 'U') IS NOT NULL DROP TABLE ConfiguracionAreaHistorial;",

    # 2. Borrar tabla vieja
    "IF OBJECT_ID('ConfiguracionArea', 'U') IS NOT NULL DROP TABLE ConfiguracionArea;",

    # 3. Crear tabla nueva con campos estructurados
    """
    CREATE TABLE ConfiguracionArea (
        IdConfiguracionArea     INT IDENTITY(1,1) PRIMARY KEY,
        FkIdArea                INT NOT NULL UNIQUE,

        -- TURNOS
        PermitirSinDni          BIT NOT NULL DEFAULT 0,
        MultiplesTurnosDni      BIT NOT NULL DEFAULT 1,
        MaxTurnosPorDia         SMALLINT NOT NULL DEFAULT 3,
        VencimientoTurnos       BIT NOT NULL DEFAULT 1,

        -- PRIORIDADES
        PrioridadAdultoMayor    BIT NOT NULL DEFAULT 1,
        PrioridadEmbarazadas    BIT NOT NULL DEFAULT 1,
        PrioridadDiscapacidad   BIT NOT NULL DEFAULT 1,

        -- VISUALES
        MensajePantalla         NVARCHAR(150) NOT NULL DEFAULT N'El final es en donde partí',
        MediaHabilitada         BIT NOT NULL DEFAULT 0,

        -- OPERACIÓN
        PermitirDerivaciones    BIT NOT NULL DEFAULT 0,
        RequiereMotivoFin       BIT NOT NULL DEFAULT 1,

        -- HORARIO DE ATENCIÓN
        EmisionHoraInicio       TIME NOT NULL DEFAULT '07:00',
        EmisionHoraFin          TIME NOT NULL DEFAULT '12:30',
        AtencionHoraInicio      TIME NOT NULL DEFAULT '07:30',
        AtencionHoraFin         TIME NOT NULL DEFAULT '12:30',

        -- CONFIGURACIÓN GENERAL
        TiempoLlamadaSeg        SMALLINT NOT NULL DEFAULT 10,
        VozLlamada              BIT NOT NULL DEFAULT 0,
        SonidoLlamada           BIT NOT NULL DEFAULT 1,

        CONSTRAINT FK_ConfigArea_Area FOREIGN KEY (FkIdArea) REFERENCES Area(IdArea)
    );
    """,

    # 4. Recrear tabla de historial/auditoría
    """
    CREATE TABLE ConfiguracionAreaHistorial (
        IdConfiguracionAreaHistorial INT IDENTITY(1,1) PRIMARY KEY,
        FkIdConfiguracionArea        INT NOT NULL,
        CampoModificado              NVARCHAR(100) NOT NULL,
        ValorAnterior                NVARCHAR(2000) NULL,
        ValorNuevo                   NVARCHAR(2000) NOT NULL,
        FkIdUsuarioModifico          INT NOT NULL,
        FechaHoraModificacion        DATETIME2 NOT NULL DEFAULT GETDATE(),

        CONSTRAINT FK_ConfigHist_Config FOREIGN KEY (FkIdConfiguracionArea)
            REFERENCES ConfiguracionArea(IdConfiguracionArea),
        CONSTRAINT FK_ConfigHist_Usuario FOREIGN KEY (FkIdUsuarioModifico)
            REFERENCES Usuario(IdUsuario)
    );
    """,

    # 5. Insertar configuración por defecto para el área existente (ID=1)
    """
    INSERT INTO ConfiguracionArea (FkIdArea)
    SELECT IdArea FROM Area WHERE IdArea NOT IN (SELECT FkIdArea FROM ConfiguracionArea);
    """,

    # 6. Actualizar versión del schema
    """
    INSERT INTO SchemaVersion (Version, Descripcion, FechaAplicacion)
    VALUES ('1.3.0', 'ConfiguracionArea: migración de clave/valor a campos estructurados', GETDATE());
    """,
]


def main():
    cursor = connections['default'].cursor()
    
    print("=" * 60)
    print("  MIGRACIÓN: ConfiguracionArea → Campos Estructurados")
    print("=" * 60)
    
    for i, sql in enumerate(SQL_STATEMENTS, 1):
        desc = sql.strip().split('\n')[0][:80]
        print(f"\n[{i}/{len(SQL_STATEMENTS)}] {desc}...")
        try:
            cursor.execute(sql)
            print(f"  ✓ OK")
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            raise
    
    # Verificar resultado
    cursor.execute("SELECT COUNT(*) FROM ConfiguracionArea")
    count = cursor.fetchone()[0]
    print(f"\n{'=' * 60}")
    print(f"  ✓ Migración completada. {count} configuración(es) creada(s).")
    
    # Mostrar configuración insertada
    cursor.execute("""
        SELECT ca.IdConfiguracionArea, a.Nombre,
               ca.PermitirSinDni, ca.MultiplesTurnosDni, ca.MaxTurnosPorDia,
               ca.EmisionHoraInicio, ca.EmisionHoraFin,
               ca.MensajePantalla
        FROM ConfiguracionArea ca
        JOIN Area a ON a.IdArea = ca.FkIdArea
    """)
    for row in cursor.fetchall():
        print(f"\n  Área: {row[1]}")
        print(f"    Sin DNI: {'Sí' if row[2] else 'No'} | Múltiples: {'Sí' if row[3] else 'No'} | Máx/día: {row[4]}")
        print(f"    Emisión: {row[5]} - {row[6]}")
        print(f"    Mensaje: {row[7]}")
    
    print(f"\n{'=' * 60}")


if __name__ == "__main__":
    main()
