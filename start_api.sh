#!/bin/bash

# 1. In das Verzeichnis dieses Skripts wechseln
cd "$(dirname "$0")"

# 2. Die virtuelle Umgebung aktivieren
if [ -f "Debian_Venv/bin/activate" ]; then
    source Debian_Venv/bin/activate
else
    echo "⚠️ Venv 'Debian_Venv' nicht gefunden!"
fi

# 3. In den Backend-Ordner springen
cd backend

# 4. Startbefehl ausführen
echo "⚡ Starte FastAPI auf Port 8080..."
python -m uvicorn main:app --port 8080 --reload
