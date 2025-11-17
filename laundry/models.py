from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Inquilino(models.Model):
    apartamento = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=128, null=True, blank=True) # Hashed password
    creditos = models.IntegerField(default=10)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        if not self.password:
            return False
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"Inquilino do Apto {self.apartamento}"

class Maquina(models.Model):
    class StatusMaquina(models.TextChoices):
        DISPONIVEL = 'Disponível'
        EM_USO = 'Em Uso'
        MANUTENCAO = 'Manutenção'

    nome = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField(unique=True)
    status = models.CharField(
        max_length=20,
        choices=StatusMaquina.choices,
        default=StatusMaquina.DISPONIVEL
    )
    tempo_minutos = models.IntegerField(default=30, help_text="Tempo do ciclo em minutos")
    custo_creditos = models.IntegerField(default=1)

    def __str__(self):
        return self.nome

class HistoricoUso(models.Model):
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE)
    inquilino = models.ForeignKey(Inquilino, on_delete=models.CASCADE)
    data_hora_inicio = models.DateTimeField(auto_now_add=True)
    data_hora_fim = models.DateTimeField(null=True, blank=True)
    custo_creditos = models.IntegerField()

    def __str__(self):
        return f"{self.maquina.nome} - {self.inquilino.apartamento} em {self.data_hora_inicio}"
