@echo off
echo Starte FastAPI Inventar-Management auf Windows...
call .\Windows_Venv\Scripts\activate
uvicorn backend.main:app --reload --port 8080
pause