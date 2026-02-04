# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Laundry IoT is a Django 6.0 web application for condominium laundry automation. Tenants log in by apartment number, spend credits to use washing/drying machines, which are controlled remotely via Sonoff smart plugs running Tasmota firmware over HTTP.

## Commands

```bash
# Run with Docker (recommended)
docker-compose up -d

# Run locally (needs PostgreSQL running)
python manage.py runserver          # Django server
python manage.py qcluster           # Background task worker (required for machine auto-release)

# Tests
python manage.py test laundry

# Database
python manage.py migrate
python manage.py setup_scheduler    # Configure django-q periodic tasks
```

## Architecture

### Django Apps
- **`laundry/`** — Single app containing all business logic
- **`laundry_iot/`** — Django project settings and URL dispatcher

### Key Models (`laundry/models.py`)
- **Inquilino** (Tenant): apartment number, hashed password, credit balance
- **Maquina** (Machine): name, Tasmota device IP, status (`Disponível`/`Em Uso`/`Manutenção`), cycle time, credit cost
- **HistoricoUso** (Usage History): tenant→machine link with timestamps and cost

### Machine Usage Flow
1. User clicks "Usar" on dashboard → `usar_maquina_view` validates credits and machine availability
2. `TasmotaService.ligar_com_timer()` sends HTTP GET to `http://{IP}/cm?cmnd=Backlog PulseTime {time};Power On`
3. PulseTime = (minutes × 60) + 100 — ensures hardware-level auto-shutoff
4. Database updated atomically: deduct credits, set status to "Em Uso", create HistoricoUso with `data_hora_fim`

### Machine Release (two mechanisms)
- **Primary**: django-q scheduled task `liberar_maquinas_expiradas` runs every 2 minutes (`laundry/tasks.py`)
- **Fallback**: `home_view` checks and releases expired machines on each dashboard load

### IoT Communication (`laundry/services.py`)
`TasmotaService` — static methods for Tasmota HTTP API: `ligar_com_timer`, `ligar`, `desligar`, `alternar`, `verificar_status_dispositivo`. All use plain HTTP GET with 5-second timeout. No MQTT or authentication.

### Authentication
- Apartment-based login with password hashing via Django's `make_password`/`check_password`
- Backward compatibility: plaintext passwords are auto-hashed on first successful login
- Session timeout: 60 seconds (both server-side via `SESSION_COOKIE_AGE` and client-side JS redirect)

### Admin (`laundry/admin.py`)
Staff users can manually control machines (on/off/toggle) and see real-time Tasmota device status in the admin list view.

## Tech Stack
- Django 6.0, PostgreSQL 15, django-q2 (ORM broker, 1 worker)
- Frontend: server-rendered templates with Bootstrap 5 (no SPA)
- Containerized with Docker Compose (app + postgres services)

## Testing
Tests are in `laundry/tests/` and use `unittest.mock.patch` to mock HTTP requests to Tasmota devices. No external network or devices needed. Three test modules: `test_login.py`, `test_services.py`, `test_usage.py`.

## Language
All code, UI, models, and variable names are in Brazilian Portuguese.
