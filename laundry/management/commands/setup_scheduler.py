"""
Comando de gerenciamento para configurar o scheduler do django-q.

Este comando cria ou atualiza a tarefa periódica que libera máquinas
automaticamente quando o tempo de ciclo expira.

Uso:
    python manage.py setup_scheduler
"""
from django.core.management.base import BaseCommand
from django_q.models import Schedule
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Configura o scheduler para liberar máquinas automaticamente'

    def handle(self, *args, **options):
        # Nome da tarefa
        task_name = 'Liberar Máquinas Expiradas'
        func = 'laundry.tasks.liberar_maquinas_expiradas'
        
        # Verifica se já existe uma tarefa agendada com este nome
        existing_schedule = Schedule.objects.filter(name=task_name).first()
        
        if existing_schedule:
            self.stdout.write(
                self.style.WARNING(
                    f'Tarefa "{task_name}" já existe. Atualizando...'
                )
            )
            existing_schedule.delete()
        
        # Cria nova tarefa agendada
        # Executa a cada 2 minutos
        Schedule.objects.create(
            func=func,
            name=task_name,
            schedule_type=Schedule.MINUTES,
            minutes=2,
            repeats=-1,  # Repete indefinidamente
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Tarefa "{task_name}" configurada com sucesso!\n'
                f'  A tarefa será executada a cada 2 minutos.\n'
                f'  Para iniciar o scheduler, execute: python manage.py qcluster'
            )
        )

