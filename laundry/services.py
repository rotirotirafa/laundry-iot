import requests
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

class TasmotaService:
    def ligar_com_timer(self, ip_address: str, tempo_minutos: int) -> bool:
        """
        Envia um comando 'Backlog' para ligar o dispositivo usando PulseTime.
        O PulseTime garante desligamento automático mesmo em caso de falha de rede.
        Retorna True se o comando foi aceito pelo dispositivo, False caso contrário.
        """
        if not isinstance(tempo_minutos, int) or tempo_minutos <= 0:
            logger.error(f"Tempo de ciclo inválido fornecido para {ip_address}: {tempo_minutos}")
            return False

        try:
            # PulseTime é calculado como: tempo em segundos + 100 (offset padrão do Tasmota)
            # Exemplo: 60 minutos = 3600s + 100 = 3700
            tempo_segundos = tempo_minutos * 60
            pulse_time_value = tempo_segundos + 100
            comando = f"Backlog PulseTime {pulse_time_value}; Power On"
            url_comando = quote(comando)
            url = f"http://{ip_address}/cm?cmnd={url_comando}"

            logger.info(f"Enviando para {ip_address}: {comando}")
            response = requests.get(url, timeout=5)

            if response.ok:
                logger.info(f"Comando aceito por {ip_address}. Resposta: {response.text}")
                return True
            else:
                logger.error(f"Tasmota em {ip_address} retornou um erro: {response.status_code} {response.text}")
                response.raise_for_status()
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de comunicação ao tentar ligar {ip_address}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado no TasmotaService.ligar_com_timer: {e}")
            return False

    def verificar_status_dispositivo(self, ip_address: str) -> str:
        """
        Verifica o status de energia de um dispositivo Tasmota.
        Retorna: "ON", "OFF" ou "ERRO".
        """
        try:
            url = f"http://{ip_address}/cm?cmnd=Status%200"
            logger.info(f"Verificando status de {ip_address}")
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            power_status = data.get("StatusSTS", {}).get("POWER", "ERRO")
            logger.info(f"Status recebido de {ip_address}: {power_status}")
            return power_status

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao verificar status de {ip_address}: {e}")
            return "ERRO"
        except Exception as e:
            logger.error(f"Erro inesperado no TasmotaService.verificar_status_dispositivo: {e}")
            return "ERRO"
