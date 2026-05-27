# REPOINVENT
<<<<<<< HEAD
Repositorio para inventario de equipamentos de TI
=======

Inventário de equipamentos de TI (SQLite + Python/FastAPI + React/Vite).

## Requisitos

- Python 3.11+
- Node.js 18+

## Backend (API)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8010
```

API: `http://127.0.0.1:8010`

## Backup (SQLite)

Roda um backup do arquivo SQLite em `backend/backups/` e mantém 14 dias:

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.run_backup
```

Agendamento 3x por dia (Windows Task Scheduler): use o script `backend/scripts/backup-3x-dia.ps1` e crie 3 triggers diários (ex.: 08:00, 13:00, 18:00).

## Frontend (Web)

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Web: `http://127.0.0.1:5173`
>>>>>>> e97182e (Initial version)
