
from django.contrib import admin
from .models import Maquina, Inquilino, HistoricoUso

@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'ip_tomada', 'status')
    list_filter = ('tipo', 'status')
    search_fields = ('nome', 'ip_tomada', 'device_id')

@admin.register(Inquilino)
class InquilinoAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'nome_responsavel', 'creditos')
    search_fields = ('identificador', 'nome_responsavel')
    list_editable = ('creditos',)

@admin.register(HistoricoUso)
class HistoricoUsoAdmin(admin.ModelAdmin):
    list_display = ('inquilino', 'maquina', 'data_hora')
    list_filter = ('maquina', 'inquilino', 'data_hora')
    search_fields = ('inquilino__identificador', 'maquina__nome')
    readonly_fields = ('data_hora',)
