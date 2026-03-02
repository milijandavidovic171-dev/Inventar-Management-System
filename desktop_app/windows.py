import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox


class BaseFrame(ttk.Frame):
    def __init__(self, master, app_instance, title, **kwargs):
        super().__init__(master)
        self.app = app_instance
        self.title_label = ttk.Label(self, text=title, font=("Arial", 16, "bold"))
        # Hier nutzen wir pack, weil es nur der Titelcontainer ist, der Rest nutzt grid
        self.title_label.pack(pady=10)


class WareneingangWindow(BaseFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, app_instance, "Wareneingang", **kwargs)
        self.connect_db = self.app.connect_db

        # Haupt-Container
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        self.main_frame.columnconfigure(1, weight=1)

        # Titel im Grid
        ttk.Label(self.main_frame, text="Wareneingang erfassen", font=("Arial", 14, "bold")).grid(row=0, column=0,
                                                                                                  columnspan=2, pady=10)

        # Inputs
        ttk.Label(self.main_frame, text="Artikelnummer oder Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.artikel_input = ttk.Entry(self.main_frame, width=40)
        self.artikel_input.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(self.main_frame, text="Menge hinzufügen:").grid(row=2, column=0, sticky="w", pady=5)
        self.menge_input = ttk.Entry(self.main_frame, width=40)
        self.menge_input.grid(row=2, column=1, sticky="ew", pady=5, padx=5)

        # Status
        self.status_label = ttk.Label(self.main_frame, text="", foreground="green")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=10)

        # Button
        ttk.Button(self.main_frame, text="Buchen", command=self.process_wareneingang).grid(row=4, column=0,
                                                                                           columnspan=2, ipady=10,
                                                                                           sticky="ew")

    def process_wareneingang(self):
        artikel_id = self.artikel_input.get().strip()
        menge_str = self.menge_input.get().strip()

        if not artikel_id or not menge_str:
            self.status_label.config(text="Bitte Artikelnummer/Name und Menge eingeben.", foreground="red")
            return

        try:
            menge = int(menge_str)
            if menge <= 0:
                self.status_label.config(text="Menge muss größer als 0 sein.", foreground="red")
                return
        except ValueError:
            self.status_label.config(text="Menge muss eine gültige Zahl sein.", foreground="red")
            return

        conn = self.connect_db()
        if conn is None: return
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT menge FROM artikel WHERE artikelnummer = ? OR name = ?", (artikel_id, artikel_id))
            result = cursor.fetchone()

            if result:
                aktuelle_menge = result[0]
                neue_menge = aktuelle_menge + menge
                cursor.execute("UPDATE artikel SET menge = ? WHERE artikelnummer = ? OR name = ?",
                               (neue_menge, artikel_id, artikel_id))
                conn.commit()
                self.status_label.config(text=f"Erfolg: {menge} Stück hinzugefügt. Neuer Bestand: {neue_menge}",
                                         foreground="green")
                self.clear_fields()
            else:
                self.status_label.config(text=f"Artikel '{artikel_id}' nicht gefunden.", foreground="red")
                messagebox.showwarning("Fehler", f"Artikel '{artikel_id}' nicht gefunden.")

        except sqlite3.Error as e:
            self.status_label.config(text=f"Datenbankfehler: {e}", foreground="red")
        finally:
            conn.close()

    def clear_fields(self):
        self.artikel_input.delete(0, tk.END)
        self.menge_input.delete(0, tk.END)


