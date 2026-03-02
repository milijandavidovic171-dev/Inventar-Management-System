from typing import List, Optional
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, SQLModel, Field, create_engine
from contextlib import asynccontextmanager

# --- DATENBANK KONFIGURATION ---
db_path = "/home/milijandavidovic/Schreibtisch/Inventar-Management-System/backend/db.sqlite3"
sqlite_url = f"sqlite:///{db_path}"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})



# --- DATENMODELL (SQLModel) ---
class Artikel(SQLModel, table=True):
    # Wir nutzen "artikel", da dies in deiner Binärdatei sichtbar war
    __tablename__ = "artikel"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    menge: int
    standort: Optional[str] = None
    artikelnummer: str = Field(unique=True, index=True)

    # Zeitstempel mit Standardwerten, damit die Datenbank nicht meckert
    erstellt_am: datetime = Field(default_factory=datetime.now)
    aktualisiert_am: datetime = Field(default_factory=datetime.now)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 FastAPI aktiv. Datenbank-Pfad: {db_path}")
    yield

app = FastAPI(lifespan=lifespan, title="Inventar Web-App API")

# --- CORS KONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_session():
    with Session(engine) as session:
        yield session

# --- API ENDPUNKTE ---

@app.get("/api/health")
def health_check():
    return {"status": "online"}

@app.get("/api/artikel", response_model=List[Artikel])
def get_all_items(session: Session = Depends(get_session)):
    try:
        return session.exec(select(Artikel).order_by(Artikel.id.desc())).all()
    except Exception as e:
        print(f"Datenbankfehler: {e}")
        # Falls die Tabelle doch "inventar_app_artikel" heißt, gibt dies einen Hinweis im Terminal
        raise HTTPException(status_code=500, detail="Tabellenstruktur nicht gefunden.")

@app.post("/api/artikel", response_model=Artikel)
def create_item(artikel: Artikel, session: Session = Depends(get_session)):
    try:
        artikel.erstellt_am = datetime.now()
        artikel.aktualisiert_am = datetime.now()
        session.add(artikel)
        session.commit()
        session.refresh(artikel)
        return artikel
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Fehler: {str(e)}")

@app.delete("/api/artikel/{item_id}")
def delete_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Artikel, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    session.delete(item)
    session.commit()
    return {"ok": True}

@app.patch("/api/artikel/{item_id}/menge")
def update_menge(item_id: int, diff: int, session: Session = Depends(get_session)):
    item = session.get(Artikel, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    item.menge = max(0, item.menge + diff)
    item.aktualisiert_am = datetime.now()
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)