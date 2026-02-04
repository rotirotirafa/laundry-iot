
import requests
from unittest.mock import patch, Mock
from django.test import TestCase
from urllib.parse import quote

from ..services import TasmotaService

class TasmotaServiceTest(TestCase):
    """
    Suíte de testes para o TasmotaService.
    Estes testes usam 'unittest.mock.patch' para simular as requisições HTTP,
    isolando o serviço da necessidade de uma rede ou dispositivo real.
    """

    def setUp(self):
        """Configura uma instância do serviço para ser usada em cada teste."""
        self.service = TasmotaService()
        self.ip_address = "192.168.1.100"

    @patch('laundry.services.requests.get')
    def test_ligar_com_timer_sucesso(self, mock_get):
        """
        Testa o caminho feliz: a comunicação é bem-sucedida e o dispositivo
        retorna a resposta esperada usando PulseTime.
        """
        # Configuração do Mock para simular uma resposta HTTP bem-sucedida
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '{"POWER":"ON"}'
        mock_get.return_value = mock_response

        # Execução
        tempo_minutos = 70
        resultado = self.service.ligar_com_timer(self.ip_address, tempo_minutos)

        # Verificações
        self.assertTrue(resultado)
        mock_get.assert_called_once()
        # PulseTime = (tempo_minutos * 60) + 100
        tempo_segundos = tempo_minutos * 60
        pulse_time_value = tempo_segundos + 100
        comando = f"Backlog PulseTime {pulse_time_value}; Power On"
        url_esperada = f"http://{self.ip_address}/cm?cmnd={quote(comando)}"
        self.assertEqual(mock_get.call_args[0][0], url_esperada)
        # Verificar que o timeout é 5 segundos
        self.assertEqual(mock_get.call_args[1]['timeout'], 5)

    @patch('laundry.services.requests.get')
    def test_ligar_com_timer_falha_de_rede(self, mock_get):
        """
        Testa o cenário de falha de rede (timeout).
        """
        # Configuração do Mock para simular uma exceção de rede
        mock_get.side_effect = requests.exceptions.Timeout("Simulando timeout")

        # Execução
        resultado = self.service.ligar_com_timer(self.ip_address, 70)

        # Verificação
        self.assertFalse(resultado)

    # --- Testes para verificar_status_dispositivo ---

    @patch('laundry.services.requests.get')
    def test_verificar_status_dispositivo_on(self, mock_get):
        """
        Testa a verificação de status quando o dispositivo está ON.
        """
        # Configuração do Mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"StatusSTS": {"POWER": "ON"}}
        mock_get.return_value = mock_response

        # Execução
        status = self.service.verificar_status_dispositivo(self.ip_address)

        # Verificações
        self.assertEqual(status, "ON")
        url_esperada = f"http://{self.ip_address}/cm"
        mock_get.assert_called_once_with(url_esperada, params={'cmnd': 'Status 0'}, timeout=5)

    @patch('laundry.services.requests.get')
    def test_verificar_status_dispositivo_off(self, mock_get):
        """
        Testa a verificação de status quando o dispositivo está OFF.
        """
        # Configuração do Mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"StatusSTS": {"POWER": "OFF"}}
        mock_get.return_value = mock_response

        # Execução
        status = self.service.verificar_status_dispositivo(self.ip_address)

        # Verificação
        self.assertEqual(status, "OFF")

    @patch('laundry.services.requests.get')
    def test_verificar_status_dispositivo_falha_comunicacao(self, mock_get):
        """
        Testa a verificação de status em caso de falha de rede.
        """
        # Configuração do Mock
        mock_get.side_effect = requests.exceptions.RequestException("Erro de rede")

        # Execução
        status = self.service.verificar_status_dispositivo(self.ip_address)

        # Verificação
        self.assertEqual(status, "ERRO")

    @patch('laundry.services.requests.get')
    def test_verificar_status_dispositivo_resposta_inesperada(self, mock_get):
        """
        Testa a verificação de status quando a resposta do dispositivo é inesperada.
        """
        # Configuração do Mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"StatusFoo": {"BAR": "BAZ"}} # Estrutura inválida
        mock_get.return_value = mock_response

        # Execução
        status = self.service.verificar_status_dispositivo(self.ip_address)

        # Verificação
        self.assertEqual(status, "ERRO")

    # --- Testes para ligar ---

    @patch('laundry.services.requests.get')
    def test_ligar_sucesso(self, mock_get):
        """
        Testa o ligar com sucesso.
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '{"POWER":"ON"}'
        mock_get.return_value = mock_response

        resultado = self.service.ligar(self.ip_address)

        self.assertTrue(resultado)
        comando = "Power On"
        url_esperada = f"http://{self.ip_address}/cm?cmnd={quote(comando)}"
        mock_get.assert_called_once_with(url_esperada, timeout=5)

    @patch('laundry.services.requests.get')
    def test_ligar_falha_rede(self, mock_get):
        """
        Testa o ligar com falha de rede.
        """
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        resultado = self.service.ligar(self.ip_address)

        self.assertFalse(resultado)

    # --- Testes para desligar ---

    @patch('laundry.services.requests.get')
    def test_desligar_sucesso(self, mock_get):
        """
        Testa o desligar com sucesso.
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '{"POWER":"OFF"}'
        mock_get.return_value = mock_response

        resultado = self.service.desligar(self.ip_address)

        self.assertTrue(resultado)
        comando = "Power Off"
        url_esperada = f"http://{self.ip_address}/cm?cmnd={quote(comando)}"
        mock_get.assert_called_once_with(url_esperada, timeout=5)

    @patch('laundry.services.requests.get')
    def test_desligar_falha_rede(self, mock_get):
        """
        Testa o desligar com falha de rede.
        """
        mock_get.side_effect = requests.exceptions.RequestException("Erro")

        resultado = self.service.desligar(self.ip_address)

        self.assertFalse(resultado)
