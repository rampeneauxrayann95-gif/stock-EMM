# Stock EMM — Gestion de stock (hébergeable)

- FastAPI + SQLite
- Frontend intégré servi par FastAPI (http://host/)
- Mouvements sécurisés (pas de stock négatif)

## Local
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
→ Ouvre http://localhost:8000

## Render
Repo GitHub → New Web Service
Build: pip install -r requirements.txt
Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
