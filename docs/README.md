# 📚 Documentación - Turnero Django

Bienvenido a la documentación del Sistema de Turnos. Esta carpeta contiene toda la información técnica y funcional del proyecto.

## 📖 Índice de Documentación

### Arquitectura
- [Visión General](./arquitectura/vision-general.md) - Arquitectura del sistema
- [Modelos de Datos](./arquitectura/modelos.md) - Esquema de base de datos
- [API REST](./arquitectura/api.md) - Documentación de endpoints

### Pantallas
- [Monitor Público](./pantallas/monitor-publico.md) - Pantalla de sala de espera
- [Panel Operador](./pantallas/panel-operador.md) - Interfaz de atención
- [Dashboard Admin](./pantallas/dashboard-admin.md) - Panel de administración

### Guías
- [Instalación](./guias/instalacion.md) - Configuración del entorno
- [Desarrollo](./guias/desarrollo.md) - Guía para desarrolladores
- [Despliegue](./guias/despliegue.md) - Guía de producción

---

## 🚀 Inicio Rápido

```bash
# Clonar repositorio
git clone <repo-url>
cd turnero_django

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env

# Migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

## 🏗️ Estructura del Proyecto

```
turnero_django/
├── api/                  # API REST (DRF)
├── apps/
│   ├── core/             # Modelos centrales
│   ├── turnos/           # Tótem público y monitor
│   ├── atencion/         # Panel operador
│   └── administracion/   # Dashboard admin
├── docs/                 # 📍 Estás aquí
├── static/               # Archivos estáticos
├── templates/            # Plantillas HTML
└── turnero/              # Configuración Django
```

## 👥 Roles del Sistema

| Rol       | Acceso                  | Funciones                    |
|-----------|-------------------------|------------------------------|
| Público   | Sin autenticación       | Solicitar turno, ver monitor |
| Operador  | `/mesa/`                | Atender turnos               |
| Director  | `/dashboard/`           | Gestión y estadísticas       |
