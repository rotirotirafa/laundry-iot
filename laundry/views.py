from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Maquina, Inquilino, HistoricoUso
from django.utils import timezone
from datetime import timedelta
from .services import TasmotaService
from django.db import transaction # Importa o módulo de transação
from django.contrib import messages # Para mensagens de erro mais elegantes

def landing_page_view(request):
    """
    Renderiza a página de aterrissagem principal da aplicação.
    """
    return render(request, 'landing.html')

def login_view(request):
    if request.method == 'POST':
        identificador = request.POST.get('identificador')
        try:
            inquilino = Inquilino.objects.get(identificador=identificador)
            # Redireciona para a home, passando o identificador na URL
            return redirect('laundry:home', identificador_inquilino=inquilino.identificador)
        except Inquilino.DoesNotExist:
            return render(request, 'login.html', {'error': 'Inquilino não encontrado.'})
    return render(request, 'login.html')

def home_view(request, identificador_inquilino):
    # --- Lógica de Verificação de Máquinas Expiradas (Fail-safe) ---
    # Esta lógica é uma segurança extra caso o Tasmota falhe em desligar.
    now = timezone.now()
    usos_expirados = HistoricoUso.objects.filter(
        maquina__status=Maquina.StatusMaquina.EM_USO,
        data_hora_fim__lte=now
    )
    for uso in usos_expirados:
        maquina = uso.maquina
        maquina.status = Maquina.StatusMaquina.DISPONIVEL
        maquina.save()

    # --- Renderização da Página ---
    inquilino = get_object_or_404(Inquilino, identificador=identificador_inquilino)
    maquinas = Maquina.objects.all().order_by('nome')
    context = {
        'inquilino': inquilino,
        'maquinas': maquinas,
    }
    return render(request, 'home.html', context)

def usar_maquina_view(request, identificador_inquilino, id_maquina):
    inquilino = get_object_or_404(Inquilino, identificador=identificador_inquilino)

    # Validação inicial de créditos, ANTES de qualquer outra coisa.
    if inquilino.creditos <= 0:
        messages.error(request, "Você não tem créditos suficientes para usar a máquina.")
        return redirect('laundry:home', identificador_inquilino=identificador_inquilino)

    try:
        # Inicia uma transação atômica para garantir a consistência dos dados.
        with transaction.atomic():
            # Busca e bloqueia a linha da máquina no banco de dados.
            # Nenhuma outra requisição pode modificar esta máquina até a transação terminar.
            maquina = Maquina.objects.select_for_update().get(pk=id_maquina)

            # Validação CRÍTICA do status da máquina DENTRO da transação
            if maquina.status != Maquina.StatusMaquina.DISPONIVEL:
                messages.error(request, "Esta máquina não está mais disponível. Outra pessoa pode ter iniciado o uso.")
                return redirect('laundry:home', identificador_inquilino=identificador_inquilino)

            # Camada extra de segurança: Verificação do status real no dispositivo
            tasmota_service = TasmotaService()
            status_real = tasmota_service.verificar_status_dispositivo(maquina.ip_tomada)

            if status_real == "ON":
                # Se o dispositivo já está ligado, algo está fora de sincronia.
                # Força a atualização do nosso banco de dados para refletir a realidade e avisa o usuário.
                maquina.status = Maquina.StatusMaquina.EM_USO
                maquina.save() # Salva a sincronização
                messages.warning(request, "A máquina já se encontrava em uso. O status no painel foi corrigido.")
                return redirect('laundry:home', identificador_inquilino=identificador_inquilino)
            
            if status_real == "ERRO":
                messages.error(request, "Falha de comunicação com a máquina. Não foi possível verificar o status atual.")
                return redirect('laundry:home', identificador_inquilino=identificador_inquilino)

            # Se chegamos aqui, a máquina está DISPONÍVEL no DB e DESLIGADA no mundo real.
            # Agora podemos prosseguir com a ativação.

            # Ação Principal: Envia o comando para o dispositivo
            sucesso_comunicacao = tasmota_service.ligar_com_timer(
                ip_address=maquina.ip_tomada,
                tempo_minutos=maquina.tempo_ciclo_minutos
            )

            if not sucesso_comunicacao:
                messages.error(request, "Falha de comunicação ao tentar ligar a máquina. Tente novamente.")
                # A transação será revertida, nenhuma mudança no DB será feita.
                return redirect('laundry:home', identificador_inquilino=identificador_inquilino)

            # --- SUCESSO! ATUALIZA O ESTADO DO SISTEMA ---

            # 1. Debita o crédito do inquilino
            inquilino.creditos -= 1
            inquilino.save() # Salva a mudança de créditos

            # 2. Altera o status da máquina para "Em Uso"
            maquina.status = Maquina.StatusMaquina.EM_USO
            maquina.save() # <<-- CORREÇÃO CRÍTICA PARA PERSISTIR O ESTADO

            # 3. Cria um registro do uso
            hora_fim = timezone.now() + timedelta(minutes=maquina.tempo_ciclo_minutos)
            HistoricoUso.objects.create(
                inquilino=inquilino, 
                maquina=maquina,
                data_hora_fim=hora_fim
            )

            # Se tudo deu certo, a transação é concluída (commit) automaticamente ao sair do 'with'.

    except Maquina.DoesNotExist:
        messages.error(request, "Máquina não encontrada.")
        return redirect('laundry:home', identificador_inquilino=identificador_inquilino)

    # Redireciona para a página de sucesso se a transação foi bem-sucedida
    return redirect('laundry:sucesso', identificador_inquilino=inquilino.identificador)


def sucesso_view(request, identificador_inquilino):
    inquilino = get_object_or_404(Inquilino, identificador=identificador_inquilino)
    context = {
        'creditos': inquilino.creditos,
        'identificador_inquilino': inquilino.identificador
    }
    return render(request, 'sucesso.html', context)
