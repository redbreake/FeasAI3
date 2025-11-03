import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Busqueda
from core.utils import clasificar_consulta

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Reclasifica todas las búsquedas existentes usando la función clasificar_consulta()'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta el comando en modo prueba sin aplicar cambios',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Aplica los cambios sin pedir confirmación',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        if dry_run:
            self.stdout.write(
                self.style.WARNING('Ejecutando en modo DRY-RUN. No se aplicarán cambios.')
            )

        # Obtener todas las búsquedas existentes
        busquedas = Busqueda.objects.all()
        total_busquedas = busquedas.count()

        self.stdout.write(f'Encontradas {total_busquedas} búsquedas para reclasificar.')

        cambios_aplicados = 0
        cambios_pendientes = []

        for busqueda in busquedas:
            nueva_categoria = clasificar_consulta(busqueda.texto_problema)
            categoria_actual = busqueda.categoria

            if nueva_categoria != categoria_actual:
                cambios_pendientes.append({
                    'id': busqueda.id,
                    'usuario': busqueda.usuario.username,
                    'texto_original': busqueda.texto_problema[:100] + '...' if len(busqueda.texto_problema) > 100 else busqueda.texto_problema,
                    'categoria_actual': categoria_actual,
                    'nueva_categoria': nueva_categoria,
                })

        if not cambios_pendientes:
            self.stdout.write(
                self.style.SUCCESS('No hay cambios pendientes. Todas las categorías están actualizadas.')
            )
            return

        self.stdout.write(f'Se encontraron {len(cambios_pendientes)} búsquedas con categorías desactualizadas.')

        # Mostrar cambios pendientes
        for cambio in cambios_pendientes:
            self.stdout.write(
                f'ID: {cambio["id"]} | Usuario: {cambio["usuario"]} | '
                f'Actual: {cambio["categoria_actual"]} -> Nueva: {cambio["nueva_categoria"]}\n'
                f'Texto: {cambio["texto_original"]}\n'
            )

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'DRY-RUN completado. {len(cambios_pendientes)} cambios pendientes.')
            )
            return

        if not force:
            # Confirmar aplicación de cambios
            self.stdout.write('\n¿Aplicar los cambios? (y/N): ', ending='')
            respuesta = input().strip().lower()

            if respuesta != 'y':
                self.stdout.write('Operación cancelada.')
                return

        # Aplicar cambios en una transacción
        with transaction.atomic():
            for cambio in cambios_pendientes:
                try:
                    busqueda = Busqueda.objects.get(id=cambio['id'])
                    busqueda.categoria = cambio['nueva_categoria']
                    busqueda.save()

                    logger.info(
                        f'Búsqueda ID {busqueda.id} reclasificada: '
                        f'{cambio["categoria_actual"]} -> {cambio["nueva_categoria"]}'
                    )
                    cambios_aplicados += 1

                except Exception as e:
                    logger.error(f'Error al reclasificar búsqueda ID {cambio["id"]}: {str(e)}')
                    self.stdout.write(
                        self.style.ERROR(f'Error al procesar búsqueda ID {cambio["id"]}: {str(e)}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Reclasificación completada. {cambios_aplicados} búsquedas actualizadas.')
        )

        # Log final
        logger.info(f'Comando reclasificar_busquedas completado. Cambios aplicados: {cambios_aplicados}')