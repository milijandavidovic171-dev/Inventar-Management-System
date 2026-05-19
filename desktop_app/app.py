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


class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Inventar-Management-System")
        self.geometry("1200x750")

        # Format: Light-Mode-Farben, Dark-Mode-Farben
        self.BG_MAIN = ("#F2F4F7", "#0F111A") # Sehr tiefes Dunkelblau für den Hintergrund
        self.BG_CARD = ("#FFFFFF", "#161925") # Heller Weißton für Karten, dunkleres Grau für Dark Mode
        self.ACCENT_COLOR = ("#007AFF", "#7000FF") # maOS Blau für Light Mode, kräftiges Lila für Dark Mode
        self.HOVER_COLOR = ("#E5E9F0", "#22263F") # Heller Grauton für Hover im Light Mode, dunkleres Grau für Dark Mode
        self.TEXT_MAIN = ("#1C1C1E", "#FFFFFF") # Sehr dunkles Grau für Text im Light Mode, reines Weiß für Dark Mode


        # --- Pfade und Ressourcen ---
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.script_dir, 'inventar.db')
        self.assets_dir = os.path.join(self.script_dir, "assets")

        # --- Design Initialisieren ---
        saved_theme = self.load_theme_from_config()
        ctk.set_appearance_mode(saved_theme)
        self.configure(fg_color=self.BG_MAIN)

        # --- Native Menüleiste ---
        self.setup_menubar()

        # --- Topbar--- (Profil - Header)
        self.top_bar = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color="transparent")
        self.top_bar.pack(side="top", fill="x", padx=10)

        # --- Sidebar --- (Fließendes Design mit abgerundeten Ecken und Schatteneffekt)
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=20, fg_color=self.BG_CARD)
        self.sidebar_frame.pack(side="left", fill="y", padx=(20, 0), pady=20)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="IMS System", font=ctk.CTkFont(family="SF Pro Display",size=20, weight="bold"), text_color=self.ACCENT_COLOR)
        self.logo_label.pack(pady=30)

        # -- Content Area --
        self.content_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="transparent")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # -- Menü Management --
        self.frames = {}
        self.create_frames()
        self.create_sidebar_buttons()

        # -- Startseite anzeigen --
        self.show_frame("WelcomeFrame")

    def load_theme_from_config(self):
        """Lädt das gespeicherte Theme aus der JSON-Datei und setzt es als aktuelles Erscheinungsbild."""
        import json
        config_path = os.path.join(self.script_dir, "config.json")

        if not os.path.exists(config_path):
            return "system"  # Standard auf "system" setzen, wenn keine Konfigurationsdatei existiert

        try:
            with open(config_path, "r") as f:
                content = f.read().strip()
                if not content:
                    return "system"  # Standard auf "system" setzen, wenn die Datei leer ist
        
                #JSON parsen
                config = json.loads(content)

                # Sicherstellen dass der "theme" Schlüssel existiert und gültig ist
                theme = config.get("theme")
                if theme in ["System", "Light", "Dark", "system", "light", "dark"]:
                    return theme
                
        except Exception as e:
            print(f"Fehler beim Lader der Konfigurationsdatei: {e} - Standard-Theme wird verwendet.")
            return "system" 
            
    def save_theme_to_config(self, new_mode):
        """Speichert das gewählte Theme in die JSON-Datei"""
        import json
        config_path = os.path.join(self.script_dir, "config.json")
        try:
            config = {"theme": new_mode}
            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Fehler beim Speichern der Konfigurationsdatei: {e}")

    def setup_menubar(self):
        """Erstellt eine native Menüleiste mit den Hauptkategorien."""
        menubar = tk.Menu(self)
            
        # Datei Menü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Einstellungen", command=self.open_settings)
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

    def open_settings(self):
        # Prüfen ob das Einstellungsfenster bereits geöffnet ist
        if hasattr(self, "settings_window") and self.settings_window.winfo_exists():
            self.settings_window.focus()
        else:
            self.settings_window = SettingsWindow(self)

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
        btns = [("Dashboard", "WelcomeFrame"), 
                ("Lager", "InventoryWindow"),
                ("Wareneingang", "WareneingangWindow"), 
                ("Warenausgang", "WarenausgangWindow"),
                ("Artikelanlage", "ArtikelanlageWindow"), 
                ("Bestellungen", "OrderingWindow"), 
                ("Retouren", "RetourenWindow")]
        for text, target in btns:
            btn = ctk.CTkButton(
                self.sidebar_frame,  
                text=text, 
                fg_color="transparent",
                text_color=self.TEXT_MAIN,
                hover_color=self.HOVER_COLOR,
                font=ctk.CTkFont(family="SF Pro Text", size=14, weight="normal"),
                anchor="w",
                height=40,
                corner_radius=10,
                command=lambda t=target: self.show_frame(t),
            )
            btn.pack(pady=6, padx=15, fill="x")
            
        
        # Beenden Button am unteren Rand der Sidebar
        self.sidebar_exit_btn = ctk.CTkButton(self.sidebar_frame, 
                                              text="Beenden", 
                                              fg_color=("#E53E3E", "#A51D24"), 
                                              hover_color=("#a93226", "#741217"),
                                              text_color="white",
                                              font=ctk.CTkFont(family="SF Pro Text", size=14,weight="bold"),
                                              height=40,
                                              corner_radius=10, 
                                              command=self.quit
                                        )
        self.sidebar_exit_btn.pack(side="bottom", pady=20, padx=15, fill="x")


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
        super().__init__(parent, fg_color="transparent") # Transparenter Hintergrund, damit das Hauptfenster durchscheint
        self.controller = controller
        
        self.grid_columnconfigure((0,1,2), weight=1, uniform="equal")
        self.grid_rowconfigure((1,2), weight=1)

        #Titel Zentriert oben
        self.title_label = ctk.CTkLabel(
            self,
            text="Willkommen zum Inventar-Management-System",
            font=ctk.CTkFont(family="SF Pro Display", size=32, weight="bold"),
            text_color=controller.TEXT_MAIN
        )
        self.title_label.grid(row=0, column=0, columnspan=3,pady=(20, 10), sticky="w", padx=20)


        cards = [
            ("Lagerbestand", "InventarWindow", "inventory.png"),
            ("Wareneingang", "WareneingangWindow", "add-item.png"),
            ("Warenausgang", "WarenausgangWindow", "tracking.png"),
            ("Artikelanlage", "ArtikelanlageWindow","order-fulfillment.png"),
            ("Bestellungen", "OrderingWindow", "add-item.png"),
            ("Retouren","RetourenWindow", "sale-return-icon.png")
        ]

        row, col = 1, 0
        for title,target, icon_file in cards:
            # Eine Kachel erstellen (Frame mit Rahmen)
            # Die Kachelnutz das neue Edle Container Design mit abgerundeten Ecken und Schatteneffekt
            card = ctk.CTkFrame(self, corner_radius=20, fg_color=controller.BG_CARD, border_width=0)
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

            # Icon laden und Skalieren
            # ctk_instance.assets_dir Variable verwenden, um den Pfad zum Assets-Ordner zu erhalten
            img_path = os.path.join(self.controller.assets_dir, icon_file)

            try:
                # PIL Image Laden und Skalieren
                pil_img = Image.open(img_path)
                # PIL Resize verwenden, um die Größe des Bildes anzupassen
                ctk_img = ctk.CTkImage(
                    light_image=pil_img,
                    dark_image=pil_img,
                    size=(100, 100)
                )

            except Exception as e:
                print(f"Icon '{icon_file}' konnte nicht geladen werden. Fallback: Kein Icon. \nFehler: {e}")
                ctk_img = None


            # Button in die Karte legen
            btn = ctk.CTkButton(card, 
                                text=f"{title}",
                                image=ctk_img,
                                compound="top",# Wichtig für das Bild über dem Text Layout 
                                fg_color="transparent",
                                text_color=controller.TEXT_MAIN,
                                hover_color=controller.BG_CARD,
                                font=ctk.CTkFont(family="SF Pro Text",size=16, weight="bold"),
                                command=lambda t=target: self.controller.show_frame(t))
                        
            btn.pack(expand=True, fill="both", padx=10, pady=15)

            col += 1
            if col > 2:
                col = 0
                row += 1
        
        self.exit_btn = ctk.CTkButton(
            self,
            text="Programm Beenden",
            fg_color="#c0392b", # Rotes Design für den Exit-Button
            hover_color="#a93226", # Dunkleres Rot beim Hover (Drüberfahren)
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            command=self.controller.quit # schließt die Anwendung
        )

        self.exit_btn.grid(row=3, column=0, columnspan=3, pady=(30, 10), padx=20, sticky="ew")

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title("Einstellungen")
        self.geometry("400x300")
        self.configure(fg_color=parent.BG_CARD)
        self.attributes("-topmost",True)
        self.after(10, self.lift)



        self.label = ctk.CTkLabel(self, text="System-Präferenzen", font=ctk.CTkFont(family="SF Pro Display", size=20, weight="bold"))
        self.label.pack(pady=25)

        # Theme Auswahl
        self.theme_label = ctk.CTkLabel(self, text="Erscheinungsmodus:", font=ctk.CTkFont(size=13))
        self.theme_label.pack(pady=(10, 0))

        self.theme_option = ctk.CTkSegmentedButton(self,
                                                    values=["System", "Light", "Dark"],
                                                    selected_color=parent.ACCENT_COLOR,
                                                    command=self.update_theme)
        self.theme_option.pack(pady=15, padx=30, fill="x")
        self.theme_option.set(ctk.get_appearance_mode())

        self.close_btn = ctk.CTkButton(self, text="Schließen", fg_color=parent.ACCENT_COLOR, command=self.destroy)
        self.close_btn.pack(pady=30, padx=40, fill="x")
    
    def update_theme(self, new_mode):
        ctk.set_appearance_mode(new_mode)
        self.master.save_theme_to_config(new_mode)

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()