class InventoryWindow(BaseFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, app_instance, "Artikelverwaltung", **kwargs)
        self.connect_db = self.app.connect_db

        # Variablen
        self.entry_name_var = tk.StringVar()
        self.entry_menge_var = tk.StringVar()
        self.entry_standort_var = tk.StringVar()
        self.entry_artikelnummer_var = tk.StringVar()
        self.search_term = tk.StringVar()

        # Haupt-Container für Grid
        self.content_frame = ttk.Frame(self, padding="10")
        self.content_frame.pack(fill="both", expand=True)

        # Grid Konfiguration
        self.content_frame.columnconfigure(1, weight=1)  # Eingabefelder sollen wachsen
        self.content_frame.rowconfigure(7, weight=1)  # Tabelle soll wachsen

        # --- Zeile 0: Suche ---
        search_frame = ttk.Frame(self.content_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))

        ttk.Label(search_frame, text="Suche: ").pack(side="left")
        search_entry = ttk.Entry(search_frame, textvariable=self.search_term, width=30)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        search_entry.bind("<Return>", lambda e: self.search_artikel())
        search_entry.bind("<KeyRelease>", lambda e: self.search_artikel())  # Live Suche

        ttk.Button(search_frame, text="Reset", command=self.reset_search).pack(side="left")

        # --- Zeile 1-4: Eingabefelder (Original Grid Layout) ---
        ttk.Label(self.content_frame, text="Artikelname:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(self.content_frame, textvariable=self.entry_name_var, width=40).grid(row=1, column=1, sticky="ew",
                                                                                       pady=5)

        ttk.Label(self.content_frame, text="Menge:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(self.content_frame, textvariable=self.entry_menge_var, width=40).grid(row=2, column=1, sticky="ew",
                                                                                        pady=5)

        ttk.Label(self.content_frame, text="Standort:").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(self.content_frame, textvariable=self.entry_standort_var, width=40).grid(row=3, column=1, sticky="ew",
                                                                                           pady=5)

        ttk.Label(self.content_frame, text="Artikelnummer:").grid(row=4, column=0, sticky="w", pady=5)
        ttk.Entry(self.content_frame, textvariable=self.entry_artikelnummer_var, width=40).grid(row=4, column=1,
                                                                                                sticky="ew", pady=5)

        # --- Zeile 5: Buttons ---
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Button(btn_frame, text="Hinzufügen", command=self.add_artikel).pack(side="left", fill="x", expand=True,
                                                                                padx=2)
        ttk.Button(btn_frame, text="Löschen", command=self.delete_artikel).pack(side="left", fill="x", expand=True,
                                                                                padx=2)
        ttk.Button(btn_frame, text="Felder leeren", command=self.clear_entries).pack(side="left", fill="x", expand=True,
                                                                                     padx=2)

        # --- Zeile 6: Status ---
        self.status_label = ttk.Label(self.content_frame, text="", foreground="green")
        self.status_label.grid(row=6, column=0, columnspan=2, pady=5)

        # --- Zeile 7: Tabelle ---
        self.create_inventory_table()  # Erstellt self.tree

        # Daten initial laden
        self.load_artikel_data()

    def add_artikel(self):
        name = self.entry_name_var.get()
        menge_str = self.entry_menge_var.get()
        standort = self.entry_standort_var.get()
        artikelnummer = self.entry_artikelnummer_var.get()

        if not name or not menge_str or not artikelnummer:
            messagebox.showwarning("Fehler", "Name, Menge und Nummer sind Pflichtfelder.")
            return
        try:
            menge = int(menge_str)
        except ValueError:
            messagebox.showwarning("Fehler", "Menge muss eine Zahl sein.")
            return

        try:
            conn = self.connect_db()
            if conn is None: return
            cursor = conn.cursor()
            cursor.execute("INSERT INTO artikel (name, menge, standort, artikelnummer) VALUES (?, ?, ?, ?)",
                           (name, menge, standort, artikelnummer))
            conn.commit()
            conn.close()
            self.status_label.config(text="Artikel hinzugefügt", foreground="green")
            self.clear_entries()
            self.load_artikel_data()
        except sqlite3.IntegrityError:
            messagebox.showerror("Fehler", "Artikelnummer existiert bereits!")
        except sqlite3.Error as e:
            self.status_label.config(text=f"DB Fehler: {e}", foreground="red")

    def delete_artikel(self):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        art_id = item["values"][0]

        if messagebox.askyesno("Löschen", f"Artikel ID {art_id} wirklich löschen?"):
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM artikel WHERE id = ?", (art_id,))
            conn.commit()
            conn.close()
            self.load_artikel_data()
            self.status_label.config(text="Gelöscht", foreground="green")

    def reset_search(self):
        self.search_term.set("")
        self.load_artikel_data()

    def clear_entries(self):
        self.entry_name_var.set("")
        self.entry_menge_var.set("")
        self.entry_standort_var.set("")
        self.entry_artikelnummer_var.set("")

    def create_inventory_table(self):
        # Frame für Tabelle in Zeile 7
        table_frame = ttk.Frame(self.content_frame)
        table_frame.grid(row=7, column=0, columnspan=2, sticky="nsew")

        columns = ("id", "name", "menge", "standort", "artikelnummer")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("menge", text="Menge")
        self.tree.heading("standort", text="Standort")
        self.tree.heading("artikelnummer", text="Nummer")

        self.tree.column("id", width=40)
        self.tree.column("name", width=200)
        self.tree.column("menge", width=60)
        self.tree.column("standort", width=100)
        self.tree.column("artikelnummer", width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_artikel_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = self.connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM artikel ORDER BY id DESC")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
            conn.close()

    def search_artikel(self):
        term = self.search_term.get()
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM artikel WHERE name LIKE ? OR artikelnummer LIKE ?", (f"%{term}%", f"%{term}%"))
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()


class WarenausgangWindow(BaseFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, app_instance, "Warenausgang", **kwargs)
        self.connect_db = self.app.connect_db

        self.main_frame = ttk.Frame(self, padding=20)
        self.main_frame.pack(fill="both", expand=True)
        self.main_frame.columnconfigure(1, weight=1)

        ttk.Label(self.main_frame, text="Warenausgang erfassen", font=("Arial", 16, "bold")).grid(row=0, column=0,
                                                                                                  columnspan=2, pady=10)

        ttk.Label(self.main_frame, text="Artikelnummer oder Name: ").grid(row=1, column=0, sticky="w", pady=5)
        self.artikel_input = ttk.Entry(self.main_frame, width=40)
        self.artikel_input.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(self.main_frame, text="Menge entnehmen: ").grid(row=2, column=0, sticky="w", pady=5)
        self.menge_input = ttk.Entry(self.main_frame, width=40)
        self.menge_input.grid(row=2, column=1, sticky="ew", pady=5, padx=5)

        self.status_label = ttk.Label(self.main_frame, text="", foreground="green")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(self.main_frame, text="Verarbeiten", command=self.process_warenausgang).grid(row=4, column=0,
                                                                                                columnspan=2, ipady=10,
                                                                                                sticky="ew")

    def process_warenausgang(self):
        artikel_id = self.artikel_input.get().strip()
        menge_str = self.menge_input.get().strip()

        if not artikel_id or not menge_str:
            self.status_label.config(text="Bitte alle Felder ausfüllen.", foreground="red")
            return
        try:
            menge = int(menge_str)
        except ValueError:
            self.status_label.config(text="Menge muss eine Zahl sein.", foreground="red")
            return

        conn = self.connect_db()
        if not conn: return
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT menge FROM artikel WHERE artikelnummer = ? OR name = ?", (artikel_id, artikel_id))
            result = cursor.fetchone()

            if result:
                aktuelle_menge = result[0]
                if aktuelle_menge < menge:
                    self.status_label.config(text=f"Bestand zu gering ({aktuelle_menge})", foreground="red")
                    return

                neue_menge = aktuelle_menge - menge
                cursor.execute("UPDATE artikel SET menge = ? WHERE artikelnummer = ? OR name = ?",
                               (neue_menge, artikel_id, artikel_id))
                conn.commit()
                self.status_label.config(text=f"Erfolg. Neuer Bestand: {neue_menge}", foreground="green")
                self.artikel_input.delete(0, tk.END)
                self.menge_input.delete(0, tk.END)
            else:
                self.status_label.config(text="Artikel nicht gefunden.", foreground="red")
        finally:
            conn.close()


# --- Vollständige Implementierungen der Zusatzfenster (Grid Layout) ---

class ArtikelanlageWindow(BaseFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, app_instance, "Artikel anlegen", **kwargs)
        self.connect_db = self.app.connect_db

        self.var_name = tk.StringVar()
        self.var_nr = tk.StringVar()
        self.var_menge = tk.StringVar(value="0")
        self.var_ort = tk.StringVar()

        f = ttk.Frame(self, padding=20)
        f.pack(fill="both", expand=True)
        f.columnconfigure(1, weight=1)

        ttk.Label(f, text="Name:*").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(f, textvariable=self.var_name).grid(row=0, column=1, sticky="ew", padx=10)

        ttk.Label(f, text="Nummer:*").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(f, textvariable=self.var_nr).grid(row=1, column=1, sticky="ew", padx=10)

        ttk.Label(f, text="Menge:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(f, textvariable=self.var_menge).grid(row=2, column=1, sticky="ew", padx=10)

        ttk.Label(f, text="Ort:").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(f, textvariable=self.var_ort).grid(row=3, column=1, sticky="ew", padx=10)

        ttk.Button(f, text="Speichern", command=self.save).grid(row=4, column=0, columnspan=2, pady=20, sticky="ew")

    def save(self):
        # Einfache Speicherlogik analog zu InventoryWindow
        try:
            conn = self.connect_db()
            conn.execute("INSERT INTO artikel (name, artikelnummer, menge, standort) VALUES (?, ?, ?, ?)",
                         (self.var_name.get(), self.var_nr.get(), int(self.var_menge.get()), self.var_ort.get()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Erfolg", "Gespeichert!")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))


class OrderingWindow(BaseFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, app_instance, "Bestellungen", **kwargs)
        self.connect_db = self.app.connect_db

        # Grid Layout für Bestellungen
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(main_frame, columns=("Name", "Bestand"), show="headings")
        self.tree.heading("Name", text="Artikel")
        self.tree.heading("Bestand", text="Bestand")
        self.tree.pack(fill="both", expand=True)

        ttk.Button(self, text="Laden (Bestand < 5)", command=self.load).pack(pady=10)
        self.load()

    def load(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = self.connect_db()
        cur = conn.execute("SELECT name, menge FROM artikel WHERE menge < 5")
        for row in cur:
            self.tree.insert("", "end", values=row)
        conn.close()


class RetourenWindow(BaseFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, app_instance, "Retoure erfassen", **kwargs)
        self.connect_db = self.app.connect_db

        self.main_frame = ttk.Frame(self, padding=20)
        self.main_frame.pack(fill="both", expand=True)
        self.main_frame.columnconfigure(1, weight=1)

        ttk.Label(self.main_frame, text="Artikel (Nr. oder Name):").grid(row=0, column=0, sticky="w", pady=5)
        self.artikel_input = ttk.Entry(self.main_frame, width=40)
        self.artikel_input.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(self.main_frame, text="Menge retourniert:").grid(row=1, column=0, sticky="w", pady=5)
        self.menge_input = ttk.Entry(self.main_frame, width=40)
        self.menge_input.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(self.main_frame, text="Grund (Optional):").grid(row=2, column=0, sticky="w", pady=5)
        self.grund_input = ttk.Entry(self.main_frame, width=40)
        self.grund_input.grid(row=2, column=1, sticky="ew", pady=5, padx=5)

        self.status_label = ttk.Label(self.main_frame, text="", foreground="green")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(self.main_frame, text="Retoure buchen", command=self.process_retoure).grid(row=4, column=0,
                                                                                              columnspan=2, pady=10,
                                                                                              sticky="ew")

    def process_retoure(self):
        artikel_id = self.artikel_input.get().strip()
        menge_str = self.menge_input.get().strip()
        # Grund wird aktuell nur erfasst, aber noch nicht in einer Historie gespeichert
        # Das wäre ein guter nächster Schritt für die Transaktions-Tabelle!
        grund = self.grund_input.get().strip()

        if not artikel_id or not menge_str:
            self.status_label.config(text="Bitte Artikelnummer/Name und Menge eingeben.", foreground="red")
            return

        try:
            menge = int(menge_str)
            if menge <= 0: raise ValueError
        except ValueError:
            self.status_label.config(text="Bitte gültige Menge eingeben.", foreground="red")
            return

        conn = self.connect_db()
        if conn is None: return
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT menge FROM artikel WHERE artikelnummer=? OR name=?", (artikel_id, artikel_id))
            res = cursor.fetchone()
            if res:
                new_menge = res[0] + menge
                cursor.execute("UPDATE artikel SET menge=? WHERE artikelnummer=? OR name=?",
                               (new_menge, artikel_id, artikel_id))
                conn.commit()
                self.status_label.config(text=f"Retoure gebucht. Neuer Bestand: {new_menge}", foreground="green")
                self.clear_fields()
            else:
                self.status_label.config(text="Artikel nicht gefunden.", foreground="red")
                messagebox.showerror("Fehler", "Artikel nicht gefunden.")
        except sqlite3.Error as e:
            self.status_label.config(text=f"Datenbankfehler: {e}", foreground="red")
        finally:
            conn.close()

    def clear_fields(self):
        self.artikel_input.delete(0, tk.END)
        self.menge_input.delete(0, tk.END)
        self.grund_input.delete(0, tk.END)