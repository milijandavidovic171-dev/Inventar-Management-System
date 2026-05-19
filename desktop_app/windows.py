import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3

class BaseFrame(ctk.CTkFrame):
    """Basis-Klasse für alle Fenster-Frames."""
    def __init__(self, master, app_instance, title, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app_instance
        self.connect_db = self.app.connect_db

        # Moderner Titel oben in jedem Frame
        self.title_label = ctk.CTkLabel(
            self, 
            text=title, 
            font=ctk.CTkFont(size=26, weight="bold")
        )
        self.title_label.pack(pady=(20, 10))

    def clear_fields(self, *widgets):
        """Hilfsmethode zum Leeren von Eingabefeldern."""
        for widget in widgets:
            widget.delete(0, 'end')

# --- WARENEINGANG ---
class WareneingangWindow(BaseFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, app_instance, "Wareneingang buchen", **kwargs)

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=40, pady=20)

        ctk.CTkLabel(self.container, text="Artikel (Name oder Nummer):").pack(pady=(20, 0))
        self.artikel_input = ctk.CTkEntry(self.container, width=350, placeholder_text="z.B. Art-001")
        self.artikel_input.pack(pady=10)

        ctk.CTkLabel(self.container, text="Anzahl hinzufügen:").pack(pady=(10, 0))
        self.menge_input = ctk.CTkEntry(self.container, width=350, placeholder_text="Menge")
        self.menge_input.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.container, text="", text_color="gray")
        self.status_label.pack(pady=10)

        self.btn = ctk.CTkButton(self.container, text="Bestand erhöhen", command=self.process)
        self.btn.pack(pady=20)

    def process(self):
        art = self.artikel_input.get().strip()
        qty = self.menge_input.get().strip()
        
        if not art or not qty:
            self.status_label.configure(text="Bitte alle Felder ausfüllen!", text_color="red")
            return

        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT menge FROM artikel WHERE artikelnummer=? OR name=?", (art, art))
            res = cursor.fetchone()

            if res:
                new_qty = res[0] + int(qty)
                cursor.execute("UPDATE artikel SET menge=? WHERE artikelnummer=? OR name=?", (new_qty, art, art))
                conn.commit()
                self.status_label.configure(text=f"Bestand aktualisiert: {new_qty}", text_color="green")
                self.clear_fields(self.artikel_input, self.menge_input)
            else:
                self.status_label.configure(text="Artikel nicht gefunden!", text_color="red")
            conn.close()
        except ValueError:
            self.status_label.configure(text="Menge muss eine Zahl sein!", text_color="red")

# --- INVENTAR / TABELLE ---
class InventoryWindow(BaseFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, app_instance, "Lagerübersicht", **kwargs)

        # Suchleiste
        self.search_bar = ctk.CTkEntry(self, placeholder_text="Suche nach Name oder Nummer...", width=500)
        self.search_bar.pack(pady=10, padx=20)
        self.search_bar.bind("<KeyRelease>", lambda e: self.refresh_data())

        # Tabellen-Container
        self.table_container = ctk.CTkFrame(self)
        self.table_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Styling für den Treeview (Standard-Tkinter sieht sonst alt aus)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        style.map("Treeview", background=[('selected', '#1f538d')])

        cols = ("ID", "Name", "Bestand", "Lagerort", "Art.-Nr.")
        self.tree = ttk.Treeview(self.table_container, columns=cols, show="headings")
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)
        
        scroll = ctk.CTkScrollbar(self.table_container, command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)

        self.refresh_data()

    def refresh_data(self):
        term = self.search_bar.get()
        for item in self.tree.get_children(): self.tree.delete(item)
        
        conn = self.connect_db()
        if term:
            cur = conn.execute("SELECT * FROM artikel WHERE name LIKE ? OR artikelnummer LIKE ?", (f"%{term}%", f"%{term}%"))
        else:
            cur = conn.execute("SELECT * FROM artikel")
        
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

# --- WARENAUSGANG ---
class WarenausgangWindow(BaseFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, app_instance, "Warenausgang / Entnahme", **kwargs)

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=40, pady=20)

        ctk.CTkLabel(self.container, text="Artikel (Name oder Nummer):").pack(pady=(20, 0))
        self.art_in = ctk.CTkEntry(self.container, width=350)
        self.art_in.pack(pady=5)

        ctk.CTkLabel(self.container, text="Menge entnehmen:").pack(pady=(10, 0))
        self.qty_in = ctk.CTkEntry(self.container, width=350)
        self.qty_in.pack(pady=5)

        self.status = ctk.CTkLabel(self.container, text="")
        self.status.pack(pady=10)

        ctk.CTkButton(self.container, text="Entnahme buchen", fg_color="#c0392b", hover_color="#a93226", command=self.process).pack(pady=20)

    def process(self):
        art = self.art_in.get().strip()
        qty_s = self.qty_in.get().strip()

        try:
            qty = int(qty_s)
            conn = self.connect_db()
            cur = conn.cursor()
            cur.execute("SELECT menge FROM artikel WHERE artikelnummer=? OR name=?", (art, art))
            res = cur.fetchone()

            if res:
                if res[0] >= qty:
                    new_val = res[0] - qty
                    cur.execute("UPDATE artikel SET menge=? WHERE artikelnummer=? OR name=?", (new_val, art, art))
                    conn.commit()
                    self.status.configure(text=f"Entnommen. Restbestand: {new_val}", text_color="green")
                    self.clear_fields(self.art_in, self.qty_in)
                else:
                    self.status.configure(text=f"Fehler: Nur {res[0]} auf Lager!", text_color="red")
            else:
                self.status.configure(text="Artikel nicht gefunden!", text_color="red")
            conn.close()
        except:
            self.status.configure(text="Ungültige Eingabe!", text_color="red")

