
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Maquina, Inquilino, HistoricoUso

# --- Mock da função de controle da tomada --- 
# Substitua pela sua implementação real com tinytuya
def ligar_tomada(device_id, ip, local_key):
    """
    Função para ligar a tomada inteligente.
    Esta é uma implementação mock. Você deve substituí-la pela lógica real
    usando a biblioteca tinytuya.
    """
    print(f"[SIMULAÇÃO] Ligando a tomada...\n  Device ID: {device_id}\n  IP: {ip}\n  Local Key: {local_key}")
    # Exemplo com tinytuya (descomente e ajuste conforme necessário):
    # import tinytuya
    # d = tinytuya.OutletDevice(device_id, ip, local_key)
    # d.set_version(3.3) 
    # d.turn_on()
    return True # Retorna True em caso de sucesso

def login_view(request):
    if request.method == 'POST':
        identificador = request.POST.get('identificador')
        try:
            inquilino = Inquilino.objects.get(identificador=identificador)
            return redirect('laundry:home', identificador_inquilino=inquilino.identificador)
        except Inquilino.DoesNotExist:
            return render(request, 'login.html', {'error': 'Inquilino não encontrado.'})
    return render(request, 'login.html')

def home_view(request, identificador_inquilino):
    try:
        inquilino = Inquilino.objects.get(identificador=identificador_inquilino)
        maquinas = Maquina.objects.all().order_by('nome')
        context = {
            'inquilino': inquilino,
            'maquinas': maquinas
        }
        return render(request, 'home.html', context)
    except Inquilino.DoesNotExist:
        # Redireciona para a página de login se o inquilino não for encontrado
        return redirect('laundry:login')

def usar_maquina_view(request, id_maquina, identificador_inquilino):
    maquina = get_object_or_404(Maquina, pk=id_maquina)
    inquilino = get_object_or_404(Inquilino, identificador=identificador_inquilino)

    # Validações
    if inquilino.creditos <= 0:
        return render(request, 'home.html', {
            'inquilino': inquilino,
            'maquinas': Maquina.objects.all().order_by('nome'),
            'error': 'Você não tem créditos suficientes.'
        })
    if maquina.status != Maquina.StatusMaquina.DISPONIVEL:
        return render(request, 'home.html', {
            'inquilino': inquilino,
            'maquinas': Maquina.objects.all().order_by('nome'),
            'error': 'Esta máquina não está disponível no momento.'
        })

    # Ação Principal
    try:
        # Tenta ligar a tomada
        ligar_tomada(maquina.device_id, maquina.ip_tomada, maquina.local_key)

        # Atualiza o estado do sistema
        inquilino.creditos -= 1
        maquina.status = Maquina.StatusMaquina.EM_USO
        
        HistoricoUso.objects.create(inquilino=inquilino, maquina=maquina)

        inquilino.save()
        maquina.save()

        # Prepara o contexto para a página de sucesso
        context = {
            'creditos': inquilino.creditos,
            'identificador_inquilino': inquilino.identificador
        }
        return render(request, 'sucesso.html', context)

    except Exception as e:
        print(f"Erro ao tentar usar a máquina: {e}")
        return render(request, 'home.html', {
            'inquilino': inquilino,
            'maquinas': Maquina.objects.all().order_by('nome'),
            'error': 'Ocorreu um erro ao tentar ligar a máquina. Tente novamente.'
        })
