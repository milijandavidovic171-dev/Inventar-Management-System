import sqlite3

def crate_database():

    """
    Erstellt die SQLite-Datenbank und die Tabelle 'Artikel'.
    """
    conn = None

    try:
        conn = sqlite3.connect('inventar.db')
        cursor = conn.cursor()

        create_table_sql =  """
        CREATE TABLE IF NOT EXISTS artikel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            menge INTEGER NOT NULL,
            standort TEXT,
            artikelnummer TEXT UNIQUE NOT NULL
        );
        """

        cursor.execute(create_table_sql)
        print("Datenbank und Tabelle 'Artikel' erfolgreich erstellt.")

    except sqlite3.Error as e:
        print(f"Fehler bei der Datenbankoperationen: {e}")

    finally:
        if conn:
            conn.close()
            print("Datenbankverbindung geschlossen")

if __name__ == "__main__":
    crate_database()