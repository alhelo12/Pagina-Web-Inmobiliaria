# AGENTS.md

Guía para agentes de IA trabajando en este repo.

## Stack

- **Backend**: FastAPI + SQLAlchemy + Alembic, PostgreSQL, JWT HS256.
- **Frontend**: Vue 3 + Pinia + Vite, axios, WebSocket unificado.
- **PWA**: Workbox + Leaflet Maps.

## Estructura clave

- `backend/app/`: `controllers/` (routers), `services/` (lógica), `models/` (ORM), `schemas/` (Pydantic), `core/` (config, JWT, deps).
- `frontendProyecto/src/`: `views/[role]/` (client/advisor/admin), `components/`, `stores/` (Pinia), `api/` (axios), `composables/` (`useWebSocket.js`).

## Comandos

- Backend: `cd backend && uvicorn app.main:app --reload`, migraciones `alembic upgrade head`.
- Frontend: `cd frontendProyecto && npm run dev`, build `npm run build`.

## Convenciones

- Commits: [Conventional Commits](https://www.conventionalcommits.org/).
- Backend: Ruff para lint/format. Frontend: ESLint + Prettier.
- No subir `.env` ni secretos. Usar `.env-example.txt` / `.env.example` como plantilla.
- Roles: `admin`, `advisor`, `client` — mantener layouts/vistas separadas por rol.
- Enums del sistema: fuente de verdad en backend (`GET /constants`), el frontend los carga vía `utils/enums.js`.
- Real-time: un solo WebSocket en `/ws?token=JWT` gestionado por `useWebSocket.js`.

## Notas

- Ver `README.md` para el detalle completo de endpoints, variables de entorno y estructura.
- `opencode.json` carga el plugin ponytail (modo full por defecto).
