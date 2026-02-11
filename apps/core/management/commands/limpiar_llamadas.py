"""
Management command para limpiar eventos antiguos de LlamadaTurno.
Uso: python manage.py limpiar_llamadas [--dias DIAS]
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.core.models import LlamadaTurno


class Command(BaseCommand):
    help = 'Limpia eventos antiguos de LlamadaTurno (por defecto mayores a 7 días)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=7,
            help='Número de días de antigüedad para eliminar (default: 7)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra cuántos registros se eliminarían sin borrar'
        )

    def handle(self, *args, **options):
        dias = options['dias']
        dry_run = options['dry_run']
        
        limite = timezone.now() - timedelta(days=dias)
        eventos_antiguos = LlamadaTurno.objects.filter(fecha_hora__lt=limite)
        
        count = eventos_antiguos.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[DRY RUN] Se eliminarían {count} eventos de llamada "
                    f"anteriores a {limite.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            )
        else:
            if count == 0:
                self.stdout.write(
                    self.style.SUCCESS("No hay eventos antiguos para limpiar")
                )
            else:
                eventos_antiguos.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Eliminados {count} eventos de llamada "
                        f"anteriores a {limite.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                )
