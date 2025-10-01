
from django.db import models

class Maquina(models.Model):
    class TipoMaquina(models.TextChoices):
        LAVADORA = 'LAVADORA', 'Lavadora'
        SECADORA = 'SECADORA', 'Secadora'

    class StatusMaquina(models.TextChoices):
        DISPONIVEL = 'DISPONIVEL', 'Disponível'
        EM_USO = 'EM_USO', 'Em Uso'
        MANUTENCAO = 'MANUTENCAO', 'Manutenção'

    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TipoMaquina.choices)
    ip_tomada = models.GenericIPAddressField()
    device_id = models.CharField(max_length=100)
    local_key = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=StatusMaquina.choices, default=StatusMaquina.DISPONIVEL)
    tempo_ciclo_minutos = models.PositiveIntegerField(
        default=70,
        help_text="Tempo de duração do ciclo em minutos. Este valor será usado para programar o timer do dispositivo Tasmota."
    )

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

class Inquilino(models.Model):
    identificador = models.CharField(max_length=50, unique=True)
    nome_responsavel = models.CharField(max_length=200, blank=True, null=True)
    creditos = models.IntegerField(default=0)

    def __str__(self):
        return self.identificador

class HistoricoUso(models.Model):
    inquilino = models.ForeignKey(Inquilino, on_delete=models.CASCADE, related_name='usos')
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='historico')
    data_hora_inicio = models.DateTimeField(auto_now_add=True)
    data_hora_fim = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Uso por {self.inquilino} em {self.data_hora_inicio.strftime('%d/%m/%Y %H:%M')}"
