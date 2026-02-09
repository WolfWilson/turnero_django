# Script para migrar datos de SQLite a SQL Server
# Ejecutar después de crear la DB en SQL Server y aplicar migraciones

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'turnero.settings')
django.setup()

from django.contrib.auth.models import User, Group
from apps.core.models import Area, Tramite, Mesa, Persona, Turno

print("=" * 60)
print("MIGRACIÓN DE DATOS: SQLite → SQL Server")
print("=" * 60)

# Datos a migrar desde SQLite
datos_migracion = {
    'grupos': [
        {'name': 'Director'},
        {'name': 'Operador'},
    ],
    'usuarios': [
        {
            'username': 'wbenitez',
            'email': 'wbenitez@example.com',
            'first_name': 'Will',
            'last_name': 'Benitez',
            'password': 'turnero1986',
            'is_superuser': True,
            'is_staff': True,
            'grupos': ['Director']
        },
        {
            'username': 'abouvier',
            'email': 'abouvier@example.com',
            'first_name': 'Antonio',
            'last_name': 'Bouvier',
            'password': 'TuPass123',
            'grupos': ['Director']
        },
        {
            'username': 'wil_admin',
            'email': 'wil_admin@example.com',
            'first_name': 'Wil',
            'last_name': 'Admin',
            'password': 'Metallica123',
            'grupos': ['Operador']
        },
    ],
    'personas': [
        {'dni': 12345678, 'nombre': 'MARÍA', 'apellido': 'SÁNCHEZ'},
        {'dni': 87654321, 'nombre': 'JUAN', 'apellido': 'PÉREZ'},
        {'dni': 56789012, 'nombre': 'ANA', 'apellido': 'GÓMEZ'},
    ]
}

try:
    # 1. Crear grupos
    print("\n1. Creando grupos...")
    for grupo_data in datos_migracion['grupos']:
        grupo, created = Group.objects.get_or_create(name=grupo_data['name'])
        print(f"   {'✓' if created else '○'} Grupo: {grupo.name}")

    # 2. Crear usuarios
    print("\n2. Creando usuarios...")
    for user_data in datos_migracion['usuarios']:
        username = user_data['username']
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': user_data.get('email', ''),
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'is_superuser': user_data.get('is_superuser', False),
                'is_staff': user_data.get('is_staff', False),
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
        
        # Agregar a grupos
        for grupo_name in user_data.get('grupos', []):
            grupo = Group.objects.get(name=grupo_name)
            user.groups.add(grupo)
        
        print(f"   {'✓' if created else '○'} Usuario: {username} ({', '.join(user_data.get('grupos', []))})")

    # 3. Crear personas del fixture
    print("\n3. Creando personas...")
    for persona_data in datos_migracion['personas']:
        persona, created = Persona.objects.get_or_create(
            dni=persona_data['dni'],
            defaults={
                'nombre': persona_data['nombre'],
                'apellido': persona_data['apellido'],
            }
        )
        print(f"   {'✓' if created else '○'} Persona: {persona.nombre} {persona.apellido} (DNI: {persona.dni})")

    print("\n" + "=" * 60)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print("\nResumen:")
    print(f"  - Grupos: {Group.objects.count()}")
    print(f"  - Usuarios: {User.objects.count()}")
    print(f"  - Personas: {Persona.objects.count()}")
    print(f"  - Áreas: {Area.objects.count()}")
    print(f"  - Trámites: {Tramite.objects.count()}")
    print(f"  - Mesas: {Mesa.objects.count()}")
    print(f"  - Turnos: {Turno.objects.count()}")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