# --- ARTIKELANLAGE ---
class ArtikelanlageWindow(BaseFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, app_instance, "Neuen Artikel anlegen", **kwargs)

        f = ctk.CTkFrame(self)
        f.pack(fill="both", expand=True, padx=40, pady=20)

        self.in_name = ctk.CTkEntry(f, placeholder_text="Bezeichnung", width=350)
        self.in_name.pack(pady=10)
        self.in_nr = ctk.CTkEntry(f, placeholder_text="Artikelnummer (Eindeutig)", width=350)
        self.in_nr.pack(pady=10)
        self.in_qty = ctk.CTkEntry(f, placeholder_text="Anfangsbestand", width=350)
        self.in_qty.pack(pady=10)
        self.in_loc = ctk.CTkEntry(f, placeholder_text="Lagerort (z.B. Regal A1)", width=350)
        self.in_loc.pack(pady=10)

        ctk.CTkButton(f, text="In Datenbank speichern", command=self.save).pack(pady=20)

    def save(self):
        try:
            conn = self.connect_db()
            conn.execute("INSERT INTO artikel (name, artikelnummer, menge, standort) VALUES (?,?,?,?)",
                         (self.in_name.get(), self.in_nr.get(), int(self.in_qty.get()), self.in_loc.get()))
            conn.commit()
            conn.close()
            messagebox.showinfo("IMS", "Artikel erfolgreich angelegt!")
            self.clear_fields(self.in_name, self.in_nr, self.in_qty, self.in_loc)
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Artikel nicht speichern: {e}")

# --- BESTELLUNGEN ---
class OrderingWindow(BaseFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, app_instance, "Nachbestellungen prüfen", **kwargs)

        self.info = ctk.CTkLabel(self, text="Folgende Artikel haben einen kritischen Bestand (< 5 Stück):")
        self.info.pack(pady=10)

        self.table_f = ctk.CTkFrame(self)
        self.table_f.pack(fill="both", expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(self.table_f, columns=("N", "B"), show="headings")
        self.tree.heading("N", text="Artikelname")
        self.tree.heading("B", text="Aktueller Bestand")
        self.tree.pack(fill="both", expand=True)

        ctk.CTkButton(self, text="Liste aktualisieren", command=self.load).pack(pady=10)
        self.load()

    def load(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = self.connect_db()
        cur = conn.execute("SELECT name, menge FROM artikel WHERE menge < 5")
        for row in cur:
            self.tree.insert("", "end", values=row)
        conn.close()

# --- RETOUREN ---
class RetourenWindow(BaseFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, app_instance, "Retouren erfassen", **kwargs)

        f = ctk.CTkFrame(self)
        f.pack(fill="both", expand=True, padx=40, pady=20)

        self.art_in = ctk.CTkEntry(f, placeholder_text="Artikelnummer", width=350)
        self.art_in.pack(pady=10)
        self.qty_in = ctk.CTkEntry(f, placeholder_text="Menge", width=350)
        self.qty_in.pack(pady=10)
        self.reason = ctk.CTkEntry(f, placeholder_text="Grund (Optional)", width=350)
        self.reason.pack(pady=10)

        ctk.CTkButton(f, text="Retoure einbuchen", command=self.process).pack(pady=20)

    def process(self):
        # Hier nutzen wir einfach die Wareneingangs-Logik
        art = self.art_in.get()
        qty = self.qty_in.get()
        if art and qty:
            try:
                conn = self.connect_db()
                cur = conn.cursor()
                cur.execute("SELECT menge FROM artikel WHERE artikelnummer=? OR name=?", (art, art))
                res = cur.fetchone()
                if res:
                    new = res[0] + int(qty)
                    cur.execute("UPDATE artikel SET menge=? WHERE artikelnummer=? OR name=?", (new, art, art))
                    conn.commit()
                    messagebox.showinfo("Retoure", f"Erfolgreich verbucht. Neuer Bestand: {new}")
                    self.clear_fields(self.art_in, self.qty_in, self.reason)
                conn.close()
            except:
                pass