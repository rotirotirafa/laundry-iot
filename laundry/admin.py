from django.contrib import admin
from .models import Maquina, Inquilino, HistoricoUso

@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ip_address', 'status', 'tempo_minutos', 'custo_creditos')
    list_filter = ('status',)
    search_fields = ('nome', 'ip_address')

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
