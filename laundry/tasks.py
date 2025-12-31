"""
Tarefas assíncronas para o sistema de lavanderia.
"""
import logging
from django.utils import timezone
from django.db import transaction
from .models import Maquina, HistoricoUso

logger = logging.getLogger(__name__)


def liberar_maquinas_expiradas():
    """
    Tarefa periódica que verifica e libera máquinas cujo tempo de ciclo expirou.
    
    Esta função é executada automaticamente pelo scheduler do django-q
    a cada 1-2 minutos. Ela busca todas as máquinas com status 'Em Uso'
    e verifica se o tempo de ciclo já expirou baseado no data_hora_fim
    do último HistoricoUso.
    
    Returns:
        dict: Estatísticas da execução (máquinas verificadas, máquinas liberadas)
    """
    maquinas_liberadas = 0
    maquinas_verificadas = 0
    
    try:
        # Busca todas as máquinas em uso
        maquinas_em_uso = Maquina.objects.filter(
            status=Maquina.StatusMaquina.EM_USO
        ).select_for_update()
        
        maquinas_verificadas = maquinas_em_uso.count()
        
        if maquinas_verificadas == 0:
            logger.debug("Nenhuma máquina em uso para verificar")
            return {
                'verificadas': 0,
                'liberadas': 0
            }
        
        agora = timezone.now()
        
        with transaction.atomic():
            for maquina in maquinas_em_uso:
                # Busca o último uso da máquina
                ultimo_uso = HistoricoUso.objects.filter(
                    maquina=maquina
                ).order_by('-data_hora_fim').first()
                
                if ultimo_uso and ultimo_uso.data_hora_fim:
                    # Verifica se o tempo já expirou
                    if ultimo_uso.data_hora_fim <= agora:
                        maquina.status = Maquina.StatusMaquina.DISPONIVEL
                        maquina.save()
                        maquinas_liberadas += 1
                        logger.info(
                            f"Máquina '{maquina.nome}' liberada automaticamente. "
                            f"Tempo expirado em {ultimo_uso.data_hora_fim}"
                        )
        
        logger.info(
            f"Liberação automática concluída: {maquinas_liberadas} de "
            f"{maquinas_verificadas} máquinas liberadas"
        )
        
        return {
            'verificadas': maquinas_verificadas,
            'liberadas': maquinas_liberadas
        }
        
    except Exception as e:
        logger.error(
            f"Erro ao liberar máquinas expiradas: {e}",
            exc_info=True
        )
        return {
            'verificadas': maquinas_verificadas,
            'liberadas': maquinas_liberadas,
            'erro': str(e)
        }

