Inventar-Management-System 📦

Ein modernes System zur Verwaltung von Lagerbeständen, bestehend aus einem FastAPI-Backend und einer Desktop-Applikation.

🚀 Funktionen

Lagerverwaltung: Artikel hinzufügen, bearbeiten und löschen.

Echtzeit-API: Schnelle Datenverarbeitung durch FastAPI.

Desktop-Interface: Benutzerfreundliche Oberfläche für die tägliche Arbeit.

Datenbank: Lokale Speicherung via SQLite.

🛠 Installation & Setup

Voraussetzungen

Python 3.8+

Git

Lokale Einrichtung

Repository klonen:

git clone [https://github.com/milijandavidovic171-dev/Inventar-Management-System.git](https://github.com/milijandavidovic171-dev/Inventar-Management-System.git)
cd Inventar-Management-System


Abhängigkeiten installieren:

pip install -r requirements.txt


(Hinweis: Falls noch keine requirements.txt vorhanden ist, installiere fastapi, uvicorn und requests manuell).

🖥 Starten der Anwendung

1. Backend (API) starten

Wechsle in den Backend-Ordner und starte den Server:

uvicorn backend.main:app --reload


2. Desktop-App starten

Starte die Hauptanwendung:

python desktop_app/main.py


📝 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.