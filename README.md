# Media Converter

Aplikacja webowa do transkodowania plików multimedialnych (wideo/audio).

## Stack

- Backend: Django 5 + DRF
- Frontend: React 18 + Vite 5 + Tailwind
- Kolejka: Celery + Redis
- DB: PostgreSQL 16

## Wymagania

- Python 3.11+
- Node 18+
- Docker + Docker Compose

## Konfiguracja

1. Skopiuj `.env.example` do `.env`.
2. Ustaw `SECRET_KEY`, `POSTGRES_PASSWORD`, `INTERNAL_SHARED_TOKEN`.
3. Uruchom `docker compose up`.

## Struktura

- `backend/` - Django REST API
- `worker/` - Usługa obliczeniowa FFmpeg
- `frontend/` - React SPA
- `docs/` - Dokumentacja
- `scripts/` - Skrypty pomocnicze
