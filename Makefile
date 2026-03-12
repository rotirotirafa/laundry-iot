# Laundry IoT — Makefile de operações
# Uso: make <comando> [ip=<IP>] [minutos=<N>]

.DEFAULT_GOAL := ajuda

# ─── SISTEMA ──────────────────────────────────────────────────────────────────

ligar-sistema:
	@echo "Iniciando o sistema..."
	docker-compose up -d
	@echo "Sistema iniciado. Acesse http://localhost:8000"

desligar-sistema:
	@echo "Desligando o sistema..."
	docker-compose down
	@echo "Sistema desligado."

reiniciar-sistema:
	@echo "Reiniciando o sistema..."
	docker-compose restart
	@echo "Sistema reiniciado."

status-sistema:
	@echo "=== Status dos containers ==="
	docker-compose ps
	@echo ""
	@echo "=== Logs recentes ==="
	docker-compose logs --tail=20

logs:
	docker-compose logs -f

# ─── MÁQUINAS (Tasmota via HTTP) ──────────────────────────────────────────────

# Verifica se o ip foi fornecido
_check_ip:
ifndef ip
	$(error Informe o IP da maquina. Ex: make ligar ip=192.168.1.100)
endif

ligar: _check_ip
	@echo "Ligando maquina em $(ip)..."
	@curl -sf "http://$(ip)/cm?cmnd=Power%20On" && echo "OK — maquina ligada." || echo "ERRO — nao foi possivel conectar em $(ip)."

desligar: _check_ip
	@echo "Desligando maquina em $(ip)..."
	@curl -sf "http://$(ip)/cm?cmnd=Power%20Off" && echo "OK — maquina desligada." || echo "ERRO — nao foi possivel conectar em $(ip)."

alternar: _check_ip
	@echo "Alternando estado da maquina em $(ip)..."
	@curl -sf "http://$(ip)/cm?cmnd=Power%20Toggle" && echo "OK — estado alternado." || echo "ERRO — nao foi possivel conectar em $(ip)."

status-maquina: _check_ip
	@echo "=== Status da maquina em $(ip) ==="
	@curl -sf "http://$(ip)/cm?cmnd=Status%200" | python3 -m json.tool 2>/dev/null || echo "ERRO — nao foi possivel conectar em $(ip)."

ligar-com-timer: _check_ip
ifndef minutos
	$(error Informe os minutos. Ex: make ligar-com-timer ip=192.168.1.100 minutos=45)
endif
	@echo "Ligando maquina em $(ip) por $(minutos) minutos..."
	$(eval PULSE=$(shell python3 -c "print($(minutos) * 60 + 100)"))
	@curl -sf "http://$(ip)/cm?cmnd=Backlog%20PulseTime%20$(PULSE)%3B%20Power%20On" && echo "OK — maquina ligada por $(minutos) min." || echo "ERRO — nao foi possivel conectar em $(ip)."

# ─── TESTES ───────────────────────────────────────────────────────────────────

testar:
	docker-compose exec laundry-iot python manage.py test laundry

# ─── AJUDA ────────────────────────────────────────────────────────────────────

ajuda:
	@echo ""
	@echo "Laundry IoT — Comandos disponíveis"
	@echo "======================================"
	@echo ""
	@echo "  SISTEMA"
	@echo "    make ligar-sistema         Inicia todos os containers"
	@echo "    make desligar-sistema      Para todos os containers"
	@echo "    make reiniciar-sistema     Reinicia os containers"
	@echo "    make status-sistema        Mostra status e logs recentes"
	@echo "    make logs                  Acompanha logs em tempo real"
	@echo ""
	@echo "  MÁQUINAS  (requer ip=<IP>)"
	@echo "    make ligar ip=192.168.1.x              Liga a maquina"
	@echo "    make desligar ip=192.168.1.x           Desliga a maquina"
	@echo "    make alternar ip=192.168.1.x           Alterna o estado"
	@echo "    make status-maquina ip=192.168.1.x     Mostra status da maquina"
	@echo "    make ligar-com-timer ip=192.168.1.x minutos=45   Liga por N minutos"
	@echo ""

.PHONY: ligar-sistema desligar-sistema reiniciar-sistema status-sistema logs \
        ligar desligar alternar status-maquina ligar-com-timer \ 
		testar ajuda _check_ip
