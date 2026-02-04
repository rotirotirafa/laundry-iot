from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Maquina, Inquilino, HistoricoUso
from .services import TasmotaService

@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ip_address', 'status', 'status_sonoff', 'acoes_maquina')
    list_filter = ('status',)
    search_fields = ('nome', 'ip_address')
    readonly_fields = ('status_sonoff',)

    def status_sonoff(self, obj):
        """
        Verifica o status de energia (ON/OFF) do dispositivo Sonoff.
        Retorna 'ON', 'OFF', ou 'Indisponível' com tratamento de erro.
        """
        try:
            # Timeout de 2 segundos para não travar o Admin em caso de dispositivo offline
            status = TasmotaService().verificar_status_dispositivo(obj.ip_address, timeout=2)
            # Acessa a chave 'POWER' do dicionário retornado. Em caso de falha, retorna 'Desconhecido'
            return status.get('POWER', 'Desconhecido')
        except Exception:
            # Se ocorrer qualquer exceção na comunicação, retorna 'Indisponível'
            return "Indisponível"
    status_sonoff.short_description = 'Status Sonoff'

    def acoes_maquina(self, obj):
        """
        Cria botões de ação para ligar, desligar e alternar o estado da máquina.
        """
        # Cria as URLs para cada ação, usando o 'reverse' para garantir que as URLs sejam sempre corretas
        url_ligar = reverse('laundry:controle_maquina', args=[obj.pk, 'ligar'])
        url_desligar = reverse('laundry:controle_maquina', args=[obj.pk, 'desligar'])
        url_alternar = reverse('laundry:controle_maquina', args=[obj.pk, 'alternar'])
        
        # Formata o HTML para exibir os botões na listagem do admin
        return format_html(
            '<a class="button" href="{}">Ligar</a>&nbsp;'
            '<a class="button" href="{}">Desligar</a>&nbsp;'
            '<a class="button" href="{}">Alternar</a>',
            url_ligar,
            url_desligar,
            url_alternar,
        )
    acoes_maquina.short_description = 'Ações Manuais'
    acoes_maquina.allow_tags = True


@admin.register(Inquilino)
class InquilinoAdmin(admin.ModelAdmin):
    list_display = ('apartamento', 'creditos')
    search_fields = ('apartamento',)
    list_editable = ('creditos',)

@admin.register(HistoricoUso)
class HistoricoUsoAdmin(admin.ModelAdmin):
    list_display = ('inquilino', 'maquina', 'data_hora_inicio', 'data_hora_fim', 'custo_creditos')
    list_filter = ('maquina', 'inquilino', 'data_hora_inicio')
    search_fields = ('inquilino__apartamento', 'maquina__nome')
    readonly_fields = ('data_hora_inicio', 'data_hora_fim')