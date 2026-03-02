import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from PIL import Image, ImageTk

# Importiere alle Fensterklassen aus windows.py
from windows import (
    WareneingangWindow, InventoryWindow, WarenausgangWindow,
    ArtikelanlageWindow, OrderingWindow, RetourenWindow
)


class InventoryApp():
    def __init__(self, root):
        self.root = root
        self.root.title("Inventar-Management-System")

        # --- Fenstergröße und Zentrierung ---
        window_width = 1200
        window_height = 750
        self.center_window(self.root, window_width, window_height)

        # --- Globale Stile (Design) ---
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Farbpalette definieren
        self.colors = {
            "bg_main": "#f4f6f9",
            "bg_sidebar": "#2c3e50",
            "text_light": "#ffffff",
            "text_dark": "#333333",
            "accent": "#3498db"
        }

        # Hintergrundfarbe des Hauptfensters setzen
        self.root.configure(background=self.colors["bg_main"])

        # --- Styles konfigurieren ---
        self.style.configure("TFrame", background=self.colors["bg_main"])
        self.style.configure("TLabel", background=self.colors["bg_main"], foreground=self.colors["text_dark"])

        self.style.configure("Title.TLabel",
                             font=("Segoe UI", 24, "bold"),
                             background=self.colors["bg_main"],
                             foreground=self.colors["text_dark"])

        self.style.configure("Sidebar.TFrame", background=self.colors["bg_sidebar"])
        self.style.configure("Sidebar.TLabel", background=self.colors["bg_sidebar"],
                             foreground=self.colors["text_light"])

        self.style.configure("Sidebar.TButton",
                             font=("Segoe UI", 11),
                             foreground=self.colors["text_light"],
                             background=self.colors["bg_sidebar"],
                             borderwidth=0,
                             anchor="w",
                             padding=8)
        self.style.map("Sidebar.TButton",
                       background=[("active", self.colors["accent"]), ("!active", self.colors["bg_sidebar"])],
                       foreground=[("active", self.colors["text_light"])])

        # Große Dashboard-Buttons
        self.style.configure("Dashboard.TButton",
                             font=("Segoe UI", 12, "bold"),
                             foreground=self.colors["text_dark"],
                             background="#ffffff",
                             compound="top",
                             padding=15)
        self.style.map("Dashboard.TButton",
                       background=[("active", "#e0e8f0")],
                       relief=[("pressed", "sunken"), ("!pressed", "solid")])

        # --- Pfade und Ressourcen ---
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.script_dir, 'inventar.db')

        self.icon_images = self.create_dashboard_icons()

        # --- Datenbank initialisieren ---
        self.create_table()

        # --- Layout-Aufbau ---
        self.main_container = ttk.Frame(root, style="TFrame")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.main_container.grid_columnconfigure(0, weight=0, minsize=220)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(2, weight=0, minsize=200)
        self.main_container.grid_rowconfigure(0, weight=1)

        # 1. Linke Sidebar
        self.sidebar_frame = ttk.Frame(self.main_container, style="Sidebar.TFrame")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.create_sidebar_buttons()

        # 2. Hauptinhalt (Mitte)
        self.content_frame = ttk.Frame(self.main_container, style="TFrame", padding=20)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # 3. Rechte Sidebar (Infos)
        self.right_sidebar_frame = ttk.Frame(self.main_container, padding=10, style="TFrame")
        self.right_sidebar_frame.grid(row=0, column=2, sticky="nsew")
        self.add_right_sidebar_content()

        # --- Menübar und Frames initialisieren ---
        self.create_menubar()
        self.frames = {}
        self.create_frames()

        # --- Statusleiste ---
        self.status_bar_frame = ttk.Frame(self.root, relief="sunken")
        self.status_bar_frame.pack(side="bottom", fill="x")

        ttk.Label(self.status_bar_frame, text="Version 1.0", font=("Arial", 8)).pack(side="left", padx=10)
        ttk.Label(self.status_bar_frame, text="Status: Bereit", font=("Arial", 8)).pack(side="right", padx=10)

        # Startbildschirm anzeigen
        self.show_frame("WelcomeFrame")

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def create_dashboard_icons(self):
        images = {}
        icon_size = (64, 64)

        # Dateinamen müssen exakt so im Ordner liegen
        file_map = {
            "list": "inventory.png",
            "plus": "add-item.png",
            "in": "order-fulfillment.png",
            "out": "tracking.png",
            "cart": "sale-return-icon.png",
            "return": "product-return.png"
        }

        for key, filename in file_map.items():
            path = os.path.join(self.script_dir, filename)
            try:
                pil_img = Image.open(path)
                pil_img = pil_img.resize(icon_size, Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(pil_img)
                images[key] = tk_img
            except Exception as e:
                print(f"Warnung: Konnte Icon '{filename}' nicht laden: {e}")
                images[key] = None

        return images

    def create_frames(self):
        frame_classes = {
            "WelcomeFrame": (WelcomeFrame, {"icon_images": self.icon_images}),
            "InventoryWindow": (InventoryWindow, {}),
            "WareneingangWindow": (WareneingangWindow, {}),
            "WarenausgangWindow": (WarenausgangWindow, {}),
            "ArtikelanlageWindow": (ArtikelanlageWindow, {}),
            "OrderingWindow": (OrderingWindow, {}),
            "RetourenWindow": (RetourenWindow, {})
        }

        for name, (FClass, kwargs) in frame_classes.items():
            frame = FClass(self.content_frame, self, **kwargs)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        try:
            frame = self.frames[page_name]
            frame.tkraise()
            if page_name == "InventoryWindow" and hasattr(frame, "load_artikel_data"):
                frame.load_artikel_data()
        except KeyError:
            if page_name == "EinstellungenWindow":
                messagebox.showinfo("Info", "Die Einstellungen sind noch nicht implementiert.")
            else:
                messagebox.showerror("Fehler", f"Fenster '{page_name}' nicht gefunden.")

    def create_sidebar_buttons(self):
        ttk.Button(self.sidebar_frame, text="Startseite", style="Sidebar.TButton",
                   command=lambda: self.show_frame("WelcomeFrame")).pack(fill="x", pady=(20, 5), padx=5)

        ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill="x", padx=5, pady=10)

        ttk.Label(self.sidebar_frame, text="Vorgänge", style="Sidebar.TLabel", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=10)

        buttons = [
            ("Artikelverwaltung", "InventoryWindow"),
            ("Artikelanlage", "ArtikelanlageWindow"),
            ("Wareneingang", "WareneingangWindow"),
            ("Warenausgang", "WarenausgangWindow"),
            ("Bestellungen", "OrderingWindow"),
            ("Retouren", "RetourenWindow")
        ]

        for text, frame_name in buttons:
            btn = ttk.Button(self.sidebar_frame, text=text, style="Sidebar.TButton",
                             command=lambda f=frame_name: self.show_frame(f))
            btn.pack(fill="x", pady=2, padx=5)

    def add_right_sidebar_content(self):
        ttk.Label(self.right_sidebar_frame, text="Benutzer", font=("Segoe UI", 10, "bold")).pack(anchor="w",
                                                                                                 pady=(20, 5))
        user_combo = ttk.Combobox(self.right_sidebar_frame, values=["Admin", "Lagerist"])
        user_combo.set("Admin")
        user_combo.pack(fill="x", pady=5)

    def create_menubar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Datei", menu=file_menu)
        file_menu.add_command(label="Über uns", command=self.open_about_window)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.root.quit)

        nav_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ansicht", menu=nav_menu)
        nav_menu.add_command(label="Startseite", command=lambda: self.show_frame("WelcomeFrame"))
        nav_menu.add_command(label="Inventar", command=lambda: self.show_frame("InventoryWindow"))

    def open_about_window(self):
        top = tk.Toplevel(self.root)
        top.title("Über uns")
        self.center_window(top, 400, 350)

        ttk.Label(top, text="Inventar Manager v1.0", font=("Arial", 16, "bold")).pack(pady=20)
        ttk.Label(top, text="Entwickelt von Milijan").pack()
        ttk.Label(top, text="Kempten (Allgäu), Deutschland").pack()

        try:
            img_path = os.path.join(self.script_dir, "Milijan Davidovic.jpg")
            pil_img = Image.open(img_path).resize((120, 120), Image.Resampling.LANCZOS)
            top.tk_img = ImageTk.PhotoImage(pil_img)
            lbl = ttk.Label(top, image=top.tk_img)
            lbl.pack(pady=15)
        except Exception as e:
            print(f"Profilbild nicht geladen: {e}")

        ttk.Button(top, text="Schließen", command=top.destroy).pack(pady=10)

    def connect_db(self):
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            messagebox.showerror("DB Fehler", f"Verbindung fehlgeschlagen: {e}")
            return None

    def create_table(self):
        conn = self.connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                               CREATE TABLE IF NOT EXISTS artikel
                               (
                                   ID
                                   INTEGER
                                   PRIMARY
                                   KEY
                                   AUTOINCREMENT,
                                   name
                                   TEXT
                                   NOT
                                   NULL,
                                   menge
                                   INTEGER
                                   NOT
                                   NULL,
                                   standort
                                   TEXT,
                                   artikelnummer
                                   TEXT
                                   UNIQUE
                                   NOT
                                   NULL
                               )
                               """)
                conn.commit()
            finally:
                conn.close()


# --- Startbildschirm (Dashboard) ---
class WelcomeFrame(ttk.Frame):
    def __init__(self, parent, controller, icon_images=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.icon_images = icon_images if icon_images else {}

        self.config(style="TFrame")

        # Begrüßungstext
        title = ttk.Label(self, text="Willkommen im Inventar-Management-System", style="Title.TLabel")
        title.pack(pady=(40, 30))

        # Container für die Kacheln
        grid_frame = ttk.Frame(self, style="TFrame")
        grid_frame.pack(expand=True)

        # --- Buttons manuell erstellen ---

        # Zeile 0, Spalte 0: Artikelverwaltung
        btn_list = ttk.Button(
            grid_frame,
            text="Artikelverwaltung",
            image=self.icon_images.get("list"),
            style="Dashboard.TButton",
            compound="top",  # WICHTIG: Erzwingt Bild oben, Text unten
            command=lambda: self.controller.show_frame("InventoryWindow")
        )
        btn_list.grid(row=0, column=0, padx=20, pady=20, sticky="nsew", ipadx=20, ipady=20)

        # Zeile 0, Spalte 1: Artikel anlegen
        btn_plus = ttk.Button(
            grid_frame,
            text="Neuen Artikel\nanlegen",
            image=self.icon_images.get("plus"),
            style="Dashboard.TButton",
            compound="top",
            command=lambda: self.controller.show_frame("ArtikelanlageWindow")
        )
        btn_plus.grid(row=0, column=1, padx=20, pady=20, sticky="nsew", ipadx=20, ipady=20)

        # Zeile 0, Spalte 2: Wareneingang
        btn_in = ttk.Button(
            grid_frame,
            text="Wareneingang\nbuchen",
            image=self.icon_images.get("in"),
            style="Dashboard.TButton",
            compound="top",
            command=lambda: self.controller.show_frame("WareneingangWindow")
        )
        btn_in.grid(row=0, column=2, padx=20, pady=20, sticky="nsew", ipadx=20, ipady=20)

        # Zeile 1, Spalte 0: Warenausgang
        btn_out = ttk.Button(
            grid_frame,
            text="Warenausgang\nbuchen",
            image=self.icon_images.get("out"),
            style="Dashboard.TButton",
            compound="top",
            command=lambda: self.controller.show_frame("WarenausgangWindow")
        )
        btn_out.grid(row=1, column=0, padx=20, pady=20, sticky="nsew", ipadx=20, ipady=20)

        # Zeile 1, Spalte 1: Bestellungen
        btn_cart = ttk.Button(
            grid_frame,
            text="Offene\nBestellungen",
            image=self.icon_images.get("cart"),
            style="Dashboard.TButton",
            compound="top",
            command=lambda: self.controller.show_frame("OrderingWindow")
        )
        btn_cart.grid(row=1, column=1, padx=20, pady=20, sticky="nsew", ipadx=20, ipady=20)

        # Zeile 1, Spalte 2: Retouren
        btn_return = ttk.Button(
            grid_frame,
            text="Retouren\nverwalten",
            image=self.icon_images.get("return"),
            style="Dashboard.TButton",
            compound="top",
            command=lambda: self.controller.show_frame("RetourenWindow")
        )
        btn_return.grid(row=1, column=2, padx=20, pady=20, sticky="nsew", ipadx=20, ipady=20)

        # "Programm Beenden"-Button - KORRIGIERT: Jetzt Kind von grid_frame
        destroy_button = ttk.Button(grid_frame, text="Programm Beenden", command=self.controller.root.destroy)
        destroy_button.grid(row=2, column=0, columnspan=3, pady=40, ipadx=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()