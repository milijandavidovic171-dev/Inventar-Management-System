import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

# Importiere alle Fensterklassen aus windows.py
from windows import (
    WareneingangWindow, InventoryWindow, WarenausgangWindow,
    ArtikelanlageWindow, OrderingWindow, RetourenWindow
)

# Globales Design-Setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Inventar-Management-System v2.0")
        self.geometry("1200x750")

        # --- Automatischer Dark Mode basierend auf Systemzeit ---
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # --- Pfade und Ressourcen ---
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.script_dir, 'inventar.db')
        self.assets_dir = os.path.join(self.script_dir, "assets")

        # --- Native Menüleiste ---
        self.setup_menubar()

        # --- Topbar---
        self.top_bar = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color=("white", "#2B2B2B"))
        self.top_bar.pack(side="top", fill="x")

        self.setup_profile_header()

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="IMS System", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20)

        # -- Content Area --
        self.content_frame = ctk.CTkFrame(self, corner_radius=15)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # -- Menü Management --
        self.frames = {}
        self.create_frames()
        self.create_sidebar_buttons()

        # -- Startseite anzeigen --
        self.show_frame("WelcomeFrame")


    def setup_menubar(self):
        """Erstellt eine native Menüleiste mit den Hauptkategorien."""
        menubar = tk.Menu(self)
        
        # Datei Menü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Einstellungen", command=lambda: messagebox.showinfo("Einstellungen", "Hier können Sie die Einstellungen anpassen."))
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.quit)
        menubar.add_cascade(label="Datei", menu=file_menu)
        self.config(menu=menubar)

        # Menü Info
        info_menu = tk.Menu(menubar, tearoff=0)
        info_menu.add_command(label="Über mich", command=self.show_about)
        info_menu.add_command(label="Software-Info")
        menubar.add_cascade(label="Info", menu=info_menu)

        self.config(menu=menubar)

    def setup_profile_header(self):
        # Container für den Profilbereich
        p_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        p_frame.pack(side="right", padx=20)

        try:
            img_path = os.path.join(self.assets_dir, "Milijan Davidovic.jpg")
            pil_img = Image.open(img_path).resize((50, 50))
            self.profile_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img)

            img_lbl = ctk.CTkLabel(p_frame, image=self.profile_img, text="")
            img_lbl.pack(side="right", padx=(10, 0), pady=10)
        except Exception as e:
            print(f"Fehler beim Laden des Profilbildes: {e}")
            ctk.CTkLabel(p_frame, text="👤", font=ctk.CTkFont(size=14)).pack(side="right", padx=(10, 0), pady=10)

        ctk.CTkLabel(p_frame, text="Milijan Davidovic", font=ctk.CTkFont(size=14)).pack(side="right", padx=(10, 0), pady=10)

    def show_about(self):
        """Zeigt ein Info-Fenster mit Informationen über die Software."""
        messagebox.showinfo(
            "Über IMS System",
            "Inventar-Management-System v2.0\n"
            "Entwickelt von Milijan Davidovic\n"
            "Version 2.0\n\n"
            "Diese Software wurde entwickelt, um die Lagerverwaltung zu optimieren und zu vereinfachen."
        )

    def create_sidebar_buttons(self):
        """Erstellt die Navigations-Buttons in der Sidebar."""
        btns = [("Dashboard", "WelcomeFrame"), ("Lager", "InventoryWindow")
                , ("Wareneingang", "WareneingangWindow"), ("Warenausgang", "WarenausgangWindow"),
                ("Artikelanlage", "ArtikelanlageWindow"), ("Bestellungen", "OrderingWindow"), ("Retouren", "RetourenWindow")]
        for text, target in btns:
            ctk.CTkButton(self.sidebar_frame,  text=text, command=lambda t=target: self.show_frame(t)).pack(pady=10, padx=20, fill="x")


    def create_frames(self):
        """Initialisiert alle Frames und legt sie im content_frame übereinander."""
        frame_classes = {
            "WelcomeFrame": WelcomeFrame,
            "InventoryWindow": InventoryWindow,
            "WareneingangWindow": WareneingangWindow,
            "WarenausgangWindow": WarenausgangWindow,
            "ArtikelanlageWindow": ArtikelanlageWindow,
            "OrderingWindow": OrderingWindow,
            "RetourenWindow": RetourenWindow
        }

        for name, FClass in frame_classes.items():
            frame = FClass(self.content_frame, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def show_frame(self, page_name):
        """Bringt den gewählten Frame nach vorne und aktualisiert ggf. die Daten."""
        frame = self.frames[page_name]
        
        # Falls das Fenster eine 'refresh_data' oder 'load' Methode hat, rufen wir sie auf
        if hasattr(frame, "refresh_data"):
            frame.refresh_data()
        elif hasattr(frame, "load"):
            frame.load()
            
        frame.tkraise()

    def connect_db(self):
        """Stellt eine Verbindung zur SQLite Datenbank her."""
        import sqlite3
        return sqlite3.connect(os.path.join(self.script_dir, 'inventar.db'))



# --- Startbildschirm (Dashboard) ---
class WelcomeFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(self, text="Willkommen zum Inventar-Management-System", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, columnspan=3, pady=(20, 10))

        cards = [
            ("Lagerbestand", "InventarWindow", "inventory.png"),
            ("Wareneingang", "WareneingangWindow", "add-item.png"),
            ("Warenausgang", "WarenausgangWindow", "tracking.png"),
            ("Artikelanlage", "ArtikelanlageWindow","order-fufillment.png"),
            ("Bestellungen", "OrderingWindow", "add-item.png"),
            ("Retouren","RetourenWindow", "sale-return-icon.png")
        ]
        

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()