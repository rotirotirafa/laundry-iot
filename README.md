# Lavanderia IoT

Sistema de automação para lavanderias de condomínios que permite aos inquilinos utilizarem máquinas de lavar e secar através de um sistema de créditos, com controle remoto via tomadas inteligentes Sonoff com firmware Tasmota.

## 🛠️ Tecnologias

- **Backend:** Django 6.0
- **Banco de Dados:** PostgreSQL 15
- **Frontend:** HTML puro com Bootstrap 5
- **Integração IoT:** Tomadas Sonoff com Tasmota (comunicação via HTTP)

## 📋 Pré-requisitos

- Python 3.12+
- Docker e Docker Compose
- pip (gerenciador de pacotes Python)

## 🚀 Instalação e Configuração

### 1. Criar ambiente virtual

```bash
python3 -m venv venv
```

### 2. Ativar o ambiente virtual

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

**Para desenvolvimento local (sem Docker Compose):**

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
DB_NAME=laundry_db
DB_USER=user
DB_PASS=IJmUjBt4
DB_HOST=localhost
DB_PORT=5432
```

**Para Docker Compose:**

Se estiver usando Docker Compose, você pode criar um arquivo `.env` com variáveis opcionais para o superuser:

```env
DJANGO_SUPERUSER_USERNAME=renato
DJANGO_SUPERUSER_PASSWORD=123456
DJANGO_SUPERUSER_EMAIL=renato@example.com
```

Se não fornecer essas variáveis, será criado um superuser padrão:
- Username: `admin`
- Password: `admin123`
- Email: `admin@example.com`

**Nota:** As configurações de banco de dados no Docker Compose já estão definidas no `docker-compose.yml`. O `DB_HOST` dentro do container é `postgres` (nome do serviço).

### 5. Subir o ambiente com Docker Compose

**Opção A: Usando Docker Compose (Recomendado)**

O Docker Compose configura automaticamente todo o ambiente, incluindo:
- Banco de dados PostgreSQL
- Aplicação Django
- Migrações automáticas
- Criação de superuser (se configurado)
- Configuração do scheduler

Para usar com superuser personalizado, crie um arquivo `.env` na raiz do projeto:

```env
DJANGO_SUPERUSER_USERNAME=user
DJANGO_SUPERUSER_PASSWORD=123456
DJANGO_SUPERUSER_EMAIL=user@example.com
```

Depois, suba todos os serviços:

```bash
docker-compose up -d
```

O sistema estará disponível em `http://localhost:8000/`

**O que acontece automaticamente ao subir o Docker Compose:**
- ✅ Aguarda o banco de dados estar pronto
- ✅ Executa todas as migrações do Django
- ✅ Configura as migrações do django-q
- ✅ Configura o scheduler para liberação automática de máquinas
- ✅ Cria o superuser (se as variáveis estiverem definidas)
- ✅ Inicia o servidor Django na porta 8000

**Opção B: Apenas o banco de dados**

Se preferir rodar a aplicação localmente e apenas usar Docker para o banco:

```bash
docker-compose up -d postgres
```

Isso irá iniciar apenas o container PostgreSQL na porta 5432.

### 6. Executar migrações

```bash
python manage.py migrate
```

### 7. Criar superusuário do Django

```bash
python manage.py createsuperuser
```

Siga as instruções para criar um usuário administrador que terá acesso ao painel admin do Django.

### 8. Configurar migrações do django-q

```bash
python manage.py migrate django_q
```

### 9. Configurar o scheduler para liberação automática

```bash
python manage.py setup_scheduler
```

Este comando configura uma tarefa periódica que libera automaticamente as máquinas quando o tempo de ciclo expira.

### 10. Iniciar o qcluster (scheduler)

Em um terminal separado, inicie o qcluster:

```bash
python manage.py qcluster
```

**Importante:** O qcluster deve estar rodando para que a liberação automática funcione. Em produção, configure o qcluster como um serviço (systemd, supervisor, etc.).

### 11. Rodar o servidor de desenvolvimento

Em outro terminal, inicie o servidor:

```bash
python manage.py runserver
```

O sistema estará disponível em `http://127.0.0.1:8000/`

## 📖 Como o Sistema Funciona

### Fluxo Principal

1. **Login:** Inquilinos fazem login usando o número do apartamento e senha
2. **Visualização:** Após o login, o inquilino vê:
   - Seus créditos disponíveis
   - Lista de máquinas (lavadoras/secadoras) disponíveis
   - Status de cada máquina (Disponível, Em Uso, Manutenção)
3. **Uso de Máquina:** Ao clicar em "Usar" uma máquina:
   - O sistema verifica se há créditos suficientes
   - Verifica se a máquina está disponível
   - Envia comando HTTP para a tomada Tasmota ligar a máquina
   - Configura o `PulseTime` no Tasmota para desligamento automático após o tempo do ciclo
   - Debita os créditos do inquilino
   - Marca a máquina como "Em Uso"
   - Registra o uso no histórico
