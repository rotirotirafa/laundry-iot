from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Inquilino, Maquina, HistoricoUso
from .services import TasmotaService
from django.contrib.auth.hashers import identify_hasher

def landing_page_view(request):
    return render(request, 'landing.html')

def login_view(request):
    if request.method == 'POST':
        apto = request.POST.get('apartamento')
        raw_password = request.POST.get('password')

        if not apto or not raw_password:
            messages.error(request, 'Apartamento e senha são obrigatórios.')
            return redirect('laundry:login')

        try:
            inquilino = Inquilino.objects.get(apartamento=apto)
            # If no password stored, set one (first access)
            if not inquilino.password:
                inquilino.set_password(raw_password)
                inquilino.save()
                messages.success(request, 'Sua nova senha foi definida com sucesso!')
                request.session['inquilino_id'] = inquilino.id
                return redirect('laundry:home')

            # If stored password is a proper hashed value, use check_password
            if inquilino.check_password(raw_password):
                request.session['inquilino_id'] = inquilino.id
                return redirect('laundry:home')

            # If stored value is not a recognized hashed password (maybe raw/plaintext),
            # accept it if it matches the provided raw password and then hash it for future logins.
            hashed_ok = True
            try:
                identify_hasher(inquilino.password)
            except Exception:
                hashed_ok = False

            if not hashed_ok and inquilino.password == raw_password:
                inquilino.set_password(raw_password)
                inquilino.save()
                messages.success(request, 'Senha atualizada automaticamente. Agora você está logado.')
                request.session['inquilino_id'] = inquilino.id
                return redirect('laundry:home')

            messages.error(request, 'Apartamento ou senha inválidos.')
            return redirect('laundry:login')

        except Inquilino.DoesNotExist:
            messages.error(request, 'Apartamento não encontrado.')
            return redirect('laundry:login')

    return render(request, 'login.html')

def home_view(request):
    inquilino_id = request.session.get('inquilino_id')
    if not inquilino_id:
        return redirect('laundry:login')
    
    maquinas_list = Maquina.objects.all().order_by('nome')
    for maquina in maquinas_list:
        if maquina.status == Maquina.StatusMaquina.EM_USO:
            ultimo_uso = maquina.historicouso_set.order_by('-data_hora_fim').first()
            if ultimo_uso and ultimo_uso.data_hora_fim <= timezone.now():
                maquina.status = Maquina.StatusMaquina.DISPONIVEL
                maquina.save()

    context = {
        'inquilino': get_object_or_404(Inquilino, pk=inquilino_id),
        'maquinas': maquinas_list,
        'creditos_disponiveis': max(0, get_object_or_404(Inquilino, pk=inquilino_id).creditos),
    }
    return render(request, 'home.html', context)

def usar_maquina_view(request, maquina_id):
    inquilino_id = request.session.get('inquilino_id')
    if not inquilino_id:
        return redirect('laundry:login')

    tasmota_service = TasmotaService()

    try:
        with transaction.atomic():
            maquina = Maquina.objects.select_for_update().get(pk=maquina_id)
            inquilino = Inquilino.objects.select_for_update().get(pk=inquilino_id)

            if maquina.status == Maquina.StatusMaquina.EM_USO:
                ultimo_uso = maquina.historicouso_set.order_by('-data_hora_fim').first()
                if ultimo_uso and ultimo_uso.data_hora_fim <= timezone.now():
                    maquina.status = Maquina.StatusMaquina.DISPONIVEL

            if maquina.status != Maquina.StatusMaquina.DISPONIVEL:
                messages.error(request, 'Máquina não está disponível.')
                return redirect('laundry:home')

            if inquilino.creditos < maquina.custo_creditos:
                messages.error(request, 'Créditos insuficientes.')
                return redirect('laundry:home')
            
            tempo_ciclo = maquina.tempo_minutos
            if not tempo_ciclo or tempo_ciclo <= 0:
                messages.error(request, f"Erro crítico: A máquina '{maquina.nome}' está configurada com tempo de ciclo inválido. Contate o suporte.")
                return redirect('laundry:home')

            sucesso_tasmota = tasmota_service.ligar_com_timer(maquina.ip_address, tempo_ciclo)

            if not sucesso_tasmota:
                messages.error(request, f"Falha na comunicação com a máquina '{maquina.nome}'. Tente novamente.")
                return redirect('laundry:home')

            inquilino.creditos -= maquina.custo_creditos
            inquilino.save()

            maquina.status = Maquina.StatusMaquina.EM_USO
            maquina.save()

            data_hora_fim = timezone.now() + timedelta(minutes=tempo_ciclo)
            HistoricoUso.objects.create(
                maquina=maquina,
                inquilino=inquilino,
                data_hora_fim=data_hora_fim,
                custo_creditos=maquina.custo_creditos
            )

            messages.success(request, f"Máquina '{maquina.nome}' iniciada com sucesso!")
            return redirect('laundry:sucesso')

    except Maquina.DoesNotExist:
        messages.error(request, "Máquina não encontrada.")
        return redirect('laundry:home')
    except Inquilino.DoesNotExist:
        messages.error(request, "Inquilino não encontrado.")
        return redirect('laundry:login')
    except Exception as e:
        messages.error(request, f"Ocorreu um erro inesperado: {e}")
        return redirect('laundry:home')

def sucesso_view(request):
    inquilino_id = request.session.get('inquilino_id')
    if not inquilino_id:
        return redirect('laundry:login')
    
    inquilino = get_object_or_404(Inquilino, pk=inquilino_id)
    context = {
        'inquilino': inquilino,
        'creditos': inquilino.creditos,
    }
    return render(request, 'sucesso.html', context)

def logout_view(request):
    """Realiza logout do usuário, limpando a sessão e redirecionando para a landing page."""
    request.session.flush()
    messages.success(request, 'Você saiu com sucesso!')
    return redirect('laundry:landing_page')