4. **Desligamento Automático:** O Tasmota desliga automaticamente após o tempo configurado, mesmo se houver falha de rede (graças ao recurso `PulseTime`)
5. **Liberação Automática:** O scheduler do django-q verifica periodicamente (a cada 2 minutos) se alguma máquina em uso já completou seu ciclo e a libera automaticamente no sistema

### Componentes Principais

- **Inquilinos:** Moradores do condomínio que possuem créditos para usar as máquinas
- **Máquinas:** Lavadoras e secadoras cadastradas no sistema, cada uma com:
  - IP da tomada Tasmota
  - Tempo de ciclo (em minutos)
  - Custo em créditos
  - Status atual
- **Histórico de Uso:** Registro de todos os usos das máquinas pelos inquilinos

### Integração com Tasmota

O sistema se comunica com as tomadas Sonoff/Tasmota via requisições HTTP GET:

- **Ligar máquina:** `GET http://{ip}/cm?cmnd=Backlog%20PulseTime%20{tempo};Power%20On`
- **Verificar status:** `GET http://{ip}/cm?cmnd=Power`

O `PulseTime` é calculado como: `(tempo_em_minutos * 60) + 100` segundos. Isso garante que a máquina desligue automaticamente mesmo em caso de falha de rede.

### Liberação Automática de Máquinas

O sistema possui um scheduler automático que verifica e libera máquinas quando o tempo de ciclo expira:

- **Frequência:** A tarefa é executada a cada 2 minutos pelo django-q
- **Funcionamento:** O scheduler verifica todas as máquinas com status "Em Uso" e compara o `data_hora_fim` do último uso com o horário atual
- **Liberação:** Quando o tempo expira, a máquina é automaticamente marcada como "Disponível" no sistema
- **Fallback:** A view `home_view` também verifica e libera máquinas como medida de segurança caso o scheduler não esteja rodando

**Importante:** Para que a liberação automática funcione, o qcluster deve estar rodando. Sem ele, as máquinas só serão liberadas quando alguém acessar a página home.

## 🔧 Comandos Úteis

### Parar o banco de dados
```bash
docker-compose down
```

### Ver logs do banco de dados
```bash
docker-compose logs postgres
```

### Acessar o painel admin do Django
Acesse `http://127.0.0.1:8000/admin/` e faça login com o superusuário criado.

### Criar dados de teste
Use o painel admin do Django para:
- Criar inquilinos (apartamentos)
- Cadastrar máquinas com seus IPs
- Atribuir créditos aos inquilinos

### Gerenciar o Scheduler

**Verificar tarefas agendadas:**
```bash
python manage.py shell
>>> from django_q.models import Schedule
>>> Schedule.objects.all()
```

**Reconfigurar o scheduler:**
```bash
python manage.py setup_scheduler
```

**Parar o qcluster:**
Pressione `Ctrl+C` no terminal onde o qcluster está rodando, ou envie um sinal de término ao processo.

**Em produção:**
Configure o qcluster como serviço usando systemd ou supervisor para garantir que ele sempre esteja rodando.

## 📝 Estrutura do Projeto

```
laundry-iot/
├── laundry/              # App principal
│   ├── models.py         # Modelos: Inquilino, Maquina, HistoricoUso
│   ├── views.py          # Views: login, home, usar_maquina, logout
│   ├── services.py       # TasmotaService - comunicação com tomadas
│   ├── templates/        # Templates HTML
│   └── migrations/       # Migrações do banco de dados
├── laundry_iot/          # Configurações do projeto Django
│   ├── settings.py       # Configurações
│   └── urls.py           # URLs principais
├── docker-compose.yml    # Configuração do PostgreSQL
├── requirements.txt      # Dependências Python
└── manage.py            # Script de gerenciamento Django
```

## 🔒 Segurança

- Senhas dos inquilinos são armazenadas com hash (usando Django password hashers)
- Primeiro acesso permite definir senha
- Sessões gerenciadas pelo Django
- Timeout de 5 segundos nas requisições HTTP para evitar travamentos

## 🐛 Troubleshooting

**Erro de conexão com o banco:**
- Verifique se o container PostgreSQL está rodando: `docker-compose ps`
- Confirme as variáveis de ambiente no arquivo `.env`

**Máquina não liga:**
- Verifique se o IP da máquina está correto no banco de dados
- Teste se a tomada Tasmota está acessível na rede local
- Verifique os logs do Django para erros de comunicação

**Máquinas não aparecem:**
- Certifique-se de que há máquinas cadastradas no banco de dados
- Use o painel admin para verificar/criar máquinas

